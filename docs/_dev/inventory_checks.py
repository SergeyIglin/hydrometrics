"""Точечные проверки поведения для INVENTORY.md (раздел 5).

Запуск из корня репозитория: ``PYTHONPATH=. python docs/_dev/inventory_checks.py``.
Каждый блок печатает факт, на который ссылается инвентаризация.
"""

from __future__ import annotations

import inspect
import json
import warnings

import numpy as np
import pandas as pd
import polars as pl
import xarray as xr

import hydrometrics as hm
from hydrometrics.backends import numpy as np_backend

warnings.simplefilter("ignore")
rng = np.random.default_rng(0)
n, g = 400, 3
obs = 30 + rng.gamma(2.0, 8.0, (n, g)) * np.array([1.0, 2.0, 0.5])
sim = obs * 0.9 + rng.normal(0, 5, (n, g))
w = rng.uniform(0.5, 2.0, (n, g))


def show(title, func):
    try:
        print(f"[{title}] {func()}")
    except Exception as exc:  # noqa: BLE001
        print(f"[{title}] EXC {type(exc).__name__}: {str(exc)[:150]}")


def per_col(metric_core, **kw):
    return np.array([metric_core(obs[:, i], sim[:, i], **kw) for i in range(g)])


print("--- A. axis: форма и корректность ---")
for name in ["nse", "rmse", "nrmse", "pbias", "kge_2009", "rsr", "ssigma", "ve", "willmott_d",
             "pearson_r", "spearman_r", "kendall_tau", "roc_auc", "pr_auc", "forecast_verification",
             "brier_score", "sharpness", "reliability", "crps", "crpss"]:
    f = getattr(hm, name)
    a, b = obs, sim
    if name in ("roc_auc", "pr_auc", "brier_score", "sharpness", "reliability"):
        a = (obs > np.median(obs, axis=0)).astype(float)
        b = np.clip(sim / sim.max(), 0, 0.99)

    def run(name=name, f=f, a=a, b=b):
        columns = [float(np.nanmean(f(a[:, i], b[:, i]).value)) for i in range(g)]
        res = f(a, b, axis=0, reduction="none").value
        res = np.asarray(res)
        agree = res.shape == (g,) and np.allclose(res, columns, equal_nan=True)
        return f"shape={res.shape} совпало_с_поколоночным={agree}"

    show(name, run)
    show(name + " axis=1 mean", lambda f=f, a=a, b=b: (np.asarray(f(a, b, axis=1, reduction='none').value).shape,
                                                       f(a, b, axis=1).value))

print("--- B. nrmse/pbias при axis=1: среднее против верного ---")
true_pbias = np.mean([100 * np.mean(sim[i] - obs[i]) / np.mean(obs[i]) for i in range(n)])
print("pbias axis=1 верное среднее", true_pbias)
show("pbias axis=1 библиотека", lambda: hm.pbias(obs, sim, axis=1).value)
show("pbias axis=0 библиотека, reduction=none", lambda: hm.pbias(obs, sim, axis=0, reduction="none").value)
print("pbias axis=0 верное", [100 * np.mean(sim[:, i] - obs[:, i]) / np.mean(obs[:, i]) for i in range(g)])
show("pbias axis=1 pandas", lambda: np.shape(hm.pbias(pd.DataFrame(obs), pd.DataFrame(sim), axis=1).value))
true_nrmse = np.mean([np.sqrt(np.mean((sim[i] - obs[i]) ** 2)) / np.mean(obs[i]) for i in range(n)])
print("nrmse axis=1 верное среднее", true_nrmse)
show("nrmse axis=1 библиотека", lambda: hm.nrmse(obs, sim, axis=1).value)
show("nrmse axis=0 библиотека, reduction=none", lambda: hm.nrmse(obs, sim, axis=0, reduction="none").value)
print("nrmse axis=0 верное", [np.sqrt(np.mean((sim[:, i] - obs[:, i]) ** 2)) / np.mean(obs[:, i]) for i in range(g)])
show("nrmse axis=0 std", lambda: hm.nrmse(obs, sim, axis=0, reduction="none", normalization="std").value)
show("spearman axis=0 2D", lambda: hm.spearman_r(obs, sim, axis=0, reduction="none").value)
show("roc_auc axis=0 2D", lambda: hm.roc_auc((obs > 40).astype(float), sim / sim.max(), axis=0, reduction="none").value)
show("ssigma numpy axis ignored", lambda: (float(hm.ssigma(obs, sim, axis=0).value), float(hm.ssigma(obs, sim).value)))

