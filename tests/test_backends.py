"""numpy, pandas, polars and xarray agree (report items #6, #7, #28, #29; D11, section 5.4)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm
from _cases import (
    AXIS_NAMES, BACKENDS, NAMES, case_1d, case_2d, same, values, weights, wrap,
)

OTHERS = ["pandas", "polars", "xarray"]


@pytest.mark.parametrize("backend", OTHERS)
@pytest.mark.parametrize("name", NAMES)
def test_scalar_value_matches_numpy(name, backend):
    obs, sim, extra = case_1d(name)
    f = getattr(hm, name)
    ref = f(obs, sim, **extra)
    got = f(wrap(backend, obs), wrap(backend, sim), **extra)
    assert same(values(got), values(ref)), (name, backend)


@pytest.mark.parametrize("backend", OTHERS)
@pytest.mark.parametrize("name", NAMES)
def test_result_metadata_is_identical_across_backends(name, backend):
    """Section 5.4: 23 metrics had different names; EDI had different bounds."""
    obs, sim, extra = case_1d(name)
    f = getattr(hm, name)
    ref = f(obs, sim, **extra)
    got = f(wrap(backend, obs), wrap(backend, sim), **extra)
    for attr in ("name", "direction", "bounds", "reference", "norm_source"):
        assert getattr(got, attr) == getattr(ref, attr), (name, backend, attr)
    assert got.meta["formula"] == ref.meta["formula"]
    assert type(got).__name__ == "MetricResult"


@pytest.mark.parametrize("name", ["kge_2009", "kge_2012"])
@pytest.mark.parametrize("backend", BACKENDS)
def test_kge_returns_a_scalar_result_on_every_backend(name, backend):
    """#7 (D11): pandas, polars and xarray returned a tuple."""
    obs, sim, _ = case_1d(name)
    result = getattr(hm, name)(wrap(backend, obs), wrap(backend, sim))
    assert result.is_scalar
    assert float(result) == pytest.approx(float(getattr(hm, name)(obs, sim)), rel=1e-12)


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("version", ["2009", "2012"])
def test_kge_components_value_is_a_dict_on_every_backend(backend, version):
    obs, sim, _ = case_1d("kge_components")
    result = hm.kge_components(wrap(backend, obs), wrap(backend, sim), version=version)
    assert type(result).__name__ == "MetricResult"
    assert set(result.value) == ({"r", "alpha", "beta"} | ({"gamma"} if version == "2012" else set()))


@pytest.mark.parametrize("name", AXIS_NAMES)
def test_pandas_and_polars_axis_match_numpy(name):
    obs, sim = case_2d(name)
    ref = values(getattr(hm, name)(obs, sim, axis=0))
    for backend in ("pandas", "polars"):
        got = values(getattr(hm, name)(wrap(backend, obs), wrap(backend, sim), axis=0))
        assert same(got, ref), (name, backend)


@pytest.mark.parametrize("name", AXIS_NAMES)
def test_xarray_dim_matches_numpy_axis(name):
    """#28, #29: dim failed for ten metrics and axis= raised TypeError."""
    obs, sim = case_2d(name)
    ref0 = values(getattr(hm, name)(obs, sim, axis=0))
    ref1 = values(getattr(hm, name)(obs, sim, axis=1))
    xo, xs = wrap("xarray", obs), wrap("xarray", sim)
    assert same(values(getattr(hm, name)(xo, xs, dim="time")), ref0)
    assert same(values(getattr(hm, name)(xo, xs, dim="station")), ref1)
    assert same(values(getattr(hm, name)(xo, xs, axis=0)), ref0)
    assert same(values(getattr(hm, name)(xo, xs, axis=1)), ref1)


@pytest.mark.parametrize("name", [n for n in AXIS_NAMES if n not in ("forecast_verification", "kge_components")])
def test_xarray_all_dimensions_equals_pooled_numpy(name):
    obs, sim = case_2d(name)
    pooled = values(getattr(hm, name)(obs, sim))
    xo, xs = wrap("xarray", obs), wrap("xarray", sim)
    got = values(getattr(hm, name)(xo, xs, dim=["time", "station"]))
    assert same(got, pooled), name


@pytest.mark.parametrize("name", ["nse", "rmse", "pearson_r", "kge_2012", "crps", "brier_score", "accuracy"])
def test_weights_match_across_backends(name):
    obs, sim = case_2d(name)
    w = weights(obs.shape)
    ref = values(getattr(hm, name)(obs, sim, axis=0, sample_weight=w))
    for backend in OTHERS:
        wo, ws, ww = wrap(backend, obs), wrap(backend, sim), wrap(backend, w)
        where = {"dim": "time"} if backend == "xarray" else {"axis": 0}
        got = values(getattr(hm, name)(wo, ws, sample_weight=ww, **where))
        assert same(got, ref), (name, backend)


def test_xarray_result_keeps_dimension_and_coordinate():
    xr = pytest.importorskip("xarray")
    obs, sim = case_2d("nse", g=3)
    coords = {"time": np.arange(obs.shape[0]), "station": ["upper", "middle", "lower"]}
    xo = xr.DataArray(obs, dims=["time", "station"], coords=coords)
    xs = xr.DataArray(sim, dims=["time", "station"], coords=coords)
    value = hm.nse(xo, xs, dim="time").value
    assert isinstance(value, xr.DataArray)
    assert value.dims == ("station",)
    assert value.coords["station"].values.tolist() == ["upper", "middle", "lower"]
    assert hm.nse(xo, xs, dim=["time", "station"]).value.dims == ()


def test_xarray_aligns_dimension_order_by_name():
    xr = pytest.importorskip("xarray")
    obs, sim = case_2d("nse", g=3)
    xo = xr.DataArray(obs, dims=["time", "station"])
    xs = xr.DataArray(sim, dims=["time", "station"]).transpose("station", "time")
    assert same(values(hm.nse(xo, xs, dim="time")), values(hm.nse(obs, sim, axis=0)))


def test_xarray_dim_and_axis_together_are_rejected():
    obs, sim = case_2d("nse", g=3)
    xo, xs = wrap("xarray", obs), wrap("xarray", sim)
    with pytest.raises(TypeError, match="dim"):
        hm.nse(xo, xs, dim="time", axis=0)


def test_xarray_dataset_is_not_supported_with_a_clear_message():
    """#30: the Dataset branch was unreachable."""
    xr = pytest.importorskip("xarray")
    obs, sim = case_2d("nse", g=3)
    ds = xr.Dataset({"q": xr.DataArray(obs, dims=["time", "station"])})
    with pytest.raises(NotImplementedError, match="Dataset"):
        hm.nse(ds, ds)


@pytest.mark.parametrize("backend", BACKENDS)
def test_shape_mismatch_message_is_the_same_on_every_backend(backend):
    obs, sim, _ = case_1d("nse")
    # labelled pandas inputs of different length fail the strict index check first
    pattern = "not aligned" if backend == "pandas" else "Shape mismatch"
    with pytest.raises(ValueError, match=pattern):
        hm.nse(wrap(backend, obs), wrap(backend, sim[:-1]))
