.. _metric-crpss:

================================
Индекс мастерства CRPS (CRPSS)
================================

CRPSS показывает, насколько прогноз лучше опорного по :ref:`metric-crps`: единица минус отношение средней CRPS прогноза к средней CRPS опорного прогноза. Положительное значение означает выигрыш относительно опоры.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.crpss(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict", ref_forecast=None)

Запись в справочнике API: :func:`hydrometrics.crpss`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{CRPSS} = 1 - \frac{\overline{\mathrm{CRPS}}}{\overline{\mathrm{CRPS}}_{\mathrm{ref}}}

Черта обозначает (взвешенное) среднее по оси ``axis``; отношение берётся от средних, а не среднее от отношений. :math:`\mathrm{CRPS}` считается классической оценкой. Без ``ref_forecast`` опорой служит постоянный прогноз, равный среднему наблюдений вдоль оси.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Опорный прогноз по умолчанию это среднее выборки, по которой оценивается прогноз, то есть оценка получена на тех же данных. Параметра ``fair`` у функции нет. ``ref_forecast`` может быть детерминированным массивом формы ``obs`` или ансамблем ``(n, m)``; его CRPS считается так же, как для прогноза.

Диапазон значений и оптимум
-----------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table

   * - Диапазон
     - Оптимум
     - Направление
   * - (-∞, 1]
     - 1
     - больше лучше

Значение 1 достигается при нулевой CRPS, значение 0 при равенстве опоре, отрицательное при худшем результате. Если CRPS опорного прогноза равна нулю, результат NaN.

Интерпретация и критерии оценки
---------------------------------

Общепринятых порогов нет: значение определяется выбором опоры, поэтому его нужно публиковать вместе с описанием опорного прогноза.

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
     - Детерминированный прогноз той же формы, что ``obs``, или ансамбль ``(n, m)``.
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
   * - ``ref_forecast``
     - массив | None
     - ``None``
     - Опорный прогноз: массив формы ``obs`` или ансамбль ``(n, m)``, например климатический гидрограф. Без него используется среднее наблюдений.

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
     - 0.75
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
   * - пустой ввод
     - NaN (RuntimeWarning)
   * - разная длина ``obs`` и ``sim``
     - ValueError

При умолчании ``nan_policy="omit"`` пары с пропуском в ``obs`` или ``sim`` удаляются целиком, в том числе при заданной оси. ``"propagate"`` возвращает NaN, если в ряду (или в срезе вдоль оси) есть пропуск, ``"raise"`` вызывает ``ValueError``. Значение ``inf`` пропуском не считается; результат для него показан в таблице.

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

   skill = hm.crpss(q_obs, members)
   print(f"CRPSS (reference: mean of the observations) = {float(skill):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   CRPSS (reference: mean of the observations) = 0.934

Умолчание слабое: опорный прогноз это постоянное среднее наблюдений, а не климатический ход. Честнее взять среднемноголетний гидрограф:

.. testcode::

   climatology = hm.mean_annual_hydrograph(q_obs, dates)[doy]
   print(round(float(hm.crpss(q_obs, members, ref_forecast=climatology)), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.038

Для детерминированного прогноза с умолчанием ``crpss`` равна :ref:`metric-modified_nse`: обе строятся как единица минус отношение средних абсолютных ошибок.

.. testcode::

   print(round(float(hm.crpss(q_obs, q_sim)), 4), round(float(hm.modified_nse(q_obs, q_sim)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.7538 0.7538

По сезонам умолчание опирается на среднее каждого сезона:

.. testcode::

   # Сезон по месяцу: половодье с апреля по июнь, остальные месяцы межень
   month = dates.astype("datetime64[M]").astype(int) % 12 + 1
   season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")

.. testcode::

   by_season = hm.compute_grouped(hm.crpss, None, q_obs, members, group_by={"season": season})
   for (label,), value in by_season:
       print(label, round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   low_flow 0.55
   flood 0.938

Особенности применения в гидрологии
-------------------------------------

С опорой «среднее за период» любая модель, воспроизводящая сезонный ход, получает высокий CRPSS, поскольку сезонность в этой опоре отсутствует: в примере выигрыш относительно среднемноголетнего гидрографа заметно меньше. Для рек с выраженным режимом опорой должен служить гидрограф климатического года.

Связанные метрики
-------------------

- :ref:`metric-crps`
- :ref:`metric-weighted_crps`
- :ref:`metric-modified_nse`
- :ref:`metric-nse`

Литература
------------

.. footbibliography::