print("--- C. веса вместе с axis ---")
for name in ["mae", "nse", "pearson_r", "kge_2009", "alpha_component", "rsr", "sharpness", "nrmse"]:
    show(name + " sample_weight+axis=0", lambda name=name: np.asarray(
        getattr(hm, name)(obs, sim, axis=0, reduction="none", sample_weight=w).value).shape)

print("--- D. игнорирование весов ---")
for name in ["spearman_r", "kendall_tau", "roc_auc", "pr_auc", "ssigma", "forecast_verification"]:
    f = getattr(hm, name)
    a, b = obs[:, 0], sim[:, 0]
    if name in ("roc_auc", "pr_auc"):
        a = (a > np.median(a)).astype(float)
        b = b / b.max()
    show(name, lambda f=f, a=a, b=b: (float(f(a, b).value) == float(f(a, b, sample_weight=w[:, 0]).value)))
show("crps ensemble weights ignored", lambda: (
    float(hm.crps(obs[:, 0], sim).value) == float(hm.crps(obs[:, 0], sim, sample_weight=w[:, 0]).value)))

print("--- E. KGE: формула 2012 против Kling et al. ---")
a, b = obs[:, 0], sim[:, 0]
r = np.corrcoef(a, b)[0, 1]
alpha = b.std(ddof=1) / a.std(ddof=1)
beta = b.mean() / a.mean()
gamma = alpha / beta
print("kge_2012", float(hm.kge_2012(a, b).value))
print("4 слагаемых (r,alpha,beta,gamma)", 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2 + (gamma - 1) ** 2))
print("Kling 2012 (r,beta,gamma)", 1 - np.sqrt((r - 1) ** 2 + (beta - 1) ** 2 + (gamma - 1) ** 2))
print("kge_2009", float(hm.kge_2009(a, b).value), "ручной", 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2))
print("kge_2009 pandas value type", type(hm.kge_2009(pd.Series(a), pd.Series(b)).value).__name__)
show("float(kge_2009 pandas)", lambda: float(hm.kge_2009(pd.Series(a), pd.Series(b))))
show("kge_2009 xarray dim", lambda: hm.kge_2009(xr.DataArray(obs, dims=["time", "station"]),
                                                xr.DataArray(sim, dims=["time", "station"]), dim="time"))

print("--- F. xarray ---")
xo = xr.DataArray(obs, dims=["time", "station"], coords={"time": np.arange(n), "station": ["a", "b", "c"]})
xs = xr.DataArray(sim, dims=["time", "station"], coords={"time": np.arange(n), "station": ["a", "b", "c"]})
res = hm.nse(xo, xs, dim="time").value
print("dim=time", type(res).__name__, res.dims, res.coords["station"].values.tolist())
print("dim=time reduction=mean ignored", np.asarray(hm.nse(xo, xs, dim="time", reduction="mean").value).shape)
print("dim=[time,station]", np.asarray(hm.nse(xo, xs, dim=["time", "station"]).value).shape)
show("axis=0 xarray", lambda: hm.nse(xo, xs, axis=0))
show("dim=time for nrmse", lambda: hm.nrmse(xo, xs, dim="time").value.shape)
show("dim=time for pbias", lambda: hm.pbias(xo, xs, dim="time").value.shape)
show("dim=time for rsr", lambda: hm.rsr(xo, xs, dim="time").value.shape)
show("dim=time for ssigma", lambda: hm.ssigma(xo, xs, dim="time").value.shape)
show("no alignment: reversed coords", lambda: (float(hm.nse(xo, xs.isel(time=slice(None, None, -1))).value),
                                              float(hm.nse(xo, xs).value)))
ds_o = xr.Dataset({"q": xo})
ds_s = xr.Dataset({"q": xs})
show("Dataset dim=time", lambda: np.asarray(hm.nse(ds_o, ds_s, dim="time").value).shape)
show("Dataset no dim", lambda: float(hm.nse(ds_o, ds_s).value))
show("kge_components xarray type", lambda: {k: type(v).__name__ for k, v in hm.kge_components(xo, xs, dim="time").items()})
show("kge_components xarray value type", lambda: type(hm.kge_components(xo, xs, dim="time")["r"].value).__name__)

print("--- G. ленивые массивы dask ---")
xo_d = xo.chunk({"time": 100})
xs_d = xs.chunk({"time": 100})
out = hm.nse(xo_d, xs_d, dim="time").value
print("dask input result is", type(out.data).__name__)

