from __future__ import annotations
import numpy as np
import torch
from episode.semantic_representation import Composition, Properties
from episode.torch_model import FullModel, TransitionPointModule
from abc import ABC, abstractmethod
from episode.gam import GAM, ShapeFunction
from episode import utils
from typing import Sequence, Callable, Tuple, Mapping
from episode.torch_model import PropertyModule
from episode.composition_map import CompositionMapBase
from episode.dataset import FeatureDataset
from episode.types import NpArrayOrList
from episode.basis import BasisFunctions, OneHotBasisFunctions
from episode.config import PropertyMapConfig, TorchTrainerConfig
from episode.training import fit_property_module, PropertyModuleTrainer
from episode.trajectory_predictor import C0TrajectoryPredictor


class NDPropertyMapBase(ABC):

    def __init__(self, 
                M: int,
                x0_index_dict: dict[int, int | float | None] = {},
                X_ranges: Sequence[tuple[float, float] | set[int]] | None = None,
                verbose: bool = True):
        self.M = M
        self.x0_index_dict = x0_index_dict
        self.X_ranges = X_ranges
        self.verbose = verbose
        self.per_dim = [self.init_property_map(m) for m in range(M)]
         
    @abstractmethod
    def init_property_map(self, m:int) -> PropertyMapBase:
        """Initialize the 1D property map."""
        pass

class NDPropertyMap(NDPropertyMapBase):

    def __init__(
        self,
        M: int,
        basis_functions: BasisFunctions,
        x0_index_dict: dict[int, int | float | None],
        t_range: tuple[float, float],
        X_ranges: Sequence[tuple[float, float] | set[int]] | None = None,
        config: PropertyMapConfig = PropertyMapConfig(),
        seed: int = 0,
        verbose: bool = True
    ):
        self.basis_functions = basis_functions
        self.config = config
        self.seed = seed
        self.t_range = t_range
        super().__init__(M, x0_index_dict, X_ranges, verbose)
       

    def init_property_map(self, m:int) -> PropertyMapBase:
        """Initialize the 1D property map."""
        x0_index = self.x0_index_dict.get(m, None)
        return PropertyMap( 
            basis_functions=self.basis_functions,
            x0_index=x0_index,
            t_range=self.t_range,
            X_ranges=self.X_ranges,
            config=self.config,
            seed=self.seed,
            verbose=self.verbose
        )

