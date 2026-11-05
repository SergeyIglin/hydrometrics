# NSE — Nash-Sutcliffe Efficiency

Основная метрика в гидрологии для оценки качества моделирования расхода.

## Классический NSE

```python
from hydrometrics import nse
nse(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Формула**: $1 - \frac{\sum_{i=1}^n (y_i - \hat{y}_i)^2}{\sum_{i=1}^n (y_i - \bar{y})^2}$
- **Ссылка**: Nash & Sutcliffe (1970) DOI: 10.1088/0022-3727/3/3/306

### Интерпретация

| NSE | Качество | Значение |
|-----|----------|----------|
| 1.0 | Идеальное | Модель = наблюдения |
| > 0.75 | Очень хорошее | Рекомендуется для операционного использования |
| 0.65–0.75 | Хорошее | Приемлемо для многих применений |
| 0.50–0.65 | Удовлетворительное | Требует улучшения |
| 0.0 | Эквивалент среднего | Модель не лучше константы $\bar{y}$ |
| < 0 | Хуже среднего | Среднее наблюдений точнее модели |

## Log NSE

```python
from hydrometrics import log_nse
log_nse(obs, sim, eps=1e-10, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Параметр `eps`**: Смещение для избежания log(0), default 1e-10
- **Формула**: NSE на log(obs + eps) и log(sim + eps)
- **Использование**: Акцент на малых расходах, сухость.

## Modified NSE (L1 norm)

```python
from hydrometrics import modified_nse
modified_nse(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Формула**: $1 - \frac{\sum|y_i - \hat{y}_i|}{\sum|y_i - \bar{y}|}$ (L1 вместо L2)
- **Свойства**: Менее чувствителен к выбросам/пиковым ошибкам.
- **Примечание**: Параметр `j` (степень) не поддерживается — фиксирован j=1 (L1).

## Normalized NSE (NNSE)

```python
from hydrometrics import nnse
nnse(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: [0, 1]
- **Формула**: $\frac{1}{2 - NSE}$ для NSE ≤ 1, иначе 1
- **Свойства**: Ограничивает диапазон [0, 1]. Линейно отображает NSE ≤ 1.

## Variance-weighted NSE (многопостовая)

```python
from hydrometrics import nse_variance_weighted
nse_variance_weighted(obs, sim, gauge, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Параметр `gauge`**: Массив ID станций (обязательный)
- **Формула**: $\frac{\sum_g w_g NSE_g}{\sum_g w_g}$, где $w_g = \sigma_g^2$
- **Использование**: Общий NSE для нескольких станций с весами по дисперсии.

## Пример использования

```python
import numpy as np
from hydrometrics import nse, log_nse, modified_nse, nnse

np.random.seed(42)
obs = np.random.lognormal(2.0, 0.5, 365)
sim = obs * np.random.lognormal(-0.03, 0.15, 365) + np.random.normal(0, 3, 365)
sim = np.maximum(sim, 0.1)

print(f"NSE:           {float(nse(obs, sim)):.3f}")
print(f"Log NSE:       {float(log_nse(obs, sim)):.3f}")
print(f"Modified NSE:  {float(modified_nse(obs, sim)):.3f}")
print(f"NNSE:          {float(nnse(obs, sim)):.3f}")

# Многопостовая
gauge = np.repeat(["A", "B", "C", "D", "E"], 73)
# Разная длина для примера
gauge = gauge[:365]
print(f"Variance-w NSE: {float(nse_variance_weighted(obs, sim, gauge)):.3f}")
```

## Критика и ограничения NSE

1. **Чувствителен к пикам** — L2 норма даёт большой вес большим ошибкам
2. **Асимметричен** — завышение штрафуется сильнее занижения
3. **Не подходит для лог-нормальных данных** — используйте Log NSE
4. **NSE < 0** — трудно интерпретировать "насколько хуже"

### Рекомендации

- Всегда смотрите **Log NSE** для малых расходов
- Используйте **KGE** для диагностики компонент ошибки
- **Modified NSE** — для робастной оценки
- **NNSE** — для сравнения между бассенами