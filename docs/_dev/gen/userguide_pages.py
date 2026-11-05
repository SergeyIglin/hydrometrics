"""User guide pages: missing values, axes, input data. All outputs come from real runs."""
from lib import Doc
from metricpage import SETUP, STATIONS

UG = "user_guide/"


def hdr(d):
    """Common first lines of the code samples."""
    d.code(*SETUP, show_output=False)


# ============================================================================ missing values
def missing_values() -> Doc:
    d = Doc(UG + "missing_values.rst", label="missing-values")
    d.title(("Пропуски в данных", "Missing values"))
    d.p(("В рядах наблюдений расходов воды пропуски обычны: сбой датчика, ледовые явления, период без измерений. Все метрики обрабатывают их одним способом, за который отвечает аргумент ``nan_policy``. Пара ``(obs[i], sim[i])`` считается недействительной, если NaN стоит в ``obs``, в ``sim`` или в весе ``sample_weight``.",
         "Gaps are common in discharge records: a sensor failure, ice conditions, a period without measurements. All metrics treat them in one way, controlled by the argument ``nan_policy``. A pair ``(obs[i], sim[i])`` is invalid if NaN stands in ``obs``, in ``sim`` or in the weight ``sample_weight``."))

    d.h(("Три политики", "Three policies"))
    d.table((("Значение", "Value"), ("Действие", "Action")), [
        (("``\"omit\"`` (умолчание)", "``\"omit\"`` (default)"), ("Недействительные пары исключаются целиком, в том числе при заданной оси. Результат совпадает с расчётом по заранее отфильтрованным парам. Число удалённых пар записано в ``nan_info``.",
                                      "Invalid pairs are dropped whole, also along an axis. The result equals a computation over pre-filtered pairs. The number of removed pairs is recorded in ``nan_info``.")),
        ("``\"propagate\"``", ("Расчёт идёт по тем же данным, но результат (или срез вдоль оси), в котором был пропуск, получает NaN. По парам NaN стоит только на затронутых местах.",
                               "The computation uses the same data, but the result (or the slice along the axis) that contained a gap gets NaN. In a per-pair result NaN stands only at the affected positions.")),
        ("``\"raise\"``", ("``ValueError`` при любом NaN в ``obs``, ``sim`` или весах.", "``ValueError`` for any NaN in ``obs``, ``sim`` or the weights.")),
    ], widths=[22, 78])
    d.p(("Любое другое значение вызывает ``ValueError``.", "Any other value raises ``ValueError``."))

    d.h(("Сравнение политик на одном примере", "Comparing the policies on one example"))
    d.p(("В наблюдениях месяц без измерений, в модельном ряду десять пропущенных суток. Для трёх метрик показаны результаты при ``omit``, расчёт по заранее отфильтрованным парам, ``propagate`` и ``raise``.",
         "The observations lack a month of measurements and the simulated series has ten missing days. For three metrics the table shows the results under ``omit``, a computation over pre-filtered pairs, ``propagate`` and ``raise``."))
    hdr(d)
    d.code('''
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
''')
    d.p(("``omit`` и расчёт по отфильтрованным парам совпадают до последнего знака. ``propagate`` удобен, когда пропуск должен делать результат недействительным, например при проверке полноты ряда, а ``raise`` в конвейерах, где пропусков быть не должно.",
         "``omit`` and the pre-filtered computation agree to the last digit. ``propagate`` is useful when a gap should invalidate the result, for example when checking the completeness of a record, and ``raise`` in pipelines where gaps must not occur."))

    d.h(("Сведения об удалении: nan_info", "Information about removal: nan_info"))
    d.code('''
result = hm.nse(q_obs_gap, q_sim_gap)
print(result.nan_info)
''')
    d.p(("``n_nan_removed`` равно числу удалённых пар при ``omit`` и нулю при ``propagate`` и ``raise``; ``n_total`` равно числу элементов ``obs``.",
         "``n_nan_removed`` equals the number of removed pairs under ``omit`` and zero under ``propagate`` and ``raise``; ``n_total`` equals the number of elements of ``obs``."))

    d.h(("Попарное удаление вдоль оси", "Pairwise removal along an axis"))
    d.p(("При заданной оси пары исключаются внутри каждого среза. Столбец с пропусками не влияет на соседние столбцы:",
         "With an axis pairs are dropped within each slice. A column with gaps does not affect its neighbours:"))
    d.code(*STATIONS, show_output=False)
    d.code('''
obs_gap = q_obs_st.copy()
obs_gap[200:260, 1] = np.nan  # gap only at the middle gauge
per_gauge = hm.nse(obs_gap, q_sim_st, axis=0)
print(np.round(per_gauge.value, 4))
print(per_gauge.nan_info)
''', '''
obs_gap = q_obs_st.copy()
obs_gap[200:260, 1] = np.nan  # gap only at the middle gauge
per_gauge = hm.nse(obs_gap, q_sim_st, axis=0)
print(np.round(per_gauge.value, 4))
print(per_gauge.nan_info)
''')

    d.h(("Что не считается пропуском", "What is not a gap"))
    d.p(("Значение ``inf`` пропуском не является: оно участвует в расчёте и обычно даёт ``inf`` или NaN в результате. Если бесконечности попали в ряд из-за деления на ноль, замените их на NaN до вызова.",
         "The value ``inf`` is not a gap: it takes part in the computation and usually gives ``inf`` or NaN in the result. If infinities entered the series through a division by zero, replace them with NaN before the call."))
    d.code('''
q_inf = q_obs.copy()
q_inf[10] = np.inf
print(float(hm.nse(q_inf, q_sim)))
print(round(float(hm.nse(np.where(np.isinf(q_inf), np.nan, q_inf), q_sim)), 4))
''')
    d.p(("Коды пропуска вроде ``-999`` библиотека не распознаёт: заменяйте их на NaN до вызова (``numpy.where`` или ``df.replace(-999, float(\"nan\"))``).",
         "The library does not recognise missing-data codes such as ``-999``: replace them with NaN before the call (``numpy.where`` or ``df.replace(-999, float(\"nan\"))``)."))
    d.code('''
q_coded = q_obs.copy()
q_coded[100:130] = -999
q_clean = np.where(q_coded == -999, np.nan, q_coded)
print(round(float(hm.nse(q_clean, q_sim)), 4), round(float(hm.nse(q_obs_gap, q_sim)), 4))
''')

    d.h(("Веса, ансамбли и вспомогательные массивы", "Weights, ensembles and auxiliary arrays"))
    d.p(("NaN в весе делает пару недействительной так же, как NaN в данных:", "NaN in a weight invalidates a pair in the same way as NaN in the data:"))
    d.code('''
weights = np.ones_like(q_obs)
weights[50:60] = np.nan
with_weights = hm.nse(q_obs, q_sim, sample_weight=weights)
kept = ~np.isnan(weights)
print(round(float(with_weights), 6), round(float(hm.nse(q_obs[kept], q_sim[kept])), 6))
''')
    d.p(("Для ансамбля строка недействительна, если NaN стоит в ``obs`` или во всех членах сразу. Пропуск в части членов не исключает строку, члены с NaN просто не участвуют в оценке:",
         "For an ensemble a row is invalid if NaN stands in ``obs`` or in all members at once. A gap in some members does not exclude the row; members with NaN simply do not take part in the estimate:"))
    d.code('''
ens_rng = np.random.default_rng(7)
members = 1.05 * q_obs[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.15 * q_obs[:, None])
members_gap = members.copy()
members_gap[5, :4] = np.nan
print(round(float(hm.crps(q_obs, members)), 4), round(float(hm.crps(q_obs, members_gap)), 4))
''')
    d.p(("Массивы, которые задают группы или даты (``gauge``, ``ref_date``, ``dates``), при ``omit`` не фильтруются: ядра метрик пропускают позиции с NaN сами, поэтому длина этих массивов всегда равна длине ``obs``.",
         "Arrays that define groups or dates (``gauge``, ``ref_date``, ``dates``) are not filtered under ``omit``: the metric kernels skip positions with NaN themselves, so the length of these arrays always equals the length of ``obs``."))

    d.h(("Как выбрать политику", "Choosing a policy"))
    d.p(("Для оценки модели по ряду с пропусками подходит умолчание ``omit``, но число удалённых пар нужно смотреть в ``nan_info``: метрика, посчитанная по половине ряда, сравнима с метрикой по полному ряду только при случайном характере пропусков. Пропуски в наблюдениях чаще приходятся на зиму и на пики, и тогда ``omit`` смещает оценку в сторону сезонов, где измерения были. Ряд, в котором пропуски не должны встречаться, лучше проверять политикой ``raise``.",
         "For assessing a model on a record with gaps the default ``omit`` fits, but the number of removed pairs should be read from ``nan_info``: a metric computed on half of the record is comparable with the metric on the full record only if the gaps are random. Gaps in observations more often fall in winter and at peaks, and then ``omit`` shifts the estimate towards the seasons in which measurements exist. A record in which gaps must not occur is better checked with the policy ``raise``."))
    return d


