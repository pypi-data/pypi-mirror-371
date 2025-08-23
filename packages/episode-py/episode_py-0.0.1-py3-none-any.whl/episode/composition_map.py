from __future__ import annotations
from episode.semantic_representation import Composition
from typing import Sequence, Tuple
import numpy as np
from episode.types import NpArrayOrList
from episode.decision_tree import DecisionTreeClassifier
from episode import utils
from copy import deepcopy
import multiprocessing
import itertools
from tqdm import tqdm
from episode.optimize_properties import calculate_score, ScipyOptimizationAlgorithm
from episode import constants
from episode.dataset import FeatureDataset
from episode.config import DecisionTreeConfig
import pandas as pd
import os
from abc import ABC, abstractmethod

class NDCompositionMapBase(ABC):

    def __init__(self,
                 M: int,
                 composition_library_list: Sequence[Sequence[Composition]],
                 t_range: tuple[float, float],
                 x0_index_dict: dict[int, int | float | None],
                 train_on_whole_trajectory: bool = True,
                 verbose: bool = False,
                 seed: int = 0
                 ):
        self.M = M
        self.composition_library_list = composition_library_list
        self.t_range = t_range
        self.x0_index_dict  = x0_index_dict
        self.train_on_whole_trajectory = train_on_whole_trajectory
        self.verbose = verbose
        self.seed = seed
        self.per_dim = [self.init_composition_map(m) for m in range(M)]

    @abstractmethod
    def init_composition_map(self, m: int) -> CompositionMapBase:
        pass

class NDDecisionTreeCompositionMap(NDCompositionMapBase):

    def __init__(
        self,
        M: int,
        composition_library_list: Sequence[Sequence[Composition]],
        t_range: tuple[float, float],
        x0_index_dict: dict[int, int | float | None],
        train_on_whole_trajectory: bool = True,
        dt_config: DecisionTreeConfig = DecisionTreeConfig(),
        verbose: bool = False, 
        seed: int = 0):
        self.dt_config = dt_config
        super().__init__(
            M=M,
            composition_library_list=composition_library_list,
            t_range=t_range,
            x0_index_dict=x0_index_dict,
            train_on_whole_trajectory=train_on_whole_trajectory,
            verbose=verbose,
            seed=seed
        )
    
    def init_composition_map(self, m: int) -> CompositionMapBase:
        x0_index = self.x0_index_dict.get(m, None)
        return DecisionTreeCompositionMap(
            composition_library=self.composition_library_list[m],
            t_range=self.t_range,
            x0_index=x0_index,
            train_on_whole_trajectory=self.train_on_whole_trajectory,
            dt_config=self.dt_config,
            verbose=self.verbose,
            seed=self.seed
        )
    
    

