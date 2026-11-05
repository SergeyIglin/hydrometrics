"""
Hydrological metrics for HydroMetrics.

Includes NSE, LogNSE, Modified NSE, NNSE, KGE variants, RSR, VE,
and other hydrological metrics.
"""

from __future__ import annotations

from hydrometrics.core.policies import ReductionType
from typing import Literal, Optional
import numpy as np

from hydrometrics.core.base import metric
from hydrometrics.backends.numpy import (
    _nse_core,
    _log_nse_core,
    _modified_nse_core,
    _nse_bounded_core,
    _kge_2009_core,
    _kge_2012_core,
    _r_component_core,
    _alpha_component_core,
    _beta_component_core,
    _gamma_component_core,
    _rsr_core,
    _ve_core,
    _reg_nse_core,
    _forecast_verification_core,
    _forecast_verification_delta_core,
    _ssigma_core,
    _ssigma_delta_core,
    _nse_variance_weighted_core

       
)


# ============================================================================
# Hydrological Metrics
# ============================================================================
@metric(
    name="Variance-Weighted Nash-Sutcliffe Efficiency",
    direction="maximize",
    bounds=(-np.inf, 1.0),
    reference=(
        "Gartsman et al. (2024), DOI: 10.24057/2071-9388-2024-3564"
    ),
    description=(
        "Variance-weighted multi-site Nash-Sutcliffe Efficiency. "
        "Computes NSE independently for each gauge and aggregates "
        "the results using the variance of observed values at each "
        "gauge as weights. Gauges with greater observed-flow "
        "variability contribute more to the aggregate score. "
        "A value of 1 indicates perfect agreement, while values "
        "below 0 indicate performance worse than using the mean "
        "observed value at each gauge as the reference prediction."
    ),
    formula=(
        r"\mathrm{NSE}_{\mathrm{VW}} = "
        r"\frac{\sum_{g=1}^{G} \sigma_g^2 \, \mathrm{NSE}_g}"
        r"{\sum_{g=1}^{G} \sigma_g^2}"
    ),
    supports_weight=False,
    supports_axis=False,
)
def nse_variance_weighted(
    obs: np.ndarray,
    sim: np.ndarray,
    gauge: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """
    Variance-weighted Nash-Sutcliffe Efficiency across gauges.

    Computes NSE separately for each gauge and combines the
    gauge-specific scores using the variance of observed values
    as weights.

    Parameters
    ----------
    obs : np.ndarray
        Observed values.
    sim : np.ndarray
        Simulated values.
    gauge : np.ndarray
        Gauge labels identifying the observation station for
        each paired observed and simulated value.
    weight : array-like, optional
        Sample weights. Not supported by this metric.
    axis : int, optional
        Axis along which to compute. Not supported by this metric.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy. Not used by this metric.

    Returns
    -------
    float
        Variance-weighted mean NSE across gauges, or NaN if
        no valid gauge scores with positive observed variance
        are available.

    References
    ----------
    - Gartsman, B. I., Solomatine, D. P., & Gubareva, T. S. (2024).
      A Method of Multi-Site Calibration of Distributed Hydrological
      Models Based on the Nash-Sutcliffe Efficiency.
      Geography, Environment, Sustainability, 17(4), 76-87.
      DOI: 10.24057/2071-9388-2024-3564.
    - Nash, J. E., & Sutcliffe, J. V. (1970).
      River flow forecasting through conceptual models.
      Part I — A discussion of principles.
      DOI: 10.1016/0022-1694(70)90255-6.
    """
    return _nse_variance_weighted_core(obs, sim, gauge)






@metric(
    name="S/sigma_delta",
    direction="minimize",
    bounds=(0.0, np.inf),
    reference=(
        "Georgievsky & Shanochkin (2007), "
        "Hydrological Forecasts"
    ),
    description=(
        "Group-wise S/sigma criterion for evaluating short-term "
        "hydrological forecasts. For each reference-date group, "
        "the root mean squared forecast error, adjusted by n - m, "
        "is divided by the sample standard deviation of observed "
        "values within that group. The resulting score is assigned "
        "to every valid observation in the group. A value of 0 "
        "indicates perfect agreement; smaller values indicate "
        "lower forecast error relative to within-group variability. "
        "The score is undefined for groups with insufficient "
        "valid observations or zero observed variability."
    ),
    formula=(
        r"\left(\frac{S}{\sigma_\Delta}\right)_d = "
        r"\frac{\sqrt{\frac{1}{n_d-m}"
        r"\sum_{i \in G_d}(y_i-\hat{y}_i)^2}}"
        r"{\sqrt{\frac{1}{n_d-1}"
        r"\sum_{i \in G_d}(y_i-\bar{y}_d)^2}}"
    ),
    supports_weight=False,
    supports_axis=False,
)
def ssigma_delta(
    obs: np.ndarray,
    sim: np.ndarray,
    ref_date: np.ndarray,
    m: int = 2,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """
    Group-wise S/sigma_delta criterion for short-term
    hydrological forecasts.

    The metric is calculated independently for each group
    identified by ref_date. Each group's score is assigned
    to all valid observations belonging to that group.

    Here sigma is the sample standard deviation (``ddof=1``) of the observed values
    within a reference-date group. A group whose observed variance is zero up to
    rounding gives NaN.

    Parameters
    ----------
    obs : np.ndarray
        Observed values.
    sim : np.ndarray
        Simulated or forecast values, with the same shape as obs.
    ref_date : np.ndarray
        Group labels (e.g. reference dates), with the same
        shape as obs and sim.
    m : int, default=2
        Number of fitted parameters used in the error
        degrees-of-freedom adjustment; a finite non-negative number
        (``ValueError`` otherwise). Each group must contain
        more than m valid observation-simulation pairs.
    weight : array-like, optional
        Sample weights. Not supported.
    axis : int, optional
        Axis along which to compute. Not supported.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy. Not used; the result retains
        the shape of the input arrays.

    Returns
    -------
    float or np.ndarray
        By default the mean of the valid scores. With ``reduction="none"`` the array of
        group-wise S/sigma_delta scores with the same shape as obs. Groups with
        insufficient data or zero observed variance are filled with NaN.

    References
    ----------
    - Georgievsky, Y. M., & Shanochkin, S. V. (2007).
      Hydrological Forecasts.
    """
    return _ssigma_delta_core(obs, sim, ref_date, m=m)





@metric(
    name="S/sigma",
    direction="minimize",
    bounds=(0.0, np.inf),
    reference=(
        "Georgievsky & Shanochkin (2007), "
        "Hydrological Forecasts"
    ),
    description=(
        "S/sigma is a hydrological model and forecast "
        "performance criterion defined as the ratio of the "
        "root mean squared residual error, adjusted by the "
        "degrees of freedom n - m, to the sample standard "
        "deviation of observed values. It measures the "
        "prediction error relative to the variability of "
        "observations. A value of 0 indicates perfect agreement; "
        "smaller values indicate better performance. Values "
        "below 1 indicate that the error is smaller than the "
        "standard deviation of the observed series. The "
        "interpretation of performance thresholds depends on "
        "the forecasting task and the applicable hydrological "
        "guidelines."
    ),
    formula=(
        r"\frac{S}{\sigma} = "
        r"\frac{\sqrt{\frac{1}{n-m}"
        r"\sum_{i=1}^{n}(y_i-\hat{y}_i)^2}}"
        r"{\sqrt{\frac{1}{n-1}"
        r"\sum_{i=1}^{n}(y_i-\bar{y})^2}}"
    ),
    supports_weight=False,
)
def ssigma(
    obs: np.ndarray,
    sim: np.ndarray,
    m: int = 2,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """
    S/sigma hydrological model performance criterion.

    Measures the root mean squared residual error relative
    to the sample standard deviation of observed values. Along an ``axis`` every slice is
    scored separately; a slice with ``n <= m`` valid pairs or a constant ``obs`` gives NaN.

    Parameters
    ----------
    obs : np.ndarray
        Observed values.
    sim : np.ndarray
        Simulated or forecast values.
    m : int, default=2
        Number of fitted parameters used in the error
        degrees-of-freedom adjustment; a finite non-negative number
        (``ValueError`` otherwise). Must be smaller
        than the number of valid observations.
    weight : array-like, optional
        Sample weights. Not supported by this metric.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or np.ndarray
        Ratio of the adjusted root mean squared residual
        error to the sample standard deviation of observations.

    References
    ----------
    - Georgievsky, Y. M., & Shanochkin, S. V. (2007).
      Hydrological Forecasts.
    """
    return _ssigma_core(obs, sim, m=m, weight=weight, axis=axis)





@metric(
    name="Forecast Verification",
    direction="maximize",
    bounds=(0, 1),
    reference=(
        "Georgievsky & Shanochkin (2007), "
        "Hydrological Forecasts"
    ),
    description=(
        "Forecast verification criterion for hydrological forecasts. "
        "A forecast is considered verified if the absolute difference "
        "between the observed and forecast values is less than 0.674 "
        "times the sample standard deviation of all observations. "
        "The criterion returns 1 for a verified forecast, 0 for a "
        "forecast that is not, and NaN where the error or the threshold "
        "is undefined. Higher values indicate a greater proportion of "
        "forecasts meeting this accuracy threshold when the individual "
        "results are averaged."
    ),
    formula=(
        r"V_i = "
        r"\mathbb{1}\left("
        r"|y_i-\hat{y}_i| < 0.674\,\sigma_y"
        r"\right)"
    ),
    supports_weight=False,
)
def forecast_verification(
    obs: np.ndarray,
    sim: np.ndarray,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """
    Forecast verification criterion for hydrological forecasts.

    A forecast is considered verified when its absolute error
    is less than 0.674 times the sample standard deviation
    (``ddof=1``) of all observations along ``axis``. The coefficient is the
    module constant ``PROBABLE_ERROR_COEFFICIENT`` of ``hydrometrics.backends.numpy``,
    the probable deviation of the normal law (0.6745 sigma).

    Parameters
    ----------
    obs : np.ndarray
        Observed values.
    sim : np.ndarray
        Forecast or simulated values.
    weight : array-like, optional
        Sample weights. Not supported by this metric.
    axis : int, optional
        Axis along which the standard deviation is calculated.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.

    Returns
    -------
    float or np.ndarray
        With ``reduction="mean"``, the fraction of verified forecasts. With
        ``reduction="none"``, an array of 1.0 (verified), 0.0 (not verified) and NaN
        where the error or the threshold is undefined, for example for a missing
        observation or forecast.

    References
    ----------
    - Georgievsky, Y. M., & Shanochkin, S. V. (2007).
      Hydrological Forecasts.
    """
    return _forecast_verification_core(
        obs, sim, axis=axis
    )



@metric(
    name="Forecast verification delta",
    direction="maximize",
    bounds=(0, 1),
    reference="Georgievsky & Shanochkin (2007), Hydrological Forecasts",
    description=(
        "Binary forecast verification criterion based on the standard deviation "
        "of forecast errors within each reference date. A forecast is considered "
        "verified when its absolute error is less than 0.674 times the sample "
        "standard deviation of forecast errors for the corresponding date. "
        "The result is NaN where the error is missing or the group has fewer "
        "than two valid errors."
    ),
    formula=(
        r"\mathbb{1}\left("
        r"|y_i-\hat{y}_i| < 0.674\,\sigma_{\Delta,d(i)}"
        r"\right),\quad "
        r"\sigma_{\Delta,d}="
        r"\sqrt{\frac{1}{n_d-1}\sum_{j\in d}"
        r"(\Delta_j-\overline{\Delta}_d)^2},\quad "
        r"\Delta_j=\hat{y}_j-y_j"
    ),
    supports_weight=False,
    supports_axis=False,
)
def forecast_verification_delta(
    obs: np.ndarray,
    sim: np.ndarray,
    ref_date: np.ndarray,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Calculate the forecast verification criterion based on forecast errors.

    For each reference date, the sample standard deviation (``ddof=1``) of the
    forecast errors ``sim - obs`` is calculated across valid pairs. A forecast is
    considered verified if its absolute error is less than 0.674 times this
    standard deviation (``PROBABLE_ERROR_COEFFICIENT`` of
    ``hydrometrics.backends.numpy``).

    Here sigma_delta is the spread of the forecast errors ``sim - obs`` within a
    reference-date group.

    Parameters
    ----------
    obs : np.ndarray
        Observed values.
    sim : np.ndarray
        Simulated or forecast values.
    ref_date : np.ndarray
        Reference dates used to group forecast errors.
    weight : np.ndarray, optional
        Weights. Not supported.
    axis : int, optional
        Axis along which to calculate the metric. Not supported.
    reduction : ReductionType, default="mean"
        Reduction applied by the wrapper, if applicable.

    Returns
    -------
    float or np.ndarray
        With ``reduction="mean"``, the fraction of verified forecasts. With
        ``reduction="none"``, an array of 1.0 (verified), 0.0 (not verified) and NaN
        where the error is missing or its group has fewer than two valid errors.

    References
    ----------
    Georgievsky & Shanochkin (2007), *Hydrological Forecasts*.
    """
    return _forecast_verification_delta_core(
        obs,
        sim,
        ref_date,
        weight=weight,
        axis=axis,
        reduction=reduction,
    )


@metric(
    name="Regime Nash-Sutcliffe Efficiency (regNSE)",
    direction="maximize",
    bounds=(-np.inf, 1.0),
    reference=(
        "Gartsman (2023), DOI: 10.34753/HS.2023.5.3.228"
    ),
    description=(
        "Regime Nash-Sutcliffe Efficiency (regNSE). Evaluates "
        "the agreement between observed and simulated annual "
        "flow-duration curves by comparing ranked values at "
        "corresponding rank positions across years. The reference "
        "regime curve is the flow duration curve of the mean annual "
        "hydrograph (calendar-day means of the observed values over "
        "all years, sorted in descending order), or supplied "
        "externally. A value of 1 indicates perfect agreement. "
        "Lower values indicate poorer agreement relative to the "
        "observed regime curve, and negative values indicate that "
        "the squared errors exceed the reference variability."
    ),
    formula=(
        r"\mathrm{regNSE} = "
        r"1 - \frac{\sum_{y=1}^{Y}\sum_{j=1}^{365}"
        r"(Q^{\mathrm{sim}}_{y,j}-Q^{\mathrm{obs}}_{y,j})^2}"
        r"{\sum_{y=1}^{Y}\sum_{j=1}^{365}"
        r"(Q^{\mathrm{obs}}_{y,j}-Q^{\mathrm{reg}}_j)^2}"
    ),
    supports_weight=False,
    supports_axis=False,
)
def regNSE(
    obs: np.ndarray,
    sim: np.ndarray,
    dates: np.ndarray,
    regime: Optional[np.ndarray] = None,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """
    Regime Nash-Sutcliffe Efficiency (regNSE).

    Evaluates simulated annual flow-duration curves against
    observed curves using a reference regime curve: the flow
    duration curve of the mean annual hydrograph of the
    observations (calendar-day means over all years, sorted in
    descending order).

    Parameters
    ----------
    obs : np.ndarray
        One-dimensional array of observed values.
    sim : np.ndarray
        One-dimensional array of simulated values.
    dates : np.ndarray
        One-dimensional array of dates corresponding to the
        observations and simulations.
    regime : np.ndarray, optional
        Precomputed reference regime curve, with shape (365,).
        If None, the curve is calculated from observed data.
    weight : array-like, optional
        Sample weights. Not supported by this metric.
    axis : int, optional
        Axis along which to compute. Not supported by this metric.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy. Not used by this metric.

    Returns
    -------
    float
        Regime NSE value. Returns NaN if no usable years are
        available or the denominator is zero.

    References
    ----------
    - Gartsman, B. I. (2023). Assessing the quality of modeling
      and forecasting in hydrology – reasoning about the method.
      Hydrosphere. Hazard Processes and Phenomena, 5(3), 228–243.
      DOI: 10.34753/HS.2023.5.3.228.
    - Nash, J. E., & Sutcliffe, J. V. (1970). River flow forecasting
      through conceptual models. Part I — A discussion of principles.
      DOI: 10.1016/0022-1694(70)90255-6.
    """
    return _reg_nse_core(
        obs, sim, dates=dates, regime=regime
    )




@metric(
    name="Nash-Sutcliffe Efficiency",
    direction="maximize",
    bounds=(-np.inf, 1.0),
    reference="Nash & Sutcliffe (1970), DOI: 10.1016/0022-1694(70)90255-6",
    description="Nash-Sutcliffe Efficiency (NSE). Measures predictive skill relative to mean observation. NSE=1 is perfect, NSE=0 is equivalent to using mean observation, NSE<0 is worse than mean.",
    formula=r"1 - \frac{\sum_{i=1}^n (y_i - \hat{y}_i)^2}{\sum_{i=1}^n (y_i - \bar{y})^2}",
)
def nse(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    norm: float | np.ndarray | None = None,
) -> float | np.ndarray:
    """
    Nash-Sutcliffe Efficiency (NSE).

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
    norm : float or array-like, optional
        Reference value for normalization (climatological norm).
        If None, uses mean of observations.

    Returns
    -------
    float or ndarray
        NSE value.

    References
    ----------
    - Nash & Sutcliffe (1970), DOI: 10.1016/0022-1694(70)90255-6
    - Moriasi et al. (2007), DOI: 10.13031/2013.23153 (performance ratings)
    """
    return _nse_core(obs, sim, weight=weight, axis=axis, reduction=reduction, norm=norm)


@metric(
    name="Log NSE",
    direction="maximize",
    bounds=(-np.inf, 1.0),
    reference="Krause et al. (2005), DOI: 10.5194/adgeo-5-89-2005",
    description="Log-transformed NSE. Emphasizes low flows by applying log transformation. Adding epsilon to avoid log(0).",
    formula=r"1 - \frac{\sum(\ln(y_i + \epsilon) - \ln(\hat{y}_i + \epsilon))^2}{\sum(\ln(y_i + \epsilon) - \overline{\ln(y + \epsilon)})^2}",
)
def log_nse(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    eps: float = 1e-10,
) -> float | np.ndarray:
    """
    Log-transformed NSE (LogNSE).

    Parameters
    ----------
    obs : array-like
        Observed values (must be >= 0).
    sim : array-like
        Simulated values (must be >= 0).
    weight : array-like, optional
        Sample weights.
    axis : int, optional
        Axis along which to compute.
    reduction : {"mean", "sum", "none"}, default="mean"
        Reduction strategy.
    eps : float, default=1e-10
        Small constant added before log to avoid log(0).

    Returns
    -------
    float or ndarray
        LogNSE value.

    References
    ----------
    - Krause et al. (2005), DOI: 10.5194/adgeo-5-89-2005
    """
    return _log_nse_core(obs, sim, weight=weight, axis=axis, reduction=reduction, eps=eps)


@metric(
    name="Modified NSE",
    direction="maximize",
    bounds=(-np.inf, 1.0),
    reference="Krause et al. (2005), DOI: 10.5194/adgeo-5-89-2005",
    description="Modified NSE using absolute differences instead of squared differences. Less sensitive to outliers than standard NSE.",
    formula=r"1 - \frac{\sum|y_i - \hat{y}_i|}{\sum|y_i - \bar{y}|}",
)
def modified_nse(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    norm: float | np.ndarray | None = None,
) -> float | np.ndarray:
    """
    Modified NSE (mNSE).

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
    norm : float or array-like, optional
        Reference value for normalization. If None, uses mean of observations.

    Returns
    -------
    float or ndarray
        Modified NSE value.

    References
    ----------
    - Krause et al. (2005), DOI: 10.5194/adgeo-5-89-2005
    """
    return _modified_nse_core(obs, sim, weight=weight, axis=axis, reduction=reduction, norm=norm)


@metric(
    name="Bounded Nash-Sutcliffe Efficiency",
    direction="maximize",
    bounds=(-1.0, 1.0),
    reference="No verified primary source",
    description="Bounded NSE: NSE / (2 - NSE), with values in (-1, 1]. It ranks models like NSE and has the same zero. Not the nNSE of the literature, which is 1 / (2 - NSE).",
    formula=r"\frac{NSE}{2 - NSE}",
)
def nse_bounded(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Bounded NSE.

    ``NSE / (2 - NSE)``, a bounded transform of NSE with values in (-1, 1] and
    value 0 at NSE = 0. It ranks models like NSE. The name nNSE is used in the
    literature for the form 1 / (2 - NSE), with values in (0, 1] and 0.5 at
    NSE = 0, which is a different quantity. No primary source for the form
    implemented here could be verified.

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
        Bounded NSE value in (-1, 1].

    References
    ----------
    - No verified primary source
    """
    return _nse_bounded_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Kling-Gupta Efficiency 2009",
    direction="maximize",
    bounds=(-np.inf, 1.0),
    reference="Gupta et al. (2009), DOI: 10.1016/j.jhydrol.2009.08.003",
    description="Kling-Gupta Efficiency (KGE) 2009 version. Decomposes NSE into correlation (r), variability ratio (alpha), and bias ratio (beta).",
    formula=r"1 - \sqrt{(r-1)^2 + (\alpha-1)^2 + (\beta-1)^2}",
)
def kge_2009(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Kling-Gupta Efficiency (KGE) 2009 version.

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
        KGE value.

    References
    ----------
    - Gupta et al. (2009), DOI: 10.1016/j.jhydrol.2009.08.003
    """
    kge, _, _, _ = _kge_2009_core(obs, sim, weight=weight, axis=axis, reduction=reduction)
    return kge


def _kge_2009_raw(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> tuple:
    """Internal function returning raw tuple for testing."""
    return _kge_2009_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Kling-Gupta Efficiency 2012",
    direction="maximize",
    bounds=(-np.inf, 1.0),
    reference="Kling et al. (2012), DOI: 10.1016/j.jhydrol.2012.01.011",
    description="Kling-Gupta Efficiency (KGE') 2012 version. Replaces the variability ratio alpha of the 2009 version by the ratio of coefficients of variation (gamma).",
    formula=r"1 - \sqrt{(r-1)^2 + (\beta-1)^2 + (\gamma-1)^2}",
)
def kge_2012(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Kling-Gupta Efficiency (KGE') 2012 version.

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
        KGE value.

    Notes
    -----
    KGE' = 1 - sqrt((r - 1)^2 + (beta - 1)^2 + (gamma - 1)^2) with
    beta = mean(sim) / mean(obs) and gamma = (std(sim) / mean(sim)) / (std(obs) / mean(obs)).
    The variability ratio alpha is not a term of this version; it is a term of
    :func:`hydrometrics.kge_2009`.

    References
    ----------
    - Kling et al. (2012), DOI: 10.1016/j.jhydrol.2012.01.011
    """
    kge, _, _, _, _ = _kge_2012_core(obs, sim, weight=weight, axis=axis, reduction=reduction)
    return kge


def _kge_2012_raw(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> tuple:
    """Internal function returning raw tuple for testing."""
    return _kge_2012_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="KGE Components",
    direction="target",
    bounds=(None, None),
    reference="Gupta et al. (2009); Kling et al. (2012)",
    description="Compute all KGE components: r (correlation), alpha (variability), beta (bias), gamma (CV ratio).",
    formula=r"r, \alpha, \beta, \gamma",
    optimum=1.0,
)
def kge_components(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    version: Literal["2009", "2012"] = "2012",
) -> dict[str, float | np.ndarray]:
    """
    Compute all KGE components.

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
    version : {"2009", "2012"}, default="2012"
        KGE version. It decides which components are returned: ``gamma`` is added
        for "2012". The values of ``r``, ``alpha`` and ``beta`` do not depend on it.

    Returns
    -------
    dict
        Dictionary with keys: 'r', 'alpha', 'beta', 'gamma' (if version=2012).
        KGE 2009 is 1 - sqrt((r - 1)^2 + (alpha - 1)^2 + (beta - 1)^2); KGE 2012
        is 1 - sqrt((r - 1)^2 + (beta - 1)^2 + (gamma - 1)^2), so 'alpha' is
        returned for information only in that version.

    Raises
    ------
    ValueError
        If ``version`` is not "2009" or "2012".
    """
    if version not in ("2009", "2012"):
        raise ValueError(f"version must be '2009' or '2012', got {version!r}")

    r = _r_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction)
    alpha = _alpha_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction, version=version)
    beta = _beta_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction)

    result = {"r": r, "alpha": alpha, "beta": beta}

    if version == "2012":
        gamma = _gamma_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction)
        result["gamma"] = gamma

    return result


@metric(
    name="KGE r Component (Correlation)",
    direction="maximize",
    bounds=(-1.0, 1.0),
    reference="Gupta et al. (2009)",
    description="Correlation component of KGE.",
    formula=r"r = \frac{\text{cov}(y, \hat{y})}{\sigma_y \sigma_{\hat{y}}}",
)
def r_component(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    KGE r component (Pearson correlation).

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
        Correlation value.
    """
    return _r_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="KGE alpha Component (Variability Ratio)",
    direction="target",
    bounds=(0.0, None),
    reference="Kling et al. (2012)",
    description="Alpha component of KGE. Both 2009 and 2012 versions: std(sim)/std(obs).",
    formula=r"\alpha = \frac{\sigma_{\hat{y}}}{\sigma_y}",
    optimum=1.0,
)
def alpha_component(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    version: Literal["2009", "2012"] = "2012",
) -> float | np.ndarray:
    """
    KGE alpha component (variability ratio).

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
    version : {"2009", "2012"}, default="2012"
        KGE version. It is validated but has no effect on the value: alpha is
        std(sim) / std(obs) in both cases. Alpha is a term of KGE 2009 only; KGE'
        (2012) uses the ratio of coefficients of variation gamma instead.

    Returns
    -------
    float or ndarray
        Alpha value.

    Raises
    ------
    ValueError
        If ``version`` is not "2009" or "2012".
    """
    return _alpha_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction, version=version)


@metric(
    name="KGE beta Component (Bias Ratio)",
    direction="target",
    bounds=(None, None),
    reference="Gupta et al. (2009)",
    description="Beta component of KGE: mean(sim)/mean(obs). Beta=1 indicates no bias.",
    formula=r"\beta = \frac{\bar{\hat{y}}}{\bar{y}}",
    optimum=1.0,
)
def beta_component(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    KGE beta component (bias ratio).

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
        Beta value.
    """
    return _beta_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="KGE gamma Component (CV Ratio)",
    direction="target",
    bounds=(None, None),
    reference="Kling et al. (2012)",
    description="Gamma component of KGE': CV(sim)/CV(obs). Gamma=1 indicates matching coefficient of variation.",
    formula=r"\gamma = \frac{CV_{\hat{y}}}{CV_y} = \frac{\sigma_{\hat{y}}/\bar{\hat{y}}}{\sigma_y/\bar{y}}",
    optimum=1.0,
)
def gamma_component(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    KGE gamma component (coefficient of variation ratio).

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
        Gamma value.
    """
    return _gamma_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Ratio of RMSE to Standard Deviation (RSR)",
    direction="minimize",
    bounds=(0.0, None),
    reference="Moriasi et al. (2007), DOI: 10.13031/2013.23153",
    description="RSR = RMSE / std(obs). Normalized error metric. RSR=0 is perfect, RSR=1 is equivalent to mean observation.",
    formula=r"\frac{RMSE}{\sigma_y}",
)
def rsr(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Ratio of RMSE to Standard Deviation of Observations (RSR).

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
        RSR value.

    References
    ----------
    - Moriasi et al. (2007), DOI: 10.13031/2013.23153
    """
    return _rsr_core(obs, sim, weight=weight, axis=axis, reduction=reduction)


@metric(
    name="Volumetric Efficiency (VE)",
    direction="maximize",
    bounds=(-np.inf, 1.0),
    reference="Criss & Winston (2008), DOI: 10.1002/hyp.7072",
    description="Volumetric Efficiency. Measures volume matching. VE=1 is perfect volume match, VE=0 is equivalent to zero simulation.",
    formula=r"1 - \frac{\sum|y_i - \hat{y}_i|}{\sum|y_i|}",
)
def ve(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
) -> float | np.ndarray:
    """
    Volumetric Efficiency (VE).

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
        VE value.

    References
    ----------
    - Criss & Winston (2008), DOI: 10.1002/hyp.7072
    """
    return _ve_core(obs, sim, weight=weight, axis=axis, reduction=reduction)
