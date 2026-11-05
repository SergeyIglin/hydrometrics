"""
NumPy backend for HydroMetrics.

Core numpy implementations of all metrics.
"""

from __future__ import annotations

from typing import Literal, Optional
import numpy as np

from hydrometrics.core.policies import ReductionType


# ============================================================================
# Helper functions
# ============================================================================

def _safe_divide(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    """Safe division returning NaN where denominator is zero."""
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.true_divide(num, den)
        # Handle both scalar and array cases
        if np.isscalar(result):
            if np.isscalar(den):
                return np.nan if den == 0 else result
            else:
                result = np.where(den == 0, np.nan, result)
                return result
        # Array case
        result[den == 0] = np.nan
    return result


# A sum of squares is treated as zero when it is at most this fraction of the sum of squares of
# the data: variance <= 1e-24 * mean**2, i.e. a coefficient of variation below 1e-12. Rounding of
# the mean of a constant series leaves a relative variance of about 1e-32.
ZERO_VARIANCE_RTOL = 1e-24

# Probable deviation of the normal law, 0.6745 sigma; the forecast-quality source gives 0,674.
PROBABLE_ERROR_COEFFICIENT = 0.674


def _drop_negligible(total: np.ndarray, scale: np.ndarray, squared: bool = True) -> np.ndarray:
    """Replace ``total`` by 0 where it is rounding noise relative to ``scale``.

    ``total`` is a sum of squares (``squared=True``) or of absolute values
    (``squared=False``, tolerance ``sqrt(ZERO_VARIANCE_RTOL)``); ``scale`` is the same
    sum for the data themselves.
    """
    rtol = ZERO_VARIANCE_RTOL if squared else np.sqrt(ZERO_VARIANCE_RTOL)
    return np.where(total <= rtol * scale, 0.0, total)[()]


def _check_nonnegative_number(value, name: str):
    """Return ``value`` if it is a finite non-negative real number, else raise."""
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise TypeError(f"{name} must be a non-negative number, got {value!r}")
    if not np.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite non-negative number, got {value!r}")
    return value


def _check_binary_probability(obs: np.ndarray, sim: np.ndarray) -> None:
    """Raise ``ValueError`` unless ``obs`` is 0/1 and ``sim`` lies in [0, 1]; NaN is ignored."""
    o = np.asarray(obs, dtype=float)
    s = np.asarray(sim, dtype=float)
    o = o[~np.isnan(o)]
    s = s[~np.isnan(s)]
    if np.any((o != 0) & (o != 1)):
        raise ValueError("obs must be binary (0 or 1) for a probability score")
    if np.any((s < 0) | (s > 1)):
        raise ValueError("sim must hold probabilities in [0, 1]")


def _weighted_mean(
    arr: np.ndarray,
    weight: np.ndarray | None,
    axis: int | None,
) -> np.ndarray:
    if weight is None:
        return np.nanmean(arr, axis=axis)
    w = np.broadcast_to(np.asarray(weight, dtype=float), arr.shape)
    # Only pairs with a valid value and a valid weight count in numerator and denominator.
    valid = ~(np.isnan(arr) | np.isnan(w))
    num = np.sum(np.where(valid, arr * w, 0.0), axis=axis)
    den = np.sum(np.where(valid, w, 0.0), axis=axis)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(den == 0, np.nan, num / den)[()]


def _weighted_var(
    arr: np.ndarray, weight: np.ndarray | None, axis: int | None, ddof: int = 0
) -> np.ndarray:
    """Compute weighted variance along axis."""
    if weight is None:
        return np.nanvar(arr, axis=axis, ddof=ddof)
    mean = _weighted_mean(arr, weight, axis)
    if axis is not None:
        mean = np.expand_dims(mean, axis)
    # Weights of missing values do not count in the sum of weights.
    w = np.where(np.isnan(arr), np.nan, np.broadcast_to(np.asarray(weight, dtype=float), arr.shape))
    return np.nansum(w * (arr - mean) ** 2, axis=axis) / (np.nansum(w, axis=axis) - ddof)


def _weighted_cov(
    x: np.ndarray, y: np.ndarray, weight: np.ndarray | None, axis: int | None
) -> np.ndarray:
    """Compute weighted covariance along axis."""
    mean_x = _weighted_mean(x, weight, axis)
    mean_y = _weighted_mean(y, weight, axis)
    if axis is not None:
        mean_x = np.expand_dims(mean_x, axis)
        mean_y = np.expand_dims(mean_y, axis)
    diff_x = x - mean_x
    diff_y = y - mean_y
    if weight is None:
        return np.nansum(diff_x * diff_y, axis=axis) / (np.count_nonzero(~np.isnan(x), axis=axis) - 1)
    w = np.where(
        np.isnan(x) | np.isnan(y), np.nan, np.broadcast_to(np.asarray(weight, dtype=float), x.shape)
    )
    return np.nansum(w * diff_x * diff_y, axis=axis) / (np.nansum(w, axis=axis) - 1)


def _weighted_corr(
    x: np.ndarray, y: np.ndarray, weight: np.ndarray | None, axis: int | None
) -> np.ndarray:
    """Compute weighted Pearson correlation along axis."""
    cov = _weighted_cov(x, y, weight, axis)
    std_x = np.sqrt(_weighted_var(x, weight, axis, ddof=1))
    std_y = np.sqrt(_weighted_var(y, weight, axis, ddof=1))
    return _safe_divide(cov, std_x * std_y)

def _along_axis(func, obs: np.ndarray, sim: np.ndarray, weight: np.ndarray | None, axis: int | None):
    """Apply ``func(obs_1d, sim_1d, weight_1d)`` to every slice along ``axis``.

    ``axis=None`` pools all values. The result has the shape of ``obs`` without ``axis``.
    """
    if axis is None:
        return func(obs.ravel(), sim.ravel(), None if weight is None else weight.ravel())
    o = np.moveaxis(obs, axis, -1)
    s = np.moveaxis(sim, axis, -1)
    w = None if weight is None else np.moveaxis(weight, axis, -1)
    out = np.empty(o.shape[:-1], dtype=float)
    for index in np.ndindex(out.shape):
        out[index] = func(o[index], s[index], None if w is None else w[index])
    return out[()]


def mean_annual_hydrograph(
    obs: np.ndarray,
    date: np.ndarray    
) -> np.ndarray:
    """Compute mean annual hydrograph.

    Returns 366 values if the input series contains any leap year,
    otherwise 365 values. 29 February is kept as its own calendar day.

    Parameters
    ----------
    obs : np.ndarray
        Observed discharge values, one-dimensional.
    date : np.ndarray
        Observation dates, same shape as ``obs``.

    Returns
    -------
    np.ndarray
        Mean discharge for each calendar day (365 or 366 values).
    """
    date = np.asarray(date)
    discharge = np.asarray(obs)

    if date.ndim != 1 or discharge.ndim != 1:
        raise ValueError("date and discharge must be one-dimensional arrays.")

    if date.shape != discharge.shape:
        raise ValueError("date and discharge must have the same shape.")

    # Day of year (0-based).
    day_of_year = (
        date.astype("datetime64[D]")
        - date.astype("datetime64[Y]").astype("datetime64[D]")
    ).astype(int)

    # Leap years present in the series?
    year = date.astype("datetime64[Y]").astype(int) + 1970
    is_leap = (year % 4 == 0) & ((year % 100 != 0) | (year % 400 == 0))
    n_days = 366 if is_leap.any() else 365

    # Daily means, ignoring NaNs.
    result = np.full(n_days, np.nan, dtype=float)

    valid = ~np.isnan(discharge)

    sums = np.bincount(day_of_year[valid], weights=discharge[valid], minlength=n_days)
    counts = np.bincount(day_of_year[valid], minlength=n_days)

    np.divide(sums, counts, out=result, where=counts > 0)

    return result

def mean_annual_hydrograph_duration_curve(
    obs: np.ndarray,
    date: np.ndarray,
) -> np.ndarray:
    """Compute a flow duration curve based on the mean annual hydrograph.

    Notes
    -----
    1. Compute the mean annual hydrograph (365 or 366 values).
    2. Sort it in descending order.
    3. If the result has 366 values, average the values at ranks 365 and 366 of the
       descending ranking (the two smallest) so that the final length is 365. These
       are rank positions, not calendar days: after sorting, 29 February has no fixed
       position. The annual curves of ``regNSE`` follow the same rule.

    Parameters
    ----------
    obs : np.ndarray
        Observed discharge values.
    date : np.ndarray
        Observation dates.

    Returns
    -------
    np.ndarray
        Flow duration curve with 365 values, sorted in descending order.
    """
    obs = np.asarray(obs)
    date = np.asarray(date)

    if date.ndim != 1 or obs.ndim != 1:
        raise ValueError("obs and date must be one-dimensional arrays.")

    if date.shape != obs.shape:
        raise ValueError("obs and date must have the same shape.")

    # Mean annual hydrograph (365 or 366 values).
    mah = mean_annual_hydrograph(obs, date)

    # Sort descending.
    sorted_mah = np.sort(mah)[::-1]

    # Reduce 366 -> 365 by averaging ranks 365 and 366, the same rule as for the annual curves.
    if sorted_mah.size == 366:
        sorted_mah = np.concatenate([
            sorted_mah[:364],
            [np.nanmean(sorted_mah[364:366])],
        ])

    return sorted_mah

def _annual_day_index(date: np.ndarray) -> np.ndarray:
    """Convert dates to 365-day calendar indices.

    29 February is assigned to the same index as 28 February.
    """ 
    date = np.asarray(date)

    day_of_year = (
        date.astype("datetime64[D]")
        - date.astype("datetime64[Y]").astype("datetime64[D]")
    ).astype(int)

    year = date.astype("datetime64[Y]").astype(int) + 1970

    is_leap = (year % 4 == 0) & ((year % 100 != 0) | (year % 400 == 0))

    day_index = day_of_year.copy()

    leap_day = is_leap & (day_of_year == 59)
    after_leap_day = is_leap & (day_of_year > 59)

    day_index[leap_day] = 58
    day_index[after_leap_day] -= 1

    return day_index






def meanyear_ranked(
    obs: np.ndarray,
    sim: np.ndarray,
    dates: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    
    obs = np.asarray(obs, dtype=float)
    sim = np.asarray(sim, dtype=float)
    dates = np.asarray(dates, dtype="datetime64[D]")

     
    years_arr = dates.astype("datetime64[Y]").astype(int) + 1970
    unique_years = np.unique(years_arr)
    n_years = len(unique_years)

    
    obs_ranked = np.full((n_years, 365), np.nan, dtype=float)
    sim_ranked = np.full((n_years, 365), np.nan, dtype=float)

    for i, year in enumerate(unique_years):
        year_mask = years_arr == year
        obs_year = obs[year_mask]
        sim_year = sim[year_mask]

        
        obs_clean = obs_year[~np.isnan(obs_year)]
        sim_clean = sim_year[~np.isnan(sim_year)]

       
        obs_sorted = np.sort(obs_clean)[::-1]
        sim_sorted = np.sort(sim_clean)[::-1]

        
        is_leap = (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0)
        expected_days = 366 if is_leap else 365

        
        if len(obs_sorted) == 0:
            continue

        
        if len(obs_sorted) == expected_days:
            if is_leap:
                
                obs_ranked[i, :364] = obs_sorted[:364]
                obs_ranked[i, 364] = (obs_sorted[364] + obs_sorted[365]) / 2.0
                sim_ranked[i, :364] = sim_sorted[:364]
                sim_ranked[i, 364] = (sim_sorted[364] + sim_sorted[365]) / 2.0
            else:
                obs_ranked[i, :] = obs_sorted
                sim_ranked[i, :] = sim_sorted
        else:
            
            n_fill = min(len(obs_sorted), 365)
            obs_ranked[i, :n_fill] = obs_sorted[:n_fill]
            sim_ranked[i, :n_fill] = sim_sorted[:n_fill]
  

    return obs_ranked, sim_ranked, unique_years


# ============================================================================
# Regression metrics
# ============================================================================

def _mae_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Mean Absolute Error."""
    diff = np.abs(obs - sim)
    result = _weighted_mean(diff, weight, axis)
    return result


def _mse_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Mean Squared Error."""
    diff = (obs - sim) ** 2
    result = _weighted_mean(diff, weight, axis)
    return result


def _rmse_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Root Mean Squared Error."""
    mse = _mse_core(obs, sim, weight=weight, axis=axis, reduction="none")
    return np.sqrt(mse)


def _nrmse_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    normalization: Literal["mean", "std", "range", "iqr"] = "mean",
) -> float | np.ndarray:
    """Normalized Root Mean Squared Error."""
    rmse = _rmse_core(obs, sim, weight=weight, axis=axis, reduction="none")

    if normalization == "mean":
        norm = _weighted_mean(obs, weight, axis)
    elif normalization == "std":
        norm = np.sqrt(_weighted_var(obs, weight, axis, ddof=1))
    elif normalization == "range":
        obs_max = np.nanmax(obs, axis=axis)
        obs_min = np.nanmin(obs, axis=axis)
        norm = obs_max - obs_min
    elif normalization == "iqr":
        q75 = np.nanpercentile(obs, 75, axis=axis)
        q25 = np.nanpercentile(obs, 25, axis=axis)
        norm = q75 - q25
    else:
        raise ValueError(f"Unknown normalization: {normalization}")

    return _safe_divide(rmse, norm)


def _bias_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Bias (mean error)."""
    diff = sim - obs
    result = _weighted_mean(diff, weight, axis)
    return result


def _pbias_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Percent Bias."""
    bias = _bias_core(obs, sim, weight=weight, axis=axis, reduction="none")
    obs_mean = _weighted_mean(obs, weight, axis)
    return _safe_divide(bias, obs_mean) * 100


def _r2_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Coefficient of Determination (R²)."""
    ss_res = np.nansum((obs - sim) ** 2 * (weight if weight is not None else 1), axis=axis)
    obs_mean = _weighted_mean(obs, weight, axis)
    if axis is not None:
        obs_mean = np.expand_dims(obs_mean, axis)
    ss_tot = np.nansum((obs - obs_mean) ** 2 * (weight if weight is not None else 1), axis=axis)
    ss_tot = _drop_negligible(ss_tot, np.nansum(obs ** 2 * (weight if weight is not None else 1), axis=axis))
    # Handle constant observations: if ss_tot == 0, R2 is 1.0 if ss_res == 0 else NaN
    result = 1 - _safe_divide(ss_res, ss_tot)
    result = np.where(ss_tot == 0, np.where(ss_res == 0, 1.0, np.nan), result)
    # No valid pair (empty or all-NaN input): the score is undefined, not perfect.
    n_valid = np.sum(~(np.isnan(obs) | np.isnan(sim)), axis=axis)
    return np.where(n_valid == 0, np.nan, result)


def _pearson_r_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Pearson correlation coefficient."""
    return _weighted_corr(obs, sim, weight, axis)


def _scipy_stats():
    """``scipy.stats``, imported when a rank correlation is computed (scipy is an optional dependency)."""
    try:
        from scipy import stats
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise ImportError(
            "spearman_r and kendall_tau need scipy; install it with `pip install scipy` "
            "or `pip install hydrometrics[scipy]`"
        ) from exc
    return stats


def _rank_correlation(statistic):
    """1-D rank correlation over the pairs without NaN; NaN for fewer than two pairs."""
    def one(o, s, w=None):
        valid = ~(np.isnan(o) | np.isnan(s))
        if np.count_nonzero(valid) < 2:
            return np.nan
        return statistic(o[valid], s[valid]).correlation
    return one


def _spearman_r_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Spearman rank correlation (weights are not supported)."""
    return _along_axis(_rank_correlation(_scipy_stats().spearmanr), obs, sim, None, axis)


def _kendall_tau_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Kendall's tau rank correlation (weights are not supported)."""
    return _along_axis(_rank_correlation(_scipy_stats().kendalltau), obs, sim, None, axis)


def _willmott_d_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Willmott's index of agreement (d)."""
    obs_mean = _weighted_mean(obs, weight, axis)
    if axis is not None:
        obs_mean = np.expand_dims(obs_mean, axis)
    numerator = np.nansum((obs - sim) ** 2 * (weight if weight is not None else 1), axis=axis)
    denominator = np.nansum(
        (np.abs(sim - obs_mean) + np.abs(obs - obs_mean)) ** 2 * (weight if weight is not None else 1),
        axis=axis
    )
    return 1 - _safe_divide(numerator, denominator)


# ============================================================================
# Hydrological metrics
# ============================================================================
def _ssigma_delta_core(
    obs: np.ndarray,
    sim: np.ndarray,
    ref_date: np.ndarray,
    *,
    m: int = 2,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "None",
) -> np.ndarray:
    """S/sigma_delta, рассчитанное по группам ref_date.

    Для каждой уникальной даты в ref_date вычисляется своя sigma
    (стандартное отклонение obs внутри группы), после чего
    возвращается отношение S/sigma поэлементно.

    S = sqrt( sum((obs - sim)^2) / (n - m) )   внутри группы
    sigma = sqrt( sum((obs - mean(obs))^2) / (n - 1) )   внутри группы

    Parameters
    ----------
    obs, sim : np.ndarray
        Наблюдения и прогнозы, одинаковой формы.
    ref_date : np.ndarray
        Массив дат (или иных меток группы), той же формы, что obs/sim.
        Для каждого уникального значения считается своя sigma.
    m : int, default=2
        Число степеней свободы в знаменателе S. Должно быть n > m
        внутри каждой группы.
    weight : None
        Не поддерживается.
    axis : None
        Не поддерживается (группировка ведётся по ref_date).
    reduction : ReductionType, default="None"
        Заглушка для совместимости с общим API.

    Returns
    -------
    np.ndarray
        Массив той же формы, что obs, со значениями S/sigma.
        Точки, где группа содержит n <= m, заполняются NaN.
    """
    m = _check_nonnegative_number(m, "m")
    if axis is not None:
        raise NotImplementedError(
            "axis is not supported for Ssigma (grouping is done via ref_date)"
        )
    if weight is not None:
        raise NotImplementedError(
            "weight is not supported for Ssigma"
        )

    obs = np.asarray(obs, dtype=float)
    sim = np.asarray(sim, dtype=float)
    ref_date = np.asarray(ref_date)

    if obs.shape != sim.shape or obs.shape != ref_date.shape:
        raise ValueError(
            f"obs, sim and ref_date must have the same shape, "
            f"got {obs.shape}, {sim.shape}, {ref_date.shape}"
        )

    result = np.full_like(obs, np.nan, dtype=float)

    for date in np.unique(ref_date):
        mask = (ref_date == date) & ~np.isnan(obs) & ~np.isnan(sim)
        n = np.sum(mask)

        if n <= m:
            # недостаточно точек в группе — оставляем NaN
            continue

        obs_g = obs[mask]
        sim_g = sim[mask]

        obs_mean = np.mean(obs_g)

        S = np.sqrt(np.sum((obs_g - sim_g) ** 2) / (n - m))
        ss_obs = _drop_negligible(np.sum((obs_g - obs_mean) ** 2), np.sum(obs_g ** 2))
        sigma = np.sqrt(ss_obs / (n - 1))

        if sigma == 0:
            # degenerate group (all obs equal up to rounding): the metric is undefined
            continue

        result[mask] = S / sigma

    return result



def _ssigma_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    m: int = 2,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "none",
) -> np.ndarray:
    """S/sigma: sqrt(sum((obs - sim)^2) / (n - m)) / std(obs, ddof=1).

    Without an axis the valid sample must be larger than ``m`` (``ValueError``). Along an
    axis a slice with ``n <= m`` valid pairs, or with a constant ``obs``, gives NaN.
    """

    m = _check_nonnegative_number(m, "m")
    if weight is not None:
        raise NotImplementedError(
            "weight is not supported for Ssigma"
        )

    n = np.sum(~np.isnan(obs), axis=axis)
    too_few = n <= m
    if axis is None and too_few:
        raise ValueError(
            f"Sample size too small: need n > m={m}, got n={n}"
        )

    obs_mean = np.nanmean(obs, axis=axis)
    if axis is not None:
        obs_mean = np.expand_dims(obs_mean, axis)

    dof_error = np.where(too_few, np.nan, n - m)
    dof_obs = np.where(n > 1, n - 1, np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        S = np.sqrt(np.nansum((obs - sim) ** 2, axis=axis) / dof_error)
        ss_obs = _drop_negligible(
            np.nansum((obs - obs_mean) ** 2, axis=axis), np.nansum(obs ** 2, axis=axis)
        )
        sigma = np.sqrt(ss_obs / dof_obs)

    return _safe_divide(S, sigma)




def _forecast_verification_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "None",
) -> np.ndarray:
    """Forecast_verification."""

    obs_mean = np.nanmean(obs, axis=axis)
    if axis is not None:
        obs_mean = np.expand_dims(obs_mean, axis)

    if weight is not None:
            raise NotImplementedError(
                "weight is not supported for Forecast_verification"
            )
    n = np.sum(~np.isnan(obs), axis=axis)

    with np.errstate(invalid="ignore", divide="ignore"):
        sigma = np.sqrt(
            np.nansum((obs - obs_mean) ** 2, axis=axis) / (n - 1)
        )

    if axis is not None:
        sigma = np.expand_dims(sigma, axis)

    error = np.abs(obs - sim)
    verified = (error < PROBABLE_ERROR_COEFFICIENT * sigma).astype(float)
    # A missing error or threshold is not a failed forecast: the result is NaN.
    return np.where(np.isnan(error) | np.isnan(sigma), np.nan, verified)


def _forecast_verification_delta_core(
    obs: np.ndarray,
    sim: np.ndarray,
    ref_date: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "None",
) -> np.ndarray:
    """Forecast_verification. based on forecast error."""

    delta = sim - obs

    if axis is not None:
        raise NotImplementedError(
            "axis is not supported for forecast_verification_delta"
        )
    if weight is not None:
            raise NotImplementedError(
                "weight is not supported for Forecast_verification"
            )
    
    sigma_delta = np.full_like(delta, np.nan, dtype=float)

    for date in np.unique(ref_date):
        mask = (ref_date == date) & ~np.isnan(delta)

        n = np.sum(mask)

        if n >= 2:
            delta_mean = np.mean(delta[mask])
            sigma_delta[mask] = np.sqrt(
                np.sum((delta[mask] - delta_mean) ** 2) / (n - 1)
            )

    error = np.abs(obs - sim)
    verified = (error < PROBABLE_ERROR_COEFFICIENT * sigma_delta).astype(float)
    return np.where(np.isnan(error) | np.isnan(sigma_delta), np.nan, verified)




def _reg_nse_core(
    obs: np.ndarray,
    sim: np.ndarray,
    dates: np.ndarray,
    *,
    regime: Optional[np.ndarray] = None,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",          
) -> float | np.ndarray:
    """
    Core implementation of regNSE.

    For every calendar year:

    1. OBS is sorted independently in descending order.
    2. SIM is sorted independently in descending order.
    3. Every year is converted to exactly 365 rank positions.
    4. For leap years, the two lowest values are averaged.
    5. Q_reg is the flow duration curve of the mean annual hydrograph: the
       calendar-day means of OBS over all years, sorted in descending order
       (see ``mean_annual_hydrograph_duration_curve``), or provided externally
       via `regime`. Pairs with a missing value are removed before the curves
       are built.
    6. regNSE is calculated as:

           1 - sum((SIM - OBS)^2)
               --------------------
               sum((OBS - Q_reg)^2)

    The sums are pooled over all years and all 365 rank positions.

    Parameters
    ----------
    obs : np.ndarray
        1D array of observed values.
    sim : np.ndarray
        1D array of simulated values.
    dates : np.ndarray
        1D array of dates (datetime64[D]).
    regime : Optional[np.ndarray], default=None
        Pre‑computed ranked mean annual hydrograph (Q_reg) – a 1D array
        of length 365. If provided, it is used directly instead of the curve
        computed from ``obs``. Must have shape (365,).
    """
    
    obs = np.asarray(obs, dtype=float)
    sim = np.asarray(sim, dtype=float)
    dates = np.asarray(dates, dtype="datetime64[D]")

    if axis is not None:
        raise NotImplementedError(
            "axis is not supported for regNSE"
        )
    if weight is not None:
        raise NotImplementedError(
            "weight is not supported for regNSE"
        )
 

    if obs.shape != sim.shape:
        raise ValueError(
            f"Shape mismatch: obs {obs.shape} != sim {sim.shape}"
        )

    if obs.shape != dates.shape:
        raise ValueError(
            f"Shape mismatch: obs {obs.shape} != dates {dates.shape}"
        )

    if obs.ndim != 1:
        raise ValueError(
            f"regNSE requires 1D arrays, got {obs.ndim}D"
        )

    
    # Pairwise removal before the ranked curves are built, so both series keep the same dates.
    valid = ~(np.isnan(obs) | np.isnan(sim) | np.isnat(dates))
    obs, sim, dates = obs[valid], sim[valid], dates[valid]

    obs_ranked, sim_ranked, unique_years = meanyear_ranked(obs, sim, dates)

    n_years = len(unique_years)

    if n_years == 0:
        return np.nan

    
    if regime is None:
        Q_reg = mean_annual_hydrograph_duration_curve(obs, dates)
    else:
        Q_reg = np.asarray(regime, dtype=float)
        if Q_reg.shape != (365,):
            raise ValueError(
                f"regime must be a 1D array of length 365, got {Q_reg.shape}"
            )

    
    numerator = np.nansum(
        (sim_ranked - obs_ranked) ** 2
    )

    denominator = np.nansum(
        (obs_ranked - Q_reg[None, :]) ** 2
    )
    
    if denominator == 0:
        return np.nan

    reg_nse = 1.0 - numerator / denominator

    return reg_nse


def _nse_variance_weighted_core(
    obs: np.ndarray,
    sim: np.ndarray,
    gauge: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float:
    """Variance-weighted Nash-Sutcliffe Efficiency across gauges.

    NSE is calculated independently for each gauge using ``_nse_core``.
    The resulting NSE values are then averaged using the variance of
    observations at each gauge as weights.

    Parameters
    ----------
    obs : np.ndarray
        Observed values, shape (n,).
    sim : np.ndarray
        Simulated values, shape (n,).
    gauge : np.ndarray
        Gauge labels, shape (n,).

    Returns
    -------
    float
        Variance-weighted mean NSE across gauges.
    """
    obs = np.asarray(obs)
    sim = np.asarray(sim)
    gauge = np.asarray(gauge)

    if axis is not None:
            raise NotImplementedError(
                "axis is not supported for _nse_variance_weighted"
            )
    if weight is not None:
            raise NotImplementedError(
                "weight is not supported for _nse_variance_weighted"
            )

    if obs.ndim != 1 or sim.ndim != 1 or gauge.ndim != 1:
        raise ValueError("obs, sim and gauge must be 1-dimensional arrays.")

    if not (obs.shape == sim.shape == gauge.shape):
        raise ValueError("obs, sim and gauge must have the same shape.")

    nse_values = []
    variances = []

    for gauge_id in np.unique(gauge):
        mask = (
            (gauge == gauge_id)
            & np.isfinite(obs)
            & np.isfinite(sim)
        )

        obs_g = obs[mask]
        sim_g = sim[mask]

        if obs_g.size == 0:
            continue

        # Use the library's NSE implementation.
        nse_g = _nse_core(obs_g, sim_g)

        # Variance of observations at this gauge.
        variance_g = np.var(obs_g)

        # A gauge with constant observations (variance zero up to rounding) has no score.
        informative = obs_g.size * variance_g > ZERO_VARIANCE_RTOL * np.sum(obs_g ** 2)

        if np.isfinite(nse_g) and np.isfinite(variance_g) and informative:
            nse_values.append(nse_g)
            variances.append(variance_g)

    if not variances:
        return np.nan

    return np.average(nse_values, weights=variances)



def _nse_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    norm: float | np.ndarray | None = None,
) -> float | np.ndarray:
    """Nash-Sutcliffe Efficiency (NSE).

    Reference: Nash & Sutcliffe (1970), DOI: 10.1016/0022-1694(70)90255-6
    """
    if norm is None:
        norm = _weighted_mean(obs, weight, axis)
    if axis is not None:
            norm = np.expand_dims(norm, axis)
    ss_res = np.nansum((obs - sim) ** 2 * (weight if weight is not None else 1), axis=axis)
    ss_tot = np.nansum((obs - norm) ** 2 * (weight if weight is not None else 1), axis=axis)
    ss_tot = _drop_negligible(ss_tot, np.nansum(obs ** 2 * (weight if weight is not None else 1), axis=axis))
    return 1 - _safe_divide(ss_res, ss_tot)


def _log_nse_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    eps: float = 1e-10,
) -> float | np.ndarray:
    """Log-transformed NSE.

    Reference: Krause et al. (2005), DOI: 10.5194/adgeo-5-89-2005
    """
    # Add small epsilon to avoid log(0). A pair with obs + eps <= 0 or sim + eps <= 0 has no
    # logarithm and is treated as missing in both series.
    obs_shifted = obs + eps
    sim_shifted = sim + eps
    valid = (obs_shifted > 0) & (sim_shifted > 0)
    obs_log = np.where(valid, np.log(np.where(valid, obs_shifted, 1.0)), np.nan)
    sim_log = np.where(valid, np.log(np.where(valid, sim_shifted, 1.0)), np.nan)
    return _nse_core(obs_log, sim_log, weight=weight, axis=axis, reduction=reduction)


