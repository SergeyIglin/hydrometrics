"""Cross-check against ``properscoring``: ensemble CRPS and Brier score.

Conventions read from the installed ``properscoring/_crps.py``, ``_gufuncs.py``,
``_brier.py``:

* ``crps_ensemble(observations, forecasts, weights=None, axis=-1)`` integrates the
  squared difference between the empirical CDF of the members and the step function of
  the observation EXACTLY; for equal member weights this is the CLASSICAL estimator
  (spread term divided by ``m**2``), i.e. library ``crps(fair=False)``. There is no
  fair option; the fair value differs by the factor ``m / (m - 1)`` in the spread term;
* NaN members are ignored (the ensemble size becomes the number of valid members);
  a NaN observation gives NaN, so such observations are removed before the call;
* ``weights`` are MEMBER weights (probabilities of the members), not observation
  weights; with equal weights the result is unchanged;
* ``brier_score(observations, forecasts)`` is the per-observation ``(f - o)**2`` and
  raises for ``f`` outside [0, 1] or ``o`` other than 0, 1, NaN.
"""
import numpy as np
import pytest

ps = pytest.importorskip("properscoring")

from crosscheck_data import ALL, ATOL, RTOL, get_ensemble, get_events, lib_value  # noqa: E402

CRPS_VARIANTS = ["clean", "nan", "weighted", "weighted_nan", "2d", "2d_nan", "2d_weighted_nan"]


def _reference(obs, members, w, **kwargs):
    ocols = obs if obs.ndim == 2 else obs[:, None]
    mcols = members if members.ndim == 3 else members[:, None, :]
    wcols = None if w is None else (w if w.ndim == 2 else w[:, None])
    out = []
    for j in range(ocols.shape[1]):
        valid = ~np.isnan(ocols[:, j])
        score = ps.crps_ensemble(ocols[valid, j], mcols[valid, j, :], **kwargs)
        out.append(np.average(score, weights=None if wcols is None else wcols[valid, j]))
    return np.array(out)


@pytest.mark.parametrize("variant", CRPS_VARIANTS)
def test_crps_is_classical(variant):
    obs, members, w = get_ensemble(variant)
    got = lib_value("crps", obs, members, w, fair=False)
    np.testing.assert_allclose(got, _reference(obs, members, w), rtol=1e-8, atol=1e-10)


def test_crps_is_not_fair():
    obs, members, w = get_ensemble("clean")
    fair = lib_value("crps", obs, members, w, fair=True)
    assert not np.allclose(fair, _reference(obs, members, w), rtol=1e-6)


def test_crps_equal_member_weights_unchanged():
    obs, members, _ = get_ensemble("clean")
    plain = ps.crps_ensemble(obs, members)
    weighted = ps.crps_ensemble(obs, members, weights=np.ones_like(members))
    np.testing.assert_allclose(plain, weighted, rtol=1e-12)


@pytest.mark.parametrize("variant", ALL)
def test_brier_score(variant):
    eo, _, p, w = get_events(variant)
    got = lib_value("brier_score", eo, p, w)
    ocols = eo if eo.ndim == 2 else eo[:, None]
    pcols = p if p.ndim == 2 else p[:, None]
    wcols = None if w is None else (w if w.ndim == 2 else w[:, None])
    ref = []
    for j in range(ocols.shape[1]):
        valid = ~(np.isnan(ocols[:, j]) | np.isnan(pcols[:, j]))
        score = ps.brier_score(ocols[valid, j], pcols[valid, j])
        ref.append(np.average(score, weights=None if wcols is None else wcols[valid, j]))
    np.testing.assert_allclose(got, np.array(ref), rtol=RTOL, atol=ATOL)
