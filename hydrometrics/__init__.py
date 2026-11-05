"""
HydroMetrics - Hydrological and hydrometeorological model evaluation metrics.

A comprehensive library for evaluating hydrological models with support for
NumPy, pandas, xarray, and polars data structures.
"""

from importlib import metadata as _metadata

try:
    __version__ = _metadata.version("hydrometrics")
except _metadata.PackageNotFoundError:  # a source tree that has not been installed
    __version__ = "0+unknown"

from hydrometrics.core.base import MetricResult
from hydrometrics.core.validation import validate_inputs
from hydrometrics.core.policies import NanPolicy, Reduction
from hydrometrics.core.dispatch import registry
from hydrometrics.core.grouping import compute_grouped, GroupedResult
from hydrometrics.backends.numpy import mean_annual_hydrograph
from hydrometrics.backends.numpy import mean_annual_hydrograph_duration_curve


# Import NumPy backend metrics (these are the base implementations)
from hydrometrics.metrics.regression import (
    mae as _mae_numpy,
    mse as _mse_numpy,
    rmse as _rmse_numpy,
    nrmse as _nrmse_numpy,
    bias as _bias_numpy,
    pbias as _pbias_numpy,
    r2 as _r2_numpy,
    pearson_r as _pearson_r_numpy,
    spearman_r as _spearman_r_numpy,
    kendall_tau as _kendall_tau_numpy,
    willmott_d as _willmott_d_numpy,
)

from hydrometrics.metrics.hydro import (
    nse as _nse_numpy,
    log_nse as _log_nse_numpy,
    modified_nse as _modified_nse_numpy,
    nse_bounded as _nse_bounded_numpy,
    kge_2009 as _kge_2009_numpy,
    kge_2012 as _kge_2012_numpy,
    kge_components as _kge_components_numpy,
    r_component as _r_component_numpy,
    alpha_component as _alpha_component_numpy,
    beta_component as _beta_component_numpy,
    gamma_component as _gamma_component_numpy,
    rsr as _rsr_numpy,
    ve as _ve_numpy,
    regNSE as _regNSE_numpy,
    forecast_verification as _forecast_verification_numpy,
    forecast_verification_delta as _forecast_verification_delta_numpy,
    ssigma as _ssigma_numpy,
    ssigma_delta as _ssigma_delta_numpy,
    nse_variance_weighted as _nse_variance_weighted_numpy
)

from hydrometrics.metrics.probabilistic import (
    crps as _crps_numpy,
    weighted_crps as _weighted_crps_numpy,
    crpss as _crpss_numpy,
    brier_score as _brier_score_numpy,
    reliability as _reliability_numpy,
    sharpness as _sharpness_numpy,
)

from hydrometrics.metrics.classification import (
    accuracy as _accuracy_numpy,
    precision as _precision_numpy,
    recall as _recall_numpy,
    f1_score as _f1_score_numpy,
    roc_auc as _roc_auc_numpy,
    pr_auc as _pr_auc_numpy,
    edi as _edi_numpy,
    sedi as _sedi_numpy,
)

# Import backend-specific functions
try:
    from hydrometrics.backends.pandas import (
        mae as _mae_pandas,
        mse as _mse_pandas,
        rmse as _rmse_pandas,
        nrmse as _nrmse_pandas,
        bias as _bias_pandas,
        pbias as _pbias_pandas,
        r2 as _r2_pandas,
        pearson_r as _pearson_r_pandas,
        spearman_r as _spearman_r_pandas,
        kendall_tau as _kendall_tau_pandas,
        willmott_d as _willmott_d_pandas,
        ssigma as _ssigma_pandas,
        nse_variance_weighted as _nse_variance_weighted_pandas,
        forecast_verification as _forecast_verification_pandas,
        forecast_verification_delta as _forecast_verification_delta_pandas,
        regNSE as _regNSE_pandas,
        nse as _nse_pandas,
        log_nse as _log_nse_pandas,
        modified_nse as _modified_nse_pandas,
        nse_bounded as _nse_bounded_pandas,
        kge_2009 as _kge_2009_pandas,
        kge_2012 as _kge_2012_pandas,
        kge_components as _kge_components_pandas,
        r_component as _r_component_pandas,
        alpha_component as _alpha_component_pandas,
        beta_component as _beta_component_pandas,
        gamma_component as _gamma_component_pandas,
        rsr as _rsr_pandas,
        ve as _ve_pandas,
        crps as _crps_pandas,
        weighted_crps as _weighted_crps_pandas,
        crpss as _crpss_pandas,
        brier_score as _brier_score_pandas,
        reliability as _reliability_pandas,
        sharpness as _sharpness_pandas,
        accuracy as _accuracy_pandas,
        precision as _precision_pandas,
        recall as _recall_pandas,
        f1_score as _f1_score_pandas,
        roc_auc as _roc_auc_pandas,
        pr_auc as _pr_auc_pandas,
        edi as _edi_pandas,
        ssigma_delta as _ssigma_delta_pandas,
        sedi as _sedi_pandas,
    )
    HAS_PANDAS_BACKEND = True
