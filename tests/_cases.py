"""Shared synthetic inputs for the property tests: one valid case for each of the 44 metrics."""

from __future__ import annotations

import sys

import numpy as np
import pytest

NAMES = [
    "mae", "mse", "rmse", "nrmse", "bias", "pbias", "r2", "pearson_r", "spearman_r",
    "kendall_tau", "willmott_d", "nse", "log_nse", "modified_nse", "nse_bounded", "kge_2009",
    "kge_2012", "kge_components", "r_component", "alpha_component", "beta_component",
    "gamma_component", "rsr", "ve", "ssigma", "ssigma_delta", "forecast_verification",
    "forecast_verification_delta", "regNSE", "nse_variance_weighted", "crps",
    "weighted_crps", "crpss", "brier_score", "reliability", "sharpness", "accuracy",
    "precision", "recall", "f1_score", "roc_auc", "pr_auc", "edi", "sedi",
]
BINARY_SCORE = {"brier_score", "reliability", "sharpness", "roc_auc", "pr_auc"}
BINARY_LABEL = {"accuracy", "precision", "recall", "f1_score", "edi", "sedi"}
NEEDS_EXTRA = {"regNSE", "ssigma_delta", "forecast_verification_delta", "nse_variance_weighted"}
NO_WEIGHT = {
    "spearman_r", "kendall_tau", "roc_auc", "pr_auc", "ssigma", "ssigma_delta",
    "forecast_verification", "forecast_verification_delta", "regNSE", "nse_variance_weighted",
}
NO_AXIS = {"ssigma_delta", "forecast_verification_delta", "regNSE", "nse_variance_weighted"}
ELEMENTWISE = {"forecast_verification", "ssigma_delta", "forecast_verification_delta"}
WEIGHT_NAMES = [n for n in NAMES if n not in NO_WEIGHT]
AXIS_NAMES = [n for n in NAMES if n not in NO_AXIS]
BACKENDS = ["numpy", "pandas", "polars", "xarray"]


def series(n: int, seed: int):
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    obs = 20 + 80 * np.exp(-(((t % 365) - 120) / 25.0) ** 2) + rng.gamma(2.0, 1.5, n)
    sim = np.clip(0.9 * obs + 4 + rng.normal(0, 4, n), 0.1, None)
    return obs, sim


def _transform(name: str, obs, sim):
    if name in BINARY_SCORE:
        event = (obs > np.quantile(obs, 0.8)).astype(float)
        span = sim.max() - sim.min()
        return event, np.clip((sim - sim.min()) / span, 0.0, 0.999)
    if name in BINARY_LABEL:
        threshold = np.quantile(obs, 0.8)
        return (obs > threshold).astype(float), (sim > threshold).astype(float)
    return obs, sim


def case_1d(name: str, n: int = 400, seed: int = 0):
    """obs, sim and the extra keyword arrays a metric needs."""
    obs, sim = _transform(name, *series(n, seed))
    extra = {}
    if name == "regNSE":
        extra["dates"] = np.datetime64("2001-01-01") + np.arange(n).astype("timedelta64[D]")
    elif name in ("ssigma_delta", "forecast_verification_delta"):
        extra["ref_date"] = np.arange(n) % 10
    elif name == "nse_variance_weighted":
        extra["gauge"] = np.arange(n) % 3
    return obs, sim, extra


def case_2d(name: str, n: int = 150, g: int = 12, seed: int = 1):
    """(time, station) arrays; every column is an independent series."""
    columns = [_transform(name, *series(n, seed + 7 * j)) for j in range(g)]
    obs = np.column_stack([c[0] * (1 + 0.1 * j) for j, c in enumerate(columns)])
    sim = np.column_stack([c[1] * (1 + 0.1 * j) for j, c in enumerate(columns)])
    if name in BINARY_SCORE | BINARY_LABEL:
        obs = np.column_stack([c[0] for c in columns])
        sim = np.column_stack([c[1] for c in columns])
    return obs, sim


def weights(shape, seed: int = 5):
    return np.random.default_rng(seed).uniform(0.5, 3.0, shape)


def wrap(backend: str, array: np.ndarray):
    if backend == "numpy":
        return array
    if backend == "pandas":
        pd = pytest.importorskip("pandas")
        return pd.Series(array) if array.ndim == 1 else pd.DataFrame(array)
    if backend == "polars":
        pl = pytest.importorskip("polars")
        if array.ndim == 1:
            return pl.Series("q", array)
        return pl.DataFrame({f"c{i}": array[:, i] for i in range(array.shape[1])})
    if backend == "xarray":
        xr = pytest.importorskip("xarray")
        dims = ["time"] if array.ndim == 1 else ["time", "station"]
        return xr.DataArray(array, dims=dims)
    raise ValueError(backend)


def values(result):
    """Numeric content of a result as an ndarray (dict components stacked on axis 0)."""
    value = result.value if hasattr(result, "value") else result
    if isinstance(value, dict):
        return np.stack([values(value[k]) for k in sorted(value)])
    xr = sys.modules.get("xarray")  # not imported => the value cannot be a DataArray
    if xr is not None and isinstance(value, xr.DataArray):
        return np.asarray(value.values, dtype=float)
    return np.asarray(value, dtype=float)


def same(a, b, rtol=1e-9):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return a.shape == b.shape and np.allclose(a, b, rtol=rtol, atol=1e-12, equal_nan=True)
