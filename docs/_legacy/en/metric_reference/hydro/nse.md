# Nash-Sutcliffe Efficiency (NSE)

## Name and Purpose

**Nash-Sutcliffe Efficiency (NSE)** is the classic metric for evaluating hydrological model performance, assessing how well simulated values reproduce observed values compared to using the mean observed value as a naive predictor.

It is used to evaluate the quality of streamflow, water level, precipitation, and other hydrological variable simulations. It has been the de facto standard in hydrology since 1970.

## Mathematical Formula

$$\text{NSE} = 1 - \frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y})^2}$$

Where:
- $y_i$ — observed value at time $i$
- $\hat{y}_i$ — simulated value at time $i$
- $\bar{y} = \frac{1}{n}\sum_{i=1}^{n} y_i$ — mean observed value
- $n$ — number of valid observation pairs (after NaN removal)

**Implementation in code** (`hydrometrics/backends/numpy.py`, function `_nse_core`):
- Denominator: sum of squared deviations from the mean of observations (with weights if provided)
- Numerator: sum of squared modeling errors
- Uses `np.nansum` for automatic NaN ignoring
- Supports weighted computation via `weight` parameter
- Supports `axis` and `reduction` for multidimensional arrays

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Perfect match (sim = obs) |
| **0.0** | Model no better than using mean of observations as predictor |
| **< 0.0** | Model worse than mean of observations |
| **(-∞, 1.0]** | Theoretical range |

**Hydrological benchmarks (Moriasi et al., 2007):**
- **> 0.75**: Very good
- **0.65 – 0.75**: Good
- **0.50 – 0.65**: Satisfactory
- **< 0.50**: Unsatisfactory

Optimization direction: **maximize** (higher is better)
Ideal value: **1.0**

## Public API

```python
from hydrometrics import nse

result = nse(
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

**Import**: `from hydrometrics import nse`

## Parameters and Return Value

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `obs` | array-like | required | Observed values |
| `sim` | array-like | required | Simulated values |
| `weight` | array-like | `None` | Sample weights (broadcastable to obs/sim) |
| `axis` | int | `None` | Axis along which to compute (None = flatten) |
| `reduction` | str | `"mean"` | `"mean"`, `"sum"`, or `"none"` |
| `nan_policy` | str | `"omit"` | `"omit"`, `"propagate"`, `"raise"` |
| `sentinel` | float/list | `None` | Missing value codes to convert to NaN |

**Returns**: `MetricResult` with attributes:
- `value`: float or ndarray — NSE value
- `direction`: `"maximize"`
- `bounds`: `(-np.inf, 1.0)`
- `name`: `"Nash-Sutcliffe Efficiency"`
- `reference`: `"Nash & Sutcliffe (1970), DOI: 10.1016/0022-1694(70)90255-6"`
- `parameters`: dict with used parameters
- `nan_info`: dict with NaN handling information
- `meta`: dict with description and formula

## Python Example

```python
import numpy as np
from hydrometrics import nse

# Observed and simulated streamflow (m³/s)
obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

# Compute NSE
result = nse(obs, sim)

print(result)
# NSE: 0.9772 (direction: maximize, bounds: (-inf, 1.0))

# Access individual attributes
print(f"Value: {float(result):.4f}")
print(f"Direction: {result.direction}")
print(f"Bounds: {result.bounds}")
print(f"Reference: {result.reference}")
```

**Expected output:**
```
NSE: 0.9772 (direction: maximize, bounds: (-inf, 1.0))
Value: 0.9772
Direction: maximize
Bounds: (-inf, 1.0)
Reference: Nash & Sutcliffe (1970), DOI: 10.1016/0022-1694(70)90255-6
```

## Working with Multidimensional Data

```python
import numpy as np
from hydrometrics import nse

# 2D data: 10 time steps × 3 stations
obs_2d = np.random.rand(10, 3) * 100
sim_2d = obs_2d + np.random.randn(10, 3) * 5

# NSE per station (axis=0)
result_per_station = nse(obs_2d, sim_2d, axis=0, reduction="none")
print(result_per_station.value)  # array([0.92, 0.89, 0.95])

# Mean NSE across all stations
result_mean = nse(obs_2d, sim_2d, axis=0, reduction="mean")
print(float(result_mean))  # 0.92
```

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| All `obs` constant (variance = 0) | Returns `NaN` (division by zero) |
| Fewer than 2 valid pairs after NaN removal | Returns `NaN` |
| NaN present (nan_policy="omit") | Pairwise NaN removal, compute on remaining |
| NaN present (nan_policy="propagate") | Returns `NaN` |
| NaN present (nan_policy="raise") | Raises `ValueError` |
| Sentinel values (-999, -9999) | Converted to NaN before computation via `sentinel` parameter |

## Related Metrics

- [Log NSE (log_nse)](../en/metric_reference/hydro/log_nse.md) — log transformation for low-flow emphasis
- [Modified NSE (modified_nse)](../en/metric_reference/hydro/modified_nse.md) — absolute errors (j=1)
- [Normalized NSE (nnse)](../en/metric_reference/hydro/nnse.md) — normalized version in [0, 1] range
- [Variance-Weighted NSE (nse_variance_weighted)](../en/metric_reference/hydro/nse_variance_weighted.md) — multi-gauge evaluation
- [RSR (rsr)](../en/metric_reference/hydro/rsr.md) — related via RSR² = 1 - NSE
- [KGE 2012 (kge_2012)](../en/metric_reference/hydro/kge_2012.md) — decomposable alternative

## Scientific References

1. **Nash, J. E., & Sutcliffe, J. V. (1970).** River flow forecasting through conceptual models part I — A discussion of principles. *Journal of Hydrology*, 10(3), 282-290. DOI: [10.1016/0022-1694(70)90255-6](https://doi.org/10.1016/0022-1694(70)90255-6)

2. **Moriasi, D. N., Arnold, J. G., Van Liew, M. W., Bingner, R. L., Harmel, R. D., & Veith, T. L. (2007).** Model evaluation guidelines for systematic quantification of accuracy in watershed simulations. *Transactions of the ASABE*, 50(3), 885-900. DOI: [10.13031/2013.23153](https://doi.org/10.13031/2013.23153)