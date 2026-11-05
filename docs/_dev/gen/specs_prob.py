"""Metric pages, family 4: probabilistic forecasts and binary events.

weighted_crps, crpss, brier_score, reliability, sharpness, accuracy, precision, recall,
f1_score, roc_auc, pr_auc, edi, sedi.
"""
import numpy as np

from exkit import ENS, EVENT, PROB, setup
from lib import fmt
from specs_regr import NAN_STD

BINARY_OBS = ("Бинарные наблюдения: 1 событие произошло, 0 не произошло.", "Binary observations: 1 the event occurred, 0 it did not.")
PROB_SIM = ("Вероятность события той же формы, что ``obs``. Значения должны лежать в [0, 1] (NaN игнорируется), иначе ``ValueError``.", "Event probability of the same shape as ``obs``. Values must lie in [0, 1] (NaN is ignored), otherwise ``ValueError``.")
PROB_SIM_UNCHECKED = ("Вероятность события той же формы, что ``obs``. Диапазон [0, 1] не проверяется.", "Event probability of the same shape as ``obs``. The range [0, 1] is not checked.")
LABEL_SIM = ("Бинарный прогноз события: 1 событие ожидается, 0 нет.", "Binary event forecast: 1 the event is expected, 0 it is not.")

MONTH_SEASON = (
    '''
# Сезон по месяцу: половодье с апреля по июнь, остальные месяцы межень
month = dates.astype("datetime64[M]").astype(int) % 12 + 1
season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")
''',
    '''
# Season by month: flood from April to June, low flow in the other months
month = dates.astype("datetime64[M]").astype(int) % 12 + 1
season = np.where(np.isin(month, [4, 5, 6]), "flood", "low_flow")
''')

EVENT_ST = (
    '''
# Три створа с разной редкостью события: пороги 80-й, 90-й и 95-й процентили
levels = [0.8, 0.9, 0.95]
event_obs_st = np.column_stack([q_obs > np.quantile(q_obs, k) for k in levels]).astype(float)
event_sim_st = np.column_stack([q_sim > np.quantile(q_obs, k) for k in levels]).astype(float)
''',
    '''
# Three gauges with different event rarity: thresholds at the 80th, 90th and 95th percentiles
levels = [0.8, 0.9, 0.95]
event_obs_st = np.column_stack([q_obs > np.quantile(q_obs, k) for k in levels]).astype(float)
event_sim_st = np.column_stack([q_sim > np.quantile(q_obs, k) for k in levels]).astype(float)
''')

PROB_ST = (
    '''
# Вероятности события для тех же трёх порогов
event_obs_st = np.column_stack([q_obs > np.quantile(q_obs, k) for k in (0.8, 0.9, 0.95)]).astype(float)
prob_st = np.column_stack([(members > np.quantile(q_obs, k)).mean(axis=1) for k in (0.8, 0.9, 0.95)])
''',
    '''
# Event probabilities for the same three thresholds
event_obs_st = np.column_stack([q_obs > np.quantile(q_obs, k) for k in (0.8, 0.9, 0.95)]).astype(float)
prob_st = np.column_stack([(members > np.quantile(q_obs, k)).mean(axis=1) for k in (0.8, 0.9, 0.95)])
''')


def event_flow(name, check=None, kw="", extra=None, prob=False, sim="event_sim"):
    """Basic call, independent check, gauges, season groups, pandas."""
    def run(d):
        setup(d)
        d.code(*(PROB if prob else EVENT), show_output=False)
        sim_name = "prob_sim" if prob else sim
        args = f", {kw}" if kw else ""
        d.code(f'''
result = hm.{name}(event_obs, {sim_name}{args})
print(f"{name} = {{float(result):.4f}}")
''')
        if check:
            d.p(check[0])
            d.code(*check[1:])
        if extra:
            extra(d)
        d.p(("По трём створам с разной редкостью события, ``axis=0``:", "For three gauges with different event rarity, ``axis=0``:"))
        if prob:
            d.code(*PROB_ST, show_output=False)
            d.code(f'''
per_gauge = hm.{name}(event_obs_st, prob_st, axis=0{args})
print(np.round(per_gauge.value, 4))
''')
        else:
            d.code(*EVENT_ST, show_output=False)
            d.code(f'''
per_gauge = hm.{name}(event_obs_st, event_sim_st, axis=0{args})
print(np.round(per_gauge.value, 4))
''')
        d.p(("По сезонам через :func:`~hydrometrics.compute_grouped`. В межень событий нет, поэтому метрики, которые делят на число событий или прогнозов, там не определены.", "By season with :func:`~hydrometrics.compute_grouped`. There are no events in low flow, so metrics that divide by the number of events or forecasts are undefined there."))
        d.code(*MONTH_SEASON, show_output=False)
        d.code(f'''
by_season = hm.compute_grouped(hm.{name}, None, event_obs, {sim_name}, group_by={{"season": season}}{args})
for (label,), value in by_season:
    print(label, round(float(value), 4))
''')
        d.p(("На pandas результат тот же:", "On pandas the result is the same:"))
        d.code(f'''
import pandas as pd

print(round(float(hm.{name}(pd.Series(event_obs), pd.Series({sim_name}){args})), 4))
''')
    return run


# ================================================================================= weighted_crps
def wcrps_examples(d):
    setup(d)
    d.code(*ENS, show_output=False)
    d.code('''
plain = hm.crps(q_obs, members)
low_flow = hm.weighted_crps(q_obs, members, weight_func=lambda y: 1 / y)
print(f"crps = {float(plain):.3f}, weighted (1/y) = {float(low_flow):.3f} m3/s")
''')
    d.p(("Без ``weight_func`` результат совпадает с :func:`~hydrometrics.crps`; метрика с весом вида :math:`y` усиливает вклад половодья:",
         "Without ``weight_func`` the result equals :func:`~hydrometrics.crps`; a weight of the form :math:`y` strengthens the contribution of the flood:"))
    d.code('''
print(round(float(hm.weighted_crps(q_obs, members)), 3), round(float(hm.weighted_crps(q_obs, members, weight_func=lambda y: y)), 3))
''')
    d.p(("По сезонам для весов :math:`1/y`:", "By season for the weights :math:`1/y`:"))
    d.code(*MONTH_SEASON, show_output=False)
    d.code('''
by_season = hm.compute_grouped(hm.weighted_crps, None, q_obs, members, group_by={"season": season}, weight_func=lambda y: 1 / y)
for (label,), value in by_season:
    print(label, round(float(value), 3))
''')
    d.p(("Детерминированный прогноз: метрика равна взвешенной средней абсолютной ошибке.", "A deterministic forecast: the metric equals a weighted mean absolute error."))
    d.code('''
print(round(float(hm.weighted_crps(q_obs, q_sim)), 3), round(float(hm.mae(q_obs, q_sim)), 3))
''')


