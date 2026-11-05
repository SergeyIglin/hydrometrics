"""Эмпирический зонд для INVENTORY.md: фиксирует фактическое поведение всех метрик.

Запуск из корня репозитория:

    PYTHONPATH=. python docs/_dev/inventory_probe.py docs/_dev/inventory_probe.json

Скрипт ничего не меняет в пакете. Для каждой метрики и каждого бэкенда он
выполняет набор вызовов и записывает тип результата, форму, значение,
предупреждения и исключение.
"""

from __future__ import annotations

import json
import sys
import warnings

import numpy as np
import pandas as pd
import polars as pl
import xarray as xr

import hydrometrics as hm

REGRESSION = ["mae", "mse", "rmse", "nrmse", "bias", "pbias", "r2", "pearson_r",
              "spearman_r", "kendall_tau", "willmott_d"]
HYDRO = ["nse", "log_nse", "modified_nse", "nse_bounded", "kge_2009", "kge_2012", "kge_components",
         "r_component", "alpha_component", "beta_component", "gamma_component", "rsr", "ve",
         "ssigma", "ssigma_delta", "forecast_verification", "forecast_verification_delta",
         "regNSE", "nse_variance_weighted"]
PROBABILISTIC = ["crps", "weighted_crps", "crpss", "brier_score", "reliability", "sharpness"]
CLASSIFICATION = ["accuracy", "precision", "recall", "f1_score", "roc_auc", "pr_auc", "edi", "sedi"]
ALL_METRICS = REGRESSION + HYDRO + PROBABILISTIC + CLASSIFICATION

FAMILY = {**{m: "regression" for m in REGRESSION}, **{m: "hydro" for m in HYDRO},
          **{m: "probabilistic" for m in PROBABILISTIC},
          **{m: "classification" for m in CLASSIFICATION}}

# Метрики, которым на вход нужны бинарные наблюдения.
BINARY_SCORE = {"brier_score", "reliability", "sharpness", "roc_auc", "pr_auc"}
BINARY_LABEL = {"accuracy", "precision", "recall", "f1_score", "edi", "sedi"}

N = 1096
DATES = np.datetime64("2001-01-01") + np.arange(N).astype("timedelta64[D]")


def continuous(n: int = N) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    t = np.arange(n)
    obs = 20 + 80 * np.exp(-((t % 365 - 120) / 25.0) ** 2) + rng.gamma(2.0, 1.5, n)
    sim = 0.9 * obs + 4 + rng.normal(0, 4, n)
    return obs, np.clip(sim, 0.1, None)


def data_for(name: str) -> tuple[np.ndarray, np.ndarray]:
    obs, sim = continuous()
    if name in BINARY_SCORE:
        event = (obs > np.quantile(obs, 0.8)).astype(float)
        score = np.clip((sim - sim.min()) / (sim.max() - sim.min()), 0.0, 0.999)
        return event, score
    if name in BINARY_LABEL:
        threshold = np.quantile(obs, 0.8)
        return (obs > threshold).astype(float), (sim > threshold).astype(float)
    return obs, sim


def extras(name: str, n: int = N) -> dict:
    if name == "regNSE":
        return {"dates": DATES[:n]}
    if name == "ssigma_delta" or name == "forecast_verification_delta":
        return {"ref_date": np.arange(n) % 10}
    if name == "nse_variance_weighted":
        return {"gauge": np.arange(n) % 3}
    return {}


def describe(value):
    """Компактное JSON-совместимое описание значения результата."""
    if isinstance(value, dict):
        return {"kind": "dict", "items": {k: describe(v) for k, v in value.items()}}
    if isinstance(value, tuple):
        return {"kind": "tuple", "items": [describe(v) for v in value]}
    if isinstance(value, xr.DataArray):
        return {"kind": "DataArray", "dims": list(value.dims), "shape": list(value.shape)}
    if isinstance(value, np.ndarray):
        out = {"kind": "ndarray", "shape": list(value.shape), "dtype": str(value.dtype)}
        if value.ndim == 0:
            out["value"] = float(value)
        return out
    if isinstance(value, hm.MetricResult):
        return {"kind": "MetricResult", "value": describe(value.value)}
    if isinstance(value, (float, int, np.floating, np.integer)):
        return {"kind": type(value).__name__, "value": float(value)}
    return {"kind": type(value).__name__, "repr": repr(value)[:120]}


