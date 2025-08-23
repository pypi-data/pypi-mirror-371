import lightning as L
import torch
import os
from episode.torch_model import FullModel, ProcessedFeatures
from typing import Tuple
from episode.semantic_representation import Composition
from lightning.pytorch.callbacks import ModelCheckpoint, EarlyStopping
from datetime import datetime
import numpy as np
from episode import utils
import optuna
import logging
import copy
from episode.config import TorchTrainerConfig

class PropertyModuleTrainer(L.LightningModule):

    def __init__(self, config: TorchTrainerConfig):
        super().__init__()
        self.automatic_optimization = False
        self.config = config
        self.x0_included = config.x0_included
        L.seed_everything(self.config.seed)
        self.model: FullModel = FullModel(config)
        self.lr = self.config.lr

    def prediction_loss(self, Y_pred, Y, mask):
        """
        Calculate the prediction loss.
        
        Args:
            Y_pred: predicted values
            Y: true values
            mask: mask to apply to the loss
        
        Returns:
            prediction loss
        """
        diff_squared = (Y_pred - Y) ** 2
        diff_squared = diff_squared * mask  # Apply mask to the squared differences
        loss_per_sample = torch.sum(diff_squared, dim=1) / mask.sum(dim=1)  # shape (batch_size,)
        prediction_loss = torch.mean(loss_per_sample)
        return prediction_loss
      

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        X, B, T, X0, B_cat, mask = batch
        return self.forward(B, T, X0, B_cat)
           
    def forward(self, B, T, X0, B_cat):
        if not self.x0_included:
            X0 = None
        processed_features = ProcessedFeatures(B,
                                               B_cat, 
                                               self.config.categorical_features_indices,
                                               self.config.cat_n_unique_dict,
                                               X0)
        return self.model.forward(processed_features, T)

    def training_step(self, batch, batch_idx):

        opt = self.optimizers()
        assert not isinstance(opt, list)

        def closure():
           
            X, B, T, Y, X0, B_cat, mask = batch
              
            opt.zero_grad()

            Y_pred = self.forward(B, T, X0, B_cat)

            loss = self.prediction_loss(Y_pred, Y, mask) + self.model.loss_last_transition_point() + self.model.loss_discontinuity_of_derivatives()

            self.manual_backward(loss)
            self.log('train_loss', loss)
            return loss

        opt.step(closure=closure)

    def validation_step(self, batch, batch_idx):

        X, B, T, Y, X0, B_cat, mask = batch
      
        Y_pred = self.forward(B, T, X0, B_cat)
           
        prediction_loss = self.prediction_loss(Y_pred, Y, mask)

        self.log('val_loss', prediction_loss)

        return prediction_loss

    def test_step(self, batch, batch_idx):

        X, B, T, Y, X0, B_cat, mask = batch
      
        Y_pred = self.forward(B, T, X0, B_cat)
           
        loss = self.prediction_loss(Y_pred, Y, mask)
       
        self.log('test_loss', loss)

        return loss

    def configure_optimizers(self):
        # optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=self.config['weight_decay'])
        optimizer = torch.optim.LBFGS(self.model.parameters(), lr=self.lr, history_size=100, max_iter=20, line_search_fn='strong_wolfe')
        # params=list()
        # params.extend(list(self.model.parameters()))
        # optimizer = LBFGSNew(self.model.parameters(), lr=self.lr, cost_use_gradient=True, history_size=100, max_iter=20)
        return optimizer