WCRPS = dict(
    name="weighted_crps",
    title=("Взвешенная CRPS (по наблюдениям)", "Weighted CRPS (by observation)"),
    short=[("Среднее значений :ref:`metric-crps` по срокам, взвешенное функцией от наблюдения. Функция ``weight_func`` задаёт, какие наблюдения важнее, например вес :math:`1/y` усиливает вклад малых расходов.",
            "The mean of the :ref:`metric-crps` values over times, weighted by a function of the observation. The function ``weight_func`` sets which observations matter more; for example the weight :math:`1/y` strengthens the contribution of small discharge.")],
    sig_opt=", weight_func=None",
    sim_doc=("Детерминированный прогноз той же формы, что ``obs``, или ансамбль с дополнительным последним измерением, ``(n, m)``.", "A deterministic forecast of the same shape as ``obs``, or an ensemble with an extra trailing dimension, ``(n, m)``."),
    formula=[r"\mathrm{wCRPS} = \frac{\sum_{t} u_t\,\mathrm{CRPS}_t}{\sum_{t} u_t}, \qquad u_t = w_t\cdot g(O_t)"],
    symbols=[(r":math:`\mathrm{CRPS}_t` значение :ref:`metric-crps` для срока :math:`t` (классическая оценка с делителем :math:`m^2`), :math:`g` функция ``weight_func`` (по умолчанию 1), :math:`w_t` вес ``sample_weight``. Усреднение идёт по оси ``axis``.",
              r":math:`\mathrm{CRPS}_t` is the :ref:`metric-crps` value for time :math:`t` (the classical estimate with divisor :math:`m^2`), :math:`g` the function ``weight_func`` (default 1), :math:`w_t` the weight ``sample_weight``. The mean runs along ``axis``.")],
    deviation=[("Взвешиваются наблюдения, а не подынтегральное выражение. Это не пороговая и не квантильно-взвешенная CRPS Gneiting и Ranjan :footcite:p:`gneiting2011`, где вес задаётся на оси значений величины внутри интеграла. Параметра ``fair`` у функции нет.",
                "Observations are weighted, not the integrand. This is not the threshold- or quantile-weighted CRPS of Gneiting and Ranjan :footcite:p:`gneiting2011`, where the weight is set on the axis of values of the variable inside the integral. The function has no ``fair`` parameter.")],
    range="[0, +∞)", optimum="0", dir="down",
    bounds=[("Единица измерения совпадает с единицей величины. Значение 0 достигается при совпадении прогноза с наблюдением во всех сроках с ненулевым весом. Если сумма весов равна нулю, результат NaN.",
             "The unit is that of the variable. The value 0 is reached when the forecast equals the observation at all times with non-zero weight. If the sum of weights is zero the result is NaN.")],
    interp=[("Общепринятых градаций нет. Значения с разной ``weight_func`` несопоставимы, потому что веса нормируются на свою сумму и меняют долю сроков.",
             "There are no accepted ratings. Values with different ``weight_func`` are not comparable because the weights are normalised by their own sum and change the share of the times.")],
    params_opt=[("``weight_func``", ("функция | None", "callable | None"), "``None``",
                 ("Функция от массива ``obs``, возвращающая массив весов той же формы. Умножается на ``sample_weight``, если он задан.", "A function of the array ``obs`` that returns weights of the same shape. It is multiplied by ``sample_weight`` if that is given."))],
    special=[NAN_STD, ("Ансамбль без пропусков проходит без ограничений. Член ансамбля с NaN исключается из расчёта срока, число действительных членов считается отдельно для каждого срока.", "An ensemble without gaps passes without restrictions. An ensemble member with NaN is left out of the computation for that time and the number of valid members is counted separately for each time."),
             ("Если ``weight_func`` возвращает нули или отрицательные значения, проверки нет; отрицательные веса приводят к бессмысленному результату.", "There is no check if ``weight_func`` returns zeros or negative values; negative weights give a meaningless result.")],
    examples=wcrps_examples,
    hydro=[("Вес :math:`1/y` — простой способ показать качество на межени, где обычная CRPS почти не заметна из-за малых абсолютных значений. Но это взвешивание дней, а не порога: ансамбль, плохо описывающий редкие маловодные дни, при большом числе обычных дней получает за них малый суммарный вес.",
            "The weight :math:`1/y` is a simple way to show quality in low flow, where ordinary CRPS is barely noticeable because of small absolute values. But it weights days, not thresholds: an ensemble that describes rare dry days poorly gets a small total weight for them if there are many ordinary days."),
           ("Для выбора порога по обеспеченности используйте пороговую CRPS из литературы :footcite:p:`gneiting2011`, которой в библиотеке нет.",
            "To choose a threshold by exceedance probability use the threshold-weighted CRPS of the literature :footcite:p:`gneiting2011`, which the library does not provide.")],
    related=["crps", "crpss", "mae"],
    refs=True,
)

# ======================================================================================= crpss
def crpss_examples(d):
    setup(d)
    d.code(*ENS, show_output=False)
    d.code('''
skill = hm.crpss(q_obs, members)
print(f"CRPSS (reference: mean of the observations) = {float(skill):.3f}")
''', '''
skill = hm.crpss(q_obs, members)
print(f"CRPSS (reference: mean of the observations) = {float(skill):.3f}")
''')
    d.p(("Умолчание слабое: опорный прогноз это постоянное среднее наблюдений, а не климатический ход. Честнее взять среднемноголетний гидрограф:",
         "The default is weak: the reference forecast is the constant mean of the observations, not the seasonal climatology. A fairer choice is the mean annual hydrograph:"))
    d.code('''
climatology = hm.mean_annual_hydrograph(q_obs, dates)[doy]
print(round(float(hm.crpss(q_obs, members, ref_forecast=climatology)), 3))
''')
    d.p(("Для детерминированного прогноза с умолчанием ``crpss`` равна :ref:`metric-modified_nse`: обе строятся как единица минус отношение средних абсолютных ошибок.",
         "For a deterministic forecast with the default, ``crpss`` equals :ref:`metric-modified_nse`: both are one minus a ratio of mean absolute errors."))
    d.code('''
print(round(float(hm.crpss(q_obs, q_sim)), 4), round(float(hm.modified_nse(q_obs, q_sim)), 4))
''')
    d.p(("По сезонам умолчание опирается на среднее каждого сезона:", "By season the default relies on the mean of each season:"))
    d.code(*MONTH_SEASON, show_output=False)
    d.code('''
by_season = hm.compute_grouped(hm.crpss, None, q_obs, members, group_by={"season": season})
for (label,), value in by_season:
    print(label, round(float(value), 3))
''')


CRPSS = dict(
    name="crpss",
    title=("Индекс мастерства CRPS (CRPSS)", "CRPS skill score (CRPSS)"),
    short=[("CRPSS показывает, насколько прогноз лучше опорного по :ref:`metric-crps`: единица минус отношение средней CRPS прогноза к средней CRPS опорного прогноза. Положительное значение означает выигрыш относительно опоры.",
            "CRPSS shows how much better the forecast is than a reference one in terms of :ref:`metric-crps`: one minus the ratio of the mean CRPS of the forecast to the mean CRPS of the reference forecast. A positive value means a gain over the reference.")],
    sig_opt=", ref_forecast=None",
    sim_doc=("Детерминированный прогноз той же формы, что ``obs``, или ансамбль ``(n, m)``.", "A deterministic forecast of the same shape as ``obs``, or an ensemble ``(n, m)``."),
    formula=[r"\mathrm{CRPSS} = 1 - \frac{\overline{\mathrm{CRPS}}}{\overline{\mathrm{CRPS}}_{\mathrm{ref}}}"],
    symbols=[(r"Черта обозначает (взвешенное) среднее по оси ``axis``; отношение берётся от средних, а не среднее от отношений. :math:`\mathrm{CRPS}` считается классической оценкой. Без ``ref_forecast`` опорой служит постоянный прогноз, равный среднему наблюдений вдоль оси.",
              r"The bar denotes the (weighted) mean along ``axis``; the ratio is taken of means, not the mean of ratios. :math:`\mathrm{CRPS}` uses the classical estimator. Without ``ref_forecast`` the reference is a constant forecast equal to the mean of the observations along the axis.")],
    deviation=[("Опорный прогноз по умолчанию это среднее выборки, по которой оценивается прогноз, то есть оценка получена на тех же данных. Параметра ``fair`` у функции нет. ``ref_forecast`` может быть детерминированным массивом формы ``obs`` или ансамблем ``(n, m)``; его CRPS считается так же, как для прогноза.",
                "The default reference forecast is the mean of the very sample on which the forecast is scored, so the score is in-sample. The function has no ``fair`` parameter. ``ref_forecast`` may be a deterministic array of the shape of ``obs`` or an ensemble ``(n, m)``; its CRPS is computed in the same way as for the forecast.")],
    range="(-∞, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 достигается при нулевой CRPS, значение 0 при равенстве опоре, отрицательное при худшем результате. Если CRPS опорного прогноза равна нулю, результат NaN.",
             "The value 1 is reached at zero CRPS, the value 0 when equal to the reference, a negative value when worse. If the CRPS of the reference is zero the result is NaN.")],
    interp=[("Общепринятых порогов нет: значение определяется выбором опоры, поэтому его нужно публиковать вместе с описанием опорного прогноза.",
             "There are no accepted thresholds: the value is set by the choice of the reference, so it should be published together with a description of the reference forecast.")],
    params_opt=[("``ref_forecast``", ("массив | None", "array | None"), "``None``",
                 ("Опорный прогноз: массив формы ``obs`` или ансамбль ``(n, m)``, например климатический гидрограф. Без него используется среднее наблюдений.", "A reference forecast: an array of the shape of ``obs`` or an ensemble ``(n, m)``, for example a climatological hydrograph. Without it the mean of the observations is used."))],
    special=[NAN_STD],
    examples=crpss_examples,
    hydro=[("С опорой «среднее за период» любая модель, воспроизводящая сезонный ход, получает высокий CRPSS, поскольку сезонность в этой опоре отсутствует: в примере выигрыш относительно среднемноголетнего гидрографа заметно меньше. Для рек с выраженным режимом опорой должен служить гидрограф климатического года.",
            "With a period-mean reference any model that reproduces the seasonal cycle gets a high CRPSS because the reference has no seasonality: in the example the gain over the mean annual hydrograph is clearly smaller. For rivers with a pronounced regime the reference should be a climatological-year hydrograph.")],
    related=["crps", "weighted_crps", "modified_nse", "nse"],
    refs=True,
)

