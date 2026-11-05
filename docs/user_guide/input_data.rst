.. _input-data:

===========================
Входные данные и проверки
===========================

Метрики принимают наблюдённый ряд ``obs`` и модельный ``sim`` одинаковой формы. Библиотека определяет бэкенд по типу входа, приводит данные к числам с плавающей точкой и возвращает результат в типе, привычном для этого бэкенда.

Допустимые типы и выбор бэкенда
---------------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 34 14 52

   * - Тип входа
     - Бэкенд
     - Замечания
   * - ``list``, ``numpy.ndarray``
     - numpy
     - Списки и массивы целых и логических значений приводятся к ``float64``; ``float32`` сохраняется.
   * - ``pandas.Series``, ``pandas.DataFrame``
     - pandas
     - Столбцы DataFrame трактуются как створы при ``axis=0``.
   * - ``polars.Series``, ``polars.DataFrame``
     - polars
     - ``LazyFrame`` не поддерживается.
   * - ``xarray.DataArray``
     - xarray
     - Ось задаётся именем измерения, ``dim``.
   * - ``xarray.Dataset``
     - -
     - ``NotImplementedError``: выберите переменную, например ``ds["discharge"]``.

Бэкенд выбирается по первому подходящему типу среди ``obs`` и ``sim`` в порядке xarray, pandas, polars; иначе numpy. Поэтому смешанный вызов, например ``obs`` в pandas и ``sim`` в numpy, допустим и идёт по пути pandas. Явного выбора бэкенда нет.

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

   import pandas as pd
   import polars as pl
   import xarray as xr

   inputs = {
       "numpy": (q_obs, q_sim),
       "pandas": (pd.Series(q_obs), pd.Series(q_sim)),
       "polars": (pl.Series(q_obs), pl.Series(q_sim)),
       "xarray": (xr.DataArray(q_obs, dims="time"), xr.DataArray(q_sim, dims="time")),
   }
   for backend, (obs, sim) in inputs.items():
       result = hm.nse(obs, sim)
       print(f"{backend:7s} {type(result).__name__} {type(result.value).__name__} {float(result):.6f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   numpy   MetricResult float64 0.953750
   pandas  MetricResult float64 0.953750
   polars  MetricResult float64 0.953750
   xarray  MetricResult float64 0.953750

Результат один и тот же на всех бэкендах. Различается тип значения для расчёта по оси: на xarray это ``DataArray`` с сохранёнными координатами, на остальных ``numpy.ndarray``.

Выравнивание рядов: параметр align
------------------------------------

Метрики сопоставляют значения по позиции, но у pandas и xarray есть метки (индекс, координаты). Параметр ``align`` решает, что делать с метками. По умолчанию ``"strict"``: если ``obs`` и ``sim`` оба объекты pandas, их индексы должны совпадать (``Index.equals``, порядок учитывается); если оба ``DataArray``, должны совпадать координаты по тем измерениям, где они есть с обеих сторон. Иначе ``ValueError`` с первым расхождением и подсказкой. Сдвинутые по времени ряды больше не считаются молча:

.. testcode::

   obs_series = pd.Series(q_obs[:10], index=pd.date_range("2020-01-01", periods=10))
   sim_series = pd.Series(q_sim[:10], index=pd.date_range("2020-01-03", periods=10))
   try:
       hm.nse(obs_series, sim_series)
   except ValueError as exc:
       print(str(exc)[:60])

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   obs and sim are not aligned: obs has 10 labels (2020-01-01 0

``align="inner"`` оставляет общие метки в порядке ``obs`` и делает это до обработки пропусков. Число отброшенных строк (из ``obs`` и из ``sim`` вместе) записано в ``result.meta["n_dropped_by_align"]``:

.. testcode::

   result = hm.nse(obs_series, sim_series, align="inner")
   common = obs_series.index.intersection(sim_series.index)
   by_hand = float(hm.nse(obs_series[common], sim_series[common]))
   print(round(float(result), 4), round(by_hand, 4), result.meta["n_dropped_by_align"])

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   -6.3511 -6.3511 4

Дубликаты в индексе, пустое пересечение и входы без меток (numpy, polars, смешанные типы) при ``"inner"`` дают ``ValueError``. При ``"strict"`` входы разных типов и polars не проверяются, а дополнительные массивы (``dates``, ``gauge``, ``ref_date``) и веса сопоставляются по позиции. Для ансамбля (``sim`` как таблица с участниками в столбцах) сравниваются индексы строк. Параметр действует и в :func:`~hydrometrics.compute_grouped`.

Проверки и исключения
-----------------------

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 70 30

   * - Ситуация
     - Исключение
   * - Разные формы ``obs`` и ``sim``
     - ``ValueError``
   * - Форма веса не совпадает с ``obs``
     - ``ValueError``
   * - Отрицательный вес
     - ``ValueError``
   * - ``weight`` и ``sample_weight`` одновременно
     - ``TypeError``
   * - Неизвестное значение ``nan_policy`` или ``reduction``
     - ``ValueError``
   * - Вес у метрики без поддержки весов, ось у метрики без оси
     - ``NotImplementedError``
   * - Нечисловые значения (строки, ``None`` в массиве ``object``)
     - ``TypeError``
   * - Индексы pandas или координаты xarray не совпадают при ``align="strict"``; неизвестное значение ``align``
     - ``ValueError``
   * - Ось вне размерности массива
     - ``numpy.exceptions.AxisError``

.. testcode::

   for call in (
       lambda: hm.nse(q_obs, q_sim[:-1]),
       lambda: hm.nse(q_obs, q_sim, sample_weight=-np.ones_like(q_obs)),
       lambda: hm.nse(q_obs, q_sim, nan_policy="drop"),
       lambda: hm.spearman_r(q_obs, q_sim, sample_weight=np.ones_like(q_obs)),
   ):
       try:
           call()
       except Exception as exc:
           print(type(exc).__name__ + ":", exc)

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   ValueError: Shape mismatch: obs (1096,) != sim (1095,)
   ValueError: Sample weights must be non-negative
   ValueError: nan_policy must be one of ('propagate', 'omit', 'raise'), got 'drop'
   NotImplementedError: spearman_r does not support sample_weight

Пустой ряд и ряд из одного элемента у большинства метрик не вызывают исключений: результат NaN для метрик, которым нужна дисперсия или несколько пар. Исключение это ``ssigma`` без оси, которая при числе пар не больше ``m`` вызывает ``ValueError``.

Веса
------

Канонический аргумент ``sample_weight``; ``weight`` принимается как алиас. Вес нулевой означает, что пара не участвует в расчёте. Метрики без поддержки весов перечислены на их страницах и вызывают ``NotImplementedError``.

.. testcode::

   w = np.ones_like(q_obs)
   w[q_obs > 100] = 0.0  # drop the flood from the estimate
   print(round(float(hm.nse(q_obs, q_sim, sample_weight=w)), 4), round(float(hm.nse(q_obs[q_obs <= 100], q_sim[q_obs <= 100])), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.5742 0.5742

Результат с нулевыми весами совпадает с расчётом по оставшимся парам.

Возвращаемый объект
---------------------

Функция возвращает :class:`~hydrometrics.MetricResult` с полями ``value``, ``name``, ``direction``, ``bounds``, ``optimum``, ``parameters``, ``reference``, ``nan_info`` и ``meta``. ``float(result)`` извлекает число из скалярного результата, ``result.to_dict()`` собирает все поля в словарь.

.. testcode::

   result = hm.nse(q_obs, q_sim)
   print(result.name, result.direction, result.bounds)
   print(result.parameters)

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   Nash-Sutcliffe Efficiency maximize (-inf, 1.0)
   {'axis': None, 'nan_policy': 'omit', 'reduction': 'mean'}

Словарь ``to_dict`` содержит ``-inf`` в границах и массивы в параметрах, поэтому для записи в JSON его нужно предварительно преобразовать.
