"""
Regression metrics for HydroMetrics.

Includes MAE, MSE, RMSE, NRMSE, Bias, PBIAS, R2, correlations, and Willmott's d.
"""

from __future__ import annotations

from typing import Literal
import numpy as np

from hydrometrics.core.base import metric
from hydrometrics.backends.numpy import (
    _mae_core,
    _mse_core,
    _rmse_core,
    _nrmse_core,
    _bias_core,
    _pbias_core,
    _r2_core,
    _pearson_r_core,
    _spearman_r_core,
    _kendall_tau_core,
    _willmott_d_core,
)


# ============================================================================
# Regression Metrics
# ============================================================================


@metric(
    name="Mean Absolute Error",
    direction="minimize",
    bounds=(0.0, None),
    reference="Standard metric",
    description="Mean absolute difference between observed and simulated values.",
    formula=r"\frac{1}{n}\sum_{i=1}^n |y_i - \hat{y}_i|",
)
def mae(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Mean Absolute Error (MAE).

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values.
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        MAE value.

    References
    ----------
    - Willmott & Matsuura (2005), DOI: 10.3354/cr030079
    """
    return _mae_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Mean Squared Error",
    direction="minimize",
    bounds=(0.0, None),
    reference="Standard metric",
    description="Mean squared difference between observed and simulated values.",
    formula=r"\frac{1}{n}\sum_{i=1}^n (y_i - \hat{y}_i)^2",
)
def mse(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Mean Squared Error (MSE).

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values.
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        MSE value.
    """
    return _mse_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Root Mean Squared Error",
    direction="minimize",
    bounds=(0.0, None),
    reference="Standard metric",
    description="Square root of mean squared error.",
    formula=r"\sqrt{\frac{1}{n}\sum_{i=1}^n (y_i - \hat{y}_i)^2}",
)
def rmse(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Root Mean Squared Error (RMSE).

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values.
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        RMSE value.
    """
    return _rmse_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Normalized Root Mean Squared Error",
    direction="minimize",
    bounds=(0.0, None),
    reference="Standard metric",
    description="RMSE normalized by a reference value (mean, std, range, or IQR of observations).",
    formula=r"\frac{RMSE}{\text{norm}}",
)
def nrmse(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    normalization: Literal["mean", "std", "range", "iqr"] = "mean",
) -> float | np.ndarray:
    """
    Normalized Root Mean Squared Error (NRMSE).

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values.
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.
    normalization : {"mean", "std", "range", "iqr"}, default="mean"
        Normalization method:
        - "mean": divide by mean of observations
        - "std": divide by standard deviation of observations
        - "range": divide by range (max - min) of observations
        - "iqr": divide by interquartile range of observations

    Returns
    -------
    float or ndarray
        NRMSE value.
    """
    return _nrmse_core(
        obs, sim, weight=weight, axis=axis, reduction=reduction, normalization=normalization
    )


@metric(
    name="Bias",
    direction="target",
    bounds=(None, None),
    reference="Standard metric",
    description="Mean error (simulated - observed). Negative values indicate underestimation.",
    formula=r"\frac{1}{n}\sum_{i=1}^n (\hat{y}_i - y_i)",
    optimum=0.0,
)
def bias(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Bias (Mean Error).

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values.
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        Bias value.
    """
    return _bias_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Percent Bias",
    direction="target",
    bounds=(None, None),
    reference="Standard metric",
    description="Percent bias relative to the observed total: 100 * sum(sim - obs) / sum(obs). Positive values mean overestimation.",
    formula=r"100 \cdot \frac{\sum_{i=1}^n (\hat{y}_i - y_i)}{\sum_{i=1}^n y_i}",
    optimum=0.0,
)
def pbias(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Percent Bias (PBIAS).

    PBIAS = 100 * sum(sim - obs) / sum(obs). A positive value means overestimation
    by the model, consistent with ``bias = sim - obs``.

    .. note::
       The sign is opposite to the definition of Moriasi et al. (2007), who use
       ``obs - sim`` (citing Gupta et al., 1999), so that a positive value there means
       underestimation. The magnitude is the same; the rating thresholds of Moriasi et
       al. apply to ``abs(pbias)``.

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values.
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        PBIAS value in percent.

    References
    ----------
    - Gupta et al. (1999), DOI: 10.1061/(ASCE)1084-0699(1999)4:2(135)
    - Moriasi et al. (2007), DOI: 10.13031/2013.23153
    """
    return _pbias_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="R-squared",
    direction="maximize",
    bounds=(-np.inf, 1.0),
    reference="Standard metric",
    description="Coefficient of determination. Measures proportion of variance explained.",
    formula=r"1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}",
)
def r2(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Coefficient of Determination (R²).

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values.
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        R² value.
    """
    return _r2_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Pearson Correlation",
    direction="maximize",
    bounds=(-1.0, 1.0),
    reference="Standard metric",
    description="Pearson product-moment correlation coefficient.",
    formula=r"\frac{\text{cov}(y, \hat{y})}{\sigma_y \sigma_{\hat{y}}}",
)
def pearson_r(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Pearson Correlation Coefficient.

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values.
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        Pearson r value.
    """
    return _pearson_r_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Spearman Correlation",
    direction="maximize",
    bounds=(-1.0, 1.0),
    reference="Standard metric",
    description="Spearman rank correlation coefficient.",
    formula=r"\rho(\text{rank}(y), \text{rank}(\hat{y}))",
    supports_weight=False,
)
def spearman_r(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Spearman Rank Correlation.

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values.
    weight : array-like, optional
        Sample weights (currently ignored for Spearman).
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        Spearman rho value.
    """
    return _spearman_r_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Kendall's Tau",
    direction="maximize",
    bounds=(-1.0, 1.0),
    reference="Standard metric",
    description="Kendall's tau rank correlation coefficient.",
    formula=r"\tau",
    supports_weight=False,
)
def kendall_tau(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Kendall's Tau Rank Correlation.

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values.
    weight : array-like, optional
        Sample weights (currently ignored for Kendall).
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        Kendall's tau value.
    """
    return _kendall_tau_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Willmott's Index of Agreement",
    direction="maximize",
    bounds=(0.0, 1.0),
    reference="Willmott (1981), DOI: 10.1080/02723646.1981.10642213",
    description="Willmott's index of agreement (d). Bounded between 0 and 1.",
    formula=r"1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(|\hat{y}_i - \bar{y}| + |y_i - \bar{y}|)^2}",
)
def willmott_d(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Willmott's Index of Agreement (d).

    Implements the original index of Willmott (1981),
    ``d = 1 - sum((O - P)^2) / sum((|P - mean(O)| + |O - mean(O)|)^2)``. With weights, the
    sums and the observed mean are weighted. Modified and refined variants of the index,
    including the refined index of Willmott et al. (2012), are not implemented.

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Simulated values.
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        Willmott's d value.

    References
    ----------
    - Willmott (1981), DOI: 10.1080/02723646.1981.10642213
    - Willmott et al. (2012), DOI: 10.1002/joc.2419
    """
    return _willmott_d_core(obs, sim, weight=weight, axis=axis, reduction=reduction)
