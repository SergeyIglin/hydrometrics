.. _api-helpers:

==================================
Вспомогательные функции и реестр
==================================

Из ``hydrometrics`` экспортируются три объекта, которые не являются метриками: две функции для построения режимных кривых и реестр, через который вызов метрики попадает на нужный бэкенд.

Средний годовой гидрограф
---------------------------

Функция :func:`~hydrometrics.mean_annual_hydrograph` усредняет значения по календарным суткам за все годы ряда; пропуски не учитываются. Если в ряду есть високосный год, результат содержит 366 значений, и 29 февраля занимает отдельное место.

Функция :func:`~hydrometrics.mean_annual_hydrograph_duration_curve` сортирует средний годовой гидрограф по убыванию. Из 366 значений получается 365: при наличии високосного года усредняются два наименьших значения, то есть значения на 365-й и 366-й позициях ранжированного ряда (то же правило, что для годовых кривых в :ref:`metric-regNSE`). Это позиции по рангу, а не календарные дни. Полученная кривая служит опорной в :ref:`metric-regNSE`.

.. autofunction:: hydrometrics.mean_annual_hydrograph

.. autofunction:: hydrometrics.mean_annual_hydrograph_duration_curve

Пример: два водных года с половодьем в конце апреля, расход в м³/с.

.. testcode::

   import numpy as np
   import hydrometrics as hm

   dates = np.arange("2011-10-01", "2013-10-01", dtype="datetime64[D]")  # contains 29 February 2012
   doy = (dates - dates.astype("datetime64[Y]")).astype(int)
   q = 20 + 150 * np.exp(-(((doy - 118) / 16.0) ** 2))  # synthetic flood hydrograph, m3/s
   hydrograph = hm.mean_annual_hydrograph(q, dates)
   curve = hm.mean_annual_hydrograph_duration_curve(q, dates)
   print(hydrograph.shape, curve.shape)
   print(bool(np.all(np.diff(curve) <= 0)), round(float(curve[0]), 1), round(float(curve[-1]), 1))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   (366,) (365,)
   True 170.0 20.0

Реестр бэкендов
-----------------

Каждая метрика зарегистрирована в реестре под своим именем для numpy, pandas, polars и xarray. Публичная функция, например ``hydrometrics.nse``, это диспетчер: он смотрит на тип входов и вызывает реализацию нужного бэкенда, а при её отсутствии реализацию numpy. Глобальный реестр доступен как ``hydrometrics.registry``.

.. testcode::

   import hydrometrics as hm

   print(type(hm.registry).__name__)
   print(hm.registry.get_dispatcher("nse").__name__)

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   BackendRegistry
   nse

Собственную метрику создаёт декоратор :func:`hydrometrics.core.base.metric`; регистрация в реестре даёт ей единый вызов со всеми параметрами метрик пакета (``nan_policy``, ``sample_weight``, ``axis``, ``reduction``). В примере используется отдельный экземпляр реестра, чтобы не менять глобальный.

.. testcode::

   import numpy as np
   import pandas as pd
   from hydrometrics.core.base import metric
   from hydrometrics.core.dispatch import BackendRegistry


   @metric(name="Mean ratio", direction="target", bounds=(0.0, None), reference="own", optimum=1.0)
   def mean_ratio(obs, sim, *, weight=None, axis=None, reduction="mean"):
       """Ratio of the means of simulated and observed values."""
       return np.nanmean(sim, axis=axis) / np.nanmean(obs, axis=axis)


   registry = BackendRegistry()  # a private registry; hydrometrics.registry holds the package metrics
   registry.register_numpy("mean_ratio", mean_ratio)
   dispatch = registry.get_dispatcher("mean_ratio")

   q_obs = pd.Series([10.0, 20.0, np.nan, 40.0])
   q_sim = pd.Series([12.0, 18.0, 25.0, 44.0])
   result = dispatch(q_obs, q_sim)
   print(round(float(result), 4), result.direction, result.nan_info["n_nan_removed"])

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   1.0571 target 1

Для pandas-входа в этом примере нет отдельной реализации, поэтому используется numpy-функция; пара с пропуском удалена, а число удалённых пар записано в ``nan_info``.

.. autoclass:: hydrometrics.core.dispatch.BackendRegistry
   :members:
