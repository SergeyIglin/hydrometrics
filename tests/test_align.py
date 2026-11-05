"""Stage B of task_5: strict index check by default, align="inner" on request (KNOWN_ISSUES #7)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm

# These tests need all three optional backends; without them the module is skipped.
pd = pytest.importorskip("pandas")
pl = pytest.importorskip("polars")
xr = pytest.importorskip("xarray")

RNG = np.random.default_rng(11)
N = 12
DAYS = pd.date_range("2020-01-01", periods=N)
SHIFTED = pd.date_range("2020-01-04", periods=N)  # overlaps on the last 9 days of DAYS
OBS = 10 + RNG.gamma(2.0, 3.0, N)
SIM = OBS + RNG.normal(0, 2, N)
HINT = "align='inner'"


def series(values, index):
    return pd.Series(values, index=index)


def manual_inner(metric, obs_s, sim_s, **kw):
    common = obs_s.index.intersection(sim_s.index)
    common = obs_s.index[obs_s.index.isin(common)]
    return float(metric(obs_s.loc[common].to_numpy(), sim_s.loc[common].to_numpy(), **kw))


# ---- pandas ----

def test_equal_indexes_give_the_old_result():
    for align in ("strict", "inner"):
        got = float(hm.nse(series(OBS, DAYS), series(SIM, DAYS), align=align))
        assert got == pytest.approx(float(hm.nse(OBS, SIM)), rel=1e-14)
    assert float(hm.nse(series(OBS, DAYS), series(SIM, DAYS))) == pytest.approx(float(hm.nse(OBS, SIM)), rel=1e-14)


def test_shifted_index_is_an_error_with_the_first_difference_and_a_hint():
    with pytest.raises(ValueError) as info:
        hm.nse(series(OBS, DAYS), series(SIM, SHIFTED))
    message = str(info.value)
    assert "not aligned" in message and HINT in message
    assert "2020-01-01" in message and "2020-01-04" in message  # the first labels that differ
    assert str(N) in message  # lengths


def test_different_lengths_are_reported():
    with pytest.raises(ValueError, match="not aligned") as info:
        hm.nse(series(OBS, DAYS), series(SIM[:-2], DAYS[:-2]))
    assert str(N) in str(info.value) and str(N - 2) in str(info.value)


def test_inner_equals_the_manual_calculation_over_the_intersection():
    o, s = series(OBS, DAYS), series(SIM, SHIFTED)
    got = hm.nse(o, s, align="inner")
    assert float(got) == pytest.approx(manual_inner(hm.nse, o, s), rel=1e-14)
    assert got.meta["n_dropped_by_align"] == 3 + 3


def test_permuted_index_is_an_error_in_strict_and_follows_obs_in_inner():
    o = series(OBS, DAYS)
    s = series(SIM, DAYS).iloc[::-1]
    with pytest.raises(ValueError, match="not aligned"):
        hm.nse(o, s)
    got = hm.nse(o, s, align="inner")
    assert float(got) == pytest.approx(float(hm.nse(OBS, SIM)), rel=1e-14)
    assert got.meta["n_dropped_by_align"] == 0
    # a non-symmetric metric is sensitive to the order: pairs must follow obs
    assert float(hm.bias(o, s, align="inner")) == pytest.approx(float(hm.bias(OBS, SIM)), rel=1e-14)


def test_dataframe_with_several_columns_and_axis():
    o = pd.DataFrame({"a": OBS, "b": OBS * 2}, index=DAYS)
    s = pd.DataFrame({"a": SIM, "b": SIM * 2.1}, index=SHIFTED)
    with pytest.raises(ValueError, match="not aligned"):
        hm.nse(o, s, axis=0)
    got = np.asarray(hm.nse(o, s, axis=0, align="inner").value)
    common = o.index[o.index.isin(s.index)]
    expected = [float(hm.nse(o[c].loc[common].to_numpy(), s[c].loc[common].to_numpy())) for c in ("a", "b")]
    np.testing.assert_allclose(got, expected, rtol=1e-13)


def test_ensemble_dataframe_is_compared_on_its_row_index():
    members = pd.DataFrame(OBS[:, None] + RNG.normal(0, 1, (N, 5)), index=SHIFTED)
    o = series(OBS, DAYS)
    with pytest.raises(ValueError, match="not aligned"):
        hm.crps(o, members)
    got = hm.crps(o, members, align="inner")
    common = o.index[o.index.isin(members.index)]
    expected = float(hm.crps(o.loc[common].to_numpy(), members.loc[common].to_numpy()))
    assert float(got) == pytest.approx(expected, rel=1e-13)


def test_duplicate_labels_are_an_error_for_inner_only():
    dup = pd.DatetimeIndex(list(DAYS[:-1]) + [DAYS[0]])
    o, s = series(OBS, dup), series(SIM, dup)
    assert np.isfinite(float(hm.nse(o, s)))  # equal indexes pass the strict check
    with pytest.raises(ValueError, match="duplicate"):
        hm.nse(o, s, align="inner")


def test_empty_intersection_is_an_error():
    far = pd.date_range("2030-01-01", periods=N)
    with pytest.raises(ValueError, match="no common"):
        hm.nse(series(OBS, DAYS), series(SIM, far), align="inner")


def test_alignment_happens_before_the_nan_handling():
    o, s = series(OBS.copy(), DAYS), series(SIM.copy(), SHIFTED)
    o.iloc[5] = np.nan  # 2020-01-06 lies in the overlap
    got = hm.nse(o, s, align="inner")
    assert got.nan_info["n_total"] == 9
    assert got.nan_info["n_nan_removed"] == 1
    assert hm.nse(o, s, align="inner", nan_policy="propagate").value != hm.nse(o, s, align="inner").value


def test_pandas_weights_follow_the_alignment():
    w = series(np.linspace(1, 2, N), DAYS)
    o, s = series(OBS, DAYS), series(SIM, SHIFTED)
    got = float(hm.nse(o, s, align="inner", sample_weight=w))
    common = o.index[o.index.isin(s.index)]
    expected = float(hm.nse(o.loc[common].to_numpy(), s.loc[common].to_numpy(), sample_weight=w.loc[common].to_numpy()))
    assert got == pytest.approx(expected, rel=1e-13)


# ---- xarray ----

def da(values, **coords):
    dims = list(coords)
    return xr.DataArray(values, dims=dims, coords={k: v for k, v in coords.items() if v is not None})


def test_xarray_equal_coordinates_give_the_old_result():
    o, s = da(OBS, time=DAYS), da(SIM, time=DAYS)
    assert float(hm.nse(o, s)) == pytest.approx(float(hm.nse(OBS, SIM)), rel=1e-14)


def test_xarray_shifted_coordinates_error_and_inner():
    o, s = da(OBS, time=DAYS), da(SIM, time=SHIFTED)
    with pytest.raises(ValueError) as info:
        hm.nse(o, s)
    assert "not aligned" in str(info.value) and HINT in str(info.value) and "time" in str(info.value)
    got = hm.nse(o, s, align="inner")
    expected = manual_inner(hm.nse, series(OBS, DAYS), series(SIM, SHIFTED))
    assert float(got) == pytest.approx(expected, rel=1e-14)
    assert got.meta["n_dropped_by_align"] == 6


def test_xarray_only_one_side_labelled_or_none_is_not_checked():
    labelled = da(OBS, time=DAYS)
    bare = xr.DataArray(SIM, dims=["time"])
    expected = float(hm.nse(OBS, SIM))
    assert float(hm.nse(labelled, bare)) == pytest.approx(expected, rel=1e-14)
    bare_obs = xr.DataArray(OBS, dims=["time"])
    assert float(hm.nse(bare_obs, da(SIM, time=SHIFTED))) == pytest.approx(expected, rel=1e-14)
    assert float(hm.nse(xr.DataArray(OBS, dims=["time"]), bare)) == pytest.approx(expected, rel=1e-14)


def test_xarray_two_dimensions():
    stations = ["up", "down"]
    o = da(np.c_[OBS, OBS * 2], time=DAYS, station=stations)
    s_ok = da(np.c_[SIM, SIM * 2.1], time=DAYS, station=stations)
    s_bad_time = da(np.c_[SIM, SIM * 2.1], time=SHIFTED, station=stations)
    s_bad_station = da(np.c_[SIM, SIM * 2.1], time=DAYS, station=["up", "other"])
    assert np.asarray(hm.nse(o, s_ok, dim="time").value).shape == (2,)
    with pytest.raises(ValueError, match="not aligned"):
        hm.nse(o, s_bad_time, dim="time")
    with pytest.raises(ValueError, match="not aligned"):
        hm.nse(o, s_bad_station, dim="time")
    got = hm.nse(o, s_bad_time, dim="time", align="inner").value
    assert got.dims == ("station",)
    common = DAYS[3:]
    expected = [float(hm.nse(OBS[3:], SIM[:9])), float(hm.nse(OBS[3:] * 2, SIM[:9] * 2.1))]
    np.testing.assert_allclose(got.to_numpy(), expected, rtol=1e-13)


def test_xarray_inner_follows_the_order_of_obs():
    o = da(OBS, time=DAYS)
    s = da(SIM[::-1], time=DAYS[::-1])
    got = hm.bias(o, s, align="inner")
    assert float(got) == pytest.approx(float(hm.bias(OBS, SIM)), rel=1e-14)


def test_xarray_empty_intersection_and_duplicates():
    far = pd.date_range("2030-01-01", periods=N)
    with pytest.raises(ValueError, match="no common"):
        hm.nse(da(OBS, time=DAYS), da(SIM, time=far), align="inner")
    dup = pd.DatetimeIndex(list(DAYS[:-1]) + [DAYS[0]])
    with pytest.raises(ValueError, match="duplicate"):
        hm.nse(xr.DataArray(OBS, dims=["time"], coords={"time": dup}), xr.DataArray(SIM, dims=["time"], coords={"time": dup}), align="inner")


# ---- numpy, polars, mixed inputs ----

@pytest.mark.parametrize("make", [
    lambda a: a,
    lambda a: pl.Series(a),
])
def test_inner_needs_labelled_inputs(make):
    with pytest.raises(ValueError, match="requires labelled inputs"):
        hm.nse(make(OBS), make(SIM), align="inner")
    assert float(hm.nse(make(OBS), make(SIM), align="strict")) == pytest.approx(float(hm.nse(OBS, SIM)), rel=1e-14)


def test_mixed_types_skip_the_strict_check_and_reject_inner():
    o = series(OBS, DAYS)
    assert float(hm.nse(o, SIM)) == pytest.approx(float(hm.nse(OBS, SIM)), rel=1e-14)
    assert float(hm.nse(o, pl.Series(SIM))) == pytest.approx(float(hm.nse(OBS, SIM)), rel=1e-14)
    with pytest.raises(ValueError, match="requires labelled inputs"):
        hm.nse(o, SIM, align="inner")


def test_invalid_value_of_align():
    for o, s in ((OBS, SIM), (series(OBS, DAYS), series(SIM, DAYS)), (pl.Series(OBS), pl.Series(SIM)),
                 (da(OBS, time=DAYS), da(SIM, time=DAYS))):
        with pytest.raises(ValueError, match="align"):
            hm.nse(o, s, align="outer")


def test_messages_have_one_structure_on_every_labelled_backend():
    pandas_error = xarray_error = None
    try:
        hm.nse(series(OBS, DAYS), series(SIM, SHIFTED))
    except ValueError as exc:
        pandas_error = str(exc)
    try:
        hm.nse(da(OBS, time=DAYS), da(SIM, time=SHIFTED))
    except ValueError as exc:
        xarray_error = str(exc)
    for message in (pandas_error, xarray_error):
        assert message.startswith("obs and sim are not aligned")
        assert "first difference" in message and message.endswith(HINT + ".")


def test_align_is_in_the_signature_and_documented():
    import inspect
    for name in ("nse", "crps", "regNSE", "kge_components"):
        func = getattr(hm, name)
        assert inspect.signature(func).parameters["align"].default == "strict"
        assert "\nalign :" in func.__doc__


# ---- compute_grouped ----

def test_compute_grouped_checks_and_aligns():
    o, s = series(OBS, DAYS), series(SIM, SHIFTED)
    groups = pd.Series(["a", "b", "a", "b", "a", "b", "a", "b", "a", "b", "a", "b"], index=DAYS)
    with pytest.raises(ValueError, match="not aligned"):
        hm.compute_grouped(hm.mae, None, o, s, group_by={"g": groups})
    result = hm.compute_grouped(hm.mae, None, o, s, group_by={"g": groups}, align="inner")
    common = DAYS[3:]
    o2, s2, g2 = o.loc[common], s.loc[common], groups.loc[common]
    for (key,), value in result:
        mask = (g2 == key).to_numpy()
        assert value == pytest.approx(float(hm.mae(o2.to_numpy()[mask], s2.to_numpy()[mask])), rel=1e-13)


def test_compute_grouped_dataframe_columns_share_an_index():
    df = pd.DataFrame({"q_obs": OBS, "q_sim": SIM, "g": [1, 1, 1, 2, 2, 2] * 2}, index=DAYS)
    plain = hm.compute_grouped(hm.mae, df, "q_obs", "q_sim", group_by="g")
    inner = hm.compute_grouped(hm.mae, df, "q_obs", "q_sim", group_by="g", align="inner")
    np.testing.assert_allclose(plain.values, inner.values, rtol=1e-14)
