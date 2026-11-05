# Forecast Verification (CRPS-based)

## Название и назначение

**Forecast Verification** — метрика верификации прогнозов на основе CRPS (Continuous Ranked Probability Score) для детерминистических прогнозов. Оценивает качество вероятностного прогноза, представленного ансамблем или распределением.

Используется для оценки качества гидрологических прогнозов (сток, уровень воды) в вероятностном виде.

## Математическая формула

Для детерминистического прогноза (один прогноз на момент времени):

$$\text{FV} = 1 - \frac{\text{CRPS}(\hat{y}, y)}{\text{CRPS}_{\text{ref}}}$$

Где:
- $\text{CRPS}(\hat{y}, y)$ — CRPS между прогнозом и наблюдением
- $\text{CRPS}_{\text{ref}}$ — CRPS референсного прогноза (климатология/среднее)

Для ансамблевого прогноза с $M$ членами:

$$\text{CRPS} = \frac{1}{M} \sum_{m=1}^{M} |y_m - y| - \frac{1}{2M^2} \sum_{m=1}^{M} \sum_{k=1}^{M} |y_m - y_k|$$

**Реализация** (`_forecast_verification_core`):
- Поддерживает детерминистические и ансамблевые прогнозы
- Референс: климатологическое среднее
- Возвращает skill score (1 = идеально, 0 = как референс, < 0 = хуже референса)

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Идеальный прогноз |
| **0.0** | Не лучше климатологии |
| **< 0.0** | Хуже климатологии |
| **(-∞, 1.0]** | Теоретический диапазон |

Направление: **maximize**
Идеальное значение: **1.0**

## Публичный API

```python
from hydrometrics import forecast_verification

result = forecast_verification(
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

**Импорт**: `from hydrometrics import forecast_verification`

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `obs` | array-like | обязательный | Наблюдаемые значения |
| `sim` | array-like | обязательный | Прогнозы (1D) или ансамбль (2D: time × members) |
| `weight` | array-like | `None` | Веса выборки |
| `axis` | int | `None` | Ось для вычислений |
| `reduction` | str | `"mean"` | Редукция для массивов |
| `nan_policy` | str | `"omit"` | Политика NaN |
| `sentinel` | float/list | `None` | Значения-пропуски |

## Python пример

```python
import numpy as np
from hydrometrics import forecast_verification

# Детерминистический прогноз
obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = forecast_verification(obs, sim)
print(result)
# Forecast Verification: 0.7234 (direction: maximize, bounds: (-inf, 1.0))

# Ансамблевый прогноз (10 time steps × 50 members)
sim_ensemble = np.random.normal(sim[:, None], 2, size=(10, 50))
result_ens = forecast_verification(obs, sim_ensemble)
print(result_ens)
```

## Связанные метрики

- [Forecast Verification Delta (forecast_verification_delta)](forecast_verification_delta.md) — разность skill scores
- [CRPS (crps)](../probabilistic/crps.md) — базовая метрика CRPS
- [KGE 2012 (kge_2012)](kge_2012.md) — для детерминистической оценки

## Научные ссылки

1. **Hersbach, H. (2000).** Decomposition of the Continuous Ranked Probability Score for ensemble prediction systems. *Weather and Forecasting*, 15(5), 559-570. DOI: 10.1175/1520-0434(2000)015<0559:DOTCRP>2.0.CO;2

2. **Gneiting, T., & Raftery, A. E. (2007).** Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359-378. DOI: 10.1198/016214506000001437