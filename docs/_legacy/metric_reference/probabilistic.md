# Вероятностные метрики

Метрики для оценки вероятностных/ансамблевых прогнозов.

## CRPS — Continuous Ranked Probability Score

```python
from hydrometrics import crps
crps(obs, sim, **kwargs)
```

- **Направление**: minimize
- **Границы**: [0, ∞)
- **Вход**:
  - Детерминированный: `sim.shape = (n,)` → CRPS = MAE
  - Ансамбль: `sim.shape = (n, n_ensemble)` → полноценный CRPS
- **Формула (ансамбль)**: $CRPS = \frac{1}{n}\sum_{i=1}^n \frac{1}{m}\sum_{j=1}^m |\hat{y}_{ij} - y_i| - \frac{1}{2m^2}\sum_{j=1}^m\sum_{k=1}^m |\hat{y}_{ij} - \hat{y}_{ik}|$
- **Свойства**: Строго собственный скор. Обобщает MAE на распределения.
- **Ссылка**: Gneiting & Raftery (2007) DOI: 10.1198/016214506000001437

### Детерминированный vs Ансамбль

```python
import numpy as np
from hydrometrics import crps, mae

obs = np.array([10, 12, 15])
sim_det = np.array([9.5, 11.8, 14.5])
sim_ens = np.array([[9, 10, 11], [11, 12, 13], [14, 15, 16]])

print(f"CRPS (det): {float(crps(obs, sim_det)):.3f}")  # = MAE
print(f"MAE:        {float(mae(obs, sim_det)):.3f}")
print(f"CRPS (ens): {float(crps(obs, sim_ens)):.3f}")  # ≤ MAE
```

## Weighted CRPS

```python
from hydrometrics import weighted_crps
weighted_crps(obs, sim, weight_func=None, **kwargs)
```

- **Направление**: minimize
- **Границы**: [0, ∞)
- **Параметр `weight_func`**: Функция $w(y) \ge 0$, акцентирующая области распределения
- **Формула**: $\int w(y) (F(y) - 1_{y \ge y_{obs}})^2 dy$

```python
# Акцент на паводки (высокие значения)
def flood_weight(y):
    return np.exp(y / 50.0)

wcrps = weighted_crps(obs, sim_ens, weight_func=flood_weight)

# Акцент на сухость (низкие значения)
def drought_weight(y):
    return np.exp(-y / 10.0)
```

## CRPS Skill Score (CRPSS)

```python
from hydrometrics import crpss
crpss(obs, sim, ref_forecast=None, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Параметр `ref_forecast`**: Референсный ансамбль (default: климатология из obs)
- **Формула**: $1 - \frac{CRPS_{model}}{CRPS_{ref}}$
- **Интерпретация**: > 0 лучше референса, < 0 хуже.

```python
# Климатологический референс
clim_ens = np.random.choice(obs, size=(len(obs), 100), replace=True)
crpss_val = crpss(obs, sim_ens, ref_forecast=clim_ens)
```

## Brier Score

```python
from hydrometrics import brier_score
brier_score(obs, sim, **kwargs)
```

- **Направление**: minimize
- **Границы**: [0, 1]
- **Вход**: `obs` — бинарный (0/1), `sim` — вероятность [0,1]
- **Формула**: $\frac{1}{n}\sum(p_i - o_i)^2$
- **Разложение**: $BS = \text{Reliability} - \text{Resolution} + \text{Uncertainty}$

```python
obs_binary = (obs > threshold).astype(float)
prob = (sim_ens > threshold).mean(axis=1)  # Вероятность события
bs = brier_score(obs_binary, prob)
```

## Reliability (Калибровка)

```python
from hydrometrics import reliability
reliability(obs, sim, n_bins=10, **kwargs)
```

- **Направление**: minimize
- **Границы**: [0, ∞)
- **Параметр `n_bins`**: Количество бинов для группировки вероятностей
- **Описание**: Компонента надежности разложения Brier Score. 0 = идеальная калибровка.

## Sharpness (Резкость)

```python
from hydrometrics import sharpness
sharpness(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: [0, ∞)
- **Описание**: Дисперсия прогнозируемых вероятностей. Выше = более уверенные прогнозы.
- **Формула**: $\frac{1}{n}\sum p_i(1-p_i)$ для бинарного случая.

## Сводная таблица

| Метрика | Вход | Направление | Границы | Для чего |
|---------|------|-------------|---------|----------|
| `crps` | det / ens | minimize | [0, ∞) | Общая точность распределения |
| `weighted_crps` | ens | minimize | [0, ∞) | Акцент на хвосты |
| `crpss` | ens | maximize | (-∞, 1.0] | Навык vs референс |
| `brier_score` | prob | minimize | [0, 1] | Бинарные события |
| `reliability` | prob | minimize | [0, ∞) | Калибровка |
| `sharpness` | prob | maximize | [0, ∞) | Уверенность прогноза |

## Полный пример

```python
import numpy as np
from hydrometrics import crps, weighted_crps, crpss, brier_score, reliability, sharpness

np.random.seed(123)
n = 500
n_ens = 20

# Наблюдения
obs = np.random.gamma(2.0, 50.0, n)

# Ансамбль с небольшим смещением
sim_ens = np.random.gamma(
    shape=(obs * 0.98)[:, None] / 0.3**2,
    scale=0.3**2,
    size=(n, n_ens)
)

# 1. CRPS
print(f"CRPS: {float(crps(obs, sim_ens)):.3f}")

# 2. Weighted CRPS (паводки)
p95 = np.percentile(obs, 95)
def flood_weight(y):
    return np.where(y > p95, 10.0, 1.0)
print(f"Weighted CRPS: {float(weighted_crps(obs, sim_ens, flood_weight)):.3f}")

# 3. CRPSS
clim = np.random.gamma(2.0, 50.0, (n, 100))
print(f"CRPSS: {float(crpss(obs, sim_ens, clim)):.3f}")

# 4. Brier Score для паводка
obs_flood = (obs > p95).astype(float)
prob_flood = (sim_ens > p95).mean(axis=1)
print(f"Brier Score: {float(brier_score(obs_flood, prob_flood)):.4f}")
print(f"Reliability: {float(reliability(obs_flood, prob_flood)):.4f}")
print(f"Sharpness:   {float(sharpness(prob_flood)):.4f}")
```