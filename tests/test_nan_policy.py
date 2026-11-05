"""One NaN policy on every metric and backend (report items #1-#6, #22; D6)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm
from _cases import (
    AXIS_NAMES, BACKENDS, ELEMENTWISE, NAMES, case_1d, case_2d, same, values, wrap,
)

GAP_OBS = [5, 40, 41, 200]
GAP_SIM = [10, 80, 200, 300]


def gaps(obs, sim):
    obs_g, sim_g = obs.astype(float).copy(), sim.astype(float).copy()
    obs_g[GAP_OBS] = np.nan
    sim_g[GAP_SIM] = np.nan
    keep = ~(np.isnan(obs_g) | np.isnan(sim_g))
    return obs_g, sim_g, keep


def _filter(extra, keep):
    return {k: v[keep] for k, v in extra.items()}


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("name", NAMES)
def test_omit_removes_pairs_and_equals_filtered_call(name, backend):
    obs, sim, extra = case_1d(name)
    obs_g, sim_g, keep = gaps(obs, sim)
    f = getattr(hm, name)
    got = f(wrap(backend, obs_g), wrap(backend, sim_g), nan_policy="omit", **extra)
    expected = f(obs_g[keep], sim_g[keep], **_filter(extra, keep))
    assert same(values(got), values(expected)), (name, backend)


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("name", NAMES)
def test_default_policy_is_omit(name, backend):
    obs, sim, extra = case_1d(name)
    obs_g, sim_g, _ = gaps(obs, sim)
    f = getattr(hm, name)
    a = f(wrap(backend, obs_g), wrap(backend, sim_g), **extra)
    b = f(wrap(backend, obs_g), wrap(backend, sim_g), nan_policy="omit", **extra)
    assert same(values(a), values(b))
    assert a.nan_info["policy"] == "omit"


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("name", NAMES)
def test_propagate_gives_nan_when_a_pair_is_missing(name, backend):
    obs, sim, extra = case_1d(name)
    obs_g, sim_g, _ = gaps(obs, sim)
    got = getattr(hm, name)(wrap(backend, obs_g), wrap(backend, sim_g), nan_policy="propagate", **extra)
    assert np.isnan(values(got)).all(), (name, backend)


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("name", NAMES)
def test_propagate_is_exact_without_gaps(name, backend):
    obs, sim, extra = case_1d(name)
    f = getattr(hm, name)
    a = f(wrap(backend, obs), wrap(backend, sim), nan_policy="propagate", **extra)
    b = f(wrap(backend, obs), wrap(backend, sim), nan_policy="omit", **extra)
    assert same(values(a), values(b))


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("where", ["obs", "sim"])
def test_raise_gives_value_error_on_every_backend(name, backend, where):
    obs, sim, extra = case_1d(name)
    obs_g, sim_g = obs.astype(float).copy(), sim.astype(float).copy()
    (obs_g if where == "obs" else sim_g)[7] = np.nan
    with pytest.raises(ValueError, match="NaN"):
        getattr(hm, name)(wrap(backend, obs_g), wrap(backend, sim_g), nan_policy="raise", **extra)


@pytest.mark.parametrize("backend", BACKENDS)
def test_raise_is_silent_without_nan(backend):
    obs, sim, _ = case_1d("nse")
    assert np.isfinite(float(hm.nse(wrap(backend, obs), wrap(backend, sim), nan_policy="raise")))


@pytest.mark.parametrize("backend", BACKENDS)
def test_unknown_policy_is_rejected(backend):
    obs, sim, _ = case_1d("nse")
    with pytest.raises(ValueError, match="nan_policy"):
        hm.nse(wrap(backend, obs), wrap(backend, sim), nan_policy="bogus")


def test_policy_accepts_enum_members():
    obs, sim, _ = case_1d("nse")
    obs_g, sim_g, keep = gaps(obs, sim)
    a = hm.nse(obs_g, sim_g, nan_policy=hm.NanPolicy.OMIT)
    assert same(values(a), values(hm.nse(obs_g[keep], sim_g[keep])))
    with pytest.raises(ValueError):
        hm.nse(obs_g, sim_g, nan_policy=hm.NanPolicy.RAISE)


# ---- policies along an axis ----

def _gappy_2d(name):
    obs, sim = case_2d(name)
    obs_g, sim_g = obs.astype(float).copy(), sim.astype(float).copy()
    obs_g[[3, 17, 90], 1] = np.nan
    sim_g[[20, 21], 1] = np.nan
    obs_g[[50], 4] = np.nan
    sim_g[[60, 61, 62], 7] = np.nan
    return obs_g, sim_g


@pytest.mark.parametrize("name", [n for n in AXIS_NAMES if n not in ELEMENTWISE])
def test_omit_with_axis_is_pairwise_per_slice(name):
    """#3: omit with an axis removed nothing."""
    obs_g, sim_g = _gappy_2d(name)
    f = getattr(hm, name)
    got = values(f(obs_g, sim_g, axis=0, nan_policy="omit"))
    parts = []
    for j in range(obs_g.shape[1]):
        keep = ~(np.isnan(obs_g[:, j]) | np.isnan(sim_g[:, j]))
        parts.append(values(f(obs_g[keep, j], sim_g[keep, j], reduction="none")))
    assert same(got, np.stack(parts, axis=-1)), name


