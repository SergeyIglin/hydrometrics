"""Reference pages after the task_2 fixes: overrides of the texts that described the old behaviour."""
from exkit import xr_dim
from lib import fmt  # noqa: F401
from metricpage import FRAME, SETUP, STATIONS
import specs_ref as _s

NSE, KGE12, CRPS = _s.NSE, _s.KGE12, _s.CRPS

# ------------------------------------------------------------------------------------- NSE
NSE["deviation"] = [
    ("Без весов и ``norm`` формула совпадает с классической. Веса и ``norm`` являются расширениями библиотеки: заданный ``norm`` заменяет :math:`\\bar{O}` в знаменателе.",
     "Without weights and ``norm`` the formula is the classical one. Weights and ``norm`` are library extensions: a given ``norm`` replaces :math:`\\bar{O}` in the denominator."),
    ("При умолчании ``nan_policy=\"omit\"`` пара с пропуском в ``obs`` или ``sim`` исключается из обеих сумм сразу, поэтому среднее :math:`\\bar{O}` тоже считается только по действительным парам.",
     "With the default ``nan_policy=\"omit\"`` a pair with a gap in ``obs`` or ``sim`` leaves both sums at once, so the mean :math:`\\bar{O}` is also computed over valid pairs only."),
]
NSE["special"] = [
    ("Умолчание ``nan_policy=\"omit\"`` удаляет пары попарно, в том числе при заданной оси; результат совпадает с расчётом по заранее отфильтрованным парам. ``\"propagate\"`` возвращает NaN, если в ряду (или в срезе вдоль оси) есть пропуск. ``\"raise\"`` вызывает ``ValueError``. Значение ``inf`` пропуском не считается: ``inf`` в ``obs`` даёт NaN, ``inf`` в ``sim`` даёт ``-inf``.",
     "The default ``nan_policy=\"omit\"`` drops pairs pairwise, also along an axis; the result equals a computation over pre-filtered pairs. ``\"propagate\"`` returns NaN if the series (or the slice along the axis) contains a gap. ``\"raise\"`` raises ``ValueError``. An ``inf`` is not a gap: ``inf`` in ``obs`` gives NaN, ``inf`` in ``sim`` gives ``-inf``."),
]


def nse_examples(d):
    d.p(("Суточный гидрограф за три водных года: половодье, межень, расходы в м³/с.",
         "A daily hydrograph over three water years with a spring flood and low flow, discharge in m³/s."))
    d.code(*SETUP, show_output=False)
    d.code('''
result = hm.nse(q_obs, q_sim)
print(f"NSE = {float(result):.3f}")
''')
    d.p(("Значения по створам: при заданной оси без ``reduction`` возвращается массив по створам, явный ``reduction=\"mean\"`` сворачивает его в одно число.",
         "Per-gauge values: with an axis and no ``reduction`` the array over the gauges is returned, an explicit ``reduction=\"mean\"`` collapses it into one number."))
    d.code(*STATIONS, show_output=False)
    d.code('''
per_station = hm.nse(q_obs_st, q_sim_st, axis=0)
print(np.round(per_station.value, 3))
print(round(float(hm.nse(q_obs_st, q_sim_st, axis=0, reduction="mean")), 3))
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
    d.p(("Пропуски: по умолчанию пары с пробелом исключаются, а ``nan_info`` сообщает их число. ``propagate`` в той же ситуации даёт NaN.",
         "Gaps: by default the pairs with a gap are dropped and ``nan_info`` reports how many. ``propagate`` gives NaN in the same situation."))
    d.code('''
q_obs_gap = q_obs.copy()
q_obs_gap[100:130] = np.nan  # месяц без наблюдений на створе
gap = hm.nse(q_obs_gap, q_sim)
print(round(float(gap), 3), gap.nan_info["n_nan_removed"])
print(hm.nse(q_obs_gap, q_sim, nan_policy="propagate").value)
''', '''
q_obs_gap = q_obs.copy()
q_obs_gap[100:130] = np.nan  # a month without observations at the gauge
gap = hm.nse(q_obs_gap, q_sim)
print(round(float(gap), 3), gap.nan_info["n_nan_removed"])
print(hm.nse(q_obs_gap, q_sim, nan_policy="propagate").value)
''')
    d.p(("Опорное значение можно задать через ``norm``, например среднюю многолетнюю норму. Значение попадает в ``norm_source``.",
         "The reference value can be set with ``norm``, for example a long-term mean. It is recorded in ``norm_source``."))
    d.code('''
long_term_mean = 30.0
custom = hm.nse(q_obs, q_sim, norm=long_term_mean)
print(round(float(custom), 3), custom.norm_source)
''')


NSE["examples"] = nse_examples

# ---------------------------------------------------------------------------------- KGE 2012
KGE12["short"] = [
    ("Метрика измеряет евклидово расстояние от идеальной точки в пространстве компонент: корреляции :math:`r`, отношения средних :math:`\\beta` и отношения коэффициентов вариации :math:`\\gamma` :footcite:p:`kling2012`.",
     "The metric measures the Euclidean distance from the ideal point in the space of its components: the correlation :math:`r`, the ratio of means :math:`\\beta` and the ratio of coefficients of variation :math:`\\gamma` :footcite:p:`kling2012`."),
]
KGE12["formula"] = [r"\mathrm{KGE}' = 1 - \sqrt{(r-1)^2 + (\beta-1)^2 + (\gamma-1)^2}",
                    r"\beta = \frac{\mu_S}{\mu_O}, \quad \gamma = \frac{\sigma_S/\mu_S}{\sigma_O/\mu_O}"]
KGE12["deviation"] = [
    ("Реализация совпадает с формой KGE′, приведённой у Santos et al. :footcite:p:`santos2018`: три слагаемых, отношение коэффициентов вариации :math:`\\gamma` заменяет отношение стандартных отклонений :math:`\\alpha`. Отличий от определения нет.",
     "The implementation matches the KGE′ form given by Santos et al. :footcite:p:`santos2018`: three terms, with the ratio of coefficients of variation :math:`\\gamma` replacing the ratio of standard deviations :math:`\\alpha`. There is no deviation from the definition."),
    ("Версии библиотеки до исправления добавляли четвёртое слагаемое :math:`\\alpha`; значения ``kge_2012``, полученные ими, с нынешними несопоставимы (см. ``CHANGELOG.md``). Компонента :math:`\\alpha` по-прежнему доступна как :func:`~hydrometrics.alpha_component` и входит в :ref:`metric-kge_2009`.",
     "Library versions before the fix added a fourth term :math:`\\alpha`; the ``kge_2012`` values they produced are not comparable with current ones (see ``CHANGELOG.md``). The component :math:`\\alpha` is still available as :func:`~hydrometrics.alpha_component` and is a term of :ref:`metric-kge_2009`."),
]
KGE12["interp"] = [
    ("Общепринятых порогов качества для KGE′ нет. Значение не имеет встроенного ориентира, подобного ``NSE = 0``: Knoben et al. :footcite:p:`knoben2019` показывают для KGE 2009 г., что прогноз средним расходом даёт :math:`1-\\sqrt{2}\\approx-0.41`, а не 0, и требуют явно указывать опорную модель.",
     "There are no accepted quality thresholds for KGE′. The value has no built-in reference similar to ``NSE = 0``: Knoben et al. :footcite:p:`knoben2019` show for the 2009 KGE that a mean-flow forecast yields :math:`1-\\sqrt{2}\\approx-0.41`, not 0, and call for stating the benchmark explicitly."),
    ("Для трёхчленной формы KGE′ тот же результат получается из формулы: у постоянного прогноза средним :math:`r=0`, :math:`\\beta=1`, :math:`\\gamma=0`, поэтому :math:`1-\\sqrt{1+0+1}`. Это расчёт по формулам; сама функция для постоянного ряда возвращает NaN, потому что корреляция не определена.",
     "For the three-term KGE′ the same result follows from the formula: a constant forecast at the mean has :math:`r=0`, :math:`\\beta=1`, :math:`\\gamma=0`, so :math:`1-\\sqrt{1+0+1}`. This is a calculation from the formulas; the function itself returns NaN for a constant series because the correlation is undefined."),
]
KGE12["special"] = [
    ("При ``nan_policy=\"omit\"`` (умолчание) средние и стандартные отклонения считаются по действительным парам; ``\"propagate\"`` возвращает NaN при любом пропуске в срезе, ``\"raise\"`` вызывает ``ValueError``.",
     "With ``nan_policy=\"omit\"`` (the default) means and standard deviations are computed over valid pairs; ``\"propagate\"`` returns NaN for any gap in the slice, ``\"raise\"`` raises ``ValueError``."),
]
KGE12["bounds"] = [
    (r"Значение 1 достигается при :math:`r=\beta=\gamma=1`. При среднем наблюдений, близком к нулю, :math:`\beta` и :math:`\gamma` становятся очень большими, и метрика теряет смысл: на ряде с вычтенным средним она даёт порядка :math:`-10^{14}`. Метрика рассчитана на положительные величины вроде расхода воды.",
     r"The value 1 is reached at :math:`r=\beta=\gamma=1`. When the observed mean is close to zero, :math:`\beta` and :math:`\gamma` become very large and the metric loses meaning: on a series with its mean removed it gives about :math:`-10^{14}`. The metric is intended for positive quantities such as discharge."),
]
KGE12["hydro"] = [
    ("Разложение помогает увидеть причину низкой оценки: ошибку фазы и формы гидрографа в :math:`r`, ошибку объёма в :math:`\\beta`, ошибку амплитуды и изменчивости в :math:`\\gamma`. Для этого сами компоненты полезнее итогового числа.",
     "The decomposition helps locate the cause of a low score: phase and shape errors of the hydrograph in :math:`r`, volume errors in :math:`\\beta`, amplitude and variability errors in :math:`\\gamma`. For that purpose the components are more useful than the final number."),
    ("Mizukami et al. :footcite:p:`mizukami2019` сообщают, что калибровка по KGE (форма 2009 г.) воспроизводит годовые максимумы стока лучше, чем калибровка по NSE. Для формы 2012 г. этот вывод в прочитанной статье не проверялся.",
     "Mizukami et al. :footcite:p:`mizukami2019` report that calibration on KGE (the 2009 form) reproduces annual peak flows better than calibration on NSE. For the 2012 form this conclusion was not examined in the paper that was read."),
    ("Применять KGE′ к логарифмам расходов следует осторожно: Santos et al. :footcite:p:`santos2018` сообщают, что влияние константы, добавляемой к расходам, в этом случае меняется хаотично и не показывает тренда. В библиотеке этот случай отдельно не обрабатывается.",
     "Take care when applying KGE′ to log-transformed flows: Santos et al. :footcite:p:`santos2018` report that the effect of the constant added to flows is erratic and shows no trend in that setting. The library does not treat this case separately."),
]
KGE12["backend_note"] = [
    ("На всех бэкендах результат это :class:`~hydrometrics.MetricResult` со скаляром, ``float(result)`` работает. Компоненты возвращает :func:`~hydrometrics.kge_components`.",
     "On every backend the result is a :class:`~hydrometrics.MetricResult` with a scalar, and ``float(result)`` works. The components are returned by :func:`~hydrometrics.kge_components`."),
]


def kge_examples(d):
    d.code(*SETUP, show_output=False)
    d.code('''
result = hm.kge_2012(q_obs, q_sim)
print(f"kge_2012 = {float(result):.4f}")
''')
    d.p(("Независимый пересчёт по трёхчленной формуле даёт то же значение; слагаемого :math:`\\alpha` в ней нет.",
         "An independent recalculation with the three-term formula gives the same value; there is no :math:`\\alpha` term in it."))
    d.code('''
r = np.corrcoef(q_obs, q_sim)[0, 1]
beta = q_sim.mean() / q_obs.mean()
gamma = (q_sim.std(ddof=1) / q_sim.mean()) / (q_obs.std(ddof=1) / q_obs.mean())
by_hand = 1 - np.sqrt((r - 1)**2 + (beta - 1)**2 + (gamma - 1)**2)
print(f"{by_hand:.4f}")
''')
    d.p(("Компоненты показывают, где потеряна точность: фаза и форма в :math:`r`, объём в :math:`\\beta`, амплитуда в :math:`\\gamma`.",
         "The components show where accuracy is lost: phase and shape in :math:`r`, volume in :math:`\\beta`, amplitude in :math:`\\gamma`."))
    d.code('''
parts = hm.kge_components(q_obs, q_sim).value
print({name: round(float(value), 3) for name, value in parts.items()})
''')
    d.p(("По створам и водным годам:", "By gauge and by water year:"))
    d.code(*STATIONS, show_output=False)
    d.code('''
per_station = hm.kge_2012(q_obs_st, q_sim_st, axis=0)
print(np.round(per_station.value, 3))
''')
    d.code(*FRAME, show_output=False)
    d.code('''
by_year = hm.compute_grouped(hm.kge_2012, df, "q_obs", "q_sim", group_by="water_year")
for (water_year,), value in by_year:
    print(int(water_year), round(float(value), 3))
''')
    d.p(("На pandas результат тот же и тоже скаляр:", "On pandas the result is the same and also a scalar:"))
    d.code('''
import pandas as pd

print(round(float(hm.kge_2012(pd.Series(q_obs), pd.Series(q_sim))), 4))
''')
    xr_dim(d, "kge_2012")


KGE12["examples"] = kge_examples

# ------------------------------------------------------------------------------------- CRPS
CRPS["short"] = [
    ("CRPS измеряет расстояние между прогнозным распределением и наблюдением в единицах самой величины, для расхода воды в м³/с. Для ансамбля по умолчанию используется классическая оценка, ``fair=True`` включает fair-оценку; для детерминированного прогноза метрика равна средней абсолютной ошибке.",
     "CRPS measures the distance between the forecast distribution and the observation in the units of the variable itself, m³/s for discharge. For an ensemble the classical estimator is the default and ``fair=True`` selects the fair estimator; for a deterministic forecast the metric equals the mean absolute error."),
]
CRPS["deviation"] = [
    (r"Классическая ансамблевая оценка усредняет разброс по всем :math:`m^2` парам с нормировкой :math:`1/(2m^2)`. Она используется по умолчанию. Параметр ``fair=True`` делит сумму по упорядоченным парам на :math:`2m(m-1)`: это fair CRPS :footcite:p:`ferro2014`. До исправления fair-вариант был единственным и применялся без возможности выбора, поэтому значения для ансамбля из прежних версий больше, чем у ``fair=True``, не равны новым умолчаниям (см. ``CHANGELOG.md``).",
     r"The classical ensemble estimator averages the spread over all :math:`m^2` pairs with a factor of :math:`1/(2m^2)`. It is the default. The parameter ``fair=True`` divides the sum over ordered pairs by :math:`2m(m-1)`: this is the fair CRPS :footcite:p:`ferro2014`. Before the fix the fair variant was the only one and could not be chosen, so ensemble values from earlier versions differ from the new defaults (see ``CHANGELOG.md``)."),
    ("Интегральное определение и его ансамблевая форма обсуждаются у Hersbach :footcite:p:`hersbach2000` и Gneiting & Raftery :footcite:p:`gneiting2007`. Строка ``formula`` в метаданных результата содержит интегральную запись, а не реализованную оценку.",
     "The integral definition and its ensemble form are discussed by Hersbach :footcite:p:`hersbach2000` and Gneiting & Raftery :footcite:p:`gneiting2007`. The ``formula`` string in the result metadata holds the integral form rather than the implemented estimator."),
]
CRPS["bounds"] = [
    (r"Единица измерения совпадает с единицей величины. Обе оценки неотрицательны: по неравенству треугольника :math:`|X_j-X_k|\le|X_j-o|+|X_k-o|` сумма по парам не превышает :math:`2(m-1)\sum_j|X_j-o|`, поэтому член разброса не больше среднего модуля ошибки членов. Поэтому ``bounds=(0, None)`` верны и при ``fair=False``, и при ``fair=True``. Значение 0 достигается не только при идеальном прогнозе: для двух членов, охватывающих наблюдение, fair-оценка равна нулю при любом разбросе.",
     r"The unit is that of the variable. Both estimators are non-negative: by the triangle inequality :math:`|X_j-X_k|\le|X_j-o|+|X_k-o|` the sum over pairs does not exceed :math:`2(m-1)\sum_j|X_j-o|`, so the spread term is at most the mean absolute error of the members. Hence ``bounds=(0, None)`` hold for both ``fair=False`` and ``fair=True``. The value 0 is not reached only by a perfect forecast: for two members bracketing the observation the fair estimator is zero at any spread."),
]
CRPS["weight_doc"] = ("Веса наблюдений той же формы, что ``obs``; действуют и для детерминированного прогноза, и для ансамбля. ``weight`` принимается как алиас.",
                      "Weights of the observations, same shape as ``obs``; used for both a deterministic forecast and an ensemble. ``weight`` is accepted as an alias.")
CRPS["axis_doc"] = ("Ось ``obs``, по которой усредняются оценки отдельных наблюдений; ``None`` усредняет по всем. Ансамбль всегда на последней оси ``sim``.",
                    "Axis of ``obs`` along which the per-observation scores are averaged; ``None`` averages over all. The ensemble is always on the last axis of ``sim``.")
CRPS["params_opt"] = [("``fair``", "bool", "``False``", ("Только для ансамбля: ``False`` классическая оценка, ``True`` fair-оценка (делитель :math:`m(m-1)`).",
                                                       "Ensemble only: ``False`` is the classical estimator, ``True`` the fair one (divisor :math:`m(m-1)`)."))]
CRPS["ret_note"] = [
    ("Таблица относится к детерминированному вводу. Для ансамбля ``obs`` формы ``(n,)`` и ``sim`` формы ``(n, m)`` на всех бэкендах возвращается скаляр; значения по срокам даёт ``reduction=\"none\"`` без оси.",
     "The table covers deterministic input. For an ensemble with ``obs`` of shape ``(n,)`` and ``sim`` of shape ``(n, m)`` a scalar is returned on every backend; the values per time come from ``reduction=\"none\"`` without an axis."),
]
CRPS["special"] = [
    ("Пропуск в наблюдении исключает срок целиком; пропуск у отдельных членов ансамбля исключает только эти члены, число членов в формуле равно числу действительных. ``\"propagate\"`` возвращает NaN при любом пропуске, ``\"raise\"`` вызывает ``ValueError`` (в том числе для членов ансамбля).",
     "A gap in the observation drops the whole time step; a gap in single ensemble members drops only those members, and the number of members in the formula is the number of valid ones. ``\"propagate\"`` returns NaN for any gap, ``\"raise\"`` raises ``ValueError`` (also for ensemble members)."),
    ("Ансамбль из одного члена в виде ``(n, 1)`` считается как средняя абсолютная ошибка.", "A single-member ensemble of shape ``(n, 1)`` is computed as the mean absolute error."),
]


def crps_examples(d):
    d.p(("Ансамбль из 20 членов: разброс растёт вместе с расходом, а центр смещён вверх на 5 %.",
         "A 20-member ensemble whose spread grows with discharge and whose centre is biased up by 5 %."))
    d.code(*SETUP, show_output=False)
    d.code('''
ens_rng = np.random.default_rng(7)
members = 1.05 * q_obs[:, None] + ens_rng.normal(0, 1, (q_obs.size, 20)) * (2 + 0.15 * q_obs[:, None])
classic = float(hm.crps(q_obs, members))
fair = float(hm.crps(q_obs, members, fair=True))
print(members.shape)
print(f"classic = {classic:.3f}  fair = {fair:.3f} m3/s")
''')
    d.p(("Независимый пересчёт классической оценки по определению:", "An independent recalculation of the classical estimator from its definition:"))
    d.code('''
m = members.shape[1]
term_obs = np.abs(members - q_obs[:, None]).mean(axis=1)
spread_sum = np.abs(members[:, :, None] - members[:, None, :]).sum(axis=(1, 2))
by_hand = (term_obs - spread_sum / (2 * m * m)).mean()
print(round(by_hand, 3))
''')
    d.p(("Без ансамблевого измерения ``crps`` сводится к средней абсолютной ошибке:",
         "Without an ensemble dimension ``crps`` reduces to the mean absolute error:"))
    d.code('''
deterministic = members.mean(axis=1)
print(round(float(hm.crps(q_obs, deterministic)), 3), round(float(hm.mae(q_obs, deterministic)), 3))
''')
    d.p(("Пропуски в наблюдениях: сроки с пропуском исключаются, ``nan_info`` сообщает их число.",
         "Gaps in the observations: the time steps with a gap are dropped and ``nan_info`` reports how many."))
    d.code('''
q_obs_gap = q_obs.copy()
q_obs_gap[100:130] = np.nan  # месяц без наблюдений
gap = hm.crps(q_obs_gap, members)
print(round(float(gap), 3), gap.nan_info["n_nan_removed"])
''', '''
q_obs_gap = q_obs.copy()
q_obs_gap[100:130] = np.nan  # a month without observations
gap = hm.crps(q_obs_gap, members)
print(round(float(gap), 3), gap.nan_info["n_nan_removed"])
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
    d.p(("Значения по срокам получаются при ``reduction=\"none\"`` без оси:", "Per-time values come from ``reduction=\"none\"`` without an axis:"))
    d.code('''
per_time = hm.crps(q_obs, members, reduction="none").value
print(per_time.shape, round(float(per_time.max()), 3))
''')


CRPS["examples"] = crps_examples
CRPS["hydro"] = [
    ("Метрика зависит от размера ансамбля через оценку разброса. Fair-вариант предназначен для сравнения ансамблей разного размера :footcite:p:`ferro2014`; опубликованные значения, полученные другой оценкой, напрямую с результатом ``crps`` сравнивать нельзя.",
     "The metric depends on ensemble size through the spread estimate. The fair variant is intended for comparing ensembles of different sizes :footcite:p:`ferro2014`; published values obtained with another estimator cannot be compared directly with the ``crps`` result."),
    ("CRPS в абсолютных единицах определяется периодами больших расходов: в половодье и расход, и разброс выше, поэтому значение за апрель–июнь больше, чем за остальные месяцы. Это само по себе не означает, что в половодье ансамбль хуже; для такого вывода нормируйте на опорный прогноз с помощью :ref:`metric-crpss`.",
     "In absolute units CRPS is dominated by high-flow periods: during the flood both discharge and spread are higher, so the April to June value exceeds that of the other months. This alone does not mean the ensemble is worse during the flood; to conclude that, normalise by a reference forecast with :ref:`metric-crpss`."),
]
