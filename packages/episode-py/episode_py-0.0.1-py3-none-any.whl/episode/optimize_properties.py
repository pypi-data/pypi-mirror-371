from abc import ABC, abstractmethod
from typing import Callable, Tuple, Union
import numpy as np
from episode.semantic_representation import Composition, Properties
from scipy.optimize import minimize
from episode.utils import sigmoid_numpy, softmax_numpy, softplus_numpy
from episode.trajectory_predictor import C0TrajectoryPredictor
from episode import constants


class OptimizationAlgorithm(ABC):

    @abstractmethod
    def minimize(self, loss_function: Callable, initial_guess: np.ndarray) -> np.ndarray:
        pass

class ScipyOptimizationAlgorithm(OptimizationAlgorithm):
    """Optimization algorithm using SciPy's minimize function.
    This class allows for different optimization methods to be specified.
    """
    def __init__(self, method: str = 'L-BFGS-B'):
        """
        Parameters
        ----------
        method : str, optional
            The optimization method to use. Defaults to 'L-BFGS-B'.
        """
        self.method = method

    def minimize(self, loss_function: Callable, initial_guess: np.ndarray) -> np.ndarray:

        result = minimize(loss_function, initial_guess, method=self.method)
        return result.x
    

def create_dictionary(composition: Composition, x0_included: bool) -> Tuple[dict, int]:
    n_parameters = {}
    
    n_parameters['horizontal_values'] = len(composition.bounded_part)
    n_parameters['vertical_values'] = len(composition.bounded_part)
    n_parameters['infinite_properties'] = composition.get_number_of_properties_for_unbounded_motif()


    n_parameters['t_last_finite_transition_point'] = 0
    if not composition.is_bounded():
        if len(composition) != 1:
            n_parameters['t_last_finite_transition_point'] = 1

    if composition.get_first_derivative_at_start_status() == "weights":
        n_parameters['first_derivative_at_start'] = 1
    else:
        n_parameters['first_derivative_at_start'] = 0

    if composition.get_first_derivative_at_end_status() == "weights":
        n_parameters['first_derivative_at_end'] = 1
    else:
        n_parameters['first_derivative_at_end'] = 0
    
    if composition.get_second_derivative_at_end_status() == "weights":
        n_parameters['second_derivative_at_end'] = 1
    else:
        n_parameters['second_derivative_at_end'] = 0
    
    if not x0_included:
        n_parameters['x0'] = 1
    else:
        n_parameters['x0'] = 0

    dictionary = {}
    current_index = 0
    for key, value in n_parameters.items():
        if value != 0:
            dictionary[key] = (current_index, current_index+value)
        else:
            dictionary[key] = None
        current_index += value

    n_all_parameters = current_index

    return dictionary, n_all_parameters

def from_parameters_to_raw_properties(parameters: np.ndarray, dictionary: dict) -> dict:
    """
    Converts a flat array of parameters into a dictionary of arguments based on the provided mapping.

    Parameters
    ----------
    parameters : np.ndarray
        A flat array of parameters.
    dictionary : dict
        A mapping from argument names to their corresponding indices in the parameters array.
        key is argument name such as "horizontal_values", "vertical_values", etc.
        value is a tuple indicating the start and end indices in the parameters array, or None if not applicable.
    
    Returns
    -------
    dict
        A dictionary mapping argument names to their corresponding values.
    """

    arguments = {}

    for key, value in dictionary.items():
        if key in ['horizontal_values', 'vertical_values']:
            if value is not None:
                arguments[key] = parameters[value[0]:value[1]]
            else:
                arguments[key] = np.zeros(1)
        elif key == 'infinite_properties':
            if value is not None:
                arguments[key] = parameters[value[0]:value[1]]
            else:
                arguments[key] = None
        else:
            if value is not None:
                arguments[key] = parameters[value[0]]
            else:
                arguments[key] = None
    
    return arguments

