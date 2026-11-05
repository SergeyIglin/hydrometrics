.. _axes:

.. _axis-limits:

==========================
Оси и многомерные данные
==========================

Аргумент ``axis`` задаёт измерение, вдоль которого метрика сворачивает значения; остальные измерения сохраняются. С ``axis=None`` все значения объединяются в один ряд. На xarray вместо номера оси используется имя измерения, аргумент ``dim``.

Форма результата
------------------

Данные трёх створов, форма ``(время, створ)``, и поле расходов, форма ``(время, широта, долгота)``. Таблица ниже получена запуском; ``reduction`` не задан.

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

   # Три створа: столбцы массива (время, створ)
   q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
   q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])

.. testcode::

   field_obs = q_obs[:, None, None] * np.array([[1.0, 0.5], [2.0, 1.5]])
   field_sim = q_sim[:, None, None] * np.array([[1.0, 0.5], [2.0, 1.5]])

   calls = {
       "(time, gauge), axis=None": hm.nse(q_obs_st, q_sim_st),
       "(time, gauge), axis=0": hm.nse(q_obs_st, q_sim_st, axis=0),
       "(time, gauge), axis=1": hm.nse(q_obs_st, q_sim_st, axis=1),
       "(time, gauge), axis=0, reduction='mean'": hm.nse(q_obs_st, q_sim_st, axis=0, reduction="mean"),
       "(time, lat, lon), axis=0": hm.nse(field_obs, field_sim, axis=0),
   }
   for label, result in calls.items():
       print(f"{label:42s} {np.shape(result.value)}")

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   (time, gauge), axis=None                   ()
   (time, gauge), axis=0                      (3,)
   (time, gauge), axis=1                      (1096,)
   (time, gauge), axis=0, reduction='mean'    ()
   (time, lat, lon), axis=0                   (2, 2)

Умолчание для ``reduction`` зависит от оси: при заданной оси возвращается массив по оставшимся измерениям (как ``"none"``), без оси результат это одно число (как ``"mean"``). Явный ``reduction="mean"`` сворачивает массив в число и среднее считается по значениям срезов, а не по всем элементам сразу. Для метрик со словарём результата, как :func:`~hydrometrics.kge_components`, правило применяется к каждому значению.

xarray: имена измерений и координаты
--------------------------------------

На ``DataArray`` ось задаётся именем, а координаты оставшихся измерений сохраняются. Несколько измерений можно свернуть сразу:

.. testcode::

   import xarray as xr

   coords = {"time": dates, "lat": [55.0, 56.0], "lon": [37.0, 38.0]}
   obs_da = xr.DataArray(field_obs, dims=["time", "lat", "lon"], coords=coords)
   sim_da = xr.DataArray(field_sim, dims=["time", "lat", "lon"], coords=coords)
   per_cell = hm.nse(obs_da, sim_da, dim="time").value
   print(per_cell.dims, per_cell.shape)
   overall = hm.nse(obs_da, sim_da, dim=["time", "lat", "lon"]).value
   print(overall.dims, round(float(overall), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   ('lat', 'lon') (2, 2)
   () 0.957

Одновременная передача ``dim`` и ``axis`` вызывает ``TypeError``. Координаты xarray проверяются параметром ``align`` (см. :doc:`input_data`).

Ансамбли
----------

Метрики для ансамблей, :func:`~hydrometrics.crps` и производные, ожидают члены ансамбля на последней оси: ``obs`` формы ``(n,)``, ``sim`` формы ``(n, m)``. Если члены стоят на первой оси, как в ``(член, время)``, её нужно переставить:

.. testcode::

   ens_rng = np.random.default_rng(7)
   members = 1.05 * q_obs[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.15 * q_obs[:, None])
   member_first = members.T  # shape (member, time)
   print(member_first.shape)
   print(round(float(hm.crps(q_obs, np.moveaxis(member_first, 0, -1))), 4), round(float(hm.crps(q_obs, members)), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   (20, 1096)
   2.06 2.06

Для ансамбля ось ``axis`` применяется к измерениям ``obs``, а не к члену ансамбля. Пример по створам: ``obs`` формы ``(n, g)``, ``sim`` формы ``(n, g, m)`` и ``axis=0`` дают значение для каждого створа.

.. testcode::

   members_st = np.stack([members, 0.5 * members, 1.5 * members], axis=1)
   print(members_st.shape)
   print(np.round(hm.crps(q_obs_st, members_st, axis=0).value, 3))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   (1096, 3, 20)
   [2.06  2.042 6.14 ]

Метрики без расчёта по оси
----------------------------

Четыре метрики задаются групповыми массивами, и ось для них не определена: любое значение ``axis`` кроме ``None`` вызывает ``NotImplementedError``. Это :func:`~hydrometrics.ssigma_delta`, :func:`~hydrometrics.forecast_verification_delta`, :func:`~hydrometrics.regNSE` и :func:`~hydrometrics.nse_variance_weighted`. Ряды разных створов для них считают в цикле по створам.

.. testcode::

   try:
       hm.regNSE(q_obs_st, q_sim_st, dates=dates, axis=0)
   except NotImplementedError as exc:
       print(exc)

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   regNSE does not support axis (it is not defined along an axis)

Ранговые метрики, :func:`~hydrometrics.spearman_r` и :func:`~hydrometrics.kendall_tau`, ось поддерживают, но считают каждый срез отдельно в цикле, поэтому на больших массивах медленнее остальных.

Если вес задан, его форма должна совпадать с формой ``obs``; иначе ``ValueError``.
