# regNSE (Regime NSE)

## Название и назначение

**regNSE (Regime Nash-Sutcliffe Efficiency)** — метрика эффективности Наша-Сатклиффа на основе режима расхода, оценивающая, насколько хорошо смоделированные годовые кривые длительности воспроизводят наблюдаемые режимы расхода.

В отличие от классического NSE, который сравнивает значения в одно и то же время, regNSE сравнивает *ранжированные* значения расхода. Для каждого календарного года наблюдаемые и смоделированные значения сортируются независимо по убыванию, затем вычисляется средняя режимирующая кривая (Q_reg) как среднее наблюдаемое значение для каждого ранга по всем годам. regNSE затем вычисляется как NSE между ранжированными значениями obs и sim относительно этой режимирующей кривой.

Ссылка: Gartsman (2023), DOI: 10.34753/HS.2023.5.3.228.

## Математическая формула

Для каждого календарного года:

1. Наблюдаемые значения $y$ сортируются по убыванию независимо от смоделированных значений $\hat{y}$.
2. Каждый год приводится к 365 ранговым позициям (для високосных годов два наименьших значения усредняются).
3. Режимирующая кривая $Q_{\text{reg}}$ вычисляется как среднее наблюдаемое значение для каждого ранга по всем годам (или задаётся внешне через параметр `regime`).
4. regNSE вычисляется как:

$$\text{regNSE} = 1 - \frac{\sum (\hat{y}_{\text{ранг}} - y_{\text{ранг}})^2}{\sum (y_{\text{ранг}} - Q_{\text{reg}})^2}$$

Суммы берутся по всем годам и всем 365 ранговым позициям.

**Реализация** (`hydrometrics/backends/numpy.py`, функция `_reg_nse_core`):
- Требует параметр `dates` (массив datetime64[D]) для группировки по годам
- Опциональный параметр `regime` — предварительно вычисленная режимирующая кривая формы (365,)
- Не поддерживает `weight`, `axis`, `reduction` (вызывают NotImplementedError)
- Работает только с 1D массивами

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Идеальное совпадение ранжированных кривых |
| **0.0** | Модель не лучше режимирующей кривой |
| **< 0.0** | Модель хуже режимирующей кривой |
| **(-∞, 1.0]** | Теоретический диапазон |

Направление оптимизации: **maximize**
Идеальное значение: **1.0**

regNSE оценивает соответствие *формы* распределения расходов (кривой длительности), игнорируя тайминг отдельных событий.

## Публичный API

```python
from hydrometrics import regNSE

result = regNSE(
    obs: array-like,
    sim: array-like,
    dates: array-like,
    *,
    regime: array-like | None = None,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Импорт**: `from hydrometrics import regNSE`

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `obs` | array-like | обязательный | Наблюдаемые значения (1D) |
| `sim` | array-like | обязательный | Смоделированные значения (1D, такая же форма как obs) |
| `dates` | array-like | обязательный | Даты наблюдений (datetime64[D], 1D) |
| `regime` | array-like | `None` | Предвычисленная режимирующая кривая формы (365,) |
| `weight` | array-like | `None` | **Не поддерживается** (вызовет NotImplementedError) |
| `axis` | int | `None` | **Не поддерживается** (вызовет NotImplementedError) |
| `reduction` | str | `"mean"` | **Не используется** |
| `nan_policy` | str | `"omit"` | Политика обработки NaN |
| `sentinel` | float/list | `None` | Значения-пропуски для конвертации в NaN |

## Python пример

```python
import numpy as np
from hydrometrics import regNSE

# Создаём временной ряд: 3 года ежедневных данных
np.random.seed(42)  # Для воспроизводимости
n_days = 3 * 365
dates = np.datetime64('2000-01-01') + np.arange(n_days).astype('timedelta64[D]')
obs = np.abs(np.random.randn(n_days) * 10 + 50)  # Наблюдаемые расходы
sim = obs + np.random.randn(n_days) * 3           # Смоделированные расходы

# Вычисление regNSE (dates должен передаваться как именованный аргумент)
result = regNSE(obs, sim, dates=dates)
print(result)
# Regime Nash-Sutcliffe Efficiency (regNSE): 0.9637 (direction: maximize, bounds: (-inf, 1.0))

# Доступ к атрибутам
print(f"Значение: {float(result):.4f}")
print(f"Ссылка: {result.reference}")
```

**Ожидаемый вывод** (значения будут отличаться из-за случайности):
```
Regime Nash-Sutcliffe Efficiency (regNSE): 0.9637 (direction: maximize, bounds: (-inf, 1.0))
Значение: 0.9637
Ссылка: Gartsman, B. I. (2023). Assessing the quality of modeling and forecasting in hydrology – reasoning about the method. Hydrosphere. Hazard Processes and Phenomena, 5(3), 228–243. DOI: 10.34753/HS.2023.5.3.228.
```

## Граничные случаи (Edge Cases)

| Сценарий | Поведение |
|----------|-----------|
| Менее 1 полного года данных | Возвращает `NaN` |
| Все наблюдаемые значения константны в пределах года | Возвращает `NaN` (деление на ноль в знаменателе) |
| `weight`, `axis`, `reduction` переданы | Вызывает `NotImplementedError` |
| Входные массивы не 1D | Вызывает `ValueError` |
| Форма `obs`, `sim`, `dates` не совпадает | Вызывает `ValueError` |
| `regime` задана, но форма не (365,) | Вызывает `ValueError` |
| Наличие NaN (nan_policy="omit") | Парное удаление NaN перед вычислением |
| Наличие NaN (nan_policy="propagate") | Возвращает `NaN` |
| Наличие NaN (nan_policy="raise") | Вызывает `ValueError` |

## Связанные метрики

- [NSE (nse)](nse.md) — классический NSE (сравнивает значения по времени)
- [Forecast Verification (forecast_verification)](forecast_verification.md) — умение относительно климатологии
- [Sigma Skill (ssigma)](ssigma.md) — комбинация RMSE и штрафа за смещение

## Научные ссылки

1. **Gartsman, B. I. (2023).** Assessing the quality of modeling and forecasting in hydrology – reasoning about the method. *Hydrosphere. Hazard Processes and Phenomena*, 5(3), 228–243. DOI: [10.34753/HS.2023.5.3.228](https://doi.org/10.34753/HS.2023.5.3.228)

2. **Nash, J. E., & Sutcliffe, J. V. (1970).** River flow forecasting through conceptual models part I — A discussion of principles. *Journal of Hydrology*, 10(3), 282-290. DOI: [10.1080/02626667009493734](https://doi.org/10.1080/02626667009493734)