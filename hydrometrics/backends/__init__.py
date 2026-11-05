"""
Backends package for HydroMetrics.

The numpy backend is always available. The pandas, polars and xarray backends import their
packages, so they are loaded on first access and raise ``ImportError`` if the package is missing.
"""

from importlib import import_module

from hydrometrics.backends import numpy

__all__ = ["numpy", "pandas", "xarray", "polars"]


def __getattr__(name):
    if name in ("pandas", "xarray", "polars"):
        return import_module(f"hydrometrics.backends.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
