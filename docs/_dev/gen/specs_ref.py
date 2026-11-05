"""Reference metric pages: NSE, KGE 2012, CRPS."""
from lib import fmt
from metricpage import FRAME, SETUP, STATIONS

MORIASI_NSE = (
    ("Очень хорошо", "Very good"), ("Хорошо", "Good"), ("Удовлетворительно", "Satisfactory"), ("Неудовлетворительно", "Unsatisfactory"))


def nse_interp(d):
    d.p(("``NSE = 1`` означает полное совпадение. ``NSE = 0`` означает, что модель в сумме квадратов ошибок равна постоянному прогнозу средним наблюдённым значением за тот же период; ``NSE < 0`` означает, что такой прогноз точнее модели. Этот ориентир следует из самой формулы и не зависит от данных.",
         "``NSE = 1`` means a perfect match. ``NSE = 0`` means that, in terms of the sum of squared errors, the model equals a constant forecast at the observed mean of the same period; ``NSE < 0`` means that constant forecast beats the model. This reference follows from the formula itself and does not depend on the data."))
    d.p(("Градации приведены в таблице 4 у Moriasi et al. :footcite:p:`moriasi2007`. Они предложены для непрерывного долгосрочного моделирования водосборов на **месячном** шаге по данным о стоке, наносах и биогенных элементах.",
         "A rating scale is given in Table 4 of Moriasi et al. :footcite:p:`moriasi2007`. It was proposed for continuous long-term watershed simulation at a **monthly** time step, using streamflow, sediment and nutrient data."))
    d.table((("Оценка", "Rating"), "NSE"), [
        (MORIASI_NSE[0], "0.75 < NSE < 1.00"), (MORIASI_NSE[1], "0.65 < NSE < 0.75"),
        (MORIASI_NSE[2], "0.50 < NSE < 0.65"), (MORIASI_NSE[3], "NSE < 0.50")])
    d.p(("Пороги эмпирические. Авторы прямо указывают, что их надо корректировать с учётом качества данных, процедуры калибровки, шага по времени и масштаба проекта, а с ростом шага осреднения оценка должна становиться строже. Перенос этих значений на суточный расход или прогноз половодья без проверки не обоснован.",
         "The thresholds are empirical. The authors state that they should be adjusted for data quality, calibration procedure, time step and project scope, and that a coarser time step warrants a stricter rating. Applying these values to daily discharge or to a spring flood forecast without further checks is not justified."))
    d.p(("В обзоре Moriasi et al. :footcite:p:`moriasi2015` для моделей масштаба водосбора удовлетворительным назван поток с ``NSE > 0.50`` на суточном, месячном и годовом шаге (по аннотации статьи; полная таблица недоступна, см. :doc:`/user_guide/known_limits`).",
         "The review by Moriasi et al. :footcite:p:`moriasi2015` calls a watershed-scale flow simulation satisfactory at ``NSE > 0.50`` on daily, monthly and annual steps (taken from the article abstract; the full table was not accessible, see :doc:`/user_guide/known_limits`)."))


def nse_examples(d):
    d.p(("Суточный гидрограф за три водных года: половодье, межень, расходы в м³/с.",
         "A daily hydrograph over three water years with a spring flood and low flow, discharge in m³/s."))
    d.code(*SETUP, show_output=False)
    d.code('''
result = hm.nse(q_obs, q_sim)
print(f"NSE = {float(result):.3f}")
''')
    d.p(("Значения по створам: ``reduction=\"none\"`` отключает осреднение, которое numpy-путь применяет по умолчанию.",
         "Per-gauge values: ``reduction=\"none\"`` disables the averaging that the NumPy path applies by default."))
    d.code(*STATIONS, show_output=False)
    d.code('''
per_station = hm.nse(q_obs_st, q_sim_st, axis=0, reduction="none")
print(np.round(per_station.value, 3))
''')
    d.p(("По водным годам и по сезонам через :func:`~hydrometrics.compute_grouped`:",
         "By water year and by season with :func:`~hydrometrics.compute_grouped`:"))
    d.code(*FRAME, show_output=False)
    d.code('''
by_year = hm.compute_grouped(hm.nse, df, "q_obs", "q_sim", group_by="water_year")
for (water_year,), value in by_year:
    print(int(water_year), round(float(value), 3))
''')
    d.code('''
df["season"] = np.where(df.index.month.isin([4, 5, 6]), "flood", "low_flow")
by_season = hm.compute_grouped(hm.nse, df, "q_obs", "q_sim", group_by="season")
for (season,), value in by_season:
    print(season, round(float(value), 3))
''')
    d.p(("Опорное значение можно задать через ``norm``, например среднюю многолетнюю норму. Значение попадает в ``norm_source``.",
         "The reference value can be set with ``norm``, for example a long-term mean. It is recorded in ``norm_source``."))
    d.code('''
long_term_mean = 30.0
custom = hm.nse(q_obs, q_sim, norm=long_term_mean)
print(round(float(custom), 3), custom.norm_source)
''')


