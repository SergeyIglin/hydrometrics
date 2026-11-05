# beta_component (Bias Ratio β)

## Name and Purpose

**beta_component** — bias component (β) from KGE 2012. Ratio of simulated mean to observed mean. Assesses systematic over- or under-estimation by the model.

## Mathematical Formula

$$\beta = \frac{\bar{\hat{y}}}{\bar{y}} = \frac{\frac{1}{n}\sum_{i=1}^{n}\hat{y}_i}{\frac{1}{n}\sum_{i=1}^{n}y_i}$$

**Implementation** (`_beta_core`):
- Ratio of sample means
- β > 1: systematic overestimation
- β < 1: systematic underestimation

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | No systematic bias |
| **> 1.0** | Systematic overestimation (positive bias) |
| **< 1.0** | Systematic underestimation (negative bias) |
| **(0, ∞)** | Theoretical range |

Direction: **maximize** (toward 1.0)
Ideal value: **1.0**

## Public API

```python
from hydrometrics import beta_component

result = beta_component(
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

**Import**: `from hydrometrics import beta_component`

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
from hydrometrics import beta_component

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = beta_component(obs, sim)
print(result)
# beta_component: 0.9923 (direction: maximize, bounds: (0.0, inf))

# β < 1 — slight systematic underestimation
```

## Related Metrics

- [KGE Components (kge_components)](../en/metric_reference/hydro/kge_components.md) — all three components
- [r_component](../en/metric_reference/hydro/r_component.md) — correlation
- [alpha_component](../en/metric_reference/hydro/alpha_component.md) — variability
- [gamma_component](../en/metric_reference/hydro/gamma_component.md) — coefficient of variation (KGE 2009)
- [PBIAS (pbias)](../en/metric_reference/hydro/pbias.md) — percent bias

## Scientific References

1. **Gupta, H. V., et al. (2009).** Decomposition of the mean squared error and NSE performance criteria. *Journal of Hydrology*, 377(1-2), 80-91.
2. **Kling, H., et al. (2012).** Runoff conditions in the upper Danube basin. *Journal of Hydrology*, 424-425, 264-277.