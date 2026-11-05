"""validate_inputs, NanPolicy, Reduction, MetricResult, GroupedResult, compute_grouped (report 5.6)."""

from __future__ import annotations

import dataclasses
import json

import numpy as np
import pytest

import hydrometrics as hm
from hydrometrics.core.result import MetricResult
from hydrometrics.core.validation import validate_inputs

# These tests need all three optional backends; without them the module is skipped.
pd = pytest.importorskip("pandas")
pl = pytest.importorskip("polars")
xr = pytest.importorskip("xarray")


# ---------------------------------------------------------------- enums

def test_nan_policy_members_equal_their_strings():
    assert hm.NanPolicy.OMIT == "omit" and hm.NanPolicy("raise") is hm.NanPolicy.RAISE
    assert {p.value for p in hm.NanPolicy} == {"propagate", "omit", "raise"}


def test_reduction_members_equal_their_strings():
    assert hm.Reduction.NONE == "none" and hm.Reduction("sum") is hm.Reduction.SUM
    assert {r.value for r in hm.Reduction} == {"mean", "sum", "none"}


def test_unknown_enum_value_is_rejected():
    with pytest.raises(ValueError):
        hm.NanPolicy("drop")


# ---------------------------------------------------------------- validate_inputs

def test_validate_inputs_returns_arrays_weights_and_info():
    obs, sim, w, info = validate_inputs([1.0, 2.0, 3.0], (1.5, 2.5, 3.5), sample_weight=[1, 2, 3])
    assert isinstance(obs, np.ndarray) and isinstance(sim, np.ndarray) and isinstance(w, np.ndarray)
    assert info == {"policy": "omit", "n_nan_removed": 0, "n_total": 3}


@pytest.mark.parametrize("make", [
    lambda a: pd.Series(a), lambda a: pl.Series("q", a), lambda a: xr.DataArray(a, dims=["t"]),
    lambda a: pd.DataFrame({"a": a}), lambda a: pl.DataFrame({"a": a}),
])
def test_validate_inputs_converts_every_input_type(make):
    a = np.array([1.0, 2.0, 3.0])
    obs, sim, _, _ = validate_inputs(make(a), make(a))
    assert isinstance(obs, np.ndarray) and obs.size == 3 and np.array_equal(obs.ravel(), a)


def test_validate_inputs_omit_sets_nan_in_both_arrays_and_keeps_the_shape():
    obs, sim, w, info = validate_inputs([1.0, np.nan, 3.0, 4.0], [1.0, 2.0, np.nan, 4.0],
                                        sample_weight=[1, 1, 1, np.nan], nan_policy="omit")
    assert np.isnan(obs).tolist() == np.isnan(sim).tolist() == np.isnan(w).tolist() == [False, True, True, True]
    assert info["n_nan_removed"] == 3 and info["n_total"] == 4


def test_validate_inputs_propagate_leaves_data_untouched_but_marks_the_result():
    obs, sim, _, info = validate_inputs([1.0, np.nan], [1.0, 2.0], nan_policy="propagate")
    assert info["n_nan_removed"] == 0 and info["policy"] == "propagate"


def test_validate_inputs_raise_and_unknown_policy():
    with pytest.raises(ValueError, match="NaN"):
        validate_inputs([1.0, np.nan], [1.0, 2.0], nan_policy="raise")
    with pytest.raises(ValueError, match="nan_policy"):
        validate_inputs([1.0], [1.0], nan_policy="drop")


def test_validate_inputs_does_not_modify_the_caller_arrays():
    obs, sim = np.array([1.0, np.nan, 3.0]), np.array([1.0, 2.0, 3.0])
    validate_inputs(obs, sim, nan_policy="omit")
    assert np.isnan(obs[1]) and sim[1] == 2.0


def test_validate_inputs_accepts_ensemble_shapes():
    obs, sim, _, _ = validate_inputs(np.zeros(5), np.zeros((5, 3)))
    assert sim.shape == (5, 3)
    with pytest.raises(ValueError, match="Shape mismatch"):
        validate_inputs(np.zeros(5), np.zeros((4, 3)))


def test_validate_inputs_rejects_bad_weights():
    with pytest.raises(ValueError, match="non-negative"):
        validate_inputs([1.0, 2.0], [1.0, 2.0], sample_weight=[1.0, -1.0])
    with pytest.raises(ValueError, match="Weight shape"):
        validate_inputs([1.0, 2.0], [1.0, 2.0], sample_weight=[1.0])


def test_validate_inputs_rejects_text():
    with pytest.raises(TypeError):
        validate_inputs(np.array(["a", "b"]), np.array(["a", "b"]))


