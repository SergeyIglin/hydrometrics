# Вероятностные прогнозы

Примеры работы с вероятностными/ансамблевыми прогнозами.

## CRPS для детерминированных прогнозов

Для детерминированных прогнозов CRPS = MAE:

```python
import numpy as np
from hydrometrics import crps, mae

obs = np.array([10, 12, 15, 14, 13])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5])

crps_det = crps(obs, sim)
mae_val = mae(obs, sim)

print(f"CRPS (deterministic): {crps_det}")
print(f"MAE:                   {mae_val}")
print(f"Equal: {abs(float(crps_det) - float(mae_val)) < 1e-10}")
```

## CRPS для ансамблевых прогнозов

```python
from hydrometrics import crps

np.random.seed(42)
n_samples = 100
n_ensemble = 51

# Наблюдения
obs = np.random.lognormal(2.0, 0.5, n_samples)

# Ансамбль: 51 член на каждую точку
# sim.shape = (n_samples, n_ensemble)
sim_ens = np.random.lognormal(
    mean=np.log(obs)[:, None] - 0.02,
    sigma=0.15,
    size=(n_samples, n_ensemble)
)

crps_ens = crps(obs, sim_ens)
print(f"Ensemble CRPS: {crps_ens}")

# Для сравнения: детерминированный (ensemble mean)
sim_det = sim_ens.mean(axis=1)
crps_det = crps(obs, sim_det)
print(f"Deterministic (mean) CRPS: {crps_det}")

# Ансамбль должен давать лучший (ниже) CRPS
print(f"Ensemble better: {float(crps_ens) < float(crps_det)}")
```

## Weighted CRPS (акцент на хвосты)

```python
from hydrometrics import weighted_crps

# Весовая функция: больше веса высоким значениям (паводки)
def flood_weight(y):
    # Экспоненциальный вес для высоких расходов
    return np.exp(y / 50.0)

wcrps = weighted_crps(obs, sim_ens, weight_func=flood_weight)
print(f"Weighted CRPS (flood emphasis): {wcrps}")

# Вес для низких расходов (сухость)
def drought_weight(y):
    return np.exp(-y / 10.0)

wcrps_drought = weighted_crps(obs, sim_ens, weight_func=drought_weight)
print(f"Weighted CRPS (drought emphasis): {wcrps_drought}")
```

## CRPS Skill Score (CRPSS)

```python
from hydrometrics import crpss

# Климатологический референс (историческое распределение)
climatology = np.random.lognormal(2.0, 0.5, (n_samples, 1000))

crpss_val = crpss(obs, sim_ens, ref_forecast=climatology)
print(f"CRPSS: {crpss_val}")
# > 0: лучше климатологии
# < 0: хуже климатологии
```

## Brier Score (бинарные события)

```python
from hydrometrics import brier_score, reliability, sharpness

# Событие: расход > 90-й перцентиль (паводок)
threshold = np.percentile(obs, 90)
obs_binary = (obs > threshold).astype(float)

# Вероятностный прогноз: доля ансамбля выше порога
prob_flood = (sim_ens > threshold).mean(axis=1)

bs = brier_score(obs_binary, prob_flood)
print(f"Brier Score: {bs}")

# Калибровка
rel = reliability(obs_binary, prob_flood, n_bins=10)
print(f"Reliability: {rel}")

# Резкость
sharp = sharpness(prob_flood)
print(f"Sharpness: {sharp}")
```

## Полный пример: прогноз паводков

```python
import numpy as np
from hydrometrics import crps, crpss, brier_score, reliability, sharpness, weighted_crps

np.random.seed(123)
n = 500

# Наблюдаемые расходы (м³/с)
obs = np.random.gamma(shape=2.0, scale=50.0, size=n)

# Ансамблевый прогноз (20 членов)
n_ens = 20
# Добавляем смещение и разброс
bias = 0.95  # Небольшое занижение
spread = 0.3
sim_ens = np.random.gamma(
    shape=(obs * bias)[:, None] / (spread**2),
    scale=spread**2,
    size=(n, n_ens)
)

# 1. Общий CRPS
crps_val = crps(obs, sim_ens)
print(f"CRPS: {crps_val:.3f}")

# 2. CRPSS vs климатология
clim_ens = np.random.gamma(shape=2.0, scale=50.0, size=(n, 100))
crpss_val = crpss(obs, sim_ens, ref_forecast=clim_ens)
print(f"CRPSS: {crpss_val:.3f}")

# 3. Фокус на паводки (> 95 перцентиль)
p95 = np.percentile(obs, 95)
obs_flood = (obs > p95).astype(float)
prob_flood = (sim_ens > p95).mean(axis=1)

bs = brier_score(obs_flood, prob_flood)
rel = reliability(obs_flood, prob_flood)
sharp = sharpness(prob_flood)

print(f"\nFlood (>P95) Brier Score: {bs:.4f}")
print(f"Reliability: {rel:.4f}")
print(f"Sharpness: {sharp:.4f}")

# 4. Weighted CRPS для паводков
def flood_weight(y):
    return np.where(y > p95, 10.0, 1.0)

wcrps = weighted_crps(obs, sim_ens, weight_func=flood_weight)
print(f"\nFlood-weighted CRPS: {wcrps:.3f}")
```