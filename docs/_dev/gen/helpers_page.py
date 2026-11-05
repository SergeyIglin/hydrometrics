"""Page docs/api/helpers.rst: mean_annual_hydrograph*, the backend registry."""
from lib import Doc

D_CODE_FN = '''
import numpy as np
import hydrometrics as hm

dates = np.arange("2011-10-01", "2013-10-01", dtype="datetime64[D]")  # contains 29 February 2012
doy = (dates - dates.astype("datetime64[Y]")).astype(int)
q = 20 + 150 * np.exp(-(((doy - 118) / 16.0) ** 2))  # synthetic flood hydrograph, m3/s
hydrograph = hm.mean_annual_hydrograph(q, dates)
curve = hm.mean_annual_hydrograph_duration_curve(q, dates)
print(hydrograph.shape, curve.shape)
print(bool(np.all(np.diff(curve) <= 0)), round(float(curve[0]), 1), round(float(curve[-1]), 1))
'''

D_CODE_REG = '''
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
'''

D_CODE_GLOBAL = '''
import hydrometrics as hm

print(type(hm.registry).__name__)
print(hm.registry.get_dispatcher("nse").__name__)
'''


def helpers_page() -> Doc:
    d = Doc("api/helpers.rst", label="api-helpers")
    d.title(("Вспомогательные функции и реестр", "Helper functions and the registry"))
    d.p(("Из ``hydrometrics`` экспортируются три объекта, которые не являются метриками: две функции для построения режимных кривых и реестр, через который вызов метрики попадает на нужный бэкенд.",
         "``hydrometrics`` exports three objects that are not metrics: two functions that build regime curves and the registry through which a metric call reaches the right backend."))

    d.h(("Средний годовой гидрограф", "Mean annual hydrograph"))
    d.p(("Функция :func:`~hydrometrics.mean_annual_hydrograph` усредняет значения по календарным суткам за все годы ряда; пропуски не учитываются. Если в ряду есть високосный год, результат содержит 366 значений, и 29 февраля занимает отдельное место.",
         "The function :func:`~hydrometrics.mean_annual_hydrograph` averages the values by calendar day over all years of the series; gaps are ignored. If the series contains a leap year, the result has 366 values and 29 February keeps a place of its own."))
    d.p(("Функция :func:`~hydrometrics.mean_annual_hydrograph_duration_curve` сортирует средний годовой гидрограф по убыванию. Из 366 значений получается 365: при наличии високосного года усредняются два наименьших значения, то есть значения на 365-й и 366-й позициях ранжированного ряда (то же правило, что для годовых кривых в :ref:`metric-regNSE`). Это позиции по рангу, а не календарные дни. Полученная кривая служит опорной в :ref:`metric-regNSE`.",
         "The function :func:`~hydrometrics.mean_annual_hydrograph_duration_curve` sorts the mean annual hydrograph in descending order. 366 values are reduced to 365 when a leap year is present by averaging the two smallest values, that is the values at positions 365 and 366 of the ranked series (the same rule as for the annual curves in :ref:`metric-regNSE`). These are rank positions, not calendar days. The resulting curve is the reference of :ref:`metric-regNSE`."))
    d.raw(".. autofunction:: hydrometrics.mean_annual_hydrograph")
    d.raw(".. autofunction:: hydrometrics.mean_annual_hydrograph_duration_curve")
    d.p(("Пример: два водных года с половодьем в конце апреля, расход в м³/с.",
         "Example: two water years with a spring flood in late April, discharge in m³/s."))
    d.code(D_CODE_FN, D_CODE_FN)

    d.h(("Реестр бэкендов", "Backend registry"))
    d.p(("Каждая метрика зарегистрирована в реестре под своим именем для numpy, pandas, polars и xarray. Публичная функция, например ``hydrometrics.nse``, это диспетчер: он смотрит на тип входов и вызывает реализацию нужного бэкенда, а при её отсутствии реализацию numpy. Глобальный реестр доступен как ``hydrometrics.registry``.",
         "Every metric is registered under its name for NumPy, pandas, polars and xarray. A public function such as ``hydrometrics.nse`` is a dispatcher: it looks at the type of the inputs and calls the implementation of that backend, or the NumPy one if there is none. The global registry is available as ``hydrometrics.registry``."))
    d.code(D_CODE_GLOBAL, D_CODE_GLOBAL)
    d.p(("Собственную метрику создаёт декоратор :func:`hydrometrics.core.base.metric`; регистрация в реестре даёт ей единый вызов со всеми параметрами метрик пакета (``nan_policy``, ``sample_weight``, ``axis``, ``reduction``). В примере используется отдельный экземпляр реестра, чтобы не менять глобальный.",
         "A custom metric is made with the decorator :func:`hydrometrics.core.base.metric`; registering it gives it the unified call with all the parameters of the package metrics (``nan_policy``, ``sample_weight``, ``axis``, ``reduction``). The example uses a separate registry instance so as not to change the global one."))
    d.code(D_CODE_REG, D_CODE_REG)
    d.p(("Для pandas-входа в этом примере нет отдельной реализации, поэтому используется numpy-функция; пара с пропуском удалена, а число удалённых пар записано в ``nan_info``.",
         "There is no pandas-specific implementation in this example, so the NumPy function is used; the pair with a gap is dropped and the number of dropped pairs is recorded in ``nan_info``."))
    d.raw(".. autoclass:: hydrometrics.core.dispatch.BackendRegistry\n   :members:")
    return d