# ---------------------------------------------------------------- MetricResult

def _result(value=0.5, **kw):
    base = dict(value=value, name="Test", direction="maximize", bounds=(0.0, 1.0), parameters={"axis": None},
                reference="ref", nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 1})
    base.update(kw)
    return MetricResult(**base)


def test_metric_result_is_immutable():
    result = _result()
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.value = 1.0
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.name = "other"


def test_metric_result_float_conversion_rules():
    assert float(_result(np.float64(0.25))) == 0.25
    assert float(_result(np.array(0.75))) == 0.75
    with pytest.raises(TypeError):
        float(_result(np.array([1.0, 2.0])))
    with pytest.raises(TypeError):
        float(_result({"r": 1.0}))


def test_metric_result_scalar_properties():
    assert _result(0.5).is_scalar and _result(0.5).scalar_value == 0.5
    assert not _result(np.array([1.0, 2.0])).is_scalar
    with pytest.raises(ValueError, match="not a scalar"):
        _result(np.array([1.0, 2.0])).scalar_value


def test_metric_result_to_dict_has_all_fields_and_lists_arrays():
    d = _result(np.array([1.0, 2.0])).to_dict()
    assert set(d) == {"value", "name", "direction", "bounds", "parameters", "reference", "nan_info",
                      "norm_source", "meta", "optimum"}
    assert d["value"] == [1.0, 2.0]
    json.dumps({k: v for k, v in d.items() if k != "bounds"})  # the rest is plain data


def test_metric_result_text_forms():
    assert "Test: 0.5" in str(_result(0.5))
    assert "MetricResult" in repr(_result(0.5)) and "name='Test'" in repr(_result(0.5))
    assert "array(2,)" in str(_result(np.array([1.0, 2.0])))


def test_metric_result_is_what_every_metric_returns():
    result = hm.nse(np.arange(5.0), np.arange(5.0) + 0.1)
    assert isinstance(result, MetricResult)
    assert result.name == "Nash-Sutcliffe Efficiency" and result.direction == "maximize"
    assert result.parameters["nan_policy"] == "omit" and result.norm_source is None
    assert hm.nse(np.arange(5.0), np.arange(5.0) + 0.1, norm=2.0).norm_source == "user"


# ---------------------------------------------------------------- GroupedResult and compute_grouped

def _frame():
    rng = np.random.default_rng(9)
    n = 120
    index = pd.date_range("2001-03-01", periods=n)
    obs = 20 + rng.gamma(2.0, 6.0, n)
    return pd.DataFrame({"q_obs": obs, "q_sim": obs + rng.normal(0, 3, n), "month": index.month,
                         "station": np.where(np.arange(n) % 2 == 0, "b", "a")})


def test_groups_come_in_order_of_first_appearance_and_values_match_a_manual_split():
    df = _frame()
    result = hm.compute_grouped(hm.rmse, df, "q_obs", "q_sim", group_by="month")
    assert [g[0] for g in result.groups] == [3, 4, 5, 6]  # data start in March: not sorted by name
    for (month,), value in result:
        part = df[df.month == month]
        assert value == pytest.approx(np.sqrt(np.mean((part.q_obs - part.q_sim) ** 2)))


def test_result_fields_and_containers():
    result = hm.compute_grouped(hm.nse, _frame(), "q_obs", "q_sim", group_by="month")
    assert isinstance(result, hm.GroupedResult)
    assert result.name == "Nash-Sutcliffe Efficiency" and result.group_names == ("month",)
    assert len(result) == 4 and result.values.shape == (4,)
    assert all(isinstance(g, tuple) and len(g) == 1 for g in result.groups)
    assert {"direction", "bounds", "reference"} <= set(result.meta)
    assert "n_groups=4" in repr(result)
    assert dict(result.to_dict()) == result.to_dict() and result.to_dict()["group_names"] == ["month"]


def test_two_grouping_columns():
    df = _frame()
    result = hm.compute_grouped(hm.mae, df, "q_obs", "q_sim", group_by=["station", "month"])
    assert result.group_names == ("station", "month")
    assert result.groups[0] == ("b", 3) and len(result) == len(df.groupby(["station", "month"]))


def test_to_pandas_and_to_xarray():
    result = hm.compute_grouped(hm.mae, _frame(), "q_obs", "q_sim", group_by="month")
    frame = result.to_pandas()
    assert list(frame.columns) == ["month", result.name] and len(frame) == 4
    dataset = result.to_xarray()
    assert dict(dataset.sizes) == {"month": 4} and dataset["month"].values.tolist() == [3, 4, 5, 6]


