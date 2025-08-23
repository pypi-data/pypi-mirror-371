__all__ = [
    "normal",
    "normal_set",
    "normal_minmax",
]

import torch
from lt_utils.common import *


def normal(
    x: torch.Tensor,
    mean: Optional[float] = None,
    std: Optional[float] = None,
    eps: float = 1e-9,
) -> torch.Tensor:
    """Normalizes tensor by mean and std."""

    if mean is None:
        mean = x.mean() * 0.5
    if std is None:
        std = x.std() * 0.5
    return (x - mean) / (std + eps)


def normal_minmax(
    x: torch.Tensor, min_val: float = -1.0, max_val: float = 1.0
) -> torch.Tensor:
    """Scales tensor to [min_val, max_val] range."""
    x_min, x_max = x.min(), x.max()
    return (x - x_min) / (x_max - x_min + 1e-8) * (max_val - min_val) + min_val


def normal_set(
    S: torch.Tensor,
    value: float = float("inf"),
    axis: int = 0,
    threshold: float = 1e-10,
    fill: bool = False,
) -> torch.Tensor:
    mag = S.abs().float()

    if value is None:
        return S

    elif value == float("inf"):
        length = mag.max(dim=axis, keepdim=True).values

    elif value == float("-inf"):
        length = mag.min(dim=axis, keepdim=True).values

    elif value == 0:
        length = (mag > 0).sum(dim=axis, keepdim=True).float()

    elif value > 0:
        length = (mag**value).sum(dim=axis, keepdim=True) ** (1.0 / value)

    else:
        raise ValueError(f"Unsupported value: {value}")

    small_idx = length < threshold
    length = length.clone()
    if fill:
        length[small_idx] = float("nan")
        Snorm = S / length
        Snorm[Snorm != Snorm] = 1.0  # replace nan with fill_norm (default 1.0)
    else:
        length[small_idx] = float("inf")
        Snorm = S / length

    return Snorm
