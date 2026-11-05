# Normalized NSE (NNSE)

## Name and Purpose

**Normalized Nash-Sutcliffe Efficiency (NNSE)** — NSE variant normalized to the [0, 1] range. Convenient for interpretation and comparison since values are always non-negative.

Useful when a fixed-range metric is needed for reporting or optimization.

## Mathematical Formula

$$\text{NNSE} = \frac{1}{2 - \text{NSE}} = \frac{1}{2 - \left(1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}\right)} = \frac{\sum (y_i - \bar{y})^2}{\sum (y_i - \bar{y})^2 + \sum (y_i - \hat{y}_i)^2}$$

Where:
- $y_i$ — observed value
- $\hat{y}_i$ — simulated value
- $\bar{y}$ — mean observed value
- $n$ — number of valid pairs

**Implementation** (`_nnse_core`):
- Computes NSE, then applies transformation $1 / (2 - \text{NSE})$
- At NSE = 1 → NNSE = 1.0
- At NSE = 0 → NNSE = 0.5
- As NSE → -∞ → NNSE → 0.0

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Perfect match (sim = obs) |
| **0.5** | Equivalent to NSE = 0 (model = mean) |
| **0.0 – 0.5** | Equivalent to NSE < 0 (worse than mean) |
| **[0, 1]** | Fixed range |

Direction: **maximize**
Ideal value: **1.0**

## Public API

```python
from hydrometrics import nnse

result = nnse(
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

**Import**: `from hydrometrics import nnse`

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
from hydrometrics import nnse

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = nnse(obs, sim)
print(result)
# NNSE: 0.9886 (direction: maximize, bounds: (0.0, 1.0))
```

## Related Metrics

- [NSE (nse)](../en/metric_reference/hydro/nse.md) — classic NSE in range (-∞, 1]
- [Modified NSE (modified_nse)](../en/metric_reference/hydro/modified_nse.md) — absolute errors
- [RSR (rsr)](../en/metric_reference/hydro/rsr.md) — related: RSR² = 1 - NSE

## Scientific References

1. **Nash, J. E., & Sutcliffe, J. V. (1970).** River flow forecasting through conceptual models part I. *Journal of Hydrology*, 10(3), 282-290. DOI: 10.1016/0022-1694(70)90255-6

2. **Moriasi, D. N., et al. (2007).** Model evaluation guidelines for systematic quantification of accuracy in watershed simulations. *Transactions of the ASABE*, 50(3), 885-900.