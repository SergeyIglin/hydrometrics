# hydrometrics

Metrics for verifying hydrological and hydrometeorological models: NSE, KGE,
RMSE, volumetric efficiency, CRPS, Brier score, event-based skill scores and
others, with inputs from NumPy, pandas, polars and xarray.

## Installation

```bash
pip install hydrometrics
```

The core package depends only on NumPy and requires Python 3.10 or newer.
Optional extras:

```bash
pip install "hydrometrics[pandas]"   # also [polars], [xarray]
pip install "hydrometrics[scipy]"    # required by spearman_r and kendall_tau
pip install "hydrometrics[all]"      # all backends and SciPy
 For development:

```bash
pip install -e ".[dev]"
```

## Minimal example

```python
import numpy as np
import hydrometrics as hm

rng = np.random.default_rng(42)
q_obs = 20 + rng.gamma(2.0, 5.0, 365)                      # observed discharge, m3/s
q_sim = 0.9 * q_obs + 3 + rng.normal(0, 2, 365)            # simulated discharge, m3/s

result = hm.nse(q_obs, q_sim, nan_policy="omit")
print(float(result))      # a MetricResult converts to float for scalar values
print(result.direction)   # "maximize"
```

## Documentation

Documentation is available in two languages (Russian is the source language):

- Russian: <https://hydrometrics.readthedocs.io/ru/latest/>
- English: <https://hydrometrics.readthedocs.io/en/latest/>

To build it locally:

```bash
pip install -e .[docs]
make html          # on Windows: make.bat html
```

`make html` builds both languages; `make html-ru` and `make html-en` build one (the English pages
come from the gettext catalogs in `docs/locale/en`). `make linkcheck` checks the links. Russian is the
source language of all pages.


## License

MIT, see [LICENSE](https://github.com/SergeyIglin/hydrometrics/blob/main/LICENSE).
