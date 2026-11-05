.. _metric-nse_variance_weighted:

========================================================================
Взвешенный по дисперсии критерий Нэша–Сатклиффа для нескольких створов
========================================================================

Метрика вычисляет :ref:`metric-nse` отдельно для каждого створа и усредняет результаты с весами, равными дисперсиям наблюдённых расходов на створах :footcite:p:`gartsman2024`. Створы с большей изменчивостью стока вносят больший вклад.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.nse_variance_weighted(obs, sim, *, gauge, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.nse_variance_weighted`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{NSE}_{\mathrm{VW}} = \frac{\sum_{g=1}^{G}\sigma_g^2\,\mathrm{NSE}_g}{\sum_{g=1}^{G}\sigma_g^2}, \qquad \sigma_g^2 = \frac{1}{n_g}\sum_{i\in g}\left(O_i-\bar{O}_g\right)^2

:math:`G` число створов, :math:`n_g` число действительных пар на створе :math:`g`, :math:`\bar{O}_g` среднее наблюдений створа, :math:`\mathrm{NSE}_g` критерий Нэша–Сатклиффа створа. Дисперсия считается с делителем :math:`n_g` (``ddof=0``). Суммирование идёт по створам, которые задаёт массив ``gauge``.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Формула в коде совпадает с приведённой. Створ исключается, если у него нет действительных пар, если его NSE не конечна или если наблюдения постоянны с точностью до округления. Если подходящих створов нет, результат равен NaN. Значения ``inf`` исключаются как пропуски (в отличие от большинства метрик библиотеки).

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

Результат это взвешенное среднее значений NSE, не превышающих 1, поэтому он не превышает 1 и снизу не ограничен. Значение 1 означает безупречный результат на всех учтённых створах; значение 0 соответствует в среднем прогнозу средним по каждому створу.

Интерпретация и критерии оценки
---------------------------------

Градаций для взвешенной оценки в литературе, которая прочитана, нет. К значению применимы те же ориентиры, что и к :ref:`metric-nse`, с поправкой на то, что результат определяют створы с наибольшей дисперсией. Пороги Moriasi et al. :footcite:p:`moriasi2007` предложены для NSE одного створа на месячном шаге.

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
     - Наблюдённые расходы всех створов в одном одномерном массиве.
   * - ``sim``
     - массив
     - обязателен
     - Модельные расходы той же длины.
   * - ``gauge``
     - массив
     - обязателен
     - Метки створов той же длины, что ``obs``; допускаются числа и строки. Другая длина вызывает ``ValueError``.
   * - ``axis``
     - int | None
     - ``None``
     - Не поддерживается: любое значение, кроме ``None``, вызывает ``NotImplementedError``.
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
     - не применимо: метрика требует одномерного ввода
   * - pandas
     - numpy.float64
     - не применимо: метрика требует одномерного ввода
   * - polars
     - numpy.float64
     - не применимо: метрика требует одномерного ввода
   * - xarray
     - numpy.float64
     - не применимо: метрика требует одномерного ввода

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
     - NaN
   * - ``inf`` в ``obs``
     - 0.9529
   * - постоянный ``obs`` (нулевая дисперсия)
     - NaN
   * - ``obs`` и ``sim`` из одних нулей
     - NaN
   * - отрицательные значения (ряд минус его среднее)
     - 0.9529
   * - пустой ввод
     - NaN
   * - разная длина ``obs`` и ``sim``
     - ValueError

При ``omit`` пара с пропуском исключается из расчёта и NSE, и дисперсии створа; ``propagate`` даёт NaN, ``raise`` вызывает ``ValueError``. Двумерный ввод вызывает ``ValueError``: створы кодируются метками, а не столбцами.

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
     - нет
     - да
     - да
   * - pandas
     - нет
     - нет
     - да
     - да
   * - polars
     - нет
     - нет
     - да
     - да
   * - xarray
     - нет
     - нет
     - да
     - да

Индексы pandas и координаты xarray проверяются параметром ``align``: по умолчанию несовпадающие метки дают ``ValueError``, ``align="inner"`` оставляет общие (см. :doc:`/user_guide/input_data`).

Примеры
---------

Три створа на одной реке: у нижнего расходы в пять раз больше, чем у верхнего, у малого притока в пять раз меньше. Модель завышает расход на 10 % и вносит случайную ошибку с одинаковым стандартным отклонением 8 м³/с на всех створах.

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

   gauge_rng = np.random.default_rng(5)
   scale = {"upper": 1.0, "lower": 5.0, "tributary": 0.2}
   obs_all = np.concatenate([q_obs[:365] * k for k in scale.values()])
   sim_all = obs_all * 1.1 + gauge_rng.normal(0, 8, obs_all.size)
   gauge = np.repeat(list(scale), 365)  # метка створа для каждой пары

.. testcode::

   nse_vw = hm.nse_variance_weighted(obs_all, sim_all, gauge=gauge)
   print(f"variance-weighted NSE = {float(nse_vw):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   variance-weighted NSE = 0.983

Значения по створам и веса показывают, как получен результат: NSE каждого створа умножается на дисперсию его наблюдений.

.. testcode::

   names = list(scale)
   per_gauge = [float(hm.nse(obs_all[gauge == g], sim_all[gauge == g])) for g in names]
   variance = [float(np.var(obs_all[gauge == g])) for g in names]
   for g, nse_g, var_g in zip(names, per_gauge, variance):
       print(g, round(nse_g, 3), round(var_g, 1))
   by_hand = np.average(per_gauge, weights=variance)
   print(round(by_hand, 3), round(float(np.mean(per_gauge)), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   upper 0.963 2810.8
   lower 0.985 70269.0
   tributary 0.43 112.4
   0.983 0.793

Пропуски: при ``omit`` пара с пропуском исключается, при ``propagate`` результат равен NaN.

.. testcode::

   sim_gap = sim_all.copy()
   sim_gap[10] = np.nan
   print(round(float(hm.nse_variance_weighted(obs_all, sim_gap, gauge=gauge)), 4))
   print(hm.nse_variance_weighted(obs_all, sim_gap, gauge=gauge, nan_policy="propagate").value)

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.9834
   nan

На pandas метки створов передаются массивом той же длины:

.. testcode::

   import pandas as pd

   print(round(float(hm.nse_variance_weighted(pd.Series(obs_all), pd.Series(sim_all), gauge=gauge)), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.983

Особенности применения в гидрологии
-------------------------------------

Вес створа равен дисперсии наблюдённых расходов, выраженной в единицах величины, поэтому вес растёт как квадрат масштаба. В примере у створа с пятикратным расходом вес в 25 раз больше, чем у верхнего, а малый приток почти не влияет: значение 0.9834 определяется двумя крупными створами, тогда как простое среднее NSE по створам даёт 0.7927. Метрика скрывает плохую оценку на малой реке.

Ряды створов объединяются в один массив с метками, поэтому длины рядов могут быть разными. Створ с постоянными наблюдениями исключается и из числителя, и из знаменателя.

Многостворовое взвешивание по дисперсии рассматривают Гарцман и соавторы :footcite:p:`gartsman2024`; про их выводы о калибровке здесь сказано только то, что прочитано в статье: многомерный NSE равен среднему NSE по створам, взвешенному дисперсиями расходов.

Связанные метрики
-------------------

- :ref:`metric-nse`
- :ref:`metric-regNSE`
- :ref:`metric-kge_2012`

Литература
------------

.. footbibliography::
