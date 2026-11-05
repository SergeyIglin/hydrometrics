"""Cross-check against ``scoringrules``: ensemble CRPS (classical and fair), Brier score.

Conventions read from the installed ``scoringrules/_crps.py`` and
``scoringrules/core/crps/_approx.py``:

* ``crps_ensemble(obs, fct, estimator=...)``, members on the last axis; the default
  estimator is ``"qd"`` (quantile decomposition), which is algebraically the CLASSICAL
  estimator ``mean|X - y| - 0.5 * sum|X_j - X_k| / m**2``; ``"nrg"`` is the same
  formula written directly; ``"fair"`` divides the spread term by ``m (m - 1)``
  (Ferro 2014); ``"pwm"`` is algebraically the fair estimator;
* library ``crps(fair=False)`` <-> ``"nrg"`` / ``"qd"``; ``crps(fair=True)`` <->
  ``"fair"`` / ``"pwm"``;
* the result is a per-observation score; the library averages it over the valid
  observations (with ``weight`` as observation weights), the reference does the same here;
* ``nan_policy="omit"`` drops NaN members (``nrg``, ``fair``, ``qd``, ``pwm``); a NaN
  observation gives NaN, so such observations are removed before the call;
* ``ens_w`` are MEMBER weights, not observation weights: not comparable with the
  library ``weight``.
* ``brier_score(obs, fct)`` is the per-observation ``(fct - obs)**2``.
"""
import numpy as np
import pytest

sr = pytest.importorskip("scoringrules")

from crosscheck_data import ALL, ATOL, RTOL, get_ensemble, get_events, lib_value  # noqa: E402

CRPS_VARIANTS = ["clean", "nan", "weighted", "weighted_nan", "2d", "2d_nan", "2d_weighted_nan"]


def _reference_crps(obs, members, w, estimator):
    out = []
    ocols = obs if obs.ndim == 2 else obs[:, None]
    mcols = members if members.ndim == 3 else members[:, None, :]
    wcols = None if w is None else (w if w.ndim == 2 else w[:, None])
    for j in range(ocols.shape[1]):
        valid = ~np.isnan(ocols[:, j])
        score = sr.crps_ensemble(
            ocols[valid, j], mcols[valid, j, :], estimator=estimator, nan_policy="omit"
        )
        out.append(np.average(score, weights=None if wcols is None else wcols[valid, j]))
    return np.array(out)


@pytest.mark.parametrize("variant", CRPS_VARIANTS)
@pytest.mark.parametrize(
    "fair, estimator",
    [(False, "nrg"), (False, "qd"), (True, "fair"), (True, "pwm")],
)
def test_crps(fair, estimator, variant):
    obs, members, w = get_ensemble(variant)
    got = lib_value("crps", obs, members, w, fair=fair)
    ref = _reference_crps(obs, members, w, estimator)
    np.testing.assert_allclose(got, ref, rtol=1e-8, atol=1e-10)


def test_fair_is_smaller_than_classical():
    obs, members, _ = get_ensemble("clean")
    classical = lib_value("crps", obs, members, fair=False)[0]
    fair = lib_value("crps", obs, members, fair=True)[0]
    assert fair < classical


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
        score = np.asarray(sr.brier_score(ocols[valid, j], pcols[valid, j]))
        ref.append(np.average(score, weights=None if wcols is None else wcols[valid, j]))
    np.testing.assert_allclose(got, np.array(ref), rtol=RTOL, atol=ATOL)
