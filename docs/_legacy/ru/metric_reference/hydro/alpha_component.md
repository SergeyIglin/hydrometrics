# alpha_component (Variability Ratio α)

## Название и назначение

**alpha_component** — компонента вариабельности (α) из KGE 2012. Отношение стандартного отклонения смоделированных значений к стандартному отклонению наблюдаемых. Оценивает, насколько хорошо модель воспроизводит амплитуду колебаний.

## Математическая формула

$$\alpha = \frac{\sigma_{\hat{y}}}{\sigma_y} = \frac{\sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(\hat{y}_i - \bar{\hat{y}})^2}}{\sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(y_i - \bar{y})^2}}$$

**Реализация** (`_alpha_core`):
- Отношение выборочных стандартных отклонений (ddof=1)
- α > 1: модель более вариабельна, чем наблюдения
- α < 1: модель менее вариабельна

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Идеальное совпадение вариабельности |
| **> 1.0** | Переоценка вариабельности (переамплитуда) |
| **< 1.0** | Недооценка вариабельности (сглаживание) |
| **(0, ∞)** | Теоретический диапазон |

Направление: **maximize** (к 1.0)
Идеальное значение: **1.0**

## Публичный API

```python
from hydrometrics import alpha_component

result = alpha_component(
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

**Импорт**: `from hydrometrics import alpha_component`

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
from hydrometrics import alpha_component

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = alpha_component(obs, sim)
print(result)
# alpha_component: 0.9654 (direction: maximize, bounds: (0.0, inf))

# α < 1 — модель сглаживает пики
```

## Связанные метрики

- [KGE Components (kge_components)](kge_components.md) — все три компоненты
- [r_component](r_component.md) — корреляция
- [beta_component](beta_component.md) — смещение
- [gamma_component](gamma_component.md) — коэффициент вариации (KGE 2009)

## Научные ссылки

1. **Kling, H., Fuchs, M., & Paulin, M. (2012).** Runoff conditions in the upper Danube basin. *Journal of Hydrology*, 424-425, 264-277. DOI: 10.1016/j.jhydrol.2012.01.011