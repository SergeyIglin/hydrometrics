# Классификация событий

Примеры бинарной классификации для гидрологических событий (паводки, сухость).

## Базовая классификация

```python
import numpy as np
from hydrometrics import (
    accuracy, precision, recall, f1_score,
    roc_auc, pr_auc, edi, sedi
)

np.random.seed(42)
n = 1000

# Истинные события (1 = паводок, 0 = нет)
# Базовая частота 10%
obs = np.random.binomial(1, 0.10, n)

# Прогнозы с некоторым качеством
# Вероятность детекции = 0.8, ложная тревога = 0.15
prob_detect = 0.8
prob_false = 0.15

sim_binary = np.zeros(n)
for i in range(n):
    if obs[i] == 1:
        sim_binary[i] = np.random.binomial(1, prob_detect)
    else:
        sim_binary[i] = np.random.binomial(1, prob_false)

# Метрики классификации
print(f"Accuracy:  {accuracy(obs, sim_binary)}")
print(f"Precision: {precision(obs, sim_binary)}")
print(f"Recall:    {recall(obs, sim_binary)}")
print(f"F1 Score:  {f1_score(obs, sim_binary)}")
```

## Вероятностные прогнозы (ROC-AUC, PR-AUC)

```python
# Вероятностный прогноз (не бинарный!)
# Для событий: выше вероятность, для не-событий: ниже
prob_event = 0.7 + np.random.beta(2, 5, np.sum(obs == 1)) * 0.3
prob_noevent = np.random.beta(1, 5, np.sum(obs == 0)) * 0.4

sim_prob = np.zeros(n)
sim_prob[obs == 1] = prob_event
sim_prob[obs == 0] = prob_noevent

roc = roc_auc(obs, sim_prob)
pr = pr_auc(obs, sim_prob)

print(f"ROC-AUC: {roc}")
print(f"PR-AUC:  {pr}")
```

## Редкие события: EDI и SEDI

Для редких событий (паводки, экстремальные сухини) обычные метрики не работают хорошо из-за дисбаланса классов. EDI и SEDI устойчивы к базовой частоте.

```python
# Очень редкое событие (1%)
obs_rare = np.random.binomial(1, 0.01, 10000)

# Идеальный прогноз
sim_perfect = obs_rare.copy()

# Случайный прогноз (базовая частота)
sim_random = np.random.binomial(1, 0.01, 10000)

# Прогноз с навыком
sim_skill = np.zeros(10000)
for i in range(10000):
    if obs_rare[i] == 1:
        sim_skill[i] = np.random.binomial(1, 0.7)  # POD = 0.7
    else:
        sim_skill[i] = np.random.binomial(1, 0.005)  # FAR = 0.005

print("=== Редкое событие (1%) ===")
for name, sim in [("Perfect", sim_perfect), ("Random", sim_random), ("Skill", sim_skill)]:
    print(f"\n{name}:")
    print(f"  Accuracy:  {accuracy(obs_rare, sim):.4f}")
    print(f"  Precision: {precision(obs_rare, sim):.4f}")
    print(f"  Recall:    {recall(obs_rare, sim):.4f}")
    print(f"  F1:        {f1_score(obs_rare, sim):.4f}")
    print(f"  EDI:       {edi(obs_rare, sim):.4f}")
    print(f"  SEDI:      {sedi(obs_rare, sim):.4f}")

# EDI/SEDI диапазон: [-1, 1]
# 1 = идеальный, 0 = случайный, < 0 = хуже случайного
```

## Практический пример: прогноз паводков

```python
import numpy as np
import pandas as pd
from hydrometrics import (
    accuracy, precision, recall, f1_score,
    roc_auc, pr_auc, edi, sedi
)

np.random.seed(123)

# 5 лет дневных данных
dates = pd.date_range("2018-01-01", periods=1825, freq="D")
n = len(dates)

# Наблюдаемые расходы
obs_flow = np.random.gamma(shape=2.0, scale=50.0, size=n)

# Порог паводка: 95 перцентиль
flood_threshold = np.percentile(obs_flow, 95)
obs_flood = (obs_flow > flood_threshold).astype(int)

print(f"Flood threshold: {flood_threshold:.1f} m³/s")
print(f"Flood days: {obs_flood.sum()} ({obs_flood.mean()*100:.1f}%)")

# Модель: вероятность паводка
# Хорошая модель: высокая вероятность в дни паводков
prob_flood = np.zeros(n)
for i in range(n):
    if obs_flood[i] == 1:
        # В дни паводка: высокая вероятность
        prob_flood[i] = 0.6 + np.random.beta(3, 2) * 0.4
    else:
        # В обычные дни: низкая вероятность
        prob_flood[i] = np.random.beta(1, 10) * 0.3

# Бинарный прогноз по порогу 0.5
sim_binary = (prob_flood > 0.5).astype(int)

print("\n=== Binary metrics (threshold=0.5) ===")
print(f"Accuracy:  {accuracy(obs_flood, sim_binary):.4f}")
print(f"Precision: {precision(obs_flood, sim_binary):.4f}")
print(f"Recall:    {recall(obs_flood, sim_binary):.4f}")
print(f"F1 Score:  {f1_score(obs_flood, sim_binary):.4f}")
print(f"EDI:       {edi(obs_flood, sim_binary):.4f}")
print(f"SEDI:      {sedi(obs_flood, sim_binary):.4f}")

print("\n=== Probabilistic metrics ===")
print(f"ROC-AUC: {roc_auc(obs_flood, prob_flood):.4f}")
print(f"PR-AUC:  {pr_auc(obs_flood, prob_flood):.4f}")

# Reliability diagram данные
from hydrometrics import reliability, sharpness
rel = reliability(obs_flood, prob_flood, n_bins=10)
sharp = sharpness(prob_flood)
print(f"\nReliability: {rel:.4f}")
print(f"Sharpness:   {sharp:.4f}")
```

## Оптимизация порога

```python
# Поиск оптимального порога для F1
thresholds = np.arange(0.05, 0.95, 0.05)
f1_scores = []

for thresh in thresholds:
    sim_bin = (prob_flood > thresh).astype(int)
    f1_scores.append(float(f1_score(obs_flood, sim_bin)))

best_idx = np.argmax(f1_scores)
print(f"\nBest threshold: {thresholds[best_idx]:.2f} (F1={f1_scores[best_idx]:.4f})")

# Поиск по SEDI (лучше для редких событий)
sedi_scores = []
for thresh in thresholds:
    sim_bin = (prob_flood > thresh).astype(int)
    sedi_scores.append(float(sedi(obs_flood, sim_bin)))

best_sedi_idx = np.argmax(sedi_scores)
print(f"Best threshold (SEDI): {thresholds[best_sedi_idx]:.2f} (SEDI={sedi_scores[best_sedi_idx]:.4f})")
```