# ================================================================================== brier_score
def brier_extra(d):
    d.p(("Опорный прогноз «климатическая частота» даёт :math:`\\bar{o}(1-\\bar{o})`. Индекса мастерства в библиотеке нет, он считается вручную:",
         "The reference forecast climatological frequency gives :math:`\\bar{o}(1-\\bar{o})`. The library has no skill score, so it is computed by hand:"))
    d.code('''
base_rate = event_obs.mean()
bs_climatology = base_rate * (1 - base_rate)
bs = float(hm.brier_score(event_obs, prob_sim))
print(round(bs, 5), round(bs_climatology, 5), round(1 - bs / bs_climatology, 3))
''')


BRIER = dict(
    name="brier_score",
    title=("Оценка Брайера (Brier score)", "Brier score"),
    short=[("Средний квадрат разности между прогнозной вероятностью события и исходом (0 или 1) :footcite:p:`brier1950`. Оценивает вероятностный прогноз события, например превышения порога расхода.",
            "The mean squared difference between the forecast probability of an event and the outcome (0 or 1) :footcite:p:`brier1950`. It scores a probabilistic forecast of an event, for example exceedance of a discharge threshold.")],
    obs_doc=BINARY_OBS, sim_doc=PROB_SIM,
    formula=[r"\mathrm{BS} = \frac{\sum_{i} w_i\,\left(p_i - o_i\right)^2}{\sum_{i} w_i}"],
    symbols=[(r":math:`p_i` прогнозная вероятность, :math:`o_i` исход (1 или 0), :math:`w_i` вес. Суммирование идёт по оси ``axis``.", r":math:`p_i` is the forecast probability, :math:`o_i` the outcome (1 or 0), :math:`w_i` the weight. The sum runs along ``axis``.")],
    deviation=[("Совпадает с определением. Библиотека проверяет, что ``obs`` равны 0 или 1, а ``sim`` лежат в [0, 1] (NaN игнорируется); иначе возникает ``ValueError``.",
                "It matches the definition. The library checks that ``obs`` are 0 or 1 and ``sim`` lie in [0, 1] (NaN is ignored); otherwise ``ValueError`` is raised.")],
    range="[0, 1]", optimum="0", dir="down",
    bounds=[("Значение 0 у безошибочного детерминированного прогноза 0/1. Верхняя граница 1 достигается, когда каждая вероятность противоположна исходу. Границы верны при вероятностях в [0, 1].",
             "The value 0 belongs to an error-free deterministic 0/1 forecast. The upper bound 1 is reached when every probability is opposite to the outcome. The bounds hold for probabilities in [0, 1].")],
    interp=[("Общепринятых градаций нет: значение зависит от частоты события. Для редких событий оценка мала даже у бесполезного прогноза, поэтому её сравнивают с оценкой климатической частоты (пример выше).",
             "There are no accepted ratings: the value depends on the event frequency. For rare events the score is small even for a useless forecast, so it is compared with the score of the climatological frequency (the example above).")],
    special=[NAN_STD],
    examples=event_flow("brier_score", extra=brier_extra, prob=True),
    hydro=[("Для редких событий вроде превышения 95-й обеспеченности Brier score определяется в основном качеством прогноза «ничего не произойдёт», и различия между системами тонут в малых значениях. Раздельная оценка надёжности и чёткости помогает: :ref:`metric-reliability`, :ref:`metric-sharpness`.",
            "For rare events such as exceedance of the 95th percentile the Brier score is dominated by the quality of the forecast that nothing will happen, and differences between systems drown in small values. Separate assessment of reliability and sharpness helps: :ref:`metric-reliability`, :ref:`metric-sharpness`."),
           ("Ансамблевую вероятность превышения порога при небольшом числе членов нужно оценивать с учётом конечности ансамбля; библиотека этого не делает.",
            "An ensemble probability of exceeding a threshold with a small number of members must be estimated with the finite ensemble size in mind; the library does not do this.")],
    related=["reliability", "sharpness", "crps", "roc_auc"],
    refs=True,
)

# ================================================================================== reliability
def reliability_extra(d):
    d.p(("Чрезмерно уверенный прогноз (вероятности растянуты к 0 и 1) теряет надёжность:", "An overconfident forecast (probabilities stretched towards 0 and 1) loses reliability:"))
    d.code('''
prob_sharp = np.clip(0.5 + 3 * (prob_sim - 0.5), 0, 1)
print(round(float(hm.reliability(event_obs, prob_sim)), 5), round(float(hm.reliability(event_obs, prob_sharp)), 5))
''')


