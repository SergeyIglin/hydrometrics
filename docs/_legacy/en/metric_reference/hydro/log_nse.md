# Log-Transformed NSE (Log NSE)

## Name and Purpose

**Log-Transformed Nash-Sutcliffe Efficiency (Log NSE)** is an NSE variant applied to log-transformed data. It emphasizes low flows since the log compresses large values and stretches small ones.

Recommended for evaluating model performance during low-flow periods where relative error matters more than absolute error.

## Mathematical Formula

$$\text{Log NSE} = 1 - \frac{\sum_{i=1}^{n} (\ln(y_i + \epsilon) - \ln(\hat{y}_i + \epsilon))^2}{\sum_{i=1}^{n} (\ln(y_i + \epsilon) - \overline{\ln(y + \epsilon)})^2}$$

Where:
- $y_i$ — observed value
- $\hat{y}_i$ — simulated value
- $\epsilon$ — offset constant (default 0.001) to avoid $\ln(0)$
- $\overline{\ln(y + \epsilon)}$ — mean of log-transformed observations
- $n$ — number of valid pairs

**Implementation** (`_log_nse_core`):
- Applies `np.log(obs + eps)` and `np.log(sim + eps)` before NSE computation
- Offset `eps` defaults to 0.001 (configurable via `eps` parameter)
- Supports same parameters as NSE

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Perfect match in log-space |
| **0.0** | No better than mean in log-space |
| **< 0.0** | Worse than mean in log-space |
| **(-∞, 1.0]** | Theoretical range |

Direction: **maximize**
Ideal value: **1.0**

Sensitive to systematic errors on low flows.

## Public API

```python
from hydrometrics import log_nse

result = log_nse(
    obs: array-like,
    sim: array-like,
    *,
    eps: float = 0.001,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Import**: `from hydrometrics import log_nse`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `obs` | array-like | required | Observed values (> -eps) |
| `sim` | array-like | required | Simulated values (> -eps) |
| `eps` | float | `0.001` | Offset to avoid log(0) |
| `weight` | array-like | `None` | Sample weights |
| `axis` | int | `None` | Axis for computation |
| `reduction` | str | `"mean"` | Reduction for arrays |
| `nan_policy` | str | `"omit"` | NaN policy |
| `sentinel` | float/list | `None` | Missing value codes |

## Python Example

```python
import numpy as np
from hydrometrics import log_nse

# Data with low flows
obs = np.array([0.5, 1.2, 0.8, 0.3, 2.1, 0.6, 0.4, 0.9, 0.2, 1.0])
sim = np.array([0.45, 1.1, 0.85, 0.35, 2.0, 0.55, 0.45, 0.85, 0.25, 0.95])

result = log_nse(obs, sim)
print(result)
# Log NSE: 0.9642 (direction: maximize, bounds: (-inf, 1.0))
```

**Expected Output:**
```
Log NSE: 0.9642 (direction: maximize, bounds: (-inf, 1.0))
```

## Edge Cases

- Values ≤ -offset cause error or NaN (log undefined)
- offset must be > 0
- Same NaN policies as NSE

## Related Metrics

- [NSE (nse)](../en/metric_reference/hydro/nse.md)
- [Modified NSE (modified_nse)](../en/metric_reference/hydro/modified_nse.md)
- [KGE 2012 (kge_2012)](../en/metric_reference/hydro/kge_2012.md)

## Scientific References

1. **Nash, J. E., & Sutcliffe, J. V. (1970).** River flow forecasting through conceptual models part I. *Journal of Hydrology*, 10(3), 282-290. DOI: 10.1016/0022-1694(70)90255-6

2. **Krause, P., Boyle, D. P., & Bäse, F. (2005).** Comparison of different efficiency criteria for hydrological model assessment. *Advances in Geosciences*, 5, 89-97. DOI: 10.5194/adgeo-5-89-2005