def test_numpy_arrays_with_dict_codes_and_two_dimensional_data():
    rng = np.random.default_rng(1)
    obs = rng.gamma(2.0, 5.0, (60, 3))
    sim = obs + rng.normal(0, 1, (60, 3))
    codes = np.repeat([1, 2, 3], 20)
    result = hm.compute_grouped(hm.mae, None, obs, sim, group_by={"block": codes})
    for (block,), value in result:
        m = codes == block
        assert value == pytest.approx(np.abs(obs[m] - sim[m]).mean())


def test_metric_keywords_are_forwarded_to_the_metric():
    df = _frame()
    result = hm.compute_grouped(hm.nse, df, "q_obs", "q_sim", group_by="month", nan_policy="omit")
    assert result.meta["direction"] == "maximize"
    weighted = hm.compute_grouped(hm.mae, df, "q_obs", "q_sim", group_by="month", sample_weight=None)
    assert len(weighted) == 4


def test_xarray_dataset_names_are_resolved():
    """The names 'q_obs' and 'q_sim' used to become 0-d arrays and fail with IndexError."""
    df = _frame()
    ds = xr.Dataset({"q_obs": ("time", df.q_obs.values), "q_sim": ("time", df.q_sim.values)},
                    coords={"month": ("time", df.month.values)})
    a = hm.compute_grouped(hm.rmse, ds, "q_obs", "q_sim", group_by="month")
    b = hm.compute_grouped(hm.rmse, df, "q_obs", "q_sim", group_by="month")
    assert np.allclose(a.values, b.values)


def test_errors_are_value_key_or_type_errors_not_index_errors():
    df = _frame()
    with pytest.raises(KeyError, match="zzz"):
        hm.compute_grouped(hm.rmse, df, "q_obs", "q_sim", group_by="zzz")
    with pytest.raises(ValueError, match="No grouping"):
        hm.compute_grouped(hm.rmse, df, "q_obs", "q_sim", group_by={})
    with pytest.raises(TypeError, match="dict"):
        hm.compute_grouped(hm.rmse, None, df.q_obs.values, df.q_sim.values, group_by="month")
    with pytest.raises(ValueError, match="rows"):
        hm.compute_grouped(hm.rmse, None, df.q_obs.values, df.q_sim.values, group_by={"m": [1, 2]})
    with pytest.raises(ValueError, match="length"):
        hm.compute_grouped(hm.rmse, None, df.q_obs.values, df.q_sim.values,
                           group_by={"m": df.month.values, "s": df.month.values[:5]})
    with pytest.raises(ValueError, match="rows"):
        hm.compute_grouped(hm.rmse, None, df.q_obs.values[:10], df.q_sim.values[:10], group_by={"m": df.month.values})


def test_a_group_with_one_value_gives_nan_not_an_error():
    result = hm.compute_grouped(hm.nse, None, np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.5]),
                                group_by={"g": [1, 1, 2]})
    assert result.values[0] == 1.0 and np.isnan(result.values[1])


def test_empty_categories_do_not_appear():
    df = _frame().assign(c=lambda d: pd.Categorical(d.month, categories=range(0, 20)))
    assert len(hm.compute_grouped(hm.rmse, df, "q_obs", "q_sim", group_by="c")) == 4


# ---- limits of compute_grouped: loud errors with a way around (task_5, stage D, KNOWN_ISSUES #2-#6) ----

def test_nan_group_key_is_a_value_error_with_a_hint():
    with pytest.raises(ValueError, match="NaN") as info:
        hm.compute_grouped(hm.mae, None, np.arange(4.0), np.arange(4.0) + 1,
                           group_by={"g": np.array([np.nan, np.nan, 1.0, 1.0])})
    assert "dropna" in str(info.value) or "filter" in str(info.value)


@pytest.mark.parametrize("keys", [
    np.array([1.0, np.nan, 1.0, 2.0]),
    np.array(["a", None, "a", "b"], dtype=object),
    np.array(["2020-01-01", "NaT", "2020-01-01", "2020-01-02"], dtype="datetime64[D]"),
])
def test_missing_keys_of_every_kind_are_rejected(keys):
    with pytest.raises(ValueError, match="missing"):
        hm.compute_grouped(hm.mae, None, np.arange(4.0), np.arange(4.0) + 1, group_by={"g": keys})


def test_nan_key_in_a_dataframe_column():
    df = _frame()
    df.loc[df.index[2], "month"] = np.nan
    with pytest.raises(ValueError, match="missing"):
        hm.compute_grouped(hm.mae, df, "q_obs", "q_sim", group_by="month")