RELIABILITY = dict(
    name="reliability",
    title=("Надёжность вероятностного прогноза (reliability)", "Reliability of a probabilistic forecast"),
    short=[("Компонента «надёжность» разложения оценки Брайера по Мерфи :footcite:p:`murphy1973`: взвешенный средний квадрат расхождения между прогнозной вероятностью и фактической частотой события внутри интервалов вероятности.",
            "The reliability component of the Brier score decomposition after Murphy :footcite:p:`murphy1973`: the weighted mean squared difference between the forecast probability and the observed event frequency within probability bins.")],
    sig_opt=", n_bins=10",
    obs_doc=BINARY_OBS, sim_doc=PROB_SIM,
    formula=[r"\mathrm{REL} = \frac{1}{N}\sum_{k=1}^{K} N_k\left(\bar{p}_k - \bar{o}_k\right)^2"],
    symbols=[(r":math:`K` число интервалов (``n_bins``), :math:`N_k` их вес (число пар при единичных весах), :math:`\bar{p}_k` среднее прогнозной вероятности и :math:`\bar{o}_k` частота события в интервале :math:`k`, :math:`N` общий вес. Интервалы равной ширины на [0, 1], правые границы открыты, кроме последнего интервала, куда входит :math:`p=1`.",
              r":math:`K` is the number of bins (``n_bins``), :math:`N_k` their weight (the number of pairs with unit weights), :math:`\bar{p}_k` the mean forecast probability and :math:`\bar{o}_k` the event frequency in bin :math:`k`, :math:`N` the total weight. The bins have equal width on [0, 1] and are open on the right except the last one, which includes :math:`p=1`.")],
    deviation=[("Реализован только один член разложения. Разрешающая способность и неопределённость как отдельные функции в библиотеке не представлены; сумма с :ref:`metric-brier_score` не проверяется. Значение зависит от числа интервалов ``n_bins``, которое должно быть целым не меньше 1. Диапазон ``obs`` (0 или 1) и ``sim`` ([0, 1]) проверяется, при нарушении возникает ``ValueError``.",
                "Only one term of the decomposition is implemented. Resolution and uncertainty are not provided as separate functions; the sum with :ref:`metric-brier_score` is not checked. The value depends on the number of bins ``n_bins``, which must be an integer of at least 1. The ranges of ``obs`` (0 or 1) and ``sim`` ([0, 1]) are checked; a violation raises ``ValueError``.")],
    range="[0, 1]", optimum="0", dir="down",
    bounds=[("Значение 0 означает, что в каждом интервале среднее прогноза равно частоте события. Верхняя граница 1 при вероятностях в [0, 1]. Для ряда без действительных пар или с нулевой суммой весов результат NaN.",
             "The value 0 means that in every bin the mean forecast equals the event frequency. The upper bound is 1 for probabilities in [0, 1]. For a series without valid pairs or with a zero sum of weights the result is NaN.")],
    interp=[("Общепринятых градаций нет. Значение зависит от числа интервалов и от размера выборки: при малом числе пар в интервалах оно смещено вверх. Диаграммы надёжности и их доверительные интервалы обсуждают Bröcker и Smith :footcite:p:`brocker2007`.",
             "There are no accepted ratings. The value depends on the number of bins and the sample size: with few pairs in the bins it is biased upward. Reliability diagrams and their confidence intervals are discussed by Bröcker and Smith :footcite:p:`brocker2007`.")],
    params_opt=[("``n_bins``", "int", "``10``", ("Число интервалов вероятности равной ширины: целое не меньше 1. Значения типа bool, float, str и None отвергаются с ``ValueError``.", "The number of probability bins of equal width: an integer of at least 1. Values of type bool, float, str and None are rejected with ``ValueError``."))],
    special=[NAN_STD],
    examples=event_flow("reliability", extra=reliability_extra, prob=True),
    hydro=[("Для редких паводковых событий большинство прогнозов попадает в первый интервал, а остальные интервалы содержат единичные пары; надёжность по ним оценивается шумно. Увеличение ``n_bins`` делит эти немногие пары на ещё меньшие группы, и оценка в каждом интервале становится ещё более шумной.",
            "For rare flood events most forecasts fall in the first bin and the remaining bins contain isolated pairs; the reliability from them is noisy. Increasing ``n_bins`` splits these few pairs into even smaller groups and the estimate in each bin becomes noisier.")],
    related=["brier_score", "sharpness", "roc_auc"],
    refs=True,
)

# =================================================================================== sharpness
def sharpness_extra(d):
    d.p(("Чёткость не использует наблюдения. Растянутые вероятности чётче, но надёжность падает, и оценка Брайера ухудшается:", "Sharpness does not use the observations. Stretched probabilities are sharper, but reliability drops and the Brier score worsens:"))
    d.code('''
prob_sharp = np.clip(0.5 + 3 * (prob_sim - 0.5), 0, 1)
for label, p in (("ensemble", prob_sim), ("stretched", prob_sharp)):
    print(label, round(float(hm.sharpness(event_obs, p)), 4), round(float(hm.brier_score(event_obs, p)), 5))
''')


SHARPNESS = dict(
    name="sharpness",
    title=("Чёткость вероятностного прогноза (sharpness)", "Sharpness of a probabilistic forecast"),
    short=[("Дисперсия прогнозных вероятностей. Показывает, насколько прогнозы отходят от среднего: чёткий прогноз использует вероятности, близкие к 0 и 1. Наблюдения не используются.",
            "The variance of the forecast probabilities. It shows how far the forecasts depart from their mean: a sharp forecast uses probabilities near 0 and 1. The observations are not used.")],
    obs_doc=("Наблюдения принимаются для единообразия вызова и в расчёте не участвуют.", "Observations are accepted for uniformity of the call and do not take part in the computation."),
    sim_doc=PROB_SIM_UNCHECKED,
    formula=[r"\mathrm{SHARP} = \frac{\sum_{i} w_i\,\left(p_i - \bar{p}\right)^2}{\sum_{i} w_i}"],
    symbols=[(r":math:`p_i` прогнозная вероятность, :math:`\bar{p}` её (взвешенное) среднее, :math:`w_i` вес. Делитель без поправки на степени свободы (``ddof=0``).", r":math:`p_i` is the forecast probability, :math:`\bar{p}` its (weighted) mean, :math:`w_i` the weight. The divisor has no degrees-of-freedom correction (``ddof=0``).")],
    deviation=[("Определение чёткости как дисперсии вероятностей выбрано в библиотеке; в литературе чёткость связывают с концентрацией прогнозного распределения. Чёткость полезна только вместе с надёжностью: по формулировке Gneiting et al. :footcite:p:`gneiting2007b`, прогноз должен быть как можно чётче при условии калиброванности.",
                "The definition of sharpness as the variance of probabilities is the library's choice; in the literature sharpness is tied to the concentration of the predictive distribution. Sharpness is useful only together with reliability: in the wording of Gneiting et al. :footcite:p:`gneiting2007b`, a forecast should be as sharp as possible subject to calibration.")],
    range="[0, 0.25]", optimum="0.25", dir="up",
    bounds=[("Для вероятностей в [0, 1] дисперсия не превышает 0,25 (половина прогнозов 0, половина 1). Постоянный прогноз даёт значение, равное нулю с точностью до округления: от точного 0 до порядка :math:`10^{-32}` в зависимости от константы и длины ряда. «Оптимум» здесь условный: больше означает чётче, но не лучше.",
             "For probabilities in [0, 1] the variance does not exceed 0.25 (half of the forecasts 0, half 1). A constant forecast gives a value equal to zero up to rounding: from an exact 0 to the order of :math:`10^{-32}` depending on the constant and the series length. The optimum here is conditional: larger means sharper, not better.")],
    interp=[("Порогов нет. Значение сравнивается только между прогнозами одного и того же события и вместе с :ref:`metric-reliability`.", "There are no thresholds. The value is compared only between forecasts of the same event and together with :ref:`metric-reliability`.")],
    special=[NAN_STD],
    examples=event_flow("sharpness", extra=sharpness_extra, prob=True),
    hydro=[("Для редкого события чёткость в абсолютных числах мала даже у хорошей системы, так как большинство вероятностей близки к 0. Сопоставлять её нужно с частотой события: максимально возможная дисперсия при данной частоте :math:`\\bar{o}` равна :math:`\\bar{o}(1-\\bar{o})`.",
            "For a rare event sharpness in absolute numbers is small even for a good system, since most probabilities are near 0. It should be compared with the event frequency: the maximum possible variance at a given frequency :math:`\\bar{o}` is :math:`\\bar{o}(1-\\bar{o})`.")],
    related=["reliability", "brier_score"],
    refs=True,
)

# ================================================================================= classification
def accuracy_extra(d):
    d.p(("Событие редкое (порог 90-го процентиля), поэтому прогноз «события не будет» никогда не пропускает дней без события и получает высокую долю верных:",
         "The event is rare (a threshold at the 90th percentile), so a forecast that the event will never occur is never wrong on the days without the event and gets a high share of correct:"))
    d.code('''
never = np.zeros_like(event_obs)
print(round(float(hm.accuracy(event_obs, event_sim)), 4), round(float(hm.accuracy(event_obs, never)), 4))
''')


