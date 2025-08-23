from typing import Union, Sequence
import numpy as np
import torch

NpArrayOrTensor = Union[np.ndarray, torch.Tensor]

ArrayOrList = Union[NpArrayOrTensor, Sequence[NpArrayOrTensor]]

NpArrayOrList = Union[np.ndarray, Sequence[np.ndarray]]

