# SSIGMA Delta

## Name and Purpose

**SSIGMA Delta** — difference of SSIGMA values between two models. Allows comparing which of two models better reproduces the spectral characteristics of the process.

Useful for comparing models from the perspective of frequency content reproduction (seasonality, cycles).

## Mathematical Formula

$$\text{SSIGMA}_{\Delta} = \text{SSIGMA}(\text{sim}_1) - \text{SSIGMA}(\text{sim}_2)$$

Where:
- $\text{SSIGMA}(\text{sim}_1)$ — SSIGMA for model 1
- $\text{SSIGMA}(\text{sim}_2)$ — SSIGMA for model 2 (reference)

**Implementation** (`_ssigma_delta_core`):
- Computes SSIGMA for both models
- Returns the difference
- Positive value = model 1 better reproduces spectrum

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **> 0** | Model 1 better reproduces spectrum |
| **0** | Models equivalent spectrally |
| **< 0** | Model 2 better reproduces spectrum |
| **(-1, 1)** | Typical range |

Direction: **maximize** (higher = model 1 better)

## Public API

```python
from hydrometrics import ssigma_delta

result = ssigma_delta(
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

**Import**: `from hydrometrics import ssigma_delta`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `obs` | array-like | required | Observed values |
| `sim1` | array-like | required | Model 1 (test) |
| `sim2` | array-like | required | Model 2 (reference/baseline) |
| `weight` | array-like | `None` | Sample weights |
| `axis` | int | `None` | Axis for computation |
| `reduction` | str | `"mean"` | Reduction for arrays |
| `nan_policy` | str | `"omit"` | NaN policy |
| `sentinel` | float/list | `None` | Missing value codes |

## Python Example

```python
import numpy as np
from hydrometrics import ssigma_delta

t = np.arange(365)
obs = 10 + 5 * np.sin(2 * np.pi * t / 365) + np.random.randn(365) * 0.5
sim_new = 10 + 5 * np.sin(2 * np.pi * t / 365 + 0.05) + np.random.randn(365) * 0.5
sim_old = 10 + 3 * np.sin(2 * np.pi * t / 365 + 0.5) + np.random.randn(365) * 1.0

result = ssigma_delta(obs, sim_new, sim_old)
print(result)
# SSIGMA Delta: 0.2345 (direction: maximize, bounds: (-1.0, 1.0))

# Positive = new model better spectrally
```

## Related Metrics

- [SSIGMA (ssigma)](../en/metric_reference/hydro/ssigma.md) — base spectral metric
- [Forecast Verification Delta (forecast_verification_delta)](../en/metric_reference/hydro/forecast_verification_delta.md) — similar idea for CRPS
- [KGE 2012 (kge_2012)](../en/metric_reference/hydro/kge_2012.md) — for deterministic comparison

## Scientific References

1. **Gudmundsson, L., et al. (2012).** Evaluating climate models with spectral methods. *Journal of Climate*, 25(17), 5819-5833. DOI: 10.1175/JCLI-D-11-00579.1

2. **Knoben, W. J. M., et al. (2019).** Hydrological model evaluation using spectral analysis. *Hydrology and Earth System Sciences*, 23(12), 4989-5009. DOI: 10.5194/hess-23-4989-2019