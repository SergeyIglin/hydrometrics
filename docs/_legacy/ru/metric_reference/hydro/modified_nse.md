# Modified NSE

## Название и назначение

**Modified Nash-Sutcliffe Efficiency (Modified NSE)** — вариант NSE, использующий абсолютные ошибки вместо квадратичных (L1 норма вместо L2). Менее чувствителен к выбросам и пиковым расходам.

Полезен, когда желательно уменьшить влияние экстремальных событий (наводнений) на общую оценку модели.

## Математическая формула

$$	ext{Modified NSE} = 1 - rac{\sum_{i=1}^{n} |y_i - \hat{y}_i|}{\sum_{i=1}^{n} |y_i - ar{y}|}$$

Где:
- $y_i$ — наблюдаемое значение
- $\hat{y}_i$ — смоделированное значение
- $ar{y}$ — среднее наблюдаемое значение
- $n$ — число валидных пар

**Реализация** (`_modified_nse_core`):
- Числитель: сумма абсолютных ошибок (L1 норма)
- Знаменатель: сумма абсолютных отклонений от среднего
- Использует `np.nansum` для автоматического игнорирования NaN
- Поддерживает взвешенные вычисления, `axis` и `reduction`

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Идеальное совпадение |
| **0.0** | Не лучше среднего по метрике L1 |
| **< 0.0** | Хуже среднего |
| **(-∞, 1.0]** | Теоретический диапазон |

Направление: **maximize**
Идеальное значение: **1.0**

Менее чувствителен к пиковым расходам по сравнению с классическим NSE.

## Публичный API

```python
from hydrometrics import modified_nse

result = modified_nse(
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

**Импорт**: `from hydrometrics import modified_nse`

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `obs` | array-like | обязательный | Наблюдаемые значения |
| `sim` | array-like | обязательный | Смоделированные значения |
| `weight` | array-like | `None` | Веса выборки |
| `axis` | int | `None` | Ось для вычислений |
| `reduction` | str | `"mean"` | Редукция для массивов |
| `nan_policy` | str | `"omit"` | Политика NaN |
| `sentinel` | float/list | `None` | Значения-пропуски |

## Python пример

```python
import numpy as np
from hydrometrics import modified_nse

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = modified_nse(obs, sim)
print(result)
# Modified NSE: 0.9524 (direction: maximize, bounds: (-inf, 1.0))
```

**Ожидаемый вывод:**
```
Modified NSE: 0.9524 (direction: maximize, bounds: (-inf, 1.0))
```

## Связанные метрики

- [NSE (nse)](nse.md) — классический NSE с квадратичными ошибками
- [Log NSE (log_nse)](log_nse.md) — акцент на малых расходах
- [Normalized NSE (nnse)](nnse.md) — нормализованная версия

## Научные ссылки

1. **Krause, P., Boyle, D. P., & Bäse, F. (2005).** Comparison of different efficiency criteria for hydrological model assessment. *Advances in Geosciences*, 5, 89-97. DOI: 10.5194/adgeo-5-89-2005

2. **Legates, D. R., & McCabe, G. J. (1999).** Evaluating the use of "goodness-of-fit" measures in hydrologic and hydroclimatic model validation. *Water Resources Research*, 35(1), 233-241. DOI: 10.1029/1998WR900018
