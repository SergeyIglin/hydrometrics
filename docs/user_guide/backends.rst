.. _backends:

=========
Бэкенды
=========

Поддерживаются четыре типа входов. Выбор бэкенда автоматический и описан в :doc:`input_data`; вручную его не задают и не меняют.

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 12 24 34 30

   * - Бэкенд
     - Входы
     - Результат для скалярной метрики
     - Результат по оси
   * - numpy
     - ``list``, ``ndarray``
     - ``MetricResult`` со скаляром
     - ``ndarray``
   * - pandas
     - ``Series``, ``DataFrame``
     - ``MetricResult`` со скаляром
     - ``ndarray``
   * - polars
     - ``Series``, ``DataFrame``
     - ``MetricResult`` со скаляром
     - ``ndarray``
   * - xarray
     - ``DataArray``
     - ``MetricResult`` со скаляром
     - ``DataArray`` с координатами

Что одинаково на всех бэкендах: значения, политика пропусков, правила для весов и ``reduction``, исключения, метаданные метрик. Что отличается: тип значения при расчёте по оси; ``xarray.Dataset`` не принимается; ``polars.LazyFrame`` не поддерживается.

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

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   import pandas as pd
   import polars as pl
   import xarray as xr

   frame = pd.DataFrame(q_obs_st, columns=["upper", "middle", "lower"])
   frame_sim = pd.DataFrame(q_sim_st, columns=["upper", "middle", "lower"])
   print(np.round(hm.nse(frame, frame_sim, axis=0).value, 4))
   print(np.round(hm.nse(pl.DataFrame(frame), pl.DataFrame(frame_sim), axis=0).value, 4))
   coords = {"time": dates, "station": ["upper", "middle", "lower"]}
   obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
   sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
   print(hm.nse(obs_da, sim_da, dim="time").value.round(4).to_series().to_dict())

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.9537 0.9206 0.9632]
   [0.9537 0.9206 0.9632]
   {'upper': 0.9537, 'middle': 0.9206, 'lower': 0.9632}

Измерений скорости не проводилось, и утверждений о производительности документация не делает. Ядра работают на numpy; ранговые метрики (:func:`~hydrometrics.spearman_r`, :func:`~hydrometrics.kendall_tau`) и :func:`~hydrometrics.roc_auc` считают срезы по оси в цикле.
