.. _metric-roc_auc:

==================================
Площадь под ROC-кривой (ROC AUC)
==================================

ROC AUC оценивает способность прогноза отделять случаи с событием от случаев без него: вероятность, что у события оценка выше, чем у не-события :footcite:p:`fawcett2006`. Не зависит от выбора порога вероятности.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.roc_auc(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.roc_auc`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{AUC} = \frac{R_1 - n_1(n_1+1)/2}{n_1\,n_0}

:math:`n_1` и :math:`n_0` числа событий и не-событий, :math:`R_1` сумма рангов оценок у событий (при совпадающих оценках средний ранг). Это статистика Манна–Уитни, нормированная на число пар :footcite:p:`mason2002`. Расчёт выполняется по каждому срезу вдоль оси.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Площадь считается через ранги, а не численным интегрированием ROC-кривой, поэтому совпадающие оценки дают вклад 0,5. Метки события определяются равенством ``obs == 1``. Веса не поддерживаются.

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

Значение 0,5 соответствует отсутствию различающей способности (постоянная оценка даёт ровно 0,5). Значение 1 означает идеальное разделение, значение меньше 0,5 — ранжирование в обратном порядке. Если в срезе нет событий или нет не-событий, или меньше двух пар, результат NaN.

Интерпретация и критерии оценки
---------------------------------

Общепринятых градаций качества нет; ориентир 0,5 следует из определения. AUC зависит от доли событий слабо, но при очень редких событиях ею трудно различать системы: Saito и Rehmsmeier :footcite:p:`saito2015` показывают, что на несбалансированных данных график точность–полнота информативнее ROC.

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
     - 0.9944
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN
   * - ``inf`` в ``obs``
     - 0.9944
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

   result = hm.roc_auc(event_obs, prob_sim)
   print(f"roc_auc = {float(result):.4f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   roc_auc = 0.9991

AUC равна вероятности того, что случайно выбранной паре «событие / не событие» вероятность события присвоена выше у события; совпадения считаются как половина :footcite:p:`fawcett2006`. Прямой пересчёт по парам:

.. testcode::

   positive = prob_sim[event_obs == 1]
   negative = prob_sim[event_obs == 0]
   greater = (positive[:, None] > negative[None, :]).mean()
   ties = (positive[:, None] == negative[None, :]).mean()
   print(round(float(greater + 0.5 * ties), 6), round(float(hm.roc_auc(event_obs, prob_sim)), 6))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.999147 0.999147

Метрика использует только порядок оценок, поэтому любой монотонный пересчёт её не меняет, а оценки не обязаны лежать в [0, 1]:

.. testcode::

   print(round(float(hm.roc_auc(event_obs, q_sim)), 6), round(float(hm.roc_auc(event_obs, np.log(q_sim))), 6))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.999253 0.999253

По трём створам с разной редкостью события, ``axis=0``:

.. testcode::

   # Вероятности события для тех же трёх порогов
   event_obs_st = np.column_stack([q_obs > np.quantile(q_obs, k) for k in (0.8, 0.9, 0.95)]).astype(float)
   prob_st = np.column_stack([(members > np.quantile(q_obs, k)).mean(axis=1) for k in (0.8, 0.9, 0.95)])

.. testcode::

   per_gauge = hm.roc_auc(event_obs_st, prob_st, axis=0)
   print(np.round(per_gauge.value, 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.8855 0.9991 0.9898]

По сезонам через :func:`~hydrometrics.compute_grouped`. В межень событий нет, поэтому метрики, которые делят на число событий или прогнозов, там не определены.

.. testcode::

   # Сезон по месяцу: половодье с апреля по июнь, остальные месяцы межень
   month = dates.astype("datetime64[M]").astype(int) % 12 + 1
   season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")

.. testcode::

   by_season = hm.compute_grouped(hm.roc_auc, None, event_obs, prob_sim, group_by={"season": season})
   for (label,), value in by_season:
       print(label, round(float(value), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   low_flow nan
   flood 0.9948

На pandas результат тот же:

.. testcode::

   import pandas as pd

   print(round(float(hm.roc_auc(pd.Series(event_obs), pd.Series(prob_sim))), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.9991

Особенности применения в гидрологии
-------------------------------------

AUC оценивает только ранжирование. Система, у которой все вероятности завышены вдвое, получает ту же AUC, но совершенно непригодна для принятия решений по порогу вероятности. Дополняйте AUC оценками :ref:`metric-reliability` и :ref:`metric-brier_score`.

Связанные метрики
-------------------

- :ref:`metric-pr_auc`
- :ref:`metric-brier_score`
- :ref:`metric-edi`
- :ref:`metric-recall`

Литература
------------

.. footbibliography::
