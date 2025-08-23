

import numpy as np
from typing import Any, List, Sequence, Tuple, Union
import numpy.typing as npt
from numba import jit, njit
import torch
from array_api_compat import array_namespace, is_numpy_namespace
from episode.types import NpArrayOrList, NpArrayOrTensor, ArrayOrList
from episode.semantic_representation import Composition



def pad_and_mask(
    arrays: Sequence[NpArrayOrTensor]
) -> Tuple[NpArrayOrTensor, NpArrayOrTensor]:
    """
    Pads a list of 1D numpy arrays or 1D PyTorch tensors to a 2D array/tensor.

    Parameters
    ----------
    arrays : Sequence[np.ndarray] or Sequence[torch.Tensor]
        A sequence of 1D numpy arrays or 1D PyTorch tensors to be padded.

    Returns
    -------
    NpArrayOrTensor
        Padded 2D array or tensor.
    NpArrayOrTensor
        Mask indicating real entries (1) and padded entries (0).

    Raises
    ------
    ValueError
        If the input list is empty.
    """
    if not arrays:
        raise ValueError("Input list is empty.")
    lengths = [len(a) for a in arrays]
    max_len = max(lengths)
    n = len(arrays)

    first = arrays[0]
    is_torch = False
    
    is_torch = isinstance(first, torch.Tensor)

    if is_torch:
        dtype = first.dtype if (hasattr(first, 'dtype') and isinstance(first, torch.Tensor)) else torch.float32
        padded = torch.zeros((n, max_len), dtype=dtype)
        mask = torch.zeros((n, max_len), dtype=torch.bool)
        for i, a in enumerate(arrays):
            l = len(a)
            padded[i, :l] = torch.as_tensor(a, dtype=dtype)
            mask[i, :l] = 1
    else:
        dtype = first.dtype if isinstance(first, np.ndarray) else np.float32
        padded = np.zeros((n, max_len), dtype=dtype)
        mask = np.zeros((n, max_len), dtype=bool)
        for i, a in enumerate(arrays):
            l = len(a)
            padded[i, :l] = np.asarray(a, dtype=dtype)
            mask[i, :l] = 1
    return padded, mask

    
def is_bounded_motif(motif):
    if motif[2] == 'b':
        return True
    else:
        return False
    
# def sigmoid_numpy(x, threshold=20.0):
#     maskg20 = x > threshold
#     masklm20 = x < -threshold
#     res = np.zeros_like(x)
#     res[maskg20] = 1.0
#     res[masklm20] = 0.0
#     res[~maskg20 & ~masklm20] = 1 / (1 + np.exp(-x[~maskg20 & ~masklm20]))
#     return res

# @njit
def sigmoid_numpy(x):
    return 1 / (1 + np.exp(-x))
    

def softmax_numpy(x, temperature=1.0):
    """
    Compute the softmax of vector x with a temperature parameter.
    
    Parameters:
    x (numpy.ndarray): Input data.
    temperature (float): Temperature parameter for scaling.
    
    Returns:
    numpy.ndarray: Softmax probabilities.
    """
    if temperature <= 0:
        raise ValueError("Temperature must be greater than zero.")
    
    x = np.array(x) / temperature
    x_max = np.max(x, axis=-1, keepdims=True)
    e_x = np.exp(x - x_max)
    sum_e_x = np.sum(e_x, axis=-1, keepdims=True)
    return e_x / sum_e_x

def softplus_numpy(x):
    # Use piecewise to handle different ranges of x
    mask = x > 20
    res = np.zeros_like(x)
    res[mask] = x[mask]
    res[~mask] = np.log1p(np.exp(x[~mask]))
    return res

