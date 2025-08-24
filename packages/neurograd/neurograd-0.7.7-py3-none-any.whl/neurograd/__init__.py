# Device detection and numpy/cupy setup must happen first to avoid circular imports
from .utils.device import auto_detect_device
DEVICE = auto_detect_device()
if DEVICE == "cpu":
    import numpy as xp
elif DEVICE == "cuda":
    import cupy as xp

# Now import everything else after xp is available
from .functions import (arithmetic, math, linalg, activations, reductions, conv)
from .functions.arithmetic import add, sub, mul, div, pow
from .functions.math import log, exp, sin, cos, tan, sqrt, cbrt, log10, log2, abs, clip
from .functions.linalg import matmul, dot, tensordot, transpose
from .functions.tensor_ops import reshape, flatten, squeeze, expand_dims, cast, pad, sliding_window_view, newaxis
from .functions.reductions import Sum, Mean, Max, Min, Std, sum, mean, max, min, std
from .functions.conv import conv2d, pool2d, maxpool2d, averagepool2d, pooling2d, maxpooling2d, averagepooling2d
from .tensor import Tensor, ones, zeros, ones_like, zeros_like, empty, arange, eye

# Automatic Mixed Precision (AMP) support
try:
    from .amp import autocast, GradScaler
except ImportError:
    # Define dummy functions if AMP module not available
    def autocast(*args, **kwargs):
        import contextlib
        return contextlib.nullcontext()
    
    class GradScaler:
        def __init__(self, *args, **kwargs):
            pass
        def scale(self, x):
            return x
        def step(self, optimizer):
            optimizer.step()
        def update(self):
            pass
# Optional graph visualization (requires matplotlib)
try:
    from .utils.graph import visualize_graph, save_graph, print_graph_structure
except ImportError:
    # Define dummy functions if matplotlib is not available
    def visualize_graph(*args, **kwargs):
        print("Graph visualization requires matplotlib")
    def save_graph(*args, **kwargs):
        print("Graph saving requires matplotlib")
    def print_graph_structure(*args, **kwargs):
        print("Graph structure printing requires matplotlib")



# Importing numpy data types for convenience. This allows users to use float32, int64, etc. directly
for name in ['float16', 'float32', 'float64', 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'bool_']:
    globals()[name] = getattr(xp, name)


def save(obj, f, protocol=None):
    """
    Save an object to disk.

    Recommended usage mirrors PyTorch-style checkpoints:
        ng.save({
            'model_state': model.state_dict(),
            'optimizer_state': optimizer.state_dict(),
            # optional: 'scaler_state': scaler.state_dict(), 'epoch': epoch, ...
        }, 'checkpoint.pth')

    This function is a thin wrapper over pickle/cloudpickle and will
    serialize any Python object, but saving raw Module/Optimizer objects
    is discouraged in favor of state_dict-based checkpoints.
    """
    import warnings
    try:
        import cloudpickle as _p
    except Exception:
        import pickle as _p
    import pickle as _std
    protocol = _std.HIGHEST_PROTOCOL if protocol is None else protocol

    # Nudge users toward dict-based checkpoints if they pass a single object
    if not isinstance(obj, dict) and hasattr(obj, "state_dict"):
        warnings.warn(
            "Saving raw objects is discouraged; prefer dict-based checkpoints "
            "e.g., {'model_state': model.state_dict(), ...}",
            RuntimeWarning,
        )

    if isinstance(f, (str, bytes)):
        with open(f, "wb") as fh:
            _p.dump(obj, fh, protocol=protocol)
    else:
        _p.dump(obj, f, protocol=protocol)


def load(f):
    """
    Load an object from disk.

    For checkpoints saved via ng.save with a dict payload, usage is:
        ckpt = ng.load('checkpoint.pth')
        model.load_state_dict(ckpt['model_state'])
        optimizer.load_state_dict(ckpt['optimizer_state'])

    Returns whatever object was serialized (typically a dict).
    """
    try:
        import cloudpickle as _p
    except Exception:
        import pickle as _p
    if isinstance(f, (str, bytes)):
        with open(f, "rb") as fh:
            return _p.load(fh)
    return _p.load(f)


def save_checkpoint(model=None, optimizer=None, scaler=None, path: str = None, **extra):
    """
    Convenience helper to save a PyTorch-style checkpoint.

    Args:
        model: Module with state_dict(); if provided, stored under 'model_state'.
        optimizer: Optimizer with state_dict(); if provided, stored under 'optimizer_state'.
        scaler: Optional GradScaler with state_dict(); stored under 'scaler_state'.
        path: Destination file path (e.g., 'checkpoint.pth').
        **extra: Any additional metadata to include (e.g., epoch=..., metrics=...).
    """
    if path is None:
        raise ValueError("'path' must be provided for save_checkpoint")

    payload = {}
    if model is not None:
        if not hasattr(model, "state_dict"):
            raise TypeError("model must implement state_dict()")
        payload["model_state"] = model.state_dict()
    if optimizer is not None:
        if not hasattr(optimizer, "state_dict"):
            raise TypeError("optimizer must implement state_dict()")
        payload["optimizer_state"] = optimizer.state_dict()
    if scaler is not None:
        if not hasattr(scaler, "state_dict"):
            raise TypeError("scaler must implement state_dict()")
        payload["scaler_state"] = scaler.state_dict()

    # Attach any extra metadata
    payload.update(extra)

    save(payload, path)


def load_checkpoint(path: str):
    """
    Load a checkpoint previously saved with save_checkpoint or ng.save.

    Returns:
        A dict-like object containing keys such as 'model_state',
        'optimizer_state', and any additional metadata that was saved.
    """
    if path is None:
        raise ValueError("'path' must be provided for load_checkpoint")
    obj = load(path)
    if not isinstance(obj, dict):
        raise TypeError("Checkpoint file does not contain a dict payload")
    return obj
