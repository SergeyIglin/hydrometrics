"""
Input validation and preprocessing for HydroMetrics.

Provides unified handling of different data formats (numpy, pandas, xarray, polars)
and consistent NaN policy enforcement.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal
import numpy as np

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None  # type: ignore

try:
    import xarray as xr
    HAS_XARRAY = True
except ImportError:
    HAS_XARRAY = False
    xr = None  # type: ignore

try:
    import polars as pl
    HAS_POLARS = True
except ImportError:
    HAS_POLARS = False
    pl = None  # type: ignore

from hydrometrics.core.policies import NanPolicy, NanPolicyType


ArrayLike = np.ndarray
if HAS_PANDAS:
    ArrayLike = ArrayLike | pd.Series | pd.DataFrame
if HAS_XARRAY:
    ArrayLike = ArrayLike | xr.DataArray | xr.Dataset
if HAS_POLARS:
    ArrayLike = ArrayLike | pl.Series | pl.DataFrame


NAN_POLICIES = ("propagate", "omit", "raise")


def check_choice(value: Any, choices: tuple, name: str) -> Any:
    """Return ``value`` (an ``Enum`` member is reduced to its value) if it is one of ``choices``."""
    if isinstance(value, Enum):
        value = value.value
    if value not in choices:
        raise ValueError(f"{name} must be one of {choices}, got {value!r}")
    return value


def validate_inputs(
    obs: ArrayLike,
    sim: ArrayLike,
    *,
    axis: int | None = None,
    nan_policy: NanPolicyType = "omit",
    sample_weight: ArrayLike | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, dict[str, Any]]:
    """
    Validate and convert inputs to numpy arrays with consistent NaN handling.

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values. An ensemble has one extra trailing axis,
        ``obs.shape + (n_members,)``.
    axis : int or None, optional
        Axis along which a metric will be computed. It only matters for the
        ``"propagate"`` policy, where it defines which slices become NaN.
    nan_policy : {"propagate", "omit", "raise"}, default="omit"
        How to handle NaN values. ``"omit"`` makes the removal pairwise: wherever
        ``obs``, ``sim`` or the weight is NaN, NaN is set in all three, so the arrays keep
        their shape and metrics that count only valid values drop exactly those pairs,
        also along an axis. ``"propagate"`` applies the same mask and leaves it to the
        caller to turn the affected slices into NaN. ``"raise"`` raises ``ValueError``
        for any NaN.
    sample_weight : array-like or None, optional
        Sample weights for weighted metrics, same shape as ``obs``, non-negative.

    Returns
    -------
    obs_arr : np.ndarray
        Validated observed values as numpy array.
    sim_arr : np.ndarray
        Validated simulated values as numpy array.
    weight_arr : np.ndarray or None
        Validated weights as numpy array.
    nan_info : dict
        ``{"policy", "n_nan_removed", "n_total"}``: the policy, the number of pairs
        removed (``"omit"`` only) and the number of pairs.

    Raises
    ------
    ValueError
        If inputs have incompatible shapes, weights are negative or of a wrong shape,
        the policy is unknown, or NaN is present under ``nan_policy="raise"``.
    """
    obs_arr, sim_arr, weight_arr, nan_info, _ = _prepare_inputs(
        obs, sim, axis=axis, nan_policy=nan_policy, sample_weight=sample_weight,
    )
    return obs_arr, sim_arr, weight_arr, nan_info


def _prepare_inputs(
    obs: ArrayLike,
    sim: ArrayLike,
    *,
    axis: int | None,
    nan_policy: NanPolicyType,
    sample_weight: ArrayLike | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, dict[str, Any], dict[str, Any] | None]:
    """Implementation of :func:`validate_inputs`.

    The fifth value is ``None`` unless the policy is ``"propagate"``; then it is
    ``{"slices": ..., "elements": ...}``: a boolean mask of the slices along ``axis``
    (or a single bool for ``axis=None``) that contained a NaN, and the element-wise mask
    of pairs with a NaN.
    """
    nan_policy = check_choice(nan_policy, NAN_POLICIES, "nan_policy")

    obs_arr = _to_numpy(obs)
    sim_arr = _to_numpy(sim)

    # Ensemble forecasts: sim has one extra trailing dimension
    # (obs: (n,), sim: (n, n_ensemble) or obs: (n, m), sim: (n, m, n_ensemble)).
    ensemble = sim_arr.ndim == obs_arr.ndim + 1 and sim_arr.shape[:-1] == obs_arr.shape
    if obs_arr.shape != sim_arr.shape and not ensemble:
        raise ValueError(
            f"Shape mismatch: obs {obs_arr.shape} != sim {sim_arr.shape}"
        )

    weight_arr = None
    if sample_weight is not None:
        weight_arr = _to_numpy(sample_weight)
        if weight_arr.shape != obs_arr.shape:
            raise ValueError(
                f"Weight shape {weight_arr.shape} != data shape {obs_arr.shape}"
            )
        if np.any(weight_arr < 0):
            raise ValueError("Sample weights must be non-negative")

    obs_nan = np.isnan(obs_arr)
    sim_missing = np.isnan(sim_arr)
    if ensemble:
        sim_any, sim_all = sim_missing.any(axis=-1), sim_missing.all(axis=-1)
    else:
        sim_any = sim_all = sim_missing
    weight_nan = np.isnan(weight_arr) if weight_arr is not None else np.zeros(obs_nan.shape, dtype=bool)

    any_nan = obs_nan | sim_any | weight_nan
    # A pair is lost when obs or the weight is NaN or every ensemble member is NaN;
    # single NaN members are dropped inside the ensemble metrics.
    invalid = obs_nan | sim_all | weight_nan

    n_nan = int(np.count_nonzero(any_nan))
    if nan_policy == NanPolicy.RAISE and n_nan:
        raise ValueError(f"Input contains {n_nan} NaN values (nan_policy='raise')")

    propagate = None
    if nan_policy == NanPolicy.PROPAGATE:
        slices = any_nan.any(axis=axis) if axis is not None else bool(any_nan.any())
        propagate = {"slices": slices, "elements": any_nan}

    if invalid.any():
        obs_arr = obs_arr.astype(float, copy=True)
        sim_arr = sim_arr.astype(float, copy=True)
        obs_arr[invalid] = np.nan
        sim_arr[invalid] = np.nan
        if weight_arr is not None:
            weight_arr = weight_arr.astype(float, copy=True)
            weight_arr[invalid] = np.nan

    nan_info = {
        "policy": nan_policy,
        "n_nan_removed": int(np.count_nonzero(invalid)) if nan_policy == NanPolicy.OMIT else 0,
        "n_total": obs_arr.size,
    }
    return obs_arr, sim_arr, weight_arr, nan_info, propagate


def _to_numpy(arr: ArrayLike) -> np.ndarray:
    """Convert various array types to numpy array."""
    if isinstance(arr, np.ndarray):
        return arr
    elif HAS_PANDAS and isinstance(arr, (pd.Series, pd.DataFrame)):
        return arr.to_numpy()
    elif HAS_XARRAY and isinstance(arr, xr.DataArray):
        return arr.to_numpy()
    elif HAS_XARRAY and isinstance(arr, xr.Dataset):
        # Convert dataset to array (requires all variables to have same dims)
        return arr.to_array().to_numpy()
    elif HAS_POLARS and isinstance(arr, pl.Series):
        return arr.to_numpy()
    elif HAS_POLARS and isinstance(arr, pl.DataFrame):
        return arr.to_numpy()
    else:
        # Try array protocol or direct conversion
        return np.asarray(arr)


def apply_nan_policy_axis(
    obs: np.ndarray,
    sim: np.ndarray,
    weight: np.ndarray | None,
    axis: int | None,
    nan_policy: NanPolicyType,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, dict[str, Any]]:
    """
    Apply NaN policy along a specific axis.

    For axis-specific computation, we need to handle NaN per slice.
    This is a helper for metrics that operate along an axis.
    """
    nan_info = {"policy": nan_policy, "n_nan_removed": 0, "n_total": obs.size}

    if axis is None:
        # Already handled in validate_inputs
        return obs, sim, weight, nan_info

    # Find NaN along axis
    nan_mask = np.isnan(obs) | np.isnan(sim)
    if weight is not None:
        nan_mask = nan_mask | np.isnan(weight)

    n_nan = np.count_nonzero(nan_mask)
    nan_info["n_nan_removed"] = int(n_nan)

    if n_nan == 0:
        return obs, sim, weight, nan_info

    if nan_policy == NanPolicy.RAISE:
        raise ValueError(f"Input contains {n_nan} NaN values (nan_policy='raise')")
    elif nan_policy == NanPolicy.OMIT:
        # For axis-wise, we can't easily remove individual elements
        # The metric functions will handle this per-slice
        pass
    # PROPAGATE: leave NaNs

    return obs, sim, weight, nan_info


def check_finite_arrays(*arrays: np.ndarray, names: list[str] | None = None) -> None:
    """Check that arrays contain only finite values (no NaN, no inf)."""
    if names is None:
        names = [f"array_{i}" for i in range(len(arrays))]

    for arr, name in zip(arrays, names):
        if not np.all(np.isfinite(arr)):
            n_nan = np.count_nonzero(np.isnan(arr))
            n_inf = np.count_nonzero(np.isinf(arr))
            raise ValueError(
                f"{name} contains non-finite values: {n_nan} NaN, {n_inf} Inf"
            )


def check_same_shape(*arrays: np.ndarray, names: list[str] | None = None) -> None:
    """Check that all arrays have the same shape."""
    if names is None:
        names = [f"array_{i}" for i in range(len(arrays))]

    shapes = [arr.shape for arr in arrays]
    if len(set(shapes)) > 1:
        raise ValueError(f"Shape mismatch: {dict(zip(names, shapes))}")


def check_non_empty(arr: np.ndarray, name: str = "array") -> None:
    """Check that array is not empty."""
    if arr.size == 0:
        raise ValueError(f"{name} is empty")


def check_min_samples(arr: np.ndarray, min_samples: int, name: str = "array") -> None:
    """Check that array has at least min_samples valid (non-NaN) values."""
    n_valid = np.count_nonzero(~np.isnan(arr))
    if n_valid < min_samples:
        raise ValueError(
            f"{name} has {n_valid} valid samples, minimum required: {min_samples}"
        )
