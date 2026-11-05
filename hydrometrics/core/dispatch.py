"""
Backend dispatch mechanism for HydroMetrics.

Automatically routes metric calls to the appropriate backend
based on input data types (numpy, pandas, xarray, polars).
"""

from __future__ import annotations

from typing import Any, Callable
import numpy as np


# Try to import optional dependencies
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

try:
    import xarray as xr
    HAS_XARRAY = True
except ImportError:
    HAS_XARRAY = False
    xr = None

try:
    import polars as pl
    HAS_POLARS = True
except ImportError:
    HAS_POLARS = False
    pl = None


class BackendRegistry:
    """Registry of metric functions, one implementation per backend.

    Each metric is registered under a name for the backends it supports (``register_numpy``,
    ``register_pandas``, ``register_polars``, ``register_xarray``). ``get_dispatcher`` returns a
    function that looks at the type of its inputs and calls the implementation of that backend,
    falling back to the NumPy one when a backend has none. The package registers all of its
    metrics in the global instance ``hydrometrics.registry``; a new metric made with
    :func:`hydrometrics.core.base.metric` can be registered the same way.
    """
    
    def __init__(self):
        self._numpy_funcs = {}
        self._pandas_funcs = {}
        self._xarray_funcs = {}
        self._polars_funcs = {}
    
    def register_numpy(self, name: str, func: Callable):
        """Register the NumPy implementation of metric ``name`` (also the fallback for the others)."""
        self._numpy_funcs[name] = func
    
    def register_pandas(self, name: str, func: Callable):
        """Register the implementation used for pandas ``Series`` and ``DataFrame`` inputs."""
        self._pandas_funcs[name] = func
    
    def register_xarray(self, name: str, func: Callable):
        """Register the implementation used for xarray ``DataArray`` and ``Dataset`` inputs."""
        self._xarray_funcs[name] = func
    
    def register_polars(self, name: str, func: Callable):
        """Register the implementation used for polars ``Series`` and ``DataFrame`` inputs."""
        self._polars_funcs[name] = func
    
    def get_dispatcher(self, name: str) -> Callable:
        """Create a dispatching function for a given metric name.

        The function takes ``(obs, sim, **kwargs)``, chooses the backend from the input types
        (xarray, then pandas, then polars, otherwise NumPy) and calls its implementation. The
        name, docstring, signature and metadata attributes are copied from the NumPy
        implementation, which must be registered.
        """
        numpy_func = self._numpy_funcs.get(name)
        pandas_func = self._pandas_funcs.get(name) if HAS_PANDAS else None
        xarray_func = self._xarray_funcs.get(name) if HAS_XARRAY else None
        polars_func = self._polars_funcs.get(name) if HAS_POLARS else None
        
        def dispatcher(obs: Any, sim: Any, **kwargs: Any) -> Any:
            # Check for xarray first (most specific backend features)
            if HAS_XARRAY and (isinstance(obs, (xr.DataArray, xr.Dataset)) or 
                                isinstance(sim, (xr.DataArray, xr.Dataset))):
                if xarray_func:
                    return xarray_func(obs, sim, **kwargs)
                # Fall back to numpy with array conversion
                return numpy_func(obs, sim, **kwargs)
            
            # Check for pandas
            if HAS_PANDAS and (isinstance(obs, (pd.Series, pd.DataFrame)) or 
                                isinstance(sim, (pd.Series, pd.DataFrame))):
                if pandas_func:
                    return pandas_func(obs, sim, **kwargs)
                return numpy_func(obs, sim, **kwargs)
            
            # Check for polars
            if HAS_POLARS and (isinstance(obs, (pl.Series, pl.DataFrame)) or 
                                isinstance(sim, (pl.Series, pl.DataFrame))):
                if polars_func:
                    return polars_func(obs, sim, **kwargs)
                return numpy_func(obs, sim, **kwargs)
            
            # Default to numpy
            return numpy_func(obs, sim, **kwargs)
        
        # Copy metadata from numpy function
        if numpy_func:
            dispatcher.__name__ = numpy_func.__name__
            dispatcher.__doc__ = numpy_func.__doc__
            dispatcher.__annotations__ = getattr(numpy_func, '__annotations__', {})
            # help() and autodoc read the real parameters, not (obs, sim, **kwargs)
            if hasattr(numpy_func, '__signature__'):
                dispatcher.__signature__ = numpy_func.__signature__
            # Copy metric metadata if present
            for attr in ['name', 'direction', 'bounds', 'reference', 'description', 'formula',
                         'supports_weight', 'supports_axis', 'optimum']:
                if hasattr(numpy_func, attr):
                    setattr(dispatcher, attr, getattr(numpy_func, attr))
        
        return dispatcher


# Global registry
registry = BackendRegistry()


def get_backend_type(obj: Any) -> str:
    """Determine backend type from object."""
    if HAS_XARRAY and isinstance(obj, (xr.DataArray, xr.Dataset)):
        return "xarray"
    if HAS_PANDAS and isinstance(obj, (pd.Series, pd.DataFrame)):
        return "pandas"
    if HAS_POLARS and isinstance(obj, (pl.Series, pl.DataFrame)):
        return "polars"
    return "numpy"
