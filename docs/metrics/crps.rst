.. _metric-crps:

=======================================================
Непрерывная ранжированная вероятностная оценка (CRPS)
=======================================================

CRPS измеряет расстояние между прогнозным распределением и наблюдением в единицах самой величины, для расхода воды в м³/с. Для ансамбля по умолчанию используется классическая оценка, ``fair=True`` включает fair-оценку; для детерминированного прогноза метрика равна средней абсолютной ошибке.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.crps(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.crps`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{CRPS}_t = \frac{1}{m}\sum_{j=1}^{m}\left|X_{t,j} - O_t\right| - \frac{1}{2}\cdot\frac{2}{m(m-1)}\sum_{j<k}\left|X_{t,j} - X_{t,k}\right|

.. math::

   \mathrm{CRPS} = \frac{1}{n}\sum_{t=1}^{n}\mathrm{CRPS}_t

:math:`O_t` наблюдение за срок :math:`t`, :math:`X_{t,j}` член ансамбля :math:`j` из :math:`m`, :math:`n` число сроков. Усреднение по членам идёт по последней оси, по срокам выполняет ``reduction=\"mean\"``. Если ``sim`` имеет форму ``obs``, формула заменяется на :math:`\frac{1}{n}\sum|S_t-O_t|`.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Классическая ансамблевая оценка усредняет разброс по всем :math:`m^2` парам с нормировкой :math:`1/(2m^2)`. Она используется по умолчанию. Параметр ``fair=True`` делит сумму по упорядоченным парам на :math:`2m(m-1)`: это fair CRPS :footcite:p:`ferro2014`. До исправления fair-вариант был единственным и применялся без возможности выбора, поэтому значения для ансамбля из прежних версий больше, чем у ``fair=True``, не равны новым умолчаниям (см. ``CHANGELOG.md``).

Интегральное определение и его ансамблевая форма обсуждаются у Hersbach :footcite:p:`hersbach2000` и Gneiting & Raftery :footcite:p:`gneiting2007`. Строка ``formula`` в метаданных результата содержит интегральную запись, а не реализованную оценку.

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

Единица измерения совпадает с единицей величины. Обе оценки неотрицательны: по неравенству треугольника :math:`|X_j-X_k|\le|X_j-o|+|X_k-o|` сумма по парам не превышает :math:`2(m-1)\sum_j|X_j-o|`, поэтому член разброса не больше среднего модуля ошибки членов. Поэтому ``bounds=(0, None)`` верны и при ``fair=False``, и при ``fair=True``. Значение 0 достигается не только при идеальном прогнозе: для двух членов, охватывающих наблюдение, fair-оценка равна нулю при любом разбросе.

Интерпретация и критерии оценки
---------------------------------

Общепринятых порогов нет: значение зависит от масштаба реки, поэтому между створами его напрямую не сравнивают. Для сопоставления используйте :ref:`metric-crpss` с явно заданным опорным прогнозом.

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
     - Ось ``obs``, по которой усредняются оценки отдельных наблюдений; ``None`` усредняет по всем. Ансамбль всегда на последней оси ``sim``.
   * - ``nan_policy``
     - str
     - ``"omit"``
     - ``"omit"`` удаляет пары с пропуском, ``"propagate"`` даёт NaN, ``"raise"`` вызывает ``ValueError``; см. раздел о пропусках ниже и :doc:`/user_guide/missing_values`.
   * - ``sample_weight``
     - массив | None
     - ``None``
     - Веса наблюдений той же формы, что ``obs``; действуют и для детерминированного прогноза, и для ансамбля. ``weight`` принимается как алиас.
   * - ``reduction``
     - str | None
     - ``None``
     - Свёртка результата с ``ndim > 0``: ``"mean"``, ``"sum"`` или ``"none"``. По умолчанию при заданной оси возвращается массив по оставшимся измерениям, без оси среднее.
   * - ``align``
     - str
     - ``"strict"``
     - ``"strict"`` требует равных индексов pandas и координат xarray, ``"inner"`` оставляет общие метки в порядке ``obs``. Без меток ``"inner"`` вызывает ``ValueError``.
   * - ``fair``
     - bool
     - ``False``
     - Только для ансамбля: ``False`` классическая оценка, ``True`` fair-оценка (делитель :math:`m(m-1)`).

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

Таблица относится к детерминированному вводу. Для ансамбля ``obs`` формы ``(n,)`` и ``sim`` формы ``(n, m)`` на всех бэкендах возвращается скаляр; значения по срокам даёт ``reduction="none"`` без оси.

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
     - NaN (RuntimeWarning)
   * - ``inf`` в ``obs``
     - inf
   * - постоянный ``obs`` (нулевая дисперсия)
     - 12.03
   * - ``obs`` и ``sim`` из одних нулей
     - 0
   * - пустой ввод
     - NaN (RuntimeWarning)
   * - разная длина ``obs`` и ``sim``
     - ValueError

Пропуск в наблюдении исключает срок целиком; пропуск у отдельных членов ансамбля исключает только эти члены, число членов в формуле равно числу действительных. ``"propagate"`` возвращает NaN при любом пропуске, ``"raise"`` вызывает ``ValueError`` (в том числе для членов ансамбля).

Ансамбль из одного члена в виде ``(n, 1)`` считается как средняя абсолютная ошибка.

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

Ансамбль из 20 членов: разброс растёт вместе с расходом, а центр смещён вверх на 5 %.

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

   ens_rng = np.random.default_rng(7)
   members = 1.05 * q_obs[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.15 * q_obs[:, None])
   classic = float(hm.crps(q_obs, members))
   fair = float(hm.crps(q_obs, members, fair=True))
   print(members.shape)
   print(f"classic = {classic:.3f}  fair = {fair:.3f} m3/s")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   (1096, 20)
   classic = 2.060  fair = 1.855 m3/s

Независимый пересчёт классической оценки по определению:

.. testcode::

   m = members.shape[1]
   term_obs = np.abs(members - q_obs[:, None]).mean(axis=1)
   spread_sum = np.abs(members[:, :, None] - members[:, None, :]).sum(axis=(1, 2))
   by_hand = (term_obs - spread_sum / (2 * m * m)).mean()
   print(round(by_hand, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2.06

Без ансамблевого измерения ``crps`` сводится к средней абсолютной ошибке:

.. testcode::

   deterministic = members.mean(axis=1)
   print(round(float(hm.crps(q_obs, deterministic)), 3), round(float(hm.mae(q_obs, deterministic)), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   1.974 1.974

Пропуски в наблюдениях: сроки с пропуском исключаются, ``nan_info`` сообщает их число.

.. testcode::

   q_obs_gap = q_obs.copy()
   q_obs_gap[100:130] = np.nan  # месяц без наблюдений
   gap = hm.crps(q_obs_gap, members)
   print(round(float(gap), 3), gap.nan_info["n_nan_removed"])

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2.083 30

По сезонам: для ансамблей :func:`~hydrometrics.compute_grouped` режет массивы по первой оси, поэтому ``members`` передаётся целиком.

.. testcode::

   month = dates.astype("datetime64[M]").astype(int) % 12 + 1
   season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")
   by_season = hm.compute_grouped(hm.crps, None, q_obs, members, group_by={"season": season})
   for (name,), value in by_season:
       print(name, round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   low_flow 1.227
   flood 4.571

Значения по срокам получаются при ``reduction="none"`` без оси:

.. testcode::

   per_time = hm.crps(q_obs, members, reduction="none").value
   print(per_time.shape, round(float(per_time.max()), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   (1096,) 21.855

Особенности применения в гидрологии
-------------------------------------

Метрика зависит от размера ансамбля через оценку разброса. Fair-вариант предназначен для сравнения ансамблей разного размера :footcite:p:`ferro2014`; опубликованные значения, полученные другой оценкой, напрямую с результатом ``crps`` сравнивать нельзя.

CRPS в абсолютных единицах определяется периодами больших расходов: в половодье и расход, и разброс выше, поэтому значение за апрель–июнь больше, чем за остальные месяцы. Это само по себе не означает, что в половодье ансамбль хуже; для такого вывода нормируйте на опорный прогноз с помощью :ref:`metric-crpss`.

Связанные метрики
-------------------

- :ref:`metric-crpss`
- :ref:`metric-weighted_crps`
- :ref:`metric-mae`
- :ref:`metric-brier_score`
- :ref:`metric-reliability`

Литература
------------

.. footbibliography::
