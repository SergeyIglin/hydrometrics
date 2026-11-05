# Hydrological Metrics

**Complete Reference for Hydrological Metrics in HydroMetrics**

This section contains all hydrological metrics implemented in the library. Each metric has its own dedicated page with a verified mathematical formula, explanation, and working Python example.

## Hydrological Metric Categories

### NSE Family (Nash-Sutcliffe Efficiency)
Metrics based on the ratio of error sum of squares to observation variance.

| Metric | Function | Direction | Bounds | Description |
|--------|----------|-----------|--------|-------------|
| **Nash-Sutcliffe Efficiency** | `nse` | maximize | (-∞, 1.0] | Classic model performance metric |
| **Log-Transformed NSE** | `log_nse` | maximize | (-∞, 1.0] | Emphasizes low flows via log transformation |
| **Modified NSE** | `modified_nse` | maximize | (-∞, 1.0] | Uses absolute errors (j=1) or squared (j=2) |
| **Normalized NSE** | `nnse` | maximize | [0, 1] | Bounded variant of NSE in [0, 1] range |
| **Variance-Weighted NSE** | `nse_variance_weighted` | maximize | (-∞, 1.0] | Multi-gauge NSE weighted by observed variance |

### KGE Family (Kling-Gupta Efficiency)
Decomposable efficiency metrics separating correlation, variability, and bias.

| Metric | Function | Direction | Bounds | Description |
|--------|----------|-----------|--------|-------------|
| **KGE 2009 (original)** | `kge_2009` | maximize | (-∞, 1.0] | Three components: r, α, β |
| **KGE 2012 (modified)** | `kge_2012` | maximize | (-∞, 1.0] | Four components: r, α, β, γ (recommended) |
| **KGE Components** | `kge_components` | — | — | Returns dict with all components |

#### Individual KGE Components
| Component | Function | Symbol | Ideal Value | Interpretation |
|-----------|----------|--------|-------------|----------------|
| **Correlation** | `r_component` | r | 1.0 | Linear association between obs and sim |
| **Variability Ratio** | `alpha_component` | α | 1.0 | Simulated spread matches observed |
| **Bias Ratio** | `beta_component` | β | 1.0 | No systematic bias |
| **CV Ratio** | `gamma_component` | γ | 1.0 | Flow distribution shape match (KGE 2012 only) |

### Other Hydrological Metrics

| Metric | Function | Direction | Bounds | Description |
|--------|----------|-----------|--------|-------------|
| **Ratio of RMSE to Std Dev** | `rsr` | minimize | [0, ∞) | RSR = RMSE / σ(obs), related to NSE: NSE = 1 - RSR² |
| **Volumetric Efficiency** | `ve` | maximize | (-∞, 1.0] | Volume agreement, insensitive to timing |
| **Regime NSE** | `regNSE` | maximize | (-∞, 1.0] | NSE on ranked flow-duration curves (regime) |
| **Forecast Verification** | `forecast_verification` | maximize | (-∞, 1.0] | Skill relative to climatology |
| **Forecast Verification Delta** | `forecast_verification_delta` | maximize | (-∞, 1.0] | Skill on flow increments |
| **Sigma Skill Score** | `ssigma` | maximize | (-∞, 1.0] | Combines RMSE with bias penalty |
| **Sigma Skill Score Delta** | `ssigma_delta` | maximize | (-∞, 1.0] | Sigma skill on flow increments |

## Navigation to Individual Metric Pages

```{toctree}
:maxdepth: 1
:caption: NSE Family

nse
log_nse
modified_nse
nnse
nse_variance_weighted
```

```{toctree}
:maxdepth: 1
:caption: KGE Family

kge_2009
kge_2012
kge_components
r_component
alpha_component
beta_component
gamma_component
```

```{toctree}
:maxdepth: 1
:caption: Other Metrics

rsr
ve
regnse
forecast_verification
forecast_verification_delta
ssigma
ssigma_delta
```

## Common Parameters

All hydrological metrics support common parameters:

```python
def metric(
    obs: array-like,
    sim: array-like,
    *,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    **kwargs
) -> MetricResult:
```

| Parameter | Description |
|-----------|-------------|
| `obs` | Observed values |
| `sim` | Simulated/predicted values |
| `weight` | Sample weights (broadcastable to obs/sim) |
| `axis` | Axis along which to compute (None = flatten) |
| `reduction` | "mean", "sum", or "none" for array outputs |

## Implementation Features

- **Automatic dispatching**: Works with NumPy, pandas, xarray, polars
- **NaN handling**: Three policies (`omit`, `propagate`, `raise`) via `nan_policy`
- **Sentinel values**: Support for missing value codes (e.g., -999) via `sentinel` parameter
- **MetricResult return**: Rich object with metadata, formula, references

## Links to Other Sections

- [Regression Metrics](../regression.md) — MAE, MSE, RMSE, R², correlations, etc.
- [Probabilistic Metrics](../probabilistic.md) — CRPS, Brier Score, Reliability, etc.
- [Classification Metrics](../classification.md) — Accuracy, Precision, Recall, F1, ROC AUC, EDI, SEDI