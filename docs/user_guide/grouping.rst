.. _grouping:

=============
Группировка
=============

Функция :func:`~hydrometrics.compute_grouped` считает метрику отдельно для каждой группы значений: сезона, водного года, створа, заблаговременности. Результат это :class:`~hydrometrics.GroupedResult`.

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

   import pandas as pd

   df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
   # Водный год начинается 1 октября и назван по году окончания
   df["water_year"] = df.index.year + (df.index.month >= 10)

Группы задаются столбцом таблицы или словарём массивов. Водный год начинается 1 октября.

.. testcode::

   by_year = hm.compute_grouped(hm.nse, df, "q_obs", "q_sim", group_by="water_year")
   for (water_year,), value in by_year:
       print(int(water_year), round(float(value), 4))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   2011 0.9499
   2012 0.9565
   2013 0.9548

Порядок групп это порядок первого появления в данных, а не отсортированный. Группа без наблюдений в результат не попадает, так как состав групп определяется данными. Несколько группирующих переменных дают составные ключи:

.. testcode::

   df["season"] = np.where(df.index.month.isin([4, 5, 6]), "flood", "low_flow")
   by_both = hm.compute_grouped(hm.kge_2012, df, "q_obs", "q_sim", group_by=["water_year", "season"])
   print(by_both.group_names)
   print(by_both.to_pandas().round(3).to_string(index=False))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   ('water_year', 'season')
    water_year   season  Kling-Gupta Efficiency 2012
          2011 low_flow                       -0.166
          2011    flood                        0.902
          2012 low_flow                       -0.076
          2012    flood                        0.908
          2013 low_flow                       -0.187
          2013    flood                        0.908

Без таблицы массивы передаются напрямую, а группы словарём. Так же задаются данные без pandas:

.. testcode::

   month = dates.astype("datetime64[M]").astype(int) % 12 + 1
   season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")
   by_season = hm.compute_grouped(hm.pbias, None, q_obs, q_sim, group_by={"season": season})
   print([round(float(v), 3) for v in by_season.values], [str(key[0]) for key in by_season.groups])

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   [6.568, -8.44] ['low_flow', 'flood']

Ограничения
-------------

- Метрика должна возвращать число. Метрики с результатом-словарём или массивом (:func:`~hydrometrics.kge_components`, расчёт по ``axis``, ``reduction="none"`` с поэлементным результатом) вызывают ``NotImplementedError`` с подсказкой считать по группам в цикле.
- Режутся только ``obs`` и ``sim`` по первой оси. Дополнительные массивы (``dates``, ``ref_date``, ``gauge``, а также веса и любые аргументы длиной в число строк) не разбиваются на группы, поэтому метрики, которые их требуют, как :func:`~hydrometrics.regNSE`, :func:`~hydrometrics.ssigma_delta`, :func:`~hydrometrics.forecast_verification_delta` и :func:`~hydrometrics.nse_variance_weighted`, вызывают ``NotImplementedError``. Для них считайте в цикле по группам и режьте массивы сами.
- Строки с пропуском (NaN, ``None``, NaT) в группирующей переменной вызывают ``ValueError``: отфильтруйте их заранее, например ``df.dropna(subset=["group"])``.
- Имена столбцов polars не разрешаются, polars-объекты вызывают ``TypeError``: передавайте массивы (``df["q_obs"].to_numpy()``) и ``group_by`` словарём.
- ``to_xarray()`` поддерживает одну группирующую переменную, для нескольких вызывает ``NotImplementedError``; используйте ``to_pandas()``.

Преобразования результата: ``to_pandas()``, ``to_xarray()`` (для одной группирующей переменной) и ``to_dict()``.
