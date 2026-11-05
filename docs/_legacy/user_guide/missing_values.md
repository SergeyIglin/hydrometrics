# Обработка пропущенных значений

## Политики NaN (`nan_policy`)

Все метрики поддерживают три политики обработки NaN:

### 1. `omit` (по умолчанию)
Пропускает пары, где есть хотя бы один NaN:

```python
import numpy as np
from hydrometrics import nse

obs = np.array([10, 12, np.nan, 14, 13])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5])

result = nse(obs, sim, nan_policy="omit")
print(result.nan_info)
# {'policy': 'omit', 'n_nan_removed': 1, 'n_total': 5}
```

### 2. `propagate`
Возвращает NaN, если есть любые пропуски:

```python
result = nse(obs, sim, nan_policy="propagate")
# result.value == np.nan
```

### 3. `raise`
Выбрасывает исключение при обнаружении NaN:

```python
nse(obs, sim, nan_policy="raise")
# ValueError: Input arrays contain NaN values
```

## Sentinel-значения (коды пропусков)

Гидрологические данные часто используют специальные коды для пропусков:

```python
from hydrometrics import nse

# Типичные коды: -999, -9999, -999.9
obs = [10, 12, -999, 14, 13]
sim = [9.5, 11.8, 14.5, 14.2, 13.5]

# Автоматически заменит -999 на NaN
result = nse(obs, sim, sentinel=-999)

# Несколько кодов сразу
obs = [10, -999, 15, -9999, 13]
result = nse(obs, sim, sentinel=[-999, -9999])
```

## Комбинация sentinel + nan_policy

```python
# Сначала sentinel заменяет коды на NaN, затем nan_policy обрабатывает NaN
obs = [10, -999, 15, 14, 13]
sim = [9.5, 11.8, 14.5, 14.2, 13.5]

# omit: игнорирует -999
nse(obs, sim, sentinel=-999, nan_policy="omit")

# raise: ошибка на -999
nse(obs, sim, sentinel=-999, nan_policy="raise")
```

## Информация о NaN в результате

Каждый `MetricResult` содержит поле `nan_info`:

```python
result = nse(obs, sim, nan_policy="omit")
print(result.nan_info)
# {
#     'policy': 'omit',
#     'n_nan_removed': 2,
#     'n_total': 100,
#     'n_valid': 98
# }
```

Поля:
- `policy` — использованная политика
- `n_nan_removed` — количество удалённых пар
- `n_total` — исходное количество элементов
- `n_valid` — количество валидных пар после очистки

## Особенности для многомерных данных

При `axis` не-None NaN обрабатываются **по срезам**:

```python
import numpy as np
from hydrometrics import nse

# (time=10, stations=3)
obs = np.random.randn(10, 3)
sim = np.random.randn(10, 3)
obs[2, 1] = np.nan  # NaN в станции 1, момент 2

# axis=0: по времени для каждой станции
result = nse(obs, sim, axis=0, nan_policy="omit")
# Станция 1: будет использовано 9 значений вместо 10
# Станции 0 и 2: 10 значений
```

## Рекомендации

| Ситуация | Рекомендация |
|----------|--------------|
| Редкие случайные пропуски | `nan_policy="omit"` (по умолчанию) |
| Системные пропуски (сенсоры) | `sentinel` + `omit` |
| Строгий контроль качества | `nan_policy="raise"` |
| Проверка полноты данных | `nan_policy="propagate"` + проверка `np.isnan(result.value)` |