def call(func, *args, **kwargs) -> dict:
    """Вызвать метрику и записать результат, исключение и предупреждения."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            res = func(*args, **kwargs)
            out = {"ok": True, "type": type(res).__name__}
            out["value"] = describe(res.value) if hasattr(res, "value") else describe(res)
            if hasattr(res, "nan_info"):
                out["nan_info"] = res.nan_info
            if hasattr(res, "bounds"):
                out["bounds"] = [None if b is None else float(b) for b in res.bounds]
                out["direction"] = res.direction
                out["name"] = res.name
        except Exception as exc:  # noqa: BLE001  нужен сам факт и текст исключения
            out = {"ok": False, "exc": type(exc).__name__, "msg": str(exc)[:200]}
    if caught:
        out["warnings"] = sorted({f"{w.category.__name__}: {str(w.message)[:80]}" for w in caught})
    return out


def wrap(backend: str, arr: np.ndarray):
    if backend == "numpy":
        return arr
    if backend == "pandas":
        return pd.Series(arr) if arr.ndim == 1 else pd.DataFrame(arr)
    if backend == "polars":
        if arr.ndim == 1:
            return pl.Series("q", arr)
        return pl.DataFrame({f"c{i}": arr[:, i] for i in range(arr.shape[1])})
    if backend == "xarray":
        dims = ["time"] if arr.ndim == 1 else ["time", "station"]
        return xr.DataArray(arr, dims=dims)
    raise ValueError(backend)


def probe_metric(name: str) -> dict:
    func = getattr(hm, name)
    obs, sim = data_for(name)
    kw = extras(name)
    rec: dict = {"family": FAMILY[name]}

    for backend in ("numpy", "pandas", "polars", "xarray"):
        o, s = wrap(backend, obs), wrap(backend, sim)
        b: dict = {"base": call(func, o, s, **kw)}

        # NaN: одна пропущенная пара при каждой политике.
        obs_nan = obs.copy()
        obs_nan[5] = np.nan
        for policy in ("propagate", "omit", "raise"):
            b[f"nan_{policy}"] = call(func, wrap(backend, obs_nan), s, nan_policy=policy, **kw)
        b["nan_default"] = call(func, wrap(backend, obs_nan), s, **kw)

        obs_inf = obs.copy()
        obs_inf[5] = np.inf
        b["inf"] = call(func, wrap(backend, obs_inf), s, **kw)

        b["all_nan"] = call(func, wrap(backend, np.full_like(obs, np.nan)), s, **kw)
        b["const_obs"] = call(func, wrap(backend, np.full_like(obs, obs[0])), s, **kw)
        b["identical"] = call(func, o, o.copy() if hasattr(o, "copy") else o, **kw)
        b["zeros"] = call(func, wrap(backend, np.zeros_like(obs)), wrap(backend, np.zeros_like(sim)), **kw)
        if FAMILY[name] in ("regression", "hydro"):
            b["negative"] = call(func, wrap(backend, obs - obs.mean()), wrap(backend, sim - obs.mean()), **kw)
        b["empty"] = call(func, wrap(backend, np.array([], dtype=float)),
                          wrap(backend, np.array([], dtype=float)), **extras(name, 0))
        b["length_mismatch"] = call(func, o, wrap(backend, sim[:-1]), **kw)

        # Веса: оба имени параметра, потому что numpy и остальные бэкенды различаются.
        weights = np.linspace(1.0, 2.0, obs.size)
        b["sample_weight"] = call(func, o, s, sample_weight=weights, **kw)
        b["weight"] = call(func, o, s, weight=weights, **kw)

        # Оси: (время, створ).
        if not kw:
            obs2 = np.column_stack([obs, obs * 0.7 + 3, obs * 1.3 + 1])
            sim2 = np.column_stack([sim, sim * 0.6 + 4, sim * 1.2 + 2])
            if name in BINARY_SCORE | BINARY_LABEL:
                obs2 = np.column_stack([obs, obs, obs])
                sim2 = np.column_stack([sim, sim, sim])
            o2, s2 = wrap(backend, obs2), wrap(backend, sim2)
            b["2d_none"] = call(func, o2, s2)
            for axis in (0, 1):
                b[f"axis{axis}"] = call(func, o2, s2, axis=axis)
                b[f"axis{axis}_rednone"] = call(func, o2, s2, axis=axis, reduction="none")
            b["reduction_sum"] = call(func, o2, s2, axis=0, reduction="sum")
            if backend == "xarray":
                b["dim_time"] = call(func, o2, s2, dim="time")
        rec[backend] = b
    return rec


def probe_ensemble() -> dict:
    rng = np.random.default_rng(1)
    obs, _ = continuous(200)
    ens = obs[:, None] + rng.normal(0, 5, (200, 12))
    out = {}
    for name in ("crps", "weighted_crps", "crpss"):
        func = getattr(hm, name)
        out[name] = {
            "numpy": call(func, obs, ens),
            "pandas": call(func, pd.Series(obs), pd.DataFrame(ens)),
            "polars": call(func, pl.Series(obs), pl.DataFrame(ens)),
            "xarray": call(func, xr.DataArray(obs, dims=["time"]),
                           xr.DataArray(ens, dims=["time", "member"])),
            "numpy_rednone": call(func, obs, ens, reduction="none"),
        }
    bad = obs.copy()
    bad[3] = np.nan
    out["crps"]["nan_omit"] = call(hm.crps, bad, ens, nan_policy="omit")
    out["crps"]["nan_propagate"] = call(hm.crps, bad, ens, nan_policy="propagate")
    out["crps"]["sample_weight"] = call(hm.crps, obs, ens, sample_weight=np.linspace(1, 3, 200))
    out["crps"]["axis0"] = call(hm.crps, obs, ens, axis=0)
    out["weighted_crps"]["func_det"] = call(hm.weighted_crps, obs, obs + 1.0, weight_func=lambda y: y)
    out["weighted_crps"]["func_ens"] = call(hm.weighted_crps, obs, ens, weight_func=lambda y: y)
    out["crpss"]["ref_ens"] = call(hm.crpss, obs, ens, ref_forecast=np.tile(obs.mean(), (200, 12)))
    return out


def probe_public() -> dict:
    all_names = list(hm.__all__)
    public = [n for n in dir(hm) if not n.startswith("__")]
    missing = [n for n in all_names if not hasattr(hm, n)]
    extra = [n for n in public if n not in all_names]
    return {"__all__": all_names, "not_in___all__": extra, "in_all_but_missing": missing,
            "duplicates_in_all": sorted({n for n in all_names if all_names.count(n) > 1})}


if __name__ == "__main__":
    report = {"versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                           "pandas": pd.__version__, "polars": pl.__version__,
                           "xarray": xr.__version__},
              "public": probe_public(),
              "metrics": {m: probe_metric(m) for m in ALL_METRICS},
              "ensemble": probe_ensemble()}
    target = sys.argv[1] if len(sys.argv) > 1 else "inventory_probe.json"
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1, default=str)
    print("written", target, "metrics:", len(report["metrics"]))