except ImportError:
    HAS_PANDAS_BACKEND = False

# Import backend-specific functions
try:
    from hydrometrics.backends.xarray import (
        mae as _mae_xarray,
        mse as _mse_xarray,
        rmse as _rmse_xarray,
        nrmse as _nrmse_xarray,
        bias as _bias_xarray,
        pbias as _pbias_xarray,
        r2 as _r2_xarray,
        pearson_r as _pearson_r_xarray,
        spearman_r as _spearman_r_xarray,
        kendall_tau as _kendall_tau_xarray,
        willmott_d as _willmott_d_xarray,
        forecast_verification as _forecast_verification_xarray,
        forecast_verification_delta as _forecast_verification_delta_xarray,
        ssigma as _ssigma_xarray,
        ssigma_delta as _ssigma_delta_xarray,
        nse as _nse_xarray,
        nse_variance_weighted as _nse_variance_weighted_xarray,
        log_nse as _log_nse_xarray,
        modified_nse as _modified_nse_xarray,
        nse_bounded as _nse_bounded_xarray,
        kge_2009 as _kge_2009_xarray,
        kge_2012 as _kge_2012_xarray,
        kge_components as _kge_components_xarray,
        r_component as _r_component_xarray,
        alpha_component as _alpha_component_xarray,
        beta_component as _beta_component_xarray,
        gamma_component as _gamma_component_xarray,
        rsr as _rsr_xarray,
        ve as _ve_xarray,
        regNSE as _regNSE_xarray,
        crps as _crps_xarray,
        weighted_crps as _weighted_crps_xarray,
        crpss as _crpss_xarray,
        brier_score as _brier_score_xarray,
        reliability as _reliability_xarray,
        sharpness as _sharpness_xarray,
        accuracy as _accuracy_xarray,
        precision as _precision_xarray,
        recall as _recall_xarray,
        f1_score as _f1_score_xarray,
        roc_auc as _roc_auc_xarray,
        pr_auc as _pr_auc_xarray,
        edi as _edi_xarray,
        sedi as _sedi_xarray,
    )
    HAS_XARRAY_BACKEND = True
except ImportError:
    HAS_XARRAY_BACKEND = False

# Import backend-specific functions
try:
    from hydrometrics.backends.polars import (
        mae as _mae_polars,
        mse as _mse_polars,
        rmse as _rmse_polars,
        nrmse as _nrmse_polars,
        bias as _bias_polars,
        pbias as _pbias_polars,
        r2 as _r2_polars,
        pearson_r as _pearson_r_polars,
        spearman_r as _spearman_r_polars,
        kendall_tau as _kendall_tau_polars,
        willmott_d as _willmott_d_polars,
        nse_variance_weighted as _nse_variance_weighted_polars,
        ssigma as _ssigma_polars,
        ssigma_delta as _ssigma_delta_polars,
        forecast_verification as _forecast_verification_polars,
        forecast_verification_delta as _forecast_verification_delta_polars,
        regNSE as _regNSE_polars,
        nse as _nse_polars,
        log_nse as _log_nse_polars,
        modified_nse as _modified_nse_polars,
        nse_bounded as _nse_bounded_polars,
        kge_2009 as _kge_2009_polars,
        kge_2012 as _kge_2012_polars,
        kge_components as _kge_components_polars,
        r_component as _r_component_polars,
        alpha_component as _alpha_component_polars,
        beta_component as _beta_component_polars,
        gamma_component as _gamma_component_polars,
        rsr as _rsr_polars,
        ve as _ve_polars,
        regNSE as _regNSE_polars,
        crps as _crps_polars,
        weighted_crps as _weighted_crps_polars,
        crpss as _crpss_polars,
        brier_score as _brier_score_polars,
        reliability as _reliability_polars,
        sharpness as _sharpness_polars,
        accuracy as _accuracy_polars,
        precision as _precision_polars,
        recall as _recall_polars,
        f1_score as _f1_score_polars,
        roc_auc as _roc_auc_polars,
        pr_auc as _pr_auc_polars,
        edi as _edi_polars,
        sedi as _sedi_polars,
    )
    HAS_POLARS_BACKEND = True
