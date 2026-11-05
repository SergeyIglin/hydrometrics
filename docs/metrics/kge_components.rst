.. _metric-kge_components:

=============================
Компоненты KGE (r, α, β, γ)
=============================

Функция возвращает словарь компонент, из которых строятся :ref:`metric-kge_2009` и :ref:`metric-kge_2012`: корреляцию :math:`r`, отношение стандартных отклонений :math:`\alpha`, отношение средних :math:`\beta` и отношение коэффициентов вариации :math:`\gamma`.

Сигнатура
-----------

.. code-block:: python

   hydrometrics.kge_components(obs, sim, *, axis=None, nan_policy="omit",
       sample_weight=None, weight=None, reduction=None, align="strict", version="2012")

Запись в справочнике API: :func:`hydrometrics.kge_components`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.

Математическое определение
----------------------------

.. math::

   r,\qquad \alpha = \frac{\sigma_S}{\sigma_O},\qquad \beta = \frac{\mu_S}{\mu_O},\qquad \gamma = \frac{\sigma_S/\mu_S}{\sigma_O/\mu_O}

Обозначения как на странице :ref:`metric-kge_2009`. Ключ ``gamma`` присутствует только при ``version=\"2012\"``. Каждое значение словаря обрабатывается так же, как результат отдельной компоненты: :ref:`metric-r_component`, :ref:`metric-alpha_component`, :ref:`metric-beta_component`, :ref:`metric-gamma_component`.

Отличия от классического определения
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Версия влияет только на состав словаря: значения :math:`r`, :math:`\alpha` и :math:`\beta` от неё не зависят. Для ``version="2012"`` ключ ``alpha`` возвращается для информации, он не входит в :ref:`metric-kge_2012`.

Диапазон значений и оптимум
-----------------------------

.. list-table::
   :header-rows: 1
   :class: hm-table

   * - Диапазон
     - Оптимум
     - Направление
   * - по компонентам
     - 1
     - лучше ближе к 1

Оптимум каждой компоненты равен 1. Диапазоны: :math:`r` в [-1, 1], :math:`\alpha` не меньше 0, :math:`\beta` и :math:`\gamma` определены при ненулевых средних наблюдений и модели. Недопустимое значение ``version`` вызывает ``ValueError``.

Интерпретация и критерии оценки
---------------------------------

Компоненты интерпретируются относительно 1: :math:`\beta > 1` означает завышение объёма, :math:`\alpha < 1` занижение изменчивости (часто срезанные пики), :math:`r` показывает совпадение фазы и формы. Пороги качества не приняты.

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
   * - ``version``
     - str
     - ``"2012"``
     - ``"2009"`` или ``"2012"``. Определяет состав словаря: ``gamma`` только для ``"2012"``.

Возвращаемое значение
-----------------------

На всех бэкендах функция возвращает :class:`~hydrometrics.MetricResult` со словарём в поле ``value``; значения словаря свёрнуты по тому же правилу ``reduction``.

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 15 35 50

   * - Бэкенд
     - Одномерный ввод
     - По оси, ввод формы (1096, 3)
   * - numpy
     - dict
     - ``axis=0``: dict
   * - pandas
     - dict
     - ``axis=0``: dict
   * - polars
     - dict
     - ``axis=0``: dict
   * - xarray
     - dict
     - ``dim="time"``: dict

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
     - r = 0.9788
   * - NaN в одной паре, ``nan_policy="propagate"``
     - r = NaN
   * - NaN в одной паре, ``nan_policy="raise"``
     - ValueError
   * - все ``obs`` равны NaN
     - r = NaN (RuntimeWarning)
   * - ``inf`` в ``obs``
     - r = NaN (RuntimeWarning)
   * - постоянный ``obs`` (нулевая дисперсия)
     - r = NaN
   * - ``obs`` и ``sim`` из одних нулей
     - r = NaN
   * - отрицательные значения (ряд минус его среднее)
     - r = 0.9787
   * - пустой ввод
     - r = NaN (RuntimeWarning)
   * - разная длина ``obs`` и ``sim``
     - ValueError

При умолчании ``nan_policy="omit"`` пары с пропуском в ``obs`` или ``sim`` удаляются целиком, в том числе при заданной оси. ``"propagate"`` возвращает NaN, если в ряду (или в срезе вдоль оси) есть пропуск, ``"raise"`` вызывает ``ValueError``. Значение ``inf`` пропуском не считается; результат для него показан в таблице.

Постоянный ряд даёт NaN для :math:`r`, :math:`\alpha` и :math:`\gamma`, поскольку они используют стандартное отклонение.

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

На всех бэкендах значение это словарь, значения которого имеют тип, зависящий от бэкенда (на xarray это ``DataArray``).

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

   parts = hm.kge_components(q_obs, q_sim).value
   print({name: round(float(value), 3) for name, value in parts.items()})

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   {'r': 0.981, 'alpha': 0.886, 'beta': 0.97, 'gamma': 0.913}

Версия 2009 г. возвращает три компоненты, без :math:`\gamma`:

.. testcode::

   parts_2009 = hm.kge_components(q_obs, q_sim, version="2009").value
   print(list(parts_2009))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   ['r', 'alpha', 'beta']

По створам с ``reduction="none"`` каждое значение словаря это массив по створам:

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   per_station = hm.kge_components(q_obs_st, q_sim_st, axis=0, reduction="none").value
   print({name: np.round(value, 3) for name, value in per_station.items()})

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   {'r': array([0.981, 0.981, 0.981]), 'alpha': array([0.886, 0.775, 0.99 ]), 'beta': array([0.97 , 0.991, 1.001]), 'gamma': array([0.913, 0.782, 0.989])}

На xarray компоненты возвращаются как ``DataArray`` по оставшимся измерениям:

.. testcode::

   import xarray as xr

   coords = {"time": dates, "station": ["upper", "middle", "lower"]}
   obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
   sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
   beta_da = hm.kge_components(obs_da, sim_da, dim="time").value["beta"]
   print(beta_da.round(3).to_series().to_dict())

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   {'upper': 0.97, 'middle': 0.991, 'lower': 1.001}

Особенности применения в гидрологии
-------------------------------------

Сами компоненты полезнее итога: по ним видно, чем плоха модель. Типичная картина для калибровки по NSE это :math:`\alpha < 1` при :math:`\beta` около 1: пики срезаны, объём сохранён (в примере выше :math:`\alpha \approx 0.89`).

Связанные метрики
-------------------

- :ref:`metric-kge_2009`
- :ref:`metric-kge_2012`
- :ref:`metric-r_component`
- :ref:`metric-alpha_component`
- :ref:`metric-beta_component`
- :ref:`metric-gamma_component`

Литература
------------

.. footbibliography::
