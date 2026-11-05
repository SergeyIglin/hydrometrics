# Регрессионные метрики

Базовые метрики для оценки точности предсказаний непрерывных переменных.

## MAE — Mean Absolute Error

```python
from hydrometrics import mae
mae(obs, sim, **kwargs)
```

- **Направление**: minimize
- **Границы**: [0, ∞)
- **Формула**: $\frac{1}{n}\sum|y_i - \hat{y}_i|$
- **Описание**: Средняя абсолютная ошибка. Интерпретируема в единицах измерения.
- **Чувствительность**: Линейная к ошибкам, робастна к выбросам.

## MSE — Mean Squared Error

```python
from hydrometrics import mse
mse(obs, sim, **kwargs)
```

- **Направление**: minimize
- **Границы**: [0, ∞)
- **Формула**: $\frac{1}{n}\sum(y_i - \hat{y}_i)^2$
- **Описание**: Среднеквадратичная ошибка. Сильно штрафует большие ошибки.
- **Использование**: Функция потерь для обучения моделей.

## RMSE — Root Mean Squared Error

```python
from hydrometrics import rmse
rmse(obs, sim, **kwargs)
```

- **Направление**: minimize
- **Границы**: [0, ∞)
- **Формула**: $\sqrt{\frac{1}{n}\sum(y_i - \hat{y}_i)^2}$
- **Описание**: Корень из MSE. В тех же единицах, что и данные.
- **Связь**: RMSE ≥ MAE (равенство при постоянной ошибке).

## NRMSE — Normalized RMSE

```python
from hydrometrics import nrmse
nrmse(obs, sim, norm="mean", **kwargs)
```

- **Направление**: minimize
- **Границы**: [0, ∞)
- **Параметр `norm`**:
  - `"mean"` (default) — деление на $\bar{y}$
  - `"maxmin"` — деление на $\max(y) - \min(y)$
  - `"std"` — деление на $\sigma_y$
- **Описание**: Безразмерная RMSE для сравнения между разными наборами данных.

## Bias — Mean Error

```python
from hydrometrics import bias
bias(obs, sim, **kwargs)
```

- **Направление**: minimize
- **Границы**: (-∞, ∞)
- **Формула**: $\frac{1}{n}\sum(\hat{y}_i - y_i)$
- **Описание**: Среднее смещение (sim - obs). Положительное = завышение.
- **Идеальное значение**: 0.

## PBIAS — Percent Bias

```python
from hydrometrics import pbias
pbias(obs, sim, **kwargs)
```

- **Направление**: minimize
- **Границы**: (-∞, ∞)
- **Формула**: $100 \times \frac{\sum(\hat{y}_i - y_i)}{\sum y_i}$
- **Описание**: Процентное смещение. Широко используется в гидрологии.
- **Критерии (Moriasi et al. 2007)**:
  - < ±10%: Очень хорошо
  - ±10–15%: Хорошо
  - ±15–25%: Удовлетворительно
  - > ±25%: Неудовлетворительно

## R² — Coefficient of Determination

```python
from hydrometrics import r2
r2(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Формула**: $1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}$
- **Описание**: Доля дисперсии, объяснённой моделью. Может быть отрицательной (хуже среднего).
- **Связь**: Для линейной регрессии без смещения R² = (Pearson r)².

## Pearson Correlation (r)

```python
from hydrometrics import pearson_r
pearson_r(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: [-1, 1]
- **Формула**: $\frac{\sum(y_i - \bar{y})(\hat{y}_i - \bar{\hat{y}})}{\sqrt{\sum(y_i - \bar{y})^2 \sum(\hat{y}_i - \bar{\hat{y}})^2}}$
- **Описание**: Линейная корреляция. Не чувствителен к смещению и масштабу.
- **Веса**: Игнорирует `sample_weight`.

## Spearman Rank Correlation

```python
from hydrometrics import spearman_r
spearman_r(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: [-1, 1]
- **Описание**: Ранговая корреляция. Монотнонная связь. Робастна к выбросам.
- **Веса**: Игнорирует `sample_weight`.
- **Требует**: SciPy.

## Kendall's Tau

```python
from hydrometrics import kendall_tau
kendall_tau(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: [-1, 1]
- **Описание**: Мера ранга. Более робастная, чем Спирмен. Медленнее (O(n log n)).
- **Веса**: Игнорирует `sample_weight`.
- **Требует**: SciPy.

## Willmott's Index of Agreement (d)

```python
from hydrometrics import willmott_d
willmott_d(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: [0, 1]
- **Формула**: $1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(|\hat{y}_i - \bar{y}| + |y_i - \bar{y}|)^2}$
- **Описание**: Индекс согласия Уиллмота. 1 = идеальное совпадение.
- **Ссылка**: Willmott (1981) DOI: 10.1175/1520-0450(1981)020<0117:OTSOAI>2.0.CO;2