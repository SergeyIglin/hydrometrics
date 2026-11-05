# gamma_component (Coefficient of Variation Ratio γ)

## Name and Purpose

**gamma_component** — γ component from KGE 2009. Ratio of coefficients of variation of simulated and observed values. Used in original KGE 2009 instead of α (variability ratio).

$$\gamma = \frac{CV_{\hat{y}}}{CV_y} = \frac{\sigma_{\hat{y}} / \bar{\hat{y}}}{\sigma_y / \bar{y}} = \alpha / \beta$$

Assesses variability relative to the mean (coefficient of variation).

## Mathematical Formula

$$\gamma = \frac{\frac{\sigma_{\hat{y}}}{\bar{\hat{y}}}}{\frac{\sigma_y}{\bar{y}}} = \frac{\sigma_{\hat{y}} \bar{y}}{\sigma_y \bar{\hat{y}}} = \frac{\alpha}{\beta}$$

**Implementation** (`_gamma_core`):
- Ratio of coefficients of variation
- γ = α / β (direct link to KGE 2012 components)

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Matching coefficients of variation |
| **> 1.0** | Model more variable relative to its mean |
| **< 1.0** | Model less variable relative to its mean |
| **(0, ∞)** | Theoretical range |

Direction: **maximize** (toward 1.0)
Ideal value: **1.0**

## Public API

```python
from hydrometrics import gamma_component

result = gamma_component(
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

**Import**: `from hydrometrics import gamma_component`

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
from hydrometrics import gamma_component, alpha_component, beta_component

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

gamma = gamma_component(obs, sim)
alpha = alpha_component(obs, sim)
beta = beta_component(obs, sim)

print(f"γ: {gamma.value:.4f}")
print(f"α: {alpha.value:.4f}")
print(f"β: {beta.value:.4f}")
print(f"α/β: {alpha.value/beta.value:.4f}")
# γ ≈ α/β
```

## Related Metrics

- [KGE 2009 (kge_2009)](../en/metric_reference/hydro/kge_2009.md) — uses γ instead of α
- [KGE 2012 (kge_2012)](../en/metric_reference/hydro/kge_2012.md) — uses α and β separately
- [KGE Components (kge_components)](../en/metric_reference/hydro/kge_components.md) — α, β (γ not included)
- [alpha_component](../en/metric_reference/hydro/alpha_component.md) — α
- [beta_component](../en/metric_reference/hydro/beta_component.md) — β

## Scientific References

1. **Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009).** Decomposition of the mean squared error and NSE performance criteria. *Journal of Hydrology*, 377(1-2), 80-91. DOI: 10.1016/j.jhydrol.2009.08.003

2. **Kling, H., Fuchs, M., & Paulin, M. (2012).** Runoff conditions in the upper Danube basin. *Journal of Hydrology*, 424-425, 264-277. DOI: 10.1016/j.jhydrol.2012.01.011