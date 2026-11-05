"""Boundary cases and degenerate inputs (report items #12, #19-#25, #47)."""

from __future__ import annotations

import warnings

import numpy as np
import pytest

import hydrometrics as hm


# ---- #12 reliability: p == 1.0 belongs to the last, right-closed bin ----

def reliability_ref(obs, prob, n_bins=10):
    """sum_k n_k/n (mean p_k - mean o_k)^2 with bins [a, b) and a closed last bin."""
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    total = 0.0
    for k in range(n_bins):
        upper = prob <= edges[k + 1] if k == n_bins - 1 else prob < edges[k + 1]
        mask = (prob >= edges[k]) & upper
        if mask.any():
            total += mask.sum() * (prob[mask].mean() - obs[mask].mean()) ** 2
    return total / prob.size


def test_reliability_probability_one_with_no_event():
    obs = np.zeros(4)
    prob = np.ones(4)
    assert float(hm.reliability(obs, prob)) == pytest.approx(1.0)
    assert float(hm.reliability(obs, prob)) == pytest.approx(float(hm.brier_score(obs, prob)))


def test_reliability_perfect_forecast_with_extremes_is_zero():
    obs = np.array([1.0, 1.0, 0.0, 0.0])
    assert float(hm.reliability(obs, obs.copy())) == pytest.approx(0.0)


def test_reliability_matches_reference_including_ones():
    rng = np.random.default_rng(8)
    prob = np.round(rng.uniform(0, 1, 300), 1)  # many values exactly 0.0 and 1.0
    obs = (rng.uniform(0, 1, 300) < prob).astype(float)
    assert (prob == 1.0).sum() > 0
    assert float(hm.reliability(obs, prob)) == pytest.approx(reliability_ref(obs, prob), rel=1e-12)


@pytest.mark.parametrize("n_bins", [4, 10])
def test_reliability_counts_every_forecast(n_bins):
    prob = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    obs = np.array([1.0, 0.0, 1.0, 0.0, 0.0])
    assert float(hm.reliability(obs, prob, n_bins=n_bins)) == pytest.approx(reliability_ref(obs, prob, n_bins), rel=1e-12)


# ---- #23 r2 without data ----

