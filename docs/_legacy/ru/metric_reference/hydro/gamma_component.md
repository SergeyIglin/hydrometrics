# gamma_component (Coefficient of Variation Ratio γ)

## Название и назначение

**gamma_component** — компонента γ из KGE 2009. Отношение коэффициентов вариации смоделированных и наблюдаемых значений. Использовалась в оригинальной версии KGE 2009 вместо α (variability ratio).

$$\gamma = \frac{CV_{\hat{y}}}{CV_y} = \frac{\sigma_{\hat{y}} / \bar{\hat{y}}}{\sigma_y / \bar{y}} = \alpha / \beta$$

Оценивает вариабельность относительно среднего (коэффициент вариации).

## Математическая формула

$$\gamma = \frac{\frac{\sigma_{\hat{y}}}{\bar{\hat{y}}}}{\frac{\sigma_y}{\bar{y}}} = \frac{\sigma_{\hat{y}} \bar{y}}{\sigma_y \bar{\hat{y}}} = \frac{\alpha}{\beta}$$

**Реализация** (`_gamma_core`):
- Отношение коэффициентов вариации
- γ = α / β (прямая связь с компонентами KGE 2012)

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Совпадение коэффициентов вариации |
| **> 1.0** | Модель более вариабельна относительно своего среднего |
| **< 1.0** | Модель менее вариабельна относительно своего среднего |
| **(0, ∞)** | Теоретический диапазон |

Направление: **maximize** (к 1.0)
Идеальное значение: **1.0**

## Публичный API

```python
from hydrometrics import gamma_component

result = gamma_component(
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

**Импорт**: `from hydrometrics import gamma_component`

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
from hydrometrics import gamma_component, alpha_component, beta_component

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

gamma = gamma_component(obs, sim)
alpha = alpha_component(obs, sim)
beta = beta_component(obs, sim)

print(f"γ: {gamma.value:.4f}")
print(f"α: {alpha.value:.4f}")
print(f"β: {beta.value:.4f}")
print(f"α/β: {alpha.value/beta.value:.4f}")
# γ ≈ α/β
```

## Связанные метрики

- [KGE 2009 (kge_2009)](kge_2009.md) — использует γ вместо α
- [KGE 2012 (kge_2012)](kge_2012.md) — использует α и β раздельно
- [KGE Components (kge_components)](kge_components.md) — α, β (γ не включён)
- [alpha_component](alpha_component.md) — α
- [beta_component](beta_component.md) — β

## Научные ссылки

1. **Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009).** Decomposition of the mean squared error and NSE performance criteria. *Journal of Hydrology*, 377(1-2), 80-91. DOI: 10.1016/j.jhydrol.2009.08.003

2. **Kling, H., Fuchs, M., & Paulin, M. (2012).** Runoff conditions in the upper Danube basin. *Journal of Hydrology*, 424-425, 264-277. DOI: 10.1016/j.jhydrol.2012.01.011