def nse_hydro(ns):
    all_v = float(ns["result"])
    seasons = {k[0]: float(v) for k, v in ns["by_season"]}
    return [
        (f"Метрика квадратичная, поэтому её определяют большие расходы. В примере выше ``NSE = {fmt(all_v)}`` за весь период, ``{fmt(seasons['flood'])}`` за апрель–июнь и ``{fmt(seasons['low_flow'])}`` за остальные месяцы. Хорошая оценка за год не означает, что воспроизведена межень.",
         f"The metric is quadratic, so high flows dominate it. In the example above ``NSE = {fmt(all_v)}`` over the whole period, ``{fmt(seasons['flood'])}`` for April to June and ``{fmt(seasons['low_flow'])}`` for the other months. A good annual score does not mean low flow is reproduced."),
        ("Систематическое занижение пиков при калибровке по NSE описано в литературе: Mizukami et al. :footcite:p:`mizukami2019` показывают, что калибровка по NSE плохо воспроизводит годовые максимумы из-за занижения вариабельности стока, со ссылкой на теоретический разбор Gupta et al. :footcite:p:`gupta2009`.",
         "Systematic underestimation of peaks under NSE calibration is documented: Mizukami et al. :footcite:p:`mizukami2019` show that NSE calibration reproduces annual peak flows poorly because it underestimates flow variability, citing the theoretical analysis of Gupta et al. :footcite:p:`gupta2009`."),
        ("Среднее за период является слабым ориентиром для рек с устойчивым сезонным ходом: Гарцман :footcite:p:`gartsman2023` приводит условный пример, где одна и та же модель получает 0.90 при опоре на среднее и 0.33 при опоре на среднемноголетний ход расходов. Для такой оценки в библиотеке есть :func:`~hydrometrics.regNSE` с другим смыслом, а суточного режимного опорного ряда в ``nse`` можно добиться, передав массив ``norm``.",
         "The period mean is a weak benchmark for rivers with a stable seasonal cycle: Gartsman :footcite:p:`gartsman2023` gives an illustrative case in which the same model scores 0.90 against the mean and 0.33 against the mean daily regime. The library offers :func:`~hydrometrics.regNSE`, which has a different meaning, and a daily regime reference can be used in ``nse`` by passing an array as ``norm``."),
        ("NSE нечувствительна к сдвигу среднего при низких расходах, отмечают Krause et al. :footcite:p:`krause2005`. Дополняйте её :ref:`metric-pbias` для объёма стока и :ref:`metric-log_nse` для межени.",
         "NSE is not very sensitive to systematic over- or underprediction during low flow, as Krause et al. :footcite:p:`krause2005` note. Complement it with :ref:`metric-pbias` for runoff volume and :ref:`metric-log_nse` for low flow."),
    ]


