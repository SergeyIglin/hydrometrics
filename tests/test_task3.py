"""Decisions of task_3: ssigma along an axis, public helper functions, documented registry."""

from __future__ import annotations

import inspect

import numpy as np
import pytest

import hydrometrics as hm
from hydrometrics.core.dispatch import BackendRegistry
from _cases import BACKENDS, case_2d, wrap


def _ssigma_ref(o, s, m=2):
    return np.sqrt(np.sum((o - s) ** 2) / (len(o) - m)) / o.std(ddof=1)


# ---- ssigma with an axis ----

@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("axis", [0, 1])
def test_ssigma_axis_matches_the_formula_for_every_slice(axis, backend):
    obs, sim = case_2d("ssigma")
    where = {"dim": ["time", "station"][axis]} if backend == "xarray" else {"axis": axis}
    got = np.asarray(hm.ssigma(wrap(backend, obs), wrap(backend, sim), **where).value, dtype=float)
    if axis == 0:
        expected = [_ssigma_ref(obs[:, j], sim[:, j]) for j in range(obs.shape[1])]
    else:
        expected = [_ssigma_ref(obs[i], sim[i]) for i in range(obs.shape[0])]
    assert got.shape == (len(expected),)
    assert np.allclose(got, expected, rtol=1e-12)


def test_ssigma_axis_with_the_m_parameter_and_mean_reduction():
    obs, sim = case_2d("ssigma", n=40, g=4)
    per = hm.ssigma(obs, sim, m=3, axis=0).value
    assert np.allclose(per, [_ssigma_ref(obs[:, j], sim[:, j], m=3) for j in range(4)])
    assert float(hm.ssigma(obs, sim, m=3, axis=0, reduction="mean")) == pytest.approx(per.mean())


def test_ssigma_slice_with_too_few_values_is_nan_not_an_error():
    obs, sim = case_2d("ssigma", n=30, g=3)
    obs, sim = obs.copy(), sim.copy()
    obs[2:, 1] = np.nan   # two valid values left in column 1, m = 2
    got = hm.ssigma(obs, sim, axis=0).value
    assert np.isnan(got[1]) and np.isfinite(got[[0, 2]]).all()


def test_ssigma_without_axis_still_requires_more_than_m_values():
    with pytest.raises(ValueError, match="Sample size too small"):
        hm.ssigma(np.array([1.0, 2.0]), np.array([1.5, 2.5]))


def test_ssigma_axis_constant_column_is_nan():
    obs, sim = case_2d("ssigma", n=30, g=3)
    obs = obs.copy()
    obs[:, 2] = 24.6
    assert np.isnan(hm.ssigma(obs, sim, axis=0).value[2])


def test_ssigma_is_flagged_as_supporting_axis_but_not_weights():
    assert hm.ssigma.supports_axis is True and hm.ssigma.supports_weight is False


# ---- public helpers ----

HELPERS = ["registry", "mean_annual_hydrograph", "mean_annual_hydrograph_duration_curve"]


@pytest.mark.parametrize("name", HELPERS)
def test_helper_is_exported(name):
    assert name in hm.__all__ and hasattr(hm, name)


def test_exports_are_unique():
    assert len(hm.__all__) == len(set(hm.__all__))


def test_registry_is_a_documented_backend_registry():
    assert isinstance(hm.registry, BackendRegistry)
    assert BackendRegistry.__doc__ and "metric" in BackendRegistry.__doc__.lower()
    for method in ("register_numpy", "register_pandas", "register_xarray", "register_polars", "get_dispatcher"):
        assert getattr(BackendRegistry, method).__doc__, method
    assert hm.registry.get_dispatcher("nse") is not None


@pytest.mark.parametrize("name", HELPERS[1:])
def test_helper_functions_are_documented_with_parameters_and_returns(name):
    doc = inspect.getdoc(getattr(hm, name))
    assert "Parameters" in doc and "Returns" in doc and "obs :" in doc and "date :" in doc


def test_helper_functions_work_through_the_public_names():
    dates = np.arange("2011-01-01", "2013-01-01", dtype="datetime64[D]")   # 2012 is a leap year
    q = np.arange(dates.size, dtype=float)
    assert hm.mean_annual_hydrograph(q, dates).shape == (366,)
    curve = hm.mean_annual_hydrograph_duration_curve(q, dates)
    assert curve.shape == (365,) and np.all(np.diff(curve) <= 0)
