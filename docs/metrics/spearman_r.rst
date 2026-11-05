.. _metric-spearman_r:

==================================
Ранговая корреляция Спирмена (ρ)
==================================

ρ это корреляция Пирсона между рангами наблюдённых и модельных значений :footcite:p:`spearman1904`. Она измеряет монотонную связь и не зависит от масштаба и формы связи.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.spearman_r(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.spearman_r`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \rho = \frac{\sum_i (R_i - \bar{R})(T_i - \bar{T})}{\sqrt{\sum_i (R_i - \bar{R})^2}\,\sqrt{\sum_i (T_i - \bar{T})^2}}

:math:`R_i` и :math:`T_i` ранги :math:`O_i` и :math:`S_i`; при совпадающих значениях берётся средний ранг. Расчёт выполняет ``scipy.stats.spearmanr`` отдельно для каждого среза вдоль оси.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Совпадает с классическим определением. Веса не поддерживаются: ``sample_weight`` вызывает ``NotImplementedError``. Пары с пропуском удаляются; при менее чем двух парах результат NaN.

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

Значение 1 означает строго одинаковый порядок значений, -1 противоположный. Для постоянного ряда результат NaN.

Интерпретация и критерии оценки
---------------------------------

Общепринятых градаций качества нет. Монотонная связь допускает любое смещение и любую нелинейную деформацию масштаба, поэтому высокий ρ не говорит о точности значений.

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
     - Не поддерживается: вызывает ``NotImplementedError``.
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
     - 0.7165
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN
   * - ``inf`` в ``obs``
     - 0.7123
   * - постоянный ``obs`` (нулевая дисперсия)
     - NaN (RuntimeWarning)
   * - ``obs`` и ``sim`` из одних нулей
     - NaN (RuntimeWarning)
   * - отрицательные значения (ряд минус его среднее)
     - 0.7162
   * - пустой ввод
     - NaN
   * - разная длина ``obs`` и ``sim``
     - ValueError

С ``nan_policy="omit"`` пары с пропуском удаляются; ``"propagate"`` возвращает NaN, ``"raise"`` вызывает ``ValueError``. Значение ``inf`` не считается пропуском и получает наибольший ранг, поэтому результат остаётся числом.

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
     - нет
     - ``axis``
     - да
     - да
   * - pandas
     - нет
     - ``axis``
     - да
     - да
   * - polars
     - нет
     - ``axis``
     - да
     - да
   * - xarray
     - нет
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

   result = hm.spearman_r(q_obs, q_sim)
   print(f"spearman_r = {float(result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   spearman_r = 0.408

Ранговые коэффициенты не зависят от монотонного преобразования: утроенный ряд даёт тот же результат, тогда как нелинейное преобразование меняет корреляцию Пирсона:

.. testcode::

   squared = q_obs ** 2
   print(round(float(hm.spearman_r(q_obs, squared)), 4), round(float(hm.pearson_r(q_obs, squared)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   1.0 0.9761

В примере с половодьем коэффициент заметно ниже корреляции Пирсона, потому что большая часть дней приходится на межень с шумом, и порядок значений там определяется шумом:

.. testcode::

   print(round(float(hm.spearman_r(q_obs, q_sim)), 3), round(float(hm.pearson_r(q_obs, q_sim)), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.408 0.981

По створам:

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   per_station = hm.spearman_r(q_obs_st, q_sim_st, axis=0, reduction="none")
   print(np.round(per_station.value, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.408 0.408 0.408]

По водным годам:

.. testcode::

   import pandas as pd

   df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
   # Водный год начинается 1 октября и назван по году окончания
   df["water_year"] = df.index.year + (df.index.month >= 10)

.. testcode::

   by_year = hm.compute_grouped(hm.spearman_r, df, "q_obs", "q_sim", group_by="water_year")
   for (water_year,), value in by_year:
       print(int(water_year), round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2011 0.433
   2012 0.443
   2013 0.351

На xarray ось задаётся именем измерения, а координаты створов сохраняются в результате:

.. testcode::

   import xarray as xr

   coords = {"time": dates, "station": ["upper", "middle", "lower"]}
   obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
   sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
   by_station = hm.spearman_r(obs_da, sim_da, dim="time").value
   print(by_station.round(3).to_series().to_dict())

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   {'upper': 0.408, 'middle': 0.408, 'lower': 0.408}

Особенности применения в гидрологии
-------------------------------------

Ранговая корреляция не замечает систематического занижения пиков и объёма, поэтому её используют для проверки порядка значений (например, ранжирования створов или лет по водности), а не для оценки точности расхода. В рядах суточного стока с длинной меженью ρ определяется порядком шумовых значений межени, как в примере выше.

Связанные метрики
-------------------

- :ref:`metric-kendall_tau`
- :ref:`metric-pearson_r`
- :ref:`metric-kge_2012`

Литература
------------

.. footbibliography::
