# Поддержка бэкендов

HydroMetrics автоматически определяет тип входных данных и использует соответствующий бэкенд.

## Автоматический диспетч

```python
from hydrometrics import nse

# NumPy (встроен)
import numpy as np
nse(np.array([1,2,3]), np.array([1.1,2.1,2.9]))

# Pandas
import pandas as pd
nse(pd.Series([1,2,3]), pd.Series([1.1,2.1,2.9]))

# Xarray
import xarray as xr
nse(xr.DataArray([1,2,3]), xr.DataArray([1.1,2.1,2.9]))

# Polars
import polars as pl
nse(pl.Series([1,2,3]), pl.Series([1.1,2.1,2.9]))
```

## Установка опциональных бэкендов

```bash
pip install hydrometrics[pandas]
pip install hydrometrics[xarray]
pip install hydrometrics[polars]
pip install hydrometrics[all-backends]  # все сразу
```

Без установки соответствующей библиотеки диспетчер вернёт ошибку при попытке передать её объекты.

## Особенности бэкендов

### Pandas
- Сохраняет индексы (не используются в расчётах)
- Поддерживает `pd.DataFrame` — берутся колонки по именам `obs`/`sim` или первые две числовые

```python
df = pd.DataFrame({
    "obs": [10, 12, 15],
    "sim": [9.5, 11.8, 14.5],
    "other": [1, 2, 3]
})
nse(df["obs"], df["sim"])  # Явное указание колонок
```

### Xarray
- Сохраняет координаты и атрибуты
- Параметр `axis` может быть строкой (именем измерения)
- Для `xr.Dataset` нужно передать `DataArray`

```python
obs = xr.DataArray([10, 12, 15], dims=["time"], coords={"time": pd.date_range("2020", periods=3)})
sim = xr.DataArray([9.5, 11.8, 14.5], dims=["time"])

nse(obs, sim, axis="time")  # Именованное измерение
```

### Polars
- Быстрые DataFrame операции
- Поддерживает `pl.Series` и `pl.DataFrame`

```python
df = pl.DataFrame({"obs": [10, 12, 15], "sim": [9.5, 11.8, 14.5]})
nse(df["obs"], df["sim"])
```

## Смешанные типы

При передаче разных типов (например, `np.array` + `pd.Series`) — конвертируется в NumPy:

```python
import numpy as np
import pandas as pd
from hydrometrics import nse

obs = np.array([10, 12, 15])
sim = pd.Series([9.5, 11.8, 14.5])
nse(obs, sim)  # Работает, конвертирует sim в numpy
```

## Ручной выбор бэкенда

Внутренне используется `hydrometrics.backends.dispatch`. Прямой вызов не требуется — API автоматически делает правильный выбор.

## Производительность

| Бэкенд | Скорость | Память | Лучше для |
|--------|----------|--------|-----------|
| NumPy | Базовая | Низкая | Малые/средние массивы |
| Pandas | Средняя | Средняя | Табличные данные с метаданными |
| Xarray | Средняя | Средняя | Многомерные данные с координатами |
| Polars | **Высокая** | **Низкая** | Большие DataFrame (>100к строк) |

Для больших данных рекомендуется Polars.