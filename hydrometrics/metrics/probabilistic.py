"""
Probabilistic metrics for HydroMetrics.

Includes CRPS, Weighted CRPS, CRPSS, Brier Score, Reliability, Sharpness.
"""

from __future__ import annotations

from typing import Any, Literal
import numpy as np

from hydrometrics.core.base import metric
from hydrometrics.backends.numpy import (
    _crps_core,
    _weighted_crps_core,
    _crpss_core,
    _brier_score_core,
    _reliability_core,
    _sharpness_core,
)


# ============================================================================
# Probabilistic Metrics
# ============================================================================


@metric(
    name="Continuous Ranked Probability Score",
    direction="minimize",
    bounds=(0.0, None),
    reference="Hersbach (2000), DOI: 10.1175/1520-0434(2000)015<0559:DOTCRP>2.0.CO;2",
    description="Continuous Ranked Probability Score (CRPS). For deterministic forecasts, reduces to MAE. For ensemble forecasts, measures the integrated squared difference between the forecast CDF and the observation step function.",
    formula=r"\int_{-\infty}^{\infty} (F_{\text{forecast}}(y) - F_{\text{obs}}(y))^2 dy",
)
def crps(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    fair: bool = False,
) -> float | np.ndarray:
    """
    Continuous Ranked Probability Score (CRPS).

    Parameters
    ----------
    obs : array-like
        Observed values, shape (n_samples,) or (n_samples, n_stations, ...).
    sim : array-like
        Forecast values. Deterministic forecast: same shape as ``obs``; the score is
        the absolute error. Ensemble forecast: ``obs.shape + (n_members,)``, members
        on the last axis.
    weight : array-like, optional
        Weights of the observations, same shape as ``obs``. Used for both
        deterministic and ensemble forecasts.
    axis : int, optional
        Axis of ``obs`` along which the per-observation scores are averaged.
        ``None`` averages over all observations.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy. For an ensemble with ``axis=None``, ``"none"`` returns
        the score of every observation.
    fair : bool, default=False
        Ensemble forecasts only. ``False`` is the classical estimator,
        ``mean_j |X_j - o| - 0.5 * sum_jk |X_j - X_k| / m**2``.
        ``True`` is the fair estimator named in Ferro (2014), which divides the
        spread term by m(m - 1) instead of m**2. For m members the fair value is
        smaller than the classical one.

    Returns
    -------
    float or ndarray
        CRPS value, in the units of ``obs``.

    Raises
    ------
    ValueError
        If ``sim`` is neither shaped like ``obs`` nor ``obs.shape + (n_members,)``.

    Notes
    -----
    Both estimators are non-negative, so ``bounds=(0, None)`` holds for
    ``fair=False`` and ``fair=True``: by the triangle inequality the spread term
    never exceeds the mean absolute error of the members. The default changed from
    the fair to the classical estimator.

    References
    ----------
    - Hersbach (2000), DOI: 10.1175/1520-0434(2000)015<0559:DOTCRP>2.0.CO;2
    - Gneiting & Raftery (2007), DOI: 10.1198/016214506000001437
    - Ferro (2014), DOI: 10.1002/qj.2270
    """
    return _crps_core(obs, sim, weight=weight, axis=axis, reduction=reduction, fair=fair)


@metric(
    name="Weighted Continuous Ranked Probability Score",
    direction="minimize",
    bounds=(0.0, None),
    reference="Gneiting & Ranjan (2011), DOI: 10.1198/jbes.2010.08110",
    description="Mean of the per-observation CRPS weighted by a user-defined function of the observations (e.g. 1/y to emphasise low flows). It weights observations, not the integrand of the CRPS.",
    formula=r"\frac{\sum_i w(y_i)\,\mathrm{CRPS}_i}{\sum_i w(y_i)}",
)
def weighted_crps(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    weight_func: Any | None = None,
) -> float | np.ndarray:
    """
    Weighted Continuous Ranked Probability Score (Weighted CRPS).

    The classical CRPS of every observation is averaged with the weights
    ``weight_func(obs) * weight``. This weights observations, not the integrand of
    the CRPS as Gneiting & Ranjan (2011) do for threshold- and quantile-weighted
    scores.

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Forecast values: same shape as ``obs`` (deterministic) or
        ``obs.shape + (n_members,)`` (ensemble).
    weight : array-like, optional
        Weights of the observations, multiplied with ``weight_func(obs)``.
    axis : int, optional
        Axis of ``obs`` along which the weighted mean is taken.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.
    weight_func : callable, optional
        Weight function w(y) applied to observations.
        Default: uniform weight (standard CRPS).
        Examples: lambda y: 1/y for emphasizing low flows,
        lambda y: y for emphasizing high flows.

    Returns
    -------
    float or ndarray
        Weighted CRPS value.

    Raises
    ------
    ValueError
        If ``sim`` is neither shaped like ``obs`` nor ``obs.shape + (n_members,)``.

    References
    ----------
    - Gneiting & Ranjan (2011), DOI: 10.1198/jbes.2010.08110
    """
    return _weighted_crps_core(
        obs, sim, weight=weight, axis=axis, reduction=reduction, weight_func=weight_func
    )


