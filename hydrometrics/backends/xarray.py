"""
Xarray backend for HydroMetrics.

DataArray inputs are converted to numpy arrays and handed to the shared
:meth:`hydrometrics.core.base.MetricFunction.compute`. The reduction dimension is given by
``dim`` (or by ``axis``, which is translated to dimension names); the result keeps the
remaining dimensions and their coordinates as a ``DataArray``. Coordinates are not used to
align the inputs unless ``align`` asks for it (:mod:`hydrometrics.core.align`); ``sim`` and the
weights are transposed to the dimension order of ``obs``. ``Dataset`` is not supported.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
import xarray as xr

from hydrometrics.core.align import AlignType, align_inputs
from hydrometrics.core.base import MetricFunction
from hydrometrics.core.policies import NanPolicyType, ReductionType
from hydrometrics.metrics import catalog

AxisError = getattr(np, "exceptions", np).AxisError

DATASET_MESSAGE = (
    "xarray.Dataset is not supported; pass a DataArray, for example ds['discharge']. "
    "Stacking the variables would silently add a leading axis."
)


def _to_numpy_xarray(obj: xr.DataArray | xr.Dataset | np.ndarray) -> np.ndarray:
    """Convert xarray object to numpy array."""
    if isinstance(obj, xr.DataArray):
        return obj.to_numpy()
    elif isinstance(obj, xr.Dataset):
        return obj.to_array().to_numpy()
    return np.asarray(obj)


def _prepare_xarray_inputs(
    obs: xr.DataArray | xr.Dataset | np.ndarray,
    sim: xr.DataArray | xr.Dataset | np.ndarray,
    weight: xr.DataArray | xr.Dataset | np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Prepare xarray inputs for numpy backend."""
    obs_arr = _to_numpy_xarray(obs)
    sim_arr = _to_numpy_xarray(sim)
    weight_arr = _to_numpy_xarray(weight) if weight is not None else None
    return obs_arr, sim_arr, weight_arr


def _align(array: Any, obs_dims: tuple[str, ...]) -> Any:
    """Transpose a DataArray so that its leading dimensions follow the order of ``obs``."""
    if not isinstance(array, xr.DataArray):
        return array
    n = len(obs_dims)
    lead = tuple(array.dims[:n])
    if lead != obs_dims and set(lead) == set(obs_dims):
        return array.transpose(*obs_dims, *array.dims[n:])
    return array


def _merge_axes(array: np.ndarray, axes: list[int], n_obs_dims: int) -> tuple[np.ndarray, list[int]]:
    """Move ``axes`` of the first ``n_obs_dims`` axes behind the others and flatten them into one.

    Trailing axes beyond ``n_obs_dims`` (the ensemble members) stay last. Returns the array
    and the permutation applied to the observation axes.
    """
    others = [i for i in range(n_obs_dims) if i not in axes]
    order = others + list(axes)
    tail = list(range(n_obs_dims, array.ndim))
    moved = np.transpose(array, order + tail)
    lead = moved.shape[: len(others)]
    merged = int(np.prod([array.shape[a] for a in axes]))
    return moved.reshape(lead + (merged,) + moved.shape[n_obs_dims:]), order


def _make_xarray_wrapper(metric: MetricFunction) -> Callable:
    """Create the xarray function of a metric."""

    def wrapper(
        obs: xr.DataArray | np.ndarray,
        sim: xr.DataArray | np.ndarray,
        *,
        dim: str | list[str] | None = None,
        axis: int | None = None,
        nan_policy: NanPolicyType = "omit",
        sample_weight: xr.DataArray | np.ndarray | None = None,
        weight: xr.DataArray | np.ndarray | None = None,
        reduction: ReductionType | None = None,
        align: AlignType = "strict",
        **kwargs: Any,
    ):
        if any(isinstance(item, xr.Dataset) for item in (obs, sim, sample_weight, weight)):
            raise NotImplementedError(DATASET_MESSAGE)
        if dim is not None and axis is not None:
            raise TypeError("pass either dim or axis, not both")
        obs, sim, (sample_weight, weight), dropped = align_inputs(obs, sim, align, (sample_weight, weight))

        template = obs if isinstance(obs, xr.DataArray) else sim if isinstance(sim, xr.DataArray) else None
        obs_dims = None
        if template is not None:
            obs_dims = tuple(template.dims[: np.ndim(obs)])
            sim = _align(sim, obs_dims)
            sample_weight = _align(sample_weight, obs_dims)
            weight = _align(weight, obs_dims)

        obs_arr, sim_arr, _ = _prepare_xarray_inputs(obs, sim)
        weights = [None if w is None else _to_numpy_xarray(w) for w in (sample_weight, weight)]

        axes = reduced = None
        if dim is not None:
            if obs_dims is None:
                raise ValueError("dim needs an xarray.DataArray input")
            reduced = [dim] if isinstance(dim, str) else list(dim)
            missing = [d for d in reduced if d not in obs_dims]
            if missing:
                raise ValueError(f"dimension(s) {missing} not found in {obs_dims}")
            axes = [obs_dims.index(d) for d in reduced]
        elif axis is not None:
            requested = [axis] if isinstance(axis, (int, np.integer)) else list(axis)
            axes = []
            for a in requested:
                if not -obs_arr.ndim <= a < obs_arr.ndim:
                    raise AxisError(a, obs_arr.ndim)
                axes.append(a % obs_arr.ndim)
            reduced = [obs_dims[a] for a in axes] if obs_dims is not None else None

        merged_axis, order, obs_in = axis, None, obs_arr
        if axes:
            obs_in, order = _merge_axes(obs_arr, axes, obs_arr.ndim)
            sim_arr, _ = _merge_axes(sim_arr, axes, obs_arr.ndim)
            weights = [None if w is None else _merge_axes(w, axes, obs_arr.ndim)[0] for w in weights]
            merged_axis = obs_in.ndim - 1
        elif axes is not None:
            merged_axis = None

        def pack(value: Any) -> Any:
            if not axes or reduced is None:
                return value
            arr = np.asarray(value)
            if arr.ndim == 0:
                return xr.DataArray(arr[()], dims=())
            remaining = [d for d in obs_dims if d not in reduced]
            if arr.shape == tuple(template.sizes[d] for d in remaining):
                coords = {d: template.coords[d] for d in remaining if d in template.coords}
                return xr.DataArray(arr, dims=remaining, coords=coords)
            if arr.shape == obs_in.shape:
                # element-wise result: restore the original dimension order
                sizes = [obs_arr.shape[i] for i in order]
                restored = np.transpose(arr.reshape(sizes), np.argsort(order))
                coords = {d: template.coords[d] for d in obs_dims if d in template.coords}
                return xr.DataArray(restored, dims=obs_dims, coords=coords)
            return arr

        return metric.compute(
            obs_in,
            sim_arr,
            sample_weight=weights[0],
            weight=weights[1],
            axis=merged_axis,
            nan_policy=nan_policy,
            reduction=reduction,
            kwargs=kwargs,
            extra_parameters={"dim": reduced, "axis": None if dim is not None else axis},
            pack=pack,
            align_dropped=dropped,
        )

    wrapper.__name__ = getattr(metric.func, "__name__", metric.name)
    wrapper.__doc__ = metric.func.__doc__
    return wrapper


