"""Cross-check against ``HydroErr``: NSE, KGE 2009/2012, RMSE, MAE, Spearman, R2.

Conventions read from the installed ``HydroErr/HydroErr.py``:

* signature ``f(simulated_array, observed_array)`` (sim first); 1-D arrays only;
* ``kge_2009(..., return_all=True)`` -> ``(r, alpha, beta, kge)``; std with ``ddof=1``;
* ``kge_2012(..., return_all=True)`` -> ``(r, gamma, beta, kge)``; std with ``ddof=0``
  (both cancel in the ratios alpha and gamma, the library uses ``ddof=1``);
* ``r_squared`` is the SQUARED PEARSON CORRELATION, not the coefficient of
  determination: it equals ``hm.pearson_r ** 2`` and differs from ``hm.r2``;
* NaN: the pairs are removed (done here explicitly, so no warning is raised);
* no PBIAS and no weights.
"""
import numpy as np
import pytest

HydroErr = pytest.importorskip("HydroErr")

import hydrometrics as hm  # noqa: E402
from crosscheck_data import ATOL, RTOL, UNWEIGHTED, columns, get_variant, lib_value  # noqa: E402

PAIRS = {
    "nse": HydroErr.nse,
    "kge_2009": HydroErr.kge_2009,
    "kge_2012": HydroErr.kge_2012,
    "rmse": HydroErr.rmse,
    "mae": HydroErr.mae,
    "spearman_r": HydroErr.spearman_r,
}


@pytest.mark.parametrize("variant", UNWEIGHTED)
@pytest.mark.parametrize("name", list(PAIRS))
def test_against_hydroerr(name, variant):
    obs, sim, _ = get_variant(variant)
    got = lib_value(name, obs, sim)
    ref = np.array([PAIRS[name](s, o) for o, s in columns(obs, sim)])
    np.testing.assert_allclose(got, ref, rtol=RTOL, atol=ATOL)


@pytest.mark.parametrize("variant", UNWEIGHTED)
def test_r_squared_is_squared_pearson(variant):
    obs, sim, _ = get_variant(variant)
    ref = np.array([HydroErr.r_squared(s, o) for o, s in columns(obs, sim)])
    pearson = lib_value("pearson_r", obs, sim)
    np.testing.assert_allclose(pearson**2, ref, rtol=RTOL, atol=ATOL)
    # the library r2 is the coefficient of determination: a different quantity
    assert not np.allclose(lib_value("r2", obs, sim), ref, rtol=1e-3)


@pytest.mark.parametrize("variant", ["clean", "nan"])
def test_kge_components(variant):
    obs, sim, _ = get_variant(variant)
    ((o, s),) = list(columns(obs, sim))
    r, alpha, beta, _ = HydroErr.kge_2009(s, o, return_all=True)
    comp = hm.kge_components(obs, sim, version="2009").value
    np.testing.assert_allclose(
        [float(comp["r"]), float(comp["alpha"]), float(comp["beta"])], [r, alpha, beta], rtol=RTOL
    )
    r, gamma, beta, _ = HydroErr.kge_2012(s, o, return_all=True)
    comp = hm.kge_components(obs, sim, version="2012").value
    np.testing.assert_allclose(
        [float(comp["r"]), float(comp["gamma"]), float(comp["beta"])], [r, gamma, beta], rtol=RTOL
    )