NSE = dict(
    name="nse",
    title=("Критерий Нэша–Сатклиффа (NSE)", "Nash–Sutcliffe efficiency (NSE)"),
    short=[("NSE сравнивает сумму квадратов ошибок модели с суммой квадратов отклонений наблюдений от их среднего :footcite:p:`nash1970`. Показывает, насколько модель точнее постоянного прогноза средним значением.",
            "NSE compares the sum of squared model errors with the sum of squared deviations of the observations from their mean :footcite:p:`nash1970`. It shows how much the model improves on a constant forecast at the mean.")],
    sig_opt=", norm=None",
    formula=[r"\mathrm{NSE} = 1 - \frac{\sum_{i=1}^{n} w_i\,(O_i - S_i)^2}{\sum_{i=1}^{n} w_i\,(O_i - \bar{O})^2}, \qquad \bar{O} = \frac{\sum_i w_i O_i}{\sum_i w_i}"],
    symbols=[(r":math:`O_i` наблюдённое значение, :math:`S_i` модельное значение, :math:`w_i` вес (1 без ``sample_weight``), :math:`n` число пар. Суммирование идёт по оси ``axis``, а при ``axis=None`` по всем элементам массива.",
              r":math:`O_i` is the observed value, :math:`S_i` the simulated value, :math:`w_i` the weight (1 without ``sample_weight``), :math:`n` the number of pairs. The sum runs along ``axis``, or over all array elements with ``axis=None``.")],
    deviation=[("Без весов и ``norm`` формула совпадает с классической. Веса и ``norm`` являются расширениями библиотеки: заданный ``norm`` заменяет :math:`\\bar{O}` в знаменателе.",
                "Without weights and ``norm`` the formula is the classical one. Weights and ``norm`` are library extensions: a given ``norm`` replaces :math:`\\bar{O}` in the denominator."),
               ("При ``nan_policy=\"propagate\"`` суммы считаются функцией ``nansum`` раздельно, поэтому пара с пропуском только в ``sim`` выпадает из числителя, но остаётся в знаменателе, см. раздел о пропусках.",
                "With ``nan_policy=\"propagate\"`` the sums are computed separately with ``nansum``, so a pair with a gap only in ``sim`` drops out of the numerator but stays in the denominator, see the section on missing values.")],
    range="(-∞, 1]", optimum="1", dir="up",
    bounds=[("Верхняя граница достигается при совпадении рядов. Снизу значение не ограничено. При нулевой дисперсии наблюдений знаменатель равен нулю и результат равен NaN; ``r2`` в этом случае ведёт себя иначе.",
             "The upper bound is reached when the series coincide. There is no lower bound. With zero variance in the observations the denominator is zero and the result is NaN; ``r2`` behaves differently in this case.")],
    interp=nse_interp,
    params_opt=[("``norm``", ("число или массив", "float or array"), "``None``",
                 ("Опорное значение вместо среднего наблюдений. Массив должен вещаться на ``obs``.",
                  "Reference value instead of the observed mean. An array must broadcast to ``obs``."))],
    special=[("При ``nan_policy=\"propagate\"`` NaN не распространяется в результат: ядро использует ``nansum``. Это расходится с названием политики. Если NaN есть только в ``sim``, значения при ``propagate`` и ``omit`` различаются, потому что знаменатель при ``propagate`` считается по всем ``obs``. Для расчёта по согласованным парам указывайте ``nan_policy=\"omit\"``. При заданной оси ``omit`` пары не удаляет, см. :doc:`/user_guide/missing_values`.",
              "With ``nan_policy=\"propagate\"`` NaN does not propagate to the result, because the core uses ``nansum``. This contradicts the policy name. If NaN occurs only in ``sim``, the ``propagate`` and ``omit`` values differ, since the ``propagate`` denominator uses all ``obs``. To compute over consistent pairs use ``nan_policy=\"omit\"``. With an axis ``omit`` does not remove pairs, see :doc:`/user_guide/missing_values`.")],
    examples=nse_examples,
    hydro=None,
    related=["log_nse", "modified_nse", "nse_bounded", "regNSE", "nse_variance_weighted", "kge_2009", "kge_2012", "rsr", "r2", "pbias"],
    refs=True,
)


