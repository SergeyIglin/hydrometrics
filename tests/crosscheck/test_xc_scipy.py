"""Cross-check of the rank correlations against ``scipy.stats`` and ``pandas``.

Conventions read from the installed ``scipy/stats/_stats_py.py``:

* ``spearmanr`` is the Pearson correlation of average ranks (ties get mean ranks);
* ``kendalltau`` has ``variant='b'`` by default (tau-b: ties are corrected in the
  denominator); the library calls it with the defaults, so it is tau-b, NOT tau-a;
* ``nan_policy='propagate'`` by default: the pairs are removed here explicitly.

The library calls ``scipy.stats`` itself, so the main comparison uses an independent
implementation: ``pandas.Series.corr`` (Spearman by ranks, Kendall = tau-b) and a direct
O(n^2) count for tau-a / tau-b on a series with ties.
"""
import numpy as np
import pytest

stats = pytest.importorskip("scipy.stats")

from crosscheck_data import ATOL, RTOL, UNWEIGHTED, columns, get_variant, lib_value  # noqa: E402


@pytest.mark.parametrize("variant", UNWEIGHTED)
def test_spearman(variant):
    obs, sim, _ = get_variant(variant)
    got = lib_value("spearman_r", obs, sim)
    ref = np.array([stats.spearmanr(o, s).correlation for o, s in columns(obs, sim)])
    np.testing.assert_allclose(got, ref, rtol=RTOL, atol=ATOL)


@pytest.mark.parametrize("variant", UNWEIGHTED)
def test_kendall(variant):
    obs, sim, _ = get_variant(variant)
    got = lib_value("kendall_tau", obs, sim)
    ref = np.array([stats.kendalltau(o, s).correlation for o, s in columns(obs, sim)])
    np.testing.assert_allclose(got, ref, rtol=RTOL, atol=ATOL)


@pytest.mark.parametrize("variant", UNWEIGHTED)
def test_against_pandas(variant):
    pd = pytest.importorskip("pandas")
    obs, sim, _ = get_variant(variant)
    for name, method in (("spearman_r", "spearman"), ("kendall_tau", "kendall")):
        got = lib_value(name, obs, sim)
        ref = np.array(
            [pd.Series(o).corr(pd.Series(s), method=method) for o, s in columns(obs, sim)]
        )
        np.testing.assert_allclose(got, ref, rtol=1e-8, atol=1e-10)


def _tau_counts(x, y):
    n = len(x)
    dx = np.sign(x[:, None] - x[None, :])
    dy = np.sign(y[:, None] - y[None, :])
    prod = dx * dy
    iu = np.triu_indices(n, 1)
    concordant = np.sum(prod[iu] > 0)
    discordant = np.sum(prod[iu] < 0)
    n0 = n * (n - 1) / 2
    n1 = np.sum(dx[iu] == 0)
    n2 = np.sum(dy[iu] == 0)
    return concordant, discordant, n0, n1, n2


def test_kendall_with_ties_is_tau_b_not_tau_a():
    obs, sim, _ = get_variant("clean")
    o = np.round(obs[:400] / 5.0)  # strong ties
    s = np.round(sim[:400] / 5.0)
    c, d, n0, n1, n2 = _tau_counts(o, s)
    tau_a = (c - d) / n0
    tau_b = (c - d) / np.sqrt((n0 - n1) * (n0 - n2))
    ours = float(lib_value("kendall_tau", o, s)[0])
    np.testing.assert_allclose(ours, tau_b, rtol=1e-9)
    assert abs(ours - tau_a) > 1e-3
