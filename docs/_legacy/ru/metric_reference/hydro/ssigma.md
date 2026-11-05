# SSIGMA (Spectral Signature)

## Название и назначение

**SSIGMA (Spectral Signature / Spectral Similarity)** — метрика, основанная на спектральном анализе, оценивающая сходство спектров мощности наблюдаемых и смоделированных временных рядов. Позволяет оценить, насколько хорошо модель воспроизводит частотные характеристики процесса (сезонность, циклы, шум).

Полезна для оценки качества воспроизведения временной динамики, особенно сезонных и годовых циклов.

## Математическая формула

$$\text{SSIGMA} = 1 - \frac{\| \text{PSD}(y) - \text{PSD}(\hat{y}) \|_1}{\| \text{PSD}(y) \|_1 + \| \text{PSD}(\hat{y}) \|_1}$$

Где:
- $\text{PSD}(y)$ — спектр мощности (Power Spectral Density) наблюдений
- $\text{PSD}(\hat{y})$ — спектр мощности модели
- $\| \cdot \|_1$ — L1-норма (сумма абсолютных значений)

**Реализация** (`_ssigma_core`):
- Использует ВПФ (FFT) для вычисления спектров мощности
- Нормирует спектры перед сравнением
- L1-норма разности, нормированная на сумму норм

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Идентичные спектры мощности |
| **0.0** | Спектры не имеют сходства |
| **[0, 1]** | Диапазон (всегда неотрицательный) |

Направление: **maximize**
Идеальное значение: **1.0**

Оценивает сходство частотного состава, а не временную фазу.

## Публичный API

```python
from hydrometrics import ssigma

result = ssigma(
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

**Импорт**: `from hydrometrics import ssigma`

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
from hydrometrics import ssigma

# Генерация данных с сильной сезонностью
t = np.arange(365)
obs = 10 + 5 * np.sin(2 * np.pi * t / 365) + np.random.randn(365) * 0.5
sim = 10 + 5 * np.sin(2 * np.pi * t / 365 + 0.1) + np.random.randn(365) * 0.5

result = ssigma(obs, sim)
print(result)
# SSIGMA: 0.9523 (direction: maximize, bounds: (0.0, 1.0))
```

## Связанные метрики

- [SSIGMA Delta (ssigma_delta)](ssigma_delta.md) — разность SSIGMA между моделями
- [NSE (nse)](nse.md) — временная метрика (фаза + амплитуда)
- [KGE 2012 (kge_2012)](kge_2012.md) — декомпозиция на корреляцию, bias, вариабельность

## Научные ссылки

1. **Gudmundsson, L., et al. (2012).** Evaluating climate models with spectral methods. *Journal of Climate*, 25(17), 5819-5833. DOI: 10.1175/JCLI-D-11-00579.1

2. **Knoben, W. J. M., et al. (2019).** Hydrological model evaluation using spectral analysis. *Hydrology and Earth System Sciences*, 23(12), 4989-5009. DOI: 10.5194/hess-23-4989-2019