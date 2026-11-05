.. _metric-pr_auc:

================================================================
Площадь под кривой точность–полнота (PR AUC, средняя точность)
================================================================

Средняя точность: сумма значений precision на порогах оценки, взвешенная приращениями recall. Не использует верные отрицания и потому лучше различает системы при редких событиях :footcite:p:`saito2015`.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.pr_auc(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.pr_auc`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{AP} = \sum_{k} \left(R_k - R_{k-1}\right) P_k

:math:`P_k` и :math:`R_k` precision и recall при пороге, равном :math:`k`-му различному значению оценки (в порядке убывания), :math:`R_0 = 0`. Это ступенчатая сумма, а не трапеции; Davis и Goadrich :footcite:p:`davis2006` объясняют, почему линейная интерполяция между точками такой кривой завышает площадь.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Реализована средняя точность (ступенчатая сумма), а не площадь по трапециям. Веса не поддерживаются. Метки события определяются равенством ``obs == 1``.

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

Значение 1 означает идеальное разделение. Ориентир случайной системы равен частоте события и потому зависит от данных. Если в срезе меньше двух пар или нет обоих классов, результат NaN.

Интерпретация и критерии оценки
---------------------------------

Общепринятых градаций нет. Значение нужно сравнивать с частотой события.

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
     - Оценка события (вероятность или любой монотонный балл) той же формы, что ``obs``.
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
     - 0.9844
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN
   * - ``inf`` в ``obs``
     - 0.9844
   * - постоянный ``obs`` (нулевая дисперсия)
     - NaN
   * - ``obs`` и ``sim`` из одних нулей
     - NaN
   * - пустой ввод
     - NaN
   * - разная длина ``obs`` и ``sim``
     - ValueError

С ``omit`` пары с пропуском в ``obs`` или ``sim`` удаляются, ``propagate`` возвращает NaN, ``raise`` вызывает ``ValueError``. Ряд без событий или без не-событий даёт NaN.

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

   # Вероятность события получена из ансамбля из 20 членов
   ens_rng = np.random.default_rng(7)
   members = q_sim[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.2 * q_sim[:, None])
   threshold = np.quantile(q_obs, 0.9)
   event_obs = (q_obs > threshold).astype(float)
   prob_sim = (members > threshold).mean(axis=1)

.. testcode::

   result = hm.pr_auc(event_obs, prob_sim)
   print(f"pr_auc = {float(result):.4f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   pr_auc = 0.9921

Случайные оценки дают значение около частоты события, а не 0,5 как у ROC AUC:

.. testcode::

   random_scores = np.random.default_rng(3).random(event_obs.size)
   print(round(float(event_obs.mean()), 4), round(float(hm.pr_auc(event_obs, random_scores)), 4), round(float(hm.roc_auc(event_obs, random_scores)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.1004 0.0993 0.5096

По трём створам с разной редкостью события, ``axis=0``:

.. testcode::

   # Вероятности события для тех же трёх порогов
   event_obs_st = np.column_stack([q_obs > np.quantile(q_obs, k) for k in (0.8, 0.9, 0.95)]).astype(float)
   prob_st = np.column_stack([(members > np.quantile(q_obs, k)).mean(axis=1) for k in (0.8, 0.9, 0.95)])

.. testcode::

   per_gauge = hm.pr_auc(event_obs_st, prob_st, axis=0)
   print(np.round(per_gauge.value, 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.8199 0.9921 0.9635]

По сезонам через :func:`~hydrometrics.compute_grouped`. В межень событий нет, поэтому метрики, которые делят на число событий или прогнозов, там не определены.

.. testcode::

   # Сезон по месяцу: половодье с апреля по июнь, остальные месяцы межень
   month = dates.astype("datetime64[M]").astype(int) % 12 + 1
   season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")

.. testcode::

   by_season = hm.compute_grouped(hm.pr_auc, None, event_obs, prob_sim, group_by={"season": season})
   for (label,), value in by_season:
       print(label, round(float(value), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   low_flow nan
   flood 0.9921

На pandas результат тот же:

.. testcode::

   import pandas as pd

   print(round(float(hm.pr_auc(pd.Series(event_obs), pd.Series(prob_sim))), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.9921

Особенности применения в гидрологии
-------------------------------------

Для оповещений о редких паводках PR AUC чувствительнее к числу ложных тревог, чем ROC AUC, поскольку precision прямо учитывает их долю среди тревог. Результат при этом зависит от частоты события в выборке, и PR AUC разных створов с разной частотой напрямую не сопоставляют.

Связанные метрики
-------------------

- :ref:`metric-roc_auc`
- :ref:`metric-precision`
- :ref:`metric-recall`
- :ref:`metric-f1_score`

Литература
------------

.. footbibliography::
