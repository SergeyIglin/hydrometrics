"""regNSE with gaps (item #19)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm


def _case():
    rng = np.random.default_rng(31)
    dates = np.datetime64("2004-01-01") + np.arange(3 * 365 + 1).astype("timedelta64[D]")
    doy = (dates - dates.astype("datetime64[Y]")).astype(int)
    obs = 10 + 90 * np.exp(-(((doy - 115) / 20.0) ** 2)) + rng.gamma(2.0, 1.5, dates.size)
    sim = 0.9 * obs + 2 + rng.normal(0, 3, dates.size)
    return obs, sim, dates


def test_regnse_perfect_simulation_is_one():
    obs, _, dates = _case()
    assert float(hm.regNSE(obs, obs.copy(), dates=dates)) == pytest.approx(1.0)


def test_nan_only_in_sim_does_not_break_and_equals_pairwise_removal():
    """Used to fail with 'could not broadcast input array from shape (336,) into shape (364,)'."""
    obs, sim, dates = _case()
    sim_gap = sim.copy()
    sim_gap[100:130] = np.nan
    keep = ~np.isnan(sim_gap)
    got = float(hm.regNSE(obs, sim_gap, dates=dates))
    expected = float(hm.regNSE(obs[keep], sim_gap[keep], dates=dates[keep]))
    assert np.isfinite(got)
    assert got == pytest.approx(expected, rel=1e-12)


def test_nan_in_obs_equals_pairwise_removal():
    obs, sim, dates = _case()
    obs_gap = obs.copy()
    obs_gap[400:420] = np.nan
    keep = ~np.isnan(obs_gap)
    got = float(hm.regNSE(obs_gap, sim, dates=dates))
    assert got == pytest.approx(float(hm.regNSE(obs[keep], sim[keep], dates=dates[keep])), rel=1e-12)


def test_gaps_in_both_series_at_different_dates():
    obs, sim, dates = _case()
    obs[50:60] = np.nan
    sim[200:215] = np.nan
    keep = ~(np.isnan(obs) | np.isnan(sim))
    got = float(hm.regNSE(obs, sim, dates=dates))
    assert got == pytest.approx(float(hm.regNSE(obs[keep], sim[keep], dates=dates[keep])), rel=1e-12)


def test_all_nan_gives_nan():
    obs, sim, dates = _case()
    assert np.isnan(float(hm.regNSE(np.full_like(obs, np.nan), sim, dates=dates)))
