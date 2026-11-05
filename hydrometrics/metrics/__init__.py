"""
Metrics package for HydroMetrics.
"""

from hydrometrics.core.base import MetricFunction
from hydrometrics.metrics import regression, hydro, probabilistic, classification


def _collect() -> dict[str, MetricFunction]:
    found = {}
    for module in (regression, hydro, probabilistic, classification):
        for name, obj in vars(module).items():
            if isinstance(obj, MetricFunction):
                found[name] = obj
    return found


# Every metric by its public name; the pandas, polars and xarray backends wrap these objects.
catalog = _collect()

__all__ = ["regression", "hydro", "probabilistic", "classification", "catalog"]
