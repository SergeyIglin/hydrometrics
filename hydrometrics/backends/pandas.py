"""
Pandas backend for HydroMetrics.

Series and DataFrame inputs are converted to numpy arrays and handed to the shared
:meth:`hydrometrics.core.base.MetricFunction.compute`, so the NaN policy, the weights, the
axis and the result are the same as on the NumPy path. Indexes are not used: pairs are
matched by position.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
import pandas as pd

from hydrometrics.core.base import MetricFunction, backend_function
from hydrometrics.metrics import catalog


# ============================================================================
# Internal helpers
# ============================================================================

def _to_numpy_pandas(obj: pd.Series | pd.DataFrame) -> np.ndarray:
    """Convert pandas object to numpy array; missing values (``pd.NA``) become NaN."""
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        try:
            return obj.to_numpy(dtype=float, na_value=np.nan)
        except (TypeError, ValueError):
            return obj.to_numpy()
    return np.asarray(obj)


def _prepare_pandas_inputs(
    obs: pd.Series | pd.DataFrame | np.ndarray,
    sim: pd.Series | pd.DataFrame | np.ndarray,
    weight: pd.Series | pd.DataFrame | np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Prepare pandas inputs for numpy backend."""
    obs_arr = _to_numpy_pandas(obs)
    sim_arr = _to_numpy_pandas(sim)
    weight_arr = _to_numpy_pandas(weight) if weight is not None else None
    return obs_arr, sim_arr, weight_arr


# ============================================================================
# Groupby-enabled metric functions
# ============================================================================

def _groupby_apply(
    df: pd.DataFrame,
    obs_col: str,
    sim_col: str,
    metric_func: callable,
    group_by: list[str] | str | None,
    weight_col: str | None = None,
    **kwargs: Any,
) -> pd.DataFrame | pd.Series:
    """Apply metric function grouped by columns."""
    if group_by is None:
        obs_arr = df[obs_col].to_numpy()
        sim_arr = df[sim_col].to_numpy()
        weight_arr = df[weight_col].to_numpy() if weight_col else None
        return metric_func(obs_arr, sim_arr, weight=weight_arr, **kwargs)

    if isinstance(group_by, str):
        group_by = [group_by]

    grouped = df.groupby(group_by, observed=True)

    def apply_group(group: pd.DataFrame) -> Any:
        obs_arr = group[obs_col].to_numpy()
        sim_arr = group[sim_col].to_numpy()
        weight_arr = group[weight_col].to_numpy() if weight_col else None
        return metric_func(obs_arr, sim_arr, weight=weight_arr, **kwargs)

    return grouped.apply(apply_group)


# ============================================================================
# Wide format support
# ============================================================================

def _detect_wide_format_columns(
    df: pd.DataFrame,
    obs_suffix: str = "_obs",
    sim_suffix: str = "_sim",
) -> list[tuple[str, str, str]]:
    """Detect basin/variable pairs in wide format.

    Returns list of (prefix, obs_col, sim_col).
    """
    cols = df.columns.tolist()
    pairs = []
    for col in cols:
        if col.endswith(obs_suffix):
            prefix = col[: -len(obs_suffix)]
            sim_col = prefix + sim_suffix
            if sim_col in cols:
                pairs.append((prefix, col, sim_col))
    return pairs


def _wide_to_long(
    df: pd.DataFrame,
    obs_suffix: str = "_obs",
    sim_suffix: str = "_sim",
    basin_col: str = "basin_id",
    time_col: str = "time",
) -> pd.DataFrame:
    """Convert wide format to long format."""
    pairs = _detect_wide_format_columns(df, obs_suffix, sim_suffix)
    if not pairs:
        raise ValueError("No matching _obs/_sim column pairs found")

    long_dfs = []
    for prefix, obs_col, sim_col in pairs:
        temp = df[[obs_col, sim_col]].copy()
        temp.columns = ["obs", "sim"]
        temp[basin_col] = prefix
        if time_col in df.columns:
            temp[time_col] = df[time_col]
        elif isinstance(df.index, pd.DatetimeIndex):
            temp[time_col] = df.index
        else:
            temp[time_col] = df.index
        long_dfs.append(temp)

    return pd.concat(long_dfs, ignore_index=True)


