"""axis on 2-D input (report items #8-#11, #13, #14, #18; D10)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm
from _cases import (
    AXIS_NAMES, ELEMENTWISE, NAMES, NO_AXIS, WEIGHT_NAMES, case_1d, case_2d, same, values, weights,
)


def _slices(name, obs, sim, axis, **kw):
    """Reference: the 1-D call applied to every slice along ``axis``."""
    f = getattr(hm, name)
    if axis == 0:
        parts = [values(f(obs[:, j], sim[:, j], reduction="none", **_pick(kw, j, 0))) for j in range(obs.shape[1])]
    else:
        parts = [values(f(obs[i], sim[i], reduction="none", **_pick(kw, i, 1))) for i in range(obs.shape[0])]
    return np.stack(parts, axis=-1)


def _pick(kw, index, axis):
    out = dict(kw)
    if "sample_weight" in out:
        w = out["sample_weight"]
        out["sample_weight"] = w[:, index] if axis == 0 else w[index]
    return out


@pytest.mark.parametrize("axis", [0, 1])
@pytest.mark.parametrize("name", AXIS_NAMES)
def test_axis_equals_one_dimensional_call_on_every_slice(name, axis):
    obs, sim = case_2d(name)
    got = values(getattr(hm, name)(obs, sim, axis=axis))
    expected = _slices(name, obs, sim, axis)
    if name in ELEMENTWISE:
        expected = _to_obs_layout(expected, axis)
    assert same(got, expected), name


def _to_obs_layout(stacked, axis):
    """Slices stacked on the last axis -> layout of obs: columns (axis=0) already match, rows (axis=1) need a swap."""
    return stacked if axis == 0 else np.moveaxis(stacked, -1, 0)


@pytest.mark.parametrize("name", [n for n in AXIS_NAMES if n not in ELEMENTWISE])
def test_axis_result_has_no_extra_dimension(name):
    """#8, #9: nrmse, pbias, pearson_r, kge_*, alpha_component, rsr, sharpness gave (1, n)."""
    obs, sim = case_2d(name)
    n, g = obs.shape
    got0 = values(getattr(hm, name)(obs, sim, axis=0))
    got1 = values(getattr(hm, name)(obs, sim, axis=1))
    assert got0.shape[-1:] == (g,) and got0.ndim == (2 if name == "kge_components" else 1)
    assert got1.shape[-1:] == (n,) and got1.ndim == (2 if name == "kge_components" else 1)


@pytest.mark.parametrize("axis", [0, 1])
@pytest.mark.parametrize("name", [n for n in WEIGHT_NAMES if n in AXIS_NAMES])
def test_weighted_axis_equals_weighted_slices(name, axis):
    obs, sim = case_2d(name)
    w = weights(obs.shape)
    got = values(getattr(hm, name)(obs, sim, axis=axis, sample_weight=w))
    expected = _slices(name, obs, sim, axis, sample_weight=w)
    if name in ELEMENTWISE:
        expected = _to_obs_layout(expected, axis)
    assert same(got, expected), name


@pytest.mark.parametrize("name", ["spearman_r", "kendall_tau", "roc_auc", "pr_auc", "reliability"])
def test_rank_and_binning_metrics_support_axis(name):
    """#10, #11, #13: these either failed or returned one pooled value."""
    obs, sim = case_2d(name)
    got = values(getattr(hm, name)(obs, sim, axis=0))
    assert got.shape == (obs.shape[1],)
    assert np.isfinite(got).all()


@pytest.mark.parametrize("name", sorted(NO_AXIS))
def test_metrics_without_axis_raise_not_implemented(name):
    """#14: axis was silently ignored (ssigma) or failed with another error."""
    obs, sim, extra = case_1d(name)
    obs2, sim2 = np.column_stack([obs, obs]), np.column_stack([sim, sim])
    with pytest.raises(NotImplementedError, match=name):
        getattr(hm, name)(obs2, sim2, axis=0, **extra)


def test_axis_out_of_range_is_an_error():
    obs, sim = case_2d("nse")
    with pytest.raises(getattr(np, "exceptions", np).AxisError):
        hm.nse(obs, sim, axis=5)


def test_every_metric_is_covered():
    assert set(AXIS_NAMES) | NO_AXIS == set(NAMES)
