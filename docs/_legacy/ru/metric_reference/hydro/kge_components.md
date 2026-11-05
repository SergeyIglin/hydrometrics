# KGE Components (r, α, β, γ)

## Название и назначение

**KGE Components** — функция, возвращающая компоненты KGE отдельно: корреляцию (r), вариабельность (α), смещение (β) и опционально отношение коэффициентов вариации (γ). Позволяет детально диагностировать ошибки модели без агрегации в единое число.

Полезно для глубокой диагностики: понимание, какую именно компоненту нужно улучшить.

## Математическая формула

Возвращает компоненты в зависимости от версии:

**Версия 2012 (по умолчанию):**
- **r** (correlation): $	ext{corr}(y, \hat{y})$ — корреляция Пирсона
- **α** (alpha): $rac{\sigma_{\hat{y}}}{\sigma_y}$ — отношение стандартных отклонений
- **β** (beta): $rac{ar{\hat{y}}}{ar{y}}$ — отношение средних
- **γ** (gamma): $rac{	ext{CV}_{\hat{y}}}{	ext{CV}_y} = rac{\sigma_{\hat{y}} / ar{\hat{y}}}{\sigma_y / ar{y}}$ — отношение коэффициентов вариации

**Версия 2009:**
- **r** (correlation): $	ext{corr}(y, \hat{y})$ — корреляция Пирсона
- **α** (alpha): $rac{\sigma_{\hat{y}}}{\sigma_y}$ — отношение стандартных отклонений
- **β** (beta): $rac{ar{\hat{y}}}{ar{y}}$ — отношение средних
- (нет γ компоненты)

**Реализация** (`_kge_components_core`):
- Вычисляет все компоненты за один проход
- Возвращает `MetricResult` с `value` как словарь компонент
- Поддерживает `axis`, `reduction` и параметр `version`

## Интерпретация компонентов

| Компонент | Идеальное значение | Интерпретация отклонения |
|-----------|-------------------|-------------------------|
| **r** | 1.0 | < 1: плохая фазовая синхронизация |
| **α** | 1.0 | > 1: переоценка вариабельности; < 1: недооценка |
| **β** | 1.0 | > 1: систематическое завышение; < 1: систематическое занижение |
| **γ** (только 2012) | 1.0 | > 1: переоценка CV ratio; < 1: недооценка |

Направление для всех: **maximize** (к 1.0)

## Публичный API

```python
from hydrometrics import kge_components

result = kge_components(
    obs: array-like,
    sim: array-like,
    *,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    version: Literal["2009", "2012"] = "2012",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Импорт**: `from hydrometrics import kge_components`

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `obs` | array-like | обязательный | Наблюдаемые значения |
| `sim` | array-like | обязательный | Смоделированные значения |
| `weight` | array-like | `None` | Веса выборки |
| `axis` | int | `None` | Ось для вычислений |
| `reduction` | str | `"mean"` | Редукция для массивов |
| `version` | str | `"2012"` | `"2009"` или `"2012"` |
| `nan_policy` | str | `"omit"` | Политика NaN |
| `sentinel` | float/list | `None` | Значения-пропуски |

**Возвращает**: `MetricResult` с `value` как словарь: `{"r": float, "alpha": float, "beta": float, "gamma": float}` (gamma только для version="2012")

## Python пример

```python
import numpy as np
from hydrometrics import kge_components

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

# Версия 2012 (по умолчанию, 4 компоненты)
result = kge_components(obs, sim)
print(f"r (correlation): {result.value['r']:.4f}")
print(f"α (variability): {result.value['alpha']:.4f}")
print(f"β (bias): {result.value['beta']:.4f}")
print(f"γ (CV ratio): {result.value['gamma']:.4f}")

# KGE 2012 можно восстановить:
kge_2012 = 1 - np.sqrt((result.value['r']-1)**2 + (result.value['alpha']-1)**2 + (result.value['beta']-1)**2 + (result.value['gamma']-1)**2)
print(f"KGE 2012: {kge_2012:.4f}")

# Версия 2009 (3 компоненты)
result_2009 = kge_components(obs, sim, version="2009")
print(f"Version 2009 components: {result_2009.value}")
```

**Ожидаемый вывод:**
```
r (correlation): 0.9940
α (variability): 1.0563
β (bias): 0.9806
γ (CV ratio): 1.0773
KGE 2012: 0.9022
Version 2009 components: {'r': 0.9940, 'alpha': 1.0563, 'beta': 0.9806}
```

## Диагностика модели по компонентам

| Проблема | r | α | β | γ | Действие |
|----------|---|---|---|---|----------|
| Фазовый сдвиг | ↓ | ~1 | ~1 | ~1 | Улучшить маршрутизацию/фазу |
| Неверная амплитуда | ~1 | ≠1 | ~1 | ~1 | Калибровать параметры образования стока |
| Систематический bias | ~1 | ~1 | ≠1 | ~1 | Скорректировать входные данные/параметры |
| Неверная форма распределения | ~1 | ~1 | ~1 | ≠1 | Проверить параметры распределения |

## Связанные метрики

- [KGE 2012 (kge_2012)](kge_2012.md) — агрегированная метрика
- [KGE 2009 (kge_2009)](kge_2009.md) — версия с 3 компонентами
- [Отдельные компоненты](r_component.md) — r_component, alpha_component, beta_component, gamma_component

## Научные ссылки

1. **Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009).** Decomposition of the mean squared error and NSE performance criteria. *Journal of Hydrology*, 377(1-2), 80-91. DOI: 10.1016/j.jhydrol.2009.08.003

2. **Kling, H., Fuchs, M., & Paulin, M. (2012).** Runoff conditions in the upper Danube basin. *Journal of Hydrology*, 424-425, 264-277. DOI: 10.1016/j.jhydrol.2012.01.011