def train_property_module(
        litmodule: L.LightningModule,
        config: TorchTrainerConfig, 
        train_dataset: torch.utils.data.TensorDataset, 
        val_dataset: torch.utils.data.TensorDataset,
        n_epochs: int,
        patience: int, 
        seed: int,
        verbose: bool = False,
        only_loss: bool = False
        ) -> Tuple[float, PropertyModuleTrainer] | float:

    property_module_timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

    # create callbacks
    best_val_checkpoint = ModelCheckpoint(
        monitor='val_loss',
        mode='min',
        save_top_k=1,
        filename='best_val',
        dirpath=f'./checkpoints/{property_module_timestamp}'
    )
    # added early stopping callback, if validation loss does not improve over 10 epochs -> terminate training.
    early_stop_callback = EarlyStopping(
        monitor='val_loss',
        min_delta=0,
        patience=patience,
        verbose=False,
        mode='min'
    )
    callback_ls = [best_val_checkpoint, early_stop_callback]

    lightning_accelerator = utils.get_lightning_accelerator(config.device)

    trainer_dict = {
        'deterministic': True,
        'devices': 1,
        'enable_model_summary': False,
        'enable_progress_bar': verbose,
        'accelerator': lightning_accelerator,
        'max_epochs': n_epochs,
        'check_val_every_n_epoch': 5,
        'log_every_n_steps': 1,
        'callbacks': callback_ls,
        'logger': False,
    }
    trainer = L.Trainer(**trainer_dict)

    torch_gen = torch.Generator()
    torch_gen.manual_seed(seed)

    train_dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=len(train_dataset), shuffle=True, generator=torch_gen)
    val_dataloader = torch.utils.data.DataLoader(val_dataset, batch_size=len(val_dataset), shuffle=False)

        
    logging.getLogger("lightning.pytorch.utilities.rank_zero").setLevel(logging.WARNING) 
    logging.getLogger('lightning').setLevel(0)

    trainer.fit(model=litmodule,train_dataloaders=train_dataloader,val_dataloaders=val_dataloader)
    assert best_val_checkpoint.best_model_score is not None, "Best model score should not be None"
    val_loss = best_val_checkpoint.best_model_score.item()

    final_epoch = trainer.current_epoch
    print(f"Finished after {final_epoch} epochs")
    best_model_path =  best_val_checkpoint.best_model_path

    if only_loss:
        # Delete the checkpoint directory
        os.remove(best_model_path)  # Remove the specific checkpoint file
        os.rmdir(os.path.dirname(best_model_path))  # Remove the directory if empty
        return val_loss
    else:
        best_model = PropertyModuleTrainer.load_from_checkpoint(checkpoint_path=best_model_path,config=litmodule.config)
        # Delete the checkpoint directory
        os.remove(best_model_path)  # Remove the specific checkpoint file
        os.rmdir(os.path.dirname(best_model_path))  # Remove the directory if empty
        return val_loss, best_model

def tune_property_module(
        trainer: type[L.LightningModule],
        config: TorchTrainerConfig, 
        train_dataset: torch.utils.data.TensorDataset, 
        val_dataset: torch.utils.data.TensorDataset
        ) -> TorchTrainerConfig:
    
    config = config.copy()  # Create a copy of the config to avoid modifying the original

    def objective(trial):

        parameters = {
            # 'dis_loss_coeff_1': trial.suggest_float('dis_loss_coeff_1', 1e-9, 1e-1, log=True),
            'dis_loss_coeff_2': trial.suggest_float('dis_loss_coeff_2', 1e-9, 1e-1, log=True),
            'lr': trial.suggest_float('lr', 1e-4, 1.0, log=True),
            'last_loss_coeff': trial.suggest_float('last_loss_coeff', 1e-3, 1e+3, log=True),
        }

        for key, value in parameters.items():
            config.__setattr__(key, value)

        litmodule = trainer(config)

        val_loss = train_property_module(
            litmodule=litmodule,
            config=config,
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            n_epochs=config.n_epochs // 2,
            patience=10,
            seed=config.seed,
            only_loss=True,
        )
        assert isinstance(val_loss, float), "Validation loss should be a float"
        return val_loss

    sampler = optuna.samplers.TPESampler(seed=config.seed)
    study = optuna.create_study(sampler=sampler,direction='minimize')
    study.optimize(objective, n_trials=config.n_tune)
    best_trial = study.best_trial
    best_hyperparameters = best_trial.params
    print(f'Best hyperparameters: {best_hyperparameters}')
    for key, value in best_hyperparameters.items():
        config.__setattr__(key, value)
    return config

def fit_property_module(
        trainer: type[L.LightningModule],
        config: TorchTrainerConfig, 
        train_dataset: torch.utils.data.TensorDataset, 
        val_dataset: torch.utils.data.TensorDataset,
        verbose: bool = False,
        ) -> Tuple[float, PropertyModuleTrainer | None]:

        composition = config.composition

        if config.n_tune > 0:
            config = tune_property_module(trainer, config, train_dataset, val_dataset)

        if verbose:
            print(f'Fitting the model to the data using the composition: {composition}')

        val_loss = np.inf
        best_model = None
        num_retries = 0
        while val_loss == np.inf or np.isnan(val_loss):
            if num_retries > 0:
                print(f"Retrying fitting the model with a different seed")
                config = copy.deepcopy(config)
                config.seed += 1
            litmodule = trainer(config)
            result = train_property_module(
                litmodule=litmodule,
                config=config,
                train_dataset=train_dataset,
                val_dataset=val_dataset,
                n_epochs=config.n_epochs,
                patience=20,
                seed=config.seed,
                verbose=verbose,
                only_loss=False
            )
            assert isinstance(result, tuple), "Result should be a tuple of (val_loss, best_model)"
            val_loss, best_model = result
            num_retries += 1
        
        if verbose:
            print(f'Validation loss for {composition}: {val_loss}')

        return val_loss, best_model