def compute_t_last_finite_transition_point(
        composition: Composition,
        t_range: Tuple[float, float],
        arguments: dict,
        t_max: float) -> float:
    """
    Returns the last finite transition point in time based on the composition and arguments.
    If the composition is bounded, it returns the end of the time range.

    Parameters
    ----------
    composition : Composition
        The composition object containing motif information.
    t_range : Tuple[float, float]
        The time range for the evaluation.
    arguments : dict
        A dictionary containing the arguments, including 't_last_finite_transition_point'.
    t_max : float
        The maximum time point in the data.
    
    Returns
    -------
    float
        The last finite transition point in time.
    """
    if composition.is_bounded():
        return t_range[1]
    else:
        if len(composition) > 1:
            # When fitting an individual sample, it makes sense to limit the position of the last finite transition point
            # to the range of the time points
            empirical_t_max = t_max
            empirical_range = empirical_t_max - t_range[0]
            return t_range[0] + constants.MIN_TRANSITION_POINT_SEP*len(composition) + sigmoid_numpy(arguments['t_last_finite_transition_point']) * (1-constants.MIN_RELATIVE_DISTANCE_TO_LAST_FINITE_TRANSITION_POINT) * empirical_range
        else:
            return t_range[0]
        
def _process_horizontal_values(
        horizontal_values: np.ndarray,
        t_last_finite_transition_point: float,
        t_range: Tuple[float, float]) -> np.ndarray:
    
        # pass horizontal values through a softmax function, and scale them by the range of the time points
        scale = t_last_finite_transition_point - t_range[0]
        trans_horizontal_values = softmax_numpy(horizontal_values) * scale
        good_indices = np.arange(len(trans_horizontal_values))
        bad_indices = []
        while np.min(trans_horizontal_values) < constants.MIN_TRANSITION_POINT_SEP:
            scale -= constants.MIN_TRANSITION_POINT_SEP
            i = np.argmin(trans_horizontal_values)
            good_indices = good_indices[good_indices != i]
            bad_indices.append(i)
            new_horizontal_values = softmax_numpy(horizontal_values[good_indices]) * scale
            trans_horizontal_values = np.zeros_like(horizontal_values)
            trans_horizontal_values[good_indices] = new_horizontal_values
            trans_horizontal_values[bad_indices] = constants.MIN_TRANSITION_POINT_SEP
        return trans_horizontal_values

def transition_points_from_raw_properties(
        composition: Composition, 
        horizontal_values: np.ndarray, 
        vertical_values: np.ndarray, 
        t_last_finite_transition_point: float, 
        x0: float,
        t_range: Tuple[float, float]
        ) -> np.ndarray:
    """
    Converts raw properties into transition points.

    Parameters
    ----------
    horizontal_values : np.ndarray
        The horizontal shifts betweet transition points. 1D array
    vertical_values : np.ndarray
        The vertical shifts between transition points. 1D array
    t_last_finite_transition_point : float
        The last finite transition point in time.
    x0 : float
        The initial state variable.

    Returns
    -------
    np.ndarray
        The calculated transition points of shape (num_transition_points, 2).
    """
    all_coordinate_values = np.zeros((len(composition.bounded_part)+1,2))

    if len(composition.bounded_part) > 0:

        horizontal_values = _process_horizontal_values(
            horizontal_values,
            t_last_finite_transition_point,
            t_range
        )

    # make sure vertical values are positive
    vertical_values = softplus_numpy(vertical_values) + constants.MIN_VERTICAL_SEPARATION
    
    # j = 0
    all_coordinate_values[0,0] = t_range[0]
    all_coordinate_values[0,1] = x0

    for j in range(1, len(composition.bounded_part)+1):
        sign = 1 if composition.bounded_part[j-1][0] == '+' else -1
        all_coordinate_values[j,0] = horizontal_values[j-1] + all_coordinate_values[j-1,0]
        all_coordinate_values[j,1] = sign*vertical_values[j-1] + all_coordinate_values[j-1,1]

    # Force the last point to be the end of the time range
    all_coordinate_values[-1,0] = t_last_finite_transition_point
    return all_coordinate_values

