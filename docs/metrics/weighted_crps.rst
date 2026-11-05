.. _metric-weighted_crps:

==================================
Взвешенная CRPS (по наблюдениям)
==================================

Среднее значений :ref:`metric-crps` по срокам, взвешенное функцией от наблюдения. Функция ``weight_func`` задаёт, какие наблюдения важнее, например вес :math:`1/y` усиливает вклад малых расходов.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.weighted_crps(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict", weight_func=None)

Запись в справочнике API: :func:`hydrometrics.weighted_crps`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{wCRPS} = \frac{\sum_{t} u_t\,\mathrm{CRPS}_t}{\sum_{t} u_t}, \qquad u_t = w_t\cdot g(O_t)

:math:`\mathrm{CRPS}_t` значение :ref:`metric-crps` для срока :math:`t` (классическая оценка с делителем :math:`m^2`), :math:`g` функция ``weight_func`` (по умолчанию 1), :math:`w_t` вес ``sample_weight``. Усреднение идёт по оси ``axis``.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Взвешиваются наблюдения, а не подынтегральное выражение. Это не пороговая и не квантильно-взвешенная CRPS Gneiting и Ranjan :footcite:p:`gneiting2011`, где вес задаётся на оси значений величины внутри интеграла. Параметра ``fair`` у функции нет.

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

Единица измерения совпадает с единицей величины. Значение 0 достигается при совпадении прогноза с наблюдением во всех сроках с ненулевым весом. Если сумма весов равна нулю, результат NaN.

Интерпретация и критерии оценки
---------------------------------

Общепринятых градаций нет. Значения с разной ``weight_func`` несопоставимы, потому что веса нормируются на свою сумму и меняют долю сроков.

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
     - Детерминированный прогноз той же формы, что ``obs``, или ансамбль с дополнительным последним измерением, ``(n, m)``.
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
   * - ``weight_func``
     - функция | None
     - ``None``
     - Функция от массива ``obs``, возвращающая массив весов той же формы. Умножается на ``sample_weight``, если он задан.

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
     - 3.714
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN
   * - ``inf`` в ``obs``
     - inf
   * - постоянный ``obs`` (нулевая дисперсия)
     - 12.03
   * - ``obs`` и ``sim`` из одних нулей
     - 0
   * - пустой ввод
     - NaN
   * - разная длина ``obs`` и ``sim``
     - ValueError

При умолчании ``nan_policy="omit"`` пары с пропуском в ``obs`` или ``sim`` удаляются целиком, в том числе при заданной оси. ``"propagate"`` возвращает NaN, если в ряду (или в срезе вдоль оси) есть пропуск, ``"raise"`` вызывает ``ValueError``. Значение ``inf`` пропуском не считается; результат для него показан в таблице.

Ансамбль без пропусков проходит без ограничений. Член ансамбля с NaN исключается из расчёта срока, число действительных членов считается отдельно для каждого срока.

Если ``weight_func`` возвращает нули или отрицательные значения, проверки нет; отрицательные веса приводят к бессмысленному результату.

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

   # Ансамбль из 20 членов: разброс растёт с расходом
   ens_rng = np.random.default_rng(7)
   members = 1.05 * q_obs[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.15 * q_obs[:, None])

.. testcode::

   plain = hm.crps(q_obs, members)
   low_flow = hm.weighted_crps(q_obs, members, weight_func=lambda y: 1 / y)
   print(f"crps = {float(plain):.3f}, weighted (1/y) = {float(low_flow):.3f} m3/s")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   crps = 2.060, weighted (1/y) = 1.320 m3/s

Без ``weight_func`` результат совпадает с :func:`~hydrometrics.crps`; метрика с весом вида :math:`y` усиливает вклад половодья:

.. testcode::

   print(round(float(hm.weighted_crps(q_obs, members)), 3), round(float(hm.weighted_crps(q_obs, members, weight_func=lambda y: y)), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2.06 5.598

По сезонам для весов :math:`1/y`:

.. testcode::

   # Сезон по месяцу: половодье с апреля по июнь, остальные месяцы межень
   month = dates.astype("datetime64[M]").astype(int) % 12 + 1
   season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")

.. testcode::

   by_season = hm.compute_grouped(hm.weighted_crps, None, q_obs, members, group_by={"season": season}, weight_func=lambda y: 1 / y)
   for (label,), value in by_season:
       print(label, round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   low_flow 1.203
   flood 2.048

Детерминированный прогноз: метрика равна взвешенной средней абсолютной ошибке.

.. testcode::

   print(round(float(hm.weighted_crps(q_obs, q_sim)), 3), round(float(hm.mae(q_obs, q_sim)), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   7.667 7.667

Особенности применения в гидрологии
-------------------------------------

Вес :math:`1/y` — простой способ показать качество на межени, где обычная CRPS почти не заметна из-за малых абсолютных значений. Но это взвешивание дней, а не порога: ансамбль, плохо описывающий редкие маловодные дни, при большом числе обычных дней получает за них малый суммарный вес.

Для выбора порога по обеспеченности используйте пороговую CRPS из литературы :footcite:p:`gneiting2011`, которой в библиотеке нет.

Связанные метрики
-------------------

- :ref:`metric-crps`
- :ref:`metric-crpss`
- :ref:`metric-mae`

Литература
------------

.. footbibliography::
