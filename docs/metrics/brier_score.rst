.. _metric-brier_score:

==============================
Оценка Брайера (Brier score)
==============================

Средний квадрат разности между прогнозной вероятностью события и исходом (0 или 1) :footcite:p:`brier1950`. Оценивает вероятностный прогноз события, например превышения порога расхода.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.brier_score(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.brier_score`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{BS} = \frac{\sum_{i} w_i\,\left(p_i - o_i\right)^2}{\sum_{i} w_i}

:math:`p_i` прогнозная вероятность, :math:`o_i` исход (1 или 0), :math:`w_i` вес. Суммирование идёт по оси ``axis``.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Совпадает с определением. Библиотека проверяет, что ``obs`` равны 0 или 1, а ``sim`` лежат в [0, 1] (NaN игнорируется); иначе возникает ``ValueError``.

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

Значение 0 у безошибочного детерминированного прогноза 0/1. Верхняя граница 1 достигается, когда каждая вероятность противоположна исходу. Границы верны при вероятностях в [0, 1].

Интерпретация и критерии оценки
---------------------------------

Общепринятых градаций нет: значение зависит от частоты события. Для редких событий оценка мала даже у бесполезного прогноза, поэтому её сравнивают с оценкой климатической частоты (пример выше).

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
     - 0.06464
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN (RuntimeWarning)
   * - ``inf`` в ``obs``
     - ValueError
   * - постоянный ``obs`` (нулевая дисперсия)
     - 0.08719
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

   result = hm.brier_score(event_obs, prob_sim)
   print(f"brier_score = {float(result):.4f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   brier_score = 0.0080

Опорный прогноз «климатическая частота» даёт :math:`\bar{o}(1-\bar{o})`. Индекса мастерства в библиотеке нет, он считается вручную:

.. testcode::

   base_rate = event_obs.mean()
   bs_climatology = base_rate * (1 - base_rate)
   bs = float(hm.brier_score(event_obs, prob_sim))
   print(round(bs, 5), round(bs_climatology, 5), round(1 - bs / bs_climatology, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.00801 0.09029 0.911

По трём створам с разной редкостью события, ``axis=0``:

.. testcode::

   # Вероятности события для тех же трёх порогов
   event_obs_st = np.column_stack([q_obs > np.quantile(q_obs, k) for k in (0.8, 0.9, 0.95)]).astype(float)
   prob_st = np.column_stack([(members > np.quantile(q_obs, k)).mean(axis=1) for k in (0.8, 0.9, 0.95)])

.. testcode::

   per_gauge = hm.brier_score(event_obs_st, prob_st, axis=0)
   print(np.round(per_gauge.value, 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.1143 0.008  0.0115]

По сезонам через :func:`~hydrometrics.compute_grouped`. В межень событий нет, поэтому метрики, которые делят на число событий или прогнозов, там не определены.

.. testcode::

   # Сезон по месяцу: половодье с апреля по июнь, остальные месяцы межень
   month = dates.astype("datetime64[M]").astype(int) % 12 + 1
   season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")

.. testcode::

   by_season = hm.compute_grouped(hm.brier_score, None, event_obs, prob_sim, group_by={"season": season})
   for (label,), value in by_season:
       print(label, round(float(value), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   low_flow 0.0
   flood 0.0322

На pandas результат тот же:

.. testcode::

   import pandas as pd

   print(round(float(hm.brier_score(pd.Series(event_obs), pd.Series(prob_sim))), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.008

Особенности применения в гидрологии
-------------------------------------

Для редких событий вроде превышения 95-й обеспеченности Brier score определяется в основном качеством прогноза «ничего не произойдёт», и различия между системами тонут в малых значениях. Раздельная оценка надёжности и чёткости помогает: :ref:`metric-reliability`, :ref:`metric-sharpness`.

Ансамблевую вероятность превышения порога при небольшом числе членов нужно оценивать с учётом конечности ансамбля; библиотека этого не делает.

Связанные метрики
-------------------

- :ref:`metric-reliability`
- :ref:`metric-sharpness`
- :ref:`metric-crps`
- :ref:`metric-roc_auc`

Литература
------------

.. footbibliography::