class PropertyMapBase(ABC):

    def __init__(self, 
                x0_index: int | float | None = None,
                X_ranges: Sequence[tuple[float, float] | set[int]] | None = None,
                verbose: bool = True):

        self.x0_index = x0_index
        self.X_ranges = X_ranges
        self.verbose = verbose
        self.per_composition: dict[Composition, SinglePropertyMap] = {}
        self.is_fitted = False

    def _filter_by_mask(self, 
                        V: FeatureDataset, 
                        T: NpArrayOrList, 
                        Y: NpArrayOrList, 
                        X0: np.ndarray | None, 
                        mask: np.ndarray) -> tuple[FeatureDataset, NpArrayOrList, NpArrayOrList, np.ndarray | None]:
        V_filtered = V.filter_by_mask(mask)
        T_numpy_filtered = utils.filter_by_mask(T,mask)
        Y_numpy_filtered = utils.filter_by_mask(Y,mask)
        X0_numpy_filtered = None
        if self.x0_index is not None:
            assert X0 is not None, "X0 must be defined if x0_index is provided"
            X0_numpy_filtered = X0[mask]
        assert X0_numpy_filtered is not None, "X0_numpy_filtered must not be None"
        return V_filtered, T_numpy_filtered, Y_numpy_filtered, X0_numpy_filtered # type: ignore
        

    def fit(self, V: FeatureDataset, T: NpArrayOrList, Y: NpArrayOrList, composition_map: CompositionMapBase):
        """
        Fit the semantic predictor to the data

        Parameters:
        ----------
        V: FeatureDataset
            The input feature dataset.
        T: NpArrayOrList
            The target values.
        Y: NpArrayOrList
            The additional target values.

        """
        self.composition_map = composition_map
        if not self.composition_map.is_fitted:
            raise RuntimeError("Composition map is not fitted. Call fit() on the composition map before fitting the property map.")
        
        val_loss = 0
        n_val_samples = 0

        X_ranges = self._get_global_X_ranges(V)

        X0 = None
        if self.x0_index is not None:
            if isinstance(self.x0_index,int):
                X0 = V.array[:,[self.x0_index]]
            elif isinstance(self.x0_index,float):
                X0 = np.tile(self.x0_index, (V.n_samples, 1))
            else:
                raise ValueError('x0_index must be an integer or a float')
        
        predicted_composition_indices = self.composition_map.predict_composition_indices(V)
        assert isinstance(predicted_composition_indices, np.ndarray), "predicted_composition_indices must be a numpy array"
        unique_composition_indices = np.unique(predicted_composition_indices)
        
        for composition_index in unique_composition_indices:

            mask = predicted_composition_indices == composition_index
            V_filtered, T_numpy_filtered, Y_numpy_filtered, X0_numpy_filtered = self._filter_by_mask(V, T, Y, X0, mask)

            specific_V_ranges = self.composition_map.get_specific_feature_ranges(X_ranges,composition_index)

            composition = self.composition_map.composition_library[composition_index]

            property_map, val_loss_per_branch, n_val_indices = self.fit_for_single_composition(
                composition=composition,
                V=V_filtered,
                T=T_numpy_filtered,
                Y=Y_numpy_filtered,
                X0=X0_numpy_filtered,
                specific_V_ranges=specific_V_ranges,
            )

            val_loss += val_loss_per_branch * n_val_indices
            n_val_samples += n_val_indices
            self.per_composition[composition] = property_map

            if self.verbose:
                print(f"Validation loss for composition {composition}: {val_loss_per_branch}")

        if self.verbose:
            print(f'All property maps fitted with validation loss {val_loss/n_val_samples} over {n_val_samples} samples.')
        self.is_fitted = True


    def predict(self, composition: Composition, V: FeatureDataset) -> Properties:
        """Predict the properties for a given composition and input features.

        Parameters
        ----------
        composition : Composition
            The composition for which to predict properties.
        V : FeatureDataset
            A dataset containing the input features.
        Returns
        -------
        Properties
            An instance of Properties containing the predicted properties.
        """
        if not self.is_fitted:
            raise RuntimeError("PropertyMap is not fitted. Call fit() before predict().")
        if composition not in self.per_composition:
            raise ValueError(f"Composition {composition} not found in property maps.")
        return self.per_composition[composition].predict(V.array)

    def _get_global_X_ranges(self, V: FeatureDataset) -> Sequence[Tuple[float,float] | set[int]]:
        """
        Get the range of the initial condition

        Parameters:
        -----------
        V: FeatureDataset
            The feature dataset containing the static features.
        
        Returns:
        --------
        X_ranges: list of tuples or sets
        """
        X_ranges: Sequence[Tuple[float,float] | set[int]] = []
        if self.X_ranges is None:
            for i in range(V.n_features):
                if i in V.categorical_features_indices:
                    x_range_set: set[int] = set(range(len(V.categories[i])))
                    X_ranges.append(x_range_set)
                else:
                    x_range_tuple: Tuple[float, float] = (V.array[:,i].min(), V.array[:,i].max())
                    X_ranges.append(x_range_tuple)
            self.X_ranges = X_ranges
        else:
            X_ranges = self.X_ranges
        return X_ranges

    @abstractmethod
    def fit_for_single_composition(
        self, 
        composition: Composition, 
        V: FeatureDataset, 
        T: NpArrayOrList, 
        Y: NpArrayOrList, 
        X0: np.ndarray | None,
        specific_V_ranges: Sequence[Tuple[float, float] | set[int]]
        ) -> tuple[SinglePropertyMap, float, int]:
        pass

