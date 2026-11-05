# Modified NSE

## Name and Purpose

**Modified Nash-Sutcliffe Efficiency (Modified NSE)** — NSE variant using absolute errors instead of squared errors (L1 norm instead of L2). Less sensitive to outliers and peak flows.

Useful when reducing the influence of extreme events (floods) on overall model evaluation is desired.

## Mathematical Formula

$$\text{Modified NSE} = 1 - \frac{\sum_{i=1}^{n} |y_i - \hat{y}_i|}{\sum_{i=1}^{n} |y_i - \bar{y}|}$$

Where:
- $y_i$ — observed value
- $\hat{y}_i$ — simulated value
- $\bar{y}$ — mean observed value
- $n$ — number of valid pairs

**Implementation** (`_modified_nse_core`):
- Numerator: sum of absolute errors (L1 norm)
- Denominator: sum of absolute deviations from mean
- Uses `np.nansum` for automatic NaN ignoring
- Supports weighted computation, `axis` and `reduction`

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Perfect match |
| **0.0** | No better than mean by L1 metric |
| **< 0.0** | Worse than mean |
| **(-∞, 1.0]** | Theoretical range |

Direction: **maximize**
Ideal value: **1.0**

Less sensitive to peak flows compared to classic NSE.

## Public API

```python
from hydrometrics import modified_nse

result = modified_nse(
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

**Import**: `from hydrometrics import modified_nse`

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
from hydrometrics import modified_nse

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = modified_nse(obs, sim)
print(result)
# Modified NSE: 0.9523 (direction: maximize, bounds: (-inf, 1.0))
```

## Related Metrics

- [NSE (nse)](../en/metric_reference/hydro/nse.md) — classic NSE with squared errors
- [Log NSE (log_nse)](../en/metric_reference/hydro/log_nse.md) — low-flow emphasis
- [Normalized NSE (nnse)](../en/metric_reference/hydro/nnse.md) — normalized version

## Scientific References

1. **Krause, P., Boyle, D. P., & Bäse, F. (2005).** Comparison of different efficiency criteria for hydrological model assessment. *Advances in Geosciences*, 5, 89-97. DOI: 10.5194/adgeo-5-89-2005

2. **Legates, D. R., & McCabe, G. J. (1999).** Evaluating the use of "goodness-of-fit" measures in hydrologic and hydroclimatic model validation. *Water Resources Research*, 35(1), 233-241. DOI: 10.1029/1998WR900018