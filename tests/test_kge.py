"""KGE variants against independent formulas (report items #34, #46, #26, #27)."""

from __future__ import annotations

import numpy as np
import pytest

import hydrometrics as hm


def _data():
    rng = np.random.default_rng(3)
    t = np.arange(400)
    obs = 15 + 60 * np.exp(-(((t % 365) - 120) / 25.0) ** 2) + rng.gamma(2.0, 2.0, t.size)
    sim = np.clip(0.8 * obs + 6 + rng.normal(0, 5, t.size), 0.1, None)
    return obs, sim


def _reference(obs, sim):
    """r, alpha, beta, gamma written from the published definitions."""
    r = np.corrcoef(obs, sim)[0, 1]
    mu_o, mu_s = obs.mean(), sim.mean()
    sd_o, sd_s = obs.std(ddof=1), sim.std(ddof=1)
    alpha = sd_s / sd_o
    beta = mu_s / mu_o
    gamma = (sd_s / mu_s) / (sd_o / mu_o)
    return r, alpha, beta, gamma


def test_kge_2012_has_three_terms_without_alpha():
    """Kling et al. (2012) as given by Santos et al. (2018): r, beta and gamma only."""
    obs, sim = _data()
    r, _, beta, gamma = _reference(obs, sim)
    expected = 1 - np.sqrt((r - 1) ** 2 + (beta - 1) ** 2 + (gamma - 1) ** 2)
    assert float(hm.kge_2012(obs, sim)) == pytest.approx(expected, rel=1e-12)


def test_kge_2009_has_three_terms_with_alpha():
    obs, sim = _data()
    r, alpha, beta, _ = _reference(obs, sim)
    expected = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
    assert float(hm.kge_2009(obs, sim)) == pytest.approx(expected, rel=1e-12)


def test_kge_2012_differs_from_old_four_term_form():
    obs, sim = _data()
    r, alpha, beta, gamma = _reference(obs, sim)
    old = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2 + (gamma - 1) ** 2)
    assert abs(float(hm.kge_2012(obs, sim)) - old) > 1e-4


@pytest.mark.parametrize("version", ["2009", "2012"])
def test_kge_components_reproduce_kge(version):
    obs, sim = _data()
    c = hm.kge_components(obs, sim, version=version).value
    r, alpha, beta = c["r"], c["alpha"], c["beta"]
    if version == "2009":
        kge = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
        assert kge == pytest.approx(float(hm.kge_2009(obs, sim)), rel=1e-12)
    else:
        kge = 1 - np.sqrt((r - 1) ** 2 + (beta - 1) ** 2 + (c["gamma"] - 1) ** 2)
        assert kge == pytest.approx(float(hm.kge_2012(obs, sim)), rel=1e-12)
    ref = _reference(obs, sim)
    assert (c["r"], c["alpha"], c["beta"]) == pytest.approx(ref[:3], rel=1e-12)


def test_kge_2012_perfect_and_biased_cases():
    obs, _ = _data()
    assert float(hm.kge_2012(obs, obs)) == pytest.approx(1.0)
    # A pure scale change keeps r = 1 and gamma = 1, so only beta contributes.
    assert float(hm.kge_2012(obs, 2.0 * obs)) == pytest.approx(0.0, abs=1e-12)


def _wrap(backend, array):
    if backend == "numpy":
        return array
    if backend == "pandas":
        return pytest.importorskip("pandas").Series(array)
    if backend == "polars":
        return pytest.importorskip("polars").Series("q", array)
    if backend == "xarray":
        return pytest.importorskip("xarray").DataArray(array, dims=["time"])
    raise ValueError(backend)


@pytest.mark.parametrize("backend", ["numpy", "pandas", "polars", "xarray"])
@pytest.mark.parametrize("name", ["alpha_component", "kge_components"])
def test_invalid_version_raises_value_error_on_every_backend(backend, name):
    obs, sim = _data()
    with pytest.raises(ValueError, match="version"):
        getattr(hm, name)(_wrap(backend, obs), _wrap(backend, sim), version="1999")


@pytest.mark.parametrize("version", ["2009", "2012"])
def test_alpha_ignores_valid_version(version):
    obs, sim = _data()
    assert float(hm.alpha_component(obs, sim, version=version)) == pytest.approx(_reference(obs, sim)[1])


def test_alpha_docstring_says_version_has_no_effect():
    doc = hm.alpha_component.__doc__
    assert "no effect" in doc and "KGE'" in doc
