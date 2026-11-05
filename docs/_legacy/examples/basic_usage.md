# Базовое использование

Полный пример расчёта основных метрик для гидрологической модели.

```python
import numpy as np
import pandas as pd
from hydrometrics import (
    nse, kge_2012, kge_2009, mae, rmse, pbias,
    log_nse, nnse, rsr, ve
)

# Генерация синтетических данных
np.random.seed(42)
n = 365  # Год дневных данных

# Наблюдаемые расходы (логнормальное распределение)
obs = np.random.lognormal(mean=2.0, sigma=0.5, size=n)

# Смоделированные с добавлением шума и смещения
sim = obs * np.random.lognormal(mean=-0.05, sigma=0.15, size=n) + np.random.normal(0, 2, size=n)
sim = np.maximum(sim, 0.1)  # Нет отрицательных расходов

print(f"Данных: {n} точек")
print(f"Obs: mean={obs.mean():.2f}, std={obs.std():.2f}")
print(f"Sim: mean={sim.mean():.2f}, std={sim.std():.2f}")
print()

# === Основные регрессионные метрики ===
print("=== Регрессионные метрики ===")
print(f"MAE:   {mae(obs, sim)}")
print(f"RMSE:  {rmse(obs, sim)}")
print(f"PBIAS: {pbias(obs, sim)}")
print()

# === Гидрологические метрики ===
print("=== Гидрологические метрики ===")
print(f"NSE:         {nse(obs, sim)}")
print(f"Log NSE:     {log_nse(obs, sim)}")
print(f"NNSE:        {nnse(obs, sim)}")
print(f"RSR:         {rsr(obs, sim)}")
print(f"VE:          {ve(obs, sim)}")
print()

# === KGE ===
print("=== KGE ===")
kge2012 = kge_2012(obs, sim)
kge2009 = kge_2009(obs, sim)
print(f"KGE 2012: {kge2012}")
print(f"KGE 2009: {kge2009}")

# Компоненты KGE
from hydrometrics import kge_components
comp = kge_components(obs, sim, version="2012")
print(f"Компоненты: r={comp.value['r']:.3f}, α={comp.value['alpha']:.3f}, β={comp.value['beta']:.3f}, γ={comp.value['gamma']:.3f}")
print()

# === Интерпретация ===
print("=== Интерпретация ===")
for metric, name in [(nse(obs, sim), "NSE"), (kge2012, "KGE 2012")]:
    val = float(metric)
    if metric.direction == "maximize":
        quality = "Excellent" if val > 0.75 else "Good" if val > 0.65 else "Satisfactory" if val > 0.5 else "Poor"
    else:
        quality = "Excellent" if val < 0.1 else "Good" if val < 0.2 else "Satisfactory" if val < 0.5 else "Poor"
    print(f"{name}: {val:.3f} — {quality}")

# === Экспорт результатов ===
results = {
    "MAE": float(mae(obs, sim)),
    "RMSE": float(rmse(obs, sim)),
    "PBIAS": float(pbias(obs, sim)),
    "NSE": float(nse(obs, sim)),
    "LogNSE": float(log_nse(obs, sim)),
    "KGE_2012": float(kge_2012(obs, sim)),
    "KGE_2009": float(kge_2009(obs, sim)),
    "RSR": float(rsr(obs, sim)),
    "VE": float(ve(obs, sim)),
}

import json
with open("basic_metrics.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nРезультаты сохранены в basic_metrics.json")
```