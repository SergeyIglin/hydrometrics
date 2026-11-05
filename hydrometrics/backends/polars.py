"""
Polars backend for HydroMetrics.

Series and DataFrame inputs are converted to numpy arrays and handed to the shared
:meth:`hydrometrics.core.base.MetricFunction.compute`, so the NaN policy, the weights, the
axis and the result are the same as on the NumPy path. Null values become NaN. A
``LazyFrame`` is not supported.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import polars as pl

from hydrometrics.core.base import MetricFunction, backend_function
from hydrometrics.metrics import catalog


def _to_numpy_polars(obj: pl.Series | pl.DataFrame) -> np.ndarray:
    """Convert polars object to numpy array."""
    if isinstance(obj, pl.Series):
        return obj.to_numpy()
    elif isinstance(obj, pl.DataFrame):
        return obj.to_numpy()
    return np.asarray(obj)


def _prepare_polars_inputs(
    obs: pl.Series | pl.DataFrame | np.ndarray,
    sim: pl.Series | pl.DataFrame | np.ndarray,
    weight: pl.Series | pl.DataFrame | np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Prepare polars inputs for numpy backend."""
    obs_arr = _to_numpy_polars(obs)
    sim_arr = _to_numpy_polars(sim)
    weight_arr = _to_numpy_polars(weight) if weight is not None else None
    return obs_arr, sim_arr, weight_arr


def _make_polars_wrapper(metric: MetricFunction) -> Callable:
    """Create the polars function of a metric."""
    return backend_function(metric, _to_numpy_polars)


# ============================================================================
# Regression metrics
# ============================================================================


mae = _make_polars_wrapper(catalog["mae"])
mse = _make_polars_wrapper(catalog["mse"])
rmse = _make_polars_wrapper(catalog["rmse"])
nrmse = _make_polars_wrapper(catalog["nrmse"])
bias = _make_polars_wrapper(catalog["bias"])
pbias = _make_polars_wrapper(catalog["pbias"])
r2 = _make_polars_wrapper(catalog["r2"])
pearson_r = _make_polars_wrapper(catalog["pearson_r"])
spearman_r = _make_polars_wrapper(catalog["spearman_r"])
kendall_tau = _make_polars_wrapper(catalog["kendall_tau"])
willmott_d = _make_polars_wrapper(catalog["willmott_d"])


# ============================================================================
# Hydrological metrics
# ============================================================================


nse_variance_weighted = _make_polars_wrapper(catalog["nse_variance_weighted"])
ssigma_delta = _make_polars_wrapper(catalog["ssigma_delta"])
ssigma = _make_polars_wrapper(catalog["ssigma"])
forecast_verification = _make_polars_wrapper(catalog["forecast_verification"])
forecast_verification_delta = _make_polars_wrapper(catalog["forecast_verification_delta"])
regNSE = _make_polars_wrapper(catalog["regNSE"])
nse = _make_polars_wrapper(catalog["nse"])
log_nse = _make_polars_wrapper(catalog["log_nse"])
modified_nse = _make_polars_wrapper(catalog["modified_nse"])
nse_bounded = _make_polars_wrapper(catalog["nse_bounded"])
kge_2009 = _make_polars_wrapper(catalog["kge_2009"])
kge_2012 = _make_polars_wrapper(catalog["kge_2012"])
r_component = _make_polars_wrapper(catalog["r_component"])
alpha_component = _make_polars_wrapper(catalog["alpha_component"])
beta_component = _make_polars_wrapper(catalog["beta_component"])
gamma_component = _make_polars_wrapper(catalog["gamma_component"])
kge_components = _make_polars_wrapper(catalog["kge_components"])
rsr = _make_polars_wrapper(catalog["rsr"])
ve = _make_polars_wrapper(catalog["ve"])


# ============================================================================
# Probabilistic metrics
# ============================================================================


crps = _make_polars_wrapper(catalog["crps"])
weighted_crps = _make_polars_wrapper(catalog["weighted_crps"])
crpss = _make_polars_wrapper(catalog["crpss"])
brier_score = _make_polars_wrapper(catalog["brier_score"])
reliability = _make_polars_wrapper(catalog["reliability"])
sharpness = _make_polars_wrapper(catalog["sharpness"])


# ============================================================================
# Classification metrics
# ============================================================================


accuracy = _make_polars_wrapper(catalog["accuracy"])
precision = _make_polars_wrapper(catalog["precision"])
recall = _make_polars_wrapper(catalog["recall"])
f1_score = _make_polars_wrapper(catalog["f1_score"])
roc_auc = _make_polars_wrapper(catalog["roc_auc"])
pr_auc = _make_polars_wrapper(catalog["pr_auc"])
edi = _make_polars_wrapper(catalog["edi"])
sedi = _make_polars_wrapper(catalog["sedi"])