@pytest.mark.parametrize("kind", ["empty", "all_nan"])
def test_r2_without_data_is_nan(kind):
    obs = np.array([]) if kind == "empty" else np.full(6, np.nan)
    sim = np.array([]) if kind == "empty" else np.arange(6.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        assert np.isnan(float(hm.r2(obs, sim)))


def test_r2_constant_observations_keep_documented_branches():
    obs = np.full(5, 3.0)
    assert float(hm.r2(obs, obs.copy())) == 1.0
    assert np.isnan(float(hm.r2(obs, obs + 1.0)))


# ---- #21 zero variance "up to rounding" ----

def _sim(n=1096, seed=2):
    return np.random.default_rng(seed).gamma(2.0, 8.0, n) + 1.0


@pytest.mark.parametrize("c", [20.0, 24.6, 0.1, 1e3, 7.3])
@pytest.mark.parametrize("name", ["nse", "log_nse", "nse_bounded", "modified_nse", "r2", "ssigma"])
def test_constant_observations_give_nan_not_huge_numbers(name, c):
    """Rounding of the mean made the variance ~1e-30 instead of 0: log_nse gave -3.3e+29."""
    obs = np.full(1096, c)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        assert np.isnan(float(getattr(hm, name)(obs, _sim())))


def test_variance_weighted_nse_skips_constant_gauge():
    rng = np.random.default_rng(4)
    obs_a = 20 + rng.gamma(2.0, 5.0, 400)
    sim_a = obs_a * 0.9 + rng.normal(0, 2, 400)
    obs = np.concatenate([obs_a, np.full(400, 24.6)])
    sim = np.concatenate([sim_a, rng.normal(25, 3, 400)])
    gauge = np.repeat([0, 1], 400)
    got = float(hm.nse_variance_weighted(obs, sim, gauge=gauge))
    expected = 1 - np.sum((obs_a - sim_a) ** 2) / np.sum((obs_a - obs_a.mean()) ** 2)
    assert got == pytest.approx(expected, rel=1e-12)


def test_tiny_but_real_variance_is_kept():
    rng = np.random.default_rng(9)
    obs = 1000.0 + 1e-6 * rng.normal(size=500)  # coefficient of variation 1e-9
    sim = obs + 1e-7 * rng.normal(size=500)
    expected = 1 - np.sum((obs - sim) ** 2) / np.sum((obs - obs.mean()) ** 2)
    assert float(hm.nse(obs, sim)) == pytest.approx(expected, rel=1e-6)


# ---- #22 accuracy ----

def test_accuracy_leaves_out_pairs_with_nan():
    obs = np.array([1.0, np.nan, 0.0, 1.0])
    sim = np.array([1.0, 1.0, 0.0, 0.0])
    assert float(hm.accuracy(obs, sim)) == pytest.approx(2 / 3)


def test_accuracy_all_nan_is_nan():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        assert np.isnan(float(hm.accuracy(np.full(4, np.nan), np.array([1.0, 0, 1, 0]))))


# ---- #25 EDI and SEDI at degenerate rates ----

def _rates(hit, miss, fa, cn):
    obs = np.r_[np.ones(hit + miss), np.zeros(fa + cn)]
    sim = np.r_[np.ones(hit), np.zeros(miss), np.ones(fa), np.zeros(cn)]
    return obs, sim


def edi_ref(h, f):
    return (np.log(f) - np.log(h)) / (np.log(f) + np.log(h))


def sedi_ref(h, f):
    return (np.log(f) - np.log(h) - np.log(1 - f) + np.log(1 - h)) / (
        np.log(f) + np.log(h) + np.log(1 - f) + np.log(1 - h))


def test_edi_sedi_match_formulas_for_regular_rates():
    obs, sim = _rates(hit=30, miss=20, fa=40, cn=410)
    h, f = 30 / 50, 40 / 450
    assert float(hm.edi(obs, sim)) == pytest.approx(edi_ref(h, f), rel=1e-12)
    assert float(hm.sedi(obs, sim)) == pytest.approx(sedi_ref(h, f), rel=1e-12)


@pytest.mark.parametrize("counts, edi_expected, sedi_expected", [
    ((50, 0, 0, 450), 1.0, 1.0),         # H = 1, F = 0 (obs == sim) is defined as 1
    ((0, 50, 10, 440), np.nan, np.nan),  # H = 0
    ((30, 20, 0, 450), np.nan, np.nan),  # F = 0, H < 1
    ((50, 0, 40, 410), 1.0, np.nan),     # H = 1, F > 0: log H = 0 makes EDI exactly 1
])
def test_edi_sedi_degenerate_rates_are_handled_without_warnings(counts, edi_expected, sedi_expected):
    obs, sim = _rates(*counts)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        edi, sedi = float(hm.edi(obs, sim)), float(hm.sedi(obs, sim))
    for got, expected in ((edi, edi_expected), (sedi, sedi_expected)):
        assert (np.isnan(got) and np.isnan(expected)) or got == pytest.approx(expected)


def test_edi_docstring_states_degenerate_rates():
    for name in ("edi", "sedi"):
        doc = getattr(hm, name).__doc__
        assert "NaN" in doc and "H" in doc and "1" in doc


# ---- #47 log_nse with non-positive values ----

def logreference(obs, sim, eps=1e-10):
    keep = (obs + eps > 0) & (sim + eps > 0)
    lo, ls = np.log(obs[keep] + eps), np.log(sim[keep] + eps)
    return 1 - np.sum((lo - ls) ** 2) / np.sum((lo - lo.mean()) ** 2)


def test_log_nse_report_example_is_preserved_without_warning():
    obs = np.array([-1.0, 1.0, 2.0, 3.0])
    sim = np.array([1.0, 1.0, 2.0, 3.0])
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert float(hm.log_nse(obs, sim)) == 1.0


def test_log_nse_masks_non_positive_pairs():
    rng = np.random.default_rng(14)
    obs = rng.gamma(2.0, 5.0, 300)
    sim = obs * rng.uniform(0.7, 1.3, 300)
    obs[[3, 50]] = [-2.0, -1e-3]
    sim[[10, 80]] = [-5.0, -1.0]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        got = float(hm.log_nse(obs, sim))
    assert got == pytest.approx(logreference(obs, sim), rel=1e-12)


def test_log_nse_keeps_zeros_through_eps():
    obs = np.array([0.0, 1.0, 2.0, 3.0, 5.0])
    sim = np.array([0.5, 1.2, 1.8, 3.3, 4.0])
    assert float(hm.log_nse(obs, sim)) == pytest.approx(logreference(obs, sim), rel=1e-12)
