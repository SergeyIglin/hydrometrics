.. _metric-nse:

===============================
Критерий Нэша–Сатклиффа (NSE)
===============================

NSE сравнивает сумму квадратов ошибок модели с суммой квадратов отклонений наблюдений от их среднего :footcite:p:`nash1970`. Показывает, насколько модель точнее постоянного прогноза средним значением.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.nse(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict", norm=None)

Запись в справочнике API: :func:`hydrometrics.nse`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{NSE} = 1 - \frac{\sum_{i=1}^{n} w_i\,(O_i - S_i)^2}{\sum_{i=1}^{n} w_i\,(O_i - \bar{O})^2}, \qquad \bar{O} = \frac{\sum_i w_i O_i}{\sum_i w_i}

:math:`O_i` наблюдённое значение, :math:`S_i` модельное значение, :math:`w_i` вес (1 без ``sample_weight``), :math:`n` число пар. Суммирование идёт по оси ``axis``, а при ``axis=None`` по всем элементам массива.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Без весов и ``norm`` формула совпадает с классической. Веса и ``norm`` являются расширениями библиотеки: заданный ``norm`` заменяет :math:`\bar{O}` в знаменателе.

При умолчании ``nan_policy="omit"`` пара с пропуском в ``obs`` или ``sim`` исключается из обеих сумм сразу, поэтому среднее :math:`\bar{O}` тоже считается только по действительным парам.

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

Верхняя граница достигается при совпадении рядов. Снизу значение не ограничено. При нулевой дисперсии наблюдений знаменатель равен нулю и результат равен NaN; ``r2`` в этом случае ведёт себя иначе.

Интерпретация и критерии оценки
---------------------------------

``NSE = 1`` означает полное совпадение. ``NSE = 0`` означает, что модель в сумме квадратов ошибок равна постоянному прогнозу средним наблюдённым значением за тот же период; ``NSE < 0`` означает, что такой прогноз точнее модели. Этот ориентир следует из самой формулы и не зависит от данных.

Градации приведены в таблице 4 у Moriasi et al. :footcite:p:`moriasi2007`. Они предложены для непрерывного долгосрочного моделирования водосборов на **месячном** шаге по данным о стоке, наносах и биогенных элементах.

.. list-table::
   :header-rows: 1
   :class: hm-table

   * - Оценка
     - NSE
   * - Очень хорошо
     - 0.75 < NSE < 1.00
   * - Хорошо
     - 0.65 < NSE < 0.75
   * - Удовлетворительно
     - 0.50 < NSE < 0.65
   * - Неудовлетворительно
     - NSE < 0.50

Пороги эмпирические. Авторы прямо указывают, что их надо корректировать с учётом качества данных, процедуры калибровки, шага по времени и масштаба проекта, а с ростом шага осреднения оценка должна становиться строже. Перенос этих значений на суточный расход или прогноз половодья без проверки не обоснован.

В обзоре Moriasi et al. :footcite:p:`moriasi2015` для моделей масштаба водосбора удовлетворительным назван поток с ``NSE > 0.50`` на суточном, месячном и годовом шаге (по аннотации статьи; полная таблица недоступна, см. :doc:`/user_guide/known_limits`).

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
   * - ``norm``
     - число или массив
     - ``None``
     - Опорное значение вместо среднего наблюдений. Массив должен вещаться на ``obs``.

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
     - 0.9529
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
     - 0.9529
   * - пустой ввод
     - NaN (RuntimeWarning)
   * - разная длина ``obs`` и ``sim``
     - ValueError

Умолчание ``nan_policy="omit"`` удаляет пары попарно, в том числе при заданной оси; результат совпадает с расчётом по заранее отфильтрованным парам. ``"propagate"`` возвращает NaN, если в ряду (или в срезе вдоль оси) есть пропуск. ``"raise"`` вызывает ``ValueError``. Значение ``inf`` пропуском не считается: ``inf`` в ``obs`` даёт NaN, ``inf`` в ``sim`` даёт ``-inf``.

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

Суточный гидрограф за три водных года: половодье, межень, расходы в м³/с.

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
   print(f"NSE = {float(result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   NSE = 0.954

Значения по створам: при заданной оси без ``reduction`` возвращается массив по створам, явный ``reduction="mean"`` сворачивает его в одно число.

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   per_station = hm.nse(q_obs_st, q_sim_st, axis=0)
   print(np.round(per_station.value, 3))
   print(round(float(hm.nse(q_obs_st, q_sim_st, axis=0, reduction="mean")), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.954 0.921 0.963]
   0.946

По водным годам и по сезонам через :func:`~hydrometrics.compute_grouped`:

.. testcode::

   import pandas as pd

   df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
   # Водный год начинается 1 октября и назван по году окончания
   df["water_year"] = df.index.year + (df.index.month >= 10)

.. testcode::

   by_year = hm.compute_grouped(hm.nse, df, "q_obs", "q_sim", group_by="water_year")
   for (water_year,), value in by_year:
       print(int(water_year), round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2011 0.95
   2012 0.957
   2013 0.955

.. testcode::

   df["season"] = np.where(df.index.month.isin([4, 5, 6]), "flood", "low_flow")
   by_season = hm.compute_grouped(hm.nse, df, "q_obs", "q_sim", group_by="season")
   for (season,), value in by_season:
       print(season, round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   low_flow -2.846
   flood 0.949

Пропуски: по умолчанию пары с пробелом исключаются, а ``nan_info`` сообщает их число. ``propagate`` в той же ситуации даёт NaN.

.. testcode::

   q_obs_gap = q_obs.copy()
   q_obs_gap[100:130] = np.nan  # месяц без наблюдений на створе
   gap = hm.nse(q_obs_gap, q_sim)
   print(round(float(gap), 3), gap.nan_info["n_nan_removed"])
   print(hm.nse(q_obs_gap, q_sim, nan_policy="propagate").value)

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.954 30
   nan

Опорное значение можно задать через ``norm``, например среднюю многолетнюю норму. Значение попадает в ``norm_source``.

.. testcode::

   long_term_mean = 30.0
   custom = hm.nse(q_obs, q_sim, norm=long_term_mean)
   print(round(float(custom), 3), custom.norm_source)

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.954 user

Особенности применения в гидрологии
-------------------------------------

Метрика квадратичная, поэтому её определяют большие расходы. В примере выше ``NSE = 0.9537`` за весь период, ``0.9487`` за апрель–июнь и ``-2.846`` за остальные месяцы. Хорошая оценка за год не означает, что воспроизведена межень.

Систематическое занижение пиков при калибровке по NSE описано в литературе: Mizukami et al. :footcite:p:`mizukami2019` показывают, что калибровка по NSE плохо воспроизводит годовые максимумы из-за занижения вариабельности стока, со ссылкой на теоретический разбор Gupta et al. :footcite:p:`gupta2009`.

Среднее за период является слабым ориентиром для рек с устойчивым сезонным ходом: Гарцман :footcite:p:`gartsman2023` приводит условный пример, где одна и та же модель получает 0.90 при опоре на среднее и 0.33 при опоре на среднемноголетний ход расходов. Для такой оценки в библиотеке есть :func:`~hydrometrics.regNSE` с другим смыслом, а суточного режимного опорного ряда в ``nse`` можно добиться, передав массив ``norm``.

NSE нечувствительна к сдвигу среднего при низких расходах, отмечают Krause et al. :footcite:p:`krause2005`. Дополняйте её :ref:`metric-pbias` для объёма стока и :ref:`metric-log_nse` для межени.

Связанные метрики
-------------------

- :ref:`metric-log_nse`
- :ref:`metric-modified_nse`
- :ref:`metric-nse_bounded`
- :ref:`metric-regNSE`
- :ref:`metric-nse_variance_weighted`
- :ref:`metric-kge_2009`
- :ref:`metric-kge_2012`
- :ref:`metric-rsr`
- :ref:`metric-r2`
- :ref:`metric-pbias`

Литература
------------

.. footbibliography::