@pytest.mark.parametrize("name", [n for n in AXIS_NAMES if n not in ELEMENTWISE])
def test_propagate_with_axis_poisons_only_slices_with_nan(name):
    obs_g, sim_g = _gappy_2d(name)
    f = getattr(hm, name)
    got = values(f(obs_g, sim_g, axis=0, nan_policy="propagate"))
    bad = np.zeros(obs_g.shape[1], dtype=bool)
    bad[[1, 4, 7]] = True
    assert np.isnan(got[..., bad]).all()
    clean = values(f(*case_2d(name), axis=0))
    assert same(got[..., ~bad], clean[..., ~bad])


def test_propagate_with_axis_and_mean_gives_nan():
    obs_g, sim_g = _gappy_2d("nse")
    assert np.isnan(float(hm.nse(obs_g, sim_g, axis=0, nan_policy="propagate", reduction="mean")))


# ---- nan_info ----

@pytest.mark.parametrize("backend", BACKENDS)
def test_nan_info_counts_removed_pairs(backend):
    obs, sim, _ = case_1d("nse")
    obs_g, sim_g, keep = gaps(obs, sim)
    wo, ws = wrap(backend, obs_g), wrap(backend, sim_g)
    removed = int((~keep).sum())
    info = hm.nse(wo, ws, nan_policy="omit").nan_info
    assert info == {"policy": "omit", "n_nan_removed": removed, "n_total": obs.size}
    assert hm.nse(wo, ws, nan_policy="propagate").nan_info["n_nan_removed"] == 0
    assert hm.nse(wrap(backend, obs), wrap(backend, sim)).nan_info["n_nan_removed"] == 0


# ---- extra arrays are not misaligned by omit (#5) ----

@pytest.mark.parametrize("name", ["regNSE", "ssigma_delta", "forecast_verification_delta", "nse_variance_weighted"])
def test_extra_arrays_stay_aligned_when_pairs_are_dropped(name):
    obs, sim, extra = case_1d(name)
    obs_g, sim_g, keep = gaps(obs, sim)
    got = getattr(hm, name)(obs_g, sim_g, nan_policy="omit", **extra)
    expected = getattr(hm, name)(obs_g[keep], sim_g[keep], **_filter(extra, keep))
    assert same(values(got), values(expected))


# ---- ensembles (#4) ----

def _crps_row(o, members):
    x = np.asarray(members, dtype=float)
    x = x[~np.isnan(x)]
    m = x.size
    return np.abs(x - o).mean() - 0.5 * np.abs(x[:, None] - x[None, :]).sum() / (m * m)


@pytest.mark.parametrize("backend", BACKENDS)
def test_ensemble_omit_drops_rows_with_nan_obs_and_members_with_nan(backend):
    rng = np.random.default_rng(4)
    obs = 20 + rng.gamma(2.0, 4.0, 60)
    ens = obs[:, None] + rng.normal(0, 3, (60, 6))
    obs_g, ens_g = obs.copy(), ens.copy()
    obs_g[5] = np.nan
    ens_g[9, 2] = np.nan
    ens_g[12, :] = np.nan
    rows = [i for i in range(60) if i not in (5, 12)]
    expected = np.mean([_crps_row(obs_g[i], ens_g[i]) for i in rows])
    got = hm.crps(wrap(backend, obs_g), wrap(backend, ens_g) if backend != "xarray" else __import__("xarray").DataArray(ens_g, dims=["time", "member"]), nan_policy="omit")
    assert float(got) == pytest.approx(expected, rel=1e-12)
    assert got.nan_info["n_nan_removed"] == 2


def test_ensemble_propagate_and_raise():
    rng = np.random.default_rng(4)
    obs = 20 + rng.gamma(2.0, 4.0, 40)
    ens = obs[:, None] + rng.normal(0, 3, (40, 5))
    ens[3, 1] = np.nan
    assert np.isnan(float(hm.crps(obs, ens, nan_policy="propagate")))
    with pytest.raises(ValueError, match="NaN"):
        hm.crps(obs, ens, nan_policy="raise")
