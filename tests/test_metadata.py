"""Metric metadata, signatures and docstrings (report sections 2.1, 5.4; D14)."""

from __future__ import annotations

import inspect
import re

import numpy as np
import pytest

import hydrometrics as hm
from hydrometrics.backends import numpy as np_backend
from hydrometrics.core.result import MetricResult
from _cases import BACKENDS, NAMES, NO_AXIS, NO_WEIGHT, case_1d, wrap

TARGET = {"bias": 0.0, "pbias": 0.0, "alpha_component": 1.0, "beta_component": 1.0,
          "gamma_component": 1.0, "kge_components": 1.0}
MINIMIZE = {"mae", "mse", "rmse", "nrmse", "rsr", "ssigma", "ssigma_delta", "crps", "weighted_crps",
            "brier_score", "reliability"}
CHANGED_BOUNDS = {
    "beta_component": (None, None),
    "gamma_component": (None, None),
    "kge_components": (None, None),
    "sharpness": (0.0, 0.25),
}


# ---- D14: direction and optimum ----

def test_target_direction_is_accepted_and_serialised():
    result = MetricResult(value=0.1, name="t", direction="target", bounds=(None, None), parameters={},
                          reference="r", nan_info={}, optimum=0.0)
    assert result.direction == "target" and result.optimum == 0.0
    assert result.to_dict()["optimum"] == 0.0


def test_unknown_direction_is_still_rejected():
    with pytest.raises(ValueError, match="direction must be"):
        MetricResult(value=0.1, name="t", direction="best", bounds=(0.0, 1.0), parameters={},
                     reference="r", nan_info={})


def test_optimum_defaults_to_none():
    result = MetricResult(value=0.1, name="t", direction="maximize", bounds=(0.0, 1.0), parameters={},
                          reference="r", nan_info={})
    assert result.optimum is None and result.to_dict()["optimum"] is None


@pytest.mark.parametrize("name", NAMES)
def test_direction_and_optimum_per_metric(name):
    metric = getattr(hm, name)
    if name in TARGET:
        assert metric.direction == "target" and metric.optimum == TARGET[name]
    else:
        assert metric.direction == ("minimize" if name in MINIMIZE else "maximize")
        assert metric.optimum is None


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("name", sorted(TARGET))
def test_result_carries_direction_and_optimum_on_every_backend(name, backend):
    obs, sim, extra = case_1d(name)
    result = getattr(hm, name)(wrap(backend, obs), wrap(backend, sim), **extra)
    assert result.direction == "target" and result.optimum == TARGET[name]


@pytest.mark.parametrize("name, expected", sorted(CHANGED_BOUNDS.items()))
def test_bounds_follow_the_actual_range(name, expected):
    assert getattr(hm, name).bounds == expected


def test_sharpness_never_exceeds_its_upper_bound():
    rng = np.random.default_rng(0)
    p = rng.choice([0.0, 1.0], 1000)
    assert float(hm.sharpness(p, p)) <= 0.25 + 1e-12


# ---- dispatcher signature ----

def test_signature_shows_real_parameters():
    sig = inspect.signature(hm.nse)
    names = list(sig.parameters)
    assert names[:2] == ["obs", "sim"]
    for expected in ("norm", "axis", "nan_policy", "sample_weight", "weight", "reduction"):
        assert expected in sig.parameters
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for n, p in sig.parameters.items() if n not in ("obs", "sim"))
    assert sig.parameters["nan_policy"].default == "omit"
    assert sig.parameters["reduction"].default is None


@pytest.mark.parametrize("name, extra", [("regNSE", ["dates", "regime"]), ("ssigma_delta", ["ref_date", "m"]),
                                         ("nse_variance_weighted", ["gauge"]), ("crps", ["fair"]),
                                         ("nrmse", ["normalization"]), ("log_nse", ["eps"]),
                                         ("alpha_component", ["version"]), ("reliability", ["n_bins"]),
                                         ("precision", ["positive_class"]), ("crpss", ["ref_forecast"]),
                                         ("weighted_crps", ["weight_func"])])
def test_signature_lists_metric_specific_parameters(name, extra):
    params = inspect.signature(getattr(hm, name)).parameters
    for e in extra:
        assert e in params, (name, e)


def test_required_extra_arrays_are_required_keywords():
    params = inspect.signature(hm.regNSE).parameters
    assert params["dates"].default is inspect.Parameter.empty
    assert params["regime"].default is None


# ---- docstrings ----

@pytest.mark.parametrize("name", NAMES)
def test_docstring_has_the_common_parameters_and_raises(name):
    doc = getattr(hm, name).__doc__
    for parameter in ("axis", "nan_policy", "sample_weight", "reduction"):
        assert f"\n{parameter} :" in doc, (name, parameter)
    assert "\nRaises\n------" in doc
    for exception in ("ValueError", "TypeError", "NotImplementedError"):
        assert f"\n{exception}\n" in doc, (name, exception)


def _entry(doc, parameter):
    """Description lines of one parameter of the Parameters section."""
    match = re.search(rf"\n{parameter} :[^\n]*\n((?:    [^\n]*\n)*)", doc)
    return match.group(1)


@pytest.mark.parametrize("name", NAMES)
def test_docstring_states_what_is_not_supported(name):
    doc = getattr(hm, name).__doc__
    assert ("Not supported" in _entry(doc, "sample_weight")) == (name in NO_WEIGHT), name
    assert ("Not supported" in _entry(doc, "axis")) == (name in NO_AXIS), name


@pytest.mark.parametrize("name", NAMES)
def test_docstring_parses_with_napoleon(name):
    napoleon = pytest.importorskip("sphinx.ext.napoleon.docstring")
    lines = napoleon.NumpyDocstring(getattr(hm, name).__doc__).lines()
    text = "\n".join(lines)
    assert ":param nan_policy:" in text and ":param sample_weight:" in text
    assert ":raises ValueError:" in text


# ---- corrected statements (section 5.4) ----

def test_mean_annual_hydrograph_documents_its_real_parameters():
    doc = np_backend.mean_annual_hydrograph.__doc__
    params = doc.split("Parameters")[1].split("Returns")[0]
    assert "obs :" in params and "date :" in params and "discharge :" not in params
    assert params.index("obs :") < params.index("date :")


def test_duration_curve_note_says_rank_positions_not_calendar_days():
    doc = np_backend.mean_annual_hydrograph_duration_curve.__doc__
    assert "29 Feb and 1 Mar positions" not in doc
    assert "rank positions" in doc


def test_regnse_reference_curve_is_described_as_the_mean_hydrograph_duration_curve():
    for doc in (hm.regNSE.__doc__, hm.regNSE.description, np_backend._reg_nse_core.__doc__):
        assert "mean annual hydrograph" in doc, doc[:80]
        assert "averaging observed values at each rank position" not in doc
    assert "mean OBS value for every rank" not in np_backend._reg_nse_core.__doc__


def test_ssigma_delta_docstring_does_not_promise_the_input_shape_for_every_reduction():
    doc = hm.ssigma_delta.__doc__
    assert "the result retains" not in doc
    assert 'reduction="none"' in doc


def test_forecast_verification_return_type_is_documented():
    assert "fraction of verified forecasts" in hm.forecast_verification.__doc__
