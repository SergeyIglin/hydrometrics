"""Dispatcher, registry, a user-defined metric and the validation helpers (report 5.6)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm
from hydrometrics.core import validation as v
from hydrometrics.core.base import MetricFunction, metric
from hydrometrics.core.dispatch import BackendRegistry, get_backend_type

# These tests need all three optional backends; without them the module is skipped.
pd = pytest.importorskip("pandas")
pl = pytest.importorskip("polars")
xr = pytest.importorskip("xarray")


def test_backend_type_is_detected_from_the_input():
    assert get_backend_type(np.ones(2)) == "numpy"
    assert get_backend_type([1.0]) == "numpy"
    assert get_backend_type(pd.Series([1.0])) == "pandas"
    assert get_backend_type(pd.DataFrame({"a": [1.0]})) == "pandas"
    assert get_backend_type(pl.Series([1.0])) == "polars"
    assert get_backend_type(xr.DataArray([1.0])) == "xarray"


def _own_metric():
    @metric(name="Mean ratio", direction="target", bounds=(0.0, None), reference="own", optimum=1.0)
    def mean_ratio(obs, sim, *, weight=None, axis=None, reduction="mean", floor=0.0):
        """Ratio of means.

        Parameters
        ----------
        obs : array-like
            Observed.
        sim : array-like
            Simulated.
        floor : float, default=0.0
            Values below it are ignored.

        Returns
        -------
        float
            Ratio.
        """
        return np.nanmean(sim, axis=axis) / np.nanmean(obs, axis=axis)
    return mean_ratio


def test_a_user_metric_gets_the_unified_call_and_documentation():
    mean_ratio = _own_metric()
    assert isinstance(mean_ratio, MetricFunction)
    obs, sim = np.array([1.0, 2.0, np.nan, 4.0]), np.array([2.0, 4.0, 5.0, 8.0])
    result = mean_ratio(obs, sim)
    assert float(result) == pytest.approx(2.0)          # the NaN pair is dropped (omit is the default)
    assert result.direction == "target" and result.optimum == 1.0
    with pytest.raises(ValueError, match="NaN"):
        mean_ratio(obs, sim, nan_policy="raise")
    assert "\nnan_policy :" in mean_ratio.__doc__ and "floor" in str(mean_ratio.__signature__)


def test_registry_falls_back_to_numpy_when_a_backend_has_no_implementation():
    registry = BackendRegistry()
    registry.register_numpy("mean_ratio", _own_metric())
    dispatch = registry.get_dispatcher("mean_ratio")
    obs, sim = np.array([1.0, 2.0, 4.0]), np.array([2.0, 4.0, 8.0])
    for wrapped in (pd.Series(obs), pl.Series(obs), xr.DataArray(obs)):
        assert float(dispatch(wrapped, sim)) == pytest.approx(2.0)
    assert dispatch.__name__ == "mean_ratio" and dispatch.optimum == 1.0


def test_registry_routes_to_the_backend_function_when_it_exists():
    registry = BackendRegistry()
    calls = []
    registry.register_numpy("m", lambda o, s: calls.append("numpy"))
    registry.register_pandas("m", lambda o, s: calls.append("pandas"))
    registry.register_polars("m", lambda o, s: calls.append("polars"))
    registry.register_xarray("m", lambda o, s: calls.append("xarray"))
    dispatch = registry.get_dispatcher("m")
    dispatch(np.ones(1), np.ones(1))
    dispatch(pd.Series([1.0]), np.ones(1))
    dispatch(pl.Series([1.0]), np.ones(1))
    dispatch(xr.DataArray([1.0]), pd.Series([1.0]))
    assert calls == ["numpy", "pandas", "polars", "xarray"]


# ---- validation helpers ----

def test_check_finite_arrays_reports_nan_and_inf():
    v.check_finite_arrays(np.ones(3))
    with pytest.raises(ValueError, match="q_obs contains non-finite values: 1 NaN, 1 Inf"):
        v.check_finite_arrays(np.array([1.0, np.nan, np.inf]), names=["q_obs"])


def test_check_same_shape_and_non_empty_and_min_samples():
    v.check_same_shape(np.ones(3), np.zeros(3))
    with pytest.raises(ValueError, match="Shape mismatch"):
        v.check_same_shape(np.ones(3), np.ones(4), names=["a", "b"])
    v.check_non_empty(np.ones(1))
    with pytest.raises(ValueError, match="empty"):
        v.check_non_empty(np.array([]), "series")
    v.check_min_samples(np.array([1.0, np.nan, 3.0]), 2)
    with pytest.raises(ValueError, match="1 valid samples"):
        v.check_min_samples(np.array([1.0, np.nan]), 2)


def test_apply_nan_policy_axis_follows_the_policy():
    obs = np.array([[1.0, np.nan], [2.0, 3.0]])
    sim = np.ones((2, 2))
    assert v.apply_nan_policy_axis(obs, sim, None, None, "raise")[3]["n_nan_removed"] == 0   # no axis: handled elsewhere
    assert v.apply_nan_policy_axis(obs, sim, None, 0, "propagate")[3]["n_nan_removed"] == 1
    assert v.apply_nan_policy_axis(obs, sim, None, 0, "omit")[3]["n_nan_removed"] == 1
    with pytest.raises(ValueError, match="NaN"):
        v.apply_nan_policy_axis(obs, sim, None, 0, "raise")
    clean = v.apply_nan_policy_axis(np.ones((2, 2)), sim, np.ones((2, 2)), 0, "omit")
    assert clean[3]["n_nan_removed"] == 0


def test_public_names_are_the_documented_ones():
    assert hm.validate_inputs is v.validate_inputs
    assert set(hm.__all__) >= {"MetricResult", "NanPolicy", "Reduction", "GroupedResult", "compute_grouped"}
