# NSE с весами по дисперсии (Variance-Weighted NSE)

## Название и назначение

**NSE с весами по дисперсии (Variance-Weighted NSE)** — вариант NSE для оценки качества моделирования на нескольких станциях/реках одновременно. Каждая станция взвешивается пропорционально дисперсии её наблюдений, чтобы станции с большей вариабельностью вносили больший вклад.

Полезен для мульти-стационарной оценки (multi-gauge evaluation), когда нужно получить единую интегральную оценку качества модели по всей сети наблюдений.

## Математическая формула

$$\text{NSE}_{\text{vw}} = 1 - \frac{\sum_{k=1}^{K} w_k \sum_{i=1}^{n_k} (y_{ki} - \hat{y}_{ki})^2}{\sum_{k=1}^{K} w_k \sum_{i=1}^{n_k} (y_{ki} - \bar{y}_k)^2}$$

Где:
- $K$ — количество станций/групп
- $n_k$ — количество наблюдений на станции $k$
- $y_{ki}$ — наблюдаемое значение на станции $k$, момент $i$
- $\hat{y}_{ki}$ — смоделированное значение на станции $k$, момент $i$
- $\bar{y}_k$ — среднее наблюдаемое значение на станции $k$
- $w_k = \text{Var}(y_k)$ — вес станции $k$ (дисперсия её наблюдений)

**Реализация** (`_nse_variance_weighted_core`):
- Вычисляет NSE для каждой группы отдельно
- Взвешивает числитель и знаменатель дисперсиями групп
- Требует параметр `group` (array-like) для указания принадлежности к группам
- Поддерживает `nan_policy` и `sentinel`

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Идеальное совпадение на всех станциях |
| **0.0** | В среднем не лучше средних по станциям |
| **< 0.0** | В среднем хуже средних по станциям |
| **(-∞, 1.0]** | Теоретический диапазон |

Направление: **maximize**
Идеальное значение: **1.0**

Станции с большей вариабельностью (дисперсией) имеют больший вес в итоговой оценке.

## Публичный API

```python
from hydrometrics import nse_variance_weighted

result = nse_variance_weighted(
    obs: array-like,
    sim: array-like,
    group: array-like,
    *,
    weight: array-like | None = None,
    axis: int | None = None,
    reduction: Literal["mean", "sum", "none"] = "mean",
    nan_policy: Literal["omit", "propagate", "raise"] = "omit",
    sentinel: float | list[float] | None = None,
) -> MetricResult
```

**Импорт**: `from hydrometrics import nse_variance_weighted`

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `obs` | array-like | обязательный | Наблюдаемые значения |
| `sim` | array-like | обязательный | Смоделированные значения |
| `group` | array-like | обязательный | Идентификаторы групп/станций |
| `weight` | array-like | `None` | Дополнительные веса выборки |
| `axis` | int | `None` | Ось для вычислений |
| `reduction` | str | `"mean"` | Редукция для массивов |
| `nan_policy` | str | `"omit"` | Политика NaN |
| `sentinel` | float/list | `None` | Значения-пропуски |

## Python пример

```python
import numpy as np
from hydrometrics import nse_variance_weighted

# Данные: 30 временных шагов × 3 станции (сплющены в 1D)
obs = np.concatenate([
    np.random.normal(100, 20, 10),  # Станция 1: среднее 100, std 20
    np.random.normal(50, 10, 10),   # Станция 2: среднее 50, std 10
    np.random.normal(200, 50, 10),  # Станция 3: среднее 200, std 50 (больший вес)
])
sim = obs + np.random.randn(30) * 5

group = np.array([0]*10 + [1]*10 + [2]*10)  # 3 станции

result = nse_variance_weighted(obs, sim, group)
print(result)
# Variance-Weighted NSE: 0.8723 (direction: maximize, bounds: (-inf, 1.0))
```

## Связанные метрики

- [NSE (nse)](nse.md) — классический NSE для одной станции
- [KGE 2012 (kge_2012)](kge_2012.md) — декомпозируемая альтернатива для мульти-стационарной оценки

## Научные ссылки

1. **Nash, J. E., & Sutcliffe, J. V. (1970).** River flow forecasting through conceptual models part I. *Journal of Hydrology*, 10(3), 282-290. DOI: 10.1016/0022-1694(70)90255-6

2. **Krause, P., Boyle, D. P., & Bäse, F. (2005).** Comparison of different efficiency criteria for hydrological model assessment. *Advances in Geosciences*, 5, 89-97. DOI: 10.5194/adgeo-5-89-2005