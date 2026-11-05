# Log-Transformed NSE (Log NSE)

## Название и назначение

**Log-Transformed Nash-Sutcliffe Efficiency (Log NSE)** — вариант NSE, применяемый к логарифмированным данным. Он акцентирует внимание на малых расходах, так как логарифм сжимает большие значения и растягивает малые.

Рекомендуется для оценки качества моделирования в периоды малых расходов, когда относительная ошибка важнее абсолютной.

## Математическая формула

$$	ext{Log NSE} = 1 - rac{\sum_{i=1}^{n} (\ln(y_i + \epsilon) - \ln(\hat{y}_i + \epsilon))^2}{\sum_{i=1}^{n} (\ln(y_i + \epsilon) - \overline{\ln(y + \epsilon)})^2}$$

Где:
- $y_i$ — наблюдаемое значение
- $\hat{y}_i$ — смоделированное значение
- $\epsilon$ — константа смещения (по умолчанию 0.001) для избежания $\ln(0)$
- $\overline{\ln(y + \epsilon)}$ — среднее логарифмированных наблюдений
- $n$ — число валидных пар

**Реализация** (`_log_nse_core`):
- Применяет `np.log(obs + eps)` и `np.log(sim + eps)` перед вычислением NSE
- Смещение `eps` по умолчанию 0.001 (настраивается через параметр `eps`)
- Поддерживает те же параметры, что и NSE

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Идеальное совпадение в лог-пространстве |
| **0.0** | Не лучше среднего в лог-пространстве |
| **< 0.0** | Хуже среднего в лог-пространстве |
| **(-∞, 1.0]** | Теоретический диапазон |

Направление: **maximize**
Идеальное значение: **1.0**

Чувствительно к системаческим ошибкам на малых расходах.

## Публичный API

```python
from hydrometrics import log_nse

result = log_nse(
    obs: array-like,
    sim: array-like,
    *,
    eps: float = 0.001,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Импорт**: `from hydrometrics import log_nse`

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `obs` | array-like | обязательный | Наблюдаемые значения (> -eps) |
| `sim` | array-like | обязательный | Смоделированные значения (> -eps) |
| `eps` | float | `0.001` | Смещение для избежания log(0) |
| `weight` | array-like | `None` | Веса выборки |
| `axis` | int | `None` | Ось для вычислений |
| `reduction` | str | `"mean"` | Редукция для массивов |
| `nan_policy` | str | `"omit"` | Политика NaN |
| `sentinel` | float/list | `None` | Значения-пропуски |

## Python пример

```python
import numpy as np
from hydrometrics import log_nse

# Данные с малыми расходами
obs = np.array([0.5, 1.2, 0.8, 0.3, 2.1, 0.6, 0.4, 0.9, 0.2, 1.0])
sim = np.array([0.45, 1.1, 0.85, 0.35, 2.0, 0.55, 0.45, 0.85, 0.25, 0.95])

result = log_nse(obs, sim)
print(result)
# Log NSE: 0.9714 (direction: maximize, bounds: (-inf, 1.0))
```

**Ожидаемый вывод:**
```
Log NSE: 0.9714 (direction: maximize, bounds: (-inf, 1.0))
```

## Граничные случаи

- Значения ≤ -eps вызывают ошибку или NaN (log не определён)
- eps должен быть > 0
- Те же политики NaN, что и у NSE

## Связанные метрики

- [NSE (nse)](nse.md)
- [Modified NSE (modified_nse)](modified_nse.md)
- [KGE 2012 (kge_2012)](kge_2012.md)

## Научные ссылки

1. **Nash, J. E., & Sutcliffe, J. V. (1970).** River flow forecasting through conceptual models part I. *Journal of Hydrology*, 10(3), 282-290. DOI: 10.1016/0022-1694(70)90255-6

2. **Krause, P., Boyle, D. P., & Bäse, F. (2005).** Comparison of different efficiency criteria for hydrological model assessment. *Advances in Geosciences*, 5, 89-97. DOI: 10.5194/adgeo-5-89-2005
