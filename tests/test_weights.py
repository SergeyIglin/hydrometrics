"""Weights: names, unsupported metrics and the reduction rule (items #7, section 2.3; D7, D8, D10)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm
from _cases import (
    BACKENDS, NAMES, NO_WEIGHT, WEIGHT_NAMES, case_1d, case_2d, same, values, weights, wrap,
)


def _weighted_mean(x, w):
    return np.sum(w * x) / np.sum(w)


def test_weighted_reference_values():
    """Independent weighted formulas for the simple metrics."""
    obs, sim, _ = case_1d("mae")
    w = weights(obs.shape)
    assert float(hm.mae(obs, sim, sample_weight=w)) == pytest.approx(_weighted_mean(np.abs(obs - sim), w), rel=1e-12)
    assert float(hm.mse(obs, sim, sample_weight=w)) == pytest.approx(_weighted_mean((obs - sim) ** 2, w), rel=1e-12)
    assert float(hm.bias(obs, sim, sample_weight=w)) == pytest.approx(_weighted_mean(sim - obs, w), rel=1e-12)
    mean = _weighted_mean(obs, w)
    nse = 1 - np.sum(w * (obs - sim) ** 2) / np.sum(w * (obs - mean) ** 2)
    assert float(hm.nse(obs, sim, sample_weight=w)) == pytest.approx(nse, rel=1e-12)


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("name", WEIGHT_NAMES)
def test_weight_is_an_alias_of_sample_weight(name, backend):
    obs, sim, extra = case_1d(name)
    w = weights(obs.shape)
    f = getattr(hm, name)
    a = f(wrap(backend, obs), wrap(backend, sim), sample_weight=wrap(backend, w), **extra)
    b = f(wrap(backend, obs), wrap(backend, sim), weight=wrap(backend, w), **extra)
    assert same(values(a), values(b))
    assert not same(values(a), values(f(wrap(backend, obs), wrap(backend, sim), **extra))) or name in ("sharpness",)


@pytest.mark.parametrize("backend", BACKENDS)
def test_both_weight_names_at_once_are_rejected(backend):
    obs, sim, _ = case_1d("mae")
    w = wrap(backend, weights(obs.shape))
    with pytest.raises(TypeError, match="sample_weight"):
        hm.mae(wrap(backend, obs), wrap(backend, sim), sample_weight=w, weight=w)


@pytest.mark.parametrize("keyword", ["sample_weight", "weight"])
@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("name", sorted(NO_WEIGHT))
def test_metrics_without_weights_refuse_them(name, backend, keyword):
    """D8: weights were dropped silently on numpy."""
    obs, sim, extra = case_1d(name)
    w = wrap(backend, weights(obs.shape))
    with pytest.raises(NotImplementedError, match=name):
        getattr(hm, name)(wrap(backend, obs), wrap(backend, sim), **{keyword: w}, **extra)


def test_the_unsupported_list_matches_the_metric_flags():
    flagged = {n for n in NAMES if not getattr(hm, n).supports_weight}
    assert flagged == set(NO_WEIGHT)


@pytest.mark.parametrize("backend", BACKENDS)
def test_negative_weights_are_rejected(backend):
    obs, sim, _ = case_1d("mae")
    w = weights(obs.shape)
    w[3] = -1.0
    with pytest.raises(ValueError, match="non-negative"):
        hm.mae(wrap(backend, obs), wrap(backend, sim), sample_weight=wrap(backend, w))


@pytest.mark.parametrize("backend", BACKENDS)
def test_weight_shape_must_match(backend):
    obs, sim, _ = case_1d("mae")
    with pytest.raises(ValueError, match="Weight shape"):
        hm.mae(wrap(backend, obs), wrap(backend, sim), sample_weight=wrap(backend, weights(obs.shape[0] - 1)))


def test_nan_weight_makes_the_pair_invalid_under_omit():
    obs, sim, _ = case_1d("mae")
    w = weights(obs.shape)
    w[[2, 9]] = np.nan
    keep = ~np.isnan(w)
    got = hm.mae(obs, sim, sample_weight=w)
    assert float(got) == pytest.approx(_weighted_mean(np.abs(obs - sim)[keep], w[keep]), rel=1e-12)
    assert got.nan_info["n_nan_removed"] == 2


def test_zero_weights_for_all_pairs_give_nan():
    obs, sim, _ = case_1d("mae")
    assert np.isnan(float(hm.mae(obs, sim, sample_weight=np.zeros(obs.shape))))


# ---- reduction (D10) ----

@pytest.mark.parametrize("backend", BACKENDS)
def test_axis_without_reduction_returns_an_array(backend):
    obs, sim = case_2d("nse", g=5)
    where = {"dim": "time"} if backend == "xarray" else {"axis": 0}
    value = values(hm.nse(wrap(backend, obs), wrap(backend, sim), **where))
    assert value.shape == (5,)


@pytest.mark.parametrize("backend", BACKENDS)
def test_without_axis_reduction_defaults_to_mean(backend):
    obs, sim = case_2d("nse", g=5)
    flat = values(hm.nse(wrap(backend, obs), wrap(backend, sim)))
    assert flat.shape == ()


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("reduction", ["mean", "sum", "none"])
def test_explicit_reduction_is_applied_on_every_backend(backend, reduction):
    obs, sim = case_2d("nse", g=5)
    per = values(hm.nse(obs, sim, axis=0))
    where = {"dim": "time"} if backend == "xarray" else {"axis": 0}
    got = values(hm.nse(wrap(backend, obs), wrap(backend, sim), reduction=reduction, **where))
    expected = {"mean": per.mean(), "sum": per.sum(), "none": per}[reduction]
    assert same(got, expected)


def test_reduction_applies_to_every_component_of_kge_components():
    obs, sim = case_2d("kge_components", g=5)
    per = hm.kge_components(obs, sim, axis=0).value
    assert all(np.shape(v) == (5,) for v in per.values())
    mean = hm.kge_components(obs, sim, axis=0, reduction="mean").value
    assert all(np.shape(v) == () for v in mean.values())
    assert mean["r"] == pytest.approx(np.mean(per["r"]))


def test_unknown_reduction_is_rejected():
    obs, sim = case_2d("nse", g=5)
    with pytest.raises(ValueError, match="reduction"):
        hm.nse(obs, sim, axis=0, reduction="bogus")


def test_reduction_enum_members_are_accepted():
    obs, sim = case_2d("nse", g=5)
    assert values(hm.nse(obs, sim, axis=0, reduction=hm.Reduction.NONE)).shape == (5,)
    assert values(hm.nse(obs, sim, axis=0, reduction=hm.Reduction.SUM)).shape == ()
