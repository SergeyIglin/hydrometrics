"""CRPS family against independent per-observation formulas (items #15-#18, #24, D3)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm


def crps_ref(obs, ens, fair=False):
    """CRPS of each observation: mean|X-o| - 0.5 * sum_jk |X_j-X_k| / (m^2 or m(m-1))."""
    m = ens.shape[-1]
    term_obs = np.abs(ens - obs[..., None]).mean(axis=-1)
    spread = np.abs(ens[..., :, None] - ens[..., None, :]).sum(axis=(-1, -2))
    return term_obs - 0.5 * spread / (m * (m - 1) if fair else m * m)


@pytest.fixture
def case():
    rng = np.random.default_rng(11)
    n, m = 120, 8
    obs = 20 + rng.gamma(2.0, 6.0, n)
    ens = obs[:, None] * 1.05 + rng.normal(0, 4, (n, m))
    weights = rng.uniform(0.5, 3.0, n)
    return obs, ens, weights


def test_default_is_the_classical_estimator(case):
    obs, ens, _ = case
    assert float(hm.crps(obs, ens)) == pytest.approx(crps_ref(obs, ens).mean(), rel=1e-12)


def test_fair_true_uses_m_times_m_minus_one(case):
    obs, ens, _ = case
    assert float(hm.crps(obs, ens, fair=True)) == pytest.approx(crps_ref(obs, ens, fair=True).mean(), rel=1e-12)


def test_fair_is_smaller_than_classical(case):
    obs, ens, _ = case
    assert float(hm.crps(obs, ens, fair=True)) < float(hm.crps(obs, ens, fair=False))


@pytest.mark.parametrize("fair", [False, True])
def test_deterministic_forecast_reduces_to_mae(case, fair):
    obs, ens, _ = case
    sim = ens.mean(axis=1)
    assert float(hm.crps(obs, sim, fair=fair)) == pytest.approx(np.abs(obs - sim).mean(), rel=1e-12)


def test_single_member_ensemble_is_mae(case):
    obs, ens, _ = case
    assert float(hm.crps(obs, ens[:, :1])) == pytest.approx(np.abs(obs - ens[:, 0]).mean(), rel=1e-12)


def test_per_time_values_with_reduction_none(case):
    obs, ens, _ = case
    got = hm.crps(obs, ens, reduction="none").value
    assert got.shape == obs.shape
    assert got == pytest.approx(crps_ref(obs, ens), rel=1e-12)


def test_ensemble_uses_sample_weight(case):
    """#17: weights were ignored for ensembles."""
    obs, ens, w = case
    expected = np.sum(w * crps_ref(obs, ens)) / w.sum()
    assert float(hm.crps(obs, ens, sample_weight=w)) == pytest.approx(expected, rel=1e-12)
    assert expected != pytest.approx(crps_ref(obs, ens).mean(), rel=1e-6)


def test_ensemble_honours_axis(case):
    """#18: axis=0 on (time, gauge) data gives one value per gauge, not per row."""
    rng = np.random.default_rng(5)
    n, g, m = 60, 3, 6
    obs = 10 + rng.gamma(2.0, 3.0, (n, g))
    ens = obs[..., None] + rng.normal(0, 2, (n, g, m))
    got = hm.crps(obs, ens, axis=0, reduction="none").value
    assert got.shape == (g,)
    assert got == pytest.approx(crps_ref(obs, ens).mean(axis=0), rel=1e-12)


def test_ensemble_axis_with_weights(case):
    rng = np.random.default_rng(6)
    n, g, m = 50, 2, 5
    obs = 10 + rng.gamma(2.0, 3.0, (n, g))
    ens = obs[..., None] + rng.normal(0, 2, (n, g, m))
    w = rng.uniform(0.5, 2.0, (n, g))
    got = hm.crps(obs, ens, axis=0, reduction="none", sample_weight=w).value
    expected = (w * crps_ref(obs, ens)).sum(axis=0) / w.sum(axis=0)
    assert got == pytest.approx(expected, rel=1e-12)


# ---- weighted_crps (#16, #17) ----

