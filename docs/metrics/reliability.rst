.. _metric-reliability:

==================================================
Надёжность вероятностного прогноза (reliability)
==================================================

Компонента «надёжность» разложения оценки Брайера по Мерфи :footcite:p:`murphy1973`: взвешенный средний квадрат расхождения между прогнозной вероятностью и фактической частотой события внутри интервалов вероятности.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.reliability(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict", n_bins=10)

Запись в справочнике API: :func:`hydrometrics.reliability`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{REL} = \frac{1}{N}\sum_{k=1}^{K} N_k\left(\bar{p}_k - \bar{o}_k\right)^2

:math:`K` число интервалов (``n_bins``), :math:`N_k` их вес (число пар при единичных весах), :math:`\bar{p}_k` среднее прогнозной вероятности и :math:`\bar{o}_k` частота события в интервале :math:`k`, :math:`N` общий вес. Интервалы равной ширины на [0, 1], правые границы открыты, кроме последнего интервала, куда входит :math:`p=1`.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Реализован только один член разложения. Разрешающая способность и неопределённость как отдельные функции в библиотеке не представлены; сумма с :ref:`metric-brier_score` не проверяется. Значение зависит от числа интервалов ``n_bins``, которое должно быть целым не меньше 1. Диапазон ``obs`` (0 или 1) и ``sim`` ([0, 1]) проверяется, при нарушении возникает ``ValueError``.

Диапазон значений и оптимум
-----------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table

   * - Диапазон
     - Оптимум
     - Направление
   * - [0, 1]
     - 0
     - меньше лучше

Значение 0 означает, что в каждом интервале среднее прогноза равно частоте события. Верхняя граница 1 при вероятностях в [0, 1]. Для ряда без действительных пар или с нулевой суммой весов результат NaN.

Интерпретация и критерии оценки
---------------------------------

Общепринятых градаций нет. Значение зависит от числа интервалов и от размера выборки: при малом числе пар в интервалах оно смещено вверх. Диаграммы надёжности и их доверительные интервалы обсуждают Bröcker и Smith :footcite:p:`brocker2007`.

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
     - Бинарные наблюдения: 1 событие произошло, 0 не произошло.
   * - ``sim``
     - массив
     - обязателен
     - Вероятность события той же формы, что ``obs``. Значения должны лежать в [0, 1] (NaN игнорируется), иначе ``ValueError``.
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
   * - ``n_bins``
     - int
     - ``10``
     - Число интервалов вероятности равной ширины: целое не меньше 1. Значения типа bool, float, str и None отвергаются с ``ValueError``.

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
     - 0.04268
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN
   * - ``inf`` в ``obs``
     - ValueError
   * - постоянный ``obs`` (нулевая дисперсия)
     - 0.08654
   * - ``obs`` и ``sim`` из одних нулей
     - 0
   * - пустой ввод
     - NaN
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

   # Вероятность события получена из ансамбля из 20 членов
   ens_rng = np.random.default_rng(7)
   members = q_sim[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.2 * q_sim[:, None])
   threshold = np.quantile(q_obs, 0.9)
   event_obs = (q_obs > threshold).astype(float)
   prob_sim = (members > threshold).mean(axis=1)

.. testcode::

   result = hm.reliability(event_obs, prob_sim)
   print(f"reliability = {float(result):.4f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   reliability = 0.0009

Чрезмерно уверенный прогноз (вероятности растянуты к 0 и 1) теряет надёжность:

.. testcode::

   prob_sharp = np.clip(0.5 + 3 * (prob_sim - 0.5), 0, 1)
   print(round(float(hm.reliability(event_obs, prob_sim)), 5), round(float(hm.reliability(event_obs, prob_sharp)), 5))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.00091 0.00109

По трём створам с разной редкостью события, ``axis=0``:

.. testcode::

   # Вероятности события для тех же трёх порогов
   event_obs_st = np.column_stack([q_obs > np.quantile(q_obs, k) for k in (0.8, 0.9, 0.95)]).astype(float)
   prob_st = np.column_stack([(members > np.quantile(q_obs, k)).mean(axis=1) for k in (0.8, 0.9, 0.95)])

.. testcode::

   per_gauge = hm.reliability(event_obs_st, prob_st, axis=0)
   print(np.round(per_gauge.value, 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.0489 0.0009 0.0056]

По сезонам через :func:`~hydrometrics.compute_grouped`. В межень событий нет, поэтому метрики, которые делят на число событий или прогнозов, там не определены.

.. testcode::

   # Сезон по месяцу: половодье с апреля по июнь, остальные месяцы межень
   month = dates.astype("datetime64[M]").astype(int) % 12 + 1
   season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")

.. testcode::

   by_season = hm.compute_grouped(hm.reliability, None, event_obs, prob_sim, group_by={"season": season})
   for (label,), value in by_season:
       print(label, round(float(value), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   low_flow 0.0
   flood 0.0037

На pandas результат тот же:

.. testcode::

   import pandas as pd

   print(round(float(hm.reliability(pd.Series(event_obs), pd.Series(prob_sim))), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.0009

Особенности применения в гидрологии
-------------------------------------

Для редких паводковых событий большинство прогнозов попадает в первый интервал, а остальные интервалы содержат единичные пары; надёжность по ним оценивается шумно. Увеличение ``n_bins`` делит эти немногие пары на ещё меньшие группы, и оценка в каждом интервале становится ещё более шумной.

Связанные метрики
-------------------

- :ref:`metric-brier_score`
- :ref:`metric-sharpness`
- :ref:`metric-roc_auc`

Литература
------------

.. footbibliography::
