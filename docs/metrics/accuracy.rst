.. _metric-accuracy:

======================================
Доля верных классификаций (accuracy)
======================================

Доля пар, в которых прогнозная метка совпала с наблюдённой: сумма верных прогнозов события и его отсутствия, делённая на число пар.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.accuracy(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.accuracy`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{ACC} = \frac{a + d}{a + b + c + d} = \frac{\sum_{i} w_i\,\mathbb{1}(O_i = S_i)}{\sum_{i} w_i}

:math:`a` — события предсказаны верно, :math:`b` ложные тревоги, :math:`c` пропуски, :math:`d` верные отрицания в таблице сопряжённости. Для бинарных меток обе записи совпадают.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Совпадает с определением. Пара с пропуском исключается, а не засчитывается как ошибка.

Диапазон значений и оптимум
-----------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table

   * - Диапазон
     - Оптимум
     - Направление
   * - [0, 1]
     - 1
     - больше лучше

Значение 1 означает полное совпадение меток. Для редкого события значение близко к 1 и у бесполезного прогноза (пример выше), поэтому верхняя граница почти не различает системы.

Интерпретация и критерии оценки
---------------------------------

Общепринятых градаций нет. Значение нужно читать относительно доли тривиального прогноза «события не будет», равной :math:`1 - \bar{o}`.

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
     - Наблюдённые метки. Сравнение идёт на равенство, поэтому подходят и многоклассовые метки.
   * - ``sim``
     - массив
     - обязателен
     - Прогнозные метки той же формы.
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
     - 0.9626
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN (RuntimeWarning)
   * - ``inf`` в ``obs``
     - 0.9617
   * - постоянный ``obs`` (нулевая дисперсия)
     - 0.7774
   * - ``obs`` и ``sim`` из одних нулей
     - 1
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

   # Событие: расход выше 90-го процентиля наблюдений
   threshold = np.quantile(q_obs, 0.9)
   event_obs = (q_obs > threshold).astype(float)
   event_sim = (q_sim > threshold).astype(float)

.. testcode::

   result = hm.accuracy(event_obs, event_sim)
   print(f"accuracy = {float(result):.4f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   accuracy = 0.9881

Событие редкое (порог 90-го процентиля), поэтому прогноз «события не будет» никогда не пропускает дней без события и получает высокую долю верных:

.. testcode::

   never = np.zeros_like(event_obs)
   print(round(float(hm.accuracy(event_obs, event_sim)), 4), round(float(hm.accuracy(event_obs, never)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.9881 0.8996

По трём створам с разной редкостью события, ``axis=0``:

.. testcode::

   # Три створа с разной редкостью события: пороги 80-й, 90-й и 95-й процентили
   levels = [0.8, 0.9, 0.95]
   event_obs_st = np.column_stack([q_obs > np.quantile(q_obs, k) for k in levels]).astype(float)
   event_sim_st = np.column_stack([q_sim > np.quantile(q_obs, k) for k in levels]).astype(float)

.. testcode::

   per_gauge = hm.accuracy(event_obs_st, event_sim_st, axis=0)
   print(np.round(per_gauge.value, 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.8403 0.9881 0.9881]

По сезонам через :func:`~hydrometrics.compute_grouped`. В межень событий нет, поэтому метрики, которые делят на число событий или прогнозов, там не определены.

.. testcode::

   # Сезон по месяцу: половодье с апреля по июнь, остальные месяцы межень
   month = dates.astype("datetime64[M]").astype(int) % 12 + 1
   season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")

.. testcode::

   by_season = hm.compute_grouped(hm.accuracy, None, event_obs, event_sim, group_by={"season": season})
   for (label,), value in by_season:
       print(label, round(float(value), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   low_flow 1.0
   flood 0.9524

На pandas результат тот же:

.. testcode::

   import pandas as pd

   print(round(float(hm.accuracy(pd.Series(event_obs), pd.Series(event_sim))), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.9881

Особенности применения в гидрологии
-------------------------------------

Паводки и маловодье — редкие события, и accuracy для них почти всегда высока. Для оценки прогнозов редких событий используйте :ref:`metric-recall`, :ref:`metric-precision` или индексы :ref:`metric-edi` и :ref:`metric-sedi`.

Связанные метрики
-------------------

- :ref:`metric-precision`
- :ref:`metric-recall`
- :ref:`metric-f1_score`
- :ref:`metric-edi`
- :ref:`metric-sedi`

Литература
------------

Специальной литературы для этой страницы нет: метрика определяется общепринятой формулой.
