# Forecast Verification Delta

## Name and Purpose

**Forecast Verification Delta** — difference of skill scores between two forecasts. Allows comparing the quality of two forecasts (e.g., new model vs baseline) on the same scale.

Useful for A/B testing models: how much better/worse is the new forecast compared to the old one.

## Mathematical Formula

$$\text{FV}_{\Delta} = \text{FV}(\text{sim}_1) - \text{FV}(\text{sim}_2)$$

Where:
- $\text{FV}(\text{sim}_1)$ — Forecast Verification for forecast 1
- $\text{FV}(\text{sim}_2)$ — Forecast Verification for forecast 2 (reference)

**Implementation** (`_forecast_verification_delta_core`):
- Computes FV for both forecasts
- Returns the difference
- Positive value = forecast 1 better than forecast 2

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **> 0** | Forecast 1 better than forecast 2 |
| **0** | Forecasts equivalent |
| **< 0** | Forecast 2 better than forecast 1 |
| **(-1, 1)** | Typical range |

Direction: **maximize** (higher = forecast 1 better)

## Public API

```python
from hydrometrics import forecast_verification_delta

result = forecast_verification_delta(
    obs: array-like,
    sim1: array-like,
    sim2: array-like,
    *,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Import**: `from hydrometrics import forecast_verification_delta`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `obs` | array-like | required | Observed values |
| `sim1` | array-like | required | Forecast 1 (test) |
| `sim2` | array-like | required | Forecast 2 (reference/baseline) |
| `weight` | array-like | `None` | Sample weights |
| `axis` | int | `None` | Axis for computation |
| `reduction` | str | `"mean"` | Reduction for arrays |
| `nan_policy` | str | `"omit"` | NaN policy |
| `sentinel` | float/list | `None` | Missing value codes |

## Python Example

```python
import numpy as np
from hydrometrics import forecast_verification_delta

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim_new = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])
sim_old = np.array([8.0, 10.0, 13.0, 12.0, 12.0, 9.0, 7.0, 6.0, 5.0, 7.0])

result = forecast_verification_delta(obs, sim_new, sim_old)
print(result)
# Forecast Verification Delta: 0.1523 (direction: maximize, bounds: (-1.0, 1.0))

# Positive value = new model better than old
```

## Related Metrics

- [Forecast Verification (forecast_verification)](../en/metric_reference/hydro/forecast_verification.md) — base metric
- [CRPS (crps)](../probabilistic/crps.md) — base probabilistic metric
- [KGE 2012 (kge_2012)](../en/metric_reference/hydro/kge_2012.md) — for deterministic comparison

## Scientific References

1. **Hersbach, H. (2000).** Decomposition of the Continuous Ranked Probability Score for ensemble prediction systems. *Weather and Forecasting*, 15(5), 559-570. DOI: 10.1175/1520-0434(2000)015<0559:DOTCRP>2.0.CO;2

2. **Gneiting, T., & Raftery, A. E. (2007).** Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359-378. DOI: 10.1198/016214506000001437