"""Author decisions of task_4: argument checks, one 366-to-365 rule, weights in reliability, EDI/SEDI limit."""

from __future__ import annotations

import warnings

import numpy as np
import pytest

import hydrometrics as hm

RNG = np.random.default_rng(4)
OBS = 10 + RNG.gamma(2.0, 3.0, 40)
SIM = OBS + RNG.normal(0, 2, 40)
REF = np.arange(40) // 8


# ---- 1. m in ssigma and ssigma_delta: a non-negative number ----

@pytest.mark.parametrize("bad", [-1, -0.5, np.nan, np.inf])
def test_ssigma_rejects_negative_or_non_finite_m(bad):
    with pytest.raises(ValueError, match="m"):
        hm.ssigma(OBS, SIM, m=bad)
    with pytest.raises(ValueError, match="m"):
        hm.ssigma_delta(OBS, SIM, ref_date=REF, m=bad)


def test_ssigma_rejects_non_numbers():
    for bad in ("2", None, [2]):
        with pytest.raises((TypeError, ValueError), match="m"):
            hm.ssigma(OBS, SIM, m=bad)


@pytest.mark.parametrize("good", [0, 1, 2, 1.5, np.int64(3)])
def test_ssigma_accepts_non_negative_numbers(good):
    value = float(hm.ssigma(OBS, SIM, m=good))
    expected = np.sqrt(np.sum((OBS - SIM) ** 2) / (OBS.size - good)) / OBS.std(ddof=1)
    assert value == pytest.approx(expected, rel=1e-12)


def test_ssigma_m_check_applies_on_every_backend():
    pd = pytest.importorskip("pandas")
    with pytest.raises(ValueError):
        hm.ssigma(pd.Series(OBS), pd.Series(SIM), m=-2)


# ---- 2. brier_score and reliability: binary obs, probabilities in [0, 1] ----

PROB = np.round(np.random.default_rng(5).uniform(0, 1, 60), 2)
EVENT = (np.random.default_rng(6).uniform(0, 1, 60) < PROB).astype(float)


@pytest.mark.parametrize("name", ["brier_score", "reliability"])
@pytest.mark.parametrize("bad_obs", [2.0, 0.5, -1.0, np.inf])
def test_obs_must_be_binary(name, bad_obs):
    obs = EVENT.copy()
    obs[3] = bad_obs
    with pytest.raises(ValueError, match="obs"):
        getattr(hm, name)(obs, PROB)


@pytest.mark.parametrize("name", ["brier_score", "reliability"])
@pytest.mark.parametrize("bad_prob", [1.2, -0.1, np.inf])
def test_probability_must_lie_in_unit_interval(name, bad_prob):
    prob = PROB.copy()
    prob[7] = bad_prob
    with pytest.raises(ValueError, match="sim"):
        getattr(hm, name)(EVENT, prob)


@pytest.mark.parametrize("name", ["brier_score", "reliability"])
def test_missing_values_are_not_range_errors(name):
    obs, prob = EVENT.copy(), PROB.copy()
    obs[2], prob[9] = np.nan, np.nan
    assert np.isfinite(float(getattr(hm, name)(obs, prob)))
    assert np.isnan(float(getattr(hm, name)(obs, prob, nan_policy="propagate")))


@pytest.mark.parametrize("name", ["brier_score", "reliability"])
def test_boolean_and_edge_values_are_accepted(name):
    obs = np.array([True, False, True, False])
    prob = np.array([0.0, 1.0, 0.5, 1.0])
    assert np.isfinite(float(getattr(hm, name)(obs, prob)))


def test_range_check_applies_on_other_backends_and_axis():
    pd = pytest.importorskip("pandas")
    with pytest.raises(ValueError):
        hm.brier_score(pd.Series(EVENT), pd.Series(PROB * 2))
    with pytest.raises(ValueError):
        hm.reliability(np.c_[EVENT, EVENT], np.c_[PROB, PROB * 2], axis=0)


# ---- 3. n_bins: an integer not below 1 ----

@pytest.mark.parametrize("bad", [0, -3, 2.5, 10.0, "5", None, True])
def test_n_bins_must_be_an_integer_not_below_one(bad):
    with pytest.raises(ValueError, match="n_bins"):
        hm.reliability(EVENT, PROB, n_bins=bad)


@pytest.mark.parametrize("good", [1, 2, 10, np.int64(4)])
def test_n_bins_accepts_integers(good):
    assert np.isfinite(float(hm.reliability(EVENT, PROB, n_bins=good)))


def test_one_bin_reliability_is_squared_difference_of_means():
    expected = (PROB.mean() - EVENT.mean()) ** 2
    assert float(hm.reliability(EVENT, PROB, n_bins=1)) == pytest.approx(expected, rel=1e-12)


# ---- 4. one rule for 366 days: ranks 365 and 366 are averaged ----

def _leap_series():
    dates = np.arange("2011-01-01", "2013-01-01", dtype="datetime64[D]")  # 2012 is a leap year
    rng = np.random.default_rng(3)
    doy = (dates - dates.astype("datetime64[Y]")).astype(int)
    obs = 15 + 120 * np.exp(-(((doy - 110) / 20.0) ** 2)) + rng.gamma(2.0, 2.0, dates.size)
    return dates, obs


def test_duration_curve_averages_the_last_two_ranks_when_a_leap_year_is_present():
    dates, obs = _leap_series()
    daily = hm.mean_annual_hydrograph(obs, dates)
    assert daily.size == 366
    ranked = np.sort(daily)[::-1]
    expected = np.r_[ranked[:364], 0.5 * (ranked[364] + ranked[365])]
    curve = hm.mean_annual_hydrograph_duration_curve(obs, dates)
    assert curve.shape == (365,)
    np.testing.assert_allclose(curve, expected, rtol=1e-14)