class CompositionMapBase(ABC): 

    def __init__(self,
                 composition_library: Sequence[Composition],
                 t_range: tuple[float, float],
                 x0_index: int | float | None = None,
                 train_on_whole_trajectory: bool = True,
                 verbose: bool = False,
                 seed: int = 0
                 ):
        self.composition_library = composition_library
        self.t_range = t_range
        self.x0_index = x0_index
        self.train_on_whole_trajectory = train_on_whole_trajectory
        self.verbose = verbose
        self.seed = seed
        self.is_fitted = False

    def fit(self, V: FeatureDataset, T: NpArrayOrList, Y: NpArrayOrList, composition_scores: np.ndarray | None = None) -> None:
        """Fit the composition map model.

        Parameters
        ----------
        V : FeatureDataset
            The feature dataset containing the static features.
        T : NpArrayOrList
            The target values. Shape should be a list of np.ndarray or a single np.ndarray of shape (n_samples,n_timesteps).
        Y : NpArrayOrList
            The additional input features. Shape should be a list of np.ndarray or a single np.ndarray of shape (n_samples,n_timesteps).
        composition_scores : np.ndarray, optional
            The composition scores. Shape should be (n_samples, n_compositions), by default None

        Returns
        -------
        None
        """
        if composition_scores is None:
            composition_scores = self._compute_composition_scores(V, T, Y)

        self.composition_scores = composition_scores.copy()

        self._fit_from_composition_scores(V, composition_scores)
        self.is_fitted = True
    
    def predict(self, V: FeatureDataset) -> NpArrayOrList:
        """Predict the composition for the given input.

        Parameters
        ----------
        V : FeatureDataset
            The feature dataset containing the static features.
        include_indices : bool, optional
            Whether to include the indices of the compositions, by default False

        Returns
        -------
        Sequence[Composition] | Tuple[Sequence[Composition], np.ndarray]
            If `include_indices` is False, returns a sequence of Composition objects.
            If `include_indices` is True, returns a tuple containing the sequence of Composition objects and the indices of the compositions.
        """
        if not self.is_fitted:
            raise ValueError("CompositionMap is not fitted yet. Call fit() method first.")
        
        composition_index = self.predict_composition_indices(V) # shape (n_samples,)
        compositions = [self.composition_library[index] for index in composition_index] # shape (n_samples,)
        
        return compositions

    @abstractmethod
    def _fit_from_composition_scores(self, V: FeatureDataset, composition_scores: np.ndarray) -> None:
        pass

    @abstractmethod
    def predict_composition_indices(self, V: FeatureDataset) -> np.ndarray:
        pass

    @abstractmethod
    def get_specific_feature_ranges(self, X_ranges: Sequence[tuple[float, float] | set[int]], composition_index: int) -> list[tuple[float, float] | set[int]]:
        """
        Get the range of the features for a specific composition

        Parameters
        ----------
        X_ranges : list[tuple[float, float] | set[int]]
            The ranges of the features for all compositions.
        composition_index : int
            The index of the composition to get the feature ranges for.

        Returns
        -------
        list[tuple[float, float] | set[int]]
            The ranges of the features for the specified composition.
        """
        pass
    
    def _combine_dicts_to_dataframe(self,dicts: Sequence[dict]) -> pd.DataFrame:
        """
        Combines a list of dictionaries into a single pandas DataFrame.

        Args:
            dicts (list of dict): List of dictionaries in the form {'id': id, 'col': col, 'val': val}.

        Returns:
            pd.DataFrame: A DataFrame with columns as specified by 'col',
                        values as specified by 'val', and rows aligned by 'id'.
        """
        # Convert each dictionary into a smaller DataFrame
        dataframes = []
        for d in dicts:
            temp_df = pd.DataFrame({
                'id': [d['id']],
                d['col']: [d['val']]
            })
            dataframes.append(temp_df)

        # Merge all DataFrames on 'id'
        result_df = pd.concat(dataframes, ignore_index=True).pivot_table(
            index='id', aggfunc='first'
        ).reset_index()

        return result_df

    def _compute_composition_scores(self, V: FeatureDataset, T: NpArrayOrList, Y: NpArrayOrList) -> np.ndarray:

        n_samples = V.n_samples

        train_on_whole_trajectory = self.train_on_whole_trajectory

        if self.x0_index is not None:
            if isinstance(self.x0_index,int):
                x0 = V.array[:,self.x0_index]
            elif isinstance(self.x0_index,float):
                x0 = [self.x0_index] * n_samples
            else:
                raise ValueError('x0_index should be an integer or a float')
        else:
            x0 = [None] * n_samples

        composition_ids = list(range(len(self.composition_library)))
        
        info_list = []
        for composition_id in composition_ids:
            samples = zip(deepcopy(x0), deepcopy(T), deepcopy(Y))
            sample_ids = range(n_samples)
            composition = self.composition_library[composition_id]

            composition_id_list = deepcopy([composition_id] * n_samples)
            composition_list = deepcopy([composition] * n_samples)

            info = zip(samples,
                        composition_id_list,
                        composition_list,
                        [self.t_range] * n_samples, 
                        [self.seed] * n_samples, sample_ids, 
                        [train_on_whole_trajectory] * n_samples)
            info_list.append(info)
        all_infos = itertools.chain(*info_list)
        with multiprocessing.Pool() as p:
            composition_scores = list(tqdm(p.imap(process_sample_one_comp, all_infos), total=n_samples*len(composition_ids)))
        # Create a dataframe
        composition_scores_df = self._combine_dicts_to_dataframe(composition_scores)

        # Check if there are any NaN values
        if composition_scores_df.isnull().values.any():
            raise ValueError('NaN values found in the composition scores')

        # sort by id
        composition_scores_df = composition_scores_df.sort_values(by='id')

        # Remove id column
        composition_scores_df = composition_scores_df.drop(columns=['id'])

        # Reorder compositions
        composition_scores_df = composition_scores_df[composition_ids]

        composition_scores = composition_scores_df.values

        return composition_scores
    
    def save_composition_scores_df(self,folder='composition_scores',name="composition_scores"):
        if not os.path.exists(folder):
            os.makedirs(folder)
        composition_scores_df = pd.DataFrame(self.composition_scores)
        if name != "":
            filename = f'{name}.csv'
        else:
            filename = 'composition_scores.csv'
        composition_scores_df.to_csv(os.path.join(folder,filename),index=False)


