.. _metric-log_nse:

==========================================================
Критерий Нэша–Сатклиффа для логарифмов расходов (logNSE)
==========================================================

logNSE это :ref:`metric-nse`, вычисленная для натуральных логарифмов расходов. Логарифм увеличивает вклад малых значений, поэтому метрика отражает качество воспроизведения межени.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.log_nse(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict", eps=1e-10)

Запись в справочнике API: :func:`hydrometrics.log_nse`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   \mathrm{logNSE} = 1 - \frac{\sum_{i} w_i\,\left(\ln(O_i+\varepsilon) - \ln(S_i+\varepsilon)\right)^2}{\sum_{i} w_i\,\left(\ln(O_i+\varepsilon) - \overline{\ln(O+\varepsilon)}\right)^2}

:math:`\varepsilon` добавка ``eps`` (по умолчанию :math:`10^{-10}`), :math:`w_i` вес, черта обозначает (взвешенное) среднее логарифмов наблюдений. Пара, для которой :math:`O_i+\varepsilon\le 0` или :math:`S_i+\varepsilon\le 0`, не имеет логарифма и исключается из обеих сумм.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

В коде источником указана Krause et al. :footcite:p:`krause2005`, где логарифмическая форма рассмотрена в разделе о NSE для логарифмированных значений. Добавка :math:`\varepsilon` фиксированная и абсолютная, а не доля от среднего расхода; в практике калибровки встречаются и относительные добавки.

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

Верхняя граница достигается при совпадении рядов, снизу значение не ограничено. Значение 0 соответствует прогнозу средним логарифма наблюдений, то есть геометрическим средним. При постоянных наблюдениях результат NaN.

Интерпретация и критерии оценки
---------------------------------

Общепринятых градаций для logNSE нет. Градации Moriasi et al. :footcite:p:`moriasi2007` относятся к NSE на нелогарифмированных данных (месячный шаг) и на logNSE не переносятся.

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
   * - ``eps``
     - float
     - ``1e-10``
     - Добавка перед логарифмом. Исключает логарифм нуля; влияет на результат при нулевых и очень малых расходах.

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
     - 0.8676
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
     - 0.682
   * - пустой ввод
     - NaN (RuntimeWarning)
   * - разная длина ``obs`` и ``sim``
     - ValueError

При умолчании ``nan_policy="omit"`` пары с пропуском в ``obs`` или ``sim`` удаляются целиком, в том числе при заданной оси. ``"propagate"`` возвращает NaN, если в ряду (или в срезе вдоль оси) есть пропуск, ``"raise"`` вызывает ``ValueError``. Значение ``inf`` пропуском не считается; результат для него показан в таблице.

Отрицательные значения не имеют логарифма: пара исключается из расчёта, а если пар не остаётся, результат NaN. Ряд из нулей даёт NaN.

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

   result = hm.nse(q_obs, q_sim)
   log_result = hm.log_nse(q_obs, q_sim)
   print(f"NSE = {float(result):.3f}, log NSE = {float(log_result):.3f}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   NSE = 0.954, log NSE = 0.639

Одно нулевое значение расхода в наблюдениях при ``eps=1e-10`` превращается в :math:`\ln 10^{-10}\approx-23`, и результат резко падает. Аргумент ``eps`` задаёт добавку явно; ниже она равна 1 % от среднего расхода:

.. testcode::

   q_dry = q_obs.copy()
   q_dry[10] = 0.0  # одни сутки пересыхания
   default_eps = float(hm.log_nse(q_dry, q_sim))
   scaled_eps = float(hm.log_nse(q_dry, q_sim, eps=0.01 * q_obs.mean()))
   print(round(float(hm.log_nse(q_obs, q_sim)), 3), round(default_eps, 3), round(scaled_eps, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.639 0.32 0.671

По створам:

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   per_station = hm.log_nse(q_obs_st, q_sim_st, axis=0, reduction="none")
   print(np.round(per_station.value, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.639 0.812 0.602]

По водным годам:

.. testcode::

   import pandas as pd

   df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
   # Водный год начинается 1 октября и назван по году окончания
   df["water_year"] = df.index.year + (df.index.month >= 10)

.. testcode::

   by_year = hm.compute_grouped(hm.log_nse, df, "q_obs", "q_sim", group_by="water_year")
   for (water_year,), value in by_year:
       print(int(water_year), round(float(value), 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2011 0.524
   2012 0.669
   2013 0.724

На xarray ось задаётся именем измерения, а координаты створов сохраняются в результате:

.. testcode::

   import xarray as xr

   coords = {"time": dates, "station": ["upper", "middle", "lower"]}
   obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
   sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
   by_station = hm.log_nse(obs_da, sim_da, dim="time").value
   print(by_station.round(3).to_series().to_dict())

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   {'upper': 0.639, 'middle': 0.812, 'lower': 0.602}

Особенности применения в гидрологии
-------------------------------------

Логарифм сжимает пики и растягивает межень, поэтому ``log_nse`` оценивает ту часть гидрографа, которую :ref:`metric-nse` почти не видит. В примере ``NSE = 0.9537``, а ``log_nse = 0.6389`` на тех же данных: модель хуже воспроизводит межень, чем пик.

Результат зависит от добавки ``eps``, особенно при нулевых расходах. В примере одни нулевые сутки опускают ``log_nse`` с 0.6389 до 0.3203, а добавка в 1 % среднего даёт 0.6706. Выбор добавки нужно указывать при публикации результатов. Krause et al. рассматривают логарифмическую форму для оценки низких расходов :footcite:p:`krause2005`.

Связанные метрики
-------------------

- :ref:`metric-nse`
- :ref:`metric-modified_nse`
- :ref:`metric-ve`
- :ref:`metric-kge_2012`

Литература
------------

.. footbibliography::