def kge_examples(d):
    d.code(*SETUP, show_output=False)
    d.code('''
result = hm.kge_2012(q_obs, q_sim)
print(f"kge_2012 = {float(result):.4f}")
''')
    d.p(("Независимый пересчёт показывает разницу между реализацией и трёхчленной формой KGE′.",
         "An independent recalculation shows the difference between the implementation and the three-term KGE′ form."))
    d.code('''
r = np.corrcoef(q_obs, q_sim)[0, 1]
alpha = q_sim.std(ddof=1) / q_obs.std(ddof=1)
beta = q_sim.mean() / q_obs.mean()
gamma = alpha / beta
four_terms = 1 - np.sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2 + (gamma - 1)**2)
three_terms = 1 - np.sqrt((r - 1)**2 + (beta - 1)**2 + (gamma - 1)**2)
print(f"{four_terms:.4f} {three_terms:.4f}")
''')
    d.p(("По створам и водным годам:", "By gauge and by water year:"))
    d.code(*STATIONS, show_output=False)
    d.code('''
per_station = hm.kge_2012(q_obs_st, q_sim_st, axis=0, reduction="none")
print(np.round(per_station.value, 3))
''')
    d.code(*FRAME, show_output=False)
    d.code('''
by_year = hm.compute_grouped(hm.kge_2012, df, "q_obs", "q_sim", group_by="water_year")
for (water_year,), value in by_year:
    print(int(water_year), round(float(value), 3))
''')
    d.warn(("На pandas, polars и xarray ``kge_2012`` возвращает в ``value`` кортеж ``(kge, r, alpha, beta, gamma)``, а не число; ``float(result)`` вызывает ``TypeError``, а xarray с ``dim`` вызывает ``ValueError``. Значение KGE находится в первом элементе.",
            "On pandas, polars and xarray ``kge_2012`` returns the tuple ``(kge, r, alpha, beta, gamma)`` in ``value`` rather than a number; ``float(result)`` raises ``TypeError``, and xarray with ``dim`` raises ``ValueError``. The KGE value is the first element."))
    d.code('''
import pandas as pd

as_tuple = hm.kge_2012(pd.Series(q_obs), pd.Series(q_sim)).value
print(len(as_tuple), round(float(as_tuple[0]), 4))
''')


