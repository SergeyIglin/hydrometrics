"""User guide pages, part 2: quick start, concept, backends, weighting, grouping, results, choice, pitfalls, limits, extending."""
from lib import Doc
from metricpage import FRAME, SETUP, STATIONS

UG = "user_guide/"


def hdr(d):
    d.code(*SETUP, show_output=False)


# ================================================================================ quickstart
def quickstart() -> Doc:
    d = Doc(UG + "quickstart.rst", label="quickstart")
    d.title(("Установка и быстрый старт", "Installation and quick start"))
    d.h(("Установка", "Installation"))
    d.p(("Пакету нужен Python 3.10 или новее. Обязательные зависимости: numpy, pandas, xarray, polars и scipy. Установка из каталога репозитория:",
         "The package needs Python 3.10 or newer. Required dependencies: numpy, pandas, xarray, polars and scipy. Installation from the repository directory:"))
    d.block("pip install hydrometrics", "bash")
    d.p(("Для разработки и для сборки этой документации есть дополнительные наборы зависимостей ``dev`` и ``docs``: ``pip install \".[docs]\"`` ",
         "There are extra dependency sets ``dev`` and ``docs`` for development and for building this documentation: ``pip install \".[docs]\"`` "))
    d.h(("Первый расчёт", "A first computation"))
    d.p(("Все метрики вызываются одинаково: наблюдения и модель, затем необязательные аргументы. Результат это объект :class:`~hydrometrics.MetricResult`.",
         "All metrics are called the same way: observations and simulation, then optional arguments. The result is a :class:`~hydrometrics.MetricResult` object."))
    hdr(d)
    d.code('''
result = hm.nse(q_obs, q_sim)
print(float(result))
print(result.name, result.direction, result.bounds)
''')
    d.p(("Несколько метрик по одной паре рядов: расходы воды в м³/с, суточный шаг.", "Several metrics for one pair of series: discharge in m³/s, daily step."))
    d.code('''
for name in ("nse", "kge_2012", "rmse", "pbias"):
    print(f"{name:9s} {float(getattr(hm, name)(q_obs, q_sim)):9.4f}")
''')
    d.p(("Дальше: :doc:`concept` объясняет устройство вызова, :doc:`input_data` описывает типы входов, :doc:`choosing` помогает выбрать метрику, а страницы :doc:`/metrics/index` содержат определения.",
         "Next: :doc:`concept` explains how a call works, :doc:`input_data` describes input types, :doc:`choosing` helps to select a metric, and the pages of :doc:`/metrics/index` hold the definitions."))
    return d


