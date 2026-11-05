# r_component (Correlation Component)

## Название и назначение

**r_component** — компонента корреляции Пирсона из KGE. Оценивает линейную связь между наблюдаемыми и смоделированными значениями, игнорируя масштаб и смещение.

Показывает, насколько хорошо модель воспроиздует фазовую динамику (форму гидрографа).

## Математическая формула

$$r = \frac{\sum_{i=1}^{n} (y_i - \bar{y})(\hat{y}_i - \bar{\hat{y}})}{\sqrt{\sum_{i=1}^{n} (y_i - \bar{y})^2 \sum_{i=1}^{n} (\hat{y}_i - \bar{\hat{y}})^2}}$$

**Реализация** (`_r_core`):
- Стандартная корреляция Пирсона
- Чувствительна только к форме, не к масштабу/смещению

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Идеальная линейная связь |
| **0.0** | Нет линейной связи |
| **-1.0** | Идеальная отрицательная связь |
| **[0, 1]** | Для гидрологии (отрицательные редки) |

Направление: **maximize**
Идеальное значение: **1.0**

## Публичный API

```python
from hydrometrics import r_component

result = r_component(
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

**Импорт**: `from hydrometrics import r_component`

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
from hydrometrics import r_component

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = r_component(obs, sim)
print(result)
# r_component: 0.9876 (direction: maximize, bounds: (-1.0, 1.0))
```

## Связанные метрики

- [KGE Components (kge_components)](kge_components.md) — все три компоненты сразу
- [alpha_component](alpha_component.md) — вариабельность
- [beta_component](beta_component.md) — смещение
- [gamma_component](gamma_component.md) — коэффициент вариации (KGE 2009)

## Научные ссылки

1. **Gupta, H. V., et al. (2009).** Decomposition of the mean squared error and NSE performance criteria. *Journal of Hydrology*, 377(1-2), 80-91.
2. **Kling, H., et al. (2012).** Runoff conditions in the upper Danube basin. *Journal of Hydrology*, 424-425, 264-277.