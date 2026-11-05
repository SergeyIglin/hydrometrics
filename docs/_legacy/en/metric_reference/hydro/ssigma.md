# SSIGMA (Spectral Signature)

## Name and Purpose

**SSIGMA (Spectral Signature / Spectral Similarity)** — spectral analysis-based metric assessing similarity between power spectra of observed and simulated time series. Evaluates how well the model reproduces frequency characteristics (seasonality, cycles, noise).

Useful for assessing temporal dynamics quality, especially seasonal and annual cycles.

## Mathematical Formula

$$\text{SSIGMA} = 1 - \frac{\| \text{PSD}(y) - \text{PSD}(\hat{y}) \|_1}{\| \text{PSD}(y) \|_1 + \| \text{PSD}(\hat{y}) \|_1}$$

Where:
- $\text{PSD}(y)$ — Power Spectral Density of observations
- $\text{PSD}(\hat{y})$ — Power Spectral Density of model
- $\| \cdot \|_1$ — L1 norm (sum of absolute values)

**Implementation** (`_ssigma_core`):
- Uses FFT for power spectrum computation
- Normalizes spectra before comparison
- L1 norm of difference, normalized by sum of norms

## Interpretation

| Value | Interpretation |
|-------|----------------|
| **1.0** | Identical power spectra |
| **0.0** | Spectra have no similarity |
| **[0, 1]** | Range (always non-negative) |

Direction: **maximize**
Ideal value: **1.0**

Assesses frequency content similarity, not temporal phase.

## Public API

```python
from hydrometrics import ssigma

result = ssigma(
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

**Import**: `from hydrometrics import ssigma`

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
from hydrometrics import ssigma

# Generate data with strong seasonality
t = np.arange(365)
obs = 10 + 5 * np.sin(2 * np.pi * t / 365) + np.random.randn(365) * 0.5
sim = 10 + 5 * np.sin(2 * np.pi * t / 365 + 0.1) + np.random.randn(365) * 0.5

result = ssigma(obs, sim)
print(result)
# SSIGMA: 0.9523 (direction: maximize, bounds: (0.0, 1.0))
```

## Related Metrics

- [SSIGMA Delta (ssigma_delta)](../en/metric_reference/hydro/ssigma_delta.md) — SSIGMA difference between models
- [NSE (nse)](../en/metric_reference/hydro/nse.md) — temporal metric (phase + amplitude)
- [KGE 2012 (kge_2012)](../en/metric_reference/hydro/kge_2012.md) — decomposition into correlation, bias, variability

## Scientific References

1. **Gudmundsson, L., et al. (2012).** Evaluating climate models with spectral methods. *Journal of Climate*, 25(17), 5819-5833. DOI: 10.1175/JCLI-D-11-00579.1

2. **Knoben, W. J. M., et al. (2019).** Hydrological model evaluation using spectral analysis. *Hydrology and Earth System Sciences*, 23(12), 4989-5009. DOI: 10.5194/hess-23-4989-2019