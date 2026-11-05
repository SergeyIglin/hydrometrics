# API Reference

Complete reference for all public symbols in `hydrometrics`.

All metric functions return a `MetricResult` object with the computed value, metadata, optimization direction, theoretical bounds, and NaN handling information.

**Shared parameters** (added by the dispatch decorator to every metric):
- `axis: int | None = None` — Axis along which to compute; `None` flattens inputs.
- `nan_policy: Literal["propagate", "omit", "raise"] = "omit"` — How to handle NaN values.
- `sample_weight: array-like | None = None` — Sample weights (passed as `weight` to the core function).
- `reduction: Literal["mean", "sum", "none"] = "mean"` — Reduction strategy for multi-dimensional outputs.
- `sentinel: float | list[float] | None = None` — Sentinel (missing-data) values to replace with NaN (e.g., `-999`).
- `**kwargs` — Metric-specific parameters (documented per metric below).

> **Note:** The `weight` parameter in the tables below corresponds to `sample_weight` in the public API. The dispatcher forwards `sample_weight` as `weight` to the core metric function.

## Top-Level Imports

```python
from hydrometrics import (
    # Core
    MetricResult,
    validate_inputs,
    NanPolicy,
    Reduction,
    compute_grouped,
    GroupedResult,
    # Regression metrics
    mae,
    mse,
    rmse,
    nrmse,
    bias,
    pbias,
    r2,
    pearson_r,
    spearman_r,
    kendall_tau,
    willmott_d,
    # Hydrological metrics
    nse,
    log_nse,
    modified_nse,
    nnse,
    nse_variance_weighted,
    kge_2009,
    kge_2012,
    kge_components,
    r_component,
    alpha_component,
    beta_component,
    gamma_component,
    rsr,
    ve,
    regNSE,
    forecast_verification,
    forecast_verification_delta,
    ssigma,
    ssigma_delta,
    # Probabilistic metrics
    crps,
    weighted_crps,
    crpss,
    brier_score,
    reliability,
    sharpness,
    # Classification metrics
    accuracy,
    precision,
    recall,
    f1_score,
    roc_auc,
    pr_auc,
    edi,
    sedi,
)
```

---

## Core API

### `MetricResult` (`hydrometrics.core.result.MetricResult`)

Standardized result container returned by all metric functions.

```python
class MetricResult:
    value: float | np.ndarray | dict[str, float | np.ndarray]
    name: str
    direction: Literal["maximize", "minimize"]
    bounds: tuple[float | None, float | None]
    parameters: dict[str, Any]
    reference: str
    nan_info: dict[str, Any]
    norm_source: str | None
    meta: dict[str, Any]

    def __float__(self) -> float: ...
    def __repr__(self) -> str: ...
    def to_dict(self) -> dict: ...
```

**Key attributes:**
- `value` — Computed metric value (scalar, array, or dict for `kge_components`).
- `direction` — `"maximize"` (higher is better) or `"minimize"` (lower is better).
- `bounds` — Theoretical `(lower, upper)` bounds; `None` means unbounded.
- `parameters` — All parameters used in the computation (including shared ones).
- `reference` — DOI or citation for the metric.
- `nan_info` — Dict with NaN handling details (`"policy"`, `"n_nan_removed"`, `"n_total"`).
- `norm_source` — Source of reference normal: `"user"`, `"climatology"`, `"regime"`, or `None` (metric default).
- `meta` — Additional metadata: `"description"` and `"formula"`.

**Example:**
```python
from hydrometrics import nse
import numpy as np

obs = np.array([10, 12, 15])
sim = np.array([9.5, 11.8, 14.5])
result = nse(obs, sim)

float(result)          # 0.92...
result.direction       # "maximize"
result.bounds          # (-inf, 1.0)
result.reference       # "Nash & Sutcliffe (1970)..."
result.nan_info        # {"policy": "omit", "n_nan_removed": 0, "n_total": 3}
result.meta["formula"] # "1 - Σ(y - ŷ)² / Σ(y - ȳ)²"
result.to_dict()       # Full serializable dict
```
---

### `validate_inputs` (`hydrometrics.core.validation.validate_inputs`)

Validates and converts inputs to numpy arrays with consistent NaN handling.

```python
def validate_inputs(
    obs: ArrayLike,
    sim: ArrayLike,
    *,
    axis: int | None = None,
    nan_policy: NanPolicyType = "omit",
    sample_weight: ArrayLike | None = None,
    sentinel: float | list[float] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, dict[str, Any]]: ...
```

**Returns:** `(obs_arr, sim_arr, weight_arr, nan_info)`

---

### `NanPolicy` (`hydrometrics.core.policies.NanPolicy`)

