.. _quickstart:

===========================
Установка и быстрый старт
===========================

Установка
-----------

Пакету нужен Python 3.10 или новее. Обязательные зависимости: numpy, pandas, xarray, polars и scipy. Установка из каталога репозитория:

.. code-block:: bash

   pip install hydrometrics

Для разработки и для сборки этой документации есть дополнительные наборы зависимостей ``dev`` и ``docs``: ``pip install ".[docs]"``

Первый расчёт
---------------

Все метрики вызываются одинаково: наблюдения и модель, затем необязательные аргументы. Результат это объект :class:`~hydrometrics.MetricResult`.

.. testcode::

   import numpy as np
   import hydrometrics as hm

   rng = np.random.default_rng(42)
   dates = np.arange("2010-10-01", "2013-10-01", dtype="datetime64[D]")
   doy = (dates - dates.astype("datetime64[Y]")).astype(int)
   # Половодье в конце апреля поверх зимней и летней межени, м³/с
   q_obs = 12 + 240 * np.exp(-(((doy - 118) / 16.0) ** 2)) + rng.gamma(2.0, 2.5, doy.size)
   # Модель запаздывает на двое суток и срезает пик
   q_sim = np.clip(0.88 * np.roll(q_obs, 2) + 3 + rng.normal(0, 5, doy.size), 0.1, None)

.. testcode::

   result = hm.nse(q_obs, q_sim)
   print(float(result))
   print(result.name, result.direction, result.bounds)

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.9537496969880442
   Nash-Sutcliffe Efficiency maximize (-inf, 1.0)

Несколько метрик по одной паре рядов: расходы воды в м³/с, суточный шаг.

.. testcode::

   for name in ("nse", "kge_2012", "rmse", "pbias"):
       print(f"{name:9s} {float(getattr(hm, name)(q_obs, q_sim)):9.4f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   nse          0.9537
   kge_2012     0.9063
   rmse        11.4078
   pbias       -3.0107

Дальше: :doc:`concept` объясняет устройство вызова, :doc:`input_data` описывает типы входов, :doc:`choosing` помогает выбрать метрику, а страницы :doc:`/metrics/index` содержат определения.