print("--- H. pandas: индекс и подписи ---")
idx = pd.date_range("2001-01-01", periods=n)
so = pd.Series(obs[:, 0], index=idx)
ss = pd.Series(sim[:, 0], index=idx)
print("одинаковый индекс", float(hm.nse(so, ss).value))
print("обратный порядок индекса (без выравнивания)", float(hm.nse(so, ss.iloc[::-1]).value))
df_o = pd.DataFrame(obs, index=idx, columns=list("abc"))
df_s = pd.DataFrame(sim, index=idx, columns=list("abc"))
v = hm.nse(df_o, df_s, axis=0).value
print("DataFrame axis=0", type(v).__name__, np.shape(v))
print("Series+ndarray route", type(hm.nse(so, sim[:, 0])).__name__, float(hm.nse(so, sim[:, 0]).value))
print("sim Series obs ndarray route", float(hm.nse(obs[:, 0], ss).value))
show("pandas string column obs", lambda: hm.nse(pd.Series(["1", "2"]), pd.Series(["1", "2"])))
show("pandas nullable", lambda: float(hm.mae(pd.Series([1.0, None, 3.0], dtype="Float64"), pd.Series([1.0, 2.0, 2.0]))))

print("--- I. polars ---")
po = pl.Series("o", obs[:, 0])
ps = pl.Series("s", sim[:, 0])
print("polars series", float(hm.nse(po, ps).value))
print("polars with null", float(hm.mae(pl.Series([1.0, None, 3.0]), pl.Series([1.0, 2.0, 2.0])).value))
show("LazyFrame", lambda: hm.nse(pl.DataFrame({"a": obs[:, 0]}).lazy(), pl.DataFrame({"a": sim[:, 0]}).lazy()))
pf_o = pl.DataFrame({c: obs[:, i] for i, c in enumerate("abc")})
pf_s = pl.DataFrame({c: sim[:, i] for i, c in enumerate("abc")})
print("polars DF axis=0", np.shape(hm.nse(pf_o, pf_s, axis=0).value))

print("--- J. (the sentinel argument was removed in task_5) ---")
a = np.array([1.0, -999.0, 3.0, 4.0, 5.0])
b = np.array([1.1, 2.0, 2.9, 4.2, 5.0])
print("sample_weight in parameters?", "sample_weight" in hm.mae(a, b, sample_weight=np.ones(5)).parameters)
print("nan_info omit", hm.mae(np.array([1.0, np.nan]), np.array([1.0, 2.0]), nan_policy="omit").nan_info)
print("nan_info propagate", hm.mae(np.array([1.0, np.nan]), np.array([1.0, 2.0])).nan_info)
show("bad nan_policy numpy", lambda: hm.mae(np.array([1.0, np.nan]), np.array([1.0, 2.0]), nan_policy="bogus").value)
show("bad reduction numpy", lambda: np.shape(hm.mae(obs, sim, axis=0, reduction="bogus").value))
show("negative weight", lambda: hm.mae(a, b, sample_weight=-np.ones(5)))
show("zero weight sum", lambda: hm.mae(a, b, sample_weight=np.zeros(5)).value)
show("nan weight", lambda: hm.mae(a, b, sample_weight=np.array([1, np.nan, 1, 1, 1.0])).value)
show("list input", lambda: float(hm.nse([1.0, 2.0, 3.0], [1.1, 1.9, 3.2])))
show("int array", lambda: float(hm.nse(np.array([1, 2, 3]), np.array([1, 2, 4]))))
show("int nan check", lambda: hm.validate_inputs(np.array([1, 2]), np.array([1, 2]))[3])
show("string array", lambda: hm.nse(np.array(["a", "b"]), np.array(["a", "b"])))
show("validate default policy", lambda: hm.validate_inputs(np.array([1.0, np.nan]), np.array([1.0, 2.0]))[0])
show("axis out of range", lambda: hm.nse(obs, sim, axis=5))
show("Enum policy", lambda: hm.mae(np.array([1.0, np.nan]), np.array([1.0, 2.0]), nan_policy=hm.NanPolicy.RAISE))
show("Enum reduction", lambda: np.shape(hm.mae(obs, sim, axis=0, reduction=hm.Reduction.NONE).value))
show("Enum reduction SUM", lambda: np.shape(hm.mae(obs, sim, axis=0, reduction=hm.Reduction.SUM).value))

print("--- K. NaN не парно в propagate (обе стороны) ---")
a = obs[:, 0].copy()
b = sim[:, 0].copy()
a[0:40] = np.nan
mask = ~np.isnan(a)
print("pearson propagate", float(hm.pearson_r(a, b, nan_policy="propagate").value), "omit", float(hm.pearson_r(a, b, nan_policy="omit").value),
      "scipy-pair", np.corrcoef(a[mask], b[mask])[0, 1])