except ImportError:
    HAS_POLARS_BACKEND = False


# Register all metrics with the registry
def _register_all():
    metrics = [
        ("mae", _mae_numpy, _mae_pandas if HAS_PANDAS_BACKEND else None,
         _mae_xarray if HAS_XARRAY_BACKEND else None, _mae_polars if HAS_POLARS_BACKEND else None),
        ("mse", _mse_numpy, _mse_pandas if HAS_PANDAS_BACKEND else None,
         _mse_xarray if HAS_XARRAY_BACKEND else None, _mse_polars if HAS_POLARS_BACKEND else None),
        ("rmse", _rmse_numpy, _rmse_pandas if HAS_PANDAS_BACKEND else None,
         _rmse_xarray if HAS_XARRAY_BACKEND else None, _rmse_polars if HAS_POLARS_BACKEND else None),
        ("nrmse", _nrmse_numpy, _nrmse_pandas if HAS_PANDAS_BACKEND else None,
         _nrmse_xarray if HAS_XARRAY_BACKEND else None, _nrmse_polars if HAS_POLARS_BACKEND else None),
        ("bias", _bias_numpy, _bias_pandas if HAS_PANDAS_BACKEND else None,
         _bias_xarray if HAS_XARRAY_BACKEND else None, _bias_polars if HAS_POLARS_BACKEND else None),
        ("pbias", _pbias_numpy, _pbias_pandas if HAS_PANDAS_BACKEND else None,
         _pbias_xarray if HAS_XARRAY_BACKEND else None, _pbias_polars if HAS_POLARS_BACKEND else None),
        ("r2", _r2_numpy, _r2_pandas if HAS_PANDAS_BACKEND else None,
         _r2_xarray if HAS_XARRAY_BACKEND else None, _r2_polars if HAS_POLARS_BACKEND else None),
        ("pearson_r", _pearson_r_numpy, _pearson_r_pandas if HAS_PANDAS_BACKEND else None,
         _pearson_r_xarray if HAS_XARRAY_BACKEND else None, _pearson_r_polars if HAS_POLARS_BACKEND else None),
        ("spearman_r", _spearman_r_numpy, _spearman_r_pandas if HAS_PANDAS_BACKEND else None,
         _spearman_r_xarray if HAS_XARRAY_BACKEND else None, _spearman_r_polars if HAS_POLARS_BACKEND else None),
        ("kendall_tau", _kendall_tau_numpy, _kendall_tau_pandas if HAS_PANDAS_BACKEND else None,
         _kendall_tau_xarray if HAS_XARRAY_BACKEND else None, _kendall_tau_polars if HAS_POLARS_BACKEND else None),
        ("willmott_d", _willmott_d_numpy, _willmott_d_pandas if HAS_PANDAS_BACKEND else None,
         _willmott_d_xarray if HAS_XARRAY_BACKEND else None, _willmott_d_polars if HAS_POLARS_BACKEND else None),
        ("ssigma", _ssigma_numpy, _ssigma_pandas if HAS_PANDAS_BACKEND else None, 
            _ssigma_xarray if HAS_XARRAY_BACKEND else None, _ssigma_polars if HAS_POLARS_BACKEND else None),
        ("ssigma_delta", _ssigma_delta_numpy, _ssigma_delta_pandas if HAS_PANDAS_BACKEND else None,
            _ssigma_delta_xarray if HAS_XARRAY_BACKEND else None, _ssigma_delta_polars if HAS_POLARS_BACKEND else None),
         
        ("forecast_verification", _forecast_verification_numpy, _forecast_verification_pandas if HAS_PANDAS_BACKEND else None,
            _forecast_verification_xarray if HAS_XARRAY_BACKEND else None, _forecast_verification_polars if HAS_POLARS_BACKEND else None),
        ("forecast_verification_delta", _forecast_verification_delta_numpy, _forecast_verification_delta_pandas if HAS_PANDAS_BACKEND else None,
            _forecast_verification_delta_xarray if HAS_XARRAY_BACKEND else None, _forecast_verification_delta_polars if HAS_POLARS_BACKEND else None),

        ("nse_variance_weighted", _nse_variance_weighted_numpy, _nse_variance_weighted_pandas if HAS_PANDAS_BACKEND else None,
         _nse_variance_weighted_xarray if HAS_XARRAY_BACKEND else None, _nse_variance_weighted_polars if HAS_POLARS_BACKEND else None),

         ("regNSE", _regNSE_numpy,  _regNSE_pandas if HAS_PANDAS_BACKEND else None,  _regNSE_xarray if HAS_XARRAY_BACKEND else None,
        _regNSE_polars if HAS_POLARS_BACKEND else None),
        ("nse", _nse_numpy, _nse_pandas if HAS_PANDAS_BACKEND else None,
         _nse_xarray if HAS_XARRAY_BACKEND else None, _nse_polars if HAS_POLARS_BACKEND else None),
        ("log_nse", _log_nse_numpy, _log_nse_pandas if HAS_PANDAS_BACKEND else None,
         _log_nse_xarray if HAS_XARRAY_BACKEND else None, _log_nse_polars if HAS_POLARS_BACKEND else None),
        ("modified_nse", _modified_nse_numpy, _modified_nse_pandas if HAS_PANDAS_BACKEND else None,
         _modified_nse_xarray if HAS_XARRAY_BACKEND else None, _modified_nse_polars if HAS_POLARS_BACKEND else None),
        ("nse_bounded", _nse_bounded_numpy, _nse_bounded_pandas if HAS_PANDAS_BACKEND else None,
         _nse_bounded_xarray if HAS_XARRAY_BACKEND else None, _nse_bounded_polars if HAS_POLARS_BACKEND else None),
        ("kge_2009", _kge_2009_numpy, _kge_2009_pandas if HAS_PANDAS_BACKEND else None,
         _kge_2009_xarray if HAS_XARRAY_BACKEND else None, _kge_2009_polars if HAS_POLARS_BACKEND else None),
        ("kge_2012", _kge_2012_numpy, _kge_2012_pandas if HAS_PANDAS_BACKEND else None,
         _kge_2012_xarray if HAS_XARRAY_BACKEND else None, _kge_2012_polars if HAS_POLARS_BACKEND else None),
        ("kge_components", _kge_components_numpy, _kge_components_pandas if HAS_PANDAS_BACKEND else None,
         _kge_components_xarray if HAS_XARRAY_BACKEND else None, _kge_components_polars if HAS_POLARS_BACKEND else None),
        ("r_component", _r_component_numpy, _r_component_pandas if HAS_PANDAS_BACKEND else None,
         _r_component_xarray if HAS_XARRAY_BACKEND else None, _r_component_polars if HAS_POLARS_BACKEND else None),
        ("alpha_component", _alpha_component_numpy, _alpha_component_pandas if HAS_PANDAS_BACKEND else None,
         _alpha_component_xarray if HAS_XARRAY_BACKEND else None, _alpha_component_polars if HAS_POLARS_BACKEND else None),
        ("beta_component", _beta_component_numpy, _beta_component_pandas if HAS_PANDAS_BACKEND else None,
         _beta_component_xarray if HAS_XARRAY_BACKEND else None, _beta_component_polars if HAS_POLARS_BACKEND else None),
        ("gamma_component", _gamma_component_numpy, _gamma_component_pandas if HAS_PANDAS_BACKEND else None,
         _gamma_component_xarray if HAS_XARRAY_BACKEND else None, _gamma_component_polars if HAS_POLARS_BACKEND else None),
        ("rsr", _rsr_numpy, _rsr_pandas if HAS_PANDAS_BACKEND else None,
         _rsr_xarray if HAS_XARRAY_BACKEND else None, _rsr_polars if HAS_POLARS_BACKEND else None),
        ("ve", _ve_numpy, _ve_pandas if HAS_PANDAS_BACKEND else None,
         _ve_xarray if HAS_XARRAY_BACKEND else None, _ve_polars if HAS_POLARS_BACKEND else None),       
        ("crps", _crps_numpy, _crps_pandas if HAS_PANDAS_BACKEND else None,
         _crps_xarray if HAS_XARRAY_BACKEND else None, _crps_polars if HAS_POLARS_BACKEND else None),
        ("weighted_crps", _weighted_crps_numpy, _weighted_crps_pandas if HAS_PANDAS_BACKEND else None,
         _weighted_crps_xarray if HAS_XARRAY_BACKEND else None, _weighted_crps_polars if HAS_POLARS_BACKEND else None),
        ("crpss", _crpss_numpy, _crpss_pandas if HAS_PANDAS_BACKEND else None,
         _crpss_xarray if HAS_XARRAY_BACKEND else None, _crpss_polars if HAS_POLARS_BACKEND else None),
        ("brier_score", _brier_score_numpy, _brier_score_pandas if HAS_PANDAS_BACKEND else None,
         _brier_score_xarray if HAS_XARRAY_BACKEND else None, _brier_score_polars if HAS_POLARS_BACKEND else None),
        ("reliability", _reliability_numpy, _reliability_pandas if HAS_PANDAS_BACKEND else None,
         _reliability_xarray if HAS_XARRAY_BACKEND else None, _reliability_polars if HAS_POLARS_BACKEND else None),
        ("sharpness", _sharpness_numpy, _sharpness_pandas if HAS_PANDAS_BACKEND else None,
         _sharpness_xarray if HAS_XARRAY_BACKEND else None, _sharpness_polars if HAS_POLARS_BACKEND else None),
        ("accuracy", _accuracy_numpy, _accuracy_pandas if HAS_PANDAS_BACKEND else None,
         _accuracy_xarray if HAS_XARRAY_BACKEND else None, _accuracy_polars if HAS_POLARS_BACKEND else None),
        ("precision", _precision_numpy, _precision_pandas if HAS_PANDAS_BACKEND else None,
         _precision_xarray if HAS_XARRAY_BACKEND else None, _precision_polars if HAS_POLARS_BACKEND else None),
        ("recall", _recall_numpy, _recall_pandas if HAS_PANDAS_BACKEND else None,
         _recall_xarray if HAS_XARRAY_BACKEND else None, _recall_polars if HAS_POLARS_BACKEND else None),
        ("f1_score", _f1_score_numpy, _f1_score_pandas if HAS_PANDAS_BACKEND else None,
         _f1_score_xarray if HAS_XARRAY_BACKEND else None, _f1_score_polars if HAS_POLARS_BACKEND else None),
        ("roc_auc", _roc_auc_numpy, _roc_auc_pandas if HAS_PANDAS_BACKEND else None,
         _roc_auc_xarray if HAS_XARRAY_BACKEND else None, _roc_auc_polars if HAS_POLARS_BACKEND else None),
        ("pr_auc", _pr_auc_numpy, _pr_auc_pandas if HAS_PANDAS_BACKEND else None,
         _pr_auc_xarray if HAS_XARRAY_BACKEND else None, _pr_auc_polars if HAS_POLARS_BACKEND else None),
        ("edi", _edi_numpy, _edi_pandas if HAS_PANDAS_BACKEND else None,
         _edi_xarray if HAS_XARRAY_BACKEND else None, _edi_polars if HAS_POLARS_BACKEND else None),
        ("sedi", _sedi_numpy, _sedi_pandas if HAS_PANDAS_BACKEND else None,
         _sedi_xarray if HAS_XARRAY_BACKEND else None, _sedi_polars if HAS_POLARS_BACKEND else None),
    ]

    for name, np_func, pd_func, xr_func, pl_func in metrics:
        if np_func:
            registry.register_numpy(name, np_func)
        if pd_func:
            registry.register_pandas(name, pd_func)
        if xr_func:
            registry.register_xarray(name, xr_func)
        if pl_func:
            registry.register_polars(name, pl_func)


