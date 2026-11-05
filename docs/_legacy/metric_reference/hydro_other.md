# Другие гидрологические метрики

Дополнительные специализированные метрики для гидрологии.

## RSR — RMSE-observations Standard Deviation Ratio

```python
from hydrometrics import rsr
rsr(obs, sim, **kwargs)
```

- **Направление**: minimize
- **Границы**: [0, ∞)
- **Формула**: $\frac{RMSE}{\sigma_{obs}} = \frac{\sqrt{\sum(y_i - \hat{y}_i)^2/n}}{\sqrt{\sum(y_i - \bar{y})^2/(n-1)}}$
- **Связь**: $RSR = \sqrt{1 - NSE}$ (при неисправленном знаменателе)
- **Интерпретация (Moriasi et al. 2007)**:
  - 0.00–0.50: Очень хорошее
  - 0.50–0.60: Хорошее
  - 0.60–0.70: Удовлетворительное
  - > 0.70: Неудовлетворительное

## VE — Volumetric Efficiency

```python
from hydrometrics import ve
ve(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Формула**: $1 - \frac{\sum|y_i - \hat{y}_i|}{\sum y_i}$
- **Описание**: Аналог NSE с L1 нормой и без центрирования. Фокус на объёмном балансе.
- **Идеальное значение**: 1.0 (идеальный объёмный баланс)
- **Примечание**: Не чувствителен к фазовому сдвигу, только к объёму.

## Regime NSE (regNSE)

```python
from hydrometrics import regNSE
regNSE(obs, sim, dates, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Параметр `dates`**: Массив дат (обязательный!) — для построения кривой продолжительности
- **Описание**: NSE на кривой продолжительности потока (Flow Duration Curve).
- **Использование**: Оценка воспроизведения режима реки (распределение расходов).
- **Ссылка**: Pool et al. (2018) DOI: 10.5194/hess-22-1-2018

```python
import pandas as pd
dates = pd.date_range("2020-01-01", periods=365, freq="D")
regnse = regNSE(obs, sim, dates)
```

## Forecast Verification (FV)

```python
from hydrometrics import forecast_verification
forecast_verification(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Формула**: $1 - \frac{MSE_{model}}{MSE_{climatology}}$
- **Описание**: Навык прогноза относительно климатологии (историческое среднее).
- **Интерпретация**: > 0 = лучше климатологии, < 0 = хуже.

## Forecast Verification Delta (FVΔ)

```python
from hydrometrics import forecast_verification_delta
forecast_verification_delta(obs, sim, ref_date, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Параметр `ref_date`**: Дата отсчёта (обязательный!)
- **Описание**: Навык на приращениях (изменениях) относительно климатологии.
- **Использование**: Оценка прогноза изменений, а не абсолютных значений.

## Sigma Skill Score (σ-skill)

```python
from hydrometrics import ssigma
ssigma(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Описание**: Навык на основе стандартного отклонения ошибок.

## Sigma Skill Delta (σ-skill Δ)

```python
from hydrometrics import ssigma_delta
ssigma_delta(obs, sim, ref_date, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Параметр `ref_date`**: Дата отсчёта (обязательный!)
- **Описание**: σ-skill на приращениях.

## Сводная таблица

| Метрика | Направление | Границы | Ключевой параметр | Для чего |
|---------|-------------|---------|-------------------|----------|
| `rsr` | minimize | [0, ∞) | — | Безразмерная ошибка |
| `ve` | maximize | (-∞, 1.0] | — | Объёмный баланс |
| `regNSE` | maximize | (-∞, 1.0] | `dates` (req) | Режим реки (FDC) |
| `forecast_verification` | maximize | (-∞, 1.0] | — | Навык vs климатология |
| `forecast_verification_delta` | maximize | (-∞, 1.0] | `ref_date` (req) | Навык на изменениях |
| `ssigma` | maximize | (-∞, 1.0] | — | σ-навык |
| `ssigma_delta` | maximize | (-∞, 1.0] | `ref_date` (req) | σ-навык на изменениях |

## Пример комплексного использования

```python
from hydrometrics import (
    rsr, ve, regNSE, forecast_verification,
    forecast_verification_delta, ssigma, ssigma_delta
)
import pandas as pd
import numpy as np

np.random.seed(42)
obs = np.random.lognormal(2.0, 0.5, 365)
sim = obs * np.random.lognormal(-0.03, 0.15, 365) + np.random.normal(0, 3, 365)
sim = np.maximum(sim, 0.1)
dates = pd.date_range("2020-01-01", periods=365, freq="D")

print(f"RSR:                    {float(rsr(obs, sim)):.3f}")
print(f"VE:                     {float(ve(obs, sim)):.3f}")
print(f"RegNSE:                 {float(regNSE(obs, sim, dates)):.3f}")
print(f"Forecast Verification:  {float(forecast_verification(obs, sim)):.3f}")
print(f"FV Delta:               {float(forecast_verification_delta(obs, sim, dates[0])):.3f}")
print(f"Sigma Skill:            {float(ssigma(obs, sim)):.3f}")
print(f"Sigma Skill Delta:      {float(ssigma_delta(obs, sim, dates[0])):.3f}")
```