def _modified_nse_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    norm: float | np.ndarray | None = None,
) -> float | np.ndarray:
    """Modified NSE (using absolute values instead of squared).

    Reference: Krause et al. (2005), DOI: 10.5194/adgeo-5-89-2005
    """
    if norm is None:
        norm = _weighted_mean(obs, weight, axis)
        if axis is not None:
            norm = np.expand_dims(norm, axis)
    numerator = np.nansum(np.abs(obs - sim) * (weight if weight is not None else 1), axis=axis)
    denominator = np.nansum(np.abs(obs - norm) * (weight if weight is not None else 1), axis=axis)
    denominator = _drop_negligible(
        denominator, np.nansum(np.abs(obs) * (weight if weight is not None else 1), axis=axis), squared=False
    )
    return 1 - _safe_divide(numerator, denominator)


def _nse_bounded_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Bounded NSE: NSE / (2 - NSE), with values in (-1, 1].

    Reference: No verified primary source
    """
    nse = _nse_core(obs, sim, weight=weight, axis=axis, reduction="none")
    return _safe_divide(nse, 2 - nse)


def _kge_2009_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> tuple[float | np.ndarray, float | np.ndarray, float | np.ndarray, float | np.ndarray]:
    """Kling-Gupta Efficiency (KGE) 2009 version.

    Returns (KGE, r, alpha, beta)

    Reference: Gupta et al. (2009), DOI: 10.1016/j.jhydrol.2009.08.003
    """
    r = _weighted_corr(obs, sim, weight, axis)

    obs_mean = _weighted_mean(obs, weight, axis)
    sim_mean = _weighted_mean(sim, weight, axis)
    beta = _safe_divide(sim_mean, obs_mean)

    obs_std = np.sqrt(_weighted_var(obs, weight, axis, ddof=1))
    sim_std = np.sqrt(_weighted_var(sim, weight, axis, ddof=1))
    alpha = _safe_divide(sim_std, obs_std)

    kge = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
    return kge, r, alpha, beta


def _kge_2012_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> tuple[float | np.ndarray, float | np.ndarray, float | np.ndarray, float | np.ndarray, float | np.ndarray]:
    """Kling-Gupta Efficiency (KGE') 2012 version with gamma component.

    KGE' = 1 - sqrt((r - 1)^2 + (beta - 1)^2 + (gamma - 1)^2). The ratio of
    coefficients of variation gamma replaces the variability ratio alpha of the
    2009 version, so alpha is not a term of the result.

    Returns (KGE, r, alpha, beta, gamma); alpha is returned for information only.

    Reference: Kling et al. (2012), DOI: 10.1016/j.jhydrol.2012.01.011
    """
    r = _weighted_corr(obs, sim, weight, axis)

    obs_mean = _weighted_mean(obs, weight, axis)
    sim_mean = _weighted_mean(sim, weight, axis)
    beta = _safe_divide(sim_mean, obs_mean)

    obs_std = np.sqrt(_weighted_var(obs, weight, axis, ddof=1))
    sim_std = np.sqrt(_weighted_var(sim, weight, axis, ddof=1))
    alpha = _safe_divide(sim_std, obs_std)

    # Gamma: coefficient of variation ratio
    obs_cv = _safe_divide(obs_std, obs_mean)
    sim_cv = _safe_divide(sim_std, sim_mean)
    gamma = _safe_divide(sim_cv, obs_cv)

    kge = 1 - np.sqrt((r - 1) ** 2 + (beta - 1) ** 2 + (gamma - 1) ** 2)
    return kge, r, alpha, beta, gamma


def _r_component_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """KGE r component (correlation)."""
    return _weighted_corr(obs, sim, weight, axis)


def _check_kge_version(version: str) -> None:
    """Raise ValueError for a KGE version other than '2009' or '2012'."""
    if version not in ("2009", "2012"):
        raise ValueError(f"version must be '2009' or '2012', got {version!r}")


def _alpha_component_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    version: Literal["2009", "2012"] = "2012",
) -> float | np.ndarray:
    """KGE alpha component (variability ratio).

    alpha = std(sim) / std(obs) for both versions; ``version`` is validated but has
    no effect on the value. alpha is a term of KGE 2009 only.
    """
    _check_kge_version(version)
    obs_std = np.sqrt(_weighted_var(obs, weight, axis, ddof=1))
    sim_std = np.sqrt(_weighted_var(sim, weight, axis, ddof=1))
    return _safe_divide(sim_std, obs_std)


def _beta_component_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """KGE beta component (bias ratio)."""
    obs_mean = _weighted_mean(obs, weight, axis)
    sim_mean = _weighted_mean(sim, weight, axis)
    return _safe_divide(sim_mean, obs_mean)


def _gamma_component_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """KGE gamma component (coefficient of variation ratio)."""
    obs_mean = _weighted_mean(obs, weight, axis)
    sim_mean = _weighted_mean(sim, weight, axis)
    obs_std = np.sqrt(_weighted_var(obs, weight, axis, ddof=1))
    sim_std = np.sqrt(_weighted_var(sim, weight, axis, ddof=1))
    obs_cv = _safe_divide(obs_std, obs_mean)
    sim_cv = _safe_divide(sim_std, sim_mean)
    return _safe_divide(sim_cv, obs_cv)


def _kge_components_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    version: Literal["2009", "2012"] = "2012",
) -> dict[str, float | np.ndarray]:
    """Compute all KGE components: r, alpha, beta, gamma.

    This is the core implementation used by all backends.
    """
    r = _r_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction)
    alpha = _alpha_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction, version=version)
    beta = _beta_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction)

    result = {"r": r, "alpha": alpha, "beta": beta}

    if version == "2012":
        gamma = _gamma_component_core(obs, sim, weight=weight, axis=axis, reduction=reduction)
        result["gamma"] = gamma

    return result


def _rsr_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Ratio of RMSE to standard deviation of observations (RSR).

    Reference: Moriasi et al. (2007), DOI: 10.13031/2013.23153
    """
    rmse = _rmse_core(obs, sim, weight=weight, axis=axis, reduction="none")
    obs_std = np.sqrt(_weighted_var(obs, weight, axis, ddof=1))
    return _safe_divide(rmse, obs_std)


def _ve_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Volumetric Efficiency (VE).

    Reference: Criss & Winston (2008), DOI: 10.1002/hyp.7072
    """
    numerator = np.nansum(np.abs(obs - sim) * (weight if weight is not None else 1), axis=axis)
    denominator = np.nansum(np.abs(obs) * (weight if weight is not None else 1), axis=axis)
    return 1 - _safe_divide(numerator, denominator)

# ============================================================================
# Probabilistic metrics
# ============================================================================

def _crps_samples(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    fair: bool = False,
) -> np.ndarray:
    """CRPS of every observation, shape of ``obs``.

    Deterministic forecast (``sim.shape == obs.shape``): absolute error.
    Ensemble forecast (``sim.shape == obs.shape + (m,)``, members on the last axis):

        CRPS = mean_j |X_j - o| - 0.5 * sum_jk |X_j - X_k| / D

    with D = m**2 for the classical estimator and D = m * (m - 1) for the fair
    estimator (Ferro, 2014). NaN members are left out and ``m`` is the number of
    valid members. A single-member ensemble reduces to the absolute error.
    """
    if obs.shape == sim.shape:
        return np.abs(obs - sim)
    if sim.ndim != obs.ndim + 1 or sim.shape[:-1] != obs.shape:
        raise ValueError("CRPS: ensemble dimension not found")
    if sim.shape[-1] < 2:
        return np.abs(obs - sim[..., 0])

    valid = ~np.isnan(sim)
    members = valid.sum(axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        term_obs = np.where(valid, np.abs(sim - obs[..., np.newaxis]), 0.0).sum(axis=-1) / members
        pair_ok = valid[..., :, np.newaxis] & valid[..., np.newaxis, :]
        pairs = np.abs(sim[..., :, np.newaxis] - sim[..., np.newaxis, :])
        spread = np.where(pair_ok, pairs, 0.0).sum(axis=(-1, -2))
        denominator = members * (members - 1) if fair else members * members
        return term_obs - 0.5 * spread / denominator


def _crps_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    fair: bool = False,
) -> float | np.ndarray:
    """Continuous Ranked Probability Score (CRPS).

    For an ensemble, ``sim`` has the members on its last axis. The mean (weighted by
    ``weight``) is taken along ``axis`` of ``obs``. With ``reduction="none"`` and no
    ``axis`` an ensemble returns the CRPS of every observation.

    Reference: Hersbach (2000), DOI: 10.1175/1520-0434(2000)015<0559:DOTCRP>2.0.CO;2
    """
    samples = _crps_samples(obs, sim, fair=fair)
    if reduction == "none" and axis is None and obs.shape != sim.shape:
        return samples
    return _weighted_mean(samples, weight, axis)


def _weighted_crps_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "none",
    weight_func: callable | None = None,
) -> float | np.ndarray:
    """Weighted CRPS: mean of the per-observation CRPS weighted by ``weight_func(obs)``
    times ``weight``.

    This is a weighting of observations, not the threshold- or quantile-weighted CRPS
    of Gneiting & Ranjan (2011), which weights the integrand.

    Reference: Gneiting & Ranjan (2011), DOI: 10.1198/jbes.2010.08110
    """
    w = 1.0 if weight_func is None else weight_func(obs)
    if weight is not None:
        w = w * weight
    return _weighted_mean(_crps_samples(obs, sim), w, axis)


def _crpss_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    ref_forecast: np.ndarray | None = None,
) -> float | np.ndarray:
    """CRPSS (CRP Skill Score) relative to a reference forecast.

    CRPSS = 1 - mean(CRPS) / mean(CRPS_ref), the ratio of means taken along ``axis``.
    """
    crps = _weighted_mean(_crps_samples(obs, sim), weight, axis)
    if ref_forecast is None:
        # Use climatology as reference (deterministic mean)
        ref = _weighted_mean(obs, weight, axis)
        if axis is not None:
            ref = np.expand_dims(ref, axis)
        ref_forecast = np.broadcast_to(ref, obs.shape)
    crps_ref = _weighted_mean(_crps_samples(obs, ref_forecast), weight, axis)
    return 1 - _safe_divide(crps, crps_ref)


def _brier_score_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Brier Score for binary events.

    obs: binary (0/1)
    sim: probability in [0,1]

    Reference: Brier (1950), DOI: 10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2
    """
    _check_binary_probability(obs, sim)
    diff = (sim - obs) ** 2
    return _weighted_mean(diff, weight, axis)


def _reliability_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    n_bins: int = 10,
) -> float | np.ndarray:
    """Reliability component of Brier Score decomposition.

    The weights enter the bin weights and the bin means of the probability and the frequency.
    """
    if isinstance(n_bins, (bool, np.bool_)) or not isinstance(n_bins, (int, np.integer)) or n_bins < 1:
        raise ValueError(f"n_bins must be an integer >= 1, got {n_bins!r}")
    _check_binary_probability(obs, sim)
    bins = np.linspace(0, 1, n_bins + 1)

    def one(o, s, w):
        valid = ~(np.isnan(o) | np.isnan(s))
        if w is not None:
            valid &= ~np.isnan(w)
        o, s = o[valid], s[valid]
        w = np.ones(o.shape) if w is None else w[valid]
        total_weight = w.sum()
        if total_weight <= 0:
            return np.nan
        reliability = 0.0
        for i in range(n_bins):
            # Bins are [a, b); the last one is closed on the right so that p == 1 is counted.
            upper = s <= bins[i + 1] if i == n_bins - 1 else s < bins[i + 1]
            mask = (s >= bins[i]) & upper
            bin_weight = w[mask].sum()
            if bin_weight > 0:
                mean_p = np.sum(w[mask] * s[mask]) / bin_weight
                mean_o = np.sum(w[mask] * o[mask]) / bin_weight
                reliability += bin_weight * (mean_p - mean_o) ** 2
        return reliability / total_weight

    return _along_axis(one, obs, sim, weight, axis)