Enum for NaN handling policies:
- `NanPolicy.OMIT` ("omit") — Remove NaN pairs before computation.
- `NanPolicy.PROPAGATE` ("propagate") — Return NaN if any input is NaN.
- `NanPolicy.RAISE` ("raise") — Raise `ValueError` on NaN.

---

### `Reduction` (`hydrometrics.core.policies.Reduction`)

Enum for reduction strategies:
- `Reduction.MEAN` ("mean") — Mean over axis.
- `Reduction.SUM` ("sum") — Sum over axis.
- `Reduction.NONE` ("none") — No reduction, return array.

---

### `compute_grouped` (`hydrometrics.core.grouping.compute_grouped`)

Compute a metric per group defined by grouping variables.

```python
def compute_grouped(
    metric_func: Any,
    data: Any,
    obs: Any,
    sim: Any,
    group_by: Sequence[str] | str | dict[str, Any],
    **kwargs: Any,
) -> GroupedResult: ...
```

**Example:**
```python
import pandas as pd
from hydrometrics import nse, compute_grouped

df = pd.DataFrame({
    "gauge": ["A", "A", "B", "B"],
    "obs": [10, 12, 8, 9],
    "sim": [9.5, 11.8, 7.8, 9.2]
})
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by="gauge")
result.to_pandas()
```

---

### `GroupedResult` (`hydrometrics.core.grouping.GroupedResult`)

Container for grouped metric results.

```python
class GroupedResult:
    name: str
    groups: tuple[tuple, ...]
    values: np.ndarray
    group_names: tuple[str, ...]
    meta: dict

    def __iter__(self) -> zip: ...
    def __len__(self) -> int: ...
    def to_dict(self) -> dict: ...
    def to_pandas(self) -> pd.DataFrame: ...
    def to_xarray(self) -> xr.Dataset: ...
```

---

## Regression Metrics (`hydrometrics.metrics.regression`)

| Function | Additional Parameters | Direction | Bounds | Description |
|----------|----------------------|-----------|--------|-------------|
| `mae` | — | minimize | [0, ∞) | Mean Absolute Error |
| `mse` | — | minimize | [0, ∞) | Mean Squared Error |
| `rmse` | — | minimize | [0, ∞) | Root Mean Squared Error |
| `nrmse` | `norm: "mean" | "maxmin" | "std" = "mean"` | minimize | [0, ∞) | Normalized RMSE |
| `bias` | — | minimize | (-∞, ∞) | Mean Error (sim - obs) |
| `pbias` | — | minimize | (-∞, ∞) | Percent Bias (%) |
| `r2` | — | maximize | (-∞, 1.0] | Coefficient of Determination |
| `pearson_r` | — | maximize | [-1, 1] | Pearson Correlation |
| `spearman_r` | — | maximize | [-1, 1] | Spearman Rank Correlation |
| `kendall_tau` | — | maximize | [-1, 1] | Kendall's Tau |
| `willmott_d` | — | maximize | [0, 1] | Willmott's Index of Agreement |

**Notes:**
- `nrmse` normalization: "mean" (divide by mean(obs)), "maxmin" (divide by max-min), "std" (divide by std(obs)).
- `spearman_r`, `kendall_tau` ignore `weight` parameter.

---

## Hydrological Metrics (`hydrometrics.metrics.hydro`)

| Function | Additional Parameters | Direction | Bounds | Description |
|----------|----------------------|-----------|--------|-------------|
| `nse` | — | maximize | (-∞, 1.0] | Nash-Sutcliffe Efficiency |
| `log_nse` | `eps: float = 1e-10` | maximize | (-∞, 1.0] | Log-transformed NSE |
| `modified_nse` | — | maximize | (-∞, 1.0] | Modified NSE (L1 norm, j=1) |
| `nnse` | — | maximize | [0, 1] | Normalized NSE |
| `nse_variance_weighted` | `gauge: np.ndarray` (required) | maximize | (-∞, 1.0] | Multi-gauge variance-weighted NSE |
| `kge_2009` | — | maximize | (-∞, 1.0] | KGE 2009 (r, α, β) |
| `kge_2012` | — | maximize | (-∞, 1.0] | KGE 2012 (r, α, β, γ) |
| `kge_components` | `version: "2009" | "2012" = "2012"` | — | — | Returns dict of components |
| `r_component` | — | maximize | [-1, 1] | Correlation component (r) |
| `alpha_component` | — | maximize | [0, ∞) | Variability ratio (α) |
| `beta_component` | — | maximize | [0, ∞) | Bias ratio (β) |
| `gamma_component` | — | maximize | [0, ∞) | CV ratio (γ, KGE 2012 only) |
| `rsr` | — | minimize | [0, ∞) | RMSE / std(obs) |
| `ve` | — | maximize | (-∞, 1.0] | Volumetric Efficiency |
| `regNSE` | `dates: array-like` (required) | maximize | (-∞, 1.0] | Regime NSE (flow-duration curve) |
| `forecast_verification` | — | maximize | (-∞, 1.0] | Skill vs climatology |
| `forecast_verification_delta` | `ref_date: datetime-like` (required) | maximize | (-∞, 1.0] | Skill on increments |
| `ssigma` | — | maximize | (-∞, 1.0] | Sigma skill score |
| `ssigma_delta` | `ref_date: datetime-like` (required) | maximize | (-∞, 1.0] | Sigma skill on increments |

