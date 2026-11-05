"""Cross-check against ``scikit-learn``.

Conventions read from the installed ``sklearn/metrics``:

* ``r2_score(y_true, y_pred)`` is the COEFFICIENT OF DETERMINATION
  ``1 - SS_res / SS_tot`` (not the squared correlation) and takes ``sample_weight``;
  it therefore equals the library ``r2`` and also ``nse``;
* ``root_mean_squared_error`` / ``mean_absolute_error``: weighted means, argument order
  ``(y_true, y_pred)``;
* ``average_precision_score`` is the UNINTERPOLATED STEP sum
  ``sum (R_n - R_{n-1}) P_n`` (the docstring says it differs from the trapezoidal
  area); the library ``pr_auc`` is the same step sum, not ``auc(recall, precision)``;
* ``roc_auc_score`` is the trapezoidal area of the ROC curve, which equals the
  Mann-Whitney statistic with tied scores counted 1/2 (the library uses average ranks);
* ``brier_score_loss`` is the mean of ``(p - o)**2`` for a binary problem
  (``scale_by_half="auto"`` compensates the two-column sum), weights supported;
* ``accuracy_score`` / ``precision_score`` / ``recall_score`` / ``f1_score`` take
  ``sample_weight`` and ``pos_label=1``; no NaN handling (the pairs are removed here).
"""
import numpy as np
import pytest

pytest.importorskip("sklearn")
from sklearn import metrics as skm  # noqa: E402

from crosscheck_data import (  # noqa: E402
    ALL,
    ATOL,
    RTOL,
    UNWEIGHTED,
    columns,
    get_events,
    get_variant,
    lib_value,
)

REGRESSION = {
    "r2": lambda o, s, w: skm.r2_score(o, s, sample_weight=w),
    "nse": lambda o, s, w: skm.r2_score(o, s, sample_weight=w),
    "rmse": lambda o, s, w: skm.root_mean_squared_error(o, s, sample_weight=w),
    "mae": lambda o, s, w: skm.mean_absolute_error(o, s, sample_weight=w),
}


@pytest.mark.parametrize("variant", ALL)
@pytest.mark.parametrize("name", list(REGRESSION))
def test_regression(name, variant):
    obs, sim, w = get_variant(variant)
    got = lib_value(name, obs, sim, w)
    ref = np.array([REGRESSION[name](o, s, wc) for o, s, wc in columns(obs, sim, w)])
    np.testing.assert_allclose(got, ref, rtol=RTOL, atol=ATOL)


CLASSIFICATION = {
    "accuracy": lambda o, s, w: skm.accuracy_score(o, s, sample_weight=w),
    "precision": lambda o, s, w: skm.precision_score(o, s, sample_weight=w, zero_division=np.nan),
    "recall": lambda o, s, w: skm.recall_score(o, s, sample_weight=w, zero_division=np.nan),
    "f1_score": lambda o, s, w: skm.f1_score(o, s, sample_weight=w, zero_division=np.nan),
}


@pytest.mark.parametrize("variant", ALL)
@pytest.mark.parametrize("name", list(CLASSIFICATION))
def test_classification(name, variant):
    eo, es, _, w = get_events(variant)
    got = lib_value(name, eo, es, w)
    ref = np.array([CLASSIFICATION[name](o, s, wc) for o, s, wc in columns(eo, es, w)])
    np.testing.assert_allclose(got, ref, rtol=RTOL, atol=ATOL)


@pytest.mark.parametrize("variant", ALL)
def test_brier_score(variant):
    eo, _, p, w = get_events(variant)
    got = lib_value("brier_score", eo, p, w)
    ref = np.array(
        [skm.brier_score_loss(o, pp, sample_weight=wc) for o, pp, wc in columns(eo, p, w)]
    )
    np.testing.assert_allclose(got, ref, rtol=RTOL, atol=ATOL)


@pytest.mark.parametrize("variant", UNWEIGHTED)
def test_roc_auc(variant):
    eo, _, p, _ = get_events(variant)
    got = lib_value("roc_auc", eo, p)
    ref = np.array([skm.roc_auc_score(o, pp) for o, pp, _ in columns(eo, p, None)])
    np.testing.assert_allclose(got, ref, rtol=RTOL, atol=ATOL)


@pytest.mark.parametrize("variant", UNWEIGHTED)
def test_pr_auc_is_average_precision(variant):
    eo, _, p, _ = get_events(variant)
    got = lib_value("pr_auc", eo, p)
    ref = np.array([skm.average_precision_score(o, pp) for o, pp, _ in columns(eo, p, None)])
    np.testing.assert_allclose(got, ref, rtol=RTOL, atol=ATOL)


def test_pr_auc_is_not_trapezoidal_area():
    """Convention: step sum (average precision), not ``auc(recall, precision)``."""
    eo, _, p, _ = get_events("clean")
    ((o, pp),) = list(columns(eo, p))
    precision, recall, _ = skm.precision_recall_curve(o, pp)
    trapezoid = skm.auc(recall, precision)
    ours = float(lib_value("pr_auc", eo, p)[0])
    assert abs(ours - trapezoid) > 1e-4
