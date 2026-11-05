"""Docstrings and metadata describe the actual computation (items #35, #37, #38, #42-#45; D2, D4)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm


def test_pbias_sign_is_positive_for_overestimation_and_documented():
    obs = np.array([10.0, 20.0, 30.0])
    assert float(hm.pbias(obs, obs * 1.1)) == pytest.approx(10.0)
    doc = hm.pbias.__doc__
    assert "overestimation" in doc and "Moriasi" in doc and "opposite" in doc


def test_nse_bounded_form_is_nse_over_two_minus_nse_and_documented():
    rng = np.random.default_rng(1)
    obs = 10 + rng.gamma(2.0, 4.0, 200)
    sim = obs + rng.normal(0, 5, 200)
    nse = 1 - np.sum((obs - sim) ** 2) / np.sum((obs - obs.mean()) ** 2)
    assert float(hm.nse_bounded(obs, sim)) == pytest.approx(nse / (2 - nse), rel=1e-12)
    doc = hm.nse_bounded.__doc__
    assert "NSE / (2 - NSE)" in doc and "1 / (2 - NSE)" in doc
    assert "UNVERIFIED_REFS" not in doc and "No primary source" in doc


def test_nse_bounded_has_no_primary_source_in_metadata():
    assert "Legates" not in hm.nse_bounded.reference and "Legates" not in hm.nse_bounded.__doc__


def test_sharpness_is_not_called_a_component_of_the_brier_decomposition():
    doc = hm.sharpness.__doc__
    assert "variance" in doc.lower() and "reliability, resolution and uncertainty" in doc
    assert "component of Brier Score decomposition" not in doc
    assert "component of Brier Score decomposition" not in hm.sharpness.description


def test_reliability_docstring_describes_binning():
    doc = hm.reliability.__doc__
    assert "equal-width" in doc and "closed on the right" in doc


def test_weighted_crps_metadata_describes_observation_weighting():
    assert "observations" in hm.weighted_crps.description
    assert "int" not in hm.weighted_crps.formula  # no integral: the implementation is a weighted mean


def test_willmott_docstring_states_the_1981_form():
    doc = hm.willmott_d.__doc__
    assert "1981" in doc and "not implemented" in doc


def test_crpss_docstring_names_the_default_reference():
    assert "mean of the observations" in hm.crpss.__doc__
