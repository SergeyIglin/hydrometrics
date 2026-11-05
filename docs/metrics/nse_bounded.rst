.. _metric-nse_bounded:

====================================================
Ограниченный критерий Нэша–Сатклиффа (nse_bounded)
====================================================

``nse_bounded`` это преобразование :ref:`metric-nse`, которое переводит неограниченную снизу шкалу в интервал :math:`(-1, 1]`. Значение 0 остаётся ориентиром модели, равной постоянному прогнозу средним.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.nse_bounded(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.nse_bounded`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{NSE}_b = \frac{\mathrm{NSE}}{2 - \mathrm{NSE}}

:math:`\mathrm{NSE}` значение :ref:`metric-nse` (без ``norm``) для тех же данных и тех же весов.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Подтверждённого первоисточника именно этой формы найти не удалось (см. :doc:`/user_guide/known_limits`). В литературе встречается и другая форма, :math:`1/(2-\mathrm{NSE})` с значениями в :math:`(0, 1]`, равная 0,5 при ``NSE = 0``; её источник также не подтверждён. Здесь реализована форма :math:`\mathrm{NSE}/(2-\mathrm{NSE})`, и при сравнении с опубликованными значениями нужно проверять, какая форма использована.

Диапазон значений и оптимум
-----------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table

   * - Диапазон
     - Оптимум
     - Направление
   * - (-1, 1]
     - 1
     - больше лучше

Значение 1 достигается при ``NSE = 1``. При ``NSE`` → −∞ значение стремится к −1, но не достигает его. Если NSE не определена (постоянные наблюдения), результат NaN.

Интерпретация и критерии оценки
---------------------------------

Градации для ``nse_bounded`` подтвердить не удалось. Пересчёт градаций Moriasi et al. :footcite:p:`moriasi2007` из NSE в ``nse_bounded`` возможен через формулу, но это расчёт читателя, а не опубликованная шкала.

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
     - 0.9101
   * - NaN в одной паре, ``nan_policy="propagate"``
     - NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - NaN (RuntimeWarning)
   * - ``inf`` в ``obs``
     - NaN (RuntimeWarning)
   * - постоянный ``obs`` (нулевая дисперсия)
     - NaN
   * - ``obs`` и ``sim`` из одних нулей
     - NaN
   * - отрицательные значения (ряд минус его среднее)
     - 0.91
   * - пустой ввод
     - NaN (RuntimeWarning)
   * - разная длина ``obs`` и ``sim``
     - ValueError

При умолчании ``nan_policy="omit"`` пары с пропуском в ``obs`` или ``sim`` удаляются целиком, в том числе при заданной оси. ``"propagate"`` возвращает NaN, если в ряду (или в срезе вдоль оси) есть пропуск, ``"raise"`` вызывает ``ValueError``. Значение ``inf`` пропуском не считается; результат для него показан в таблице.

Постоянный ряд даёт NaN, потому что стандартное отклонение или дисперсия равны нулю.

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

   result = hm.nse_bounded(q_obs, q_sim)
   print(f"nse_bounded = {float(result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   nse_bounded = 0.912

Метрика монотонно зависит от NSE, поэтому ранжирует модели так же; она лишь сжимает шкалу в :math:`(-1, 1]`.

.. testcode::

   nse_value = float(hm.nse(q_obs, q_sim))
   print(round(float(hm.nse_bounded(q_obs, q_sim)), 4), round(nse_value / (2 - nse_value), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.9116 0.9116

По створам:

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   per_station = hm.nse_bounded(q_obs_st, q_sim_st, axis=0, reduction="none")
   print(np.round(per_station.value, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.912 0.853 0.929]

По водным годам:

.. testcode::

   import pandas as pd

   df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
   # Водный год начинается 1 октября и назван по году окончания
   df["water_year"] = df.index.year + (df.index.month >= 10)

.. testcode::

   by_year = hm.compute_grouped(hm.nse_bounded, df, "q_obs", "q_sim", group_by="water_year")
   for (water_year,), value in by_year:
       print(int(water_year), round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2011 0.905
   2012 0.917
   2013 0.914

На xarray ось задаётся именем измерения, а координаты створов сохраняются в результате:

.. testcode::

   import xarray as xr

   coords = {"time": dates, "station": ["upper", "middle", "lower"]}
   obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
   sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
   by_station = hm.nse_bounded(obs_da, sim_da, dim="time").value
   print(by_station.round(3).to_series().to_dict())

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   {'upper': 0.912, 'middle': 0.853, 'lower': 0.929}

Особенности применения в гидрологии
-------------------------------------

Сжатие шкалы делает ``nse_bounded`` удобной для усреднения по большому числу створов: один створ с очень плохой моделью не тянет среднее в минус бесконечность. Цена за это в том, что различия между плохими моделями почти исчезают: при ``NSE`` от −10 до −100 значение ``nse_bounded`` лежит между −0,83 и −0,98.

Связанные метрики
-------------------

- :ref:`metric-nse`
- :ref:`metric-kge_2012`
- :ref:`metric-log_nse`

В литературе именем nNSE обозначают форму :math:`1/(2-\mathrm{NSE})` со значениями в :math:`(0, 1]`; ``nse_bounded`` считает другую величину, :math:`\mathrm{NSE}/(2-\mathrm{NSE})`, и сравнивать их значения нельзя.

Литература
------------

.. footbibliography::
