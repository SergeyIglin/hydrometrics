# Variance-Weighted NSE

## Name and Purpose

**Variance-Weighted NSE** — NSE variant for evaluating model performance across multiple stations/rivers simultaneously. Each station is weighted proportionally to the variance of its observations, so stations with greater variability contribute more to the overall score.

Useful for multi-gauge evaluation when a single integrated metric of model quality across the entire monitoring network is needed.

## Mathematical Formula

$$\text{NSE}_{\text{vw}} = 1 - \frac{\sum_{k=1}^{K} w_k \sum_{i=1}^{n_k} (y_{ki} - \hat{y}_{ki})^2}{\sum_{k=1}^{K} w_k \sum_{i=1}^{n_k} (y_{ki} - \bar{y}_k)^2}$$

Where:
- $K$ — number of stations/groups
- $n_k$ — number of observations at station $k$
- $y_{ki}$ — observed value at station $k$, time $i$
- $\hat{y}_{ki}$ — simulated value at station $k$, time $i$
- $\bar{y}_k$ — mean observed value at station $k$
- $w_k = \text{Var}(y_k)$ — weight of station $k$ (variance of its observations)

**Implementation** (`_nse_variance_weighted_core`):
- Computes NSE for each group separately
- Weights numerator and denominator by group variances
- Requires `group` parameter (array-like) specifying group membership
- Supports `nan_policy` and `sentinel`

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Perfect match at all stations |
| **0.0** | On average no better than station means |
| **< 0.0** | On average worse than station means |
| **(-∞, 1.0]** | Theoretical range |

Direction: **maximize**
Ideal value: **1.0**

Stations with greater variability (variance) have higher weight in the final score.

## Public API

```python
from hydrometrics import nse_variance_weighted

result = nse_variance_weighted(
    obs: array-like,
    sim: array-like,
    group: array-like,
    *,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Import**: `from hydrometrics import nse_variance_weighted`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `obs` | array-like | required | Observed values |
| `sim` | array-like | required | Simulated values |
| `group` | array-like | required | Group/station identifiers |
| `weight` | array-like | `None` | Additional sample weights |
| `axis` | int | `None` | Axis for computation |
| `reduction` | str | `"mean"` | Reduction for arrays |
| `nan_policy` | str | `"omit"` | NaN policy |
| `sentinel` | float/list | `None` | Missing value codes |

## Python Example

```python
import numpy as np
from hydrometrics import nse_variance_weighted

# Data: 30 time steps × 3 stations (flattened to 1D)
obs = np.concatenate([
    np.random.normal(100, 20, 10),  # Station 1: mean 100, std 20
    np.random.normal(50, 10, 10),   # Station 2: mean 50, std 10
    np.random.normal(200, 50, 10),  # Station 3: mean 200, std 50 (higher weight)
])
sim = obs + np.random.randn(30) * 5

group = np.array([0]*10 + [1]*10 + [2]*10)  # 3 stations

result = nse_variance_weighted(obs, sim, group)
print(result)
# Variance-Weighted NSE: 0.8723 (direction: maximize, bounds: (-inf, 1.0))
```

## Related Metrics

- [NSE (nse)](../en/metric_reference/hydro/nse.md) — classic NSE for single station
- [KGE 2012 (kge_2012)](../en/metric_reference/hydro/kge_2012.md) — decomposable alternative for multi-gauge evaluation

## Scientific References

1. **Nash, J. E., & Sutcliffe, J. V. (1970).** River flow forecasting through conceptual models part I. *Journal of Hydrology*, 10(3), 282-290. DOI: 10.1016/0022-1694(70)90255-6

2. **Krause, P., Boyle, D. P., & Bäse, F. (2005).** Comparison of different efficiency criteria for hydrological model assessment. *Advances in Geosciences*, 5, 89-97. DOI: 10.5194/adgeo-5-89-2005