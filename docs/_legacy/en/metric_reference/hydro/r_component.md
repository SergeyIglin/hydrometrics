# r_component (Correlation Component)

## Name and Purpose

**r_component** — Pearson correlation component from KGE. Assesses linear relationship between observed and simulated values, ignoring scale and bias.

Shows how well the model reproduces phase dynamics (hydrograph shape).

## Mathematical Formula

$$r = \frac{\sum_{i=1}^{n} (y_i - \bar{y})(\hat{y}_i - \bar{\hat{y}})}{\sqrt{\sum_{i=1}^{n} (y_i - \bar{y})^2 \sum_{i=1}^{n} (\hat{y}_i - \bar{\hat{y}})^2}}$$

**Implementation** (`_r_core`):
- Standard Pearson correlation
- Sensitive only to shape, not scale/bias

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Perfect linear relationship |
| **0.0** | No linear relationship |
| **-1.0** | Perfect negative relationship |
| **[0, 1]** | For hydrology (negative rare) |

Direction: **maximize**
Ideal value: **1.0**

## Public API

```python
from hydrometrics import r_component

result = r_component(
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

**Import**: `from hydrometrics import r_component`

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
from hydrometrics import r_component

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = r_component(obs, sim)
print(result)
# r_component: 0.9876 (direction: maximize, bounds: (-1.0, 1.0))
```

## Related Metrics

- [KGE Components (kge_components)](../en/metric_reference/hydro/kge_components.md) — all three components at once
- [alpha_component](../en/metric_reference/hydro/alpha_component.md) — variability
- [beta_component](../en/metric_reference/hydro/beta_component.md) — bias
- [gamma_component](../en/metric_reference/hydro/gamma_component.md) — coefficient of variation (KGE 2009)

## Scientific References

1. **Gupta, H. V., et al. (2009).** Decomposition of the mean squared error and NSE performance criteria. *Journal of Hydrology*, 377(1-2), 80-91.
2. **Kling, H., et al. (2012).** Runoff conditions in the upper Danube basin. *Journal of Hydrology*, 424-425, 264-277.