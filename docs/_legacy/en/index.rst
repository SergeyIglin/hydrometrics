HydroMetrics
============

**Hydrological and hydrometeorological model evaluation metrics library**

A comprehensive Python library for evaluating hydrological models with support for NumPy, pandas, xarray, and polars data structures.

Features
--------

- **Unified API**: All metrics follow the same interface with consistent parameters
- **Multi-backend support**: Works seamlessly with NumPy, pandas, xarray, and polars
- **Scientific rigor**: Each metric includes original reference (DOI), formula, and limitations
- **Comprehensive metrics**: Regression, hydrological, probabilistic, and classification metrics
- **Proper NaN handling**: Three policies (propagate, omit, raise) with detailed reporting
- **Rich result objects**: ``MetricResult`` contains value, metadata, provenance, and optimization direction
- **Extensive testing**: >95% coverage with property-based tests (Hypothesis)

Installation
------------

.. code-block:: bash

   pip install hydrometrics

Optional dependencies for development and documentation:

.. code-block:: bash

   pip install hydrometrics[dev]    # Development dependencies
   pip install hydrometrics[docs]   # Documentation dependencies
   pip install hydrometrics[all]    # All optional dependencies

Requires Python ≥ 3.9.

Quickstart
----------

.. code-block:: python

   import numpy as np
   from hydrometrics import nse, kge_2012, mae

   # Observed and simulated streamflow
   obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
   sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

   # Nash-Sutcliffe Efficiency
   nse_result = nse(obs, sim)
   print(nse_result)
   # NSE: 0.92 (direction: maximize, bounds: (-inf, 1.0))

   # Kling-Gupta Efficiency (2012)
   kge_result = kge_2012(obs, sim)
   print(kge_result)
   # KGE 2012: 0.95 (direction: maximize, bounds: (-inf, 1.0))

   # Mean Absolute Error
   mae_result = mae(obs, sim)
   print(mae_result)
   # Mean Absolute Error: 0.38 (direction: minimize, bounds: (0.0, inf))

All metrics return a ``MetricResult`` object with:

- **value**: The computed metric value
- **direction**: "maximize" or "minimize"
- **bounds**: Theoretical bounds (lower, upper)
- **parameters**: Parameters used in computation
- **reference**: DOI or citation
- **nan_info**: NaN handling information

Documentation Language
----------------------

- `Русский <../ru/index.html>`_ — основная версия документации (Russian - primary)
- **English** (current) — complete alternative

Metric Reference
----------------

.. toctree::
   :maxdepth: 2
   :caption: Hydrological Metrics

   metric_reference/hydro/index

Links
-----

- **Repository**: https://github.com/SergeyIglin/hydrometrics
- **Issues**: https://github.com/SergeyIglin/hydrometrics/issues
- **Documentation**: https://hydrometrics.readthedocs.io
- **PyPI**: https://pypi.org/project/hydrometrics/

Citation
--------

If you use HydroMetrics in your research, please cite the relevant metric references listed in each metric's documentation.

## Links

- **Repository**: https://github.com/SergeyIglin/hydrometrics
- **Issues**: https://github.com/SergeyIglin/hydrometrics/issues
- **Documentation**: https://hydrometrics.readthedocs.io
- **PyPI**: https://pypi.org/project/hydrometrics/

## Citation

If you use HydroMetrics in your research, please cite the relevant metric references listed in each metric's documentation.