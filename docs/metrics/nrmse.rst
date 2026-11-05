.. _metric-nrmse:

===================================================
Нормированная среднеквадратическая ошибка (NRMSE)
===================================================

NRMSE это :ref:`metric-rmse`, делённая на характеристику наблюдений: среднее, стандартное отклонение, размах или межквартильный размах. Результат безразмерный.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.nrmse(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict", normalization="mean")

Запись в справочнике API: :func:`hydrometrics.nrmse`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{NRMSE} = \frac{\mathrm{RMSE}}{N}, \qquad N \in \{\bar{O},\ \sigma_O,\ O_{\max}-O_{\min},\ Q_{75}-Q_{25}\}

:math:`\bar{O}` среднее наблюдений (взвешенное при заданных весах), :math:`\sigma_O` стандартное отклонение с ``ddof=1``, :math:`Q_{75}-Q_{25}` межквартильный размах. Нормировка выбирается аргументом ``normalization``; по умолчанию ``\"mean\"``.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

В литературе встречаются все четыре нормировки, единого определения NRMSE нет, поэтому значения нужно сопровождать указанием нормировки. Размах и межквартильный размах считаются по ``obs`` без учёта весов; среднее и стандартное отклонение взвешиваются. Если нормировка равна нулю (например, нулевое среднее), результат NaN. При отрицательном среднем нормировка ``"mean"`` даёт отрицательное значение.

Диапазон значений и оптимум
-----------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table

   * - Диапазон
     - Оптимум
     - Направление
   * - [0, +∞)
     - 0
     - меньше лучше

Значение 0 означает полное совпадение. Верхней границы нет. Для величины с нулевым средним нормировка ``"mean"`` не определена.

Интерпретация и критерии оценки
---------------------------------

Градаций для NRMSE нет, потому что значение зависит от выбранной нормировки. Для нормировки на стандартное отклонение (``"std"``) смысл совпадает с :ref:`metric-rsr`, для которого Moriasi et al. :footcite:p:`moriasi2007` приводят градации (месячный шаг).

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
   * - ``normalization``
     - str
     - ``"mean"``
     - ``"mean"``, ``"std"``, ``"range"`` или ``"iqr"``. Другое значение вызывает ``ValueError``.

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
     - 0.1426
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN (RuntimeWarning)
   * - ``inf`` в ``obs``
     - NaN
   * - постоянный ``obs`` (нулевая дисперсия)
     - 0.9662
   * - ``obs`` и ``sim`` из одних нулей
     - NaN
   * - отрицательные значения (ряд минус его среднее)
     - 7.018e+14
   * - пустой ввод
     - NaN (RuntimeWarning)
   * - разная длина ``obs`` и ``sim``
     - ValueError

При умолчании ``nan_policy="omit"`` пары с пропуском в ``obs`` или ``sim`` удаляются целиком, в том числе при заданной оси. ``"propagate"`` возвращает NaN, если в ряду (или в срезе вдоль оси) есть пропуск, ``"raise"`` вызывает ``ValueError``. Значение ``inf`` пропуском не считается; результат для него показан в таблице.

Если среднее наблюдений равно нулю лишь с точностью до округления, знаменатель не равен нулю точно, и результат огромен по модулю (в таблице строка с центрированным рядом). Для рядов с нулевым средним метрика не применяется.

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

   result = hm.nrmse(q_obs, q_sim)
   print(f"nrmse = {float(result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   nrmse = 0.321

Выбор нормировки меняет значение на порядок. При ``normalization="std"`` результат совпадает с :ref:`metric-rsr`:

.. testcode::

   for mode in ("mean", "std", "range", "iqr"):
       print(mode, round(float(hm.nrmse(q_obs, q_sim, normalization=mode)), 4))
   print(round(float(hm.rsr(q_obs, q_sim)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   mean 0.3208
   std 0.215
   range 0.0458
   iqr 1.6799
   0.215

По створам:

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   per_station = hm.nrmse(q_obs_st, q_sim_st, axis=0, reduction="none")
   print(np.round(per_station.value, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.321 0.368 0.264]

По водным годам:

.. testcode::

   import pandas as pd

   df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
   # Водный год начинается 1 октября и назван по году окончания
   df["water_year"] = df.index.year + (df.index.month >= 10)

.. testcode::

   by_year = hm.compute_grouped(hm.nrmse, df, "q_obs", "q_sim", group_by="water_year")
   for (water_year,), value in by_year:
       print(int(water_year), round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2011 0.333
   2012 0.311
   2013 0.318

На xarray ось задаётся именем измерения, а координаты створов сохраняются в результате:

.. testcode::

   import xarray as xr

   coords = {"time": dates, "station": ["upper", "middle", "lower"]}
   obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
   sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
   by_station = hm.nrmse(obs_da, sim_da, dim="time").value
   print(by_station.round(3).to_series().to_dict())

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   {'upper': 0.321, 'middle': 0.368, 'lower': 0.264}

Особенности применения в гидрологии
-------------------------------------

Нормировка на среднее удобна для сравнения створов, но на реке с большим половодьем среднее мало отличается от межени, а RMSE определяется пиком; нормировка на стандартное отклонение (то есть RSR) учитывает изменчивость и менее зависит от того, какую долю года занимает межень.

Нормировка на размах определяется одним экстремумом ряда и поэтому нестабильна при смене периода наблюдений.

Связанные метрики
-------------------

- :ref:`metric-rmse`
- :ref:`metric-rsr`
- :ref:`metric-pbias`
- :ref:`metric-nse`

Литература
------------

.. footbibliography::