@metric(
    name="Continuous Ranked Probability Skill Score",
    direction="maximize",
    bounds=(-np.inf, 1.0),
    reference="Standard metric",
    description="CRP Skill Score relative to a reference forecast. CRPSS = 1 - CRPS / CRPS_ref. CRPSS=1 is perfect, CRPSS=0 is equal to reference, CRPSS<0 is worse.",
    formula=r"1 - \frac{CRPS}{CRPS_{ref}}",
)
def crpss(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    ref_forecast: np.ndarray | None = None,
) -> float | np.ndarray:
    """
    Continuous Ranked Probability Skill Score (CRPSS).

    CRPSS = 1 - mean(CRPS) / mean(CRPS_ref): the ratio of the means over ``axis``,
    not the mean of per-observation ratios. Both scores use the classical
    estimator of :func:`crps`.

    Parameters
    ----------
    obs : array-like
        Observed values.
    sim : array-like
        Forecast values: same shape as ``obs`` or ``obs.shape + (n_members,)``.
    weight : array-like, optional
        Weights of the observations, applied to both means.
    axis : int, optional
        Axis of ``obs`` along which the means are taken.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.
    ref_forecast : array-like, optional
        Reference forecast for skill score, deterministic or an ensemble.
        If None, the (weighted) mean of the observations is the deterministic
        reference.

    Returns
    -------
    float or ndarray
        CRPSS value.
    """
    return _crpss_core(obs, sim, weight=weight, axis=axis, reduction=reduction, ref_forecast=ref_forecast)


@metric(
    name="Brier Score",
    direction="minimize",
    bounds=(0.0, 1.0),
    reference="Brier (1950), DOI: 10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2",
    description="Brier Score for binary event forecasting. BS = mean((p - o)^2) where p is forecast probability, o is binary outcome (0/1).",
    formula=r"\frac{1}{n}\sum_{i=1}^n (p_i - o_i)^2",
)
def brier_score(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Brier Score for binary events.

    A ``ValueError`` is raised if ``obs`` holds a value other than 0 or 1, or ``sim`` a
    value outside [0, 1]. Missing values are not checked.

    Parameters
    ----------
    obs : array-like
        Binary observed outcomes (0 or 1).
    sim : array-like
        Forecast probabilities in [0, 1].
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        Brier Score value.

    References
    ----------
    - Brier (1950), DOI: 10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2
    - Murphy (1973), DOI: 10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2
    """
    return _brier_score_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Reliability",
    direction="minimize",
    bounds=(0.0, None),
    reference="Murphy (1973), DOI: 10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2",
    description="Reliability component of Brier Score decomposition. Measures the conditional bias of forecasts within probability bins. Lower values indicate better reliability (calibration).",
    formula=r"\sum_k \frac{n_k}{n} (\bar{p}_k - \bar{o}_k)^2",
)
def reliability(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    n_bins: int = 10,
) -> float | np.ndarray:
    """
    Reliability (calibration) term of the Brier score decomposition of Murphy (1973):
    sum_k n_k / n * (mean(p_k) - mean(o_k))^2.

    The forecast probabilities are grouped into ``n_bins`` equal-width bins on [0, 1].
    Bins are half-open, [a, b); the last bin is closed on the right, so a probability
    of exactly 1 is counted. With weights, n_k and n are sums of weights and the bin
    means of the probability and of the frequency are weighted means. The resolution
    and uncertainty terms are not computed. A ``ValueError`` is raised if ``obs`` holds a
    value other than 0 or 1, if ``sim`` lies outside [0, 1] or if ``n_bins`` is not an
    integer of at least 1.

    Parameters
    ----------
    obs : array-like
        Binary observed outcomes (0 or 1).
    sim : array-like
        Forecast probabilities in [0, 1].
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.
    n_bins : int, default=10
        Number of probability bins for reliability diagram; an integer, at least 1.

    Returns
    -------
    float or ndarray
        Reliability value.

    References
    ----------
    - Murphy (1973), DOI: 10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2
    - Bröcker & Smith (2007), DOI: 10.1175/WAF993.1
    """
    return _reliability_core(obs, sim, weight=weight, axis=axis, reduction=reduction, n_bins=n_bins)


@metric(
    name="Sharpness",
    direction="maximize",
    bounds=(0.0, 0.25),
    reference="Standard metric",
    description="Variance of the forecast probabilities, a measure of how far forecasts depart from the climatological frequency. It does not use the observations. Higher is better only conditional on reliability.",
    formula=r"\text{Var}(p) = \frac{1}{n}\sum_{i=1}^n (p_i - \bar{p})^2",
)
def sharpness(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Sharpness of probability forecasts, measured as the variance of the forecast
    probabilities.

    This is not a term of the Murphy (1973) decomposition of the Brier score: the terms
    of that decomposition are reliability, resolution and uncertainty. The variance is
    computed from ``sim`` alone and says nothing about calibration.

    Parameters
    ----------
    obs : array-like
        Binary observed outcomes (0 or 1). Not used in calculation but required for API consistency.
    sim : array-like
        Forecast probabilities in [0, 1].
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or ndarray
        Sharpness value (variance of forecast probabilities).
    """
    return _sharpness_core(obs, sim, weight=weight, axis=axis, reduction=reduction)