**Key clarifications:**
- `kge_2009` uses 3 components (r, α, β) per Gupta et al. 2009.
- `kge_2012` uses 4 components (r, α, β, γ) per Kling et al. 2012.
- `kge_components` returns a **`MetricResult` with `value` as a `dict`**, not a tuple. Supports `version="2009"` or `"2012"`.
- `modified_nse` uses L1 norm (absolute errors). No `j` parameter exists.
- `log_nse` uses parameter `eps` (not `offset`), default `1e-10`.
- `regNSE` **requires** `dates` parameter for flow-duration curve computation.
- `forecast_verification_delta`, `ssigma_delta` require `ref_date`.

---

## Probabilistic Metrics (`hydrometrics.metrics.probabilistic`)

| Function | Additional Parameters | Direction | Bounds | Description |
|----------|----------------------|-----------|--------|-------------|
| `crps` | — | minimize | [0, ∞) | Continuous Ranked Probability Score. Accepts deterministic or ensemble forecasts. |
| `weighted_crps` | `weight_func: Callable | None = None` | minimize | [0, ∞) | Weighted CRPS. `weight_func(y)` emphasizes distribution regions (e.g., tails). |
| `crpss` | `ref_forecast: np.ndarray | None = None` | maximize | (-∞, 1.0] | CRPS Skill Score. `ref_forecast` is the reference forecast (default: climatology). |
| `brier_score` | — | minimize | [0, 1] | Brier Score for binary probabilistic forecasts. |
| `reliability` | `n_bins: int = 10` | minimize | [0, ∞) | Reliability (calibration) component of Brier Score. Number of probability bins. |
| `sharpness` | — | maximize | [0, ∞) | Sharpness component (variance of forecast probabilities). |

---

## Classification Metrics (`hydrometrics.metrics.classification`)

| Function | Additional Parameters | Direction | Bounds | Description |
|----------|----------------------|-----------|--------|-------------|
| `accuracy` | — | maximize | [0, 1] | Overall classification accuracy. |
| `precision` | `positive_class: int = 1` | maximize | [0, 1] | Precision (PPV). `positive_class` defines the positive label. |
| `recall` | `positive_class: int = 1` | maximize | [0, 1] | Recall / Sensitivity / POD. |
| `f1_score` | `positive_class: int = 1` | maximize | [0, 1] | F1 Score (harmonic mean of precision and recall). |
| `roc_auc` | — | maximize | [0, 1] | ROC AUC (requires probabilistic `sim`). |
| `pr_auc` | — | maximize | [0, 1] | PR AUC (requires probabilistic `sim`). |
| `edi` | — | maximize | [-1, 1] | Extremal Dependence Index (rare events). |
| `sedi` | — | maximize | [-1, 1] | Symmetric EDI (rare events, base-rate independent). |

---

## Backends

All metrics support multiple array backends via automatic dispatch:

| Backend | Types | Import Required |
|---------|-------|-----------------|
| NumPy | `np.ndarray`, `list`, `tuple` | Built-in |
| Pandas | `pd.Series`, `pd.DataFrame` | `pip install pandas` |
| Xarray | `xr.DataArray`, `xr.Dataset` | `pip install xarray` |
| Polars | `pl.Series`, `pl.DataFrame` | `pip install polars` |

**Dispatch:** Automatic based on input types. Mixed types default to NumPy.

```python
import pandas as pd
import numpy as np
from hydrometrics import nse

# Pandas Series
obs_s = pd.Series([10, 12, 15])
sim_s = pd.Series([9.5, 11.8, 14.5])
nse(obs_s, sim_s)  # Works automatically

# NumPy arrays
obs_a = np.array([10, 12, 15])
sim_a = np.array([9.5, 11.8, 14.5])
nse(obs_a, sim_a)  # Works
```

---

## Removed Metrics

The following metrics were **deliberately removed** and are **not available**:

- `peak_flow_error`
- `peak_timing_error`
- `low_flow_metrics`
- `flow_duration_curve_metrics`

Do not attempt to import these. They will raise `ImportError`.
