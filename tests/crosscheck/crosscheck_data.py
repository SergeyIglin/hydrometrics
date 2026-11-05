"""Shared data and helpers of the cross-check suite (``tests/crosscheck``).

The series imitates the documentation examples: a daily hydrograph for the water
years 2010-10-01 .. 2013-09-30 with a spring flood and low flow, gamma noise on the
observations, a simulation that is lagged, biased, noisy and clipped.

Every cross-check module calls ``pytest.importorskip("<package>")`` BEFORE importing
this module, so that the ordinary test run without the ``crosscheck`` extra skips them.
The module itself needs only numpy and the library.
"""
from __future__ import annotations

import numpy as np

SEED = 20240607
N_ENS = 20

#: variant name -> (two_d, with_nan, weighted)
VARIANTS = {
    "clean": (False, False, False),
    "nan": (False, True, False),
    "weighted": (False, False, True),
    "weighted_nan": (False, True, True),
    "2d": (True, False, False),
    "2d_nan": (True, True, False),
    "2d_weighted_nan": (True, True, True),
}
UNWEIGHTED = [k for k, v in VARIANTS.items() if not v[2]]
ALL = list(VARIANTS)


def daily(seed: int = SEED, scale: float = 1.0, lag: int = 3):
    """One daily series: ``(dates, q_obs, q_sim)``."""
    rng = np.random.default_rng(seed)
    dates = np.arange("2010-10-01", "2013-10-01", dtype="datetime64[D]")
    doy = (dates - dates.astype("datetime64[Y]")).astype(int) + 1
    flood = 240.0 * np.exp(-(((doy - 118) / 16.0) ** 2))
    q_obs = scale * (12.0 + flood + rng.gamma(2.0, 1.5, dates.size))
    lagged = np.concatenate([np.full(lag, q_obs[0]), q_obs[:-lag]])
    q_sim = 0.92 * lagged + 1.5 * scale + rng.normal(0.0, 3.0 * scale, dates.size)
    q_sim = np.clip(q_sim, 2.0 * scale, 200.0 * scale)
    return dates, q_obs, q_sim


def daily_2d(seed: int = SEED):
    """Three gauges (columns) with different scale: ``(q_obs, q_sim)``, shape (n, 3)."""
    obs, sim = [], []
    for j, scale in enumerate((1.0, 2.0, 0.5)):
        _, o, s = daily(seed + j, scale=scale, lag=2 + j)
        obs.append(o)
        sim.append(s)
    return np.column_stack(obs), np.column_stack(sim)


def inject_nan(obs, sim, seed: int = SEED + 100):
    """NaN in ``obs`` and in ``sim`` at different positions (about 3 % each)."""
    rng = np.random.default_rng(seed)
    obs, sim = obs.copy(), sim.copy()
    k = obs.size // 30
    obs.flat[rng.choice(obs.size, k, replace=False)] = np.nan
    sim.flat[rng.choice(sim.size, k, replace=False)] = np.nan
    return obs, sim


def get_variant(name: str):
    """``(obs, sim, weight_or_None)`` of a variant from :data:`VARIANTS`."""
    two_d, with_nan, weighted = VARIANTS[name]
    if two_d:
        obs, sim = daily_2d()
    else:
        _, obs, sim = daily()
    if with_nan:
        obs, sim = inject_nan(obs, sim)
    w = None
    if weighted:
        w = np.random.default_rng(SEED + 200).uniform(0.5, 2.0, obs.shape)
    return obs, sim, w


def columns(*arrays):
    """Yield, per column, the arrays without the pairs that contain a NaN.

    ``None`` entries stay ``None``. A 1-D input is one column.
    """
    arrs = [None if a is None else (a[:, None] if a.ndim == 1 else a) for a in arrays]
    first = next(a for a in arrs if a is not None)
    for j in range(first.shape[1]):
        cols = [None if a is None else a[:, j] for a in arrs]
        valid = np.ones(first.shape[0], dtype=bool)
        for c in cols:
            if c is not None:
                valid &= ~np.isnan(c)
        yield tuple(None if c is None else c[valid] for c in cols)


def get_events(name: str, quantile: float = 0.9):
    """Binary event data of a variant: ``(event_obs, event_sim, prob, weight)``.

    The event is "discharge above the ``quantile`` of the observations" (per column).
    ``event_*`` hold 0.0 / 1.0 (NaN where the discharge is NaN); ``prob`` is the share of
    ``N_ENS`` ensemble members above the threshold (many ties, values k / 20).
    """
    obs, sim, w = get_variant(name)
    thr = np.nanquantile(obs, quantile, axis=0)
    eo = np.where(np.isnan(obs), np.nan, (obs > thr).astype(float))
    es = np.where(np.isnan(sim), np.nan, (sim > thr).astype(float))
    rng = np.random.default_rng(SEED + 300)
    base = np.where(np.isnan(sim), 0.0, sim)[..., None]
    members = base + rng.normal(0.0, 1.0, base.shape[:-1] + (N_ENS,)) * (2.0 + 0.2 * base)
    p = (members > np.asarray(thr)[..., None]).mean(axis=-1)
    p = np.where(np.isnan(sim), np.nan, p)
    return eo, es, p, w


def get_ensemble(name: str):
    """Ensemble data of a variant: ``(obs, members, weight)``.

    ``members`` has the shape ``obs.shape + (N_ENS,)``. In the NaN variants some
    observations are NaN and some members are NaN (a few per cent).
    """
    two_d, with_nan, _ = VARIANTS[name]
    obs, sim, w = get_variant(name)
    base = np.where(np.isnan(sim), np.nanmean(sim), sim)[..., None]
    rng = np.random.default_rng(SEED + 400)
    members = base + rng.normal(0.0, 1.0, base.shape[:-1] + (N_ENS,)) * (2.0 + 0.2 * base)
    members = np.clip(members, 0.0, None)
    if with_nan:
        members.flat[rng.choice(members.size, members.size // 40, replace=False)] = np.nan
    return obs, members, w


def lib_value(name: str, obs, sim, weight=None, **kwargs):
    """Value of the library metric ``name`` as a 1-D float array (one per column)."""
    import hydrometrics as hm

    call = dict(kwargs)
    if weight is not None:
        call["weight"] = weight
    if obs.ndim == 2:
        call["axis"] = 0
    result = getattr(hm, name)(obs, sim, **call)
    return np.atleast_1d(np.asarray(result.value, dtype=float))


RTOL = 1e-9
ATOL = 1e-12
