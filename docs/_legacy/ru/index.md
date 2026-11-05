# HydroMetrics

**Библиотека метрик для оценки гидрологических и гидрометеорологических моделей**

Комплексная Python-библиотека для оценки гидрологических моделей с поддержкой структур данных NumPy, pandas, xarray и polars.

## Возможности

- **Единый API**: Все метрики следуют одному интерфейсу с согласованными параметрами
- **Многобэкендная поддержка**: Бесшовная работа с NumPy, pandas, xarray и polars
- **Научная строгость**: Каждая метрика включает оригинальную ссылку (DOI), формулу и ограничения
- **Комплексные метрики**: Регрессионные, гидрологические, вероятностные и классификационные метрики
- **Правильная обработка NaN**: Три политики (propagate, omit, raise) с детальными отчётами
- **Богатые объекты результатов**: `MetricResult` содержит значение, метаданные, происхождение и направление оптимизации
- **Обширное тестирование**: >95% покрытие с property-based тестами (Hypothesis)

## Установка

```bash
pip install hydrometrics
```

Опциональные зависимости для разработки и документации:

```bash
pip install hydrometrics[dev]    # Зависимости для разработки
pip install hydrometrics[docs]   # Зависимости для документации
pip install hydrometrics[all]    # Все опциональные зависимости
```

Требуется Python ≥ 3.9.

## Быстрый старт

```python
import numpy as np
from hydrometrics import nse, kge_2012, mae

# Наблюдаемые и смоделированные значения расхода
obs = np.array([10, 12, 15, 14, 13, 11, 9, 8, 7, 9])
sim = np.array([9.5, 11.8, 14.5, 14.2, 13.5, 10.8, 8.8, 7.5, 6.8, 8.5])

# Коэффициент Наша-Сутклиффа (NSE)
nse_result = nse(obs, sim)
print(nse_result)
# NSE: 0.92 (direction: maximize, bounds: (-inf, 1.0))

# Эффективность Клинга-Гупты (KGE 2012)
kge_result = kge_2012(obs, sim)
print(kge_result)
# KGE 2012: 0.95 (direction: maximize, bounds: (-inf, 1.0))

# Средняя абсолютная ошибка (MAE)
mae_result = mae(obs, sim)
print(mae_result)
# Mean Absolute Error: 0.38 (direction: minimize, bounds: (0.0, inf))
```

Все метрики возвращают объект `MetricResult` с:
- **value**: Вычисленное значение метрики
- **direction**: "maximize" или "minimize"
- **bounds**: Теоретические границы (нижняя, верхняя)
- **parameters**: Параметры, использованные при вычислении
- **reference**: DOI или цитирование
- **nan_info**: Информация об обработке NaN

## Язык документации

- **Русский** (текущий) — основной язык документации
- [English](../en/index.md) — полная английская версия

## Структура документации

```{toctree}
:maxdepth: 2
:caption: Начало работы

installation
quickstart
```

```{toctree}
:maxdepth: 2
:caption: Руководство пользователя

user_guide/input_data
user_guide/missing_values
user_guide/backends
user_guide/interpreting_results
user_guide/grouped_metrics
```

```{toctree}
:maxdepth: 2
:caption: Справочник метрик

metric_reference/regression
metric_reference/hydro/index
metric_reference/probabilistic
metric_reference/classification
```

```{toctree}
:maxdepth: 2
:caption: Справочник API

api_reference
```

```{toctree}
:maxdepth: 1
:caption: Примеры

examples/basic_usage
examples/multi_backend
examples/grouped_analysis
examples/probabilistic_forecasts
examples/classification_events
```

## Ссылки

- **Репозиторий**: https://github.com/SergeyIglin/hydrometrics
- **Проблемы**: https://github.com/SergeyIglin/hydrometrics/issues
- **Документация**: https://hydrometrics.readthedocs.io
- **PyPI**: https://pypi.org/project/hydrometrics/

## Цитирование

Если вы используете HydroMetrics в своих исследованиях, пожалуйста, цитируйте соответствующие ссылки на метрики, указанные в документации каждой метрики.