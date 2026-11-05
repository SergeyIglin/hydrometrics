# Групповой анализ

Продвинутые примеры группового анализа метрик.

## Анализ по водомерным станциям

```python
import pandas as pd
import numpy as np
from hydrometrics import nse, kge_2012, compute_grouped

np.random.seed(42)

# Данные для 50 станций за 5 лет
n_stations = 50
n_days = 1825

stations = [f"G{i:03d}" for i in range(n_stations)]
dates = pd.date_range("2015-01-01", periods=n_days, freq="D")

# Генерируем данные с разным качеством по станциям
data = []
for station in stations:
    quality = np.random.uniform(0.6, 0.98)  # Качество модели для станции
    obs = np.random.lognormal(2.0, 0.5, n_days)
    noise = np.random.lognormal(-0.05, 0.2, n_days)
    bias = np.random.normal(0, 0.1)
    sim = obs * noise * (1 + bias) + np.random.normal(0, 5, n_days)
    sim = np.maximum(sim, 0.1)
    
    for d, o, s in zip(dates, obs, sim):
        data.append({"station": station, "date": d, "obs": o, "sim": s})

df = pd.DataFrame(data)

# NSE по всем станциям
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by="station")
df_nse = result.to_pandas()
df_nse.columns = ["station", "NSE"]

print("Топ-5 станций:")
print(df_nse.nlargest(5, "NSE"))
print("\nФлоп-5 станций:")
print(df_nse.nsmallest(5, "NSE"))

print(f"\nСредний NSE: {df_nse['NSE'].mean():.3f}")
print(f"Медианный NSE: {df_nse['NSE'].median():.3f}")
print(f"Std NSE: {df_nse['NSE'].std():.3f}")

# Станции с NSE < 0.5 (плохие)
bad = df_nse[df_nse["NSE"] < 0.5]
print(f"\nСтанций с NSE < 0.5: {len(bad)} ({len(bad)/n_stations*100:.1f}%)")
```

## Сезонный анализ

```python
# Добавляем сезон
df["month"] = df["date"].dt.month
season_map = {12: "DJF", 1: "DJF", 2: "DJF",
              3: "MAM", 4: "MAM", 5: "MAM",
              6: "JJA", 7: "JJA", 8: "JJA",
              9: "SON", 10: "SON", 11: "SON"}
df["season"] = df["month"].map(season_map)

# NSE по сезонам
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by="season")
print("NSE по сезонам:")
print(result.to_pandas())

# NSE по станциям И сезонам
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by=["station", "season"])
df_seasonal = result.to_pandas()

# Сезонность качества
seasonal_mean = df_seasonal.groupby("season")["NSE"].mean()
print("\nСредний NSE по сезонам:")
print(seasonal_mean)
```

## Анализ по годам

```python
df["year"] = df["date"].dt.year

# Тренд качества по годам
result = compute_grouped(nse, df, obs="obs", sim="sim", group_by=["station", "year"])
df_yearly = result.to_pandas()

# Тренд для каждой станции
trends = {}
for station in stations:
    station_data = df_yearly[df_yearly["station"] == station]
    if len(station_data) >= 3:
        x = station_data["year"].values
        y = station_data["NSE"].values
        slope = np.polyfit(x, y, 1)[0]
        trends[station] = slope

# Станции с ухудшением качества
worsening = {s: m for s, m in trends.items() if m < -0.01}
print(f"Станций с ухудшением (>0.01/год): {len(worsening)}")
```

## Визуализация (Matplotlib)

```python
import matplotlib.pyplot as plt

# Гистограмма NSE
plt.figure(figsize=(10, 6))
plt.hist(df_nse["NSE"], bins=20, edgecolor="black", alpha=0.7)
plt.axvline(0.5, color="red", linestyle="--", label="NSE=0.5")
plt.axvline(0.75, color="green", linestyle="--", label="NSE=0.75")
plt.xlabel("NSE")
plt.ylabel("Количество станций")
plt.title("Распределение NSE по станциям")
plt.legend()
plt.grid(alpha=0.3)
plt.show()

# Сезонные боксплоты
df_seasonal.boxplot(column="NSE", by="season", figsize=(10, 6))
plt.title("NSE по сезонам")
plt.suptitle("")
plt.show()
```

## Экспорт сводного отчёта

```python
summary = {
    "n_stations": n_stations,
    "n_days": n_days,
    "overall_nse": float(nse(df["obs"], df["sim"])),
    "mean_nse": float(df_nse["NSE"].mean()),
    "median_nse": float(df_nse["NSE"].median()),
    "std_nse": float(df_nse["NSE"].std()),
    "n_bad_stations": int((df_nse["NSE"] < 0.5).sum()),
    "worst_station": df_nse.loc[df_nse["NSE"].idxmin(), "station"],
    "best_station": df_nse.loc[df_nse["NSE"].idxmax(), "station"],
    "seasonal_nse": df_seasonal.groupby("season")["NSE"].mean().to_dict(),
    "yearly_trends": trends
}

import json
with open("station_analysis_report.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("Отчёт сохранён в station_analysis_report.json")
```