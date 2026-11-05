# KGE Components (r, α, β, γ)

## Name and Purpose

**KGE Components** — function returning the KGE components separately: correlation (r), variability (α), bias (β), and optionally coefficient of variation ratio (γ). Enables detailed model error diagnosis without aggregation into a single scalar.

Useful for deep diagnosis: understanding which specific component needs improvement.

## Mathematical Formula

Returns components depending on version:

**Version 2012 (default):**
- **r** (correlation): $\text{corr}(y, \hat{y})$ — Pearson correlation
- **α** (alpha): $\frac{\sigma_{\hat{y}}}{\sigma_y}$ — ratio of standard deviations
- **β** (beta): $\frac{\bar{\hat{y}}}{\bar{y}}$ — ratio of means
- **γ** (gamma): $\frac{\text{CV}_{\hat{y}}}{\text{CV}_y} = \frac{\sigma_{\hat{y}} / \bar{\hat{y}}}{\sigma_y / \bar{y}}$ — ratio of coefficients of variation

**Version 2009:**
- **r** (correlation): $\text{corr}(y, \hat{y})$ — Pearson correlation
- **α** (alpha): $\frac{\sigma_{\hat{y}}}{\sigma_y}$ — ratio of standard deviations
- **β** (beta): $\frac{\bar{\hat{y}}}{\bar{y}}$ — ratio of means
- (no γ component)

**Implementation** (`_kge_components_core`):
- Computes all components in one pass
- Returns `MetricResult` with `value` as dict of components
- Supports `axis`, `reduction`, and `version` parameter

## Component Interpretation

| Component | Ideal Value | Interpretation of Deviation |
|-----------|-------------|----------------------------|
| **r** | 1.0 | < 1: poor phase synchronization |
| **α** | 1.0 | > 1: overestimated variability; < 1: underestimated |
| **β** | 1.0 | > 1: systematic overestimation; < 1: systematic underestimation |
| **γ** (2012 only) | 1.0 | > 1: overestimated CV ratio; < 1: underestimated |

Direction for all: **maximize** (toward 1.0)

## Public API

```python
from hydrometrics import kge_components

result = kge_components(
    obs: array-like,
    sim: array-like,
    *,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    version: Literal["2009", "2012"] = "2012",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Import**: `from hydrometrics import kge_components`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `obs` | array-like | required | Observed values |
| `sim` | array-like | required | Simulated values |
| `weight` | array-like | `None` | Sample weights |
| `axis` | int | `None` | Axis for computation |
| `reduction` | str | `"mean"` | Reduction for arrays |
| `version` | str | `"2012"` | `"2009"` or `"2012"` |
| `nan_policy` | str | `"omit"` | NaN policy |
| `sentinel` | float/list | `None` | Missing value codes |

**Returns**: `MetricResult` with `value` as dict: `{"r": float, "alpha": float, "beta": float, "gamma": float}` (gamma only for version="2012")

## Python Example

```python
import numpy as np
from hydrometrics import kge_components

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

# Version 2012 (default, 4 components)
result = kge_components(obs, sim)
print(f"r (correlation): {result.value['r']:.4f}")
print(f"α (variability): {result.value['alpha']:.4f}")
print(f"β (bias): {result.value['beta']:.4f}")
print(f"γ (CV ratio): {result.value['gamma']:.4f}")

# KGE 2012 can be reconstructed:
kge_2012 = 1 - np.sqrt((result.value['r']-1)**2 + (result.value['alpha']-1)**2 + (result.value['beta']-1)**2 + (result.value['gamma']-1)**2)
print(f"KGE 2012: {kge_2012:.4f}")

# Version 2009 (3 components)
result_2009 = kge_components(obs, sim, version="2009")
print(f"Version 2009 components: {result_2009.value}")
```

**Expected output:**
```
r (correlation): 0.9940
α (variability): 1.0563
β (bias): 0.9806
γ (CV ratio): 1.0773
KGE 2012: 0.9022
Version 2009 components: {'r': 0.9940, 'alpha': 1.0563, 'beta': 0.9806}
```

## Model Diagnosis by Components

| Problem | r | α | β | Action |
|---------|---|---|---|--------|
| Phase shift | ↓ | ~1 | ~1 | Improve routing/phase |
| Wrong amplitude | ~1 | ≠1 | ~1 | Calibrate runoff generation params |
| Systematic bias | ~1 | ~1 | ≠1 | Adjust input data/parameters |

## Related Metrics

- [KGE 2012 (kge_2012)](../en/metric_reference/hydro/kge_2012.md) — aggregated metric
- [KGE 2009 (kge_2009)](../en/metric_reference/hydro/kge_2009.md) — version with γ instead of α
- [Individual components](../en/metric_reference/hydro/r_component.md) — r_component, alpha_component, beta_component, gamma_component

## Scientific References

1. **Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009).** Decomposition of the mean squared error and NSE performance criteria. *Journal of Hydrology*, 377(1-2), 80-91. DOI: 10.1016/j.jhydrol.2009.08.003

2. **Kling, H., Fuchs, M., & Paulin, M. (2012).** Runoff conditions in the upper Danube basin. *Journal of Hydrology*, 424-425, 264-277. DOI: 10.1016/j.jhydrol.2012.01.011