print("beta propagate", float(hm.beta_component(a, b).value), "omit", float(hm.beta_component(a, b, nan_policy="omit").value))
print("nse propagate", float(hm.nse(a, b).value), "omit", float(hm.nse(a, b, nan_policy="omit").value))
c = sim[:, 0].copy()
c[0:40] = np.nan
print("nse NaN only in sim propagate", float(hm.nse(obs[:, 0], c).value), "omit", float(hm.nse(obs[:, 0], c, nan_policy="omit").value))
print("accuracy NaN counted wrong", float(hm.accuracy(np.array([1.0, np.nan, 0.0]), np.array([1.0, 1.0, 0.0])).value))
print("axis omit keeps NaN handling per metric", hm.nse(np.array([[1.0, 2.0], [np.nan, 3.0], [3.0, 5.0]]),
                                                       np.array([[1.1, 2.0], [2.0, 3.0], [2.8, 5.1]]), axis=0, nan_policy="omit",
                                                       reduction="none").value)

print("--- L. reliability: p=1.0 и axis ---")
oo = np.array([1.0, 1.0, 0.0, 0.0])
pp = np.array([1.0, 1.0, 0.0, 0.0])
print("perfect with p=1", float(hm.reliability(oo, pp).value))
oo2 = np.array([0.0, 0.0, 0.0, 0.0])
print("always-wrong p=1", float(hm.reliability(oo2, np.ones(4)).value), "ожидается 1.0")
print("brier", float(hm.brier_score(oo2, np.ones(4)).value))
oz = (obs > np.median(obs, axis=0)).astype(float)
pz = np.clip(sim / sim.max(), 0, 0.99)
show("reliability axis=0 shape", lambda: np.shape(hm.reliability(oz, pz, axis=0, reduction="none").value))
show("reliability axis=0 vs none", lambda: (float(hm.reliability(oz, pz, axis=0).value), float(hm.reliability(oz, pz).value)))
print("brier outside range", float(hm.brier_score(np.array([0.0]), np.array([3.0])).value))

print("--- M. crps ---")
rng2 = np.random.default_rng(3)
o = rng2.normal(10, 2, 50)
e = o[:, None] + rng2.normal(0, 2, (50, 8))
fair = np.mean(np.abs(e - o[:, None]), axis=1) - 0.5 * np.mean([np.mean(np.abs(e[i][None] - e[i][:, None])[np.triu_indices(8, 1)]) for i in range(1)])
term1 = np.mean(np.abs(e - o[:, None]), axis=1)
ens_diff = np.abs(e[:, :, None] - e[:, None, :])
standard = term1 - 0.5 * ens_diff.mean(axis=(1, 2))
fair_est = term1 - 0.5 * ens_diff.sum(axis=(1, 2)) / (8 * 7)
print("lib", float(hm.crps(o, e).value), "standard m^2", standard.mean(), "fair m(m-1)", fair_est.mean())
print("2D obs ensemble", np.shape(hm.crps(obs, np.dstack([sim, sim + 1, sim - 1]), reduction="none").value))
print("2D obs ensemble axis=0", np.shape(hm.crps(obs, np.dstack([sim, sim + 1, sim - 1]), axis=0, reduction="none").value))
print("crpss per-sample mean vs ratio of means")
ref = o[:, None] + rng2.normal(0, 4, (50, 8))
c1 = hm.crps(o, e, reduction="none").value
c2 = hm.crps(o, ref, reduction="none").value
print("lib", float(hm.crpss(o, e, ref_forecast=ref).value), "ratio_of_means", 1 - c1.mean() / c2.mean(), "mean_of_ratios", np.mean(1 - c1 / c2))
print("crpss default deterministic ref == 1-MAE ratio", float(hm.crpss(o, e).value), 1 - c1.mean() / np.mean(np.abs(o - o.mean())))
print("weighted_crps func on ensemble == mean(w*crps)/mean(w)", float(hm.weighted_crps(o, e, weight_func=lambda y: y).value), np.sum(o * c1) / np.sum(o))
show("weighted_crps func deterministic", lambda: hm.weighted_crps(o, o + 1, weight_func=lambda y: y).value)
show("weighted_crps sample_weight no func", lambda: hm.weighted_crps(o, e, sample_weight=np.ones(50)).value)
show("weighted_crps sample_weight det", lambda: hm.weighted_crps(o, o + 1, sample_weight=np.ones(50)).value)

