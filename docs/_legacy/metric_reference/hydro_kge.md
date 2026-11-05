# KGE — Kling-Gupta Efficiency

Семейство метрик KGE (Kling-Gupta Efficiency) разлагает ошибку на три/четыре компонента.

## KGE 2012 (рекомендуется)

```python
from hydrometrics import kge_2012
kge_2012(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Компоненты**: r (корреляция), α (вариабельность), β (смещение), γ (вариация коэф. вариации)
- **Формула**: $1 - \sqrt{(r-1)^2 + (\alpha-1)^2 + (\beta-1)^2 + (\gamma-1)^2}$
- **Ссылка**: Kling et al. (2012) DOI: 10.1029/2011WR011082

## KGE 2009 (оригинал)

```python
from hydrometrics import kge_2009
kge_2009(obs, sim, **kwargs)
```

- **Направление**: maximize
- **Границы**: (-∞, 1.0]
- **Компоненты**: r, α, β (без γ)
- **Формула**: $1 - \sqrt{(r-1)^2 + (\alpha-1)^2 + (\beta-1)^2}$
- **Ссылка**: Gupta et al. (2009) DOI: 10.1029/2009WR008303

## Компоненты KGE

```python
from hydrometrics import kge_components, r_component, alpha_component, beta_component, gamma_component

# Все компоненты сразу
comp = kge_components(obs, sim, version="2012")  # или "2009"
print(comp.value)  # {'r': ..., 'alpha': ..., 'beta': ..., 'gamma': ...}

# Отдельно
r_component(obs, sim)        # Корреляция
alpha_component(obs, sim)    # Отношение стандартных отклонений
beta_component(obs, sim)     # Отношение средних
gamma_component(obs, sim)    # Отношение коэффициентов вариации (только 2012)
```

### Интерпретация компонент

| Компонента | Формула | Идеал | Значение |
|------------|---------|-------|----------|
| **r** | Pearson(obs, sim) | 1 | Линейная связь |
| **α** | σ_sim / σ_obs | 1 | Вариабельность |
| **β** | μ_sim / μ_obs | 1 | Смещение (bias) |
| **γ** | CV_sim / CV_obs | 1 | Форма распределения |

## KGE' (модифицированные версии)

### Non-parametric KGE (npKGE)

Использует Спирмен вместо Пирсона — для нелинейных связей.

```python
# Не встроено напрямую, но можно собрать:
from hydrometrics import spearman_r, alpha_component, beta_component
r = spearman_r(obs, sim)
alpha = alpha_component(obs, sim)
beta = beta_component(obs, sim)
npkge = 1 - np.sqrt((float(r)-1)**2 + (float(alpha)-1)**2 + (float(beta)-1)**2)
```

### KGE с весами

Все компоненты поддерживают `sample_weight` (кроме spearman_r).

## Интерпретация значений KGE

| KGE | Качество |
|-----|----------|
| > 0.75 | Очень хорошее |
| 0.50–0.75 | Хорошее |
| 0.25–0.50 | Удовлетворительное |
| < 0.25 | Неудовлетворительное |

## Типичные проблемы

| Проблема | Компонента | Решение |
|----------|------------|---------|
| Фазовый сдвиг | r ↓ | Калибровка маршрутизации |
| Амплитуда пиков | α ↓ | Параметры производства стока |
| Системное смещение | β ≠ 1 | Корректировка входов/параметров |
| Асимметрия распределения | γ ≠ 1 | Лог-трансформация / другие параметры |

## Пример разбора

```python
from hydrometrics import kge_2012, kge_components
import numpy as np

obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

kge = kge_2012(obs, sim)
comp = kge_components(obs, sim, version="2012")

print(f"KGE 2012: {float(kge):.3f}")
print(f"  r = {comp.value['r']:.3f} (correlation)")
print(f"  α = {comp.value['alpha']:.3f} (variability ratio)")
print(f"  β = {comp.value['beta']:.3f} (bias ratio)")
print(f"  γ = {comp.value['gamma']:.3f} (CV ratio)")

# Диагностика
if comp.value['beta'] > 1.1:
    print("⚠ Модель завышает расходы (β > 1.1)")
elif comp.value['beta'] < 0.9:
    print("⚠ Модель занижает расходы (β < 0.9)")

if comp.value['alpha'] > 1.1:
    print("⚠ Модель слишком переменчива (α > 1.1)")
elif comp.value['alpha'] < 0.9:
    print("⚠ Модель недостаточно переменчива (α < 0.9)")
```