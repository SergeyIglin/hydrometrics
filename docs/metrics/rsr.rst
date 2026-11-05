.. _metric-rsr:

===========================================================
Отношение RMSE к стандартному отклонению наблюдений (RSR)
===========================================================

RSR это :ref:`metric-rmse`, делённая на стандартное отклонение наблюдений :footcite:p:`moriasi2007`. Метрика безразмерна и сочетает показатель ошибки с нормировкой на изменчивость наблюдений.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.rsr(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict")

Запись в справочнике API: :func:`hydrometrics.rsr`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{RSR} = \frac{\mathrm{RMSE}}{\sigma_O} = \frac{\sqrt{\frac{1}{n}\sum_{i} w_i\,\left(O_i - S_i\right)^2}}{\sqrt{\frac{1}{n-1}\sum_{i} w_i\,\left(O_i - \bar{O}\right)^2}}

:math:`\sigma_O` стандартное отклонение наблюдений с ``ddof=1``, :math:`\bar{O}` среднее наблюдений, :math:`w_i` вес (в записи для случая без весов).

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Moriasi et al. :footcite:p:`moriasi2007` записывают RSR как отношение корней сумм квадратов без делителей. Библиотека использует RMSE с делителем :math:`n` и стандартное отклонение с делителем :math:`n-1`, поэтому значение меньше формулы Moriasi et al. в :math:`\sqrt{n/(n-1)}` раз; для длинных рядов разница пренебрежимо мала (пример ниже).

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

Значение 0 означает нулевую ошибку. Значение 1 соответствует ``NSE`` около 0 при большом :math:`n`. Верхней границы нет. При постоянных наблюдениях результат NaN.

Интерпретация и критерии оценки
---------------------------------

Moriasi et al. :footcite:p:`moriasi2007` (таблица 4) оценивают RSR так: очень хорошо при :math:`0 \le \mathrm{RSR} \le 0.50`, хорошо при 0,50–0,60, удовлетворительно при 0,60–0,70, неудовлетворительно выше 0,70. Эти значения даны для месячного шага и для непрерывного долгосрочного моделирования водосборов; авторы подчёркивают, что градации следует корректировать с учётом качества данных и временного шага.

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
     - 0.2169
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
     - 0.2169
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

   result = hm.rsr(q_obs, q_sim)
   print(f"rsr = {float(result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   rsr = 0.215

Связь с NSE следует из определений: :math:`\mathrm{RSR}^2 = (1-\mathrm{NSE})\,(n-1)/n`. Формула Moriasi et al. без поправки ``ddof`` даёт чуть большее значение:

.. testcode::

   n = q_obs.size
   nse_value = float(hm.nse(q_obs, q_sim))
   print(round(float(hm.rsr(q_obs, q_sim)), 5), round(float(np.sqrt((1 - nse_value) * (n - 1) / n)), 5))
   moriasi = np.sqrt(np.sum((q_obs - q_sim) ** 2)) / np.sqrt(np.sum((q_obs - q_obs.mean()) ** 2))
   print(round(float(moriasi), 5))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.21496 0.21496
   0.21506

По створам:

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   per_station = hm.rsr(q_obs_st, q_sim_st, axis=0, reduction="none")
   print(np.round(per_station.value, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.215 0.282 0.192]

По водным годам:

.. testcode::

   import pandas as pd

   df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
   # Водный год начинается 1 октября и назван по году окончания
   df["water_year"] = df.index.year + (df.index.month >= 10)

.. testcode::

   by_year = hm.compute_grouped(hm.rsr, df, "q_obs", "q_sim", group_by="water_year")
   for (water_year,), value in by_year:
       print(int(water_year), round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2011 0.224
   2012 0.208
   2013 0.212

На xarray ось задаётся именем измерения, а координаты створов сохраняются в результате:

.. testcode::

   import xarray as xr

   coords = {"time": dates, "station": ["upper", "middle", "lower"]}
   obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
   sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
   by_station = hm.rsr(obs_da, sim_da, dim="time").value
   print(by_station.round(3).to_series().to_dict())

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   {'upper': 0.215, 'middle': 0.282, 'lower': 0.192}

Особенности применения в гидрологии
-------------------------------------

RSR и NSE связаны взаимно однозначно, поэтому не дают независимой информации о качестве модели: это два способа записать одну и ту же сумму квадратов. Градации Moriasi et al. для NSE и RSR согласованы между собой.

Как и NSE, RSR определяется пиками и не видит смещения при малых расходах; дополняйте её :ref:`metric-pbias`.

Связанные метрики
-------------------

- :ref:`metric-rmse`
- :ref:`metric-nse`
- :ref:`metric-nrmse`
- :ref:`metric-pbias`

Литература
------------

.. footbibliography::
