"""Cross-check against ``hydroeval``: NSE, KGE (2009), KGE' (2012), PBIAS, RMSE.

Conventions read from the installed ``hydroeval/objective_functions.py``:

* signature ``f(simulations, evaluation)`` (sim first);
* ``kge`` returns ``vstack(kge, r, alpha, beta)``, ``kgeprime`` returns
  ``vstack(kge', r, gamma, beta)``; std with ``ddof=0`` (cancels in the ratios);
* ``pbias = 100 * sum(obs - sim) / sum(obs)``: the sign is OPPOSITE to the library
  (library: ``100 * sum(sim - obs) / sum(obs)``), so the library value equals ``-pbias``;
* no weights; NaN is not handled by the objective functions (the pairs are removed here).
"""
import numpy as np
import pytest

he = pytest.importorskip("hydroeval")

import hydrometrics as hm  # noqa: E402
from crosscheck_data import ATOL, RTOL, UNWEIGHTED, columns, get_variant, lib_value  # noqa: E402

# library name -> (hydroeval function, sign that converts hydroeval to the library convention)
PAIRS = {
    "nse": (he.nse, 1.0),
    "kge_2009": (he.kge, 1.0),
    "kge_2012": (he.kgeprime, 1.0),
    "pbias": (he.pbias, -1.0),
    "rmse": (he.rmse, 1.0),
}


@pytest.mark.parametrize("variant", UNWEIGHTED)
@pytest.mark.parametrize("name", list(PAIRS))
def test_against_hydroeval(name, variant):
    obs, sim, _ = get_variant(variant)
    fn, sign = PAIRS[name]
    got = lib_value(name, obs, sim)
    ref = np.array([sign * np.ravel(fn(s, o))[0] for o, s in columns(obs, sim)])
    np.testing.assert_allclose(got, ref, rtol=RTOL, atol=ATOL)


def test_pbias_sign_is_opposite():
    obs, sim, _ = get_variant("clean")
    ours = float(hm.pbias(obs, sim).value)
    theirs = float(np.ravel(he.pbias(sim, obs))[0])
    assert ours != 0.0
    assert np.sign(ours) == -np.sign(theirs)
    np.testing.assert_allclose(ours, -theirs, rtol=RTOL)


@pytest.mark.parametrize("variant", ["clean", "nan"])
def test_kge_components(variant):
    obs, sim, _ = get_variant(variant)
    ((o, s),) = list(columns(obs, sim))
    ref = np.ravel(he.kge(s, o)).tolist()  # kge, r, alpha, beta
    comp = hm.kge_components(obs, sim, version="2009").value
    np.testing.assert_allclose(
        [float(comp["r"]), float(comp["alpha"]), float(comp["beta"])], ref[1:], rtol=RTOL
    )
    ref12 = np.ravel(he.kgeprime(s, o)).tolist()  # kge', r, gamma, beta
    comp12 = hm.kge_components(obs, sim, version="2012").value
    np.testing.assert_allclose(
        [float(comp12["r"]), float(comp12["gamma"]), float(comp12["beta"])], ref12[1:], rtol=RTOL
    )
