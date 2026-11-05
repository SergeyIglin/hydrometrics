# VE (Volumetric Efficiency)

## Название и назначение

**VE (Volumetric Efficiency)** — метрика эффективности по объёму, оценивающая, насколько хорошо смоделированный общий объём соответствует наблюдаемому. В отличие от NSE, не чувствительна к временной фазе, а только к суммарному объёму.

Полезна для оценки водного баланса: правильно ли модель воспроизводит общий объём стока.

## Математическая формула

$$\text{VE} = 1 - \frac{\sum_{i=1}^{n} |y_i - \hat{y}_i|}{\sum_{i=1}^{n} |y_i|}$$

Где:
- $y_i$ — наблюдаемое значение
- $\hat{y}_i$ — смоделированное значение
- $n$ — количество валидных пар

**Реализация** (`_ve_core`):
- Числитель: сумма абсолютных ошибок (L1-норма ошибок)
- Знаменатель: сумма абсолютных наблюдений
- VE = 1 — идеальное совпадение объёмов
- VE = 0 — эквивалентно нулевому моделированию

## Интерпретация

| Значение | Интерпретация |
|----------|---------------|
| **1.0** | Идеальное совпадение объёмов |
| **0.0** | Эквивалентно моделированию нулями |
| **< 0.0** | Ошибка по объёму больше, чем сам объём наблюдений |
| **(-∞, 1.0]** | Теоретический диапазон |

Направление: **maximize**
Идеальное значение: **1.0**

Не учитывает временную динамику — только суммарный объём.

## Публичный API

```python
from hydrometrics import ve

result = ve(
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

**Импорт**: `from hydrometrics import ve`

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
from hydrometrics import ve

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

result = ve(obs, sim)
print(result)
# VE: 0.9723 (direction: maximize, bounds: (-inf, 1.0))
```

## Связанные метрики

- [PBIAS (pbias)](pbias.md) — процентное смещение (только bias, без абсолютных ошибок)
- [NSE (nse)](nse.md) — учитывает и фазу, и амплитуду
- [Modified NSE (modified_nse)](modified_nse.md) — использует абсолютные ошибки

## Научные ссылки

1. **Criss, R. E., & Winston, W. E. (2008).** Do Nash values have value? Discussion and alternate proposals. *Hydrological Processes*, 22(14), 2723-2725. DOI: 10.1002/hyp.7072

2. **Criss, R. E., & Winston, W. E. (2008).** Reply to commentary on "Do Nash values have value?". *Hydrological Processes*, 22(14), 2735-2737. DOI: 10.1002/hyp.6989