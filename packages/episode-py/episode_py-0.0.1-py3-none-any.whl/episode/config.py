from abc import ABC, abstractmethod
from typing import Self, Sequence
from episode.semantic_representation import Composition
from copy import deepcopy
class ConfigBase:
    """
    Base class for configuration management.
    Provides methods to update configurations and validate keys.
    """
    @abstractmethod
    def __init__(self):
        pass

    def to_dict(self) -> dict:
        """Convert the configuration to a dictionary."""
        return vars(self)
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> Self:
        """Create a ConfigBase instance from a dictionary."""
        # Ensure that the dictionary contains only valid keys
        allowed_keys = vars(cls()).keys()
        for key in config_dict.keys():
            if key not in allowed_keys:
                raise ValueError(f"Unknown key in config_dict: {key}")
        return cls(**config_dict)
    
    def copy(self) -> Self:
        """Create a copy of the configuration instance."""
        dict_copy = deepcopy(self.to_dict())
        return self.from_dict(dict_copy)
    

class PropertyMapConfig(ConfigBase):
    """
    Configuration class for PropertyMapTorch.
    Inherits from ConfigBase to manage configuration settings.
    """
    def __init__(
        self,
        n_epochs: int = 1000,
        batch_size: int = 256,
        lr: float = 1.0e-1,
        device: str = 'cpu',
        dis_loss_coeff_1: float = 1e-2,
        dis_loss_coeff_2: float = 1e-6,
        last_loss_coeff: float = 100.0,
        n_tune: int = 0,
        dtw: bool = False,
    ):
        """
        Initialize the configuration for PropertyMapTorch.
        """
        self.n_epochs = n_epochs
        self.batch_size = batch_size
        self.lr = lr
        self.device = device
        self.dis_loss_coeff_1 = dis_loss_coeff_1
        self.dis_loss_coeff_2 = dis_loss_coeff_2
        self.last_loss_coeff = last_loss_coeff
        self.n_tune = n_tune
        self.dtw = dtw

class DecisionTreeConfig:
    def __init__(
            self,
            max_depth: int = 3,
            min_relative_gain_to_split: float = 1e-2,
            min_samples_leaf: int = 10,
            relative_motif_cost: float = 1e-2,
            tune_depth: bool = False,
    ):
        """Initialize the configuration for the decision tree.

        Parameters
        ----------
        max_depth : int, optional
            Maximum depth of the tree, by default 3
        min_relative_gain_to_split : float, optional
            Minimum relative gain to split, by default 1e-2
        min_samples_leaf : int, optional
            Minimum samples per leaf, by default 10
        relative_motif_cost : float, optional
            Relative cost of motif, by default 1e-2
        tune_depth : bool, optional
            Whether to tune the depth of the tree, by default False
        """
        self.max_depth = max_depth
        self.min_relative_gain_to_split = min_relative_gain_to_split
        self.min_samples_leaf = min_samples_leaf
        self.relative_motif_cost = relative_motif_cost
        self.tune_depth = tune_depth

class TorchTrainerConfig:
    """
    Configuration class for the PyTorch trainer.
    Inherits from ConfigBase to manage configuration settings.
    """
    def __init__(
        self,
        composition: Composition,
        n_features: int,
        categorical_features_indices: Sequence[int],
        cat_n_unique_dict: dict[str, int],
        x0_index: int | float | None,
        t_range: tuple[float, float],
        n_basis_functions: int,
        property_map_config: PropertyMapConfig,
        seed:int,
    ):
        """
        Initialize the configuration for the PyTorch trainer.
        """
        self.n_epochs = property_map_config.n_epochs
        self.batch_size = property_map_config.batch_size
        self.lr = property_map_config.lr
        self.device = property_map_config.device
        self.dis_loss_coeff_1 = property_map_config.dis_loss_coeff_1
        self.dis_loss_coeff_2 = property_map_config.dis_loss_coeff_2
        self.last_loss_coeff = property_map_config.last_loss_coeff
        self.n_tune = property_map_config.n_tune

        self.composition = composition
        self.n_features = n_features
        self.categorical_features_indices = categorical_features_indices
        self.cat_n_unique_dict = cat_n_unique_dict
        self.x0_index = x0_index
        self.t_range = t_range
        self.n_basis_functions = n_basis_functions
        self.x0_included = x0_index is not None

        self.seed = seed
    
    def copy(self) -> 'TorchTrainerConfig':
        """Create a copy of the configuration instance."""
        property_map_config = PropertyMapConfig(
            n_epochs=self.n_epochs,
            batch_size=self.batch_size,
            lr=self.lr,
            device=self.device,
            dis_loss_coeff_1=self.dis_loss_coeff_1,
            dis_loss_coeff_2=self.dis_loss_coeff_2,
            last_loss_coeff=self.last_loss_coeff,
            n_tune=self.n_tune
        )
        return TorchTrainerConfig(
            composition=self.composition,
            n_features=self.n_features,
            categorical_features_indices=self.categorical_features_indices,
            cat_n_unique_dict=self.cat_n_unique_dict,
            x0_index=self.x0_index,
            t_range=self.t_range,
            n_basis_functions=self.n_basis_functions,
            property_map_config=property_map_config,
            seed=self.seed
        )
