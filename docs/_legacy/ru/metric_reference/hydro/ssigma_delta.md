# SSIGMA Delta

## Название и назначение

**SSIGMA Delta** — разность значений SSIGMA между двумя моделями. Позволяет сравнить, какая из двух моделей лучше воспроизводит спектральные характеристики процесса.

Полезен для сравнения моделей с точки зрения воспроизведения частотного состава (сезонность, циклы).

## Математическая формула

$$\text{SSIGMA}_{\Delta} = \text{SSIGMA}(\text{sim}_1) - \text{SSIGMA}(\text{sim}_2)$$

Где:
- $\text{SSIGMA}(\text{sim}_1)$ — SSIGMA для модели 1
- $\text{SSIGMA}(\text{sim}_2)$ — SSIGMA для модели 2 (референс)

**Реализация** (`_ssigma_delta_core`):
- Вычисляет SSIGMA для обеих моделей
- Возвращает разность
- Положительное значение = модель 1 лучше воспроизводит спектр

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **> 0** | Модель 1 лучше воспроизводит спектр |
| **0** | Модели равнозначны по спектру |
| **< 0** | Модель 2 лучше воспроизводит спектр |
| **(-1, 1)** | Типичный диапазон |

Направление: **maximize** (чем больше, тем модель 1 лучше)

## Публичный API

```python
from hydrometrics import ssigma_delta

result = ssigma_delta(
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

**Импорт**: `from hydrometrics import ssigma_delta`

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `obs` | array-like | обязательный | Наблюдаемые значения |
| `sim1` | array-like | обязательный | Модель 1 (тестируемая) |
| `sim2` | array-like | обязательный | Модель 2 (референс/базовая) |
| `weight` | array-like | `None` | Веса выборки |
| `axis` | int | `None` | Ось для вычислений |
| `reduction` | str | `"mean"` | Редукция для массивов |
| `nan_policy` | str | `"omit"` | Политика NaN |
| `sentinel` | float/list | `None` | Значения-пропуски |

## Python пример

```python
import numpy as np
from hydrometrics import ssigma_delta

t = np.arange(365)
obs = 10 + 5 * np.sin(2 * np.pi * t / 365) + np.random.randn(365) * 0.5
sim_new = 10 + 5 * np.sin(2 * np.pi * t / 365 + 0.05) + np.random.randn(365) * 0.5
sim_old = 10 + 3 * np.sin(2 * np.pi * t / 365 + 0.5) + np.random.randn(365) * 1.0

result = ssigma_delta(obs, sim_new, sim_old)
print(result)
# SSIGMA Delta: 0.2345 (direction: maximize, bounds: (-1.0, 1.0))

# Положительное = новая модель лучше по спектру
```

## Связанные метрики

- [SSIGMA (ssigma)](ssigma.md) — базовая спектральная метрика
- [Forecast Verification Delta (forecast_verification_delta)](forecast_verification_delta.md) — аналогичная идея для CRPS
- [KGE 2012 (kge_2012)](kge_2012.md) — для детерминистического сравнения

## Научные ссылки

1. **Gudmundsson, L., et al. (2012).** Evaluating climate models with spectral methods. *Journal of Climate*, 25(17), 5819-5833. DOI: 10.1175/JCLI-D-11-00579.1

2. **Knoben, W. J. M., et al. (2019).** Hydrological model evaluation using spectral analysis. *Hydrology and Earth System Sciences*, 23(12), 4989-5009. DOI: 10.5194/hess-23-4989-2019