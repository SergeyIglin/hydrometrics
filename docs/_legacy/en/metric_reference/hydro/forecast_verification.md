# Forecast Verification (CRPS-based)

## Name and Purpose

**Forecast Verification** — forecast verification metric based on CRPS (Continuous Ranked Probability Score) for deterministic forecasts. Evaluates the quality of probabilistic forecasts represented by ensembles or distributions.

Used for assessing hydrological forecast quality (streamflow, water level) in probabilistic form.

## Mathematical Formula

For deterministic forecast (single forecast per time step):

$$\text{FV} = 1 - \frac{\text{CRPS}(\hat{y}, y)}{\text{CRPS}_{\text{ref}}}$$

Where:
- $\text{CRPS}(\hat{y}, y)$ — CRPS between forecast and observation
- $\text{CRPS}_{\text{ref}}$ — CRPS of reference forecast (climatology/mean)

For ensemble forecast with $M$ members:

$$\text{CRPS} = \frac{1}{M} \sum_{m=1}^{M} |y_m - y| - \frac{1}{2M^2} \sum_{m=1}^{M} \sum_{k=1}^{M} |y_m - y_k|$$

**Implementation** (`_forecast_verification_core`):
- Supports deterministic and ensemble forecasts
- Reference: climatological mean
- Returns skill score (1 = perfect, 0 = like reference, < 0 = worse than reference)

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Perfect forecast |
| **0.0** | No better than climatology |
| **< 0.0** | Worse than climatology |
| **(-∞, 1.0]** | Theoretical range |

Direction: **maximize**
Ideal value: **1.0**

## Public API

```python
from hydrometrics import forecast_verification

result = forecast_verification(
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

**Import**: `from hydrometrics import forecast_verification`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `obs` | array-like | required | Observed values |
| `sim` | array-like | required | Forecasts (1D) or ensemble (2D: time × members) |
| `weight` | array-like | `None` | Sample weights |
| `axis` | int | `None` | Axis for computation |
| `reduction` | str | `"mean"` | Reduction for arrays |
| `nan_policy` | str | `"omit"` | NaN policy |
| `sentinel` | float/list | `None` | Missing value codes |

## Python Example

```python
import numpy as np
from hydrometrics import forecast_verification

# Deterministic forecast
obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = forecast_verification(obs, sim)
print(result)
# Forecast Verification: 0.7234 (direction: maximize, bounds: (-inf, 1.0))

# Ensemble forecast (10 time steps × 50 members)
sim_ensemble = np.random.normal(sim[:, None], 2, size=(10, 50))
result_ens = forecast_verification(obs, sim_ensemble)
print(result_ens)
```

## Related Metrics

- [Forecast Verification Delta (forecast_verification_delta)](../en/metric_reference/hydro/forecast_verification_delta.md) — difference of skill scores
- [CRPS (crps)](../probabilistic/crps.md) — base CRPS metric
- [KGE 2012 (kge_2012)](../en/metric_reference/hydro/kge_2012.md) — for deterministic evaluation

## Scientific References

1. **Hersbach, H. (2000).** Decomposition of the Continuous Ranked Probability Score for ensemble prediction systems. *Weather and Forecasting*, 15(5), 559-570. DOI: 10.1175/1520-0434(2000)015<0559:DOTCRP>2.0.CO;2

2. **Gneiting, T., & Raftery, A. E. (2007).** Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359-378. DOI: 10.1198/016214506000001437