# Create dispatched functions
_register_all()

# Create public API with dispatching
mae = registry.get_dispatcher("mae")
mse = registry.get_dispatcher("mse")
rmse = registry.get_dispatcher("rmse")
nrmse = registry.get_dispatcher("nrmse")
bias = registry.get_dispatcher("bias")
pbias = registry.get_dispatcher("pbias")
r2 = registry.get_dispatcher("r2")
pearson_r = registry.get_dispatcher("pearson_r")
spearman_r = registry.get_dispatcher("spearman_r")
kendall_tau = registry.get_dispatcher("kendall_tau")
willmott_d = registry.get_dispatcher("willmott_d")
ssigma = registry.get_dispatcher("ssigma")
nse_variance_weighted = registry.get_dispatcher("nse_variance_weighted")
ssigma_delta = registry.get_dispatcher("ssigma_delta")
forecast_verification = registry.get_dispatcher("forecast_verification")
forecast_verification_delta = registry.get_dispatcher("forecast_verification_delta")
regNSE = registry.get_dispatcher("regNSE")
nse = registry.get_dispatcher("nse")
log_nse = registry.get_dispatcher("log_nse")
modified_nse = registry.get_dispatcher("modified_nse")
nse_bounded = registry.get_dispatcher("nse_bounded")
kge_2009 = registry.get_dispatcher("kge_2009")
kge_2012 = registry.get_dispatcher("kge_2012")
kge_components = registry.get_dispatcher("kge_components")
r_component = registry.get_dispatcher("r_component")
alpha_component = registry.get_dispatcher("alpha_component")
beta_component = registry.get_dispatcher("beta_component")
gamma_component = registry.get_dispatcher("gamma_component")
rsr = registry.get_dispatcher("rsr")
ve = registry.get_dispatcher("ve")
crps =registry.get_dispatcher("crps")
weighted_crps = registry.get_dispatcher("weighted_crps")
crpss = registry.get_dispatcher("crpss")
brier_score = registry.get_dispatcher("brier_score")
reliability = registry.get_dispatcher("reliability")
sharpness = registry.get_dispatcher("sharpness")
accuracy = registry.get_dispatcher("accuracy")
precision = registry.get_dispatcher("precision")
recall = registry.get_dispatcher("recall")
f1_score = registry.get_dispatcher("f1_score")
roc_auc = registry.get_dispatcher("roc_auc")
pr_auc = registry.get_dispatcher("pr_auc")
edi = registry.get_dispatcher("edi")
sedi = registry.get_dispatcher("sedi")