ACCURACY = dict(
    name="accuracy",
    title=("Доля верных классификаций (accuracy)", "Accuracy (fraction correct)"),
    short=[("Доля пар, в которых прогнозная метка совпала с наблюдённой: сумма верных прогнозов события и его отсутствия, делённая на число пар.",
            "The share of pairs in which the forecast label matched the observed one: the sum of correct forecasts of the event and of its absence divided by the number of pairs.")],
    obs_doc=("Наблюдённые метки. Сравнение идёт на равенство, поэтому подходят и многоклассовые метки.", "Observed labels. The comparison is for equality, so multiclass labels also work."),
    sim_doc=("Прогнозные метки той же формы.", "Forecast labels of the same shape."),
    formula=[r"\mathrm{ACC} = \frac{a + d}{a + b + c + d} = \frac{\sum_{i} w_i\,\mathbb{1}(O_i = S_i)}{\sum_{i} w_i}"],
    symbols=[(r":math:`a` — события предсказаны верно, :math:`b` ложные тревоги, :math:`c` пропуски, :math:`d` верные отрицания в таблице сопряжённости. Для бинарных меток обе записи совпадают.",
              r":math:`a` hits, :math:`b` false alarms, :math:`c` misses, :math:`d` correct negatives of the contingency table. For binary labels both expressions coincide.")],
    deviation=[("Совпадает с определением. Пара с пропуском исключается, а не засчитывается как ошибка.", "It matches the definition. A pair with a gap is excluded, not counted as an error.")],
    range="[0, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 означает полное совпадение меток. Для редкого события значение близко к 1 и у бесполезного прогноза (пример выше), поэтому верхняя граница почти не различает системы.",
             "The value 1 means a full match of labels. For a rare event the value is close to 1 even for a useless forecast (the example above), so the upper bound hardly distinguishes systems.")],
    interp=[("Общепринятых градаций нет. Значение нужно читать относительно доли тривиального прогноза «события не будет», равной :math:`1 - \\bar{o}`.", "There are no accepted ratings. The value must be read relative to the share of the trivial forecast that the event will not occur, equal to :math:`1 - \\bar{o}`.")],
    special=[NAN_STD],
    examples=event_flow("accuracy", extra=accuracy_extra),
    hydro=[("Паводки и маловодье — редкие события, и accuracy для них почти всегда высока. Для оценки прогнозов редких событий используйте :ref:`metric-recall`, :ref:`metric-precision` или индексы :ref:`metric-edi` и :ref:`metric-sedi`.",
            "Floods and drought are rare events and accuracy for them is almost always high. To assess forecasts of rare events use :ref:`metric-recall`, :ref:`metric-precision` or the indices :ref:`metric-edi` and :ref:`metric-sedi`.")],
    related=["precision", "recall", "f1_score", "edi", "sedi"],
    refs=False,
)


def contingency_extra(name):
    def run(d):
        d.p(("Таблица сопряжённости для вычисления вручную: a попадания, b ложные тревоги, c пропуски, d верные отрицания.",
             "The contingency table for a hand calculation: a hits, b false alarms, c misses, d correct negatives."))
        d.code('''
a = int(np.sum((event_obs == 1) & (event_sim == 1)))
b = int(np.sum((event_obs == 0) & (event_sim == 1)))
c = int(np.sum((event_obs == 1) & (event_sim == 0)))
d_ = int(np.sum((event_obs == 0) & (event_sim == 0)))
print(a, b, c, d_)
''')
    return run


PRECISION_DEV = ("Совпадает с определением. В числителе стоят попадания, в знаменателе все прогнозы события. Если событие не прогнозировалось ни разу, знаменатель равен нулю и результат NaN. Метка положительного класса задаётся аргументом ``positive_class``.",
                 "It matches the definition. The numerator holds the hits, the denominator all forecasts of the event. If the event was never forecast the denominator is zero and the result is NaN. The positive class label is set by the argument ``positive_class``.")
POSITIVE_CLASS = ("``positive_class``", "int", "``1``", ("Метка положительного класса (события).", "Label of the positive class (the event)."))


def precision_extra(d):
    contingency_extra("precision")(d)
    d.code('''
print(round(a / (a + b), 4), round(float(hm.precision(event_obs, event_sim)), 4))
''')


PRECISION = dict(
    name="precision",
    title=("Точность прогноза события (precision)", "Precision of an event forecast"),
    short=[("Доля прогнозов события, которые оправдались. Дополнение до единицы это доля ложных тревог среди всех тревог (false alarm ratio).",
            "The share of event forecasts that proved right. Its complement to one is the share of false alarms among all alarms (the false alarm ratio).")],
    sig_opt=", positive_class=1",
    obs_doc=BINARY_OBS, sim_doc=LABEL_SIM,
    formula=[r"\mathrm{precision} = \frac{a}{a + b}"],
    symbols=[(r":math:`a` число попаданий (событие прогнозировалось и произошло), :math:`b` число ложных тревог (прогнозировалось, но не произошло); при весах суммируются веса.", r":math:`a` is the number of hits (the event was forecast and occurred), :math:`b` the number of false alarms (forecast but did not occur); with weights the weights are summed.")],
    deviation=[PRECISION_DEV],
    range="[0, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 означает отсутствие ложных тревог. Значение не зависит от пропусков события, поэтому его следует читать вместе с :ref:`metric-recall`.", "The value 1 means no false alarms. The value does not depend on missed events, so it should be read together with :ref:`metric-recall`.")],
    interp=[("Общепринятых градаций нет. Значение зависит от частоты события: чем реже событие, тем ниже precision при той же способности системы различать.", "There are no accepted ratings. The value depends on the event frequency: the rarer the event, the lower the precision at the same discriminating ability of the system.")],
    params_opt=[POSITIVE_CLASS],
    special=[NAN_STD, ("Нет ни одного прогноза события: NaN.", "No forecast of the event: NaN.")],
    examples=event_flow("precision", extra=precision_extra),
    hydro=[("Для системы оповещения о паводке precision это доля тревог, после которых паводок действительно наступил; низкое значение приводит к потере доверия потребителей. Оно не учитывает пропущенные паводки.",
            "For a flood warning system precision is the share of alarms after which a flood actually occurred; a low value leads to a loss of confidence among users. It does not account for missed floods.")],
    related=["recall", "f1_score", "accuracy", "edi"],
    refs=False,
)


def recall_extra(d):
    contingency_extra("recall")(d)
    d.code('''
print(round(a / (a + c), 4), round(float(hm.recall(event_obs, event_sim)), 4))
''')


