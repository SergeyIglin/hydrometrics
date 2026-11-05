# Групповые вычисления

Функция `compute_grouped` позволяет вычислять метрики для групп данных (станции, лиды прогноза, сезоны и т.д.).

## Базовое использование

```python
import pandas as pd
from hydrometrics import nse, compute_grouped

df = pd.DataFrame({
    "gauge": ["A", "A", "B", "B", "A", "B"],
    "time": pd.date_range("2020-01-01", periods=6, freq="D"),
    "obs": [10, 12, 8, 9, 11, 10],
    "sim": [9.5, 11.8, 7.8, 9.2, 10.5, 9.8]
})

# NSE по каждой станции
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by="gauge")

print(result)
# GroupedResult(name='NSE', group_by=('gauge',), n_groups=2)

# DataFrame с результатами
result.to_pandas()
#    gauge        NSE
# 0      A  0.987...
# 1      B  0.952...
```

## Группировка по нескольким колонкам

```python
df = pd.DataFrame({
    "gauge": ["A", "A", "A", "B", "B", "B"],
    "season": ["DJF", "MAM", "JJA", "DJF", "MAM", "JJA"],
    "obs": [10, 12, 15, 8, 9, 11],
    "sim": [9.5, 11.8, 14.5, 7.8, 9.2, 10.5]
})

# Группировка по станции И сезону
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by=["gauge", "season"])
result.to_pandas()
#   gauge season        NSE
# 0     A    DJF  0.99...
# 1     A    MAM  0.98...
# 2     A    JJA  0.97...
# 3     B    DJF  0.95...
# ...
```

## Передача дополнительных параметров метрики

```python
# log_nse требует параметр eps
result = compute_grouped(
    log_nse,
    df,
    obs="obs",
    sim="sim",
    group_by="gauge",
    eps=1e-6  # Передаётся в log_nse
)
```

## Работа с Xarray

```python
import xarray as xr
from hydrometrics import nse, compute_grouped

# (time=100, station=5, lead=3)
obs = xr.DataArray(
    np.random.randn(100, 5, 3),
    dims=["time", "station", "lead"],
    coords={"station": ["A", "B", "C", "D", "E"]}
)
sim = obs + 0.1 * np.random.randn(100, 5, 3)

# Группировка по lead time
result = compute_grouped(nse, obs, sim, group_by="lead")
result.to_xarray()
# <xarray.Dataset>
# Dimensions:  (lead: 3)
# Coordinates:
#   * lead     (lead) int64 0 1 2
# Data variables:
#     NSE      (lead) float64 0.98 0.95 0.92
```

## Словарь группировки (для сложных случаев)

```python
# group_by как dict: ключ — имя группы, значение — массив/Series
groups = {
    "gauge": df["gauge"],
    "month": df["time"].dt.month
}
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by=groups)
```

## GroupedResult методы

| Метод | Описание |
|-------|----------|
| `to_pandas()` | `pd.DataFrame` с колонками групп и значением метрики |
| `to_xarray()` | `xr.Dataset` (если вход был xarray) |
| `to_dict()` | Словарь `{group_tuple: value}` |
| `groups` | Кортеж кортежей значений групп |
| `values` | Массив значений метрик |
| `group_names` | Имена группирующих переменных |

## Итерация

```python
for group_key, metric_value in result:
    print(f"Group {group_key}: {metric_value:.4f}")

# Или по именованным группам
for i, group in enumerate(result.groups):
    print(f"{dict(zip(result.group_names, group))}: {result.values[i]:.4f}")
```

## Агрегация результатов

```python
import numpy as np

# Средний NSE по всем станциям
mean_nse = np.mean(result.values)

# Стандартное отклонение
std_nse = np.std(result.values)

# Лучшая/худшая станция
best_idx = np.argmax(result.values)
worst_idx = np.argmin(result.values)
```

## Производительность

Для больших данных `compute_grouped` эффективнее ручного цикла:
- Векторизованная обработка внутри групп
- Автоматический выбор бэкенда
- Минимальные накладные расходы

```python
# Быстро: одна векторизованная операция
result = compute_grouped(nse, large_df, obs="obs", sim="sim", group_by="station")

# Медленно: Python-цикл
results = {}
for station, group in large_df.groupby("station"):
    results[station] = nse(group["obs"], group["sim"])
```