def _sharpness_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Sharpness component of Brier Score decomposition."""
    # Sharpness = variance of forecast probabilities
    return _weighted_var(sim, weight, axis, ddof=0)


# ============================================================================
# Classification metrics
# ============================================================================

def _accuracy_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """Accuracy for binary/multiclass classification."""
    # A pair with a missing value is left out, not counted as a wrong classification.
    valid = ~(np.isnan(obs) | np.isnan(sim))
    correct = np.where(valid, (obs == sim).astype(float), np.nan)
    return _weighted_mean(correct, weight, axis)


def _precision_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    positive_class: int = 1,
) -> float | np.ndarray:
    """Precision for binary classification."""
    tp = ((obs == positive_class) & (sim == positive_class)).astype(float)
    fp = ((obs != positive_class) & (sim == positive_class)).astype(float)
    tp_sum = np.nansum(tp * (weight if weight is not None else 1), axis=axis)
    fp_sum = np.nansum(fp * (weight if weight is not None else 1), axis=axis)
    return _safe_divide(tp_sum, tp_sum + fp_sum)


def _recall_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    positive_class: int = 1,
) -> float | np.ndarray:
    """Recall (Sensitivity) for binary classification."""
    tp = ((obs == positive_class) & (sim == positive_class)).astype(float)
    fn = ((obs == positive_class) & (sim != positive_class)).astype(float)
    tp_sum = np.nansum(tp * (weight if weight is not None else 1), axis=axis)
    fn_sum = np.nansum(fn * (weight if weight is not None else 1), axis=axis)
    return _safe_divide(tp_sum, tp_sum + fn_sum)


def _f1_score_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
    positive_class: int = 1,
) -> float | np.ndarray:
    """F1 Score for binary classification."""
    prec = _precision_core(obs, sim, weight=weight, axis=axis, reduction="none", positive_class=positive_class)
    rec = _recall_core(obs, sim, weight=weight, axis=axis, reduction="none", positive_class=positive_class)
    return _safe_divide(2 * prec * rec, prec + rec)


def _roc_auc_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """ROC AUC for binary classification.

    sim should be probability scores.
    """
    def _auc(o: np.ndarray, s: np.ndarray) -> float:
        valid = ~(np.isnan(o) | np.isnan(s))
        o = o[valid]
        s = s[valid]

        if o.size < 2:
            return np.nan

        positive = o == 1
        n_pos = np.count_nonzero(positive)
        n_neg = o.size - n_pos

        if n_pos == 0 or n_neg == 0:
            return np.nan

        # Rank scores in ascending order, using average ranks for ties.
        order = np.argsort(s, kind="mergesort")
        sorted_s = s[order]
        ranks = np.empty(o.size, dtype=float)
        ranks[order] = np.arange(1, o.size + 1, dtype=float)

        # Assign average ranks to tied scores.
        _, inverse, counts = np.unique(
            sorted_s, return_inverse=True, return_counts=True
        )
        cumulative = np.cumsum(counts)
        starts = cumulative - counts
        average_ranks = (starts + 1 + cumulative) / 2.0
        ranks[order] = average_ranks[inverse]

        rank_sum = np.sum(ranks[positive])

        return float(
            (rank_sum - n_pos * (n_pos + 1) / 2)
            / (n_pos * n_neg)
        )

    return _along_axis(lambda o, s, w: _auc(o, s), obs, sim, None, axis)

def _pr_auc_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """PR AUC (Average Precision) for binary classification."""
    def _average_precision(o: np.ndarray, s: np.ndarray) -> float:
        valid = ~(np.isnan(o) | np.isnan(s))
        o = o[valid]
        s = s[valid]

        if o.size < 2 or len(np.unique(o)) < 2:
            return np.nan

        # Sort scores in descending order.
        order = np.argsort(-s, kind="mergesort")
        o = o[order]
        s = s[order]

        # Evaluate precision and recall at distinct score thresholds.
        distinct = np.r_[np.where(np.diff(s) != 0)[0], o.size - 1]

        true_positives = np.cumsum(o == 1)[distinct]
        predicted_positives = distinct + 1

        precision = true_positives / predicted_positives
        recall = true_positives / np.count_nonzero(o == 1)

        # Average Precision: sum of precision weighted by recall increments.
        return float(np.sum(np.diff(np.r_[0.0, recall]) * precision))

    return _along_axis(lambda o, s, w: _average_precision(o, s), obs, sim, None, axis)



def _edi_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """EDI (Extremal Dependence Index).

    Reference: Ferro & Stephenson (2011), DOI: 10.1175/WAF-D-10-05030.1
    """
    tp = ((obs == 1) & (sim == 1)).astype(float)
    fp = ((obs == 0) & (sim == 1)).astype(float)
    fn = ((obs == 1) & (sim == 0)).astype(float)
    tn = ((obs == 0) & (sim == 0)).astype(float)

    w = weight if weight is not None else 1.0

    tp_sum = np.nansum(tp * w, axis=axis)
    fp_sum = np.nansum(fp * w, axis=axis)
    fn_sum = np.nansum(fn * w, axis=axis)
    tn_sum = np.nansum(tn * w, axis=axis)

    # Hit rate H = a / (a + c)
    H = _safe_divide(tp_sum, tp_sum + fn_sum)
    # False alarm rate F = b / (b + d)
    F = _safe_divide(fp_sum, fp_sum + tn_sum)

    # EDI = (log F - log H) / (log F + log H); undefined (NaN) when H or F is 0
    defined = (H > 0) & (F > 0)
    log_H = np.log(np.where(defined, H, 1.0))
    log_F = np.log(np.where(defined, F, 1.0))

    edi = _safe_divide(log_F - log_H, log_F + log_H)
    # A perfect forecast (H = 1, F = 0) is defined as 1.
    perfect = (H == 1) & (F == 0)
    return np.where(perfect, 1.0, np.where(defined, edi, np.nan))[()]


def _sedi_core(
    obs: np.ndarray,
    sim: np.ndarray,
    *,
    weight: np.ndarray | None = None,
    axis: int | None = None,
    reduction: ReductionType = "mean",
) -> float | np.ndarray:
    """SEDI (Symmetric Extremal Dependence Index).

    Reference: Ferro & Stephenson (2011), DOI: 10.1175/WAF-D-10-05030.1
    """
    tp = ((obs == 1) & (sim == 1)).astype(float)
    fp = ((obs == 0) & (sim == 1)).astype(float)
    fn = ((obs == 1) & (sim == 0)).astype(float)
    tn = ((obs == 0) & (sim == 0)).astype(float)

    w = weight if weight is not None else 1.0

    tp_sum = np.nansum(tp * w, axis=axis)
    fp_sum = np.nansum(fp * w, axis=axis)
    fn_sum = np.nansum(fn * w, axis=axis)
    tn_sum = np.nansum(tn * w, axis=axis)

    H = _safe_divide(tp_sum, tp_sum + fn_sum)
    F = _safe_divide(fp_sum, fp_sum + tn_sum)

    # Undefined (NaN) when H or F is 0 or 1: a logarithm of 0 appears.
    perfect = (H == 1) & (F == 0)
    defined = (H > 0) & (H < 1) & (F > 0) & (F < 1)
    H = np.where(defined, H, 0.5)
    F = np.where(defined, F, 0.5)
    log_H = np.log(H)
    log_F = np.log(F)
    log_1mH = np.log(1 - H)
    log_1mF = np.log(1 - F)

    numerator = log_F - log_H - log_1mF + log_1mH
    denominator = log_F + log_H + log_1mF + log_1mH

    sedi = _safe_divide(numerator, denominator)
    # A perfect forecast (H = 1, F = 0) is defined as 1.
    return np.where(perfect, 1.0, np.where(defined, sedi, np.nan))[()]