def process_sample_one_comp(info: Tuple[Tuple[float | None, np.ndarray, np.ndarray], int, Composition, Tuple[float, float], int, int, bool]) -> dict:
    opt = ScipyOptimizationAlgorithm('L-BFGS-B')
    loss_fn = lambda y_true, y_pred: np.mean((y_true - y_pred) ** 2)
    sample, composition_id, composition, t_range, seed, sample_id, train_on_all_data = info
    x0, t, y = sample
    sample_scores = {'id': sample_id}
    if not composition.is_bounded():
        train_on_all_data = train_on_all_data
    else:
        train_on_all_data = True
    loss, properties = calculate_score(
        composition, 
        t_range,
        t,
        y, 
        x0,
        optimization_alg=opt,
        loss_fn=loss_fn,
        train_on_all=train_on_all_data, 
        evaluate_on_all=True,
        train_size=0.8,
        seed=seed
    )
    if np.isnan(loss):
        loss = constants.INF
    sample_scores['col'] = composition_id
    sample_scores['val'] = loss # type: ignore
    return sample_scores

class DecisionTreeCompositionMap(CompositionMapBase):

    def __init__(
            self,
            composition_library: Sequence[Composition], 
            t_range: tuple[float, float],
            x0_index: int | float | None = None, 
            train_on_whole_trajectory: bool = True,
            dt_config: DecisionTreeConfig = DecisionTreeConfig(),
            verbose: bool = False, 
            seed: int = 0):
        """
        Args:
        composition_library: a sequence of Composition objects
        dt_config: a dictionary with the configuration for the decision tree classifier
        categorical_features_indices: a sequence of integers representing the indices of the categorical features
        x0_index: an integer or float representing the index of the initial condition, or None if not included
        verbose: a boolean indicating whether to print the decision tree structure
        """
        super().__init__(
            composition_library=composition_library,
            t_range=t_range,
            x0_index=x0_index,
            train_on_whole_trajectory=train_on_whole_trajectory,
            verbose=verbose,
            seed=seed
        )
        self.dt_config = dt_config

    def _fit_from_composition_scores(self, V: FeatureDataset, composition_scores: np.ndarray) -> None:
        """Fit the decision tree classifier from the composition scores.
        Parameters
        ----------
        V : FeatureDataset
            The feature dataset containing the static features.
        composition_scores : np.ndarray
            The composition scores. Shape should be (n_samples, n_compositions).
        """
        # Penalize the composition scores based on the length of the compositions
        # This is to encourage the decision tree to prefer shorter compositions
        # The penalty is relative to the length of the composition
        composition_lengths = np.array([len(comp) for comp in self.composition_library]).reshape(1,-1)
        composition_scores = composition_scores.copy() * (1 + composition_lengths * self.dt_config.relative_motif_cost)
        
        if self.dt_config.tune_depth:
            best_depth = self._tune_depth(V, composition_scores)
        else:
            best_depth = self.dt_config.max_depth

        # Fit the decision tree with the best depth on the whole dataset

        dt = DecisionTreeClassifier(max_depth=best_depth,
                                    metric_name='error',
                                    offset=self.dt_config.min_relative_gain_to_split,
                                    min_samples_leaf=self.dt_config.min_samples_leaf,
                                    categorical_features=V.categorical_features_indices)

        dt.fit(V.array, composition_scores)

        self.decision_tree_classifier = dt

    def predict_composition_indices(self, V: FeatureDataset) -> np.ndarray:
        """Predict the composition indices for the given input.

        Parameters
        ----------
        V : FeatureDataset
            The feature dataset containing the static features.
        Returns
        -------
        np.ndarray
            The predicted composition indices. Shape will be (n_samples,).
        """
        return self.decision_tree_classifier.predict(V.array) # shape (n_samples,)
        
    def print(self):
        if self.decision_tree_classifier is None:
            raise ValueError("Decision tree classifier is not fitted yet.")
        self.decision_tree_classifier.print_tree()

    def get_specific_feature_ranges(self, X_ranges: Sequence[tuple[float, float] | set[int]], composition_index: int) -> list[tuple[float, float] | set[int]]:
        """
        Get the range of the features for a specific composition.

        Parameters
        ----------
        X_ranges : list[tuple[float, float] | set[int]]
            The ranges of the features for all compositions.
        composition_index : int
            The index of the composition to get the feature ranges for.
        
        Returns
        -------
        list[tuple[float, float] | set[int]]
            The ranges of the features for the specified composition.
        """
        if self.decision_tree_classifier is None:
            raise ValueError("Decision tree classifier is not fitted yet.")
        return self.decision_tree_classifier.get_updated_feature_ranges(X_ranges)[composition_index]

    def _tune_depth(self, V: FeatureDataset, composition_scores: np.ndarray) -> int:
        """_summary_

        Parameters
        ----------
        V : FeatureDataset
            The feature dataset containing the static features.
        composition_scores : np.ndarray
            Composition scores of shape (n_samples, n_compositions).

        Returns
        -------
        int
            The best depth found during tuning.
        """
        # Divde v into train and validation sets and fit the decision tree
        train_indices, val_indices = utils.get_train_val_indices(V.n_samples, seed=self.seed)

        V_train = V.array[train_indices]
        composition_scores_train = composition_scores[train_indices]

        V_val = V.array[val_indices]
        composition_scores_val = composition_scores[val_indices]

        results_of_tuning = {}

        for tested_depth in range(0,self.dt_config.max_depth+1):
            dt = DecisionTreeClassifier(max_depth=tested_depth,
                                        metric_name='error',
                                        offset=self.dt_config.min_relative_gain_to_split,
                                        min_samples_leaf=self.dt_config.min_samples_leaf,
                                        categorical_features=V.categorical_features_indices)
            dt.fit(V_train,composition_scores_train)
            pred_train_indices = dt.predict(V_train)
            pred_val_indices = dt.predict(V_val)
            train_loss = np.mean([composition_scores_train[i,pred_train_indices[i]] - np.min(composition_scores_train[i,:]) for i in range(len(pred_train_indices))])
            val_loss = np.mean([composition_scores_val[i,pred_val_indices[i]] - np.min(composition_scores_val[i,:]) for i in range(len(pred_val_indices))])
            print(f"Depth: {tested_depth}, Train loss: {train_loss}, Val loss: {val_loss}")
            results_of_tuning[tested_depth] = val_loss
        
        best_depth = min(results_of_tuning, key=lambda depth: results_of_tuning[depth])

        if self.verbose:
            print(f'Best depth: {best_depth}')

        return best_depth

        
    