@pytest.mark.parametrize("name, extra", [
    ("ssigma_delta", {"ref_date": np.tile([0, 0, 0, 1, 1, 1], 2)}),
    ("forecast_verification_delta", {"ref_date": np.tile([0, 0, 0, 1, 1, 1], 2)}),
    ("nse_variance_weighted", {"gauge": np.tile([0, 1, 0, 1, 0, 1], 2)}),
    ("regNSE", {"dates": np.datetime64("2020-01-01") + np.arange(12)}),
])
def test_metrics_with_additional_arrays_are_not_groupable(name, extra):
    obs = np.arange(1.0, 13.0)
    with pytest.raises(NotImplementedError, match="does not slice") as info:
        hm.compute_grouped(getattr(hm, name), None, obs, obs + np.sin(obs), group_by={"g": np.repeat([1, 2], 6)}, **extra)
    assert name in str(info.value)
    assert "loop" in str(info.value)


@pytest.mark.parametrize("kwargs", [
    {"sample_weight": np.ones(12)},
    {"weight": np.ones(12)},
])
def test_row_length_weights_are_not_sliced_and_say_so(kwargs):
    obs = np.arange(1.0, 13.0)
    with pytest.raises(NotImplementedError, match="does not slice"):
        hm.compute_grouped(hm.mae, None, obs, obs + 1, group_by={"g": np.repeat([1, 2], 6)}, **kwargs)


def test_row_length_arrays_in_other_arguments_are_rejected_too():
    obs = np.arange(1.0, 13.0)
    with pytest.raises(NotImplementedError, match="does not slice"):
        hm.compute_grouped(hm.nse, None, obs, obs + np.sin(obs), group_by={"g": np.repeat([1, 2], 6)}, norm=np.full(12, 5.0))
    # a scalar or a short array is passed to every group unchanged
    result = hm.compute_grouped(hm.nse, None, obs, obs + np.sin(obs), group_by={"g": np.repeat([1, 2], 6)}, norm=5.0)
    assert len(result) == 2


def test_polars_column_names_give_a_type_error_with_the_way_out():
    df = pl.DataFrame({"q_obs": [1.0, 2.0, 3.0, 4.0], "q_sim": [1.1, 2.1, 2.9, 4.2], "g": [1, 1, 2, 2]})
    with pytest.raises(TypeError, match="polars") as info:
        hm.compute_grouped(hm.mae, df, "q_obs", "q_sim", group_by="g")
    assert "to_numpy" in str(info.value)
    with pytest.raises(TypeError, match="polars"):
        hm.compute_grouped(hm.mae, None, df["q_obs"], df["q_sim"], group_by={"g": df["g"]})
    with pytest.raises(TypeError, match="polars"):
        hm.compute_grouped(hm.mae, df, df["q_obs"], df["q_sim"], group_by="g")
    # the recommended way works
    result = hm.compute_grouped(hm.mae, None, df["q_obs"].to_numpy(), df["q_sim"].to_numpy(), group_by={"g": df["g"].to_numpy()})
    assert len(result) == 2


def test_names_of_columns_need_a_table():
    with pytest.raises(TypeError, match="pandas DataFrame"):
        hm.compute_grouped(hm.mae, None, "q_obs", "q_sim", group_by={"g": [1, 2]})


def test_to_xarray_with_two_grouping_variables_is_not_implemented():
    result = hm.compute_grouped(hm.mae, _frame(), "q_obs", "q_sim", group_by=["station", "month"])
    with pytest.raises(NotImplementedError, match="one grouping variable") as info:
        result.to_xarray()
    assert "to_pandas" in str(info.value)


def test_dictionary_valued_metric_is_not_groupable():
    with pytest.raises(NotImplementedError, match="one number per group") as info:
        hm.compute_grouped(hm.kge_components, _frame(), "q_obs", "q_sim", group_by="month")
    assert "kge_components" in str(info.value) and "loop" in str(info.value)


@pytest.mark.parametrize("make", [
    lambda o, s: (hm.forecast_verification, o, s, {"reduction": "none"}),
    lambda o, s: (hm.crps, o, np.c_[s, s, s], {"reduction": "none"}),
    lambda o, s: (hm.mae, np.c_[o, o], np.c_[s, s], {"axis": 0}),
    lambda o, s: (hm.mae, np.c_[o], np.c_[s], {"axis": 0}),
])
def test_array_valued_results_are_not_groupable(make):
    obs = np.arange(1.0, 13.0)
    func, o, s, kwargs = make(obs, obs + np.sin(obs))
    with pytest.raises(NotImplementedError, match="one number per group"):
        hm.compute_grouped(func, None, o, s, group_by={"g": np.repeat([1, 2], 6)}, **kwargs)