def _make_pandas_wrapper(metric: MetricFunction) -> Callable:
    """Create the pandas function of a metric."""
    return backend_function(metric, _to_numpy_pandas)


# ============================================================================
# Regression metrics
# ============================================================================


mae = _make_pandas_wrapper(catalog["mae"])
mse = _make_pandas_wrapper(catalog["mse"])
rmse = _make_pandas_wrapper(catalog["rmse"])
nrmse = _make_pandas_wrapper(catalog["nrmse"])
bias = _make_pandas_wrapper(catalog["bias"])
pbias = _make_pandas_wrapper(catalog["pbias"])
r2 = _make_pandas_wrapper(catalog["r2"])
pearson_r = _make_pandas_wrapper(catalog["pearson_r"])
spearman_r = _make_pandas_wrapper(catalog["spearman_r"])
kendall_tau = _make_pandas_wrapper(catalog["kendall_tau"])
willmott_d = _make_pandas_wrapper(catalog["willmott_d"])


# ============================================================================
# Hydrological metrics
# ============================================================================


nse_variance_weighted = _make_pandas_wrapper(catalog["nse_variance_weighted"])
ssigma_delta = _make_pandas_wrapper(catalog["ssigma_delta"])
ssigma = _make_pandas_wrapper(catalog["ssigma"])
forecast_verification = _make_pandas_wrapper(catalog["forecast_verification"])
forecast_verification_delta = _make_pandas_wrapper(catalog["forecast_verification_delta"])
regNSE = _make_pandas_wrapper(catalog["regNSE"])
nse = _make_pandas_wrapper(catalog["nse"])
log_nse = _make_pandas_wrapper(catalog["log_nse"])
modified_nse = _make_pandas_wrapper(catalog["modified_nse"])
nse_bounded = _make_pandas_wrapper(catalog["nse_bounded"])
kge_2009 = _make_pandas_wrapper(catalog["kge_2009"])
kge_2012 = _make_pandas_wrapper(catalog["kge_2012"])
r_component = _make_pandas_wrapper(catalog["r_component"])
alpha_component = _make_pandas_wrapper(catalog["alpha_component"])
beta_component = _make_pandas_wrapper(catalog["beta_component"])
gamma_component = _make_pandas_wrapper(catalog["gamma_component"])
kge_components = _make_pandas_wrapper(catalog["kge_components"])
rsr = _make_pandas_wrapper(catalog["rsr"])
ve = _make_pandas_wrapper(catalog["ve"])


# ============================================================================
# Probabilistic metrics
# ============================================================================


crps = _make_pandas_wrapper(catalog["crps"])
weighted_crps = _make_pandas_wrapper(catalog["weighted_crps"])
crpss = _make_pandas_wrapper(catalog["crpss"])
brier_score = _make_pandas_wrapper(catalog["brier_score"])
reliability = _make_pandas_wrapper(catalog["reliability"])
sharpness = _make_pandas_wrapper(catalog["sharpness"])


# ============================================================================
# Classification metrics
# ============================================================================


accuracy = _make_pandas_wrapper(catalog["accuracy"])
precision = _make_pandas_wrapper(catalog["precision"])
recall = _make_pandas_wrapper(catalog["recall"])
f1_score = _make_pandas_wrapper(catalog["f1_score"])
roc_auc = _make_pandas_wrapper(catalog["roc_auc"])
pr_auc = _make_pandas_wrapper(catalog["pr_auc"])
edi = _make_pandas_wrapper(catalog["edi"])
sedi = _make_pandas_wrapper(catalog["sedi"])
