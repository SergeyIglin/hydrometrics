# VE (Volumetric Efficiency)

## Name and Purpose

**VE (Volumetric Efficiency)** — metric assessing how well the simulated total volume matches the observed volume. Unlike NSE, it is insensitive to temporal phase and only considers total volume.

Useful for water balance evaluation: does the model correctly reproduce the total streamflow volume?

## Mathematical Formula

$$\text{VE} = 1 - \frac{\sum_{i=1}^{n} |y_i - \hat{y}_i|}{\sum_{i=1}^{n} |y_i|}$$

Where:
- $y_i$ — observed value
- $\hat{y}_i$ — simulated value
- $n$ — number of valid pairs

**Implementation** (`_ve_core`):
- Numerator: sum of absolute errors (L1 norm of errors)
- Denominator: sum of absolute observations
- VE = 1 — perfect volume match
- VE = 0 — equivalent to zero simulation

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Perfect volume match |
| **0.0** | Equivalent to zero simulation |
| **< 0.0** | Volume error exceeds observation volume |
| **(-∞, 1.0]** | Theoretical range |

Direction: **maximize**
Ideal value: **1.0**

Does not account for temporal dynamics — only total volume.

## Public API

```python
from hydrometrics import ve

result = ve(
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

**Import**: `from hydrometrics import ve`

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
from hydrometrics import ve

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = ve(obs, sim)
print(result)
# VE: 0.9723 (direction: maximize, bounds: (-inf, 1.0))
```

## Related Metrics

- [PBIAS (pbias)](../en/metric_reference/hydro/pbias.md) — percent bias (only bias, no absolute errors)
- [NSE (nse)](../en/metric_reference/hydro/nse.md) — accounts for both phase and amplitude
- [Modified NSE (modified_nse)](../en/metric_reference/hydro/modified_nse.md) — uses absolute errors

## Scientific References

1. **Criss, R. E., & Winston, W. E. (2008).** Do Nash values have value? Discussion and alternate proposals. *Hydrological Processes*, 22(14), 2723-2725. DOI: 10.1002/hyp.7072

2. **Criss, R. E., & Winston, W. E. (2008).** Reply to commentary on "Do Nash values have value?". *Hydrological Processes*, 22(14), 2735-2737. DOI: 10.1002/hyp.6989