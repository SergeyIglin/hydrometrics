# Многобэкендная работа

Примеры использования с Pandas, Xarray и Polars.

## Pandas DataFrame

```python
import pandas as pd
import numpy as np
from hydrometrics import nse, kge_2012, compute_grouped

# Данные с DateTime индексом
dates = pd.date_range("2020-01-01", periods=365, freq="D")
np.random.seed(42)

df = pd.DataFrame({
    "date": dates,
    "station": np.repeat(["A", "B", "C"], 365//3 + 1)[:365],
    "obs": np.random.lognormal(2.0, 0.5, 365),
    "sim": np.random.lognormal(2.0, 0.5, 365) * 1.05
})

# Общий NSE
print(f"Overall NSE: {nse(df['obs'], df['sim'])}")

# По станциям
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by="station")
print(result.to_pandas())
#   station        NSE
# 0       A  0.92...
# 1       B  0.89...
# 2       C  0.94...

# По месяцам
df["month"] = df["date"].dt.month
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by="month")
print(result.to_pandas())
```

## Xarray DataArray (многомерные данные)

```python
import xarray as xr
import numpy as np
from hydrometrics import nse, kge_2012, compute_grouped

# (time=730, station=10, lead=5) — 2 года, 10 станций, 5 лидов прогноза
np.random.seed(42)
time = pd.date_range("2020-01-01", periods=730, freq="D")
stations = [f"G{i:02d}" for i in range(10)]
leads = [1, 2, 3, 5, 7]  # дни вперёд

obs = xr.DataArray(
    np.random.lognormal(2.0, 0.5, (730, 10, 5)),
    dims=["time", "station", "lead"],
    coords={"time": time, "station": stations, "lead": leads},
    name="observed_flow"
)

sim = obs * np.random.lognormal(-0.02, 0.15, obs.shape) + np.random.normal(0, 2, obs.shape)
sim = xr.DataArray(np.maximum(sim, 0.1), dims=obs.dims, coords=obs.coords, name="simulated_flow")

# NSE по времени для каждой станции и лида
result = compute_grouped(nse, obs, sim, group_by=["station", "lead"])
ds = result.to_xarray()
print(ds)
# <xarray.Dataset>
# Dimensions:  (station: 10, lead: 5)
# Coordinates:
#   * station  (station) <U3 'G00' 'G01' ... 'G09'
#   * lead     (lead) int64 1 2 3 5 7
# Data variables:
#     NSE      (station, lead) float64 ...

# Средний NSE по станциям для каждого лида
mean_by_lead = ds["NSE"].mean(dim="station")
print("Mean NSE by lead:")
print(mean_by_lead.values)

# Лучшая/худшая станция
best_station = ds["NSE"].mean(dim="lead").argmax().item()
print(f"Best station: {stations[best_station]}")
```

## Polars DataFrame

```python
import polars as pl
import numpy as np
from hydrometrics import nse, kge_2012, mae, compute_grouped

np.random.seed(42)
n = 100000  # 100k строк

df = pl.DataFrame({
    "gauge": pl.Series(np.random.choice(["A", "B", "C", "D", "E"], n)),
    "obs": pl.Series(np.random.lognormal(2.0, 0.5, n)),
    "sim": pl.Series(np.random.lognormal(2.0, 0.5, n) * 1.03)
})

# Общие метрики
print(f"NSE: {nse(df['obs'], df['sim'])}")
print(f"KGE: {kge_2012(df['obs'], df['sim'])}")
print(f"MAE: {mae(df['obs'], df['sim'])}")

# Групповые (быстро на Polars)
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by="gauge")
print(result.to_pandas())
#   gauge        NSE
# 0     A  0.94...
# 1     B  0.91...
# ...
```

## Смешанные бэкенды

```python
import pandas as pd
import numpy as np
from hydrometrics import nse

# Pandas Series + NumPy array
obs_pd = pd.Series(np.random.lognormal(2.0, 0.5, 100))
sim_np = np.random.lognormal(2.0, 0.5, 100) * 1.05

# Автоматически конвертирует к NumPy
result = nse(obs_pd, sim_np)
print(f"Mixed backend NSE: {result}")
```

## Производительность

```python
import time
import numpy as np
import polars as pl
from hydrometrics import nse

np.random.seed(42)
n = 1_000_000  # 1M точек

obs_np = np.random.lognormal(2.0, 0.5, n)
sim_np = obs_np * np.random.lognormal(-0.02, 0.15, n) + np.random.normal(0, 2, n)

# NumPy
t0 = time.time()
nse(obs_np, sim_np)
print(f"NumPy: {time.time() - t0:.3f}s")

# Polars
obs_pl = pl.Series(obs_np)
sim_pl = pl.Series(sim_np)
t0 = time.time()
nse(obs_pl, sim_pl)
print(f"Polars: {time.time() - t0:.3f}s")

# Ожидается: Polars быстрее на больших данных благодаря многопоточности
```