def test_weighted_crps_deterministic_with_weight_func(case):
    """#16: raised 'cannot broadcast a non-scalar to a scalar array'."""
    obs, ens, _ = case
    sim = ens.mean(axis=1)
    got = float(hm.weighted_crps(obs, sim, weight_func=lambda y: y))
    expected = np.sum(obs * np.abs(obs - sim)) / obs.sum()
    assert got == pytest.approx(expected, rel=1e-12)


def test_weighted_crps_deterministic_with_sample_weight(case):
    obs, ens, w = case
    sim = ens.mean(axis=1)
    expected = np.sum(w * np.abs(obs - sim)) / w.sum()
    assert float(hm.weighted_crps(obs, sim, sample_weight=w)) == pytest.approx(expected, rel=1e-12)


def test_weighted_crps_ensemble_combines_function_and_weights(case):
    obs, ens, w = case
    wf = 1.0 / obs
    expected = np.sum(wf * w * crps_ref(obs, ens)) / np.sum(wf * w)
    got = float(hm.weighted_crps(obs, ens, sample_weight=w, weight_func=lambda y: 1.0 / y))
    assert got == pytest.approx(expected, rel=1e-12)


def test_weighted_crps_without_function_equals_crps(case):
    obs, ens, _ = case
    assert float(hm.weighted_crps(obs, ens)) == pytest.approx(float(hm.crps(obs, ens)), rel=1e-12)


@pytest.mark.parametrize("empty", ["empty", "all_nan"])
def test_weighted_crps_without_data_is_nan(empty):
    """#24: returned 0 for empty and all-NaN input."""
    obs = np.array([]) if empty == "empty" else np.full(5, np.nan)
    sim = np.array([]) if empty == "empty" else np.arange(5.0)
    assert np.isnan(float(hm.weighted_crps(obs, sim)))


# ---- crpss (#15) ----

def test_crpss_with_ensemble_reference_is_ratio_of_means(case):
    """#15: the mean of per-observation ratios was returned (0.3497 instead of 0.5033 in the report)."""
    obs, ens, _ = case
    rng = np.random.default_rng(12)
    ref = obs[:, None] + rng.normal(0, 8, ens.shape)
    c, c_ref = crps_ref(obs, ens), crps_ref(obs, ref)
    expected = 1 - c.mean() / c_ref.mean()
    assert float(hm.crpss(obs, ens, ref_forecast=ref)) == pytest.approx(expected, rel=1e-12)
    assert expected != pytest.approx(np.mean(1 - c / c_ref), rel=1e-3)


def test_crpss_default_reference_is_climatology(case):
    obs, ens, _ = case
    sim = ens.mean(axis=1)
    expected = 1 - np.abs(obs - sim).mean() / np.abs(obs - obs.mean()).mean()
    assert float(hm.crpss(obs, sim)) == pytest.approx(expected, rel=1e-12)


def test_crpss_perfect_forecast_is_one(case):
    obs, _, _ = case
    assert float(hm.crpss(obs, obs)) == pytest.approx(1.0)


def test_crpss_weighted_means(case):
    obs, ens, w = case
    sim = ens.mean(axis=1)
    c = np.abs(obs - sim)
    c_ref = np.abs(obs - np.sum(w * obs) / w.sum())
    expected = 1 - np.sum(w * c) / np.sum(w * c_ref)
    assert float(hm.crpss(obs, sim, sample_weight=w)) == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize("m", [2, 3, 5, 20])
@pytest.mark.parametrize("fair", [False, True])
def test_crps_is_non_negative_for_both_estimators(m, fair):
    """The triangle inequality bounds the spread term, so bounds=(0, None) is true for both."""
    rng = np.random.default_rng(100 + m)
    obs = rng.normal(0, 1, 4000)
    ens = rng.normal(0, 3, (4000, m))
    assert (_per_sample(obs, ens, fair) >= -1e-12).all()


def _per_sample(obs, ens, fair):
    return hm.crps(obs, ens, fair=fair, reduction="none").value


def test_crps_docstring_documents_fair_and_bounds():
    doc = hm.crps.__doc__
    assert "fair" in doc and "m(m - 1)" in doc and "bounds" in doc.lower()
