# Быстрый старт

Это руководство покажет основные возможности HydroMetrics за 5 минут.

## Импорт и базовый пример

```python
import numpy as np
from hydrometrics import nse, kge_2012, mae, pbias

# Наблюдаемые и смоделированные расходы (м³/с)
obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9, 11, 14])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5, 10.5, 13.8])

# Коэффициент Наша-Сутклиффа (NSE)
result = nse(obs, sim)
print(result)
# NSE: 0.94... (direction: maximize, bounds: (-inf, 1.0))

# KGE 2012 (рекомендуется)
result = kge_2012(obs, sim)
print(result)
# KGE 2012: 0.96... (direction: maximize, bounds: (-inf, 1.0))

# Bias (смещение)
result = pbias(obs, sim)
print(result)
# PBIAS: -2.1...% (direction: minimize, bounds: (-inf, inf))
```

Все метрики возвращают объект `MetricResult` — его можно печатать, преобразовывать в float, словарь.

## Работа с пропусками (NaN)

```python
import numpy as np
from hydrometrics import nse

obs = np.array([10, 12, np.nan, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

# По умолчанию nan_policy="omit" — пропуски игнорируются
result = nse(obs, sim)
print(result.nan_info)
# {'policy': 'omit', 'n_nan_removed': 1, 'n_total': 10}
```

Политики: `"omit"` (по умолчанию), `"propagate"`, `"raise"`.

## Sentinel-значения (коды пропусков)

Гидрологические данные часто используют коды вроде -999, -9999:

```python
from hydrometrics import nse

obs = [10, 12, -999, 14, 13]
sim = [9.5, 11.8, 14.5, 14.2, 13.5]

# Автоматически заменит -999 на NaN перед расчётом
result = nse(obs, sim, sentinel=-999)
```

## Pandas / Xarray / Polars — без изменений в коде

```python
import pandas as pd
import xarray as xr
from hydrometrics import nse

# Pandas Series
obs_s = pd.Series([10, 12, 15, 14, 13])
sim_s = pd.Series([9.5, 11.8, 14.5, 14.2, 13.5])
nse(obs_s, sim_s)  # Работает автоматически

# Xarray DataArray
obs_x = xr.DataArray([10, 12, 15, 14, 13], dims=["time"])
sim_x = xr.DataArray([9.5, 11.8, 14.5, 14.2, 13.5], dims=["time"])
nse(obs_x, sim_x)  # Работает автоматически
```

## Групповые вычисления (по станциям, лидам, и т.д.)

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

# Экспорт в DataFrame
result.to_pandas()
#    gauge        NSE
# 0      A  0.987...
# 1      B  0.952...
```

## Вероятностные прогнозы (CRPS)

```python
import numpy as np
from hydrometrics import crps

# Детерминированный прогноз
obs = np.array([10, 12, 15])
sim = np.array([9.5, 11.8, 14.5])
crps(obs, sim)  # Равен MAE для детерминированного

# Ансамблевый прогноз (n_samples, n_ensemble)
obs = np.array([10, 12, 15])
sim_ens = np.array([[9, 10, 11], [11, 12, 13], [14, 15, 16]])
crps(obs, sim_ens)  # CRPS для ансамбля
```

## Классификация (F1, ROC-AUC, EDI, SEDI)

```python
from hydrometrics import f1_score, roc_auc, edi, sedi

# Бинарная классификация (наводнение: да/нет)
obs = np.array([0, 1, 1, 0, 1, 0, 1, 1])
sim = np.array([0, 1, 1, 0, 0, 0, 1, 1])

f1_score(obs, sim)
roc_auc(obs, sim)  # Требует вероятности в sim

# Редкие события — EDI/SEDI (устойчивы к базовой частоте)
edi(obs, sim)
sedi(obs, sim)
```

## Получение метаданных метрики

```python
from hydrometrics import nse, kge_2012
import numpy as np

obs = np.array([10, 12, 15])
sim = np.array([9.5, 11.8, 14.5])

result = nse(obs, sim)
print(result.name)           # "Nash-Sutcliffe Efficiency"
print(result.direction)      # "maximize"
print(result.bounds)         # (-inf, 1.0)
print(result.reference)      # DOI ссылка
print(result.meta["formula"]) # LaTeX формула
print(result.to_dict())      # Полный словарь для сериализации
```

## Следующие шаги

- [Руководство пользователя](user_guide/input_data.md) — подробнее о входных данных
- [Справочник метрик](metric_reference/regression.md) — все метрики с формулами
- [API Reference](api_reference.md) — полный список функций
- [Примеры](examples/basic_usage.md) — готовые скрипты