KGE12 = dict(
    name="kge_2012",
    title=("Критерий Клинга–Гупты, версия 2012 (KGE′)", "Kling–Gupta efficiency, 2012 version (KGE′)"),
    short=[("Метрика измеряет евклидово расстояние от идеальной точки в пространстве компонент: корреляции, отношения средних и отношения коэффициентов вариации. Реализация содержит также отношение стандартных отклонений, чего нет в опубликованной форме KGE′.",
            "The metric measures the Euclidean distance from the ideal point in the space of its components: correlation, the ratio of means and the ratio of coefficients of variation. The implementation also includes the ratio of standard deviations, which the published KGE′ form does not have.")],
    formula=[r"\mathrm{KGE}_{2012} = 1 - \sqrt{(r-1)^2 + (\alpha-1)^2 + (\beta-1)^2 + (\gamma-1)^2}",
             r"\alpha = \frac{\sigma_S}{\sigma_O}, \quad \beta = \frac{\mu_S}{\mu_O}, \quad \gamma = \frac{\sigma_S/\mu_S}{\sigma_O/\mu_O}"],
    symbols=[(r":math:`r` коэффициент корреляции Пирсона, :math:`\sigma` стандартное отклонение с ``ddof=1``, :math:`\mu` среднее, индексы :math:`O` и :math:`S` обозначают наблюдения и модель. Без весов суммирование идёт по ``axis``.",
              r":math:`r` is the Pearson correlation coefficient, :math:`\sigma` the standard deviation with ``ddof=1``, :math:`\mu` the mean, and the subscripts :math:`O` and :math:`S` denote observations and simulation. Without weights the sums run along ``axis``.")],
    deviation=[(r"Опубликованная форма :footcite:p:`kling2012`, как её приводят Santos et al. :footcite:p:`santos2018`, содержит три слагаемых: :math:`r`, :math:`\beta` и :math:`\gamma`. Смысл замены в том, что отношение коэффициентов вариации не зависит от смещения среднего. В ``kge_2012`` :math:`\gamma` добавлена к :math:`\alpha`, а не заменяет её, поэтому результат не равен KGE′ из литературы.",
                r"The published form :footcite:p:`kling2012`, as given by Santos et al. :footcite:p:`santos2018`, has three terms: :math:`r`, :math:`\beta` and :math:`\gamma`. The point of the substitution is that the ratio of coefficients of variation does not depend on bias in the mean. In ``kge_2012`` :math:`\gamma` is added to :math:`\alpha` rather than replacing it, so the result differs from the KGE′ of the literature."),
               ("Разница видна в примере ниже. Сравнивая значения с опубликованными работами, считайте трёхчленную форму по компонентам из :func:`~hydrometrics.kge_components`.",
                "The difference is shown in the example below. When comparing with published values, compute the three-term form from the components returned by :func:`~hydrometrics.kge_components`.")],
    range="(-∞, 1]", optimum="1", dir="up",
    bounds=[(r"Значение 1 достигается при :math:`r=\alpha=\beta=\gamma=1`. При среднем наблюдений, близком к нулю, :math:`\beta` и :math:`\gamma` становятся очень большими, и метрика теряет смысл: на ряде с вычтенным средним она даёт порядка :math:`-10^{14}`. Метрика рассчитана на положительные величины вроде расхода воды.",
             r"The value 1 is reached at :math:`r=\alpha=\beta=\gamma=1`. When the observed mean is close to zero, :math:`\beta` and :math:`\gamma` become very large and the metric loses meaning: on a series with its mean removed it gives about :math:`-10^{14}`. The metric is intended for positive quantities such as discharge.")],
    interp=[("Общепринятых порогов качества для этой четырёхчленной формы нет. Значение KGE не имеет встроенного ориентира, подобного ``NSE = 0``: Knoben et al. :footcite:p:`knoben2019` показывают для KGE 2009 г., что прогноз средним расходом даёт :math:`1-\\sqrt{2}\\approx-0.41`, а не 0, и требуют явно указывать опорную модель. Для реализации 2012 г. этот предел неприменим: постоянный прогноз средним даёт :math:`\\sigma_S=0`, а :math:`\\gamma=0`, поэтому значение равно :math:`1-\\sqrt{3}\\approx-0.73`.",
             "There are no accepted quality thresholds for this four-term form. KGE has no built-in reference similar to ``NSE = 0``: Knoben et al. :footcite:p:`knoben2019` show for the 2009 KGE that a mean-flow forecast yields :math:`1-\\sqrt{2}\\approx-0.41`, not 0, and call for stating the benchmark explicitly. That limit does not apply to the 2012 implementation: a constant forecast at the mean has :math:`\\sigma_S=0` and :math:`\\gamma=0`, so the value is :math:`1-\\sqrt{3}\\approx-0.73`.")],
    special=[("Постоянный прогноз средним при нулевой дисперсии ``sim`` даёт :math:`r` = NaN, поэтому и весь KGE равен NaN, хотя теоретическое значение выше получено при :math:`r=0`. Чтобы воспользоваться таким ориентиром, рассчитайте его по формуле.",
              "A constant forecast at the mean with zero variance in ``sim`` gives :math:`r` = NaN, so the whole KGE is NaN, although the theoretical value above assumes :math:`r=0`. To use that benchmark, compute it from the formula."),
             ("При ``nan_policy=\"propagate\"`` средние и СКО считаются по каждому ряду отдельно, и пропуск в одном ряду не удаляет значение из другого. Для попарного расчёта при ``axis=None`` используйте ``nan_policy=\"omit\"``.",
              "With ``nan_policy=\"propagate\"`` means and standard deviations are computed per series, so a gap in one series does not remove the value from the other. For a pairwise computation with ``axis=None`` use ``nan_policy=\"omit\"``.")],
    backend_note=[("Кортеж вместо числа на pandas, polars и xarray описан в примерах. xarray с ``dim`` вызывает ``ValueError``.",
                   "The tuple returned instead of a number on pandas, polars and xarray is described in the examples. xarray with ``dim`` raises ``ValueError``.")],
    examples=kge_examples,
    hydro=[("Разложение помогает увидеть причину низкой оценки: ошибку фазы и формы гидрографа в :math:`r`, ошибку объёма в :math:`\\beta`, ошибку амплитуды в :math:`\\alpha` и :math:`\\gamma`. Для этого сами компоненты полезнее итогового числа.",
            "The decomposition helps locate the cause of a low score: phase and shape errors of the hydrograph in :math:`r`, volume errors in :math:`\\beta`, amplitude errors in :math:`\\alpha` and :math:`\\gamma`. For that purpose the components are more useful than the final number."),
           ("Mizukami et al. :footcite:p:`mizukami2019` сообщают, что калибровка по KGE (форма 2009 г.) воспроизводит годовые максимумы стока лучше, чем калибровка по NSE. На четырёхчленную форму этот вывод автоматически не переносится.",
            "Mizukami et al. :footcite:p:`mizukami2019` report that calibration on KGE (the 2009 form) reproduces annual peak flows better than calibration on NSE. That conclusion does not automatically carry over to the four-term form."),
           ("Применять KGE′ к логарифмам расходов следует осторожно: Santos et al. :footcite:p:`santos2018` сообщают, что влияние константы, добавляемой к расходам, в этом случае меняется хаотично и не показывает тренда. В библиотеке этот случай отдельно не обрабатывается.",
            "Take care when applying KGE′ to log-transformed flows: Santos et al. :footcite:p:`santos2018` report that the effect of the constant added to flows is erratic and shows no trend in that setting. The library does not treat this case separately.")],
    related=["kge_2009", "kge_components", "r_component", "alpha_component", "beta_component", "gamma_component", "nse"],
    refs=True,
)


