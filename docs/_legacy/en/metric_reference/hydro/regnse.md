# regNSE (Regime NSE)

## Name and Purpose

**regNSE (Regime Nash-Sutcliffe Efficiency)** — a regime-based NSE that evaluates how well simulated annual flow-duration curves reproduce observed flow regimes.

Unlike classic NSE which compares values at the same time points, regNSE compares *ranked* flow values. For each calendar year, observed and simulated values are independently sorted in descending order, then a regime curve (Q_reg) is computed as the mean observed value for each rank across all years. regNSE is then computed as NSE between the ranked obs and sim values relative to this regime curve.

Reference: Gartsman (2023), DOI: 10.34753/HS.2023.5.3.228.

## Mathematical Formula

For each calendar year:

1. Observed values $y$ are sorted in descending order independently from simulated values $\hat{y}$.
2. Each year is converted to exactly 365 rank positions (for leap years, the two lowest values are averaged).
3. The regime curve $Q_{\text{reg}}$ is computed as the mean observed value for each rank across all years (or provided externally via the `regime` parameter).
4. regNSE is computed as:

$$\text{regNSE} = 1 - \frac{\sum (\hat{y}_{\text{rank}} - y_{\text{rank}})^2}{\sum (y_{\text{rank}} - Q_{\text{reg}})^2}$$

Sums are taken over all years and all 365 rank positions.

**Implementation** (`hydrometrics/backends/numpy.py`, function `_reg_nse_core`):
- Requires `dates` parameter (datetime64[D] array) for grouping by year
- Optional `regime` parameter — precomputed regime curve of shape (365,)
- Does not support `weight`, `axis`, `reduction` (raise NotImplementedError)
- Works only with 1D arrays

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Perfect match of ranked curves |
| **0.0** | Model no better than regime curve |
| **< 0.0** | Model worse than regime curve |
| **(-∞, 1.0]** | Theoretical range |

Optimization direction: **maximize**
Ideal value: **1.0**

regNSE evaluates the match of the *shape* of the flow distribution (flow-duration curve), ignoring timing of individual events.

## Public API

```python
from hydrometrics import regNSE

result = regNSE(
    obs: array-like,
    sim: array-like,
    dates: array-like,
    *,
    regime: array-like | None = None,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Import**: `from hydrometrics import regNSE`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `obs` | array-like | required | Observed values (1D) |
| `sim` | array-like | required | Simulated values (1D, same shape as obs) |
| `dates` | array-like | required | Observation dates (datetime64[D], 1D) |
| `regime` | array-like | `None` | Precomputed regime curve of shape (365,) |
| `weight` | array-like | `None` | **Not supported** (raises NotImplementedError) |
| `axis` | int | `None` | **Not supported** (raises NotImplementedError) |
| `reduction` | str | `"mean"` | **Not used** |
| `nan_policy` | str | `"omit"` | NaN handling policy |
| `sentinel` | float/list | `None` | Missing value codes to convert to NaN |

## Python Example

```python
import numpy as np
from hydrometrics import regNSE

# Create time series: 3 years of daily data
np.random.seed(42)  # For reproducibility
n_days = 3 * 365
dates = np.datetime64('2000-01-01') + np.arange(n_days).astype('timedelta64[D]')
obs = np.abs(np.random.randn(n_days) * 10 + 50)  # Observed flows
sim = obs + np.random.randn(n_days) * 3           # Simulated flows

# Compute regNSE (dates must be passed as keyword argument)
result = regNSE(obs, sim, dates=dates)
print(result)
# Regime Nash-Sutcliffe Efficiency (regNSE): 0.9637 (direction: maximize, bounds: (-inf, 1.0))

# Access attributes
print(f"Value: {float(result):.4f}")
print(f"Reference: {result.reference}")
```

**Expected output** (values will vary due to randomness):
```
Regime Nash-Sutcliffe Efficiency (regNSE): 0.9637 (direction: maximize, bounds: (-inf, 1.0))
Value: 0.9637
Reference: Gartsman, B. I. (2023). Assessing the quality of modeling and forecasting in hydrology – reasoning about the method. Hydrosphere. Hazard Processes and Phenomena, 5(3), 228–243. DOI: 10.34753/HS.2023.5.3.228.
```

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Less than 1 full year of data | Returns `NaN` |
| All observed values constant within a year | Returns `NaN` (division by zero in denominator) |
| `weight`, `axis`, `reduction` passed | Raises `NotImplementedError` |
| Input arrays not 1D | Raises `ValueError` |
| Shape mismatch between `obs`, `sim`, `dates` | Raises `ValueError` |
| `regime` provided but shape not (365,) | Raises `ValueError` |
| NaN present (nan_policy="omit") | Pairwise NaN removal before computation |
| NaN present (nan_policy="propagate") | Returns `NaN` |
| NaN present (nan_policy="raise") | Raises `ValueError` |

## Related Metrics

- [NSE (nse)](../en/metric_reference/hydro/nse.md) — classic NSE (compares values at same time)
- [Forecast Verification (forecast_verification)](../en/metric_reference/hydro/forecast_verification.md) — skill relative to climatology
- [Sigma Skill (ssigma)](../en/metric_reference/hydro/ssigma.md) — combines RMSE with bias penalty

## Scientific References

1. **Gartsman, B. I. (2023).** Assessing the quality of modeling and forecasting in hydrology – reasoning about the method. *Hydrosphere. Hazard Processes and Phenomena*, 5(3), 228–243. DOI: [10.34753/HS.2023.5.3.228](https://doi.org/10.34753/HS.2023.5.3.228)

2. **Nash, J. E., & Sutcliffe, J. V. (1970).** River flow forecasting through conceptual models part I — A discussion of principles. *Journal of Hydrology*, 10(3), 282-290. DOI: [10.1080/02626667009493734](https://doi.org/10.1080/02626667009493734)