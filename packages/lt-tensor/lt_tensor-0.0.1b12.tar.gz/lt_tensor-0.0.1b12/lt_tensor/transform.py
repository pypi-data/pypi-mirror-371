import math
import torch
from torch import Tensor
from lt_utils.common import *
import torch.nn.functional as F
from lt_tensor.normalizations import normal

DeviceType: TypeAlias = Union[torch.device, str]


def stft(
    waveform: Tensor,
    n_fft: int = 512,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    window_fn: str = "hann",
    center: bool = True,
    return_complex: bool = True,
) -> Tensor:
    """Performs short-time Fourier transform using PyTorch."""
    window = (
        torch.hann_window(win_length or n_fft).to(waveform.device)
        if window_fn == "hann"
        else None
    )
    return torch.stft(
        input=waveform,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
        window=window,
        center=center,
        return_complex=return_complex,
    )


def istft(
    stft_matrix: Tensor,
    n_fft: int = 512,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    window_fn: str = "hann",
    center: bool = True,
    length: Optional[int] = None,
) -> Tensor:
    """Performs inverse short-time Fourier transform using PyTorch."""
    window = (
        torch.hann_window(win_length or n_fft).to(stft_matrix.device)
        if window_fn == "hann"
        else None
    )
    return torch.istft(
        input=stft_matrix,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
        window=window,
        center=center,
        length=length,
    )


def fft(x: Tensor, norm: Optional[str] = "backward") -> Tensor:
    """Returns the FFT of a real tensor."""
    return torch.fft.fft(x, norm=norm)


def ifft(x: Tensor, norm: Optional[str] = "backward") -> Tensor:
    """Returns the inverse FFT of a complex tensor."""
    return torch.fft.ifft(x, norm=norm)


def sp_to_linear(
    base: torch.Tensor, lin_fb: torch.Tensor, eps: float = 1e-8
) -> torch.Tensor:
    """Approximate inversion of 'base' to 'lin_fb' using pseudo-inverse."""
    mel_fb_inv = torch.pinverse(lin_fb)
    return torch.matmul(mel_fb_inv, base + eps)


def stretch_tensor(x: torch.Tensor, rate: float, mode: str = "linear") -> torch.Tensor:
    """Time-stretch tensor using interpolation."""
    B = 1 if x.ndim < 2 else x.shape[0]
    C = 1 if x.ndim < 3 else x.shape[-2]
    T = x.shape[-1]
    new_t = int(T * rate)
    stretched = F.interpolate(x.view(B * C, T), size=new_t, mode=mode)
    return stretched.view(B, C, new_t)


def pad_tensor(
    x: torch.Tensor, target_len: int, pad_value: float = 0.0
) -> torch.Tensor:
    """Pads tensor to target length along last dimension."""
    current_len = x.shape[-1]
    if current_len >= target_len:
        return x[..., :target_len]
    padding = [0] * (2 * (x.ndim - 1)) + [0, target_len - current_len]
    return F.pad(x, padding, value=pad_value)


def get_sinusoidal_embedding(timesteps: torch.Tensor, dim: int) -> torch.Tensor:
    # Expect shape [B] or [B, 1]
    if timesteps.dim() > 1:
        timesteps = timesteps.view(-1)  # flatten to [B]

    device = timesteps.device
    half_dim = dim // 2
    emb = torch.exp(
        torch.arange(half_dim, device=device) * -(math.log(10000.0) / half_dim)
    )
    emb = timesteps[:, None].float() * emb[None, :]  # [B, half_dim]
    emb = torch.cat((emb.sin(), emb.cos()), dim=-1)  # [B, dim]
    return emb


def generate_window(
    M: int, alpha: float = 0.5, device: Optional[DeviceType] = None
) -> Tensor:
    if M < 1:
        raise ValueError("Window length M must be >= 1.")
    if M == 1:
        return torch.ones(1, device=device)

    n = torch.arange(M, dtype=torch.float32, device=device)
    return alpha - (1.0 - alpha) * torch.cos(2.0 * math.pi * n / (M - 1))


def pad_center(tensor: torch.Tensor, size: int, axis: int = -1) -> torch.Tensor:
    n = tensor.shape[axis]
    if size < n:
        raise ValueError(f"Target size ({size}) must be at least input size ({n})")

    lpad = (size - n) // 2
    rpad = size - n - lpad

    pad = [0] * (2 * tensor.ndim)
    pad[2 * axis + 1] = rpad
    pad[2 * axis] = lpad

    return F.pad(tensor, pad, mode="constant", value=0)


def window_sumsquare(
    window_spec: Union[str, int, float, Callable, List[Any], Tuple[Any, ...]],
    n_frames: int,
    hop_length: int = 256,
    win_length: int = 1024,
    n_fft: int = 2048,
    mean: Optional[float] = None,
    std: Optional[float] = None,
    dtype: torch.dtype = torch.float32,
    device: Optional[torch.device] = None,
):
    if win_length is None:
        win_length = n_fft

    total_length = n_fft + hop_length * (n_frames - 1)
    x = torch.zeros(total_length, dtype=dtype, device=device)

    # Get the window (from scipy for now)
    win = generate_window(window_spec, win_length, fftbins=True)
    win = torch.tensor(win, dtype=dtype, device=device)

    # Normalize and square
    win_sq = normal(win, mean, std) ** 2
    win_sq = pad_center(win_sq, size=n_fft, axis=0)

    # Accumulate squared windows
    for i in range(n_frames):
        sample = i * hop_length
        end = min(total_length, sample + n_fft)
        length = end - sample
        x[sample:end] += win_sq[:length]

    return x


def inverse_transform(
    spec: Tensor,
    phase: Tensor,
    n_fft: int = 1024,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    length: Optional[Any] = None,
    window: Optional[Tensor] = None,
):
    if window is None:
        window = torch.hann_window(win_length or n_fft).to(spec.device)
    return torch.istft(
        spec * torch.exp(phase * 1j),
        n_fft,
        hop_length,
        win_length,
        window=window,
        length=length,
    )