class PropertyMap(PropertyMapBase):
    def __init__(
        self,
        basis_functions: BasisFunctions,
        x0_index: int | float | None,
        t_range: tuple[float, float],
        X_ranges: Sequence[tuple[float, float] | set[int]] | None = None,
        config: PropertyMapConfig = PropertyMapConfig(),
        seed: int = 0,
        verbose: bool = False):
        super().__init__(x0_index, X_ranges, verbose)
        self.basis_functions = basis_functions
        self.one_hot_basis_functions = OneHotBasisFunctions()
        self.config = config
        self.seed = seed
        self.torch_models: dict[Composition, FullModel] = {}
        self.t_range = t_range

    def _pad_T_Y(self, T: NpArrayOrList, Y: NpArrayOrList) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Pad T and Y to the same length if they are sequences.
        
        Parameters
        ----------
        T : NpArrayOrList
            Time points. Should be a numpy array of shape (n_samples, n_timesteps) or a sequence of 1D numpy arrays.
        Y : NpArrayOrList
            Target values. Should be a numpy array of shape (n_samples, n_timesteps) or a sequence of 1D numpy arrays.
        Returns
        -------
        tuple[np.ndarray, np.ndarray, np.ndarray]
            The padded time points, target values, and mask.
        """
        if isinstance(T, Sequence):
            T_new, mask_T = utils.pad_and_mask(T)
        else:
            T_new = T
            mask_T = np.ones_like(T, dtype=bool)
        if isinstance(Y, Sequence):
            Y_new, mask_Y = utils.pad_and_mask(Y)
        else:
            Y_new = Y
            mask_Y = np.ones_like(Y, dtype=bool)
        assert np.array_equal(mask_T, mask_Y), "T and Y must have the same mask."
        assert isinstance(mask_T, np.ndarray), "mask_T must be a numpy array."
        mask = mask_T.astype(float)
        assert isinstance(T_new, np.ndarray), "T_new must be a numpy array."
        assert isinstance(Y_new, np.ndarray), "Y_new must be a numpy array."
        return T_new, Y_new, mask

    def fit_for_single_composition(
        self,
        composition: Composition,
        V: FeatureDataset,
        T: NpArrayOrList,
        Y: NpArrayOrList,
        X0: np.ndarray | None,
        specific_V_ranges: Sequence[tuple[float, float] | set[int]]
    ) -> tuple[SinglePropertyMap, float, int]:
        
        V_numpy_filtered = V.array
        T_numpy_filtered = T
        Y_numpy_filtered = Y
        B_numpy_filtered = self.basis_functions.compute(V_numpy_filtered,specific_V_ranges)

        n_samples = V_numpy_filtered.shape[0]
        n_features = V_numpy_filtered.shape[1]

        T_numpy_filtered, Y_numpy_filtered, mask = self._pad_T_Y(T_numpy_filtered, Y_numpy_filtered)

        if len(V.categorical_features_indices) > 0:
            B_cat_numpy_filtered, cat_n_unique_dict = self.one_hot_basis_functions.compute(V_numpy_filtered,specific_V_ranges)
        else:
            B_cat_numpy_filtered = np.zeros((n_samples, 1))
            cat_n_unique_dict = {}

        if self.x0_index is not None:
            X0_numpy_filtered = X0
            assert isinstance(X0_numpy_filtered, np.ndarray)
        else:
            X0_numpy_filtered = np.full((n_samples, 1), np.nan)
        
        V_filtered, \
        B_filtered, \
        B_cat_filtered, \
        T_filtered, \
        Y_filtered, \
        X0_tensor, \
        mask_filtered = utils.get_tensors(
            self.config.device,
            V_numpy_filtered,
            B_numpy_filtered,
            B_cat_numpy_filtered,
            T_numpy_filtered,
            Y_numpy_filtered,
            X0_numpy_filtered,
            mask
        )
   
        train_indices, val_indices = utils.get_train_val_indices(n_samples, seed=self.seed)

        train_dataset = torch.utils.data.TensorDataset(V_filtered[train_indices], B_filtered[train_indices], T_filtered[train_indices], Y_filtered[train_indices], X0_tensor[train_indices], B_cat_filtered[train_indices], mask_filtered[train_indices])
        val_dataset = torch.utils.data.TensorDataset(V_filtered[val_indices], B_filtered[val_indices], T_filtered[val_indices], Y_filtered[val_indices], X0_tensor[val_indices], B_cat_filtered[val_indices], mask_filtered[val_indices])
        
        torch_config = TorchTrainerConfig(
            composition=composition,
            n_features=n_features,
            categorical_features_indices=V.categorical_features_indices,
            cat_n_unique_dict=cat_n_unique_dict,
            x0_index=self.x0_index,
            t_range=self.t_range,
            n_basis_functions=self.basis_functions.n_basis,
            property_map_config=self.config,
            seed=self.seed
        )

        # torch_config['soft_constraint'] = None
        # if soft_constraints is not None:
        #     if composition in soft_constraints:
        #         torch_config['soft_constraint'] = soft_constraints[composition]

        val_loss_per_branch, model = fit_property_module(PropertyModuleTrainer,torch_config,train_dataset,val_dataset,verbose=self.verbose)
        assert isinstance(model, PropertyModuleTrainer)
        torch_model = model.model
        self.torch_models[composition] = torch_model
        property_map_extractor = PropertyMapExtractor(
            self.config,
            self.basis_functions,
            self.one_hot_basis_functions,
            V.categorical_features_indices,
            V.feature_names,
            V.categories,
            x0_index=self.x0_index)
        assert isinstance(V_numpy_filtered, np.ndarray)
        histograms = self._construct_histograms(V_numpy_filtered, specific_V_ranges)
        property_map = property_map_extractor.construct_single_property_map(composition,model.model.property_module,specific_V_ranges, histograms)

        return  property_map, val_loss_per_branch, len(val_indices),
    
    def _construct_histograms(self, V_array: np.ndarray, specific_V_ranges: Sequence[set[int] | Tuple[float,float]]) -> Sequence[dict[int,int] | Tuple[np.ndarray,np.ndarray]]:

        histograms = []
        for feature_index in range(V_array.shape[1]):
            if isinstance(specific_V_ranges[feature_index],set):
                possible_classes = sorted(list(specific_V_ranges[feature_index]))
                histogram = {}
                for value in possible_classes:
                    histogram[value] = np.sum(V_array[:,feature_index] == value)
            else:
                histogram = np.histogram(V_array[:,feature_index], bins=20)
            histograms.append(histogram)
        return histograms
        

class PropertyFunction(ABC):

    @abstractmethod
    def predict(self, V: np.ndarray) -> np.ndarray:
        """Predict the output for a given input.

        Parameters
        ----------
        X : np.ndarray
            Input data of shape (n_samples, n_features).
        

        Returns
        -------
        np.ndarray
            Predicted output of shape (n_samples,).
        """
        pass

class TransitionPointPredictor(PropertyFunction):

    def __init__(self, gam: GAM):
        """
        Parameters
        ----------
        transition_point_module : TransitionPointModule
            The module that predicts the transition points.
        transition_point_index : int
            The index of the transition point to predict.
        coordinate : str
            The coordinate to predict ('x' or 't').
        """
        self.gam = gam

    def predict(self, V: np.ndarray) -> np.ndarray:
        """_summary_

        Parameters
        ----------
        V : np.ndarray
            A numpy array of shape (batch_size, n_features) containing the input features.

        Returns
        -------
        np.ndarray
            A numpy array containing the predicted values for the specified transition point and coordinate.
            Shape is (batch_size,).
        """
        return self.gam.predict(V)
    
class GAMBasedDerivativePredictor(PropertyFunction):

    def __init__(self, composition: Composition, gam: GAM, boundary: str, order: int, transition_point_predictors: dict):
        """Initialize the DerivativePredictor with a dictionary of predictors.

        Parameters
        ----------
        gam : GAM
            The GAM instance used for predictions.
        boundary : str
            The boundary to predict ('start' or 'end').
        order : int
            The order of the derivative to predict (1 or 2).
        """
        self.composition = composition
        self.gam = gam
        self.boundary = boundary
        self.order = order
        self.transition_point_predictors = transition_point_predictors

    def _extract_coordinates(self, V, motif_index):
        coordinate_1 = np.zeros((V.shape[0], 2))
        coordinate_2 = np.zeros((V.shape[0], 2))
        coordinate_1[:,0] = self.transition_point_predictors[(motif_index, "t")].predict(V)
        coordinate_1[:,1] = self.transition_point_predictors[(motif_index, "x")].predict(V)
        coordinate_2[:,0] = self.transition_point_predictors[(motif_index+1, "t")].predict(V)
        coordinate_2[:,1] = self.transition_point_predictors[(motif_index+1, "x")].predict(V)
        return coordinate_1, coordinate_2

    def predict(self, V: np.ndarray) -> np.ndarray:
        """Predict the value of the derivative.
        Parameters
        ----------
        V : np.ndarray
            A numpy array of shape (batch_size, n_features) containing the input features.
        
        Returns
        -------
        np.ndarray
            A numpy array containing the predicted values for the specified boundary and order.
            Shape is (batch_size,).
        """
        coordinate_1 = np.zeros((V.shape[0], 2))
        coordinate_2 = np.zeros((V.shape[0], 2))
        if self.boundary == 'start':
            motif_index = 0
            side = "left"
            coordinate_1, coordinate_2 = self._extract_coordinates(V, motif_index)
            result = utils._transform_first_derivative(
                self.composition,
                self.gam.predict(V),
                coordinate_1,
                coordinate_2,
                motif_index,
                side)
        elif self.boundary == 'end':
            if self.order == 1:
                if not self.composition.is_bounded():
                    result = self.gam.predict(V)
                else:
                    motif_index = len(self.composition) - 1
                    side = "right"
                    coordinate_1, coordinate_2 = self._extract_coordinates(V, motif_index)
                    result = utils._transform_first_derivative(
                        self.composition,
                        self.gam.predict(V),
                        coordinate_1,
                        coordinate_2,
                        motif_index,
                        side)
            elif self.order == 2:
                result = self.gam.predict(V)
            else:
                raise ValueError(f"Invalid order {self.order}. Must be 1 or 2.")
        else:
            raise ValueError(f"Invalid boundary {self.boundary}. Must be 'start' or 'end'.")
        assert isinstance(result, np.ndarray), "The result should be a numpy array."
        return result.reshape(-1,1)
        


class GAMBasedInfiniteMotifPredictor(PropertyFunction):
    def __init__(self, composition: Composition, gams: Sequence[GAM], property_index: int, last_value_predictor, first_derivative_at_end_predictor):
        """Initialize the GAMBasedInfiniteMotifPredictor.
        Parameters
        ----------
        composition : Composition
        """
        self.composition = composition
        self.gams = gams
        self.property_index = property_index
        self.last_value_predictor = last_value_predictor
        self.first_derivative_at_end_predictor = first_derivative_at_end_predictor

    def predict(self, V: np.ndarray) -> np.ndarray:
        """Predict the value of an infinite motif property.
        Parameters
        ----------
        V : np.ndarray
            A numpy array of shape (batch_size, n_features) containing the input features.

        Returns
        -------
        np.ndarray
            A numpy array containing the predicted values for the specified infinite motif property.
            Shape is (batch_size,).
        """
        raw_properties = np.zeros((V.shape[0], len(self.gams)))
        for i, gam in enumerate(self.gams):
            raw_properties[:, i] = gam.predict(V)
        last_value = self.last_value_predictor.predict(V)
        first_derivative_at_end = self.first_derivative_at_end_predictor.predict(V)
        result = utils.transform_properties(self.composition, raw_properties, last_value.flatten(), first_derivative_at_end.flatten())[:, self.property_index]
        assert isinstance(result, np.ndarray), "The result should be a numpy array."
        return result


class ZeroPropertyFunction(PropertyFunction):

    def predict(self,V):
        return np.zeros(V.shape[0])
    
class CustomPropertyFunction(PropertyFunction):

    def __init__(self,function):
        self.function = function
    
    def predict(self, V):
        return self.function(V)

class NaNPropertyFunction(PropertyFunction):

    def predict(self,V):
        n_samples = V.shape[0]
        result = np.full((n_samples,),np.nan)
        return result
    
class CubicDerivativePredictor(PropertyFunction):

    def __init__(
            self, 
            composition: Composition, 
            transition_point_predictors: dict[tuple[int, str], PropertyFunction], 
            first_derivative_at_start_predictor: PropertyFunction,
            order: int):
        self.composition = composition
        self.transition_point_predictors = transition_point_predictors
        self.first_derivative_at_start_predictor = first_derivative_at_start_predictor
        self.order = order
        self.trajectory_predictor = C0TrajectoryPredictor()

    def predict(self, V: np.ndarray) -> np.ndarray:
        """Predict the value of the derivative based on the cubic.
        Parameters
        ----------
        V : np.ndarray
            A numpy array of shape (batch_size, n_features) containing the input features.
        
        Returns
        -------
        np.ndarray
            A numpy array containing the predicted values for the specified order.
            Shape is (batch_size,).
        """
        n_transition_points = len(self.transition_point_predictors) // 2
        transition_points = np.zeros((V.shape[0], n_transition_points, 2))
        for i in range(n_transition_points):
            transition_points[:, i, 0] = self.transition_point_predictors[(i, "t")].predict(V)
            transition_points[:, i, 1] = self.transition_point_predictors[(i, "x")].predict(V)
        first_derivative_at_start = self.first_derivative_at_start_predictor.predict(V)

        if self.order == 1:
            result = self.trajectory_predictor._get_first_derivative_at_end_from_cubic(
                composition=self.composition,
                transition_points=transition_points,
                first_derivative_start=first_derivative_at_start
            )
        elif self.order == 2:
            result = self.trajectory_predictor._get_second_derivative_at_end_from_cubic(
                composition=self.composition,
                transition_points=transition_points,
                first_derivative_start=first_derivative_at_start
            )
        else:
            raise ValueError(f"Invalid order {self.order}. Must be 1 or 2.")
        assert isinstance(result, np.ndarray), "The result should be a numpy array."
        return result


class SinglePropertyMap:

    def __init__(self, 
                 composition : Composition,
                 transition_point_predictor : dict[tuple[int, str], PropertyFunction],
                 derivative_predictor : dict[tuple[str, int], PropertyFunction],
                 infinite_motif_predictor : Sequence[PropertyFunction] | None):
        
        """
        Args:
        composition: a tuple of strings representing the composition
        transition_point_predictor: a dictionary with keys (transition_point_index: int,coordinate: {'x','t'}) and values of type GAM
        derivative_predictor: a dictionary with keys (boundary: {'start','end'},order: {1,2}) and values of type GAM
        infinite_motif_predictor: a list of GAM
        """
        
        self.composition = composition
        self.transition_point_predictor = transition_point_predictor
        self.derivative_predictor = derivative_predictor
        self.infinite_motif_predictor = infinite_motif_predictor
        self.n_transition_points = len(transition_point_predictor) // 2
    
    def predict(self, V: np.ndarray) -> Properties:
        """Predict the properties for a given input.
        Parameters
        ----------
        V : np.ndarray
            A numpy array of shape (batch_size, n_features) containing the input features.
        Returns
        -------
        Properties
            An instance of Properties containing the predicted properties.
        """

        transition_points = np.zeros((V.shape[0], self.n_transition_points, 2))
        for i in range(self.n_transition_points):
            transition_points[:, i, 0] = self.transition_point_predictor[(i, "t")].predict(V)
            transition_points[:, i, 1] = self.transition_point_predictor[(i, "x")].predict(V)
        derivatives = {}
        for key in self.derivative_predictor.keys():
            derivatives[key] = self.derivative_predictor[key].predict(V).reshape(-1, 1)
        if not self.composition.is_bounded():
            assert self.infinite_motif_predictor is not None, "The infinite motif predictor should not be None for unbounded compositions."
            infinite_motif_properties = np.stack([predictor.predict(V) for predictor in self.infinite_motif_predictor], axis = 1)
        else:
            infinite_motif_properties = None
        return Properties("numpy",
                        self.composition,
                        transition_points, 
                        derivatives[('start',1)],
                        derivatives[('end',1)],
                        derivatives[('end',2)],
                        infinite_motif_properties,
                        unbounded_motif_properties_raw=False)



class PropertyMapExtractor:

    def __init__(self,config: PropertyMapConfig,
                 basis_functions: BasisFunctions,
                 one_hot_basis_functions: OneHotBasisFunctions,
                 categorical_features_indices: Sequence[int],
                 feature_names: Sequence[str],
                 categorical_features_categories: Mapping[int, Sequence[str]],
                 x0_index: int | float | None):
        self.config = config
        self.basis_functions = basis_functions
        self.one_hot_basis_functions = one_hot_basis_functions
        self.categorical_features_indices = categorical_features_indices
        self.categorical_features_categories = categorical_features_categories
        self.feature_names = feature_names
        self.x0_index = x0_index
        self.x0_included = x0_index is not None

    
    def _get_b_X0_tensors(self,x,feature_index,specific_V_ranges):
        X0_tensor = None
        if self.x0_included:
            if isinstance(self.x0_index,int):
                if feature_index == self.x0_index:
                    X0_tensor = utils.get_tensors(self.config.device,x.reshape(-1,1))[0]
            elif isinstance(self.x0_index,float):
                X0_tensor = utils.get_tensors(self.config.device,np.full((len(x),1),self.x0_index))[0]
            else:
                raise ValueError("Invalid x0_index")
            
        X = np.zeros((len(x),len(specific_V_ranges)))
        X[:,feature_index] = x
        if feature_index in self.categorical_features_indices:
            b = self.one_hot_basis_functions.compute_single(X,specific_V_ranges,feature_index)
        else:
            B = self.basis_functions.compute(X,specific_V_ranges)
            cont_feature_index = utils.from_feature_index_to_cont_feature_index(feature_index,self.categorical_features_indices)
            b = B[:,cont_feature_index,:]
        b_tensor = utils.get_tensors(self.config.device,b)[0]

        return b_tensor,X0_tensor
    
    def _get_B_X0_tensors(self,X,specific_V_ranges):
        B = self.basis_functions.compute(X,specific_V_ranges)
        if len(self.categorical_features_indices) > 0:
            B_cat, _ = self.one_hot_basis_functions.compute(X,specific_V_ranges)
        else:
            B_cat = np.zeros_like(X)[:,[0]]

        B_tensor, B_cat_tensor = utils.get_tensors(self.config.device,B, B_cat)
        if self.x0_included:
            if isinstance(self.x0_index,int):
                X0_tensor = utils.get_tensors(self.config.device,X[:,[self.x0_index]])[0]
            elif isinstance(self.x0_index,float):
                X0_tensor = utils.get_tensors(self.config.device,np.full((len(X),1),self.x0_index))[0]
            else:
                raise ValueError("Invalid x0_index")
        else:
            X0_tensor = None
        B = (B_tensor,B_cat_tensor)

        return B,X0_tensor

    def _extract_shape_function_of_transition_point(self, torch_model: PropertyModule, ind, coordinate, feature_index, specific_V_ranges, histogram=None, categories=None, name=None):

        def shape_function(x):
            b_tensor,X0_tensor = self._get_b_X0_tensors(x,feature_index,specific_V_ranges)
            torch_model.eval()
            with torch.no_grad():
                pred = torch_model.transition_point_module._predict_shape_function(ind,coordinate,feature_index,b_tensor,X0_tensor).detach().cpu()
            return pred.numpy()
        
        return ShapeFunction(shape_function,specific_V_ranges[feature_index], categories=categories, histogram=histogram, name=name)
    
    def _extract_bias_of_transition_point(self, torch_model: PropertyModule, ind, coordinate):

        torch_model.eval()
        with torch.no_grad():
            pred = torch_model.transition_point_module._predict_bias(ind,coordinate).detach().cpu()
        return pred.numpy()
    
    def _extract_gam_of_transition_point(self, torch_model: PropertyModule, ind, coordinate, specific_V_ranges, histograms=None, all_categories={}, feature_names=None):

        n_features = len(specific_V_ranges)
        
        shape_functions = []
        for i in range(n_features):
            categories = all_categories.get(i)
            histogram = histograms[i] if histograms else None
            name = feature_names[i] if feature_names else None
            shape_functions.append(self._extract_shape_function_of_transition_point(torch_model, ind, coordinate, i, specific_V_ranges, histogram=histogram, categories=categories, name=name))
        bias = self._extract_bias_of_transition_point(torch_model, ind, coordinate)
        return GAM(shape_functions,bias)
    
    def _extract_shape_function_of_infinite_property(self, torch_model: PropertyModule, ind, feature_index, specific_V_ranges, categories=None,histogram=None, name=None):

        
        def shape_function(x):
            b_tensor,X0_tensor = self._get_b_X0_tensors(x,feature_index,specific_V_ranges)
            torch_model.eval()
            with torch.no_grad():
                assert torch_model.final_motif_property_module is not None, "The torch model does not have a final motif property module."
                pred = torch_model.final_motif_property_module._predict_shape_function(ind,feature_index,b_tensor,X0_tensor).detach().cpu()
            return pred.numpy()
        
        return ShapeFunction(shape_function,specific_V_ranges[feature_index], categories=categories, histogram=histogram, name=name)

    def _extract_bias_of_infinite_property(self, torch_model: PropertyModule, ind):

        torch_model.eval()
        with torch.no_grad():
            assert torch_model.final_motif_property_module is not None, "The torch model does not have a final motif property module."
            pred = torch_model.final_motif_property_module._predict_bias(ind).detach().cpu()
        return pred.numpy()
    
    def _extract_gam_of_infinite_property(self, torch_model: PropertyModule, ind, specific_V_ranges, histograms=None, all_categories={}, feature_names=None):

        n_features = len(specific_V_ranges)

        shape_functions = []
        for i in range(n_features):
            categories = all_categories.get(i)
            histogram = histograms[i] if histograms else None
            name = feature_names[i] if feature_names else None
            shape_functions.append(self._extract_shape_function_of_infinite_property(torch_model, ind, i, specific_V_ranges, categories=categories, histogram=histogram, name=name))
        bias = self._extract_bias_of_infinite_property(torch_model, ind)
        return GAM(shape_functions,bias)
    
    def _extract_shape_function_of_derivative(self, torch_model: PropertyModule, boundary, order, feature_index, specific_V_ranges, categories=None,histogram=None, name=None): 

        def shape_function(x):
            b_tensor,X0_tensor = self._get_b_X0_tensors(x,feature_index,specific_V_ranges)
            torch_model.eval()
            with torch.no_grad():
                pred = torch_model.derivative_module._predict_shape_function(boundary,order,feature_index,b_tensor,X0_tensor).detach().cpu()
            return pred.numpy()
        
        return ShapeFunction(shape_function,specific_V_ranges[feature_index], categories=categories, histogram=histogram, name=name)

    def _extract_bias_of_derivative(self, torch_model: PropertyModule, boundary, order):
        
        torch_model.eval()
        with torch.no_grad():
            pred = torch_model.derivative_module._predict_bias(boundary,order).detach().cpu()
        return pred.numpy()

    def _extract_gam_of_derivative(self, torch_model: PropertyModule, boundary, order,specific_V_ranges, histograms=None, all_categories={}, feature_names=None):

        n_features = len(specific_V_ranges)

        shape_functions = []

        for i in range(n_features):
            categories = all_categories.get(i)
            histogram = histograms[i] if histograms else None
            name = feature_names[i] if feature_names else None
            shape_functions.append(self._extract_shape_function_of_derivative(torch_model, boundary, order, i,specific_V_ranges, categories=categories, histogram=histogram, name=name))
        bias = self._extract_bias_of_derivative(torch_model, boundary, order)
        return GAM(shape_functions,bias)
    
    def _construct_derivative_predictor(self,composition: Composition,torch_model, specific_V_ranges,transition_point_predictors, histograms=None, all_categories={}, feature_names=None):

        derivative_predictor = {}
        
        first_derivative_at_start_status = composition.get_first_derivative_at_start_status()
        first_derivative_at_end_status = composition.get_first_derivative_at_end_status()
        second_derivative_at_end_status = composition.get_second_derivative_at_end_status()

        # boundary = 'start' and order = 1
        if first_derivative_at_start_status == 'weights':
            gam = self._extract_gam_of_derivative(torch_model, 'start', 1, specific_V_ranges, histograms, all_categories, feature_names)
            derivative_predictor[('start',1)] = GAMBasedDerivativePredictor(composition, gam, 'start', 1, transition_point_predictors)   
        elif first_derivative_at_start_status == 'none':
            derivative_predictor[('start',1)] = NaNPropertyFunction()

        # boundary = 'end' and order = 1
        if first_derivative_at_end_status == 'weights':
            gam = self._extract_gam_of_derivative(torch_model, 'end', 1, specific_V_ranges, histograms, all_categories, feature_names)
            derivative_predictor[('end',1)] = GAMBasedDerivativePredictor(composition, gam, 'end', 1, transition_point_predictors)
        elif first_derivative_at_end_status == 'zero':
            derivative_predictor[('end',1)] = ZeroPropertyFunction()
        elif first_derivative_at_end_status == 'cubic':
            derivative_predictor[('end',1)] = CubicDerivativePredictor(
                composition, 
                transition_point_predictors,
                first_derivative_at_start_predictor=derivative_predictor[('start',1)],
                order=1
            )
        
        # boundary = 'end' and order = 2
        if second_derivative_at_end_status == 'weights':
            gam = self._extract_gam_of_derivative(torch_model, 'end', 2, specific_V_ranges, histograms, all_categories, feature_names)
            derivative_predictor[('end',2)] = GAMBasedDerivativePredictor(composition, gam, 'end', 2, transition_point_predictors)
        elif second_derivative_at_end_status == 'zero':
            derivative_predictor[('end',2)] = ZeroPropertyFunction()
        elif second_derivative_at_end_status == 'cubic':
            derivative_predictor[('end',2)] = CubicDerivativePredictor(
                composition, 
                transition_point_predictors,
                first_derivative_at_start_predictor=derivative_predictor[('start',1)],
                order=2
            )
        
        return derivative_predictor

    def construct_single_property_map(self,composition: Composition,torch_model: PropertyModule,specific_V_ranges, histograms=None):

        all_categories = self.categorical_features_categories
        feature_names = self.feature_names

        n_motifs = len(composition)
        
        if not composition.is_bounded():
            n_transition_points = n_motifs
        else:
            n_transition_points = n_motifs + 1

        transition_point_predictor = {}
        for i in range(n_transition_points):
            for coordinate in ['x','t']:
                gam = self._extract_gam_of_transition_point(torch_model, i, coordinate,specific_V_ranges,histograms=histograms, all_categories=all_categories, feature_names=feature_names)
                transition_point_predictor[(i,coordinate)] = TransitionPointPredictor(gam)
        
        derivative_predictor = self._construct_derivative_predictor(composition,torch_model,specific_V_ranges,transition_point_predictor, histograms=histograms, all_categories=all_categories, feature_names=feature_names)

        if not composition.is_bounded():
            gams = []
            infinite_motif_predictor = []
            n_properties = composition.get_number_of_properties_for_unbounded_motif()
            for i in range(n_properties):
                gam = self._extract_gam_of_infinite_property(torch_model, i, specific_V_ranges,histograms=histograms, all_categories=all_categories, feature_names=feature_names)
                gams.append(gam)
            for i in range(n_properties):
                predictor = GAMBasedInfiniteMotifPredictor(composition, gams, i,
                    transition_point_predictor[(n_transition_points - 1,'x')], derivative_predictor[('end',1)])
                infinite_motif_predictor.append(predictor)
        else:
            infinite_motif_predictor = None
        
        return SinglePropertyMap(composition,transition_point_predictor,derivative_predictor,infinite_motif_predictor)
