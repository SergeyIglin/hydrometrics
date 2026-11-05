# alpha_component (Variability Ratio α)

## Name and Purpose

**alpha_component** — variability component (α) from KGE 2012. Ratio of simulated standard deviation to observed standard deviation. Assesses how well the model reproduces fluctuation amplitude.

## Mathematical Formula

$$\alpha = \frac{\sigma_{\hat{y}}}{\sigma_y} = \frac{\sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(\hat{y}_i - \bar{\hat{y}})^2}}{\sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(y_i - \bar{y})^2}}$$

**Implementation** (`_alpha_core`):
- Ratio of sample standard deviations (ddof=1)
- α > 1: model more variable than observations
- α < 1: model less variable

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Perfect variability match |
| **> 1.0** | Overestimated variability (excessive amplitude) |
| **< 1.0** | Underestimated variability (smoothing) |
| **(0, ∞)** | Theoretical range |

Direction: **maximize** (toward 1.0)
Ideal value: **1.0**

## Public API

```python
from hydrometrics import alpha_component

result = alpha_component(
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

**Import**: `from hydrometrics import alpha_component`

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
from hydrometrics import alpha_component

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = alpha_component(obs, sim)
print(result)
# alpha_component: 0.9654 (direction: maximize, bounds: (0.0, inf))

# α < 1 — model smooths peaks
```

## Related Metrics

- [KGE Components (kge_components)](../en/metric_reference/hydro/kge_components.md) — all three components
- [r_component](../en/metric_reference/hydro/r_component.md) — correlation
- [beta_component](../en/metric_reference/hydro/beta_component.md) — bias
- [gamma_component](../en/metric_reference/hydro/gamma_component.md) — coefficient of variation (KGE 2009)

## Scientific References

1. **Kling, H., Fuchs, M., & Paulin, M. (2012).** Runoff conditions in the upper Danube basin. *Journal of Hydrology*, 424-425, 264-277. DOI: 10.1016/j.jhydrol.2012.01.011