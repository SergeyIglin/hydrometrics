"""Core module for HydroMetrics."""

from hydrometrics.core.base import MetricFunction, metric
from hydrometrics.core.result import MetricResult
from hydrometrics.core.validation import validate_inputs
from hydrometrics.core.policies import NanPolicy, Reduction, NanPolicyType, ReductionType

__all__ = [
    "MetricFunction",
    "metric",
    "MetricResult",
    "validate_inputs",
    "NanPolicy",
    "Reduction",
    "NanPolicyType",
    "ReductionType",
]
