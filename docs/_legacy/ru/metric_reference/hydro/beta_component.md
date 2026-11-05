# beta_component (Bias Ratio β)

## Название и назначение

**beta_component** — компонента смещения (β) из KGE 2012. Отношение среднего смоделированных значений к среднему наблюдаемых. Оценивает систематическое завышение или занижение модели.

## Математическая формула

$$\beta = \frac{\bar{\hat{y}}}{\bar{y}} = \frac{\frac{1}{n}\sum_{i=1}^{n}\hat{y}_i}{\frac{1}{n}\sum_{i=1}^{n}y_i}$$

**Реализация** (`_beta_core`):
- Отношение выборочных средних
- β > 1: систематическое завышение
- β < 1: систематическое занижение

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Нет систематического смещения |
| **> 1.0** | Систематическое завышение (positive bias) |
| **< 1.0** | Систематическое занижение (negative bias) |
| **(0, ∞)** | Теоретический диапазон |

Направление: **maximize** (к 1.0)
Идеальное значение: **1.0**

## Публичный API

```python
from hydrometrics import beta_component

result = beta_component(
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

**Импорт**: `from hydrometrics import beta_component`

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
from hydrometrics import beta_component

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = beta_component(obs, sim)
print(result)
# beta_component: 0.9923 (direction: maximize, bounds: (0.0, inf))

# β < 1 — небольшое систематическое занижение
```

## Связанные метрики

- [KGE Components (kge_components)](kge_components.md) — все три компоненты
- [r_component](r_component.md) — корреляция
- [alpha_component](alpha_component.md) — вариабельность
- [gamma_component](gamma_component.md) — коэффициент вариации (KGE 2009)
- [PBIAS (pbias)](pbias.md) — процентное смещение

## Научные ссылки

1. **Gupta, H. V., et al. (2009).** Decomposition of the mean squared error and NSE performance criteria. *Journal of Hydrology*, 377(1-2), 80-91.
2. **Kling, H., et al. (2012).** Runoff conditions in the upper Danube basin. *Journal of Hydrology*, 424-425, 264-277.