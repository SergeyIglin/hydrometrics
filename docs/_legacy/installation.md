# Установка

## Требования

- **Python** ≥ 3.9
- **NumPy** ≥ 1.21
- **SciPy** ≥ 1.7 (для некоторых метрик)

## Базовая установка

```bash
pip install hydrometrics
```

Это установит минимальный набор зависимостей (только NumPy).

## Опциональные зависимости

Библиотека поддерживает несколько бэкендов для работы с разными типами данных. Установите нужные вам:

```bash
# Pandas поддержка (Series, DataFrame)
pip install hydrometrics[pandas]

# Xarray поддержка (DataArray, Dataset) — для многомерных данных
pip install hydrometrics[xarray]

# Polars поддержка (Series, DataFrame) — быстрый DataFrame
pip install hydrometrics[polars]

# Все бэкенды сразу
pip install hydrometrics[all-backends]
```

## Установка для разработки

```bash
# Клонируйте репозиторий
git clone https://github.com/SergeyIglin/hydrometrics.git
cd hydrometrics

# Установите в режиме разработки с dev-зависимостями
pip install -e .[dev]

# Или с зависимостями для документации
pip install -e .[docs]

# Все опциональные зависимости
pip install -e .[all]
```

Зависимости групп:
- `dev`: pytest, hypothesis, black, ruff, mypy, pre-commit
- `docs`: sphinx, sphinx-rtd-theme, myst-parser, nbsphinx, sphinx-copybutton
- `all`: все вышеперечисленные + pandas, xarray, polars

## Проверка установки

```python
import hydrometrics as hm
print(hm.__version__)
# 0.1.0

from hydrometrics import nse
import numpy as np

obs = np.array([1, 2, 3, 4, 5])
sim = np.array([1.1, 2.2, 2.8, 4.1, 4.9])
print(nse(obs, sim))
# NSE: 0.99... (direction: maximize, bounds: (-inf, 1.0))
```

## Возможные проблемы

### Отсутствует SciPy
Некоторые метрики (Spearman, Kendall, Willmott's d) требуют SciPy. Установите его:
```bash
pip install scipy
```

### Конфликт версий NumPy
Если у вас старый NumPy (< 1.21), обновите:
```bash
pip install --upgrade numpy
```

### Xarray/Polars не импортируются
Это нормально — они опциональны. Бэкенд активируется только при наличии библиотеки и соответствующих входных данных.