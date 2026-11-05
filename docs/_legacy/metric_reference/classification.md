# Классификационные метрики

Метрики для бинарной классификации гидрологических событий (паводки, сухость, превышение порогов).

## Accuracy

```python
from hydrometrics import accuracy
accuracy(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: [0, 1]
- **Формула**: $\frac{TP + TN}{TP + TN + FP + FN}$
- **Ограничение**: Неподходит для дисбалансных классов (редкие события).

## Precision (PPV)

```python
from hydrometrics import precision
precision(obs, sim, positive_class=1, **kwargs)
```

- **Направление**: maximize
- **Границы**: [0, 1]
- **Формула**: $\frac{TP}{TP + FP}$
- **Параметр `positive_class`**: Метка положительного класса (default 1).
- **Описание**: Доля верных срабатываний среди всех срабатываний.

## Recall (Sensitivity, POD)

```python
from hydrometrics import recall
recall(obs, sim, positive_class=1, **kwargs)
```

- **Направление**: maximize
- **Границы**: [0, 1]
- **Формула**: $\frac{TP}{TP + FN}$
- **Описание**: Доля найденных событий среди всех реальных событий.
- **Гидрологический термин**: Probability of Detection (POD).

## F1 Score

```python
from hydrometrics import f1_score
f1_score(obs, sim, positive_class=1, **kwargs)
```

- **Направление**: maximize
- **Границы**: [0, 1]
- **Формула**: $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$
- **Описание**: Гармоническое среднее Precision и Recall.

## ROC-AUC

```python
from hydrometrics import roc_auc
roc_auc(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: [0, 1]
- **Вход**: `sim` — вероятности (не бинарные!)
- **Описание**: Площадь под ROC-кривой. Независима от порога.
- **Интерпретация**: Вероятность, что случайное событие получит более высокую вероятность, чем случайное не-событие.

## PR-AUC (Average Precision)

```python
from hydrometrics import pr_auc
pr_auc(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: [0, 1]
- **Вход**: `sim` — вероятности
- **Описание**: Площадь под Precision-Recall кривой. Лучше для редких событий.

## EDI — Extremal Dependence Index

```python
from hydrometrics import edi
edi(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: [-1, 1]
- **Формула**: $\frac{\log(POD) - \log(POFD)}{\log(POD) + \log(POFD)}$ где $POFD = \frac{FP}{FP + TN}$
- **Свойства**: Устойчив к базовой частоте событий. Симметричен.
- **Интерпретация**: 1 = идеальный, 0 = случайный, < 0 = хуже случайного.
- **Ссылка**: Ferro & Stephenson (2011) DOI: 10.1175/WAF-D-10-05030.1

## SEDI — Symmetric EDI

```python
from hydrometrics import sedi
sedi(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: [-1, 1]
- **Формула**: $\frac{\log(\text{POD}) - \log(\text{POFD})}{\log(\text{POD}) + \log(\text{POFD})} \times \frac{\log(1-\text{POFD}) - \log(1-\text{POD})}{\log(1-\text{POFD}) + \log(1-\text{POD})}$
- **Свойства**: Полностью симметричен (обмен классов не меняет значение). Работает для любых базовых частот.
- **Рекомендация**: Лучшая метрика для редких гидрологических событий.

## Сводная таблица

| Метрика | Вход | Направление | Границы | Для редких событий |
|---------|------|-------------|---------|-------------------|
| `accuracy` | binary | maximize | [0, 1] | ❌ Нет |
| `precision` | binary | maximize | [0, 1] | ⚠ Частично |
| `recall` | binary | maximize | [0, 1] | ⚠ Частично |
| `f1_score` | binary | maximize | [0, 1] | ⚠ Частично |
| `roc_auc` | prob | maximize | [0, 1] | ✅ Да |
| `pr_auc` | prob | maximize | [0, 1] | ✅ Да (лучше) |
| `edi` | binary | maximize | [-1, 1] | ✅ Да |
| `sedi` | binary | maximize | [-1, 1] | ✅ Да (лучшая) |

## Пример: прогноз паводков

```python
import numpy as np
from hydrometrics import (
    accuracy, precision, recall, f1_score,
    roc_auc, pr_auc, edi, sedi
)

np.random.seed(42)
n = 10000

# Редкое событие: паводок (2%)
obs = np.random.binomial(1, 0.02, n)

# Вероятностный прогноз
prob = np.zeros(n)
prob[obs == 1] = 0.5 + np.random.beta(2, 3, np.sum(obs == 1)) * 0.5  # POD ~ 0.7
prob[obs == 0] = np.random.beta(1, 20, np.sum(obs == 0)) * 0.1         # FAR ~ 0.005

# Бинарный по порогу 0.5
sim_bin = (prob > 0.5).astype(int)

print("=== Binary metrics ===")
print(f"Accuracy:  {float(accuracy(obs, sim_bin)):.4f}")
print(f"Precision: {float(precision(obs, sim_bin)):.4f}")
print(f"Recall:    {float(recall(obs, sim_bin)):.4f}")
print(f"F1:        {float(f1_score(obs, sim_bin)):.4f}")
print(f"EDI:       {float(edi(obs, sim_bin)):.4f}")
print(f"SEDI:      {float(sedi(obs, sim_bin)):.4f}")

print("\n=== Probabilistic metrics ===")
print(f"ROC-AUC: {float(roc_auc(obs, prob)):.4f}")
print(f"PR-AUC:  {float(pr_auc(obs, prob)):.4f}")

# Сравнение с базовой частотой
print(f"\nBase rate: {obs.mean():.3f}")
print(f"Random EDI: {float(edi(obs, np.random.binomial(1, 0.02, n))):.4f}")
print(f"Random SEDI: {float(sedi(obs, np.random.binomial(1, 0.02, n))):.4f}")
```

## Рекомендации по выбору

| Ситуация | Рекомендуемая метрика |
|----------|----------------------|
| Сбалансированные классы | F1, Accuracy |
| Редкие события (бинарный прогноз) | **SEDI**, EDI |
| Редкие события (вероятностный) | **PR-AUC**, ROC-AUC |
| Нужен интерпретируемый порог | Precision, Recall, F1 |
| Оптимизация порога | Поиск max SEDI / max F1 |

## Важные замечания

1. **Accuracy бесполезна для редких событий**: При 1% паводков accuracy = 99% даже для модели "всегда нет"
2. **Precision/Recall зависят от порога**: Всегда проверяйте несколько порогов
3. **SEDI лучше EDI**: Полностью симметрична, работает для любых базовых частот
4. **PR-AUC > ROC-AUC для редких событий**: ROC-AUC может быть оптимистично задрожена