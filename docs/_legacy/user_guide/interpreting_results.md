# Интерпретация результатов

Все метрики возвращают объект `MetricResult` с полной информацией для интерпретации.

## Структура MetricResult

```python
from hydrometrics import nse
import numpy as np

obs = np.array([10, 12, 15, 14, 13])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5])
result = nse(obs, sim)

# Основные атрибуты
result.value        # float — значение метрики (0.94...)
result.name         # str — название ("Nash-Sutcliffe Efficiency")
result.direction    # "maximize" или "minimize"
result.bounds       # tuple — теоретические границы ((-inf, 1.0))
result.reference    # str — DOI/цитирование
result.nan_info     # dict — информация о NaN
result.meta         # dict — дополнительные метаданные
```

## Направление оптимизации (`direction`)

| Значение | Значение | Примеры метрик |
|----------|----------|----------------|
| `"maximize"` | Чем выше, тем лучше | NSE, KGE, R², Correlation |
| `"minimize"` | Чем ниже, тем лучше | MAE, RMSE, PBIAS, CRPS |

```python
if result.direction == "maximize":
    print(f"Модель хорошая: {result.value:.3f} (ближе к {result.bounds[1]})")
else:
    print(f"Ошибка модели: {result.value:.3f} (ближе к {result.bounds[0]})")
```

## Границы (`bounds`)

Теоретические пределы помогают оценить качество:

```python
result = nse(obs, sim)
# bounds = (-inf, 1.0)
# 1.0 = идеальная модель
# 0.0 = та же точность, что среднее наблюдений
# < 0 = хуже, чем просто использовать среднее

result = mae(obs, sim)
# bounds = (0.0, inf)
# 0.0 = идеальная модель
```

**Практическая интерпретация NSE/KGE:**
- > 0.75: Очень хорошая
- 0.65–0.75: Хорошая
- 0.50–0.65: Удовлетворительная
- < 0.50: Неудовлетворительная

## Метаданные (`meta`)

```python
result.meta["description"]  # Описание метрики
result.meta["formula"]      # LaTeX формула

# Пример для NSE:
# description: "Nash-Sutcliffe Efficiency measures the relative magnitude of the residual variance..."
# formula: "1 - \\frac{\\sum (y - \\hat{y})^2}{\\sum (y - \\bar{y})^2}"
```

## Приведение к базовым типам

```python
float(result)      # Числовое значение
str(result)        # Красивое представление
repr(result)       # Подробное представление
result.to_dict()   # Полный словарь для JSON/сериализации
```

## Специальные результаты

### kge_components — возвращает dict

```python
from hydrometrics import kge_components

result = kge_components(obs, sim, version="2012")
print(result.value)
# {'r': 0.98, 'alpha': 1.02, 'beta': 0.99, 'gamma': 1.01}

# Каждый компонент — отдельное значение
for name, val in result.value.items():
    print(f"{name}: {val:.3f}")
```

### Групповые результаты (GroupedResult)

```python
from hydrometrics import compute_grouped
import pandas as pd

df = pd.DataFrame({
    "gauge": ["A", "A", "B", "B"],
    "obs": [10, 12, 8, 9],
    "sim": [9.5, 11.8, 7.8, 9.2]
})
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by="gauge")

result.to_pandas()
#    gauge        NSE
# 0      A  0.987...
# 1      B  0.952...

for group, value in result:
    print(f"{group}: {value:.3f}")
```

## Сравнение моделей

```python
from hydrometrics import nse, kge_2012, mae

models = {
    "Model_A": sim_a,
    "Model_B": sim_b,
    "Model_C": sim_c
}

for name, sim in models.items():
    nse_val = nse(obs, sim)
    kge_val = kge_2012(obs, sim)
    mae_val = mae(obs, sim)
    print(f"{name}: NSE={float(nse_val):.3f}, KGE={float(kge_val):.3f}, MAE={float(mae_val):.3f}")
```

## Экспорт отчётов

```python
import json

results = {
    "nse": nse(obs, sim).to_dict(),
    "kge": kge_2012(obs, sim).to_dict(),
    "mae": mae(obs, sim).to_dict()
}

with open("metrics_report.json", "w") as f:
    json.dump(results, f, indent=2)
```