RECALL = dict(
    name="recall",
    title=("Полнота прогноза события (recall, вероятность обнаружения)", "Recall of an event forecast (probability of detection)"),
    short=[("Доля произошедших событий, которые были спрогнозированы. В метеорологической верификации это вероятность обнаружения, hit rate :math:`H`.",
            "The share of observed events that were forecast. In meteorological verification this is the probability of detection, the hit rate :math:`H`.")],
    sig_opt=", positive_class=1",
    obs_doc=BINARY_OBS, sim_doc=LABEL_SIM,
    formula=[r"\mathrm{recall} = H = \frac{a}{a + c}"],
    symbols=[(r":math:`a` число попаданий, :math:`c` число пропусков (событие произошло, но не прогнозировалось); при весах суммируются веса.", r":math:`a` is the number of hits, :math:`c` the number of misses (the event occurred but was not forecast); with weights the weights are summed.")],
    deviation=[("Совпадает с определением. Если событий в наблюдениях не было, знаменатель равен нулю и результат NaN. Метка положительного класса задаётся аргументом ``positive_class``.", "It matches the definition. If there were no events in the observations the denominator is zero and the result is NaN. The positive class label is set by the argument ``positive_class``.")],
    range="[0, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 означает отсутствие пропусков. Тривиальный прогноз «событие всегда» даёт 1, поэтому значение нужно читать вместе с :ref:`metric-precision`.", "The value 1 means no misses. The trivial forecast that the event always occurs gives 1, so the value must be read together with :ref:`metric-precision`.")],
    interp=[("Общепринятых градаций нет. Значение определяется требованиями потребителя: для оповещения о паводке цена пропуска обычно выше цены ложной тревоги.", "There are no accepted ratings. The value is set by the user's requirements: for flood warning the cost of a miss is usually higher than the cost of a false alarm.")],
    params_opt=[POSITIVE_CLASS],
    special=[NAN_STD, ("Нет ни одного события в наблюдениях: NaN.", "No event in the observations: NaN.")],
    examples=event_flow("recall", extra=recall_extra),
    hydro=[("Recall показывает долю обнаруженных паводков, но легко завышается порогом: чем ниже порог события, тем проще его обнаружить. При сравнении систем порог должен быть одинаковым и должен быть указан.",
            "Recall shows the share of detected floods but is easily inflated by the threshold: the lower the event threshold, the easier the detection. When comparing systems the threshold must be the same and must be stated.")],
    related=["precision", "f1_score", "edi", "sedi", "roc_auc"],
    refs=False,
)


def f1_extra(d):
    contingency_extra("f1_score")(d)
    d.code('''
precision_value, recall_value = a / (a + b), a / (a + c)
print(round(2 * precision_value * recall_value / (precision_value + recall_value), 4), round(float(hm.f1_score(event_obs, event_sim)), 4))
''')


F1 = dict(
    name="f1_score",
    title=("F1-мера (f1_score)", "F1 score"),
    short=[("Гармоническое среднее :ref:`metric-precision` и :ref:`metric-recall`. Высокое значение возможно только при высоких обеих составляющих.",
            "The harmonic mean of :ref:`metric-precision` and :ref:`metric-recall`. A high value is possible only if both components are high.")],
    sig_opt=", positive_class=1",
    obs_doc=BINARY_OBS, sim_doc=LABEL_SIM,
    formula=[r"F_1 = \frac{2\,P\,R}{P + R} = \frac{2a}{2a + b + c}"],
    symbols=[(r":math:`P` precision, :math:`R` recall, :math:`a`, :math:`b`, :math:`c` элементы таблицы сопряжённости. Верные отрицания :math:`d` в формуле не участвуют.", r":math:`P` is the precision, :math:`R` the recall, :math:`a`, :math:`b`, :math:`c` the elements of the contingency table. Correct negatives :math:`d` do not enter the formula.")],
    deviation=[("Совпадает с определением. Если precision и recall не определены или обе равны нулю, результат NaN.", "It matches the definition. If precision and recall are undefined, or both are zero, the result is NaN.")],
    range="[0, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 означает безошибочный прогноз события. Верные отрицания не учитываются, поэтому метрика не зависит от числа дней без события.", "The value 1 means an error-free event forecast. Correct negatives are not counted, so the metric does not depend on the number of days without the event.")],
    interp=[("Общепринятых градаций нет. F1 придаёт одинаковую цену ложным тревогам и пропускам; если цены различаются, пользуйтесь парой precision и recall.", "There are no accepted ratings. F1 gives the same price to false alarms and misses; if the costs differ, use the pair precision and recall.")],
    params_opt=[POSITIVE_CLASS],
    special=[NAN_STD, ("NaN также при precision = recall = 0: например, когда события наблюдались, но ни разу не были спрогнозированы, или наоборот.", "NaN also when precision = recall = 0: for example when events were observed but never forecast, or the other way round.")],
    examples=event_flow("f1_score", extra=f1_extra),
    hydro=[("F1 не учитывает верные отрицания, поэтому, в отличие от :ref:`metric-accuracy`, не завышается у редких событий. Но она не имеет внутреннего ориентира случайного прогноза: у случайного прогноза F1 зависит от частоты события.",
            "F1 does not count correct negatives, so unlike :ref:`metric-accuracy` it is not inflated for rare events. But it has no built-in no-skill reference: for a random forecast F1 depends on the event frequency.")],
    related=["precision", "recall", "accuracy", "sedi"],
    refs=False,
)

# ======================================================================================= roc_auc
def roc_extra(d):
    d.p(("AUC равна вероятности того, что случайно выбранной паре «событие / не событие» вероятность события присвоена выше у события; совпадения считаются как половина :footcite:p:`fawcett2006`. Прямой пересчёт по парам:",
         "AUC equals the probability that, for a randomly chosen pair of an event and a non-event, the event gets the higher probability, ties counting as one half :footcite:p:`fawcett2006`. A direct recalculation over pairs:"))
    d.code('''
positive = prob_sim[event_obs == 1]
negative = prob_sim[event_obs == 0]
greater = (positive[:, None] > negative[None, :]).mean()
ties = (positive[:, None] == negative[None, :]).mean()
print(round(float(greater + 0.5 * ties), 6), round(float(hm.roc_auc(event_obs, prob_sim)), 6))
''')
    d.p(("Метрика использует только порядок оценок, поэтому любой монотонный пересчёт её не меняет, а оценки не обязаны лежать в [0, 1]:",
         "The metric uses only the order of the scores, so any monotone transformation leaves it unchanged and the scores need not lie in [0, 1]:"))
    d.code('''
print(round(float(hm.roc_auc(event_obs, q_sim)), 6), round(float(hm.roc_auc(event_obs, np.log(q_sim))), 6))
''')


