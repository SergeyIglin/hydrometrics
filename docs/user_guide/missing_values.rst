.. _missing-values:

===================
Пропуски в данных
===================

В рядах наблюдений расходов воды пропуски обычны: сбой датчика, ледовые явления, период без измерений. Все метрики обрабатывают их одним способом, за который отвечает аргумент ``nan_policy``. Пара ``(obs[i], sim[i])`` считается недействительной, если NaN стоит в ``obs``, в ``sim`` или в весе ``sample_weight``.

Три политики
--------------

.. list-table::
   :header-rows: 1
   :class: hm-table
   :widths: 22 78

   * - Значение
     - Действие
   * - ``"omit"`` (умолчание)
     - Недействительные пары исключаются целиком, в том числе при заданной оси. Результат совпадает с расчётом по заранее отфильтрованным парам. Число удалённых пар записано в ``nan_info``.
   * - ``"propagate"``
     - Расчёт идёт по тем же данным, но результат (или срез вдоль оси), в котором был пропуск, получает NaN. По парам NaN стоит только на затронутых местах.
   * - ``"raise"``
     - ``ValueError`` при любом NaN в ``obs``, ``sim`` или весах.

Любое другое значение вызывает ``ValueError``.

Сравнение политик на одном примере
------------------------------------

В наблюдениях месяц без измерений, в модельном ряду десять пропущенных суток. Для трёх метрик показаны результаты при ``omit``, расчёт по заранее отфильтрованным парам, ``propagate`` и ``raise``.

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

   q_obs_gap, q_sim_gap = q_obs.copy(), q_sim.copy()
   q_obs_gap[100:130] = np.nan
   q_sim_gap[400:410] = np.nan
   valid = ~(np.isnan(q_obs_gap) | np.isnan(q_sim_gap))

   for name in ("nse", "mae", "kge_2012"):
       metric = getattr(hm, name)
       omit = float(metric(q_obs_gap, q_sim_gap))
       prefiltered = float(metric(q_obs_gap[valid], q_sim_gap[valid]))
       propagate = float(metric(q_obs_gap, q_sim_gap, nan_policy="propagate"))
       try:
           metric(q_obs_gap, q_sim_gap, nan_policy="raise")
       except ValueError:
           raised = "ValueError"
       print(f"{name:9s} omit={omit:.4f} prefiltered={prefiltered:.4f} propagate={propagate} raise={raised}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   nse       omit=0.9546 prefiltered=0.9546 propagate=nan raise=ValueError
   mae       omit=7.6977 prefiltered=7.6977 propagate=nan raise=ValueError
   kge_2012  omit=0.9074 prefiltered=0.9074 propagate=nan raise=ValueError

``omit`` и расчёт по отфильтрованным парам совпадают до последнего знака. ``propagate`` удобен, когда пропуск должен делать результат недействительным, например при проверке полноты ряда, а ``raise`` в конвейерах, где пропусков быть не должно.

Сведения об удалении: nan_info
--------------------------------

.. testcode::

   result = hm.nse(q_obs_gap, q_sim_gap)
   print(result.nan_info)

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   {'policy': 'omit', 'n_nan_removed': 40, 'n_total': 1096}

``n_nan_removed`` равно числу удалённых пар при ``omit`` и нулю при ``propagate`` и ``raise``; ``n_total`` равно числу элементов ``obs``.

Попарное удаление вдоль оси
-----------------------------

При заданной оси пары исключаются внутри каждого среза. Столбец с пропусками не влияет на соседние столбцы:

.. testcode::

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   obs_gap = q_obs_st.copy()
   obs_gap[200:260, 1] = np.nan  # gap only at the middle gauge
   per_gauge = hm.nse(obs_gap, q_sim_st, axis=0)
   print(np.round(per_gauge.value, 4))
   print(per_gauge.nan_info)

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [0.9537 0.9128 0.9632]
   {'policy': 'omit', 'n_nan_removed': 60, 'n_total': 3288}

Что не считается пропуском
----------------------------

Значение ``inf`` пропуском не является: оно участвует в расчёте и обычно даёт ``inf`` или NaN в результате. Если бесконечности попали в ряд из-за деления на ноль, замените их на NaN до вызова.

.. testcode::

   q_inf = q_obs.copy()
   q_inf[10] = np.inf
   print(float(hm.nse(q_inf, q_sim)))
   print(round(float(hm.nse(np.where(np.isinf(q_inf), np.nan, q_inf), q_sim)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   nan
   0.9538

Коды пропуска вроде ``-999`` библиотека не распознаёт: заменяйте их на NaN до вызова (``numpy.where`` или ``df.replace(-999, float("nan"))``).

.. testcode::

   q_coded = q_obs.copy()
   q_coded[100:130] = -999
   q_clean = np.where(q_coded == -999, np.nan, q_coded)
   print(round(float(hm.nse(q_clean, q_sim)), 4), round(float(hm.nse(q_obs_gap, q_sim)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.9544 0.9544

Веса, ансамбли и вспомогательные массивы
------------------------------------------

NaN в весе делает пару недействительной так же, как NaN в данных:

.. testcode::

   weights = np.ones_like(q_obs)
   weights[50:60] = np.nan
   with_weights = hm.nse(q_obs, q_sim, sample_weight=weights)
   kept = ~np.isnan(weights)
   print(round(float(with_weights), 6), round(float(hm.nse(q_obs[kept], q_sim[kept])), 6))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   0.953835 0.953835

Для ансамбля строка недействительна, если NaN стоит в ``obs`` или во всех членах сразу. Пропуск в части членов не исключает строку, члены с NaN просто не участвуют в оценке:

.. testcode::

   ens_rng = np.random.default_rng(7)
   members = 1.05 * q_obs[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.15 * q_obs[:, None])
   members_gap = members.copy()
   members_gap[5, :4] = np.nan
   print(round(float(hm.crps(q_obs, members)), 4), round(float(hm.crps(q_obs, members_gap)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2.06 2.06

Массивы, которые задают группы или даты (``gauge``, ``ref_date``, ``dates``), при ``omit`` не фильтруются: ядра метрик пропускают позиции с NaN сами, поэтому длина этих массивов всегда равна длине ``obs``.

Как выбрать политику
----------------------

Для оценки модели по ряду с пропусками подходит умолчание ``omit``, но число удалённых пар нужно смотреть в ``nan_info``: метрика, посчитанная по половине ряда, сравнима с метрикой по полному ряду только при случайном характере пропусков. Пропуски в наблюдениях чаще приходятся на зиму и на пики, и тогда ``omit`` смещает оценку в сторону сезонов, где измерения были. Ряд, в котором пропуски не должны встречаться, лучше проверять политикой ``raise``.
