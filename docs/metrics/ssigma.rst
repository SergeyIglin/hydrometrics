.. _metric-ssigma:

=======================================================================
Отношение среднеквадратической ошибки к стандартному отклонению (S/σ)
=======================================================================

S/σ это среднеквадратическая ошибка, скорректированная на число параметров, в долях стандартного отклонения наблюдений :footcite:p:`georgievsky2007`. Значение меньше 1 означает, что ошибка меньше изменчивости наблюдений.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.ssigma(obs, sim, *, m=2, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.ssigma`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \frac{S}{\sigma} = \frac{\sqrt{\dfrac{1}{n-m}\sum_{i=1}^{n}\left(O_i-S_i\right)^2}}{\sqrt{\dfrac{1}{n-1}\sum_{i=1}^{n}\left(O_i-\bar{O}\right)^2}}

:math:`O_i` наблюдённое, :math:`S_i` модельное значение, :math:`n` число действительных пар, :math:`m` число параметров модели или прогностической зависимости (аргумент ``m``, по умолчанию 2). Суммирование идёт по оси ``axis``, при ``axis=None`` по всем элементам. Числитель обозначают :math:`S`, знаменатель :math:`\sigma`. Текст Георгиевского и Шаночкина :footcite:p:`georgievsky2007` при подготовке документации прочитать не удалось, поэтому формулы ниже взяты из реализации, а градации качества не приводятся (см. :doc:`/user_guide/known_limits`).

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Знаменатель использует несмещённую оценку (``ddof=1``), числитель делитель :math:`n-m`. Из этих определений следует связь с :ref:`metric-nse`: :math:`(S/\sigma)^2 = (1-\mathrm{NSE})\,(n-1)/(n-m)`. При :math:`m=1` метрика равна :math:`\sqrt{1-\mathrm{NSE}}`.

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

Значение 0 означает нулевую ошибку. Верхней границы нет. Если наблюдения постоянны с точностью до округления, σ равно нулю и результат NaN. Без оси при :math:`n \le m` вызывается ``ValueError``; вдоль оси такой срез даёт NaN.

Интерпретация и критерии оценки
---------------------------------

Значение 1 соответствует, при :math:`n \gg m`, ``NSE`` около нуля: ошибка равна изменчивости наблюдений. Это следует из связи с NSE выше.

Градации качества для S/σ здесь не приводятся: источник :footcite:p:`georgievsky2007` не был доступен, а другие источники, где пороги названы прямо, подтвердить не удалось (см. :doc:`/user_guide/known_limits`). Любой порог зависит от типа прогноза, заблаговременности и длины ряда.

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
   * - ``m``
     - int
     - ``2``
     - Число параметров, уменьшающее степени свободы ошибки. Конечное неотрицательное число (int или float); отрицательное значение, NaN или inf вызывает ``ValueError``, не число вызывает ``TypeError``.
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
     - 0.2171
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - ValueError
   * - ``inf`` в ``obs``
     - NaN
   * - постоянный ``obs`` (нулевая дисперсия)
     - NaN
   * - ``obs`` и ``sim`` из одних нулей
     - NaN
   * - отрицательные значения (ряд минус его среднее)
     - 0.2171
   * - пустой ввод
     - ValueError
   * - разная длина ``obs`` и ``sim``
     - ValueError

При ``omit`` пары с пропуском в ``obs`` или ``sim`` удаляются, ``n`` считается по оставшимся. ``propagate`` возвращает NaN, ``raise`` вызывает ``ValueError``.

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

Суточный гидрограф за три водных года, расходы в м³/с.

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

   result = hm.ssigma(q_obs, q_sim)
   print(f"S/sigma = {float(result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   S/sigma = 0.215

Связь с NSE следует из формул: :math:`S/\sigma = \sqrt{(1-\mathrm{NSE})\,(n-1)/(n-m)}`. Проверка на тех же данных:

.. testcode::

   n, m = q_obs.size, 2
   nse = float(hm.nse(q_obs, q_sim))
   print(round(float(np.sqrt((1 - nse) * (n - 1) / (n - m))), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.215

По створам вдоль оси; срез, где пар не больше ``m``, даёт NaN:

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   per_station = hm.ssigma(q_obs_st, q_sim_st, axis=0)
   print(np.round(per_station.value, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.215 0.282 0.192]

Число параметров ``m`` уменьшает число степеней свободы ошибки. Это должно быть конечное неотрицательное число; влияние видно на коротком ряду:

.. testcode::

   short_obs, short_sim = q_obs[:30], q_sim[:30]
   for m in (0, 2, 5):
       print(m, round(float(hm.ssigma(short_obs, short_sim, m=m)), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0 2.437
   2 2.522
   5 2.669

По водным годам:

.. testcode::

   import pandas as pd

   df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
   # Водный год начинается 1 октября и назван по году окончания
   df["water_year"] = df.index.year + (df.index.month >= 10)

.. testcode::

   by_year = hm.compute_grouped(hm.ssigma, df, "q_obs", "q_sim", group_by="water_year")
   for (water_year,), value in by_year:
       print(int(water_year), round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2011 0.224
   2012 0.209
   2013 0.213

Особенности применения в гидрологии
-------------------------------------

S/σ, как и NSE, построена на квадратах ошибок и потому определяется крупными расходами; у периодов межени σ мало, и тот же абсолютный промах даёт гораздо большее отношение. Поэтому значение по сезонам и по водным годам лучше считать отдельно.

Для рядов с внутригодовым ходом σ включает сезонную изменчивость, и метрика может быть низкой только потому, что сезонный ход воспроизведён. Для прогнозов с заблаговременностью смотрите :ref:`metric-ssigma_delta`, где σ берётся внутри группы.

Связанные метрики
-------------------

- :ref:`metric-ssigma_delta`
- :ref:`metric-nse`
- :ref:`metric-rmse`
- :ref:`metric-rsr`
- :ref:`metric-forecast_verification`

Литература
------------

.. footbibliography::