def test_duration_curve_without_leap_year_is_just_sorted():
    dates = np.arange("2013-01-01", "2015-01-01", dtype="datetime64[D]")  # no leap year
    obs = np.random.default_rng(2).gamma(2.0, 5.0, dates.size)
    daily = hm.mean_annual_hydrograph(obs, dates)
    assert daily.size == 365
    np.testing.assert_allclose(hm.mean_annual_hydrograph_duration_curve(obs, dates), np.sort(daily)[::-1])


def test_regnse_uses_the_same_rule_for_the_annual_curves_and_the_regime():
    dates, obs = _leap_series()
    sim = obs * 1.1 + np.random.default_rng(1).normal(0, 1, obs.size)
    years = dates.astype("datetime64[Y]").astype(int) + 1970

    def annual(values):
        rows = []
        for year in np.unique(years):
            ranked = np.sort(values[years == year])[::-1]
            if ranked.size == 366:
                ranked = np.r_[ranked[:364], 0.5 * (ranked[364] + ranked[365])]
            rows.append(ranked)
        return np.array(rows)

    regime = np.sort(hm.mean_annual_hydrograph(obs, dates))[::-1]
    regime = np.r_[regime[:364], 0.5 * (regime[364] + regime[365])]
    o, s = annual(obs), annual(sim)
    expected = 1 - np.sum((s - o) ** 2) / np.sum((o - regime[None, :]) ** 2)
    assert float(hm.regNSE(obs, sim, dates=dates)) == pytest.approx(expected, rel=1e-12)
    assert float(hm.regNSE(obs, sim, dates=dates, regime=regime)) == pytest.approx(expected, rel=1e-12)


# ---- 5. reliability uses the weights in the bin means too ----

def reliability_weighted_ref(obs, prob, w, n_bins=10):
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    total = 0.0
    for k in range(n_bins):
        upper = prob <= edges[k + 1] if k == n_bins - 1 else prob < edges[k + 1]
        mask = (prob >= edges[k]) & upper & (w > 0)
        if mask.any():
            wk = w[mask].sum()
            total += wk * (np.average(prob[mask], weights=w[mask]) - np.average(obs[mask], weights=w[mask])) ** 2
    return total / w.sum()


def test_weights_enter_the_bin_means():
    w = np.random.default_rng(8).uniform(0.2, 3.0, PROB.size)
    got = float(hm.reliability(EVENT, PROB, sample_weight=w))
    assert got == pytest.approx(reliability_weighted_ref(EVENT, PROB, w), rel=1e-12)
    assert got != pytest.approx(float(hm.reliability(EVENT, PROB)), rel=1e-6)


def test_weight_two_equals_repeating_the_pair():
    w = np.ones(PROB.size)
    w[:20] = 2.0
    repeated_obs = np.r_[EVENT[:20], EVENT]
    repeated_prob = np.r_[PROB[:20], PROB]
    assert float(hm.reliability(EVENT, PROB, sample_weight=w)) == pytest.approx(
        float(hm.reliability(repeated_obs, repeated_prob)), rel=1e-12)


def test_zero_weight_equals_dropping_the_pair():
    w = np.ones(PROB.size)
    w[20:30] = 0.0
    keep = w > 0
    assert float(hm.reliability(EVENT, PROB, sample_weight=w)) == pytest.approx(
        float(hm.reliability(EVENT[keep], PROB[keep])), rel=1e-12)


def test_unit_weights_do_not_change_reliability():
    assert float(hm.reliability(EVENT, PROB, sample_weight=np.ones(PROB.size))) == pytest.approx(
        float(hm.reliability(EVENT, PROB)), rel=1e-14)


# ---- 6. EDI and SEDI return 1 for H = 1, F = 0 ----

def _counts(hit, miss, fa, cn):
    obs = np.r_[np.ones(hit + miss), np.zeros(fa + cn)]
    sim = np.r_[np.ones(hit), np.zeros(miss), np.ones(fa), np.zeros(cn)]
    return obs, sim


@pytest.mark.parametrize("name", ["edi", "sedi"])
def test_perfect_forecast_gives_one(name):
    obs, sim = _counts(50, 0, 0, 450)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert float(getattr(hm, name)(obs, sim)) == 1.0


@pytest.mark.parametrize("name", ["edi", "sedi"])
def test_limit_applies_per_slice_along_an_axis(name):
    perfect = _counts(5, 0, 0, 45)
    regular = _counts(3, 2, 4, 41)
    obs = np.c_[perfect[0], regular[0]]
    sim = np.c_[perfect[1], regular[1]]
    got = np.asarray(getattr(hm, name)(obs, sim, axis=0).value)
    assert got[0] == 1.0
    assert got[1] == pytest.approx(float(getattr(hm, name)(*regular)), rel=1e-12)
    assert got[1] < 1.0


def test_other_degenerate_cases_stay_as_before():
    assert np.isnan(float(hm.edi(*_counts(0, 50, 10, 440))))
    assert np.isnan(float(hm.edi(*_counts(30, 20, 0, 450))))
    assert np.isnan(float(hm.sedi(*_counts(30, 20, 0, 450))))
    assert float(hm.edi(*_counts(50, 0, 40, 410))) == 1.0
    assert np.isnan(float(hm.sedi(*_counts(50, 0, 40, 410))))


def test_perfect_event_forecast_without_non_events_is_still_undefined():
    obs = np.ones(5)
    assert np.isnan(float(hm.edi(obs, obs.copy())))