# =================================================================================== concept
def concept() -> Doc:
    d = Doc(UG + "concept.rst", label="concept")
    d.title(("Концепция библиотеки", "Concept of the library"))
    d.p(("Библиотека построена вокруг трёх объектов. Метрика это функция с едиными аргументами и метаданными. Диспетчер выбирает реализацию по типу входа. Результат это объект с самим значением и сведениями о том, как оно получено.",
         "The library is built around three objects. A metric is a function with uniform arguments and metadata. A dispatcher selects the implementation from the type of the input. The result is an object holding the value and the details of how it was obtained."))
    d.h(("Единый вызов", "A uniform call"))
    d.p(("У каждой метрики есть пары ``obs`` и ``sim``, а также общие аргументы:", "Every metric takes the pair ``obs`` and ``sim`` and the common arguments:"))
    d.table((("Аргумент", "Argument"), ("Смысл", "Meaning")), [
        ("``axis`` / ``dim``", ("Измерение, вдоль которого считается метрика; см. :doc:`axes`.", "The dimension along which the metric is computed; see :doc:`axes`.")),
        ("``nan_policy``", ("Политика пропусков: ``omit`` (умолчание), ``propagate``, ``raise``; см. :doc:`missing_values`.", "Missing-value policy: ``omit`` (default), ``propagate``, ``raise``; see :doc:`missing_values`.")),
        ("``sample_weight`` / ``weight``", ("Веса пар; см. :doc:`weights`.", "Pair weights; see :doc:`weights`.")),
        ("``reduction``", ("Свёртка результата: ``mean``, ``sum`` или ``none``.", "Reduction of the result: ``mean``, ``sum`` or ``none``.")),
        ("``align``", ("Выравнивание рядов с метками: ``strict`` (умолчание) или ``inner``; см. :doc:`input_data`.", "Alignment of labelled series: ``strict`` (default) or ``inner``; see :doc:`input_data`.")),
    ], widths=[28, 72])
    d.p(("Метрики со своими параметрами (``norm``, ``eps``, ``m``, ``fair``, ``ref_date``, ``dates`` и другие) описаны на страницах метрик. Сигнатуры и докстринги формируются из общего описания, поэтому ``help(hm.nse)`` показывает все параметры, а не безымянные ``**kwargs``.",
         "Metrics with their own parameters (``norm``, ``eps``, ``m``, ``fair``, ``ref_date``, ``dates`` and others) are described on the metric pages. Signatures and docstrings are built from a common description, so ``help(hm.nse)`` shows all parameters rather than anonymous ``**kwargs``."))
    d.h(("Метаданные метрики", "Metric metadata"))
    d.p(("Каждая метрика знает своё имя, направление улучшения, границы значений, ссылку на источник и формулу. Эти сведения попадают в результат и в сводные таблицы документации.",
         "Each metric knows its name, the direction of improvement, the bounds of its values, a reference to the source and the formula. This information enters the result and the summary tables of the documentation."))
    hdr(d)
    d.code('''
result = hm.kge_2012(q_obs, q_sim)
print(result.name)
print(result.direction, result.bounds)
print(result.reference)
''')
    d.h(("Диспетчер и бэкенды", "Dispatcher and backends"))
    d.p(("Публичная функция, например ``hydrometrics.nse``, это диспетчер: по типу ``obs`` и ``sim`` он выбирает numpy, pandas, polars или xarray. Расчёт во всех случаях выполняет одно и то же ядро на numpy-массивах, а бэкенд только переводит вход и упаковывает результат. Поэтому значения не зависят от бэкенда; это проверяют парные тесты. Подробнее: :doc:`backends`.",
         "A public function, for example ``hydrometrics.nse``, is a dispatcher: from the type of ``obs`` and ``sim`` it selects numpy, pandas, polars or xarray. In every case the same kernel computes on numpy arrays, and the backend only converts the input and packs the result. Therefore the values do not depend on the backend; paired tests verify this. More: :doc:`backends`."))
    d.h(("Объект результата", "The result object"))
    d.p(("Результат это :class:`~hydrometrics.MetricResult`: значение, метаданные метрики, использованные параметры и сведения об удалённых пропусках. Подробнее: :doc:`results`.",
         "The result is a :class:`~hydrometrics.MetricResult`: the value, the metric metadata, the parameters used and information about removed gaps. More: :doc:`results`."))
    return d


# =================================================================================== backends
def backends() -> Doc:
    d = Doc(UG + "backends.rst", label="backends")
    d.title(("Бэкенды", "Backends"))
    d.p(("Поддерживаются четыре типа входов. Выбор бэкенда автоматический и описан в :doc:`input_data`; вручную его не задают и не меняют.",
         "Four input types are supported. The backend choice is automatic and described in :doc:`input_data`; it is neither set nor changed manually."))
    d.table((("Бэкенд", "Backend"), ("Входы", "Inputs"), ("Результат для скалярной метрики", "Result for a scalar metric"), ("Результат по оси", "Result along an axis")), [
        ("numpy", "``list``, ``ndarray``", ("``MetricResult`` со скаляром", "``MetricResult`` with a scalar"), ("``ndarray``", "``ndarray``")),
        ("pandas", "``Series``, ``DataFrame``", ("``MetricResult`` со скаляром", "``MetricResult`` with a scalar"), ("``ndarray``", "``ndarray``")),
        ("polars", "``Series``, ``DataFrame``", ("``MetricResult`` со скаляром", "``MetricResult`` with a scalar"), ("``ndarray``", "``ndarray``")),
        ("xarray", "``DataArray``", ("``MetricResult`` со скаляром", "``MetricResult`` with a scalar"), ("``DataArray`` с координатами", "``DataArray`` with coordinates")),
    ], widths=[12, 24, 34, 30])
    d.p(("Что одинаково на всех бэкендах: значения, политика пропусков, правила для весов и ``reduction``, исключения, метаданные метрик. Что отличается: тип значения при расчёте по оси; ``xarray.Dataset`` не принимается; ``polars.LazyFrame`` не поддерживается.",
         "What is identical on all backends: the values, the missing-value policy, the rules for weights and ``reduction``, the exceptions, the metric metadata. What differs: the type of the value for a computation along an axis; ``xarray.Dataset`` is not accepted; ``polars.LazyFrame`` is not supported."))
    hdr(d)
    d.code(*STATIONS, show_output=False)
    d.code('''
import pandas as pd
import polars as pl
import xarray as xr

frame = pd.DataFrame(q_obs_st, columns=["upper", "middle", "lower"])
frame_sim = pd.DataFrame(q_sim_st, columns=["upper", "middle", "lower"])
print(np.round(hm.nse(frame, frame_sim, axis=0).value, 4))
print(np.round(hm.nse(pl.DataFrame(frame), pl.DataFrame(frame_sim), axis=0).value, 4))
coords = {"time": dates, "station": ["upper", "middle", "lower"]}
obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
print(hm.nse(obs_da, sim_da, dim="time").value.round(4).to_series().to_dict())
''')
    d.p(("Измерений скорости не проводилось, и утверждений о производительности документация не делает. Ядра работают на numpy; ранговые метрики (:func:`~hydrometrics.spearman_r`, :func:`~hydrometrics.kendall_tau`) и :func:`~hydrometrics.roc_auc` считают срезы по оси в цикле.",
         "No speed measurements were made and the documentation makes no performance claims. The kernels run on numpy; the rank metrics (:func:`~hydrometrics.spearman_r`, :func:`~hydrometrics.kendall_tau`) and :func:`~hydrometrics.roc_auc` compute slices along an axis in a loop."))
    return d