def get_first_derivative_range(composition: Composition, motif_index: int, point1: np.ndarray, point2: np.ndarray, which_point: str) -> Tuple[float, float]:
    """
    Get the range of the first derivative for a given motif and transition points.

    Parameters
    ----------
    composition : Composition
        The composition object containing motif information.
    motif_index : int
        Index of the motif in the composition.
    point1 : np.ndarray
        numpy array of shape (2,) representing the first point (time, value).
    point2 : np.ndarray
        numpy array of shape (2,) representing the second point (time, value).
    which_point : str
        'left' or 'right' indicating which point to consider for the derivative.

    Returns
    -------
    Tuple[float, float]
        The range of the first derivative at the specified point.
    """
    slope = (point2[1] - point1[1])/(point2[0] - point1[0])

    coefficients = composition.get_first_derivative_range_coefficients(motif_index, which_point)

    return coefficients[0] * slope, coefficients[1] * slope

def first_derivative_start_from_raw_properties(
    composition: Composition,
    raw_properties: dict,
    transition_points: np.ndarray,
    ) -> np.ndarray:
    motif_index = 0
    point1 = transition_points[motif_index]
    point2 = transition_points[motif_index + 1]
    slope_min, slope_max = get_first_derivative_range(
        composition,
        motif_index,
        point1,
        point2,
        'left'
    )
    return slope_min + sigmoid_numpy(raw_properties['first_derivative_at_start']) * (slope_max - slope_min)

def first_derivative_end_from_raw_properties(
    composition: Composition,
    raw_properties: dict,
    transition_points: np.ndarray,
    ) -> np.ndarray:
    if not composition.is_bounded():
        sign = 1 if composition.motifs[-1][0] == '+' else -1
        return sign * (constants.MIN_ABS_DERIVATIVE + softplus_numpy(raw_properties['first_derivative_at_end']))
    else:
        motif_index = len(composition.bounded_part) - 1
        point1 = transition_points[motif_index]
        point2 = transition_points[motif_index + 1]
        slope_min, slope_max = get_first_derivative_range(
            composition,
            motif_index,
            point1,
            point2,
            'right'
        )
        return slope_min + sigmoid_numpy(raw_properties['first_derivative_at_end']) * (slope_max - slope_min)

def second_derivative_end_from_raw_properties(
    composition: Composition,
    raw_properties: dict,
    transition_points: np.ndarray,
    ) -> np.ndarray:
    sign = 1 if composition.motifs[-1][1] == '+' else -1
    return sign * (constants.MIN_ABS_DERIVATIVE + softplus_numpy(raw_properties['second_derivative_at_end']))

def from_raw_properties_to_properties(
        composition: Composition,
        raw_properties: dict,
        x0: Union[float, None],
        t_range: Tuple[float, float],
        t_max: float) -> Properties:
    
    if x0 is None:
        new_x0 = raw_properties['x0']
    else:
        new_x0 = x0

    t_last_finite_transition_point = compute_t_last_finite_transition_point(
        composition,
        t_range,
        raw_properties,
        t_max
    )

    transition_points = transition_points_from_raw_properties(
        composition,
        raw_properties['horizontal_values'],
        raw_properties['vertical_values'],
        t_last_finite_transition_point,
        new_x0,
        t_range
    )

    if composition.get_first_derivative_at_start_status() == "weights":
        first_derivative_start = first_derivative_start_from_raw_properties(
            composition,
            raw_properties,
            transition_points
        ).reshape((1, 1))
    elif composition.get_first_derivative_at_start_status() == "zero":
        first_derivative_start = np.zeros((1, 1))
    else: # none
        first_derivative_start = np.full((1, 1), np.nan)
    
    if composition.get_first_derivative_at_end_status() == "weights":
        first_derivative_end = first_derivative_end_from_raw_properties(
            composition,
            raw_properties,
            transition_points
        ).reshape((1, 1))
    elif composition.get_first_derivative_at_end_status() == "zero":
        first_derivative_end = np.zeros((1, 1))
    else: # cubic
        first_derivative_end = np.full((1, 1), np.nan)

    if composition.get_second_derivative_at_end_status() == "weights":
        second_derivative_end = second_derivative_end_from_raw_properties(
            composition,
            raw_properties,
            transition_points
        ).reshape((1, 1))
    elif composition.get_second_derivative_at_end_status() == "zero":
        second_derivative_end = np.zeros((1, 1))
    else: # cubic
        second_derivative_end = np.full((1, 1), np.nan)
    
    if composition.is_bounded():
        unbounded_motif_properties = None
    else:
        unbounded_motif_properties = (softplus_numpy(raw_properties['infinite_properties']) + constants.MIN_PROPERTY_VALUE).reshape((1, -1))
    
    transition_points = np.expand_dims(transition_points, axis=0)

    return Properties(
        engine='numpy',
        composition=composition,
        transition_points=transition_points,
        first_derivative_start=first_derivative_start,
        first_derivative_end=first_derivative_end,
        second_derivative_end=second_derivative_end,
        unbounded_motif_properties=unbounded_motif_properties,
        unbounded_motif_properties_raw=True
        )