ROC = dict(
    name="roc_auc",
    title=("Площадь под ROC-кривой (ROC AUC)", "Area under the ROC curve (ROC AUC)"),
    short=[("ROC AUC оценивает способность прогноза отделять случаи с событием от случаев без него: вероятность, что у события оценка выше, чем у не-события :footcite:p:`fawcett2006`. Не зависит от выбора порога вероятности.",
            "ROC AUC assesses the ability of a forecast to separate cases with the event from cases without it: the probability that the event gets a higher score than a non-event :footcite:p:`fawcett2006`. It does not depend on the choice of a probability threshold.")],
    obs_doc=BINARY_OBS, sim_doc=("Оценка события (вероятность или любой монотонный балл) той же формы, что ``obs``.", "A score for the event (a probability or any monotone score) of the same shape as ``obs``."),
    formula=[r"\mathrm{AUC} = \frac{R_1 - n_1(n_1+1)/2}{n_1\,n_0}"],
    symbols=[(r":math:`n_1` и :math:`n_0` числа событий и не-событий, :math:`R_1` сумма рангов оценок у событий (при совпадающих оценках средний ранг). Это статистика Манна–Уитни, нормированная на число пар :footcite:p:`mason2002`. Расчёт выполняется по каждому срезу вдоль оси.",
              r":math:`n_1` and :math:`n_0` are the numbers of events and non-events, :math:`R_1` the sum of the ranks of the scores of events (the mean rank for tied scores). This is the Mann–Whitney statistic normalised by the number of pairs :footcite:p:`mason2002`. The computation is done for each slice along the axis.")],
    deviation=[("Площадь считается через ранги, а не численным интегрированием ROC-кривой, поэтому совпадающие оценки дают вклад 0,5. Метки события определяются равенством ``obs == 1``. Веса не поддерживаются.", "The area is computed from ranks, not by numerical integration of the ROC curve, so tied scores contribute one half. Event labels are determined by ``obs == 1``. Weights are not supported.")],
    range="[0, 1]", optimum="1", dir="up",
    bounds=[("Значение 0,5 соответствует отсутствию различающей способности (постоянная оценка даёт ровно 0,5). Значение 1 означает идеальное разделение, значение меньше 0,5 — ранжирование в обратном порядке. Если в срезе нет событий или нет не-событий, или меньше двух пар, результат NaN.",
             "The value 0.5 corresponds to no discriminating ability (a constant score gives exactly 0.5). The value 1 means perfect separation, a value below 0.5 a reversed ranking. If a slice has no events, or no non-events, or fewer than two pairs, the result is NaN.")],
    interp=[("Общепринятых градаций качества нет; ориентир 0,5 следует из определения. AUC зависит от доли событий слабо, но при очень редких событиях ею трудно различать системы: Saito и Rehmsmeier :footcite:p:`saito2015` показывают, что на несбалансированных данных график точность–полнота информативнее ROC.",
             "There are no accepted quality ratings; the reference 0.5 follows from the definition. AUC depends only weakly on the event proportion, but with very rare events it is hard to separate systems: Saito and Rehmsmeier :footcite:p:`saito2015` show that on imbalanced data the precision-recall plot is more informative than ROC.")],
    special=[("С ``omit`` пары с пропуском в ``obs`` или ``sim`` удаляются, ``propagate`` возвращает NaN, ``raise`` вызывает ``ValueError``. Ряд без событий или без не-событий даёт NaN.", "With ``omit`` pairs with a gap in ``obs`` or ``sim`` are dropped, ``propagate`` returns NaN, ``raise`` raises ``ValueError``. A series without events or without non-events gives NaN.")],
    examples=event_flow("roc_auc", extra=roc_extra, prob=True),
    hydro=[("AUC оценивает только ранжирование. Система, у которой все вероятности завышены вдвое, получает ту же AUC, но совершенно непригодна для принятия решений по порогу вероятности. Дополняйте AUC оценками :ref:`metric-reliability` и :ref:`metric-brier_score`.",
            "AUC assesses ranking only. A system whose probabilities are all inflated twofold gets the same AUC but is entirely unfit for decisions based on a probability threshold. Complement AUC with :ref:`metric-reliability` and :ref:`metric-brier_score`.")],
    related=["pr_auc", "brier_score", "edi", "recall"],
    refs=True,
)


def pr_extra(d):
    d.p(("Случайные оценки дают значение около частоты события, а не 0,5 как у ROC AUC:", "Random scores give a value near the event frequency, not 0.5 as for ROC AUC:"))
    d.code('''
random_scores = np.random.default_rng(3).random(event_obs.size)
print(round(float(event_obs.mean()), 4), round(float(hm.pr_auc(event_obs, random_scores)), 4), round(float(hm.roc_auc(event_obs, random_scores)), 4))
''')


PR = dict(
    name="pr_auc",
    title=("Площадь под кривой точность–полнота (PR AUC, средняя точность)", "Area under the precision-recall curve (PR AUC, average precision)"),
    short=[("Средняя точность: сумма значений precision на порогах оценки, взвешенная приращениями recall. Не использует верные отрицания и потому лучше различает системы при редких событиях :footcite:p:`saito2015`.",
            "Average precision: the sum of precision values at score thresholds weighted by the recall increments. It does not use correct negatives and therefore separates systems better for rare events :footcite:p:`saito2015`.")],
    obs_doc=BINARY_OBS, sim_doc=("Оценка события (вероятность или любой монотонный балл) той же формы, что ``obs``.", "A score for the event (a probability or any monotone score) of the same shape as ``obs``."),
    formula=[r"\mathrm{AP} = \sum_{k} \left(R_k - R_{k-1}\right) P_k"],
    symbols=[(r":math:`P_k` и :math:`R_k` precision и recall при пороге, равном :math:`k`-му различному значению оценки (в порядке убывания), :math:`R_0 = 0`. Это ступенчатая сумма, а не трапеции; Davis и Goadrich :footcite:p:`davis2006` объясняют, почему линейная интерполяция между точками такой кривой завышает площадь.",
              r":math:`P_k` and :math:`R_k` are the precision and recall at a threshold equal to the :math:`k`-th distinct score value (in descending order), :math:`R_0 = 0`. This is a step sum, not trapezoids; Davis and Goadrich :footcite:p:`davis2006` explain why linear interpolation between points of such a curve overstates the area.")],
    deviation=[("Реализована средняя точность (ступенчатая сумма), а не площадь по трапециям. Веса не поддерживаются. Метки события определяются равенством ``obs == 1``.", "Average precision (a step sum) is implemented, not the area by trapezoids. Weights are not supported. Event labels are determined by ``obs == 1``.")],
    range="[0, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 означает идеальное разделение. Ориентир случайной системы равен частоте события и потому зависит от данных. Если в срезе меньше двух пар или нет обоих классов, результат NaN.", "The value 1 means perfect separation. The reference of a random system equals the event frequency and so depends on the data. If a slice has fewer than two pairs or lacks either class the result is NaN.")],
    interp=[("Общепринятых градаций нет. Значение нужно сравнивать с частотой события.", "There are no accepted ratings. The value must be compared with the event frequency.")],
    special=[("С ``omit`` пары с пропуском в ``obs`` или ``sim`` удаляются, ``propagate`` возвращает NaN, ``raise`` вызывает ``ValueError``. Ряд без событий или без не-событий даёт NaN.", "With ``omit`` pairs with a gap in ``obs`` or ``sim`` are dropped, ``propagate`` returns NaN, ``raise`` raises ``ValueError``. A series without events or without non-events gives NaN.")],
    examples=event_flow("pr_auc", extra=pr_extra, prob=True),
    hydro=[("Для оповещений о редких паводках PR AUC чувствительнее к числу ложных тревог, чем ROC AUC, поскольку precision прямо учитывает их долю среди тревог. Результат при этом зависит от частоты события в выборке, и PR AUC разных створов с разной частотой напрямую не сопоставляют.",
            "For warnings of rare floods PR AUC is more sensitive to the number of false alarms than ROC AUC because precision directly accounts for their share among alarms. The result depends on the event frequency in the sample, so PR AUC of gauges with different frequencies is not compared directly.")],
    related=["roc_auc", "precision", "recall", "f1_score"],
    refs=True,
)

# ================================================================================== edi / sedi
def edi_extra(d):
    contingency_extra("edi")(d)
    d.p(("Hit rate :math:`H` и false alarm rate :math:`F` и пересчёт по формуле:", "The hit rate :math:`H`, the false alarm rate :math:`F` and a recalculation from the formula:"))
    d.code('''
hit_rate = a / (a + c)
false_alarm_rate = b / (b + d_)
by_hand = (np.log(false_alarm_rate) - np.log(hit_rate)) / (np.log(false_alarm_rate) + np.log(hit_rate))
print(round(hit_rate, 4), round(false_alarm_rate, 4), round(float(by_hand), 4), round(float(hm.edi(event_obs, event_sim)), 4))
''')
    d.p(("Безошибочный прогноз даёт :math:`H=1`, :math:`F=0` и значение равно 1 по определению:", "An error-free forecast gives :math:`H=1`, :math:`F=0` and the value is 1 by definition:"))
    d.code('''
print(hm.edi(event_obs, event_obs).value)
''')