# =================================================================================== weights
def weights() -> Doc:
    d = Doc(UG + "weights.rst", label="weights")
    d.title(("Взвешивание", "Weighting"))
    d.p(("Вес пары задаёт её вклад в сумму и в среднее. Аргумент называется ``sample_weight``; ``weight`` принимается как алиас, а оба сразу вызывают ``TypeError``. Форма веса совпадает с формой ``obs``, значения неотрицательны, NaN делает пару недействительной (см. :doc:`missing_values`).",
         "A pair weight sets its contribution to the sums and means. The argument is called ``sample_weight``; ``weight`` is accepted as an alias and both at once raise ``TypeError``. The weight has the shape of ``obs``, values are non-negative, NaN invalidates the pair (see :doc:`missing_values`)."))
    d.p(("Вес нуль исключает пару, вес два равнозначен повтору пары. Метрики без поддержки весов: ``spearman_r``, ``kendall_tau``, ``roc_auc``, ``pr_auc``, ``ssigma``, ``ssigma_delta``, ``forecast_verification``, ``forecast_verification_delta``, ``regNSE``, ``nse_variance_weighted``; для них вес вызывает ``NotImplementedError``.",
         "A zero weight excludes a pair, a weight of two is equivalent to repeating the pair. Metrics without weight support: ``spearman_r``, ``kendall_tau``, ``roc_auc``, ``pr_auc``, ``ssigma``, ``ssigma_delta``, ``forecast_verification``, ``forecast_verification_delta``, ``regNSE``, ``nse_variance_weighted``; a weight raises ``NotImplementedError`` for them."))
    hdr(d)
    d.p(("Пример: оценить модель с усиленным вкладом межени. Вес обратен расходу, поэтому малые значения весят больше; результат по NSE сравнивается с невзвешенным.",
         "Example: assess a model with a strengthened contribution of low flow. The weight is inverse to discharge, so small values weigh more; the NSE result is compared with the unweighted one."))
    d.code('''
weights = 1.0 / q_obs
print(round(float(hm.nse(q_obs, q_sim)), 4), round(float(hm.nse(q_obs, q_sim, sample_weight=weights)), 4))
''')
    d.p(("Удвоение веса равносильно повтору пары:", "Doubling a weight is equivalent to repeating the pair:"))
    d.code('''
w = np.ones_like(q_obs)
w[:100] = 2.0
repeated_obs = np.concatenate([q_obs[:100], q_obs])
repeated_sim = np.concatenate([q_sim[:100], q_sim])
print(round(float(hm.mae(q_obs, q_sim, sample_weight=w)), 8), round(float(hm.mae(repeated_obs, repeated_sim)), 8))
''')
    d.p(("Вес в метриках оказывается на формулах по-разному: в средних он входит как множитель каждого слагаемого и нормируется суммой весов. Конкретный вид для каждой метрики указан в её формуле. Вес не переводит ряд в другой масштаб и не заменяет раздельный расчёт по сезонам (:doc:`grouping`).",
         "Weights enter the formulas in different ways: in means they multiply each term and are normalised by the sum of weights. The concrete form for each metric is given in its formula. A weight does not move a series to another scale and does not replace a separate computation by season (:doc:`grouping`)."))
    return d


# =================================================================================== grouping
def grouping() -> Doc:
    d = Doc(UG + "grouping.rst", label="grouping")
    d.title(("Группировка", "Grouping"))
    d.p(("Функция :func:`~hydrometrics.compute_grouped` считает метрику отдельно для каждой группы значений: сезона, водного года, створа, заблаговременности. Результат это :class:`~hydrometrics.GroupedResult`.",
         "The function :func:`~hydrometrics.compute_grouped` computes a metric separately for each group of values: a season, a water year, a gauge, a lead time. The result is a :class:`~hydrometrics.GroupedResult`."))
    hdr(d)
    d.code(*FRAME, show_output=False)
    d.p(("Группы задаются столбцом таблицы или словарём массивов. Водный год начинается 1 октября.", "Groups are set by a table column or by a dictionary of arrays. The water year starts on 1 October."))
    d.code('''
by_year = hm.compute_grouped(hm.nse, df, "q_obs", "q_sim", group_by="water_year")
for (water_year,), value in by_year:
    print(int(water_year), round(float(value), 4))
''')
    d.p(("Порядок групп это порядок первого появления в данных, а не отсортированный. Группа без наблюдений в результат не попадает, так как состав групп определяется данными. Несколько группирующих переменных дают составные ключи:",
         "The groups come in order of first appearance in the data, not sorted. A group without observations does not appear, since the groups are defined by the data. Several grouping variables give composite keys:"))
    d.code('''
df["season"] = np.where(df.index.month.isin([4, 5, 6]), "flood", "low_flow")
by_both = hm.compute_grouped(hm.kge_2012, df, "q_obs", "q_sim", group_by=["water_year", "season"])
print(by_both.group_names)
print(by_both.to_pandas().round(3).to_string(index=False))
''')
    d.p(("Без таблицы массивы передаются напрямую, а группы словарём. Так же задаются данные без pandas:", "Without a table the arrays are passed directly and the groups by a dictionary. Data without pandas are set the same way:"))
    d.code('''
month = dates.astype("datetime64[M]").astype(int) % 12 + 1
season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")
by_season = hm.compute_grouped(hm.pbias, None, q_obs, q_sim, group_by={"season": season})
print([round(float(v), 3) for v in by_season.values], [str(key[0]) for key in by_season.groups])
''')
    d.h(("Ограничения", "Limitations"))
    d.ul([
        ("Метрика должна возвращать число. Метрики с результатом-словарём или массивом (:func:`~hydrometrics.kge_components`, расчёт по ``axis``, ``reduction=\"none\"`` с поэлементным результатом) вызывают ``NotImplementedError`` с подсказкой считать по группам в цикле.",
         "The metric must return a number. Metrics with a dictionary or array result (:func:`~hydrometrics.kge_components`, a computation along ``axis``, ``reduction=\"none\"`` with an element-wise result) raise ``NotImplementedError`` with a hint to compute by groups in a loop."),
        ("Режутся только ``obs`` и ``sim`` по первой оси. Дополнительные массивы (``dates``, ``ref_date``, ``gauge``, а также веса и любые аргументы длиной в число строк) не разбиваются на группы, поэтому метрики, которые их требуют, как :func:`~hydrometrics.regNSE`, :func:`~hydrometrics.ssigma_delta`, :func:`~hydrometrics.forecast_verification_delta` и :func:`~hydrometrics.nse_variance_weighted`, вызывают ``NotImplementedError``. Для них считайте в цикле по группам и режьте массивы сами.",
         "Only ``obs`` and ``sim`` are sliced along the first axis. Additional arrays (``dates``, ``ref_date``, ``gauge``, and also weights and any argument with one entry per row) are not split into groups, so metrics that need them, such as :func:`~hydrometrics.regNSE`, :func:`~hydrometrics.ssigma_delta`, :func:`~hydrometrics.forecast_verification_delta` and :func:`~hydrometrics.nse_variance_weighted`, raise ``NotImplementedError``. For them compute in a loop over the groups and slice the arrays yourself."),
        ("Строки с пропуском (NaN, ``None``, NaT) в группирующей переменной вызывают ``ValueError``: отфильтруйте их заранее, например ``df.dropna(subset=[\"group\"])``.",
         "Rows with a missing value (NaN, ``None``, NaT) in a grouping variable raise ``ValueError``: filter them beforehand, for example ``df.dropna(subset=[\"group\"])``."),
        ("Имена столбцов polars не разрешаются, polars-объекты вызывают ``TypeError``: передавайте массивы (``df[\"q_obs\"].to_numpy()``) и ``group_by`` словарём.",
         "polars column names are not resolved and polars objects raise ``TypeError``: pass arrays (``df[\"q_obs\"].to_numpy()``) and ``group_by`` as a dictionary."),
        ("``to_xarray()`` поддерживает одну группирующую переменную, для нескольких вызывает ``NotImplementedError``; используйте ``to_pandas()``.",
         "``to_xarray()`` supports one grouping variable and raises ``NotImplementedError`` for several; use ``to_pandas()``."),
    ])
    d.p(("Преобразования результата: ``to_pandas()``, ``to_xarray()`` (для одной группирующей переменной) и ``to_dict()``.", "Conversions of the result: ``to_pandas()``, ``to_xarray()`` (for a single grouping variable) and ``to_dict()``."))
    return d


# =================================================================================== results
def results() -> Doc:
    d = Doc(UG + "results.rst", label="results")
    d.title(("Объект результата", "The result object"))
    d.p(("Метрики возвращают :class:`~hydrometrics.MetricResult`. Объект неизменяемый и содержит значение вместе со сведениями о расчёте.",
         "Metrics return a :class:`~hydrometrics.MetricResult`. The object is immutable and holds the value together with the details of the computation."))
    d.table((("Поле", "Field"), ("Содержимое", "Content")), [
        ("``value``", ("Значение: число, массив, словарь или ``DataArray``.", "The value: a number, an array, a dictionary or a ``DataArray``.")),
        ("``name``, ``direction``, ``bounds``, ``optimum``", ("Метаданные метрики. ``direction`` равно ``maximize``, ``minimize`` или ``target``; при ``target`` задан ``optimum``.", "Metric metadata. ``direction`` is ``maximize``, ``minimize`` or ``target``; with ``target`` an ``optimum`` is given.")),
        ("``parameters``", ("Использованные ``axis``, ``nan_policy``, ``reduction`` и параметры метрики.", "The ``axis``, ``nan_policy``, ``reduction`` used and the metric parameters.")),
        ("``reference``, ``meta``", ("Ссылка на источник, описание и формула.", "A reference to the source, the description and the formula.")),
        ("``nan_info``", ("Политика и число удалённых пар.", "The policy and the number of removed pairs.")),
        ("``norm_source``", ("Откуда взята опора в ``nse`` и родственных метриках.", "Where the benchmark in ``nse`` and related metrics came from.")),
    ], widths=[34, 66])
    hdr(d)
    d.code('''
result = hm.nse(q_obs, q_sim, norm=30.0)
print(round(float(result), 4), result.norm_source)
print(sorted(result.to_dict()))
''')
    d.p(("Скалярный результат приводится к числу через ``float(result)``; для массива используйте ``result.value``. Для записи в таблицу значения и метаданные собирают сами:",
         "A scalar result is converted to a number with ``float(result)``; for an array use ``result.value``. For a table, the values and metadata are collected by hand:"))
    d.code('''
import pandas as pd

rows = []
for name in ("nse", "kge_2012", "pbias"):
    r = getattr(hm, name)(q_obs, q_sim)
    rows.append({"metric": name, "value": float(r), "direction": r.direction})
print(pd.DataFrame(rows).round(4).to_string(index=False))
''')
    d.p(("Словарь ``to_dict()`` содержит ``-inf`` в границах и массивы в параметрах, поэтому прямая запись в JSON не работает; значения нужно сначала привести к стандартным типам. JSON-совместимый вывод есть в списке планируемых изменений.",
         "The ``to_dict()`` dictionary contains ``-inf`` in the bounds and arrays in the parameters, so writing it straight to JSON does not work; the values must first be converted to standard types. JSON-compatible output is in the list of planned changes."))
    return d


# =================================================================================== choosing
def choosing() -> Doc:
    d = Doc(UG + "choosing.rst", label="choosing")
    d.title(("Выбор метрики", "Choosing a metric"))
    d.p(("Одна метрика не описывает модель. Практика гидрологической верификации состоит в наборе метрик, каждая из которых отвечает на свой вопрос. Таблица связывает вопрос с метриками библиотеки и указывает главное ограничение; подробности на страницах метрик.",
         "A single metric does not describe a model. The practice of hydrological verification is a set of metrics, each answering its own question. The table links a question to the metrics of the library and states the main limitation; details are on the metric pages."))
    d.table((("Вопрос", "Question"), ("Метрики", "Metrics"), ("Главное ограничение", "Main limitation")), [
        (("Воспроизведены ли паводки и пики", "Are floods and peaks reproduced"), ":ref:`NSE <metric-nse>`, :ref:`RSR <metric-rsr>`, :ref:`RMSE <metric-rmse>`, :ref:`alpha <metric-alpha_component>`",
         ("Квадраты ошибок: значение определяют крупные расходы; NSE калибровки занижает изменчивость.", "Squared errors: the value is set by high flows; NSE calibration underestimates variability.")),
        (("Воспроизведена ли межень", "Is low flow reproduced"), ":ref:`logNSE <metric-log_nse>`, :ref:`mNSE <metric-modified_nse>`, :ref:`weighted_crps <metric-weighted_crps>`",
         ("logNSE зависит от добавки ``eps`` при нулевых расходах.", "logNSE depends on the offset ``eps`` with zero discharge.")),
        (("Верен ли объём стока", "Is the runoff volume right"), ":ref:`PBIAS <metric-pbias>`, :ref:`VE <metric-ve>`, :ref:`beta <metric-beta_component>`, :ref:`bias <metric-bias>`",
         ("Не видят фазу и форму гидрографа.", "They do not see the phase and shape of the hydrograph.")),
        (("Верны ли фаза и форма", "Are phase and shape right"), ":ref:`Pearson r <metric-pearson_r>`, :ref:`KGE <metric-kge_2012>`, :ref:`Spearman <metric-spearman_r>`",
         ("Корреляция не видит смещения и масштаба.", "Correlation does not see bias and scale.")),
        (("Общая картина и причины ошибки", "The overall picture and the causes of error"), ":ref:`KGE 2012 <metric-kge_2012>`, :ref:`kge_components <metric-kge_components>`, :ref:`NSE <metric-nse>`",
         ("Значения KGE 2009 и 2012 гг. несопоставимы; у KGE нет встроенного нуля.", "KGE 2009 and 2012 values are not comparable; KGE has no built-in zero.")),
        (("Верен ли годовой режим", "Is the annual regime right"), ":ref:`regNSE <metric-regNSE>`",
         ("Не видит ошибку фазы; нужны целые календарные годы.", "It does not see phase error; whole calendar years are needed.")),
        (("Несколько створов в одной оценке", "Several gauges in one assessment"), (":ref:`nse_variance_weighted <metric-nse_variance_weighted>`, расчёт по ``axis``", ":ref:`nse_variance_weighted <metric-nse_variance_weighted>`, computation by ``axis``"),
         ("Вес створа растёт как квадрат масштаба, малые реки не видны.", "A gauge weight grows with the square of the scale; small rivers are not visible.")),
        (("Прогноз с заблаговременностью", "A forecast with a lead time"), (":ref:`ssigma <metric-ssigma>`, :ref:`forecast_verification <metric-forecast_verification>`, варианты ``_delta``", ":ref:`ssigma <metric-ssigma>`, :ref:`forecast_verification <metric-forecast_verification>`, ``_delta`` variants"),
         ("Градации по Георгиевскому и Шаночкину не подтверждены.", "The ratings of Georgievsky and Shanochkin are not confirmed.")),
        (("Ансамблевый прогноз", "An ensemble forecast"), ":ref:`CRPS <metric-crps>`, :ref:`CRPSS <metric-crpss>`",
         ("Значение зависит от размера ансамбля и опоры CRPSS.", "The value depends on the ensemble size and on the CRPSS reference.")),
        (("Вероятность события, например превышения порога", "Probability of an event, for example threshold exceedance"), ":ref:`Brier <metric-brier_score>`, :ref:`reliability <metric-reliability>`, :ref:`sharpness <metric-sharpness>`, :ref:`ROC AUC <metric-roc_auc>`",
         ("Редкие события дают малые значения Brier score; AUC не проверяет калибровку.", "Rare events give small Brier scores; AUC does not check calibration.")),
        (("Бинарный прогноз события", "A binary event forecast"), ":ref:`recall <metric-recall>`, :ref:`precision <metric-precision>`, :ref:`F1 <metric-f1_score>`, :ref:`EDI <metric-edi>`, :ref:`SEDI <metric-sedi>`",
         ("Accuracy завышена у редких событий; EDI и SEDI не определены при H=0 и при отсутствии ложных тревог, если H<1.", "Accuracy is inflated for rare events; EDI and SEDI are undefined when H=0 and when there are no false alarms with H<1.")),
    ], widths=[26, 40, 34])
    d.p(("Общие правила. Для оценки модели указывайте порог и опору, а не только число. Градации качества из литературы эмпирические и относятся к конкретному типу моделей, шагу и величине (см. страницы :ref:`metric-nse` и :ref:`metric-pbias`). Расчёт по сезонам и по водным годам показывает неоднородность, которую общее число скрывает (:doc:`grouping`).",
         "General rules. When assessing a model state the threshold and the benchmark, not only the number. Quality ratings from the literature are empirical and refer to a specific type of model, step and variable (see the pages :ref:`metric-nse` and :ref:`metric-pbias`). A computation by season and by water year shows a heterogeneity that the overall number hides (:doc:`grouping`)."))
    return d


# =================================================================================== pitfalls
def pitfalls() -> Doc:
    d = Doc(UG + "pitfalls.rst", label="pitfalls")
    d.title(("Типичные ошибки интерпретации", "Common mistakes of interpretation"))
    d.p(("Перечень ловушек, каждая из которых подтверждена расчётом на страницах метрик или в этом руководстве.", "A list of traps, each confirmed by a computation on the metric pages or in this guide."))
    items = [
        (("Выравнивание рядов нужно делать явно.", "The alignment of series has to be explicit."),
         ("При ``align=\"strict\"`` сдвинутый индекс pandas или координаты xarray дают ``ValueError``; ``align=\"inner\"`` оставляет общие метки. Без меток (numpy, polars) пары идут по позиции, и сдвиг рядов не обнаруживается (:doc:`input_data`).", "Under ``align=\"strict\"`` a shifted pandas index or xarray coordinates raise ``ValueError``; ``align=\"inner\"`` keeps the common labels. Without labels (numpy, polars) pairs go by position and a shift of the series is not detected (:doc:`input_data`).")),
        (("Хорошая NSE за год не означает воспроизведённой межени.", "A good annual NSE does not mean low flow is reproduced."),
         ("NSE определяется пиками; смотрите :ref:`metric-log_nse` и расчёт по сезонам.", "NSE is set by the peaks; look at :ref:`metric-log_nse` and the computation by season.")),
        (("KGE 2009 и 2012 гг. сравнивать между собой нельзя.", "KGE 2009 and 2012 cannot be compared with each other."),
         ("Отличаются компоненты (α и γ); см. :ref:`metric-kge_2009` и :ref:`metric-kge_2012`.", "The components (α and γ) differ; see :ref:`metric-kge_2009` and :ref:`metric-kge_2012`.")),
        (("У KGE нет нуля, подобного ``NSE = 0``.", "KGE has no zero like ``NSE = 0``."),
         ("По расчёту Knoben et al. прогноз средним даёт около −0,41 для KGE 2009 г.; сама функция при постоянном ``sim`` возвращает NaN (:ref:`metric-kge_2009`).", "By the calculation of Knoben et al. a mean-flow forecast gives about −0.41 for KGE 2009; the function itself returns NaN for a constant ``sim`` (:ref:`metric-kge_2009`).")),
        (("Знак PBIAS противоположен определению Moriasi et al.", "The PBIAS sign is opposite to the definition of Moriasi et al."),
         ("Здесь положительное значение означает завышение; пороги относятся к модулю (:ref:`metric-pbias`).", "Here a positive value means overestimation; the thresholds refer to the magnitude (:ref:`metric-pbias`).")),
        (("``r2`` не равна квадрату корреляции.", "``r2`` is not the squared correlation."),
         ("Занижение на 40 % оставляет квадрат корреляции равным 1, а ``r2`` заметно ниже (:ref:`metric-r2`).", "A 40 % underestimate leaves the squared correlation at 1 while ``r2`` is clearly lower (:ref:`metric-r2`).")),
        (("Высокая accuracy у редких событий ничего не доказывает.", "A high accuracy for rare events proves nothing."),
         ("Прогноз «события не будет» уже даёт около 0,9 при частоте события 10 % (:ref:`metric-accuracy`).", "A forecast that the event will not occur already gives about 0.9 at an event frequency of 10 % (:ref:`metric-accuracy`).")),
        (("CRPSS с опорой «среднее» завышает мастерство.", "CRPSS with a mean reference overstates skill."),
         ("Для рек с режимом берите климатический гидрограф опорой (:ref:`metric-crpss`).", "For rivers with a regime take the climatological hydrograph as the reference (:ref:`metric-crpss`).")),
        (("regNSE не видит ошибку фазы.", "regNSE does not see phase error."),
         ("Перестановка значений внутри года не меняет результат (:ref:`metric-regNSE`).", "A permutation of values within a year does not change the result (:ref:`metric-regNSE`).")),
        (("Многостворовая оценка скрывает малые реки.", "A multi-gauge score hides small rivers."),
         ("Вес растёт как дисперсия (:ref:`metric-nse_variance_weighted`).", "The weight grows as the variance (:ref:`metric-nse_variance_weighted`).")),
        (("``logNSE`` зависит от ``eps``.", "``logNSE`` depends on ``eps``."),
         ("Одни нулевые сутки сильно меняют значение (:ref:`metric-log_nse`).", "A single zero day changes the value strongly (:ref:`metric-log_nse`).")),
        (("Пропуски, не случайные по сезонам, смещают оценку.", "Gaps that are not random over seasons bias the estimate."),
         ("Смотрите ``nan_info`` и сезон пропусков (:doc:`missing_values`).", "Look at ``nan_info`` and the season of the gaps (:doc:`missing_values`).")),
    ]
    for head, body in items:
        d.h3(head)
        d.p(body)
    return d


# =================================================================================== limits
def limits() -> Doc:
    d = Doc(UG + "limits.rst", label="limits")
    d.title(("Воспроизводимость и ограничения", "Reproducibility and limitations"))
    d.h(("Воспроизводимость", "Reproducibility"))
    d.p(("Метрики детерминированы: одинаковые входы дают одинаковый результат на любом бэкенде. В примерах документации случайные ряды создаются с фиксированным seed (``numpy.random.default_rng(42)``), а все выводы получены запуском при сборке и проверяются ``sphinx.ext.doctest``. Версии зависимостей для сборки закреплены в ``pyproject.toml`` (набор ``docs``).",
         "Metrics are deterministic: identical inputs give identical results on any backend. In the examples of the documentation random series are created with a fixed seed (``numpy.random.default_rng(42)``), and all outputs come from runs during the build and are checked by ``sphinx.ext.doctest``. Dependency versions for the build are pinned in ``pyproject.toml`` (the ``docs`` set)."))
    d.h(("Чего библиотека не делает", "What the library does not do"))
    d.ul([
        ("Не знает, как сопоставить ряды без меток: numpy и polars идут по позиции, а ``align=\"inner\"`` для них не определён.", "It cannot match series without labels: numpy and polars go by position, and ``align=\"inner\"`` is undefined for them."),
        ("Не принимает ``xarray.Dataset`` и ``polars.LazyFrame``.", "It does not accept ``xarray.Dataset`` or ``polars.LazyFrame``."),
        ("Не вычисляет доверительные интервалы и не проверяет значимость значений метрик.", "It does not compute confidence intervals or test the significance of metric values."),
        ("Не следит за единицами измерения и не пересчитывает шаг по времени.", "It does not track units and does not resample the time step."),
        ("Не реализует индекс мастерства Брайера, разрешающую способность, пороговую CRPS, уточнённый индекс Уилмотта и многомерный NSE на главных компонентах.", "It does not implement the Brier skill score, resolution, the threshold-weighted CRPS, the refined Willmott index and the principal-component multivariate NSE."),
        ("Не разрезает дополнительные массивы (``dates``, ``ref_date``, ``gauge``, веса) при группировке: такие вызовы дают ``NotImplementedError``.", "It does not slice additional arrays (``dates``, ``ref_date``, ``gauge``, weights) in grouping: such calls raise ``NotImplementedError``."),
    ])
    d.p(("Подробный перечень ограничений и открытых вопросов: :doc:`known_limits`.", "A detailed list of limitations and open questions: :doc:`known_limits`."))
    return d


# =================================================================================== extending
def extending() -> Doc:
    d = Doc(UG + "extending.rst", label="extending")
    d.title(("Расширение библиотеки", "Extending the library"))
    d.p(("Собственная метрика создаётся декоратором ``metric`` из ``hydrometrics.core.base``. Декоратор принимает имя, направление улучшения, границы значений, ссылку и формулу, а флаги ``supports_weight`` и ``supports_axis`` сообщают, поддерживает ли функция веса и ось. Обёртка берёт на себя проверку входов, политику пропусков, веса, ``reduction`` и сбор результата, поэтому ядро получает готовые numpy-массивы.",
         "A custom metric is created with the ``metric`` decorator from ``hydrometrics.core.base``. The decorator takes the name, the direction of improvement, the bounds of the values, a reference and a formula, and the flags ``supports_weight`` and ``supports_axis`` tell whether the function supports weights and an axis. The wrapper takes care of input checks, the missing-value policy, weights, ``reduction`` and the packing of the result, so the kernel receives ready numpy arrays."))
    d.p(("Рабочий пример с собственным экземпляром реестра приведён в :ref:`api-helpers`. Регистрация в глобальном реестре ``hydrometrics.registry`` даёт метрике тот же единый вызов, что у встроенных. Метрики, добавленные пользователем, на страницы документации не попадают.",
         "A working example with a separate registry instance is given in :ref:`api-helpers`. Registration in the global registry ``hydrometrics.registry`` gives the metric the same uniform call as the built-in ones. Metrics added by a user do not appear in the documentation pages."))
    return d


def all_pages():
    return [quickstart(), concept(), backends(), weights(), grouping(), results(), choosing(), pitfalls(), limits(), extending()]
