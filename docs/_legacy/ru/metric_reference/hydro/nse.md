# Коэффициент Наша-Сатклиффа (NSE)

## Название и назначение

**Коэффициент Наша-Сатклиффа (Nash-Sutcliffe Efficiency)** — классическая метрика качества гидрологического моделирования, оценивающая, насколько хорошо смоделированные значения воспроизводят наблюдаемые по сравнению с использованием среднего наблюдаемого значения как наивного прогноза.

Используется для оценки качества моделирования стока, уровня воды, осадков и других гидрологических переменных. Является стандартом де-факто в гидрологии с 1970 года.

## Математическая формула

$$\\text{NSE} = 1 - \\frac{\\sum_{i=1}^{n} (y_i - \\hat{y}_i)^2}{\\sum_{i=1}^{n} (y_i - \\bar{y})^2}$$

Где:
- $y_i$ — наблюдаемое значение в момент $i$
- $\\hat{y}_i$ — смоделированное значение в момент $i$
- $\\bar{y} = \\frac{1}{n}\\sum_{i=1}^{n} y_i$ — среднее наблюдаемое значение
- $n$ — количество валидных пар наблюдений (после удаления NaN)

**Реализация в коде** (`hydrometrics/backends/numpy.py`, функция `_nse_core`):
- Знаменатель: сумма квадратов отклонений от среднего наблюдений (с учётом весов, если заданы)
- Числитель: сумма квадратов ошибок моделирования
- Использует `np.nansum` для автоматического игнорирования NaN
- Поддерживает взвешенное вычисление через параметр `weight`
- Поддерживает `axis` и `reduction` для многомерных массивов

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Идеальное совпадение (sim = obs) |
| **0.0** | Модель не лучше, чем использование среднего наблюдений как прогноза |
| **< 0.0** | Модель хуже, чем среднее наблюдений |
| **(-∞, 1.0]** | Теоретический диапазон |

**Гидрологические бенчмарки (Moriasi et al., 2007):**
- **> 0.75**: Очень хорошо
- **0.65 – 0.75**: Хорошо
- **0.50 – 0.65**: Удовлетворительно
- **< 0.50**: Неудовлетворительно

Направление оптимизации: **maximize** (чем больше, тем лучше)
Идеальное значение: **1.0**

## Публичный API

```python
from hydrometrics import nse

result = nse(
    obs: array-like,
    sim: array-like,
    *,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Импорт**: `from hydrometrics import nse`

## Параметры и возвращаемое значение

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `obs` | array-like | обязательный | Наблюдаемые значения |
| `sim` | array-like | обязательный | Смоделированные значения |
| `weight` | array-like | `None` | Веса выборки (broadcastable к obs/sim) |
| `axis` | int | `None` | Ось для вычислений (None = сплющить) |
| `reduction` | str | `"mean"` | `"mean"`, `"sum"` или `"none"` |
| `nan_policy` | str | `"omit"` | `"omit"`, `"propagate"`, `"raise"` |
| `sentinel` | float/list | `None` | Значения-пропуски для конвертации в NaN |

**Возвращает**: `MetricResult` с атрибутами:
- `value`: float или ndarray — значение NSE
- `direction`: `"maximize"`
- `bounds`: `(-np.inf, 1.0)`
- `name`: `"Nash-Sutcliffe Efficiency"`
- `reference`: `"Nash & Sutcliffe (1970), DOI: 10.1016/0022-1694(70)90255-6"`
- `parameters`: dict с использованными параметрами
- `nan_info`: dict с информацией об обработке NaN
- `meta`: dict с описанием и формулой

## Python пример

```python
import numpy as np
from hydrometrics import nse

# Наблюдаемые и смоделированные расходы (м³/с)
obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

# Вычисление NSE
result = nse(obs, sim)

print(result)
# NSE: 0.9772 (direction: maximize, bounds: (-inf, 1.0))

# Доступ к отдельным атрибутам
print(f"Значение: {float(result):.4f}")
print(f"Направление: {result.direction}")
print(f"Границы: {result.bounds}")
print(f"Ссылка: {result.reference}")
```

**Ожидаемый вывод:**
```
NSE: 0.9772 (direction: maximize, bounds: (-inf, 1.0))
Значение: 0.9772
Направление: maximize
Границы: (-inf, 1.0)
Ссылка: Nash & Sutcliffe (1970), DOI: 10.1016/0022-1694(70)90255-6
```

## Работа с многомерными данными

```python
import numpy as np
from hydrometrics import nse

# 2D данные: 10 временных шагов × 3 станции
obs_2d = np.random.rand(10, 3) * 100
sim_2d = obs_2d + np.random.randn(10, 3) * 5

# NSE по каждой станции (axis=0)
result_per_station = nse(obs_2d, sim_2d, axis=0, reduction="none")
print(result_per_station.value)  # array([0.92, 0.89, 0.95])

# Средний NSE по всем станциям
result_mean = nse(obs_2d, sim_2d, axis=0, reduction="mean")
print(float(result_mean))  # 0.92
```

## Граничные случаи (Edge Cases)

| Сценарий | Поведение |
|----------|-----------|
| Все `obs` константны (дисперсия = 0) | Возвращает `NaN` (деление на ноль) |
| Менее 2 валидных пар после удаления NaN | Возвращает `NaN` |
| Наличие NaN в данных (nan_policy="omit") | Парное удаление NaN, вычисление на оставшихся |
| Наличие NaN (nan_policy="propagate") | Возвращает `NaN` |
| Наличие NaN (nan_policy="raise") | Вызывает `ValueError` |
| Sentinel values (-999, -9999) | Конвертируются в NaN перед вычислением через параметр `sentinel` |

## Связанные метрики

- [Log NSE (log_nse)](log_nse.md) — логарифмическая трансформация для акцента на малые расходы
- [Modified NSE (modified_nse)](modified_nse.md) — использование абсолютных ошибок (j=1)
- [Normalized NSE (nnse)](nnse.md) — нормализованная версия в диапазоне [0, 1]
- [Variance-Weighted NSE (nse_variance_weighted)](nse_variance_weighted.md) — для мульти-стационарной оценки
- [RSR (rsr)](rsr.md) — связан через RSR² = 1 - NSE
- [KGE 2012 (kge_2012)](kge_2012.md) — декомпозируемая альтернатива

## Научные ссылки

1. **Nash, J. E., & Sutcliffe, J. V. (1970).** River flow forecasting through conceptual models part I — A discussion of principles. *Journal of Hydrology*, 10(3), 282-290. DOI: [10.1016/0022-1694(70)90255-6](https://doi.org/10.1016/0022-1694(70)90255-6)

2. **Moriasi, D. N., Arnold, J. G., Van Liew, M. W., Bingner, R. L., Harmel, R. D., & Veith, T. L. (2007).** Model evaluation guidelines for systematic quantification of accuracy in watershed simulations. *Transactions of the ASABE*, 50(3), 885-900. DOI: [10.13031/2013.23153](https://doi.org/10.13031/2013.23153)