# =================================================================================== axes
def axes() -> Doc:
    d = Doc(UG + "axes.rst", label="axes")
    d.raw(".. _axis-limits:")
    d.title(("Оси и многомерные данные", "Axes and multidimensional data"))
    d.p(("Аргумент ``axis`` задаёт измерение, вдоль которого метрика сворачивает значения; остальные измерения сохраняются. С ``axis=None`` все значения объединяются в один ряд. На xarray вместо номера оси используется имя измерения, аргумент ``dim``.",
         "The argument ``axis`` sets the dimension along which the metric collapses values; the other dimensions are kept. With ``axis=None`` all values are pooled into one series. On xarray a dimension name is used instead of the axis number, the argument ``dim``."))

    d.h(("Форма результата", "Shape of the result"))
    d.p(("Данные трёх створов, форма ``(время, створ)``, и поле расходов, форма ``(время, широта, долгота)``. Таблица ниже получена запуском; ``reduction`` не задан.",
         "Data of three gauges, shape ``(time, gauge)``, and a discharge field, shape ``(time, lat, lon)``. The table below is from a real run; ``reduction`` is not set."))
    d.code(*SETUP, show_output=False)
    d.code(*STATIONS, show_output=False)
    d.code('''
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
''')
    d.p(("Умолчание для ``reduction`` зависит от оси: при заданной оси возвращается массив по оставшимся измерениям (как ``\"none\"``), без оси результат это одно число (как ``\"mean\"``). Явный ``reduction=\"mean\"`` сворачивает массив в число и среднее считается по значениям срезов, а не по всем элементам сразу. Для метрик со словарём результата, как :func:`~hydrometrics.kge_components`, правило применяется к каждому значению.",
         "The default for ``reduction`` depends on the axis: with an axis an array over the remaining dimensions is returned (like ``\"none\"``), without an axis the result is a single number (like ``\"mean\"``). An explicit ``reduction=\"mean\"`` collapses the array to a number and the mean is taken over the slice values, not over all elements at once. For metrics with a dictionary result, such as :func:`~hydrometrics.kge_components`, the rule applies to each value."))

    d.h(("xarray: имена измерений и координаты", "xarray: dimension names and coordinates"))
    d.p(("На ``DataArray`` ось задаётся именем, а координаты оставшихся измерений сохраняются. Несколько измерений можно свернуть сразу:",
         "On a ``DataArray`` the axis is given by name and the coordinates of the remaining dimensions are kept. Several dimensions can be collapsed at once:"))
    d.code('''
import xarray as xr

coords = {"time": dates, "lat": [55.0, 56.0], "lon": [37.0, 38.0]}
obs_da = xr.DataArray(field_obs, dims=["time", "lat", "lon"], coords=coords)
sim_da = xr.DataArray(field_sim, dims=["time", "lat", "lon"], coords=coords)
per_cell = hm.nse(obs_da, sim_da, dim="time").value
print(per_cell.dims, per_cell.shape)
overall = hm.nse(obs_da, sim_da, dim=["time", "lat", "lon"]).value
print(overall.dims, round(float(overall), 4))
''')
    d.p(("Одновременная передача ``dim`` и ``axis`` вызывает ``TypeError``. Координаты xarray проверяются параметром ``align`` (см. :doc:`input_data`).",
         "Passing ``dim`` and ``axis`` together raises ``TypeError``. The xarray coordinates are checked by the parameter ``align`` (see :doc:`input_data`)."))

    d.h(("Ансамбли", "Ensembles"))
    d.p(("Метрики для ансамблей, :func:`~hydrometrics.crps` и производные, ожидают члены ансамбля на последней оси: ``obs`` формы ``(n,)``, ``sim`` формы ``(n, m)``. Если члены стоят на первой оси, как в ``(член, время)``, её нужно переставить:",
         "Ensemble metrics, :func:`~hydrometrics.crps` and its derivatives, expect the ensemble members on the last axis: ``obs`` of shape ``(n,)``, ``sim`` of shape ``(n, m)``. If the members stand on the first axis, as in ``(member, time)``, it must be moved:"))
    d.code('''
ens_rng = np.random.default_rng(7)
members = 1.05 * q_obs[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.15 * q_obs[:, None])
member_first = members.T  # shape (member, time)
print(member_first.shape)
print(round(float(hm.crps(q_obs, np.moveaxis(member_first, 0, -1))), 4), round(float(hm.crps(q_obs, members)), 4))
''')
    d.p(("Для ансамбля ось ``axis`` применяется к измерениям ``obs``, а не к члену ансамбля. Пример по створам: ``obs`` формы ``(n, g)``, ``sim`` формы ``(n, g, m)`` и ``axis=0`` дают значение для каждого створа.",
         "For an ensemble ``axis`` applies to the dimensions of ``obs``, not to the ensemble member. By gauge: ``obs`` of shape ``(n, g)``, ``sim`` of shape ``(n, g, m)`` and ``axis=0`` give a value for each gauge."))
    d.code('''
members_st = np.stack([members, 0.5 * members, 1.5 * members], axis=1)
print(members_st.shape)
print(np.round(hm.crps(q_obs_st, members_st, axis=0).value, 3))
''')

    d.h(("Метрики без расчёта по оси", "Metrics without an axis"))
    d.p(("Четыре метрики задаются групповыми массивами, и ось для них не определена: любое значение ``axis`` кроме ``None`` вызывает ``NotImplementedError``. Это :func:`~hydrometrics.ssigma_delta`, :func:`~hydrometrics.forecast_verification_delta`, :func:`~hydrometrics.regNSE` и :func:`~hydrometrics.nse_variance_weighted`. Ряды разных створов для них считают в цикле по створам.",
         "Four metrics are defined through group arrays and an axis is undefined for them: any value of ``axis`` other than ``None`` raises ``NotImplementedError``. These are :func:`~hydrometrics.ssigma_delta`, :func:`~hydrometrics.forecast_verification_delta`, :func:`~hydrometrics.regNSE` and :func:`~hydrometrics.nse_variance_weighted`. The series of different gauges are computed for them in a loop over gauges."))
    d.code('''
try:
    hm.regNSE(q_obs_st, q_sim_st, dates=dates, axis=0)
except NotImplementedError as exc:
    print(exc)
''')
    d.p(("Ранговые метрики, :func:`~hydrometrics.spearman_r` и :func:`~hydrometrics.kendall_tau`, ось поддерживают, но считают каждый срез отдельно в цикле, поэтому на больших массивах медленнее остальных.",
         "The rank metrics, :func:`~hydrometrics.spearman_r` and :func:`~hydrometrics.kendall_tau`, support an axis but compute each slice separately in a loop, so on large arrays they are slower than the others."))
    d.p(("Если вес задан, его форма должна совпадать с формой ``obs``; иначе ``ValueError``.", "If a weight is given its shape must equal that of ``obs``; otherwise ``ValueError``."))
    return d


# ================================================================================ input data
def input_data() -> Doc:
    d = Doc(UG + "input_data.rst", label="input-data")
    d.title(("Входные данные и проверки", "Input data and validation"))
    d.p(("Метрики принимают наблюдённый ряд ``obs`` и модельный ``sim`` одинаковой формы. Библиотека определяет бэкенд по типу входа, приводит данные к числам с плавающей точкой и возвращает результат в типе, привычном для этого бэкенда.",
         "Metrics take an observed series ``obs`` and a simulated one ``sim`` of the same shape. The library determines the backend from the type of the input, converts the data to floating-point numbers and returns the result in the type usual for that backend."))

    d.h(("Допустимые типы и выбор бэкенда", "Accepted types and backend selection"))
    d.table((("Тип входа", "Input type"), ("Бэкенд", "Backend"), ("Замечания", "Notes")), [
        ("``list``, ``numpy.ndarray``", "numpy", ("Списки и массивы целых и логических значений приводятся к ``float64``; ``float32`` сохраняется.", "Lists and arrays of integers and booleans are converted to ``float64``; ``float32`` is kept.")),
        ("``pandas.Series``, ``pandas.DataFrame``", "pandas", ("Столбцы DataFrame трактуются как створы при ``axis=0``.", "DataFrame columns act as gauges with ``axis=0``.")),
        ("``polars.Series``, ``polars.DataFrame``", "polars", ("``LazyFrame`` не поддерживается.", "``LazyFrame`` is not supported.")),
        ("``xarray.DataArray``", "xarray", ("Ось задаётся именем измерения, ``dim``.", "The axis is given by dimension name, ``dim``.")),
        ("``xarray.Dataset``", "-", ("``NotImplementedError``: выберите переменную, например ``ds[\"discharge\"]``.", "``NotImplementedError``: select a variable, for example ``ds[\"discharge\"]``.")),
    ], widths=[34, 14, 52])
    d.p(("Бэкенд выбирается по первому подходящему типу среди ``obs`` и ``sim`` в порядке xarray, pandas, polars; иначе numpy. Поэтому смешанный вызов, например ``obs`` в pandas и ``sim`` в numpy, допустим и идёт по пути pandas. Явного выбора бэкенда нет.",
         "The backend is chosen by the first matching type among ``obs`` and ``sim`` in the order xarray, pandas, polars; otherwise numpy. A mixed call, for example ``obs`` in pandas and ``sim`` in numpy, is therefore allowed and follows the pandas path. There is no explicit backend selection."))
    d.code(*SETUP, show_output=False)
    d.code('''
import pandas as pd
import polars as pl
import xarray as xr

inputs = {
    "numpy": (q_obs, q_sim),
    "pandas": (pd.Series(q_obs), pd.Series(q_sim)),
    "polars": (pl.Series(q_obs), pl.Series(q_sim)),
    "xarray": (xr.DataArray(q_obs, dims="time"), xr.DataArray(q_sim, dims="time")),
}
for backend, (obs, sim) in inputs.items():
    result = hm.nse(obs, sim)
    print(f"{backend:7s} {type(result).__name__} {type(result.value).__name__} {float(result):.6f}")
''')
    d.p(("Результат один и тот же на всех бэкендах. Различается тип значения для расчёта по оси: на xarray это ``DataArray`` с сохранёнными координатами, на остальных ``numpy.ndarray``.",
         "The result is the same on all backends. The type of the value differs for a computation along an axis: on xarray it is a ``DataArray`` with coordinates kept, on the others a ``numpy.ndarray``."))

    d.h(("Выравнивание рядов: параметр align", "Aligning the series: the align parameter"))
    d.p(("Метрики сопоставляют значения по позиции, но у pandas и xarray есть метки (индекс, координаты). Параметр ``align`` решает, что делать с метками. По умолчанию ``\"strict\"``: если ``obs`` и ``sim`` оба объекты pandas, их индексы должны совпадать (``Index.equals``, порядок учитывается); если оба ``DataArray``, должны совпадать координаты по тем измерениям, где они есть с обеих сторон. Иначе ``ValueError`` с первым расхождением и подсказкой. Сдвинутые по времени ряды больше не считаются молча:",
         "Metrics pair values by position, but pandas and xarray carry labels (an index, coordinates). The parameter ``align`` decides what to do with the labels. The default is ``\"strict\"``: if ``obs`` and ``sim`` are both pandas objects their indexes must be equal (``Index.equals``, the order counts); if both are ``DataArray`` objects the coordinates must be equal on every dimension that has coordinates on both sides. Otherwise ``ValueError`` with the first difference and a hint. Series shifted in time are no longer computed silently:"))
    d.code('''
obs_series = pd.Series(q_obs[:10], index=pd.date_range("2020-01-01", periods=10))
sim_series = pd.Series(q_sim[:10], index=pd.date_range("2020-01-03", periods=10))
try:
    hm.nse(obs_series, sim_series)
except ValueError as exc:
    print(str(exc)[:60])
''')
    d.p(("``align=\"inner\"`` оставляет общие метки в порядке ``obs`` и делает это до обработки пропусков. Число отброшенных строк (из ``obs`` и из ``sim`` вместе) записано в ``result.meta[\"n_dropped_by_align\"]``:",
         "``align=\"inner\"`` keeps the common labels in the order of ``obs`` and does so before the missing values are handled. The number of rows dropped (from ``obs`` and from ``sim`` together) is recorded in ``result.meta[\"n_dropped_by_align\"]``:"))
    d.code('''
result = hm.nse(obs_series, sim_series, align="inner")
common = obs_series.index.intersection(sim_series.index)
by_hand = float(hm.nse(obs_series[common], sim_series[common]))
print(round(float(result), 4), round(by_hand, 4), result.meta["n_dropped_by_align"])
''')
    d.p(("Дубликаты в индексе, пустое пересечение и входы без меток (numpy, polars, смешанные типы) при ``\"inner\"`` дают ``ValueError``. При ``\"strict\"`` входы разных типов и polars не проверяются, а дополнительные массивы (``dates``, ``gauge``, ``ref_date``) и веса сопоставляются по позиции. Для ансамбля (``sim`` как таблица с участниками в столбцах) сравниваются индексы строк. Параметр действует и в :func:`~hydrometrics.compute_grouped`.",
         "Duplicate labels, an empty intersection and inputs without labels (numpy, polars, mixed types) raise ``ValueError`` under ``\"inner\"``. Under ``\"strict\"`` inputs of different kinds and polars are not checked, and the additional arrays (``dates``, ``gauge``, ``ref_date``) and weights are matched by position. For an ensemble (``sim`` as a table with the members in columns) the row indexes are compared. The parameter also works in :func:`~hydrometrics.compute_grouped`."))

    d.h(("Проверки и исключения", "Checks and exceptions"))
    d.table((("Ситуация", "Situation"), ("Исключение", "Exception")), [
        (("Разные формы ``obs`` и ``sim``", "Different shapes of ``obs`` and ``sim``"), "``ValueError``"),
        (("Форма веса не совпадает с ``obs``", "Weight shape differs from ``obs``"), "``ValueError``"),
        (("Отрицательный вес", "A negative weight"), "``ValueError``"),
        (("``weight`` и ``sample_weight`` одновременно", "``weight`` and ``sample_weight`` together"), "``TypeError``"),
        (("Неизвестное значение ``nan_policy`` или ``reduction``", "Unknown ``nan_policy`` or ``reduction``"), "``ValueError``"),
        (("Вес у метрики без поддержки весов, ось у метрики без оси", "A weight for a metric without weights, an axis for a metric without axes"), "``NotImplementedError``"),
        (("Нечисловые значения (строки, ``None`` в массиве ``object``)", "Non-numeric values (strings, ``None`` in an ``object`` array)"), "``TypeError``"),
        (("Индексы pandas или координаты xarray не совпадают при ``align=\"strict\"``; неизвестное значение ``align``", "pandas indexes or xarray coordinates differ under ``align=\"strict\"``; an unknown ``align``"), "``ValueError``"),
        (("Ось вне размерности массива", "An axis out of range"), ("``numpy.exceptions.AxisError``", "``numpy.exceptions.AxisError``")),
    ], widths=[70, 30])
    d.code('''
for call in (
    lambda: hm.nse(q_obs, q_sim[:-1]),
    lambda: hm.nse(q_obs, q_sim, sample_weight=-np.ones_like(q_obs)),
    lambda: hm.nse(q_obs, q_sim, nan_policy="drop"),
    lambda: hm.spearman_r(q_obs, q_sim, sample_weight=np.ones_like(q_obs)),
):
    try:
        call()
    except Exception as exc:
        print(type(exc).__name__ + ":", exc)
''')
    d.p(("Пустой ряд и ряд из одного элемента у большинства метрик не вызывают исключений: результат NaN для метрик, которым нужна дисперсия или несколько пар. Исключение это ``ssigma`` без оси, которая при числе пар не больше ``m`` вызывает ``ValueError``.",
         "An empty series and a series of one element raise no exceptions for most metrics: the result is NaN for metrics that need a variance or several pairs. The exception is ``ssigma`` without an axis, which raises ``ValueError`` when the number of pairs does not exceed ``m``."))

    d.h(("Веса", "Weights"))
    d.p(("Канонический аргумент ``sample_weight``; ``weight`` принимается как алиас. Вес нулевой означает, что пара не участвует в расчёте. Метрики без поддержки весов перечислены на их страницах и вызывают ``NotImplementedError``.",
         "The canonical argument is ``sample_weight``; ``weight`` is accepted as an alias. A zero weight means the pair does not take part in the computation. Metrics without weight support are listed on their pages and raise ``NotImplementedError``."))
    d.code('''
w = np.ones_like(q_obs)
w[q_obs > 100] = 0.0  # drop the flood from the estimate
print(round(float(hm.nse(q_obs, q_sim, sample_weight=w)), 4), round(float(hm.nse(q_obs[q_obs <= 100], q_sim[q_obs <= 100])), 4))
''', '''
w = np.ones_like(q_obs)
w[q_obs > 100] = 0.0  # drop the flood from the estimate
print(round(float(hm.nse(q_obs, q_sim, sample_weight=w)), 4), round(float(hm.nse(q_obs[q_obs <= 100], q_sim[q_obs <= 100])), 4))
''')
    d.p(("Результат с нулевыми весами совпадает с расчётом по оставшимся парам.", "The result with zero weights equals the computation over the remaining pairs."))

    d.h(("Возвращаемый объект", "The returned object"))
    d.p(("Функция возвращает :class:`~hydrometrics.MetricResult` с полями ``value``, ``name``, ``direction``, ``bounds``, ``optimum``, ``parameters``, ``reference``, ``nan_info`` и ``meta``. ``float(result)`` извлекает число из скалярного результата, ``result.to_dict()`` собирает все поля в словарь.",
         "The function returns a :class:`~hydrometrics.MetricResult` with the fields ``value``, ``name``, ``direction``, ``bounds``, ``optimum``, ``parameters``, ``reference``, ``nan_info`` and ``meta``. ``float(result)`` extracts the number from a scalar result, ``result.to_dict()`` collects all fields in a dictionary."))
    d.code('''
result = hm.nse(q_obs, q_sim)
print(result.name, result.direction, result.bounds)
print(result.parameters)
''')
    d.p(("Словарь ``to_dict`` содержит ``-inf`` в границах и массивы в параметрах, поэтому для записи в JSON его нужно предварительно преобразовать.",
         "The ``to_dict`` dictionary contains ``-inf`` in the bounds and arrays in the parameters, so it must be converted before being written to JSON."))
    return d


def all_pages():
    return [missing_values(), axes(), input_data()]