# @njit
def linalg_solve_multiple_numpy(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Solve the linear equation Ax = b for multiple right-hand sides.

    Parameters
    ----------
    A : np.ndarray
        Coefficient matrix of shape (m, n, n).
    b : np.ndarray
        Right-hand side matrix of shape (m, n).

    Returns
    -------
    np.ndarray
        Solution matrix of shape (m, n).
    """
    sol = np.zeros_like(b)
    for i in range(A.shape[0]):
        sol[i] = np.linalg.solve(A[i], b[i])
    return sol


def get_torch_device(device):
    if device == 'cuda' or device == 'gpu':
        return torch.device('cuda:0')
    elif device == 'cpu':
        return torch.device('cpu')
    else:
        raise ValueError('Unknown device')

def get_lightning_accelerator(device):
    if device == 'cuda' or device == 'gpu':
        return 'gpu'
    elif device == 'cpu':
        return 'cpu'
    else:
        raise ValueError('Unknown device')
    
def from_feature_index_to_cont_feature_index(feature_index, categorical_features_indices):
        """
        Convert a feature index to a continuous feature index

        Args:
        feature_index: integer, index of the feature

        Returns:
        output integer
        """
        if feature_index in categorical_features_indices:
            return None
        cont_feature_index = 0
        for i in range(feature_index):
            if i not in categorical_features_indices:
                cont_feature_index += 1
        
        return cont_feature_index


def get_first_derivative_range(composition : Composition, motif_index, point1, point2, which_point):
    """
    Calculate the first derivative range for a given composition and motif index.

    Parameters
    ----------
    composition : Composition
        The composition of the model.
    motif_index : int
        The index of the motif in the composition.
    point1 : NpArrayOrTensor
        Should be of shape (batch_size, 2) representing the first point.
    point2 : NpArrayOrTensor
        Should be of shape (batch_size, 2) representing the second point.
    which_point : str
        Either 'left' or 'right', indicating which side of the motif we are interested in.
    
    Returns
    -------
    Tuple[NpArrayOrTensor, NpArrayOrTensor]
        Each shape should be (batch_size,).
    """
    slope = (point2[:,1] - point1[:,1])/(point2[:,0] - point1[:,0])
    coefficients = composition.get_first_derivative_range_coefficients(motif_index, which_point)
    return coefficients[0] * slope, coefficients[1] * slope

def transform_first_derivative(boundary: str, composition : Composition, raw_first_derivative : NpArrayOrTensor, transition_points : NpArrayOrTensor) -> NpArrayOrTensor:
    """
    Transform the first derivative at the start to the proper range.
    Only used if first derivative at start is predicted from weights.

    Parameters
    ----------
    boundary : str
        Either 'start' or 'end', indicating the boundary of the composition.
    composition : Composition
        The composition of the model.
    raw_first_derivative : NpArrayOrTensor
        The raw first derivative.
        Shape should be (batch_size,)
    transition_points : NpArrayOrTensor
        The transition points of the model.
        Shape should be (batch_size, n_transition_points, 2).

    Returns
    -------
    NpArrayOrTensor
        The transformed first derivative at the start.
        Shape should be (batch_size,).
    """
    if boundary == 'start':
        status = composition.get_first_derivative_at_start_status()
        motif_index = 0
        side = 'left'
    else:
        status = composition.get_first_derivative_at_end_status()
        motif_index = len(composition) - 1
        side = 'right'
    if status == 'weights':
        coordinate_1 = transition_points[:,motif_index,:]
        coordinate_2 = transition_points[:,motif_index+1,:]
        return _transform_first_derivative(composition, raw_first_derivative, coordinate_1, coordinate_2, motif_index, side)
    else:
        raise ValueError("First derivative is not predicted from weights, cannot transform it.")
    
def _transform_first_derivative(composition: Composition, raw_first_derivative: NpArrayOrTensor, coordinate_1: NpArrayOrTensor, coordinate_2: NpArrayOrTensor, motif_index: int, side: str) -> NpArrayOrTensor:
    xp = array_namespace(raw_first_derivative, coordinate_1, coordinate_2)
    if is_numpy_namespace(xp):
        ratio = sigmoid_numpy(raw_first_derivative)
    else:
        assert isinstance(raw_first_derivative, torch.Tensor), "raw_first_derivative should be a torch tensor if not numpy"
        ratio = torch.sigmoid(raw_first_derivative)
    slope_min, slope_max = get_first_derivative_range(composition, motif_index, coordinate_1, coordinate_2, side)
    return slope_min + ratio * (slope_max - slope_min)

def transform_properties(composition: Composition, raw_properties: NpArrayOrTensor, last_value: NpArrayOrTensor, first_derivative_at_end: NpArrayOrTensor) -> NpArrayOrTensor:
    """Transform the raw properties to the proper range.

    Parameters
    ----------
    composition : Composition
        The composition of the model.
    raw_properties : NpArrayOrTensor
        The raw properties to transform.
        Shape should be (batch_size, n_properties).
    last_value : NpArrayOrTensor
        The last value of the trajectory.
        Shape should be (batch_size,).
    first_derivative_at_end : NpArrayOrTensor
        The first derivative at the end of the transition.
        Shape should be (batch_size,).

    Returns
    -------
    NpArrayOrTensor
        The transformed properties.
    """
    last_motif = composition.motifs[-1]
    if last_motif == '++f':
        return 1 / raw_properties
    elif last_motif == '+-p':
        return raw_properties
    elif last_motif == '+-h':
        y0 = last_value
        y1 = first_derivative_at_end
        c = raw_properties[:, 0] 
        offset = np.log(3)*(c-y0)/(2*y1)
        raw_properties[:,1] = offset + raw_properties[:,1]
        return raw_properties
    elif last_motif == '-+f':
        return raw_properties
    elif last_motif == '-+h':
            y0 = last_value
            y1 = first_derivative_at_end
            c =  raw_properties[:, 0]
            offset = np.log(3)*(y0-c)/(-2*y1)
            raw_properties[:,1] = offset + raw_properties[:,1]
            return raw_properties
    elif last_motif == '--f':
        return 1 / raw_properties
    raise ValueError(f"Unknown last motif: {last_motif}. Cannot transform properties.")


def _assign_to_mask(mask,target,input):
    if np.any(mask):
        if np.ndim(input) == 0 or type(input) == tuple or type(input) == str:
            input = [input]*mask.sum()
        ids = np.arange(len(target))[mask]
        counter = 0
        for i in ids:
            target[i] = input[counter]
            counter += 1

def filter_by_mask(array: ArrayOrList, mask: np.ndarray | list[bool]) -> ArrayOrList:
    """
    Filter the array by the mask

    Parameters:
    -----------
    array: np.ndarray or list
        The array to be filtered.
    mask: np.ndarray or list
        The mask to filter the array by. It should be a boolean array or list of the same length as the array.
    """
    if isinstance(array, np.ndarray):
        return array[mask]
    elif isinstance(array, list):
        return [item for i, item in enumerate(array) if mask[i]]
    elif isinstance(array, torch.Tensor):
        mask_tensor = torch.as_tensor(mask, dtype=torch.bool, device=array.device)
        return array[mask_tensor]
    else:
        raise ValueError(f"Unsupported type for filtering: {type(array)}")


def get_train_val_indices(n_samples:int, train_size: float = 0.8, seed: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Get the indices for the training and validation sets

    Parameters
    ----------
    n_samples : int
        The total number of samples.
    train_size : float, optional
        The proportion of the dataset to include in the train split (default is 0.8).
    seed : int, optional
        Random seed for reproducibility (default is 0).

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Two arrays containing the indices for the training and validation sets.
    """
    np_gen = np.random.default_rng(seed)
    train_indices = np_gen.choice(n_samples, int(train_size*n_samples), replace=False)
    val_indices = np.setdiff1d(np.arange(n_samples), train_indices)
    return train_indices, val_indices

def get_tensors(device, *args: np.ndarray) -> Tuple[torch.Tensor, ...]:
    """
    Convert numpy arrays to torch tensors

    Args:
    args: numpy arrays

    Returns:
    tuple of torch tensors
    """
    torch_device = get_torch_device(device)
    return tuple([torch.tensor(arg, dtype=torch.float32, device=torch_device) for arg in args])