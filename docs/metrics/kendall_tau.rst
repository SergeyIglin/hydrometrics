.. _metric-kendall_tau:

==================================
Ранговая корреляция Кендалла (τ)
==================================

τ оценивает согласованность порядка: долю пар наблюдений, в которых наблюдённый и модельный ряды упорядочены одинаково, за вычетом доли пар, упорядоченных противоположно :footcite:p:`kendall1938`.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.kendall_tau(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.kendall_tau`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \tau = \frac{n_c - n_d}{\sqrt{(n_0 - n_1)(n_0 - n_2)}}

:math:`n_c` и :math:`n_d` числа согласованных и несогласованных пар, :math:`n_0 = n(n-1)/2`, :math:`n_1` и :math:`n_2` поправки на совпадающие значения в каждом ряду. Это вариант τ-b; расчёт выполняет ``scipy.stats.kendalltau`` с умолчанием ``variant=\"b\"`` для каждого среза вдоль оси.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Совпадает с классическим определением τ-b. Веса не поддерживаются. Пары с пропуском удаляются; при менее чем двух парах результат NaN.

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

Значение 1 означает полностью согласованный порядок, -1 противоположный. Значения τ обычно меньше значений ρ для тех же данных, потому что шкалы различаются; прямо сравнивать их нельзя. Для постоянного ряда результат NaN.

Интерпретация и критерии оценки
---------------------------------

Общепринятых градаций качества нет. Для интерпретации используется вероятностный смысл: :math:`(1+\tau)/2` при отсутствии совпадающих значений равно вероятности того, что случайно взятая пара упорядочена в обоих рядах одинаково.

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
     - 0.5506
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN
   * - ``inf`` в ``obs``
     - 0.548
   * - постоянный ``obs`` (нулевая дисперсия)
     - NaN
   * - ``obs`` и ``sim`` из одних нулей
     - NaN
   * - отрицательные значения (ряд минус его среднее)
     - 0.5502
   * - пустой ввод
     - NaN
   * - разная длина ``obs`` и ``sim``
     - ValueError

С ``nan_policy="omit"`` пары с пропуском удаляются; ``"propagate"`` возвращает NaN, ``"raise"`` вызывает ``ValueError``. Значение ``inf`` получает наибольший ранг.

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

   result = hm.kendall_tau(q_obs, q_sim)
   print(f"kendall_tau = {float(result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   kendall_tau = 0.291

Ранговые коэффициенты не зависят от монотонного преобразования: утроенный ряд даёт тот же результат, тогда как нелинейное преобразование меняет корреляцию Пирсона:

.. testcode::

   squared = q_obs ** 2
   print(round(float(hm.kendall_tau(q_obs, squared)), 4), round(float(hm.pearson_r(q_obs, squared)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   1.0 0.9761

В примере с половодьем коэффициент заметно ниже корреляции Пирсона, потому что большая часть дней приходится на межень с шумом, и порядок значений там определяется шумом:

.. testcode::

   print(round(float(hm.kendall_tau(q_obs, q_sim)), 3), round(float(hm.pearson_r(q_obs, q_sim)), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.291 0.981

По створам:

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   per_station = hm.kendall_tau(q_obs_st, q_sim_st, axis=0, reduction="none")
   print(np.round(per_station.value, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.291 0.291 0.291]

По водным годам:

.. testcode::

   import pandas as pd

   df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
   # Водный год начинается 1 октября и назван по году окончания
   df["water_year"] = df.index.year + (df.index.month >= 10)

.. testcode::

   by_year = hm.compute_grouped(hm.kendall_tau, df, "q_obs", "q_sim", group_by="water_year")
   for (water_year,), value in by_year:
       print(int(water_year), round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2011 0.311
   2012 0.317
   2013 0.248

На xarray ось задаётся именем измерения, а координаты створов сохраняются в результате:

.. testcode::

   import xarray as xr

   coords = {"time": dates, "station": ["upper", "middle", "lower"]}
   obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
   sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
   by_station = hm.kendall_tau(obs_da, sim_da, dim="time").value
   print(by_station.round(3).to_series().to_dict())

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   {'upper': 0.291, 'middle': 0.291, 'lower': 0.291}

Особенности применения в гидрологии
-------------------------------------

Как и :ref:`metric-spearman_r`, τ оценивает порядок, а не величину расхода. Она менее чувствительна к отдельным выбросам, чем ρ, но ряд суточного стока с множеством близких значений межени даёт много поправок на совпадения.

Связанные метрики
-------------------

- :ref:`metric-spearman_r`
- :ref:`metric-pearson_r`

Литература
------------

.. footbibliography::
