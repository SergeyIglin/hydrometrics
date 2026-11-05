# RSR (Ratio of RMSE to Standard Deviation)

## Name and Purpose

**RSR (RMSE-observations Standard Deviation Ratio)** — ratio of root mean square error to standard deviation of observations. Mathematically related to NSE: $\text{RSR}^2 = 1 - \text{NSE}$.

Used as an alternative interpretable metric: shows how many times the model error is larger/smaller than the natural variability of observations.

## Mathematical Formula

$$\text{RSR} = \frac{\text{RMSE}}{\sigma_y} = \sqrt{\frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y})^2}} = \sqrt{1 - \text{NSE}}$$

Where:
- $y_i$ — observed value
- $\hat{y}_i$ — simulated value
- $\bar{y}$ — mean observed value
- $\sigma_y$ — standard deviation of observations
- $n$ — number of valid pairs

**Implementation** (`_rsr_core`):
- Computes RMSE and standard deviation
- Returns their ratio
- Equivalent to $\sqrt{1 - \text{NSE}}$ (when NSE ≤ 1)

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **0.0** | Perfect match (RMSE = 0) |
| **1.0** | Model error = observation variability (NSE = 0) |
| **> 1.0** | Model error > variability (NSE < 0) |
| **[0, ∞)** | Theoretical range |

**Benchmarks (Moriasi et al., 2007):**
- **< 0.50**: Very good (NSE > 0.75)
- **0.50 – 0.60**: Good (NSE 0.64–0.75)
- **0.60 – 0.70**: Satisfactory (NSE 0.51–0.64)
- **> 0.70**: Unsatisfactory (NSE < 0.51)

Optimization direction: **minimize** (lower is better)
Ideal value: **0.0**

## Public API

```python
from hydrometrics import rsr

result = rsr(
    obs: array-like,
    sim: array-like,
    *,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Import**: `from hydrometrics import rsr`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `obs` | array-like | required | Observed values |
| `sim` | array-like | required | Simulated values |
| `weight` | array-like | `None` | Sample weights |
| `axis` | int | `None` | Axis for computation |
| `reduction` | str | `"mean"` | Reduction for arrays |
| `nan_policy` | str | `"omit"` | NaN policy |
| `sentinel` | float/list | `None` | Missing value codes |

## Python Example

```python
import numpy as np
from hydrometrics import rsr

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = rsr(obs, sim)
print(result)
# RSR: 0.1507 (direction: minimize, bounds: (0.0, inf))

# Relation to NSE
from hydrometrics import nse
nse_result = nse(obs, sim)
print(f"NSE: {float(nse_result):.4f}, RSR²: {float(result)**2:.4f}, 1-NSE: {1-float(nse_result):.4f}")
```

**Expected Output:**
```
RSR: 0.1507 (direction: minimize, bounds: (0.0, inf))
NSE: 0.9772, RSR²: 0.0227, 1-NSE: 0.0228
```

## Related Metrics

- [NSE (nse)](../en/metric_reference/hydro/nse.md) — related: RSR² = 1 - NSE
- [RMSE (rmse)](../regression/rmse.md) — root of MSE
- [KGE 2012 (kge_2012)](../en/metric_reference/hydro/kge_2012.md) — decomposable alternative

## Scientific References

1. **Singh, J., Knapp, H. V., Arnold, J. G., & Demissie, M. (2004).** Hydrological modeling of the Iroquois River watershed using HSPF and SWAT. *Journal of the American Water Resources Association*, 41(2), 343-357. DOI: 10.1111/j.1752-1688.2005.tb03739.x

2. **Moriasi, D. N., et al. (2007).** Model evaluation guidelines for systematic quantification of accuracy in watershed simulations. *Transactions of the ASABE*, 50(3), 885-900. DOI: 10.13031/2013.23153