EDI = dict(
    name="edi",
    title=("Индекс экстремальной зависимости (EDI)", "Extremal dependence index (EDI)"),
    short=[("EDI измеряет качество бинарного детерминированного прогноза редкого события через вероятность обнаружения :math:`H` и долю ложных тревог :math:`F` :footcite:p:`ferro2011`. Индекс разработан для редких событий.",
            "EDI measures the quality of a binary deterministic forecast of a rare event through the hit rate :math:`H` and the false alarm rate :math:`F` :footcite:p:`ferro2011`. The index was developed for rare events.")],
    obs_doc=BINARY_OBS, sim_doc=LABEL_SIM,
    formula=[r"\mathrm{EDI} = \frac{\ln F - \ln H}{\ln F + \ln H}, \qquad H = \frac{a}{a+c}, \quad F = \frac{b}{b+d}"],
    symbols=[(r":math:`a` попадания, :math:`b` ложные тревоги, :math:`c` пропуски, :math:`d` верные отрицания; :math:`H` вероятность обнаружения, :math:`F` доля ложных тревог среди дней без события (false alarm rate, не путать с false alarm ratio). Формула взята из реализации; текст Ferro и Stephenson при подготовке не читался (см. :doc:`/user_guide/known_limits`).",
              r":math:`a` hits, :math:`b` false alarms, :math:`c` misses, :math:`d` correct negatives; :math:`H` is the hit rate, :math:`F` the false alarm rate among days without the event (not to be confused with the false alarm ratio). The formula is taken from the implementation; the text of Ferro and Stephenson was not read when this page was prepared (see :doc:`/user_guide/known_limits`).")],
    deviation=[("Для безошибочного прогноза (:math:`H=1`, :math:`F=0`) функция возвращает 1 по определению. В остальных случаях, когда :math:`H` или :math:`F` равны нулю, логарифм не определён, и результат NaN. Предельные значения в этих случаях по первоисточнику не проверены.", "For an error-free forecast (:math:`H=1`, :math:`F=0`) the function returns 1 by definition. In the other cases where :math:`H` or :math:`F` is zero the logarithm is undefined and the result is NaN. The limiting values in these cases were not checked against the original source.")],
    range="[-1, 1]", optimum="1", dir="up",
    bounds=[("Значение 0 получается при :math:`F=H`, то есть у прогноза без различающей способности. Значение 1 функция возвращает при :math:`H=1` и :math:`0\\le F<1`, значение -1 при :math:`F=1` и :math:`H<1`. Отрицательное значение означает, что ложных тревог больше, чем попаданий в долях. Диапазон [-1, 1] объявлен в метаданных функции.",
             "The value 0 arises at :math:`F=H`, that is for a forecast without discriminating ability. The function returns 1 for :math:`H=1` and :math:`0\\le F<1`, and -1 for :math:`F=1` and :math:`H<1`. A negative value means that false alarms exceed hits in proportion. The range [-1, 1] is declared in the function metadata.")],
    interp=[("Общепринятых градаций нет. Ориентир 0 следует из формулы.", "There are no accepted ratings. The reference 0 follows from the formula.")],
    special=[NAN_STD, ("Нет событий или нет не-событий: NaN. При :math:`H=0` или при :math:`F=0` и :math:`H<1` (нет ложных тревог без полного обнаружения): NaN. Случай :math:`H=1`, :math:`F=0` даёт 1.", "No events or no non-events: NaN. For :math:`H=0`, or :math:`F=0` with :math:`H<1` (no false alarms without full detection): NaN. The case :math:`H=1`, :math:`F=0` gives 1.")],
    examples=event_flow("edi", extra=edi_extra),
    hydro=[("Индекс построен для редких событий, например для превышения высоких порогов обеспеченности, где доли попаданий и ложных тревог малы. При небольшой выборке числа :math:`a`, :math:`b`, :math:`c` малы и значение неустойчиво: одно событие меняет :math:`H` на десятки процентов.",
            "The index is built for rare events such as exceedance of high exceedance-probability thresholds, where the hit and false alarm rates are small. For a small sample the counts :math:`a`, :math:`b`, :math:`c` are small and the value is unstable: one event changes :math:`H` by tens of percent.")],
    related=["sedi", "recall", "precision", "roc_auc"],
    refs=True,
)


def sedi_extra(d):
    contingency_extra("sedi")(d)
    d.code('''
H, F = a / (a + c), b / (b + d_)
by_hand = (np.log(F) - np.log(H) - np.log(1 - F) + np.log(1 - H)) / (np.log(F) + np.log(H) + np.log(1 - F) + np.log(1 - H))
print(round(float(by_hand), 4), round(float(hm.sedi(event_obs, event_sim)), 4), round(float(hm.edi(event_obs, event_sim)), 4))
''')


SEDI = dict(
    name="sedi",
    title=("Симметричный индекс экстремальной зависимости (SEDI)", "Symmetric extremal dependence index (SEDI)"),
    short=[("SEDI дополняет :ref:`metric-edi` симметричной формой: те же :math:`H` и :math:`F`, но и логарифмы их дополнений до единицы, поэтому формула симметрична относительно обмена события и не-события :footcite:p:`ferro2011`.",
            "SEDI extends :ref:`metric-edi` with a symmetric form: the same :math:`H` and :math:`F` plus the logarithms of their complements to one, so the formula is symmetric under exchange of event and non-event :footcite:p:`ferro2011`.")],
    obs_doc=BINARY_OBS, sim_doc=LABEL_SIM,
    formula=[r"\mathrm{SEDI} = \frac{\ln F - \ln H - \ln(1-F) + \ln(1-H)}{\ln F + \ln H + \ln(1-F) + \ln(1-H)}"],
    symbols=[(r":math:`H = a/(a+c)` и :math:`F = b/(b+d)`, как на странице :ref:`metric-edi`. Формула взята из реализации; текст Ferro и Stephenson при подготовке не читался (см. :doc:`/user_guide/known_limits`).",
              r":math:`H = a/(a+c)` and :math:`F = b/(b+d)`, as on the page :ref:`metric-edi`. The formula is taken from the implementation; the text of Ferro and Stephenson was not read when this page was prepared (see :doc:`/user_guide/known_limits`).")],
    deviation=[("Для безошибочного прогноза (:math:`H=1`, :math:`F=0`) функция возвращает 1 по определению. В остальных случаях результат NaN, если :math:`H` или :math:`F` равны 0 или 1. Предельные значения в этих случаях по первоисточнику не проверены.", "For an error-free forecast (:math:`H=1`, :math:`F=0`) the function returns 1 by definition. In the other cases the result is NaN if :math:`H` or :math:`F` equals 0 or 1. The limiting values in these cases were not checked against the original source.")],
    range="[-1, 1]", optimum="1", dir="up",
    bounds=[("Значение 0 получается при :math:`F=H`, то есть у прогноза без различающей способности. Диапазон [-1, 1] объявлен в метаданных функции.", "The value 0 arises at :math:`F=H`, that is for a forecast without discriminating ability. The range [-1, 1] is declared in the function metadata.")],
    interp=[("Общепринятых градаций нет. Ориентир 0 следует из формулы.", "There are no accepted ratings. The reference 0 follows from the formula.")],
    special=[NAN_STD, ("Нет событий или нет не-событий: NaN. NaN также, если :math:`H` или :math:`F` равны 0 или 1, кроме случая :math:`H=1`, :math:`F=0`, который даёт 1.", "No events or no non-events: NaN. NaN also if :math:`H` or :math:`F` equals 0 or 1, except the case :math:`H=1`, :math:`F=0`, which gives 1.")],
    examples=event_flow("sedi", extra=sedi_extra),
    hydro=[("Как и :ref:`metric-edi`, индекс предназначен для редких событий и неустойчив на малых выборках. SEDI удобнее EDI тем, что симметрична: оценка не меняется при обмене события и не-события местами.",
            "Like :ref:`metric-edi` the index is meant for rare events and is unstable on small samples. SEDI is more convenient than EDI because it is symmetric: the score does not change when event and non-event are exchanged.")],
    related=["edi", "recall", "f1_score", "roc_auc"],
    refs=True,
)

FAMILY4 = {s["name"]: s for s in (WCRPS, CRPSS, BRIER, RELIABILITY, SHARPNESS, ACCURACY, PRECISION, RECALL, F1, ROC, PR, EDI, SEDI)}
