.. _metric-pearson_r:

====================================
Коэффициент корреляции Пирсона (r)
====================================

Коэффициент измеряет линейную связь между наблюдённым и модельным рядами: совпадение по фазе и форме, независимо от смещения и масштаба. Он служит компонентой :ref:`metric-kge_2012`.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.pearson_r(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.pearson_r`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   r = \frac{\sum_{i} w_i\,(O_i-\bar{O})(S_i-\bar{S})}{\sqrt{\sum_{i} w_i\,(O_i-\bar{O})^2}\,\sqrt{\sum_{i} w_i\,(S_i-\bar{S})^2}}

:math:`\bar{O}` и :math:`\bar{S}` средние наблюдённого и модельного рядов (взвешенные при заданных весах), :math:`w_i` вес. В коде ковариация и дисперсии нормируются на ``n - 1`` (при весах на сумму весов минус 1); при отсутствии весов это совпадает с формулой выше.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Совпадает с классическим определением. Веса расширяют его до взвешенной корреляции.

Диапазон значений и оптимум
-----------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table

   * - Диапазон
     - Оптимум
     - Направление
   * - [-1, 1]
     - 1
     - больше лучше

Значение 1 означает точную линейную зависимость с положительным наклоном, -1 с отрицательным. Для постоянного ряда корреляция не определена, результат NaN.

Интерпретация и критерии оценки
---------------------------------

Общепринятых градаций качества нет. Высокая корреляция не означает точной модели: она допускает любое смещение и любой масштаб (пример выше).

Параметры
-----------

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 18 16 14 52

   * - Имя
     - Тип
     - По умолчанию
     - Описание
   * - ``obs``
     - массив
     - обязателен
     - Наблюдённые значения.
   * - ``sim``
     - массив
     - обязателен
     - Модельные или прогнозные значения той же формы.
   * - ``axis``
     - int | None
     - ``None``
     - Ось суммирования; ``None`` объединяет все значения. На xarray вместо неё используется ``dim`` (или ``axis``, он переводится в имя измерения).
   * - ``nan_policy``
     - str
     - ``"omit"``
     - ``"omit"`` удаляет пары с пропуском, ``"propagate"`` даёт NaN, ``"raise"`` вызывает ``ValueError``; см. раздел о пропусках ниже и :doc:`/user_guide/missing_values`.
   * - ``sample_weight``
     - массив | None
     - ``None``
     - Веса той же формы, что ``obs``, неотрицательные; NaN делает пару недействительной. ``weight`` принимается как алиас, обе формы сразу вызывают ``TypeError``.
   * - ``reduction``
     - str | None
     - ``None``
     - Свёртка результата с ``ndim > 0``: ``"mean"``, ``"sum"`` или ``"none"``. По умолчанию при заданной оси возвращается массив по оставшимся измерениям, без оси среднее.
   * - ``align``
     - str
     - ``"strict"``
     - ``"strict"`` требует равных индексов pandas и координат xarray, ``"inner"`` оставляет общие метки в порядке ``obs``. Без меток ``"inner"`` вызывает ``ValueError``.

Возвращаемое значение
-----------------------

Функция возвращает :class:`~hydrometrics.MetricResult`; значение лежит в поле ``value``. В таблице указан фактический тип ``value`` при одномерном вводе и при вычислении по оси.

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 15 35 50

   * - Бэкенд
     - Одномерный ввод
     - По оси, ввод формы (1096, 3)
   * - numpy
     - numpy.float64
     - ``axis=0``: numpy.ndarray (3,)
   * - pandas
     - numpy.float64
     - ``axis=0``: numpy.ndarray (3,)
   * - polars
     - numpy.float64
     - ``axis=0``: numpy.ndarray (3,)
   * - xarray
     - numpy.float64
     - ``dim="time"``: xarray.DataArray

Пропуски и особые случаи
--------------------------

Результаты получены запуском на numpy при сборке этой страницы. Ряд содержит 1096 суточных значений. Пометка ``RuntimeWarning`` означает, что предупреждение numpy выходит наружу.

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 60 40

   * - Случай
     - Результат
   * - NaN в одной паре, ``nan_policy="omit"`` (умолчание)
     - 0.9788
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN (RuntimeWarning)
   * - ``inf`` в ``obs``
     - NaN (RuntimeWarning)
   * - постоянный ``obs`` (нулевая дисперсия)
     - NaN
   * - ``obs`` и ``sim`` из одних нулей
     - NaN
   * - отрицательные значения (ряд минус его среднее)
     - 0.9787
   * - пустой ввод
     - NaN (RuntimeWarning)
   * - разная длина ``obs`` и ``sim``
     - ValueError

При умолчании ``nan_policy="omit"`` пары с пропуском в ``obs`` или ``sim`` удаляются целиком, в том числе при заданной оси. ``"propagate"`` возвращает NaN, если в ряду (или в срезе вдоль оси) есть пропуск, ``"raise"`` вызывает ``ValueError``. Значение ``inf`` пропуском не считается; результат для него показан в таблице.

Постоянный ряд и один элемент дают NaN.

Поддержка бэкендов
--------------------

.. list-table::
   :header-rows: 1
   :class: hm-table

   * - Бэкенд
     - Веса
     - Ось
     - ``nan_policy``
     - ``reduction``
   * - numpy
     - ``sample_weight``, ``weight``
     - ``axis``
     - да
     - да
   * - pandas
     - ``sample_weight``, ``weight``
     - ``axis``
     - да
     - да
   * - polars
     - ``sample_weight``, ``weight``
     - ``axis``
     - да
     - да
   * - xarray
     - ``sample_weight``, ``weight``
     - ``dim``, ``axis``
     - да
     - да

Индексы pandas и координаты xarray проверяются параметром ``align``: по умолчанию несовпадающие метки дают ``ValueError``, ``align="inner"`` оставляет общие (см. :doc:`/user_guide/input_data`).

Примеры
---------

Суточный гидрограф за три водных года с половодьем и меженью, расходы в м³/с.

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

   result = hm.pearson_r(q_obs, q_sim)
   print(f"pearson_r = {float(result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   pearson_r = 0.981

Корреляция не замечает смещения и масштаба: ряд, завышенный втрое, коррелирует с наблюдениями так же, как исходный.

.. testcode::

   print(round(float(hm.pearson_r(q_obs, q_sim)), 4), round(float(hm.pearson_r(q_obs, 3 * q_sim)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.9815 0.9815

С :ref:`metric-nse` её связывает разложение: NSE = 2αr − α² − β_n², где α отношение стандартных отклонений, β_n смещение в долях стандартного отклонения наблюдений :footcite:p:`gupta2009`. Проверка:

.. testcode::

   r = np.corrcoef(q_obs, q_sim)[0, 1]
   alpha = q_sim.std() / q_obs.std()
   beta_n = (q_sim.mean() - q_obs.mean()) / q_obs.std()
   print(round(2 * alpha * r - alpha ** 2 - beta_n ** 2, 6), round(float(hm.nse(q_obs, q_sim)), 6))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.95375 0.95375

По створам:

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   per_station = hm.pearson_r(q_obs_st, q_sim_st, axis=0, reduction="none")
   print(np.round(per_station.value, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.981 0.981 0.981]

По водным годам:

.. testcode::

   import pandas as pd

   df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
   # Водный год начинается 1 октября и назван по году окончания
   df["water_year"] = df.index.year + (df.index.month >= 10)

.. testcode::

   by_year = hm.compute_grouped(hm.pearson_r, df, "q_obs", "q_sim", group_by="water_year")
   for (water_year,), value in by_year:
       print(int(water_year), round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2011 0.98
   2012 0.983
   2013 0.982

На xarray ось задаётся именем измерения, а координаты створов сохраняются в результате:

.. testcode::

   import xarray as xr

   coords = {"time": dates, "station": ["upper", "middle", "lower"]}
   obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
   sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
   by_station = hm.pearson_r(obs_da, sim_da, dim="time").value
   print(by_station.round(3).to_series().to_dict())

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   {'upper': 0.981, 'middle': 0.981, 'lower': 0.981}

Особенности применения в гидрологии
-------------------------------------

Корреляция чувствительна к выбросам и, как все квадратичные метрики, определяется пиками половодья: при резком сезонном ходе она высока почти для любой модели, воспроизводящей сезонность. Автокорреляция суточного стока делает число независимых наблюдений намного меньше длины ряда, поэтому проверка значимости, рассчитанная на независимые наблюдения, к такому ряду неприменима без поправки.

Дополняйте её метриками объёма и амплитуды: :ref:`metric-pbias`, :ref:`metric-alpha_component`.

Связанные метрики
-------------------

- :ref:`metric-spearman_r`
- :ref:`metric-kendall_tau`
- :ref:`metric-r2`
- :ref:`metric-r_component`
- :ref:`metric-kge_2012`

Литература
------------

.. footbibliography::