def calculate_score(
        composition: Composition,
        t_range: Tuple[float, float],
        t: np.ndarray,
        x: np.ndarray,
        x0: Union[float, None],
        optimization_alg: OptimizationAlgorithm,
        loss_fn: Callable,
        train_on_all: bool = False,
        evaluate_on_all: bool = True,
        train_size: float = 0.8,
        seed: int = 0
        ) -> Tuple[float, Properties]:
    """Calculate the score for the given composition and data.

    Parameters
    ----------
    composition : Composition
        The composition object containing motif information.
    t_range : Tuple[float, float]
        The time range for the evaluation.
    t : np.ndarray
        The time points for the evaluation. Shape (n_time_points,).
    x : np.ndarray
        The state variables for the evaluation. Shape (n_time_points).
    x0 : Union[float, None]
        The initial state variable, if applicable.
    optimization_alg : OptimizationAlgorithm
        The optimization algorithm to use.
    loss_fn : Callable
        The loss function to minimize. Signature should be `loss_fn(x_pred, x_true) -> float` or `loss_fn(x_pred, x_true) -> np.ndarray`.
    train_on_all : bool, optional
        Whether to train on all available data, by default False.
    evaluate_on_all : bool, optional
        Whether to evaluate on all available data, by default True.
    train_size : float, optional
        The proportion of data to use for training, by default 0.8.
    seed : int, optional
        The random seed for reproducibility, by default 0.

    Returns
    -------
    Tuple[float, Properties]
        The loss value and the properties object containing the optimized parameters.
    """

    np.random.seed(seed)

    if train_on_all:
        t_train = t
        x_train = x
    else:
        n_train = int(len(t) * train_size)
        indices = list(np.arange(n_train))
        t_train = t[indices]
        x_train = x[indices]
    
    dictionary, n_all_parameters = create_dictionary(composition, x0 is not None)
    initial_guess = np.zeros(n_all_parameters)

    trajecteory_predictor = C0TrajectoryPredictor()

    def objective(parameters: np.ndarray) -> float:
        raw_properties = from_parameters_to_raw_properties(parameters, dictionary)
        properties = from_raw_properties_to_properties(
            composition,
            raw_properties,
            x0,
            t_range,
            t_max=np.max(t)
            )
        x_pred = trajecteory_predictor._predict_from_properties(properties, t_train.reshape(1,-1))
        assert isinstance(x_pred, np.ndarray), "x_pred should be a numpy array"
        x_pred = x_pred.flatten()
        return loss_fn(x_pred, x_train)

    result = optimization_alg.minimize(objective, initial_guess)
    raw_properties = from_parameters_to_raw_properties(result, dictionary)
    properties = from_raw_properties_to_properties(
        composition,
        raw_properties,
        x0,
        t_range,
        t_max=np.max(t)
    )

    if evaluate_on_all:
        t_eval = t
        x_eval = x
    else:
        n_train = int(len(t) * train_size)
        indices = list(np.arange(n_train, len(t)))
        t_eval = t[indices]
        x_eval = x[indices]
    
    x_pred = trajecteory_predictor._predict_from_properties(properties, t_eval.reshape(1,-1))
    assert isinstance(x_pred, np.ndarray), "x_pred should be a numpy array"
    x_pred = x_pred.flatten()
    loss = loss_fn(x_pred, x_eval)
    if np.isscalar(loss):
        assert isinstance(loss, float), "Loss should be a float"
        return float(loss), properties
    else:
        return loss[0], properties


        

