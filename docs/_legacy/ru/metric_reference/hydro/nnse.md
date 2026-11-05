# Нормализованный NSE (NNSE)

## Название и назначение

**Нормализованный коэффициент Наша-Сатклиффа (Normalized NSE, NNSE)** — версия NSE, нормализованная к диапазону [0, 1]. Удобна для интерпретации и сравнения, так как значения всегда неотрицательны.

Полезна, когда важно иметь метрику в фиксированном диапазоне для отчётности или оптимизации.

## Математическая формула

$$\text{NNSE} = \frac{1}{2 - \text{NSE}} = \frac{1}{2 - \left(1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}\right)} = \frac{\sum (y_i - \bar{y})^2}{\sum (y_i - \bar{y})^2 + \sum (y_i - \hat{y}_i)^2}$$

Где:
- $y_i$ — наблюдаемое значение
- $\hat{y}_i$ — смоделированное значение
- $\bar{y}$ — среднее наблюдаемое значение
- $n$ — количество валидных пар

**Реализация** (`_nnse_core`):
- Вычисляет NSE, затем применяет трансформацию $1 / (2 - \text{NSE})$
- При NSE = 1 → NNSE = 1.0
- При NSE = 0 → NNSE = 0.5
- При NSE → -∞ → NNSE → 0.0

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Идеальное совпадение (sim = obs) |
| **0.5** | Эквивалентно NSE = 0 (модель = среднее) |
| **0.0 – 0.5** | Эквивалентно NSE < 0 (хуже среднего) |
| **[0, 1]** | Фиксированный диапазон |

Направление: **maximize**
Идеальное значение: **1.0**

## Публичный API

```python
from hydrometrics import nnse

result = nnse(
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

**Импорт**: `from hydrometrics import nnse`

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
from hydrometrics import nnse

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = nnse(obs, sim)
print(result)
# NNSE: 0.9886 (direction: maximize, bounds: (0.0, 1.0))
```

## Связанные метрики

- [NSE (nse)](nse.md) — классический NSE в диапазоне (-∞, 1]
- [Modified NSE (modified_nse)](modified_nse.md) — с абсолютными ошибками
- [RSR (rsr)](rsr.md) — связан: RSR² = 1 - NSE

## Научные ссылки

1. **Nash, J. E., & Sutcliffe, J. V. (1970).** River flow forecasting through conceptual models part I. *Journal of Hydrology*, 10(3), 282-290. DOI: 10.1016/0022-1694(70)90255-6

2. **Moriasi, D. N., et al. (2007).** Model evaluation guidelines for systematic quantification of accuracy in watershed simulations. *Transactions of the ASABE*, 50(3), 885-900.