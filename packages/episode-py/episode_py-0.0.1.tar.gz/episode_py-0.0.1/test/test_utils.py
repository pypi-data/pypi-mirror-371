import pytest
import numpy as np

from episode.utils import pad_and_mask

try:
    import torch
    _HAS_TORCH = True
except ImportError:
    _HAS_TORCH = False


def test_pad_and_mask_with_numpy_arrays():
    arrays = [np.array([1, 2, 3]), np.array([4, 5]), np.array([6])]
    padded, mask = pad_and_mask(arrays)

    expected_padded = np.array([
        [1, 2, 3],
        [4, 5, 0],
        [6, 0, 0]
    ])
    expected_mask = np.array([
        [1, 1, 1],
        [1, 1, 0],
        [1, 0, 0]
    ])

    assert np.array_equal(padded, expected_padded)
    assert np.array_equal(mask, expected_mask)

@pytest.mark.skipif(not _HAS_TORCH, reason="PyTorch is not installed.")
def test_pad_and_mask_with_torch_tensors():
    if not _HAS_TORCH:
        pytest.skip("PyTorch is not installed.")
    import torch
    arrays = [torch.tensor([1, 2, 3]), torch.tensor([4, 5]), torch.tensor([6])]
    padded, mask = pad_and_mask(arrays)

    expected_padded = torch.tensor([
        [1, 2, 3],
        [4, 5, 0],
        [6, 0, 0]
    ], dtype=torch.int64)
    expected_mask = torch.tensor([
        [1, 1, 1],
        [1, 1, 0],
        [1, 0, 0]
    ], dtype=torch.bool)

    assert isinstance(padded, torch.Tensor)
    assert isinstance(mask, torch.Tensor)
    assert torch.equal(padded, expected_padded)
    assert torch.equal(mask, expected_mask)

def test_pad_and_mask_empty_list():
    with pytest.raises(ValueError, match="Input list is empty."):
        pad_and_mask([])