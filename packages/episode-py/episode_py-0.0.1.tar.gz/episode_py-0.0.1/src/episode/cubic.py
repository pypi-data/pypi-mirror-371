import numpy as np
import torch
from array_api_compat import array_namespace
from episode.types import NpArrayOrTensor

def evaluate_cubic(coefficients: NpArrayOrTensor, x: NpArrayOrTensor, derivative_order: int = 0) -> NpArrayOrTensor:
    """
    Evaluate a cubic polynomial at x (or its derivatives).
    
    Parameters:
    ----------
    coefficients : np.ndarray
        Coefficients of the cubic polynomial. Should be of shape (batch_size,4)
        The coefficients are ordered as [a,b,c,d] where the polynomial is a*x^3 + b*x^2 + c*x + d
    x : np.ndarray
        Input data. Should be (batch_size,n_time_points)
    derivative_order : int
        Order of derivative to evaluate.

    Returns:
    -------
    np.ndarray      
        Value of the cubic polynomial at x. Should be (batch_size,n_time_points)
    """
    assert coefficients.shape[1] == 4
    if derivative_order == 0:
        return coefficients[:,[0]] * x**3 + coefficients[:,[1]] * x**2 + coefficients[:,[2]] * x + coefficients[:,[3]]
    elif derivative_order == 1:
        return 3 * coefficients[:,[0]] * x**2 + 2 * coefficients[:,[1]] * x + coefficients[:,[2]]
    elif derivative_order == 2:
        return 6 * coefficients[:,[0]] * x + 2 * coefficients[:,[1]]
    elif derivative_order == 3:
        return 6 * coefficients[:,[0]]
    else:
        raise ValueError("Derivative order must be 0, 1, 2 or 3")


def first_derivative_at_end_from_cubic(coefficients: NpArrayOrTensor, t_end: NpArrayOrTensor) -> NpArrayOrTensor:
        """_summary_

        Parameters
        ----------
        coefficients : np.ndarray | torch.Tensor
            Coefficients of the cubics of shape (batch_size, n_bounded_motifs, 4)
        t_end : np.ndarray | torch.Tensor
            Time points of the final bounded transition points of shape (batch_size,)

        Returns
        -------
        np.ndarray | torch.Tensor
            First derivatives at the end of the cubics of shape (batch_size,)
        """
        # Calculate the first derivative at the end of the cubic
        first_derivative = 3 * coefficients[:, -1, 0] * t_end**2 + 2 * coefficients[:, -1, 1] * t_end + coefficients[:, -1, 2]
        return first_derivative

def second_derivative_at_end_from_cubic(coefficients: NpArrayOrTensor, t_end: NpArrayOrTensor) -> NpArrayOrTensor:
    """
    Calculate the second derivative at the end of the cubic.

    Parameters
    ----------
    coefficients : np.ndarray | torch.Tensor
        Coefficients of the cubics of shape (batch_size, n_bounded_motifs, 4)
    t_end : np.ndarray | torch.Tensor
        Time points of the final bounded transition points of shape (batch_size,)

    Returns
    -------
    np.ndarray | torch.Tensor
        Second derivatives at the end of the cubics of shape (batch_size,)
    """
    # Calculate the second derivative at the end of the cubic
    second_derivative = 6 * coefficients[:, -1, 0] * t_end + 2 * coefficients[:, -1, 1]
    return second_derivative

def create_row(coordinate: NpArrayOrTensor, order: int) -> NpArrayOrTensor:
    """Create a row of polynomial features for a given coordinate.

     Parameters
     ----------
     coordinate : np.ndarray | torch.Tensor
         Coordinate for which to create the polynomial features. Should be of shape (batch_size, 2).
     order : int
         Order of the polynomial features. 0 for the function, 1 for the first derivative, and 2 for the second derivative.

     Returns
     -------
     np.ndarray | torch.Tensor
         Row of polynomial features for the given coordinate and order. Shape: (batch_size, 4)

     Raises
     ------
     ValueError
         If the order is not 0, 1, or 2.
    """
    xp = array_namespace(coordinate)
    batch_size = coordinate.shape[0]
    if order == 0:
        return xp.stack([coordinate[:,0]**3, coordinate[:,0]**2, coordinate[:,0], xp.ones(batch_size)], axis=1)
    elif order == 1:
        return xp.stack([3*coordinate[:,0]**2, 2*coordinate[:,0], xp.ones(batch_size), xp.zeros(batch_size)], axis=1)
    elif order == 2:
        return xp.stack([6*coordinate[:,0], 2*xp.ones(batch_size), xp.zeros(batch_size), xp.zeros(batch_size)], axis=1)
    else:
        raise ValueError("Order must be 0, 1, or 2.")
