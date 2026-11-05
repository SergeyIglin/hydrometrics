.. _metric-sharpness:

==============================================
Чёткость вероятностного прогноза (sharpness)
==============================================

Дисперсия прогнозных вероятностей. Показывает, насколько прогнозы отходят от среднего: чёткий прогноз использует вероятности, близкие к 0 и 1. Наблюдения не используются.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.sharpness(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.sharpness`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{SHARP} = \frac{\sum_{i} w_i\,\left(p_i - \bar{p}\right)^2}{\sum_{i} w_i}

:math:`p_i` прогнозная вероятность, :math:`\bar{p}` её (взвешенное) среднее, :math:`w_i` вес. Делитель без поправки на степени свободы (``ddof=0``).

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Определение чёткости как дисперсии вероятностей выбрано в библиотеке; в литературе чёткость связывают с концентрацией прогнозного распределения. Чёткость полезна только вместе с надёжностью: по формулировке Gneiting et al. :footcite:p:`gneiting2007b`, прогноз должен быть как можно чётче при условии калиброванности.

Диапазон значений и оптимум
-----------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table

   * - Диапазон
     - Оптимум
     - Направление
   * - [0, 0.25]
     - 0.25
     - больше лучше

Для вероятностей в [0, 1] дисперсия не превышает 0,25 (половина прогнозов 0, половина 1). Постоянный прогноз даёт значение, равное нулю с точностью до округления: от точного 0 до порядка :math:`10^{-32}` в зависимости от константы и длины ряда. «Оптимум» здесь условный: больше означает чётче, но не лучше.

Интерпретация и критерии оценки
---------------------------------

Порогов нет. Значение сравнивается только между прогнозами одного и того же события и вместе с :ref:`metric-reliability`.

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
     - Наблюдения принимаются для единообразия вызова и в расчёте не участвуют.
   * - ``sim``
     - массив
     - обязателен
     - Вероятность события той же формы, что ``obs``. Диапазон [0, 1] не проверяется.
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
     - 0.04013
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN (RuntimeWarning)
   * - ``inf`` в ``obs``
     - 0.04011
   * - постоянный ``obs`` (нулевая дисперсия)
     - 0.04011
   * - ``obs`` и ``sim`` из одних нулей
     - 0
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

   # Вероятность события получена из ансамбля из 20 членов
   ens_rng = np.random.default_rng(7)
   members = q_sim[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.2 * q_sim[:, None])
   threshold = np.quantile(q_obs, 0.9)
   event_obs = (q_obs > threshold).astype(float)
   prob_sim = (members > threshold).mean(axis=1)

.. testcode::

   result = hm.sharpness(event_obs, prob_sim)
   print(f"sharpness = {float(result):.4f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   sharpness = 0.0789

Чёткость не использует наблюдения. Растянутые вероятности чётче, но надёжность падает, и оценка Брайера ухудшается:

.. testcode::

   prob_sharp = np.clip(0.5 + 3 * (prob_sim - 0.5), 0, 1)
   for label, p in (("ensemble", prob_sim), ("stretched", prob_sharp)):
       print(label, round(float(hm.sharpness(event_obs, p)), 4), round(float(hm.brier_score(event_obs, p)), 5))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   ensemble 0.0789 0.00801
   stretched 0.0838 0.01055

По трём створам с разной редкостью события, ``axis=0``:

.. testcode::

   # Вероятности события для тех же трёх порогов
   event_obs_st = np.column_stack([q_obs > np.quantile(q_obs, k) for k in (0.8, 0.9, 0.95)]).astype(float)
   prob_st = np.column_stack([(members > np.quantile(q_obs, k)).mean(axis=1) for k in (0.8, 0.9, 0.95)])

.. testcode::

   per_gauge = hm.sharpness(event_obs_st, prob_st, axis=0)
   print(np.round(per_gauge.value, 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.123  0.0789 0.0193]

По сезонам через :func:`~hydrometrics.compute_grouped`. В межень событий нет, поэтому метрики, которые делят на число событий или прогнозов, там не определены.

.. testcode::

   # Сезон по месяцу: половодье с апреля по июнь, остальные месяцы межень
   month = dates.astype("datetime64[M]").astype(int) % 12 + 1
   season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")

.. testcode::

   by_season = hm.compute_grouped(hm.sharpness, None, event_obs, prob_sim, group_by={"season": season})
   for (label,), value in by_season:
       print(label, round(float(value), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   low_flow 0.0
   flood 0.2088

На pandas результат тот же:

.. testcode::

   import pandas as pd

   print(round(float(hm.sharpness(pd.Series(event_obs), pd.Series(prob_sim))), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.0789

Особенности применения в гидрологии
-------------------------------------

Для редкого события чёткость в абсолютных числах мала даже у хорошей системы, так как большинство вероятностей близки к 0. Сопоставлять её нужно с частотой события: максимально возможная дисперсия при данной частоте :math:`\bar{o}` равна :math:`\bar{o}(1-\bar{o})`.

Связанные метрики
-------------------

- :ref:`metric-reliability`
- :ref:`metric-brier_score`

Литература
------------

.. footbibliography::
