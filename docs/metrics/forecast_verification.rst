.. _metric-forecast_verification:

===========================================================
Оправдываемость прогноза по допустимой погрешности 0,674σ
===========================================================

Прогноз считается оправдавшимся, если абсолютная ошибка меньше 0,674 стандартного отклонения всех наблюдений :footcite:p:`georgievsky2007`. Для каждой пары получается 1, 0 или NaN, а итог это доля оправдавшихся прогнозов.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.forecast_verification(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.forecast_verification`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   V_i = \mathbb{1}\left(\left|O_i - S_i\right| < c\,\sigma_O\right), \qquad c = 0.674, \qquad \sigma_O = \sqrt{\frac{1}{n-1}\sum_{j=1}^{n}\left(O_j-\bar{O}\right)^2}

.. math::

   \text{result} = \frac{1}{n}\sum_{i=1}^{n} V_i

:math:`\mathbb{1}` индикатор, :math:`\sigma_O` стандартное отклонение (``ddof=1``) наблюдений вдоль ``axis`` (по всем элементам при ``axis=None``). Коэффициент 0,674 хранится в константе ``PROBABLE_ERROR_COEFFICIENT`` модуля ``hydrometrics.backends.numpy``; это вероятное отклонение нормального закона, 0,6745σ, округлённое до трёх знаков. Среднее берётся по парам, для которых :math:`V_i` определено. Текст Георгиевского и Шаночкина :footcite:p:`georgievsky2007` при подготовке документации прочитать не удалось, поэтому формулы ниже взяты из реализации, а градации качества не приводятся (см. :doc:`/user_guide/known_limits`).

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Неравенство строгое. Порог одинаков для всего ряда и не зависит ни от сезона, ни от заблаговременности. Это отличается от :ref:`metric-forecast_verification_delta`, где порог берётся по ошибкам внутри группы. Формула подтверждена автором библиотеки.

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

Результат лежит в [0, 1]. По парам функция возвращает 1.0, 0.0 или NaN; NaN означает, что ошибка или порог не определены. При постоянных наблюдениях порог равен нулю, строгое неравенство не выполняется ни для одной пары, и результат равен 0, а не NaN.

Интерпретация и критерии оценки
---------------------------------

Это доля попаданий в допуск, а не мера ошибки: 0,5 означает, что половина прогнозов уложилась в 0,674σ. Для нормального распределения ошибок с нулевым средним и стандартным отклонением, равным σ, ожидаемая доля около 0,5; это свойство нормального закона, а не порог качества.

Градации качества не приводятся: источник :footcite:p:`georgievsky2007` недоступен для чтения, пороги других источников подтвердить не удалось (см. :doc:`/user_guide/known_limits`).

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
     - Ось, вдоль которой считается σ. Результат сохраняет форму входа (флаги по парам).
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
     - По умолчанию без оси возвращается доля оправдавшихся прогнозов, а при заданной оси массив флагов формы входа; ``"mean"`` усредняет флаги.
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
     - ``axis=0``: numpy.ndarray (1096,3)
   * - pandas
     - numpy.float64
     - ``axis=0``: numpy.ndarray (1096,3)
   * - polars
     - numpy.float64
     - ``axis=0``: numpy.ndarray (1096,3)
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
     - 0.9982
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN (RuntimeWarning)
   * - ``inf`` в ``obs``
     - 0.9991
   * - постоянный ``obs`` (нулевая дисперсия)
     - 0
   * - ``obs`` и ``sim`` из одних нулей
     - 0
   * - отрицательные значения (ряд минус его среднее)
     - 0.9982
   * - пустой ввод
     - NaN (RuntimeWarning)
   * - разная длина ``obs`` и ``sim``
     - ValueError

Пара с пропуском в ``obs`` или ``sim`` при ``omit`` исключается, и σ считается по остальным наблюдениям; ``propagate`` даёт NaN; ``raise`` вызывает ``ValueError``. Значение ``inf`` в ``obs`` делает σ бесконечной, порог бесконечным, и все остальные прогнозы считаются оправдавшимися. Один элемент даёт NaN (σ не определена).

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

Суточный гидрограф и модельный ряд. Прогноз оправдался, если ошибка меньше :math:`0.674\,\sigma` (σ по всем наблюдениям). Результат это доля оправдавшихся прогнозов.

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

   result = hm.forecast_verification(q_obs, q_sim)
   print(f"fraction verified = {float(result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   fraction verified = 0.974

Независимый пересчёт и значения по парам (1 оправдался, 0 нет):

.. testcode::

   threshold = 0.674 * q_obs.std(ddof=1)
   by_hand = np.mean(np.abs(q_obs - q_sim) < threshold)
   flags = hm.forecast_verification(q_obs, q_sim, reduction="none").value
   print(round(float(by_hand), 3), flags[:8], round(float(threshold), 1))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.974 [1. 1. 1. 1. 1. 1. 1. 1.] 35.8

Порог постоянен для всего ряда, поэтому на межени прогнозы оправдываются легче, чем в половодье. Доля по сезонам:

.. testcode::

   in_flood = q_obs > 100
   print(round(float(flags[in_flood].mean()), 3), round(float(flags[~in_flood].mean()), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.707 1.0

Прогнозы на 1–10 суток: доля оправдавшихся по заблаговременности.

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

   fc_flags = hm.forecast_verification(obs_fc, sim_fc, reduction="none").value
   print(np.round(fc_flags.reshape(-1, 10).mean(axis=0), 2))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [1.   1.   1.   1.   1.   1.   0.98 0.96 0.96 0.94]

Вдоль оси σ считается по каждому створу, а результат остаётся массивом флагов; доля по створам берётся вручную:

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   flags_st = hm.forecast_verification(q_obs_st, q_sim_st, axis=0).value
   print(flags_st.shape, np.round(flags_st.mean(axis=0), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   (1096, 3) [0.974 0.946 0.998]

Особенности применения в гидрологии
-------------------------------------

Порог привязан к σ всего ряда, а σ определяется половодьем. В примере допуск равен 35.77 м³/с; доля оправдавшихся прогнозов 0.7071 при расходе выше 100 м³/с и 1 при меньшем. Оправдываемость по всему ряду смешивает два режима с разной долей попаданий.

Метрика бинарна и не показывает, насколько прогноз не попал. Дополняйте её :ref:`metric-rmse` и :ref:`metric-pbias`.

Связанные метрики
-------------------

- :ref:`metric-forecast_verification_delta`
- :ref:`metric-ssigma`
- :ref:`metric-ssigma_delta`
- :ref:`metric-accuracy`

Литература
------------

.. footbibliography::