def crps_examples(d):
    d.p(("Ансамбль из 20 членов: разброс растёт вместе с расходом, а центр смещён вверх на 5 %.",
         "A 20-member ensemble whose spread grows with discharge and whose centre is biased up by 5 %."))
    d.code(*SETUP, show_output=False)
    d.code('''
ens_rng = np.random.default_rng(7)
members = 1.05 * q_obs[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.15 * q_obs[:, None])
print(members.shape)
print(f"CRPS = {float(hm.crps(q_obs, members)):.3f} m3/s")
''')
    d.p(("Без ансамблевого измерения ``crps`` сводится к средней абсолютной ошибке:",
         "Without an ensemble dimension ``crps`` reduces to the mean absolute error:"))
    d.code('''
deterministic = members.mean(axis=1)
print(round(float(hm.crps(q_obs, deterministic)), 3), round(float(hm.mae(q_obs, deterministic)), 3))
''')
    d.p(("Сравнение со стандартной оценкой по всем парам показывает, какой вариант реализован:",
         "A comparison with the standard all-pairs estimate shows which variant is implemented:"))
    d.code('''
m = members.shape[1]
term_obs = np.abs(members - q_obs[:, None]).mean(axis=1)
spread_sum = np.abs(members[:, :, None] - members[:, None, :]).sum(axis=(1, 2))
fair = (term_obs - spread_sum / (2 * m * (m - 1))).mean()
standard = (term_obs - spread_sum / (2 * m * m)).mean()
print(round(fair, 3), round(standard, 3))
''')
    d.p(("По сезонам: для ансамблей :func:`~hydrometrics.compute_grouped` режет массивы по первой оси, поэтому ``members`` передаётся целиком.",
         "By season: for ensembles :func:`~hydrometrics.compute_grouped` slices arrays along the first axis, so ``members`` is passed whole."))
    d.code('''
month = dates.astype("datetime64[M]").astype(int) % 12 + 1
season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")
by_season = hm.compute_grouped(hm.crps, None, q_obs, members, group_by={"season": season})
for (name,), value in by_season:
    print(name, round(float(value), 3))
''')
    d.p(("Значения по времени получаются при ``reduction=\"none\"``:", "Per-time values come from ``reduction=\"none\"``:"))
    d.code('''
per_time = hm.crps(q_obs, members, reduction="none").value
print(per_time.shape, round(float(per_time.max()), 3))
''')


