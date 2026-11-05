"""
Classification metrics for HydroMetrics.

Includes Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, EDI, SEDI.
"""

from __future__ import annotations

from typing import Literal
import numpy as np

from hydrometrics.core.base import metric
from hydrometrics.backends.numpy import (
    _accuracy_core,
    _precision_core,
    _recall_core,
    _f1_score_core,
    _roc_auc_core,
    _pr_auc_core,
    _edi_core,
    _sedi_core,
)


# ============================================================================
# Classification Metrics
# ============================================================================


@metric(
    name="Accuracy",
    direction="maximize",
    bounds=(0.0, 1.0),
    reference="Standard metric",
    description="Overall classification accuracy: fraction of correct predictions.",
    formula=r"\frac{TP + TN}{TP + TN + FP + FN}",
)
def accuracy(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Classification Accuracy.

    Parameters
    ----------
    obs : array-like
        True class labels (integers).
    sim : array-like
        Predicted class labels (integers).
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        Accuracy value.
    """
    return _accuracy_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Precision",
    direction="maximize",
    bounds=(0.0, 1.0),
    reference="Standard metric",
    description="Precision (Positive Predictive Value): fraction of positive predictions that are correct.",
    formula=r"\frac{TP}{TP + FP}",
)
def precision(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    positive_class: int = 1,
) -> float | np.ndarray:
    """
    Precision for binary classification.

    Parameters
    ----------
    obs : array-like
        True binary labels (0 or 1).
    sim : array-like
        Predicted binary labels (0 or 1).
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.
    positive_class : int, default=1
        Class label considered as positive.

    Returns
    -------
    float or ndarray
        Precision value.
    """
    return _precision_core(obs, sim, weight=weight, axis=axis, reduction=reduction, positive_class=positive_class)


@metric(
    name="Recall (Sensitivity)",
    direction="maximize",
    bounds=(0.0, 1.0),
    reference="Standard metric",
    description="Recall (Sensitivity, True Positive Rate): fraction of actual positives correctly identified.",
    formula=r"\frac{TP}{TP + FN}",
)
def recall(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    positive_class: int = 1,
) -> float | np.ndarray:
    """
    Recall (Sensitivity) for binary classification.

    Parameters
    ----------
    obs : array-like
        True binary labels (0 or 1).
    sim : array-like
        Predicted binary labels (0 or 1).
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.
    positive_class : int, default=1
        Class label considered as positive.

    Returns
    -------
    float or ndarray
        Recall value.
    """
    return _recall_core(obs, sim, weight=weight, axis=axis, reduction=reduction, positive_class=positive_class)


@metric(
    name="F1 Score",
    direction="maximize",
    bounds=(0.0, 1.0),
    reference="Standard metric",
    description="F1 Score: harmonic mean of precision and recall.",
    formula=r"2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}",
)
def f1_score(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    positive_class: int = 1,
) -> float | np.ndarray:
    """
    F1 Score for binary classification.

    Parameters
    ----------
    obs : array-like
        True binary labels (0 or 1).
    sim : array-like
        Predicted binary labels (0 or 1).
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.
    positive_class : int, default=1
        Class label considered as positive.

    Returns
    -------
    float or ndarray
        F1 Score value.
    """
    return _f1_score_core(obs, sim, weight=weight, axis=axis, reduction=reduction, positive_class=positive_class)


@metric(
    name="ROC AUC",
    direction="maximize",
    bounds=(0.0, 1.0),
    reference="Standard metric",
    description="Area Under the Receiver Operating Characteristic Curve. Measures ability to rank positive samples higher than negative samples.",
    formula=r"\int_0^1 \text{TPR}(FPR) dFPR",
    supports_weight=False,
)
def roc_auc(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    ROC AUC for binary classification.

    Parameters
    ----------
    obs : array-like
        True binary labels (0 or 1).
    sim : array-like
        Predicted probabilities or scores for positive class.
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        ROC AUC value.

    References
    ----------
    - Fawcett (2006), DOI: 10.1016/j.patrec.2005.10.010
    """
    return _roc_auc_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="PR AUC (Average Precision)",
    direction="maximize",
    bounds=(0.0, 1.0),
    reference="Standard metric",
    description="Area Under the Precision-Recall Curve (Average Precision). More informative than ROC AUC for imbalanced datasets.",
    formula=r"\int_0^1 \text{Precision}(Recall) dRecall",
    supports_weight=False,
)
def pr_auc(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    PR AUC (Average Precision) for binary classification.

    Parameters
    ----------
    obs : array-like
        True binary labels (0 or 1).
    sim : array-like
        Predicted probabilities or scores for positive class.
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        PR AUC value.

    References
    ----------
    - Davis & Goadrich (2006), DOI: 10.1145/1143844.1143874
    """
    return _pr_auc_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Extremal Dependence Index (EDI)",
    direction="maximize",
    bounds=(-1.0, 1.0),
    reference="Ferro & Stephenson (2011), DOI: 10.1175/WAF-D-10-05030.1",
    description=(
        "Extremal Dependence Index. Non-degenerating skill measure for "
        "deterministic forecasts of rare binary events. Base-rate independent, "
        "regular, asymptotically equitable, hard to hedge. "
        "Should be computed on recalibrated forecasts. "
        "EDI=1 perfect, EDI=0 random (no skill), EDI<0 worse than random."
    ),
    formula=r"\frac{\log F - \log H}{\log F + \log H}",
)
def edi(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Extremal Dependence Index (EDI).

    Parameters
    ----------
    obs : array-like
        True binary labels (0 or 1).
    sim : array-like
        Predicted binary labels (0 or 1).
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        EDI value in [-1, 1].

    Notes
    -----
    H = TP / (TP + FN)  -- hit rate
    F = FP / (FP + TN)  -- false alarm rate
    EDI = (log F - log H) / (log F + log H)

    A perfect forecast (H = 1 and F = 0) is defined to give 1. In the other cases
    with H = 0 or F = 0 the result is NaN, because a logarithm of 0 appears. For
    H = 1 and 0 < F < 1, log H = 0 and EDI equals 1. The definition at H = 1,
    F = 0 is a decision of the library author; the source text could not be
    checked. Pairs with a missing value count in none of the four cells.

    References
    ----------
    Ferro, C. A. T., & Stephenson, D. B. (2011).
    Extremal Dependence Indices: Improved Verification Measures for
    Deterministic Forecasts of Rare Binary Events.
    Weather and Forecasting, 26(5), 699-713.
    DOI: 10.1175/WAF-D-10-05030.1
    """
    return _edi_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Symmetric Extremal Dependence Index (SEDI)",
    direction="maximize",
    bounds=(-1.0, 1.0),
    reference="Ferro & Stephenson (2011), DOI: 10.1175/WAF-D-10-05030.1",
    description="Symmetric Extremal Dependence Index (SEDI). Non-degenerate measure for rare event forecasting. Range: -1 to 1. SEDI=1 perfect, SEDI=0 no skill, SEDI=-1 perfectly wrong. Suitable for rare events (base rate -> 0).",
    formula=r"\frac{\log(POD) - \log(POFD) - \log(1-POD) + \log(1-POFD)}{\log(POD) + \log(POFD) + \log(1-POD) + \log(1-POFD)}",
)
def sedi(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Symmetric Extremal Dependence Index (SEDI).

    Parameters
    ----------
    obs : array-like
        True binary labels (0 or 1).
    sim : array-like
        Predicted binary labels (0 or 1).
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        SEDI value.

    Notes
    -----
    With the hit rate H = TP / (TP + FN) and the false alarm rate F = FP / (FP + TN),
    a perfect forecast (H = 1 and F = 0) is defined to give 1. In the other cases with
    H or F equal to 0 or 1 the result is NaN, because a logarithm of 0 appears. The
    definition at H = 1, F = 0 is a decision of the library author; the source text
    could not be checked.

    References
    ----------
    - Ferro & Stephenson (2011), DOI: 10.1175/WAF-D-10-05030.1
    """
    return _sedi_core(obs, sim, weight=weight, axis=axis, reduction=reduction)
