# Входные данные

Все метрики принимают наблюдаемые (`obs`) и смоделированные (`sim`) значения в различных форматах.

## Поддерживаемые форматы

### NumPy arrays (базовый)
```python
import numpy as np
from hydrometrics import nse

obs = np.array([10, 12, 15, 14, 13])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5])
nse(obs, sim)
```

### Pandas Series / DataFrame
```python
import pandas as pd
from hydrometrics import nse

obs = pd.Series([10, 12, 15, 14, 13])
sim = pd.Series([9.5, 11.8, 14.5, 14.2, 13.5])
nse(obs, sim)
```

DataFrame с колонками:
```python
df = pd.DataFrame({"obs": [10, 12, 15], "sim": [9.5, 11.8, 14.5]})
nse(df["obs"], df["sim"])
```

### Xarray DataArray / Dataset
```python
import xarray as xr
from hydrometrics import nse

obs = xr.DataArray([10, 12, 15], dims=["time"])
sim = xr.DataArray([9.5, 11.8, 14.5], dims=["time"])
nse(obs, sim)
```

### Polars Series / DataFrame
```python
import polars as pl
from hydrometrics import nse

obs = pl.Series([10, 12, 15])
sim = pl.Series([9.5, 11.8, 14.5])
nse(obs, sim)
```

### Python списки и кортежи
```python
from hydrometrics import nse

obs = [10, 12, 15, 14, 13]
sim = [9.5, 11.8, 14.5, 14.2, 13.5]
nse(obs, sim)  # Автоматически конвертируется в numpy
```

## Многомерные данные

Параметр `axis` позволяет вычислять метрики вдоль заданной оси:

```python
import numpy as np
from hydrometrics import nse

# (time, stations) - вычисляем NSE по времени для каждой станции
obs = np.random.randn(100, 5)
sim = obs + np.random.randn(100, 5) * 0.1

# axis=0: агрегируем по времени (первая ось)
result = nse(obs, sim, axis=0)
# result.shape == (5,) — NSE для каждой станции
```

Для xarray можно использовать именованные измерения:
```python
import xarray as xr
from hydrometrics import nse

obs = xr.DataArray(np.random.randn(100, 5), dims=["time", "station"])
sim = obs + 0.1
nse(obs, sim, axis=0)  # или axis="time"
```

## Требования к данным

1. **Одинаковая форма**: `obs` и `sim` должны иметь одинаковую форму (или быть broadcast-совместимыми)
2. **Числовые типы**: Поддерживаются int, float, bool (для классификации)
3. **Пропуски**: NaN обрабатываются согласно `nan_policy` (по умолчанию `"omit"`)
4. **Sentinel-значения**: Коды пропусков (-999, -9999) заменяются через параметр `sentinel`

```python
from hydrometrics import nse

# Замена -999 на NaN перед расчётом
obs = [10, 12, -999, 14, 13]
sim = [9.5, 11.8, 14.5, 14.2, 13.5]
nse(obs, sim, sentinel=-999)
```

## Взвешенные метрики

Параметр `sample_weight` (передаётся как `weight` в ядро метрики):

```python
import numpy as np
from hydrometrics import nse

obs = np.array([10, 12, 15, 14, 13])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5])
weights = np.array([1.0, 1.0, 2.0, 1.0, 1.0])  # Третье наблюдение важнее

nse(obs, sim, sample_weight=weights)
```

Не все метрики поддерживают веса — см. справочник API.