CRPS = dict(
    name="crps",
    title=("Непрерывная ранжированная вероятностная оценка (CRPS)", "Continuous ranked probability score (CRPS)"),
    short=[("CRPS измеряет расстояние между прогнозным распределением и наблюдением в единицах самой величины, для расхода воды в м³/с. Для ансамбля в ``hydrometrics`` используется «честная» (fair) оценка; для детерминированного прогноза метрика равна средней абсолютной ошибке.",
            "CRPS measures the distance between the forecast distribution and the observation in the units of the variable itself, m³/s for discharge. For an ensemble ``hydrometrics`` uses the fair estimator; for a deterministic forecast the metric equals the mean absolute error.")],
    sim_doc=("Детерминированный прогноз той же формы, что ``obs``, или ансамбль с дополнительным последним измерением, ``(n, m)``.",
             "A deterministic forecast of the same shape as ``obs``, or an ensemble with an extra trailing dimension, ``(n, m)``."),
    formula=[r"\mathrm{CRPS}_t = \frac{1}{m}\sum_{j=1}^{m}\left|X_{t,j} - O_t\right| - \frac{1}{2}\cdot\frac{2}{m(m-1)}\sum_{j<k}\left|X_{t,j} - X_{t,k}\right|",
             r"\mathrm{CRPS} = \frac{1}{n}\sum_{t=1}^{n}\mathrm{CRPS}_t"],
    symbols=[(r":math:`O_t` наблюдение за срок :math:`t`, :math:`X_{t,j}` член ансамбля :math:`j` из :math:`m`, :math:`n` число сроков. Усреднение по членам идёт по последней оси, по срокам выполняет ``reduction=\"mean\"``. Если ``sim`` имеет форму ``obs``, формула заменяется на :math:`\frac{1}{n}\sum|S_t-O_t|`.",
              r":math:`O_t` is the observation at time :math:`t`, :math:`X_{t,j}` is ensemble member :math:`j` of :math:`m`, :math:`n` the number of times. Averaging over members runs along the last axis; ``reduction=\"mean\"`` averages over times. If ``sim`` has the shape of ``obs``, the formula becomes :math:`\frac{1}{n}\sum|S_t-O_t|`.")],
    deviation=[(r"Классическая ансамблевая оценка усредняет разброс по всем :math:`m^2` парам с нормировкой :math:`1/(2m^2)`. Реализация усредняет по :math:`m(m-1)/2` различным парам, то есть даёт нормировку :math:`1/(2m(m-1))` при суммировании по всем упорядоченным парам. Такой вид называют fair CRPS :footcite:p:`ferro2014`. Он меньше классической оценки на величину, зависящую от :math:`m`; разница показана в примере.",
                r"The classical ensemble estimator averages the spread over all :math:`m^2` pairs with a factor of :math:`1/(2m^2)`. The implementation averages over the :math:`m(m-1)/2` distinct pairs, which corresponds to :math:`1/(2m(m-1))` when summing over all ordered pairs. This form is known as the fair CRPS :footcite:p:`ferro2014`. It is smaller than the classical estimate by an amount that depends on :math:`m`; the example shows the difference."),
               ("Интегральное определение и его ансамблевая форма обсуждаются у Hersbach :footcite:p:`hersbach2000` и Gneiting & Raftery :footcite:p:`gneiting2007`. Строка ``formula`` в метаданных результата содержит интегральную запись, а не реализованную оценку.",
                "The integral definition and its ensemble form are discussed by Hersbach :footcite:p:`hersbach2000` and Gneiting & Raftery :footcite:p:`gneiting2007`. The ``formula`` string in the result metadata holds the integral form rather than the implemented estimator.")],
    range="[0, +∞)", optimum="0", dir="down",
    bounds=[(r"Единица измерения совпадает с единицей величины. Значение 0 достигается не только при идеальном прогнозе: для ансамбля из двух членов, охватывающих наблюдение, оценка равна нулю при любом разбросе. При случайном поиске на 200 000 ансамблях с :math:`m` от 2 до 8 отрицательных значений не нашлось, но строгого доказательства в документации нет.",
             r"The unit is that of the variable. The value 0 is not reached only by a perfect forecast: for a two-member ensemble bracketing the observation the estimate is zero at any spread. A random search over 200,000 ensembles with :math:`m` from 2 to 8 found no negative values, but this documentation offers no formal proof.")],
    interp=[("Общепринятых порогов нет: значение зависит от масштаба реки, поэтому между створами его напрямую не сравнивают. Для сопоставления используйте :ref:`metric-crpss` с явно заданным опорным прогнозом.",
             "There are no accepted thresholds: the value depends on the size of the river, so it is not compared directly across gauges. For comparisons use :ref:`metric-crpss` with an explicit reference forecast.")],
    weight_doc=("Учитывается только для детерминированного прогноза. Для ансамбля молча игнорируется. На pandas, polars и xarray параметр называется ``weight``.",
                "Used for a deterministic forecast only. Silently ignored for an ensemble. On pandas, polars and xarray the parameter is called ``weight``."),
    axis_doc=("Для детерминированного прогноза задаёт ось усреднения. Для ансамбля игнорируется: результат всегда считается по срокам.",
              "For a deterministic forecast, sets the averaging axis. Ignored for an ensemble: the result is always per time."),
    ret_note=[("Таблица относится к детерминированному вводу. Для ансамбля ``obs`` формы ``(n,)`` и ``sim`` формы ``(n, m)`` numpy даёт скаляр, а pandas, polars и xarray дают массив формы ``(n,)``, потому что ``reduction`` на них не действует.",
               "The table covers deterministic input. For an ensemble with ``obs`` of shape ``(n,)`` and ``sim`` of shape ``(n, m)`` NumPy returns a scalar, whereas pandas, polars and xarray return an array of shape ``(n,)`` because ``reduction`` has no effect there.")],
    special=[("Для ансамбля ``nan_policy=\"omit\"`` с пропусками вызывает ``IndexError``: маска формы ``(n, m)`` применяется к ``obs`` формы ``(n,)``. При ``propagate`` пропуск в ``obs`` даёт NaN в этой строке, а итоговое среднее считается через ``nanmean``, поэтому результат остаётся числом. Удалите пропущенные сроки до вызова.",
              "For an ensemble ``nan_policy=\"omit\"`` with gaps raises ``IndexError``: a mask of shape ``(n, m)`` is applied to ``obs`` of shape ``(n,)``. With ``propagate`` a gap in ``obs`` gives NaN in that row and the final mean uses ``nanmean``, so the result stays a number. Remove missing times before the call."),
             ("Ансамбль из одного члена в виде ``(n, 1)`` считается как средняя абсолютная ошибка.", "A single-member ensemble of shape ``(n, 1)`` is computed as the mean absolute error.")],
    examples=crps_examples,
    hydro=[("Метрика зависит от размера ансамбля через оценку разброса. Fair-вариант нужен как раз для сравнения ансамблей разного размера :footcite:p:`ferro2014`; если опубликованные значения получены классической оценкой, напрямую их с результатом ``crps`` сравнивать нельзя.",
            "The metric depends on ensemble size through the spread estimate. The fair variant exists to compare ensembles of different sizes :footcite:p:`ferro2014`; if published values use the classical estimator, they cannot be compared directly with ``crps``."),
           ("CRPS в абсолютных единицах определяется периодами больших расходов. В примере значение за апрель–июнь больше, чем за остальные месяцы, потому что и расход, и разброс там выше; это не означает само по себе, что в половодье ансамбль хуже. Для такого вывода нормируйте на опорный прогноз.",
            "In absolute units CRPS is dominated by high-flow periods. In the example the April to June value exceeds that of the other months because both discharge and spread are higher; this alone does not mean the ensemble is worse during the flood. To conclude that, normalise by a reference forecast.")],
    related=["crpss", "weighted_crps", "mae", "brier_score", "reliability"],
    refs=True,
)
