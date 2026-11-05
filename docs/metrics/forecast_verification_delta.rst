.. _metric-forecast_verification_delta:

===========================================================================
Оправдываемость прогноза по допустимой погрешности 0,674σ_Δ внутри группы
===========================================================================

Прогноз считается оправдавшимся, если абсолютная ошибка меньше 0,674 стандартного отклонения ошибок прогнозов внутри группы ``ref_date`` :footcite:p:`georgievsky2007`. Результат это доля оправдавшихся прогнозов.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.forecast_verification_delta(obs, sim, *, ref_date, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.forecast_verification_delta`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   V_i = \mathbb{1}\left(\left|O_i - S_i\right| < c\,\sigma_{\Delta,d(i)}\right), \qquad c = 0.674

.. math::

   \sigma_{\Delta,d} = \sqrt{\frac{1}{n_d-1}\sum_{j\in G_d}\left(\Delta_j-\bar{\Delta}_d\right)^2}, \qquad \Delta_j = S_j - O_j

:math:`G_d` группа с меткой :math:`d`, :math:`d(i)` метка группы пары :math:`i`, :math:`\Delta_j` ошибка прогноза, :math:`\bar{\Delta}_d` её среднее в группе, :math:`n_d` число действительных ошибок. Результат функции это среднее :math:`V_i` по парам, для которых оно определено. Группа с менее чем двумя действительными ошибками даёт NaN. Текст Георгиевского и Шаночкина :footcite:p:`georgievsky2007` при подготовке документации прочитать не удалось, поэтому формулы ниже взяты из реализации, а градации качества не приводятся (см. :doc:`/user_guide/known_limits`).

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Здесь :math:`\sigma_\Delta` это разброс ошибок прогноза внутри группы, то есть он зависит от того, насколько ошибки группы похожи друг на друга, а не от изменчивости самой величины. Из этого следует, что постоянное смещение не оправдывает прогноз: при одинаковых ошибках разброс равен нулю (см. пример). Формула подтверждена автором библиотеки и не менялась.

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

Результат лежит в [0, 1]. По парам возвращаются 1.0, 0.0 или NaN; NaN означает, что ошибка пропущена или в группе меньше двух действительных ошибок.

Интерпретация и критерии оценки
---------------------------------

Это доля попаданий в допуск, зависящий от группы. Значение 0,5 не имеет универсальной трактовки: допуск каждой группы определяется разбросом её собственных ошибок, поэтому группа с хорошим, но однородным прогнозом может иметь низкую долю. Градации качества не приводятся: источник :footcite:p:`georgievsky2007` недоступен для чтения (см. :doc:`/user_guide/known_limits`).

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
     - Метки групп (например дата выпуска) той же формы, что ``obs``. Другая форма вызывает ``ValueError``.
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
     - 0.4831
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN
   * - ``inf`` в ``obs``
     - 0.4848 (RuntimeWarning)
   * - постоянный ``obs`` (нулевая дисперсия)
     - 0.8066
   * - ``obs`` и ``sim`` из одних нулей
     - 0
   * - отрицательные значения (ряд минус его среднее)
     - 0.4836
   * - пустой ввод
     - NaN
   * - разная длина ``obs`` и ``sim``
     - ValueError

При ``omit`` пары с пропуском исключаются из своей группы, ``propagate`` возвращает NaN (в результате по парам NaN стоит на месте пропуска); ``raise`` вызывает ``ValueError``. Группа из одной пары даёт NaN. Ось и веса не поддерживаются.

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

Прогнозы на 1–10 суток, выпускаемые каждые 10 суток. Порог для каждого выпуска равен :math:`0.674` от стандартного отклонения ошибок внутри этого выпуска.

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

   result = hm.forecast_verification_delta(obs_fc, sim_fc, ref_date=issue_date)
   print(f"fraction verified = {float(result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   fraction verified = 0.448

Пересчёт для первой группы и доля оправдавшихся по заблаговременности:

.. testcode::

   flags = hm.forecast_verification_delta(obs_fc, sim_fc, ref_date=issue_date, reduction="none").value
   err = sim_fc[:10] - obs_fc[:10]
   by_hand = np.abs(err) < 0.674 * err.std(ddof=1)
   print(by_hand.astype(float), flags[:10])
   print(np.round(flags.reshape(-1, 10).mean(axis=0), 2))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [1. 0. 0. 1. 1. 1. 0. 0. 0. 0.] [1. 0. 0. 1. 1. 1. 0. 0. 0. 0.]
   [0.84 0.73 0.6  0.49 0.51 0.36 0.22 0.24 0.25 0.24]

Если ошибки группы почти постоянны (смещение без разброса), порог близок к нулю и прогнозы не оправдываются, хотя ошибка мала. Это свойство определения, а не сбой:

.. testcode::

   steady = hm.forecast_verification_delta(obs_fc[:10], obs_fc[:10] + 0.5, ref_date=issue_date[:10], reduction="none")
   print(steady.value)

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]

На pandas метки группы передаются тем же аргументом:

.. testcode::

   import pandas as pd

   print(round(float(hm.forecast_verification_delta(pd.Series(obs_fc), pd.Series(sim_fc), ref_date=issue_date)), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.448

Особенности применения в гидрологии
-------------------------------------

Метрика оценивает однородность ошибок в группе, а не их величину: группа с большим, но стабильным смещением не оправдывается, а группа с малым, но неустойчивым разбросом оправдывается частично. Для оценки смещения используйте :ref:`metric-pbias` или :ref:`metric-bias`.

При малых группах (до 5–10 значений) оценка :math:`\sigma_\Delta` ненадёжна, и доля оправдавшихся прогнозов сильно колеблется между выпусками.

Связанные метрики
-------------------

- :ref:`metric-forecast_verification`
- :ref:`metric-ssigma_delta`
- :ref:`metric-ssigma`
- :ref:`metric-bias`

Литература
------------

.. footbibliography::