print("--- N. группировка ---")
df = pd.DataFrame({"q_obs": obs[:, 0], "q_sim": sim[:, 0], "month": idx.month, "station": np.repeat(["b", "a"], n // 2)})
gr = hm.compute_grouped(hm.nse, df, "q_obs", "q_sim", group_by="month")
print(repr(gr), "name", gr.name, gr.groups[:3], gr.values[:3], list(gr.meta))
gr2 = hm.compute_grouped(hm.nse, df, "q_obs", "q_sim", group_by=["station", "month"])
print("порядок появления", gr2.groups[:2], gr2.groups[-1], len(gr2))
print("to_pandas", gr.to_pandas().head(2).to_dict("list"))
print("to_dict keys", list(gr.to_dict()))
show("to_xarray single", lambda: gr.to_xarray().sizes)
show("to_xarray multi", lambda: gr2.to_xarray())
show("kge_components grouped", lambda: hm.compute_grouped(hm.kge_components, df, "q_obs", "q_sim", group_by="month"))
show("ssigma_delta grouped", lambda: hm.compute_grouped(hm.ssigma_delta, df, "q_obs", "q_sim", group_by="month", ref_date=np.ones(10)))
show("numpy dict", lambda: hm.compute_grouped(hm.rmse, None, obs[:, 0], sim[:, 0], group_by={"m": idx.month}).values[:2])
show("numpy names", lambda: hm.compute_grouped(hm.rmse, None, obs[:, 0], sim[:, 0], group_by="m"))
show("missing col", lambda: hm.compute_grouped(hm.rmse, df, "q_obs", "q_sim", group_by="zzz"))
show("empty dict", lambda: hm.compute_grouped(hm.rmse, df, "q_obs", "q_sim", group_by={}))
show("len mismatch", lambda: hm.compute_grouped(hm.rmse, None, obs[:, 0], sim[:, 0], group_by={"m": [1, 2]}))
show("NaN group key", lambda: len(hm.compute_grouped(hm.rmse, None, np.arange(4.0), np.arange(4.0), group_by={"m": np.array([np.nan, np.nan, 1, 1])})))
show("categorical empty group", lambda: len(hm.compute_grouped(hm.rmse, df.assign(c=pd.Categorical(df.month, categories=range(0, 20))), "q_obs", "q_sim", group_by="c")))
xds = xr.Dataset({"q_obs": ("time", obs[:, 0]), "q_sim": ("time", sim[:, 0])}, coords={"time": idx, "month": ("time", idx.month)})
show("xarray Dataset group, strings", lambda: hm.compute_grouped(hm.rmse, xds, "q_obs", "q_sim", group_by="month"))
show("xarray Dataset group, arrays", lambda: hm.compute_grouped(hm.rmse, xds, xds["q_obs"], xds["q_sim"], group_by="month").values[:2])
pf = pl.DataFrame({"q_obs": obs[:, 0], "q_sim": sim[:, 0], "m": idx.month.values})
show("polars names", lambda: hm.compute_grouped(hm.rmse, pf, "q_obs", "q_sim", group_by="m"))
show("polars dict", lambda: hm.compute_grouped(hm.rmse, None, pf["q_obs"], pf["q_sim"], group_by={"m": pf["m"]}).values[:2])
show("2D data groups", lambda: hm.compute_grouped(hm.rmse, None, obs, sim, group_by={"m": idx.month}).values[:2])
show("group of size 1 nse", lambda: hm.compute_grouped(hm.nse, None, np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.5]), group_by={"m": [1, 1, 2]}).values)

print("--- O. MetricResult ---")
res = hm.nse(obs[:, 0], sim[:, 0])
print(str(res))
print(repr(res))
print("type(value)", type(res.value).__name__, "is_scalar", res.is_scalar, "scalar_value", res.scalar_value)
show("frozen", lambda: setattr(res, "value", 1))
show("json.dumps to_dict", lambda: len(json.dumps(res.to_dict())))
print("to_dict keys", list(res.to_dict()))
print("norm_source default", res.norm_source)
print("norm_source norm", hm.nse(obs[:, 0], sim[:, 0], norm=1.0).norm_source)
print("norm_source pandas", hm.nse(pd.Series(obs[:, 0]), pd.Series(sim[:, 0]), norm=1.0).norm_source)
print("meta numpy", list(res.meta), "meta pandas", list(hm.nse(so, ss).meta))
show("json r2 0-d", lambda: json.dumps(hm.r2(obs[:, 0], sim[:, 0]).to_dict()))
show("json dict value", lambda: len(json.dumps(hm.kge_components(obs[:, 0], sim[:, 0]).to_dict())))
show("float dict value", lambda: float(hm.kge_components(obs[:, 0], sim[:, 0])))
show("str dict", lambda: str(hm.kge_components(obs[:, 0], sim[:, 0])))
show("str r2", lambda: str(hm.r2(obs[:, 0], sim[:, 0])))
show("is_scalar r2", lambda: hm.r2(obs[:, 0], sim[:, 0]).is_scalar)
show("float r2", lambda: float(hm.r2(obs[:, 0], sim[:, 0])))
show("str DataArray value", lambda: str(hm.nse(xo, xs, dim="time"))[:80])
show("is_scalar 0d DataArray", lambda: hm.nse(xo, xs, dim=["time", "station"]).is_scalar)
show("gauge params json", lambda: json.dumps(hm.nse_variance_weighted(obs[:, 0], sim[:, 0], gauge=np.arange(n) % 3).to_dict()))
show("norm array json", lambda: json.dumps(hm.nse(obs[:, 0], sim[:, 0], norm=np.ones(n)).to_dict()))
show("str bounds inf in json", lambda: json.dumps(res.to_dict()["bounds"]))

print("--- P. метрики с параметрами ---")
a = obs[:, 0]
b = sim[:, 0]
for nm in ("mean", "std", "range", "iqr"):
    print("nrmse", nm, float(hm.nrmse(a, b, normalization=nm).value))
show("nrmse bad", lambda: hm.nrmse(a, b, normalization="bogus"))
print("nse norm=mean == default", float(hm.nse(a, b, norm=a.mean()).value) == float(hm.nse(a, b).value))
show("nse norm axis scalar", lambda: hm.nse(obs, sim, axis=0, norm=10.0, reduction="none").value)
show("nse norm axis array", lambda: hm.nse(obs, sim, axis=0, norm=np.array([1.0, 2.0, 3.0]), reduction="none").value)
show("modified_nse norm axis scalar", lambda: hm.modified_nse(obs, sim, axis=0, norm=10.0, reduction="none").value)
show("modified_nse norm axis array", lambda: hm.modified_nse(obs, sim, axis=0, norm=np.array([1.0, 2.0, 3.0]), reduction="none").value)
show("log_nse negative", lambda: float(hm.log_nse(np.array([-1.0, 1.0, 2.0, 3.0]), np.array([1.0, 1.0, 2.0, 3.0])).value))
show("log_nse zero eps", lambda: float(hm.log_nse(np.array([0.0, 1.0, 2.0, 3.0]), np.array([1.0, 1.0, 2.0, 3.0])).value))
show("log_nse zero eps=0", lambda: float(hm.log_nse(np.array([0.0, 1.0, 2.0, 3.0]), np.array([1.0, 1.0, 2.0, 3.0]), eps=0.0).value))
show("log_nse pass epsilon", lambda: float(hm.log_nse(a, b, eps=0.1).value))
print("alpha version 2009 == 2012", float(hm.alpha_component(a, b, version="2009").value) == float(hm.alpha_component(a, b, version="2012").value))
show("alpha bad version", lambda: hm.alpha_component(a, b, version="1999").value)
show("kge_components bad version", lambda: hm.kge_components(a, b, version="1999"))
show("kge_components pandas 2009", lambda: list(hm.kge_components(so, ss, version="2009").value))
show("kge_components pandas bad", lambda: list(hm.kge_components(so, ss, version="1999").value))
print("ssigma m", float(hm.ssigma(a, b, m=0).value), float(hm.ssigma(a, b, m=2).value))
show("ssigma small", lambda: hm.ssigma(a[:2], b[:2]))
show("ssigma NaN only in sim", lambda: float(hm.ssigma(a, np.where(np.arange(n) < 40, np.nan, b)).value))
show("ssigma pandas weight", lambda: hm.ssigma(so, ss, weight=np.ones(n)))
show("ssigma axis=0", lambda: hm.ssigma(obs, sim, axis=0, reduction="none").value)
show("ssigma axis=0 pandas", lambda: np.shape(hm.ssigma(df_o, df_s, axis=0).value))
show("fv reduction none", lambda: hm.forecast_verification(a, b, reduction="none").value[:5])
show("fv axis=0", lambda: np.shape(hm.forecast_verification(obs, sim, axis=0, reduction="none").value))
show("fv pandas", lambda: hm.forecast_verification(so, ss).value[:5])
rd = np.arange(n) % 10
print("fv delta", float(hm.forecast_verification_delta(a, b, ref_date=rd).value))
show("fv delta list ref", lambda: hm.forecast_verification_delta(a, b, ref_date=list(rd)))
show("fv delta shape mismatch", lambda: hm.forecast_verification_delta(a, b, ref_date=rd[:5]))
show("fv delta positional", lambda: float(hm.forecast_verification_delta(a, b, rd).value))
show("fv delta axis", lambda: hm.forecast_verification_delta(a, b, ref_date=rd, axis=0))
show("ssigma_delta axis", lambda: float(hm.ssigma_delta(a, b, ref_date=rd, axis=0).value))
show("ssigma_delta weight", lambda: float(hm.ssigma_delta(a, b, ref_date=rd, sample_weight=np.ones(n)).value))
show("ssigma_delta pandas Series ref", lambda: hm.ssigma_delta(so, ss, ref_date=pd.Series(rd, index=idx)).value[:3])
show("ssigma_delta small group -> NaN", lambda: hm.ssigma_delta(np.array([1.0, 2.0, 3.0, 4.0]), np.array([1.1, 2.1, 3.1, 4.1]), ref_date=np.array([1, 1, 2, 2]), reduction="none").value)
show("nvw axis", lambda: float(hm.nse_variance_weighted(a, b, gauge=rd, axis=0).value))
show("nvw weight", lambda: float(hm.nse_variance_weighted(a, b, gauge=rd, sample_weight=np.ones(n)).value))
show("nvw pandas weight", lambda: hm.nse_variance_weighted(so, ss, gauge=rd, weight=np.ones(n)))
show("nvw 2D", lambda: hm.nse_variance_weighted(obs, sim, gauge=np.arange(n)))
show("nvw missing gauge", lambda: hm.nse_variance_weighted(a, b))
gauge = np.repeat([0, 1], n // 2)
n0 = float(hm.nse(a[:n // 2], b[:n // 2]).value)
n1 = float(hm.nse(a[n // 2:], b[n // 2:]).value)
v0, v1 = a[:n // 2].var(), a[n // 2:].var()
print("nvw check", float(hm.nse_variance_weighted(a, b, gauge=gauge).value), (v0 * n0 + v1 * n1) / (v0 + v1))
pool = 1 - (np.sum((a[:n // 2] - b[:n // 2]) ** 2) + np.sum((a[n // 2:] - b[n // 2:]) ** 2)) / (n // 2 * (v0 + v1))
print("nvw equals pooled per-station ss", pool)
dates = np.datetime64("2004-01-01") + np.arange(366 * 2 + 365).astype("timedelta64[D]")
qo = 10 + 5 * np.sin(np.arange(dates.size) / 58.0) ** 2 + np.random.default_rng(5).gamma(2, 1, dates.size)
qs = qo * 1.05
print("regNSE", float(hm.regNSE(qo, qs, dates=dates).value))
show("regNSE regime 365", lambda: float(hm.regNSE(qo, qs, dates=dates, regime=np.sort(qo)[::-3][:365]).value))
show("regNSE regime wrong", lambda: hm.regNSE(qo, qs, dates=dates, regime=np.ones(10)))
show("regNSE str dates", lambda: float(hm.regNSE(qo, qs, dates=dates.astype(str)).value))
show("regNSE pandas dt", lambda: float(hm.regNSE(pd.Series(qo), pd.Series(qs), dates=pd.Series(pd.to_datetime(dates.astype(str)))).value))
show("regNSE DatetimeIndex", lambda: float(hm.regNSE(pd.Series(qo), pd.Series(qs), dates=pd.to_datetime(dates.astype(str))).value))
show("regNSE polars dt", lambda: float(hm.regNSE(pl.Series(qo), pl.Series(qs), dates=pl.Series(dates)).value))
show("regNSE xarray dt", lambda: float(hm.regNSE(xr.DataArray(qo), xr.DataArray(qs), dates=dates).value))
print("meanyear_ranked leap-year: last two values averaged; Q_reg averages positions 59/60")
mah = hm.mean_annual_hydrograph(qo, dates)
print("mah", mah.shape, "fdc", hm.mean_annual_hydrograph_duration_curve(qo, dates).shape)
print("day index 29 Feb/1 Mar", np_backend._annual_day_index(np.array(["2004-02-28", "2004-02-29", "2004-03-01"], dtype="datetime64[D]")).tolist())
qo_short = qo.copy()
qo_short[100:140] = np.nan
show("regNSE partial year (NaN in obs only)", lambda: float(hm.regNSE(qo_short, qs, dates=dates).value))
show("regNSE sim NaN mismatch", lambda: float(hm.regNSE(qo, np.where(np.arange(dates.size) < 30, np.nan, qs), dates=dates).value))
print("regNSE with a partial calendar year (Jan–Mar 2 yrs)", float(hm.regNSE(qo[:400], qs[:400], dates=dates[:400]).value))
d_noleap = np.datetime64("2001-01-01") + np.arange(365).astype("timedelta64[D]")
show("regNSE single year regime mean == year => denominator", lambda: float(hm.regNSE(qo[:365], qs[:365], dates=d_noleap).value))
ranked_o = np.sort(qo[:365])[::-1]
print("Q_reg from mean hydrograph, not per-year rank mean: differs", )
yrs = (dates.astype("datetime64[Y]").astype(int) + 1970)
per_rank = np.nanmean(np.vstack([np.sort(qo[yrs == y])[::-1][:365] for y in np.unique(yrs) if np.sum(yrs == y) >= 365]), axis=0)
curve = hm.mean_annual_hydrograph_duration_curve(qo, dates)
print("  max |rank-mean − FDC of mean hydrograph|", float(np.nanmax(np.abs(per_rank - curve))))

print("--- Q. классификационные пограничные ---")
o_ = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=float)
s_ = np.array([1, 0, 1, 0, 0, 0, 0, 0, 0, 0], dtype=float)
print("edi", float(hm.edi(o_, s_).value), "sedi", float(hm.sedi(o_, s_).value))
H, F = 0.5, 1 / 8
print("edi manual", (np.log(F) - np.log(H)) / (np.log(F) + np.log(H)))
print("sedi manual", (np.log(F) - np.log(H) - np.log(1 - F) + np.log(1 - H)) / (np.log(F) + np.log(H) + np.log(1 - F) + np.log(1 - H)))
print("edi H=1,F=0", float(hm.edi(o_, o_).value), "sedi", float(hm.sedi(o_, o_).value))
print("edi H=0", float(hm.edi(o_, 1 - o_).value), "sedi", float(hm.sedi(o_, 1 - o_).value))
print("edi F=0,H<1", float(hm.edi(np.array([1.0, 1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0, 0.0])).value))
print("edi H=1,F>0", float(hm.edi(np.array([1.0, 0.0, 0.0, 0.0]), np.array([1.0, 1.0, 0.0, 0.0])).value))
print("sedi H=1,F>0", float(hm.sedi(np.array([1.0, 0.0, 0.0, 0.0]), np.array([1.0, 1.0, 0.0, 0.0])).value))
print("edi without warnings? bounds check: H=.5,F=.9", (np.log(.9) - np.log(.5)) / (np.log(.9) + np.log(.5)))
print("precision no positives", float(hm.precision(o_, np.zeros(10)).value))
print("f1 tp=0", float(hm.f1_score(o_, 1 - o_).value))
print("positive_class=0", float(hm.precision(o_, s_, positive_class=0).value), float(hm.recall(o_, s_, positive_class=0).value))
print("accuracy multiclass", float(hm.accuracy(np.array([1, 2, 3]), np.array([1, 2, 4])).value))
print("edi non-binary treated", float(hm.edi(np.array([2.0, 1.0, 0.0, 0.0]), np.array([2.0, 1.0, 1.0, 0.0])).value))
print("roc constant score", float(hm.roc_auc(np.array([1.0, 0.0, 1.0, 0.0]), np.ones(4)).value))
print("pr constant score", float(hm.pr_auc(np.array([1.0, 0.0, 1.0, 0.0]), np.ones(4)).value))
show("roc weights", lambda: float(hm.roc_auc(o_, s_, sample_weight=np.arange(1, 11.0)).value))
print("pr_auc ties", float(hm.pr_auc(np.array([1.0, 0.0, 1.0, 0.0]), np.array([0.8, 0.8, 0.3, 0.2])).value))
print("roc polarity worst", float(hm.roc_auc(np.array([1.0, 1.0, 0.0, 0.0]), np.array([0.1, 0.2, 0.8, 0.9])).value))

print("--- R. метаданные и сигнатуры ---")
print("signature", inspect.signature(hm.nse))
print("__name__", hm.nse.__name__, "__module__", hm.nse.__module__, "__wrapped__" in dir(hm.nse))
print("attrs", {a: getattr(hm.nse, a, None) for a in ("name", "direction", "bounds", "reference")})
print("regNSE __name__", hm.regNSE.__name__, "ssigma name", hm.ssigma.name)
print("registry attrs", [a for a in dir(hm.registry) if not a.startswith("__")])
print("get_backend_type", [__import__("hydrometrics.core.dispatch", fromlist=["x"]).get_backend_type(x) for x in (np.ones(1), pd.Series([1.0]), xo, po, [1.0])])
print("exported helper", hm.mean_annual_hydrograph.__module__, "annual day", np_backend._annual_day_index.__module__)
print("direction bias", hm.bias.direction, "bounds", hm.bias.bounds, "sharpness", hm.sharpness.direction)
print("positional m (pandas)", )
show("ssigma positional m numpy", lambda: float(hm.ssigma(a, b, 3).value))
print("regNSE docstring claim shape", hm.regNSE.__doc__.strip().splitlines()[0])
print("_weighted_var weights with axis", )
show("direct _weighted_var", lambda: np_backend._weighted_var(obs, w, 0, ddof=1).shape)
