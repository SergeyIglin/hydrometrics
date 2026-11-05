# Forecast Verification Delta

## Название и назначение

**Forecast Verification Delta** — разность skill scores между двумя прогнозами. Позволяет сравнить качество двух прогнозов (например, новой модели vs базовой) на одной шкале.

Полезен для A/B тестирования моделей: насколько новый прогноз лучше/хуже старого.

## Математическая формула

$$\text{FV}_{\Delta} = \text{FV}(\text{sim}_1) - \text{FV}(\text{sim}_2)$$

Где:
- $\text{FV}(\text{sim}_1)$ — Forecast Verification для прогноза 1
- $\text{FV}(\text{sim}_2)$ — Forecast Verification для прогноза 2 (референс)

**Реализация** (`_forecast_verification_delta_core`):
- Вычисляет FV для обоих прогнозов
- Возвращает разность
- Положительное значение = прогноз 1 лучше прогноза 2

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **> 0** | Прогноз 1 лучше прогноза 2 |
| **0** | Прогнозы равнозначны |
| **< 0** | Прогноз 2 лучше прогноза 1 |
| **(-1, 1)** | Типичный диапазон |

Направление: **maximize** (чем больше, тем прогноз 1 лучше)

## Публичный API

```python
from hydrometrics import forecast_verification_delta

result = forecast_verification_delta(
    obs: array-like,
    sim1: array-like,
    sim2: array-like,
    *,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Импорт**: `from hydrometrics import forecast_verification_delta`

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `obs` | array-like | обязательный | Наблюдаемые значения |
| `sim1` | array-like | обязательный | Прогноз 1 (тестируемый) |
| `sim2` | array-like | обязательный | Прогноз 2 (референс/базовый) |
| `weight` | array-like | `None` | Веса выборки |
| `axis` | int | `None` | Ось для вычислений |
| `reduction` | str | `"mean"` | Редукция для массивов |
| `nan_policy` | str | `"omit"` | Политика NaN |
| `sentinel` | float/list | `None` | Значения-пропуски |

## Python пример

```python
import numpy as np
from hydrometrics import forecast_verification_delta

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim_new = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])
sim_old = np.array([8.0, 10.0, 13.0, 12.0, 12.0, 9.0, 7.0, 6.0, 5.0, 7.0])

result = forecast_verification_delta(obs, sim_new, sim_old)
print(result)
# Forecast Verification Delta: 0.1523 (direction: maximize, bounds: (-1.0, 1.0))

# Положительное значение = новая модель лучше старой
```

## Связанные метрики

- [Forecast Verification (forecast_verification)](forecast_verification.md) — базовая метрика
- [CRPS (crps)](../probabilistic/crps.md) — базовая вероятностная метрика
- [KGE 2012 (kge_2012)](kge_2012.md) — для детерминистического сравнения

## Научные ссылки

1. **Hersbach, H. (2000).** Decomposition of the Continuous Ranked Probability Score for ensemble prediction systems. *Weather and Forecasting*, 15(5), 559-570. DOI: 10.1175/1520-0434(2000)015<0559:DOTCRP>2.0.CO;2

2. **Gneiting, T., & Raftery, A. E. (2007).** Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359-378. DOI: 10.1198/016214506000001437