# ============================================================================
# Regression metrics
# ============================================================================


mae = _make_xarray_wrapper(catalog["mae"])
mse = _make_xarray_wrapper(catalog["mse"])
rmse = _make_xarray_wrapper(catalog["rmse"])
nrmse = _make_xarray_wrapper(catalog["nrmse"])
bias = _make_xarray_wrapper(catalog["bias"])
pbias = _make_xarray_wrapper(catalog["pbias"])
r2 = _make_xarray_wrapper(catalog["r2"])
pearson_r = _make_xarray_wrapper(catalog["pearson_r"])
spearman_r = _make_xarray_wrapper(catalog["spearman_r"])
kendall_tau = _make_xarray_wrapper(catalog["kendall_tau"])
willmott_d = _make_xarray_wrapper(catalog["willmott_d"])


# ============================================================================
# Hydrological metrics
# ============================================================================


nse_variance_weighted = _make_xarray_wrapper(catalog["nse_variance_weighted"])
ssigma_delta = _make_xarray_wrapper(catalog["ssigma_delta"])
ssigma = _make_xarray_wrapper(catalog["ssigma"])
forecast_verification = _make_xarray_wrapper(catalog["forecast_verification"])
forecast_verification_delta = _make_xarray_wrapper(catalog["forecast_verification_delta"])
regNSE = _make_xarray_wrapper(catalog["regNSE"])
nse = _make_xarray_wrapper(catalog["nse"])
log_nse = _make_xarray_wrapper(catalog["log_nse"])
modified_nse = _make_xarray_wrapper(catalog["modified_nse"])
nse_bounded = _make_xarray_wrapper(catalog["nse_bounded"])
kge_2009 = _make_xarray_wrapper(catalog["kge_2009"])
kge_2012 = _make_xarray_wrapper(catalog["kge_2012"])
r_component = _make_xarray_wrapper(catalog["r_component"])
alpha_component = _make_xarray_wrapper(catalog["alpha_component"])
beta_component = _make_xarray_wrapper(catalog["beta_component"])
gamma_component = _make_xarray_wrapper(catalog["gamma_component"])
kge_components = _make_xarray_wrapper(catalog["kge_components"])
rsr = _make_xarray_wrapper(catalog["rsr"])
ve = _make_xarray_wrapper(catalog["ve"])


# ============================================================================
# Probabilistic metrics
# ============================================================================


crps = _make_xarray_wrapper(catalog["crps"])
weighted_crps = _make_xarray_wrapper(catalog["weighted_crps"])
crpss = _make_xarray_wrapper(catalog["crpss"])
brier_score = _make_xarray_wrapper(catalog["brier_score"])
reliability = _make_xarray_wrapper(catalog["reliability"])
sharpness = _make_xarray_wrapper(catalog["sharpness"])


# ============================================================================
# Classification metrics
# ============================================================================


accuracy = _make_xarray_wrapper(catalog["accuracy"])
precision = _make_xarray_wrapper(catalog["precision"])
recall = _make_xarray_wrapper(catalog["recall"])
f1_score = _make_xarray_wrapper(catalog["f1_score"])
roc_auc = _make_xarray_wrapper(catalog["roc_auc"])
pr_auc = _make_xarray_wrapper(catalog["pr_auc"])
edi = _make_xarray_wrapper(catalog["edi"])
sedi = _make_xarray_wrapper(catalog["sedi"])
