.. _metric-ssigma_delta:

============================================
Отношение S/σ по группам прогнозов (S/σ_Δ)
============================================

Для каждой группы, заданной ``ref_date`` (обычно дата выпуска прогноза), считается отношение среднеквадратической ошибки к стандартному отклонению наблюдений внутри этой группы :footcite:p:`georgievsky2007`. Оценка группы присваивается всем её значениям.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.ssigma_delta(obs, sim, *, ref_date, m=2, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.ssigma_delta`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \left(\frac{S}{\sigma_\Delta}\right)_d = \frac{\sqrt{\dfrac{1}{n_d-m}\sum_{i\in G_d}\left(O_i-S_i\right)^2}}{\sqrt{\dfrac{1}{n_d-1}\sum_{i\in G_d}\left(O_i-\bar{O}_d\right)^2}}

:math:`G_d` группа с меткой :math:`d`, :math:`n_d` число действительных пар в ней, :math:`\bar{O}_d` среднее наблюдений группы, :math:`m` число параметров (по умолчанию 2). Все суммы берутся внутри группы. Результат функции это среднее по значениям пар, то есть группы с большим числом пар весят больше. Текст Георгиевского и Шаночкина :footcite:p:`georgievsky2007` при подготовке документации прочитать не удалось, поэтому формулы ниже взяты из реализации, а градации качества не приводятся (см. :doc:`/user_guide/known_limits`).

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

От :ref:`metric-ssigma` метрика отличается только тем, что σ и S считаются внутри групп. Здесь :math:`\sigma_\Delta` это стандартное отклонение наблюдений внутри группы ``ref_date``, а не стандартное отклонение изменения величины за заблаговременность. Формулы библиотеки подтверждены автором и не менялись.

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

Значение 0 означает нулевую ошибку, верхней границы нет. Группа с числом пар не больше ``m`` или с постоянными наблюдениями даёт NaN, и её значения в среднее не входят.

Интерпретация и критерии оценки
---------------------------------

Градации качества не приводятся по той же причине, что и для :ref:`metric-ssigma`: источник :footcite:p:`georgievsky2007` недоступен для чтения, пороги других источников подтвердить не удалось.

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
   * - ``ref_date``
     - массив
     - обязателен
     - Метки групп той же формы, что ``obs``: даты, числа или строки. Другая форма вызывает ``ValueError``.
   * - ``m``
     - int
     - ``2``
     - Число параметров, как в :ref:`metric-ssigma`: конечное неотрицательное число; отрицательное значение, NaN или inf вызывает ``ValueError``, не число вызывает ``TypeError``.
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
     - 0.2178
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN
   * - ``inf`` в ``obs``
     - 0.2172 (RuntimeWarning)
   * - постоянный ``obs`` (нулевая дисперсия)
     - NaN
   * - ``obs`` и ``sim`` из одних нулей
     - NaN
   * - отрицательные значения (ряд минус его среднее)
     - 0.2178
   * - пустой ввод
     - NaN
   * - разная длина ``obs`` и ``sim``
     - ValueError

Пары с пропуском в ``obs`` или ``sim`` исключаются из своей группы при ``omit``; ``propagate`` возвращает NaN (в результате по парам NaN стоит на месте пропуска, а оценка группы считается по остальным значениям); ``raise`` вызывает ``ValueError``. Ось и веса не поддерживаются.

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

Суточный гидрограф и прогнозы на 1–10 суток, выпускаемые каждые 10 суток. Группа это один выпуск прогноза: десять значений с общей датой выпуска.

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

   # Прогнозы на 1-10 суток, выпускаемые каждые 10 суток; ошибка растёт с заблаговременностью
   issue = np.arange(0, q_obs.size - 10, 10)
   lead = np.arange(1, 11)
   target = issue[:, None] + lead
   fc_rng = np.random.default_rng(11)
   obs_fc = q_obs[target].ravel()
   sim_fc = (q_obs[target] * (1 + 0.02 * lead) + fc_rng.normal(0, 1, target.shape) * (1 + 0.5 * lead)).ravel()
   issue_date = np.repeat(dates[issue], 10)  # метка группы: дата выпуска прогноза

.. testcode::

   result = hm.ssigma_delta(obs_fc, sim_fc, ref_date=issue_date)
   print(f"S/sigma_delta = {float(result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   S/sigma_delta = 1.490

С ``reduction="none"`` каждое значение пары заменено оценкой его группы. Первая группа, пересчитанная вручную:

.. testcode::

   per_pair = hm.ssigma_delta(obs_fc, sim_fc, ref_date=issue_date, reduction="none").value
   o, s = obs_fc[:10], sim_fc[:10]
   by_hand = np.sqrt(np.sum((o - s) ** 2) / (10 - 2)) / o.std(ddof=1)
   print(round(float(per_pair[0]), 4), round(float(by_hand), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2.2906 2.2906

Распределение по группам: на межени σ внутри десятидневной группы мала, и отношение велико.

.. testcode::

   per_group = per_pair.reshape(-1, 10)[:, 0]
   flood = np.array([obs_fc[i * 10:(i + 1) * 10].mean() > 100 for i in range(per_group.size)])
   print(round(float(np.nanmedian(per_group[flood])), 3), round(float(np.nanmedian(per_group[~flood])), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.696 1.459

На pandas метка группы передаётся тем же аргументом:

.. testcode::

   import pandas as pd

   print(round(float(hm.ssigma_delta(pd.Series(obs_fc), pd.Series(sim_fc), ref_date=issue_date)), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   1.49

Особенности применения в гидрологии
-------------------------------------

Внутри группы из десяти последовательных суток σ мала на межени и велика на половодье, поэтому одно и то же среднеквадратическое отклонение прогноза даёт разные отношения в разные сезоны. Сравнивать группы лучше внутри одного режима стока (см. пример выше).

Размер группы должен быть заметно больше ``m``; для групп из трёх–четырёх значений оценка σ очень неустойчива.

Связанные метрики
-------------------

- :ref:`metric-ssigma`
- :ref:`metric-forecast_verification_delta`
- :ref:`metric-forecast_verification`
- :ref:`metric-rmse`

Литература
------------

.. footbibliography::
