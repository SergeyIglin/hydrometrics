"""forecast_verification and forecast_verification_delta (items #20, #33; D1, D5)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm
from hydrometrics.backends import numpy as np_backend

COEFF = 0.674  # probable deviation of the normal law, 0.6745 sigma; the source gives 0,674


def _series():
    rng = np.random.default_rng(21)
    obs = 30 + rng.gamma(2.0, 8.0, 500)
    sim = obs + rng.normal(0, 6, 500)
    return obs, sim


def test_coefficient_is_a_single_named_constant():
    assert np_backend.PROBABLE_ERROR_COEFFICIENT == COEFF
    source = (np_backend.__file__)
    text = open(source, encoding="utf-8").read()
    assert "0.647" not in text


def test_verified_means_error_below_0674_sigma():
    obs, sim = _series()
    sigma = obs.std(ddof=1)
    expected = (np.abs(obs - sim) < COEFF * sigma).astype(float)
    got = hm.forecast_verification(obs, sim, reduction="none").value
    assert np.array_equal(got, expected)
    assert float(hm.forecast_verification(obs, sim)) == pytest.approx(expected.mean())


def test_error_between_0647_and_0674_sigma_is_now_verified():
    obs = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    sigma = obs.std(ddof=1)
    sim = obs.copy()
    sim[0] += 0.66 * sigma
    got = hm.forecast_verification(obs, sim, reduction="none").value
    assert got[0] == 1


def test_delta_version_uses_group_error_spread():
    obs, sim = _series()
    ref_date = np.arange(obs.size) % 25
    expected = np.empty(obs.size)
    for g in np.unique(ref_date):
        m = ref_date == g
        sigma_delta = (sim[m] - obs[m]).std(ddof=1)
        expected[m] = np.abs(obs[m] - sim[m]) < COEFF * sigma_delta
    got = hm.forecast_verification_delta(obs, sim, ref_date=ref_date, reduction="none").value
    assert np.array_equal(got, expected)


# ---- #20: NaN is not "not verified" ----

def test_nan_error_gives_nan_not_zero():
    obs, sim = _series()
    obs[7] = np.nan
    got = hm.forecast_verification(obs, sim, reduction="none").value
    assert np.isnan(got[7])
    assert np.isin(np.delete(got, 7), (0.0, 1.0)).all()


def test_nan_in_sim_gives_nan_for_that_element_only():
    obs, sim = _series()
    sim[3] = np.nan
    got = hm.forecast_verification(obs, sim, reduction="none").value
    assert np.isnan(got[3]) and np.isfinite(np.delete(got, 3)).all()


def test_all_nan_is_nan():
    sim = np.arange(6.0)
    got = hm.forecast_verification(np.full(6, np.nan), sim, reduction="none").value
    assert np.isnan(got).all()
    assert np.isnan(float(hm.forecast_verification(np.full(6, np.nan), sim)))


def test_delta_nan_error_and_small_groups_give_nan():
    obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
    sim = obs + np.array([0.5, -0.4, np.nan, 0.2, 0.1, -0.3, 0.6])
    ref_date = np.array([1, 1, 1, 2, 2, 2, 3])  # group 3 has a single value: no spread
    got = hm.forecast_verification_delta(obs, sim, ref_date=ref_date, reduction="none").value
    assert np.isnan(got[2])  # NaN error
    assert np.isnan(got[6])  # group with fewer than two errors
    assert np.isfinite(got[[0, 1, 3, 4, 5]]).all()


def test_docstrings_describe_the_actual_computation():
    for name in ("forecast_verification", "forecast_verification_delta"):
        doc = getattr(hm, name).__doc__
        assert "0.674" in doc and "0.647" not in doc, name
    assert "sigma_delta" in hm.forecast_verification_delta.__doc__
    for name in ("forecast_verification", "forecast_verification_delta", "ssigma_delta"):
        assert ".. warning::" not in getattr(hm, name).__doc__, name