__version__ = "0.1.0"

__all__ = [
    # Core
    "MetricResult",
    "registry",
    "validate_inputs",
    "NanPolicy",
    "Reduction",
    "compute_grouped",
    "GroupedResult",
    # Helper functions
    "mean_annual_hydrograph",
    "mean_annual_hydrograph_duration_curve",
    # Regression
    "mae",
    "mse",
    "rmse",
    "nrmse",
    "bias",
    "pbias",
    "r2",
    "pearson_r",
    "spearman_r",
    "kendall_tau",
    "willmott_d",
    # Hydro
    "nse_variance_weighted",
    "ssigma",
    "ssigma_delta",
    "forecast_verification",
    "forecast_verification_delta",
    "regNSE",
    "nse",
    "log_nse",
    "modified_nse",
    "nse_bounded",
    "kge_2009",
    "kge_2012",
    "kge_components",
    "r_component",
    "alpha_component",
    "beta_component",
    "gamma_component",
    "rsr",
    "ve",
    # Probabilistic
    "crps",
    "weighted_crps",
    "crpss",
    "brier_score",
    "reliability",
    "sharpness",
    # Classification
    "accuracy",
    "precision",
    "recall",
    "f1_score",
    "roc_auc",
    "pr_auc",
    "edi",
    "sedi",
]