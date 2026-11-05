"""Metric pages, family 1: regime, multi-gauge and forecast-criterion metrics.

regNSE, nse_variance_weighted, ssigma, ssigma_delta, forecast_verification,
forecast_verification_delta. The source of the last four is Georgievsky & Shanochkin (2007).
"""
import numpy as np

from lib import fmt
from metricpage import FRAME, SETUP, STATIONS

# ----------------------------------------------------------------------------- shared fragments
GEORG_NOT_READ = (
    "Текст Георгиевского и Шаночкина :footcite:p:`georgievsky2007` при подготовке документации прочитать не удалось, поэтому формулы ниже взяты из реализации, а градации качества не приводятся (см. :doc:`/user_guide/known_limits`).",
    "The text of Georgievsky and Shanochkin :footcite:p:`georgievsky2007` could not be read when this documentation was prepared, so the formulas below are taken from the implementation and no rating scale is given (see :doc:`/user_guide/known_limits`).")

FORECAST_SETUP = (
    '''
# Прогнозы на 1-10 суток, выпускаемые каждые 10 суток; ошибка растёт с заблаговременностью
issue = np.arange(0, q_obs.size - 10, 10)
lead = np.arange(1, 11)
target = issue[:, None] + lead
fc_rng = np.random.default_rng(11)
obs_fc = q_obs[target].ravel()
sim_fc = (q_obs[target] * (1 + 0.02 * lead) + fc_rng.normal(0, 1, target.shape) * (1 + 0.5 * lead)).ravel()
issue_date = np.repeat(dates[issue], 10)  # метка группы: дата выпуска прогноза
''',
    '''
# Forecasts for lead times of 1-10 days issued every 10 days; the error grows with lead time
issue = np.arange(0, q_obs.size - 10, 10)
lead = np.arange(1, 11)
target = issue[:, None] + lead
fc_rng = np.random.default_rng(11)
obs_fc = q_obs[target].ravel()
sim_fc = (q_obs[target] * (1 + 0.02 * lead) + fc_rng.normal(0, 1, target.shape) * (1 + 0.5 * lead)).ravel()
issue_date = np.repeat(dates[issue], 10)  # group label: forecast issue date
''')

CAL_SETUP = (
    '''
import numpy as np
import hydrometrics as hm

rng = np.random.default_rng(42)
# Календарные годы целиком: regNSE ранжирует значения внутри календарного года
dates = np.arange("2010-01-01", "2013-01-01", dtype="datetime64[D]")
doy = (dates - dates.astype("datetime64[Y]")).astype(int)
# Половодье в конце апреля поверх зимней и летней межени, м³/с
q_obs = 12 + 240 * np.exp(-(((doy - 118) / 16.0) ** 2)) + rng.gamma(2.0, 2.5, doy.size)
# Модель запаздывает на двое суток, амплитуду воспроизводит
q_sim = np.clip(np.roll(q_obs, 2) + rng.normal(0, 1, doy.size), 0.1, None)
''',
    '''
import numpy as np
import hydrometrics as hm

rng = np.random.default_rng(42)
# Whole calendar years: regNSE ranks the values within a calendar year
dates = np.arange("2010-01-01", "2013-01-01", dtype="datetime64[D]")
doy = (dates - dates.astype("datetime64[Y]")).astype(int)
# Spring flood in late April on top of winter and summer low flow, m³/s
q_obs = 12 + 240 * np.exp(-(((doy - 118) / 16.0) ** 2)) + rng.gamma(2.0, 2.5, doy.size)
# The model lags by two days and reproduces the amplitude
q_sim = np.clip(np.roll(q_obs, 2) + rng.normal(0, 1, doy.size), 0.1, None)
''')

# ===================================================================================== regNSE
def regnse_examples(d):
    d.p(("Три календарных года суточных расходов, 1096 значений. Модель запаздывает на двое суток, но воспроизводит распределение расходов внутри года.",
         "Three calendar years of daily discharge, 1096 values. The model lags by two days but reproduces the distribution of discharge within a year."))
    d.code(*CAL_SETUP, show_output=False)
    d.code('''
reg = hm.regNSE(q_obs, q_sim, dates=dates)
print(f"regNSE = {float(reg):.3f}, NSE = {float(hm.nse(q_obs, q_sim)):.3f}")
''')
    d.p(("Порядок во времени внутри года для regNSE не важен: после случайной перестановки модельных значений внутри каждого календарного года NSE становится отрицательной, а regNSE остаётся прежней, потому что набор значений года не меняется.",
         "The order in time within a year does not matter for regNSE: after a random permutation of the simulated values inside each calendar year NSE becomes negative, while regNSE stays the same because the set of values of a year does not change."))
    d.code('''
years = dates.astype("datetime64[Y]").astype(int) + 1970
q_shuffled = q_sim.copy()
for year in np.unique(years):
    inside = np.flatnonzero(years == year)
    q_shuffled[inside] = rng.permutation(q_sim[inside])
reg_shuffled = float(hm.regNSE(q_obs, q_shuffled, dates=dates))
nse_shuffled = float(hm.nse(q_obs, q_shuffled))
print(f"regNSE = {reg_shuffled:.3f}, NSE = {nse_shuffled:.3f}")
''')
    d.p(("Знаменатель мал, когда годы похожи друг на друга и близки к кривой режима. Модель без запаздывания, но с завышением всех расходов на 15 %, получает по NSE хорошую оценку, а по regNSE гораздо худшую.",
         "The denominator is small when the years resemble each other and stay close to the regime curve. A model without lag that overestimates all discharge by 15 % scores well on NSE and much worse on regNSE."))
    d.code('''
q_biased = 1.15 * q_obs
reg_biased = float(hm.regNSE(q_obs, q_biased, dates=dates))
nse_biased = float(hm.nse(q_obs, q_biased))
print(f"regNSE = {reg_biased:.3f}, NSE = {nse_biased:.3f}")
''')
    d.p(("Кривую обеспеченности режима можно передать явно, например из более длинного ряда. Здесь она построена по этим же трём годам, поэтому результат не меняется.",
         "The regime duration curve can be passed explicitly, for example from a longer record. Here it is built from the same three years, so the result does not change."))
    d.code('''
regime = hm.mean_annual_hydrograph_duration_curve(q_obs, dates)
print(regime.shape, round(float(hm.regNSE(q_obs, q_sim, dates=dates, regime=regime)), 3))
''')
    d.p(("Значения по отдельным календарным годам при общей кривой режима. Для группировки :func:`~hydrometrics.compute_grouped` здесь не подходит, потому что ``dates`` придётся передавать целиком; срез делается вручную.",
         "Values for individual calendar years against the common regime curve. :func:`~hydrometrics.compute_grouped` is not suited here because ``dates`` would have to be passed whole; the slice is made by hand."))
    d.code('''
for year in np.unique(years):
    inside = years == year
    value = hm.regNSE(q_obs[inside], q_sim[inside], dates=dates[inside], regime=regime)
    print(year, round(float(value), 3))
''')
    d.p(("На pandas даты передаются тем же аргументом; массив дат не проверяется и сопоставляется по позиции.",
         "On pandas the dates are passed in the same argument; the array of dates is not checked and is matched by position."))
    d.code('''
import pandas as pd

series_obs, series_sim = pd.Series(q_obs), pd.Series(q_sim)
print(round(float(hm.regNSE(series_obs, series_sim, dates=pd.to_datetime(dates))), 3))
''')


def regnse_hydro(ns):
    return [
        (f"Метрика сравнивает распределения расходов внутри года, а не гидрографы по времени. В примере со случайной перестановкой модельных значений внутри года ``regNSE = {fmt(ns['reg_shuffled'])}`` при ``NSE = {fmt(ns['nse_shuffled'])}``: модель с неверной фазой паводков может получить высокую оценку. Ошибку фазы regNSE не обнаруживает, для неё нужны :ref:`metric-nse` или :ref:`metric-kge_2012`.",
         f"The metric compares the distribution of discharge within a year, not hydrographs in time. In the example with simulated values randomly permuted within each year ``regNSE = {fmt(ns['reg_shuffled'])}`` at ``NSE = {fmt(ns['nse_shuffled'])}``: a model with the wrong flood phase can score high. regNSE does not detect a phase error; use :ref:`metric-nse` or :ref:`metric-kge_2012` for that."),
        (f"Знаменатель regNSE это отклонение годовых кривых обеспеченности от кривой режима, и на реке со стабильным режимом он мал. Постоянное завышение расходов на 15 % даёт ``NSE = {fmt(ns['nse_biased'])}``, но ``regNSE = {fmt(ns['reg_biased'])}``. Метрика строже NSE к смещению и объёму; сопоставляйте её с :ref:`metric-pbias`.",
         f"The regNSE denominator is the deviation of the annual duration curves from the regime curve, and on a river with a stable regime it is small. A constant 15 % overestimate gives ``NSE = {fmt(ns['nse_biased'])}`` but ``regNSE = {fmt(ns['reg_biased'])}``. The metric is stricter than NSE toward bias and volume; compare it with :ref:`metric-pbias`."),
        ("Ранжирование идёт внутри календарного года, а не водного. Год, в котором значений меньше 365, сравнивается только с самыми большими ординатами кривой режима, поэтому неполные первый и последний годы ряда искажают оценку. Подготовьте ряд из полных календарных лет или передайте режим явно.",
         "Ranking runs within a calendar year, not a water year. A year with fewer than 365 values is compared only with the largest ordinates of the regime curve, so incomplete first and last years of a record distort the score. Prepare a record of whole calendar years or pass the regime explicitly."),
        ("Если ``regime`` не задан, кривая строится по тем же наблюдениям, которые оцениваются. На коротком ряду это делает опорную модель оптимистичной: для независимой оценки используйте кривую режима по более длинному периоду.",
         "If ``regime`` is not given, the curve is built from the same observations that are being scored. On a short record this makes the benchmark optimistic: for an independent assessment use a regime curve from a longer period."),
    ]


REGNSE = dict(
    name="regNSE",
    title=("Режимный критерий Нэша–Сатклиффа (regNSE)", "Regime Nash–Sutcliffe efficiency (regNSE)"),
    short=[("regNSE сравнивает годовые кривые обеспеченности наблюдённых и модельных расходов: значения каждого календарного года ранжируются по убыванию независимо друг от друга. Мерой служит сумма квадратов разностей одноимённых рангов, отнесённая к отклонению наблюдений от кривой обеспеченности среднего многолетнего гидрографа.",
            "regNSE compares the annual duration curves of observed and simulated discharge: the values of each calendar year are ranked in descending order independently of each other. The measure is the sum of squared differences of equal ranks, relative to the deviation of the observations from the duration curve of the mean annual hydrograph.")],
    sig="dates, regime=None, ",
    formula=[r"\mathrm{regNSE} = 1 - \frac{\sum_{y=1}^{Y}\sum_{k=1}^{365}\left(S_{(y,k)} - O_{(y,k)}\right)^2}{\sum_{y=1}^{Y}\sum_{k=1}^{365}\left(O_{(y,k)} - Q^{\mathrm{reg}}_k\right)^2}"],
    symbols=[(r":math:`O_{(y,k)}` и :math:`S_{(y,k)}` это :math:`k`-е по убыванию наблюдённое и модельное значение календарного года :math:`y`, :math:`Y` число лет, :math:`Q^{\mathrm{reg}}_k` :math:`k`-я ордината кривой обеспеченности среднего многолетнего гидрографа (средние по календарным дням, отсортированные по убыванию). Суммы объединяются по всем годам и рангам; осреднения по годам нет. В коде источником метрики указан Гарцман :footcite:p:`gartsman2023`; формула здесь взята из реализации, а не из статьи.",
              r":math:`O_{(y,k)}` and :math:`S_{(y,k)}` are the :math:`k`-th largest observed and simulated values of calendar year :math:`y`, :math:`Y` is the number of years, :math:`Q^{\mathrm{reg}}_k` is the :math:`k`-th ordinate of the duration curve of the mean annual hydrograph (calendar-day means sorted in descending order). The sums are pooled over all years and ranks; there is no averaging over years. The code names Gartsman :footcite:p:`gartsman2023` as the source of the metric; the formula here is taken from the implementation, not from the article.")],
    deviation=[("От :ref:`metric-nse` метрика отличается тремя чертами: значения ранжируются, поэтому порядок во времени теряется; опорой служит кривая обеспеченности режима, а не среднее; суммы объединяются по годам. Неполный год заполняет только первые ранги, остальные ординаты в сумму не входят. Правило для 366 дней одно: если есть високосный год, ранги 365 и 366 (два наименьших значения) усредняются до 365 рангов.",
                "regNSE differs from :ref:`metric-nse` in three ways: the values are ranked, so the order in time is lost; the benchmark is the duration curve of the regime, not the mean; the sums are pooled over years. An incomplete year fills only the first ranks and the remaining ordinates do not enter the sums. There is a single rule for 366 days: when a leap year is present, ranks 365 and 366 (the two smallest values) are averaged to give 365 ranks."),
               ("Это же правило применяется к кривой режима: для ряда с високосным годом 366 календарных средних сортируются по убыванию, и ранги 365 и 366 усредняются (ранги, а не календарные дни). Для годовых кривых и для кривой режима правило одинаково.",
                "The same rule applies to the regime curve: for a record with a leap year the 366 calendar-day means are sorted in descending order and ranks 365 and 366 are averaged (ranks, not calendar days). The rule is the same for the annual curves and the regime curve.")],
    range="(-∞, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 достигается, когда годовые кривые обеспеченности модели и наблюдений совпадают. Значение 0 соответствует модели, у которой в каждом году кривая обеспеченности равна кривой режима: тогда числитель равен знаменателю. Снизу значение не ограничено. Если все наблюдения постоянны, знаменатель равен нулю и результат равен NaN.",
             "The value 1 is reached when the annual duration curves of model and observations coincide. The value 0 corresponds to a model whose annual duration curve equals the regime curve in every year: the numerator then equals the denominator. There is no lower bound. If all observations are constant, the denominator is zero and the result is NaN.")],
    interp=[("Общепринятых градаций качества для regNSE в прочитанных источниках нет. Порогов для неё в прочитанной литературе не найдено; значения следует сопоставлять с NSE той же модели и с тем же режимом.",
             "There are no accepted quality ratings for regNSE in the sources that were read. No thresholds for it were found in the literature that was read; its values should be compared with the NSE of the same model and the same regime.")],
    params_req=[("``dates``", ("массив datetime64", "datetime64 array"), ("обязателен", "required"),
                 ("Даты наблюдений, одномерный массив той же длины, что ``obs``. Принимаются также ``pandas.DatetimeIndex`` и аналоги. Пара с пропущенной датой (NaT) исключается.",
                  "Observation dates, a one-dimensional array of the same length as ``obs``. A ``pandas.DatetimeIndex`` and similar are also accepted. A pair with a missing date (NaT) is dropped.")),
                ("``regime``", ("массив (365,) | None", "array (365,) | None"), "``None``",
                 ("Готовая кривая обеспеченности режима, отсортированная по убыванию. Если не задана, строится по ``obs`` как :func:`~hydrometrics.mean_annual_hydrograph_duration_curve`. Другая длина вызывает ``ValueError``.",
                  "A ready regime duration curve sorted in descending order. If not given, it is built from ``obs`` as :func:`~hydrometrics.mean_annual_hydrograph_duration_curve`. Any other length raises ``ValueError``."))],
    obs_doc=("Наблюдённые расходы, одномерный массив.", "Observed discharge, a one-dimensional array."),
    sim_doc=("Модельные расходы той же длины.", "Simulated discharge of the same length."),
    special=[("Значения в таблице отрицательны не из-за пропусков: ряд, на котором она посчитана, состоит из трёх похожих лет, а модельный ряд (``0.9 * obs + 4`` с шумом) отличается от наблюдений больше, чем наблюдения от кривой режима. Сравнивайте строки таблицы между собой, а не с примером ниже.",
              "The values in the table are negative not because of the gaps: the series on which it is computed consists of three similar years, and the simulated series (``0.9 * obs + 4`` plus noise) differs from the observations more than the observations differ from the regime curve. Compare the rows of the table with each other, not with the example below."),
             ("Пары с пропуском в ``obs``, ``sim`` или ``dates`` удаляются до ранжирования, поэтому при ``omit`` у обоих рядов остаются одни и те же даты. ``propagate`` возвращает NaN, ``raise`` вызывает ``ValueError``. Значение ``inf`` в ``obs`` даёт NaN.",
              "Pairs with a gap in ``obs``, ``sim`` or ``dates`` are dropped before ranking, so under ``omit`` both series keep the same dates. ``propagate`` returns NaN, ``raise`` raises ``ValueError``. An ``inf`` in ``obs`` gives NaN."),
             ("Двумерный ввод вызывает ``ValueError``: метрика определена только для одномерного ряда. Расчёт по створам выполняется в цикле.",
              "Two-dimensional input raises ``ValueError``: the metric is defined only for a one-dimensional series. Compute gauges in a loop.")],
    backend_note=[("Массив ``dates`` передаётся как есть и не берётся из индекса pandas или координаты xarray.",
                   "The ``dates`` array is passed as given and is not taken from a pandas index or an xarray coordinate.")],
    examples=regnse_examples,
    hydro=regnse_hydro,
    related=["nse", "nse_variance_weighted", "kge_2012", "log_nse"],
    refs=True,
)

# ============================================================================ nse_variance_weighted
def nvw_examples(d):
    d.p(("Три створа на одной реке: у нижнего расходы в пять раз больше, чем у верхнего, у малого притока в пять раз меньше. Модель завышает расход на 10 % и вносит случайную ошибку с одинаковым стандартным отклонением 8 м³/с на всех створах.",
         "Three gauges: the lower one has five times the discharge of the upper one, a small tributary one fifth. The model overestimates discharge by 10 % and adds random error with the same standard deviation of 8 m³/s at every gauge."))
    d.code(*SETUP, show_output=False)
    d.code('''
gauge_rng = np.random.default_rng(5)
scale = {"upper": 1.0, "lower": 5.0, "tributary": 0.2}
obs_all = np.concatenate([q_obs[:365] * k for k in scale.values()])
sim_all = obs_all * 1.1 + gauge_rng.normal(0, 8, obs_all.size)
gauge = np.repeat(list(scale), 365)  # метка створа для каждой пары
''', '''
gauge_rng = np.random.default_rng(5)
scale = {"upper": 1.0, "lower": 5.0, "tributary": 0.2}
obs_all = np.concatenate([q_obs[:365] * k for k in scale.values()])
sim_all = obs_all * 1.1 + gauge_rng.normal(0, 8, obs_all.size)
gauge = np.repeat(list(scale), 365)  # gauge label for each pair
''', show_output=False)
    d.code('''
nse_vw = hm.nse_variance_weighted(obs_all, sim_all, gauge=gauge)
print(f"variance-weighted NSE = {float(nse_vw):.3f}")
''')
    d.p(("Значения по створам и веса показывают, как получен результат: NSE каждого створа умножается на дисперсию его наблюдений.",
         "The per-gauge values and weights show how the result is formed: the NSE of each gauge is multiplied by the variance of its observations."))
    d.code('''
names = list(scale)
per_gauge = [float(hm.nse(obs_all[gauge == g], sim_all[gauge == g])) for g in names]
variance = [float(np.var(obs_all[gauge == g])) for g in names]
for g, nse_g, var_g in zip(names, per_gauge, variance):
    print(g, round(nse_g, 3), round(var_g, 1))
by_hand = np.average(per_gauge, weights=variance)
print(round(by_hand, 3), round(float(np.mean(per_gauge)), 3))
''')
    d.p(("Пропуски: при ``omit`` пара с пропуском исключается, при ``propagate`` результат равен NaN.",
         "Gaps: under ``omit`` the pair with a gap is dropped, under ``propagate`` the result is NaN."))
    d.code('''
sim_gap = sim_all.copy()
sim_gap[10] = np.nan
print(round(float(hm.nse_variance_weighted(obs_all, sim_gap, gauge=gauge)), 4))
print(hm.nse_variance_weighted(obs_all, sim_gap, gauge=gauge, nan_policy="propagate").value)
''')
    d.p(("На pandas метки створов передаются массивом той же длины:",
         "On pandas the gauge labels are passed as an array of the same length:"))
    d.code('''
import pandas as pd

print(round(float(hm.nse_variance_weighted(pd.Series(obs_all), pd.Series(sim_all), gauge=gauge)), 3))
''')


def nvw_hydro(ns):
    return [
        (f"Вес створа равен дисперсии наблюдённых расходов, выраженной в единицах величины, поэтому вес растёт как квадрат масштаба. В примере у створа с пятикратным расходом вес в 25 раз больше, чем у верхнего, а малый приток почти не влияет: значение {fmt(ns['by_hand'])} определяется двумя крупными створами, тогда как простое среднее NSE по створам даёт {fmt(float(np.mean(ns['per_gauge'])))}. Метрика скрывает плохую оценку на малой реке.",
         f"The weight of a gauge is the variance of the observed discharge in the units of the variable, so it grows with the square of the scale. In the example the gauge with five times the discharge has a weight 25 times larger than the upper one, and the small tributary hardly matters: the value {fmt(ns['by_hand'])} is set by the two large gauges, while the plain mean of the gauge NSE values gives {fmt(float(np.mean(ns['per_gauge'])))}. The metric hides a poor score on a small river."),
        ("Ряды створов объединяются в один массив с метками, поэтому длины рядов могут быть разными. Створ с постоянными наблюдениями исключается и из числителя, и из знаменателя.",
         "The gauge series are pooled in one array with labels, so the series may have different lengths. A gauge with constant observations is excluded from both the numerator and the denominator."),
        ("Многостворовое взвешивание по дисперсии рассматривают Гарцман и соавторы :footcite:p:`gartsman2024`; про их выводы о калибровке здесь сказано только то, что прочитано в статье: многомерный NSE равен среднему NSE по створам, взвешенному дисперсиями расходов.",
         "Multi-gauge variance weighting is discussed by Gartsman and co-authors :footcite:p:`gartsman2024`; of their conclusions on calibration only what was read in the paper is stated here: the multivariate NSE equals the mean NSE over gauges weighted by the discharge variances."),
    ]


NVW = dict(
    name="nse_variance_weighted",
    title=("Взвешенный по дисперсии критерий Нэша–Сатклиффа для нескольких створов", "Variance-weighted Nash–Sutcliffe efficiency for several gauges"),
    short=[("Метрика вычисляет :ref:`metric-nse` отдельно для каждого створа и усредняет результаты с весами, равными дисперсиям наблюдённых расходов на створах :footcite:p:`gartsman2024`. Створы с большей изменчивостью стока вносят больший вклад.",
            "The metric computes :ref:`metric-nse` separately for each gauge and averages the results with weights equal to the variances of the observed discharge at the gauges :footcite:p:`gartsman2024`. Gauges with more variable flow contribute more.")],
    sig="gauge, ",
    formula=[r"\mathrm{NSE}_{\mathrm{VW}} = \frac{\sum_{g=1}^{G}\sigma_g^2\,\mathrm{NSE}_g}{\sum_{g=1}^{G}\sigma_g^2}, \qquad \sigma_g^2 = \frac{1}{n_g}\sum_{i\in g}\left(O_i-\bar{O}_g\right)^2"],
    symbols=[(r":math:`G` число створов, :math:`n_g` число действительных пар на створе :math:`g`, :math:`\bar{O}_g` среднее наблюдений створа, :math:`\mathrm{NSE}_g` критерий Нэша–Сатклиффа створа. Дисперсия считается с делителем :math:`n_g` (``ddof=0``). Суммирование идёт по створам, которые задаёт массив ``gauge``.",
              r":math:`G` is the number of gauges, :math:`n_g` the number of valid pairs at gauge :math:`g`, :math:`\bar{O}_g` the mean of the gauge observations, :math:`\mathrm{NSE}_g` the Nash–Sutcliffe efficiency of the gauge. The variance uses the divisor :math:`n_g` (``ddof=0``). The sum runs over the gauges defined by the array ``gauge``.")],
    deviation=[("Формула в коде совпадает с приведённой. Створ исключается, если у него нет действительных пар, если его NSE не конечна или если наблюдения постоянны с точностью до округления. Если подходящих створов нет, результат равен NaN. Значения ``inf`` исключаются как пропуски (в отличие от большинства метрик библиотеки).",
                "The formula in the code matches the one above. A gauge is excluded if it has no valid pairs, if its NSE is not finite, or if its observations are constant up to rounding. If no suitable gauge remains the result is NaN. ``inf`` values are excluded as gaps (unlike in most metrics of the library).")],
    range="(-∞, 1]", optimum="1", dir="up",
    bounds=[("Результат это взвешенное среднее значений NSE, не превышающих 1, поэтому он не превышает 1 и снизу не ограничен. Значение 1 означает безупречный результат на всех учтённых створах; значение 0 соответствует в среднем прогнозу средним по каждому створу.",
             "The result is a weighted mean of NSE values that do not exceed 1, so it does not exceed 1 and has no lower bound. The value 1 means a perfect result at every included gauge; the value 0 corresponds on average to a forecast by the mean of each gauge.")],
    interp=[("Градаций для взвешенной оценки в литературе, которая прочитана, нет. К значению применимы те же ориентиры, что и к :ref:`metric-nse`, с поправкой на то, что результат определяют створы с наибольшей дисперсией. Пороги Moriasi et al. :footcite:p:`moriasi2007` предложены для NSE одного створа на месячном шаге.",
             "There is no rating scale for the weighted score in the literature that was read. The same reference points as for :ref:`metric-nse` apply, with the caveat that the result is set by the gauges with the largest variance. The thresholds of Moriasi et al. :footcite:p:`moriasi2007` were proposed for the NSE of a single gauge at a monthly step.")],
    params_req=[("``gauge``", ("массив", "array"), ("обязателен", "required"),
                 ("Метки створов той же длины, что ``obs``; допускаются числа и строки. Другая длина вызывает ``ValueError``.",
                  "Gauge labels of the same length as ``obs``; numbers and strings are accepted. A different length raises ``ValueError``."))],
    obs_doc=("Наблюдённые расходы всех створов в одном одномерном массиве.", "Observed discharge of all gauges in one one-dimensional array."),
    sim_doc=("Модельные расходы той же длины.", "Simulated discharge of the same length."),
    special=[("При ``omit`` пара с пропуском исключается из расчёта и NSE, и дисперсии створа; ``propagate`` даёт NaN, ``raise`` вызывает ``ValueError``. Двумерный ввод вызывает ``ValueError``: створы кодируются метками, а не столбцами.",
              "Under ``omit`` a pair with a gap is dropped from both the NSE and the variance of its gauge; ``propagate`` gives NaN, ``raise`` raises ``ValueError``. Two-dimensional input raises ``ValueError``: gauges are encoded by labels, not by columns.")],
    examples=nvw_examples,
    hydro=nvw_hydro,
    related=["nse", "regNSE", "kge_2012"],
    refs=True,
)

# ================================================================================== ssigma
def ssigma_examples(d):
    d.p(("Суточный гидрограф за три водных года, расходы в м³/с.",
         "A daily hydrograph over three water years, discharge in m³/s."))
    d.code(*SETUP, show_output=False)
    d.code('''
result = hm.ssigma(q_obs, q_sim)
print(f"S/sigma = {float(result):.3f}")
''')
    d.p(("Связь с NSE следует из формул: :math:`S/\\sigma = \\sqrt{(1-\\mathrm{NSE})\\,(n-1)/(n-m)}`. Проверка на тех же данных:",
         "The link to NSE follows from the formulas: :math:`S/\\sigma = \\sqrt{(1-\\mathrm{NSE})\\,(n-1)/(n-m)}`. A check on the same data:"))
    d.code('''
n, m = q_obs.size, 2
nse = float(hm.nse(q_obs, q_sim))
print(round(float(np.sqrt((1 - nse) * (n - 1) / (n - m))), 3))
''')
    d.p(("По створам вдоль оси; срез, где пар не больше ``m``, даёт NaN:",
         "By gauge along an axis; a slice with no more than ``m`` pairs gives NaN:"))
    d.code(*STATIONS, show_output=False)
    d.code('''
per_station = hm.ssigma(q_obs_st, q_sim_st, axis=0)
print(np.round(per_station.value, 3))
''')
    d.p(("Число параметров ``m`` уменьшает число степеней свободы ошибки. Это должно быть конечное неотрицательное число; влияние видно на коротком ряду:",
         "The number of parameters ``m`` reduces the error degrees of freedom. It must be a finite non-negative number; the effect is visible on a short series:"))
    d.code('''
short_obs, short_sim = q_obs[:30], q_sim[:30]
for m in (0, 2, 5):
    print(m, round(float(hm.ssigma(short_obs, short_sim, m=m)), 3))
''')
    d.p(("По водным годам:", "By water year:"))
    d.code(*FRAME, show_output=False)
    d.code('''
by_year = hm.compute_grouped(hm.ssigma, df, "q_obs", "q_sim", group_by="water_year")
for (water_year,), value in by_year:
    print(int(water_year), round(float(value), 3))
''')


SSIGMA = dict(
    name="ssigma",
    title=("Отношение среднеквадратической ошибки к стандартному отклонению (S/σ)", "Ratio of the root mean squared error to the standard deviation (S/σ)"),
    short=[("S/σ это среднеквадратическая ошибка, скорректированная на число параметров, в долях стандартного отклонения наблюдений :footcite:p:`georgievsky2007`. Значение меньше 1 означает, что ошибка меньше изменчивости наблюдений.",
            "S/σ is the root mean squared error, adjusted for the number of parameters, relative to the standard deviation of the observations :footcite:p:`georgievsky2007`. A value below 1 means that the error is smaller than the variability of the observations.")],
    sig="m=2, ",
    formula=[r"\frac{S}{\sigma} = \frac{\sqrt{\dfrac{1}{n-m}\sum_{i=1}^{n}\left(O_i-S_i\right)^2}}{\sqrt{\dfrac{1}{n-1}\sum_{i=1}^{n}\left(O_i-\bar{O}\right)^2}}"],
    symbols=[(r":math:`O_i` наблюдённое, :math:`S_i` модельное значение, :math:`n` число действительных пар, :math:`m` число параметров модели или прогностической зависимости (аргумент ``m``, по умолчанию 2). Суммирование идёт по оси ``axis``, при ``axis=None`` по всем элементам. Числитель обозначают :math:`S`, знаменатель :math:`\sigma`. " + GEORG_NOT_READ[0],
              r":math:`O_i` is the observed and :math:`S_i` the simulated value, :math:`n` the number of valid pairs, :math:`m` the number of parameters of the model or forecast relationship (argument ``m``, default 2). The sum runs along ``axis``, over all elements with ``axis=None``. The numerator is denoted :math:`S`, the denominator :math:`\sigma`. " + GEORG_NOT_READ[1])],
    deviation=[("Знаменатель использует несмещённую оценку (``ddof=1``), числитель делитель :math:`n-m`. Из этих определений следует связь с :ref:`metric-nse`: :math:`(S/\\sigma)^2 = (1-\\mathrm{NSE})\\,(n-1)/(n-m)`. При :math:`m=1` метрика равна :math:`\\sqrt{1-\\mathrm{NSE}}`.",
                "The denominator uses the unbiased estimate (``ddof=1``), the numerator the divisor :math:`n-m`. These definitions imply the link to :ref:`metric-nse`: :math:`(S/\\sigma)^2 = (1-\\mathrm{NSE})\\,(n-1)/(n-m)`. For :math:`m=1` the metric equals :math:`\\sqrt{1-\\mathrm{NSE}}`.")],
    range="[0, +∞)", optimum="0", dir="down",
    bounds=[("Значение 0 означает нулевую ошибку. Верхней границы нет. Если наблюдения постоянны с точностью до округления, σ равно нулю и результат NaN. Без оси при :math:`n \\le m` вызывается ``ValueError``; вдоль оси такой срез даёт NaN.",
             "The value 0 means zero error. There is no upper bound. If the observations are constant up to rounding, σ is zero and the result is NaN. Without an axis, :math:`n \\le m` raises ``ValueError``; along an axis such a slice gives NaN.")],
    interp=[("Значение 1 соответствует, при :math:`n \\gg m`, ``NSE`` около нуля: ошибка равна изменчивости наблюдений. Это следует из связи с NSE выше.",
             "At :math:`n \\gg m` the value 1 corresponds to ``NSE`` near zero: the error equals the variability of the observations. This follows from the link to NSE above."),
            ("Градации качества для S/σ здесь не приводятся: источник :footcite:p:`georgievsky2007` не был доступен, а другие источники, где пороги названы прямо, подтвердить не удалось (см. :doc:`/user_guide/known_limits`). Любой порог зависит от типа прогноза, заблаговременности и длины ряда.",
             "No rating scale for S/σ is given here: the source :footcite:p:`georgievsky2007` was not available, and other sources that name thresholds directly could not be confirmed (see :doc:`/user_guide/known_limits`). Any threshold depends on the type of forecast, the lead time and the length of the record.")],
    params_req=[("``m``", "int", "``2``",
                 ("Число параметров, уменьшающее степени свободы ошибки. Конечное неотрицательное число (int или float); отрицательное значение, NaN или inf вызывает ``ValueError``, не число вызывает ``TypeError``.",
                  "The number of parameters that reduces the error degrees of freedom. A finite non-negative number (int or float); a negative value, NaN or inf raises ``ValueError``, a non-number raises ``TypeError``."))],
    special=[("При ``omit`` пары с пропуском в ``obs`` или ``sim`` удаляются, ``n`` считается по оставшимся. ``propagate`` возвращает NaN, ``raise`` вызывает ``ValueError``.",
              "Under ``omit`` pairs with a gap in ``obs`` or ``sim`` are dropped and ``n`` is counted over the rest. ``propagate`` returns NaN, ``raise`` raises ``ValueError``.")],
    examples=ssigma_examples,
    hydro=[("S/σ, как и NSE, построена на квадратах ошибок и потому определяется крупными расходами; у периодов межени σ мало, и тот же абсолютный промах даёт гораздо большее отношение. Поэтому значение по сезонам и по водным годам лучше считать отдельно.",
            "S/σ, like NSE, is built on squared errors and therefore dominated by high flows; in low-flow periods σ is small and the same absolute miss gives a much larger ratio. The value is better computed separately by season and by water year."),
           ("Для рядов с внутригодовым ходом σ включает сезонную изменчивость, и метрика может быть низкой только потому, что сезонный ход воспроизведён. Для прогнозов с заблаговременностью смотрите :ref:`metric-ssigma_delta`, где σ берётся внутри группы.",
            "For series with a seasonal cycle σ includes the seasonal variability, so the metric can be low merely because the cycle is reproduced. For forecasts with a lead time see :ref:`metric-ssigma_delta`, where σ is taken within a group.")],
    related=["ssigma_delta", "nse", "rmse", "rsr", "forecast_verification"],
    refs=True,
)

# ============================================================================= ssigma_delta
def ssd_examples(d):
    d.p(("Суточный гидрограф и прогнозы на 1–10 суток, выпускаемые каждые 10 суток. Группа это один выпуск прогноза: десять значений с общей датой выпуска.",
         "A daily hydrograph and forecasts for 1 to 10 days issued every 10 days. A group is one forecast issue: ten values with a common issue date."))
    d.code(*SETUP, show_output=False)
    d.code(*FORECAST_SETUP, show_output=False)
    d.code('''
result = hm.ssigma_delta(obs_fc, sim_fc, ref_date=issue_date)
print(f"S/sigma_delta = {float(result):.3f}")
''')
    d.p(("С ``reduction=\"none\"`` каждое значение пары заменено оценкой его группы. Первая группа, пересчитанная вручную:",
         "With ``reduction=\"none\"`` every pair carries the score of its group. The first group recomputed by hand:"))
    d.code('''
per_pair = hm.ssigma_delta(obs_fc, sim_fc, ref_date=issue_date, reduction="none").value
o, s = obs_fc[:10], sim_fc[:10]
by_hand = np.sqrt(np.sum((o - s) ** 2) / (10 - 2)) / o.std(ddof=1)
print(round(float(per_pair[0]), 4), round(float(by_hand), 4))
''')
    d.p(("Распределение по группам: на межени σ внутри десятидневной группы мала, и отношение велико.",
         "Distribution over the groups: in low flow σ within a ten-day group is small and the ratio is large."))
    d.code('''
per_group = per_pair.reshape(-1, 10)[:, 0]
flood = np.array([obs_fc[i * 10:(i + 1) * 10].mean() > 100 for i in range(per_group.size)])
print(round(float(np.nanmedian(per_group[flood])), 3), round(float(np.nanmedian(per_group[~flood])), 3))
''')
    d.p(("На pandas метка группы передаётся тем же аргументом:", "On pandas the group label is passed in the same argument:"))
    d.code('''
import pandas as pd

print(round(float(hm.ssigma_delta(pd.Series(obs_fc), pd.Series(sim_fc), ref_date=issue_date)), 3))
''')


SSD = dict(
    name="ssigma_delta",
    title=("Отношение S/σ по группам прогнозов (S/σ_Δ)", "Group-wise S/σ ratio for forecasts (S/σ_Δ)"),
    short=[("Для каждой группы, заданной ``ref_date`` (обычно дата выпуска прогноза), считается отношение среднеквадратической ошибки к стандартному отклонению наблюдений внутри этой группы :footcite:p:`georgievsky2007`. Оценка группы присваивается всем её значениям.",
            "For each group defined by ``ref_date`` (usually the forecast issue date) the ratio of the root mean squared error to the standard deviation of the observations within that group is computed :footcite:p:`georgievsky2007`. The score of the group is assigned to all its values.")],
    sig="ref_date, m=2, ",
    formula=[r"\left(\frac{S}{\sigma_\Delta}\right)_d = \frac{\sqrt{\dfrac{1}{n_d-m}\sum_{i\in G_d}\left(O_i-S_i\right)^2}}{\sqrt{\dfrac{1}{n_d-1}\sum_{i\in G_d}\left(O_i-\bar{O}_d\right)^2}}"],
    symbols=[(r":math:`G_d` группа с меткой :math:`d`, :math:`n_d` число действительных пар в ней, :math:`\bar{O}_d` среднее наблюдений группы, :math:`m` число параметров (по умолчанию 2). Все суммы берутся внутри группы. Результат функции это среднее по значениям пар, то есть группы с большим числом пар весят больше. " + GEORG_NOT_READ[0],
              r":math:`G_d` is the group with label :math:`d`, :math:`n_d` the number of valid pairs in it, :math:`\bar{O}_d` the mean of the group observations, :math:`m` the number of parameters (default 2). All sums are taken within the group. The function result is the mean over pair values, so groups with more pairs weigh more. " + GEORG_NOT_READ[1])],
    deviation=[("От :ref:`metric-ssigma` метрика отличается только тем, что σ и S считаются внутри групп. Здесь :math:`\\sigma_\\Delta` это стандартное отклонение наблюдений внутри группы ``ref_date``, а не стандартное отклонение изменения величины за заблаговременность. Формулы библиотеки подтверждены автором и не менялись.",
                "From :ref:`metric-ssigma` the metric differs only in that S and σ are computed within groups. Here :math:`\\sigma_\\Delta` is the standard deviation of the observations within the ``ref_date`` group, not the standard deviation of the change of the quantity over the lead time. The formulas of the library were confirmed by the author and are unchanged.")],
    range="[0, +∞)", optimum="0", dir="down",
    bounds=[("Значение 0 означает нулевую ошибку, верхней границы нет. Группа с числом пар не больше ``m`` или с постоянными наблюдениями даёт NaN, и её значения в среднее не входят.",
             "The value 0 means zero error and there is no upper bound. A group with no more than ``m`` pairs or with constant observations gives NaN and its values do not enter the mean.")],
    interp=[("Градации качества не приводятся по той же причине, что и для :ref:`metric-ssigma`: источник :footcite:p:`georgievsky2007` недоступен для чтения, пороги других источников подтвердить не удалось.",
             "No rating scale is given, for the same reason as for :ref:`metric-ssigma`: the source :footcite:p:`georgievsky2007` is unavailable for reading and thresholds from other sources could not be confirmed.")],
    params_req=[("``ref_date``", ("массив", "array"), ("обязателен", "required"),
                 ("Метки групп той же формы, что ``obs``: даты, числа или строки. Другая форма вызывает ``ValueError``.",
                  "Group labels of the same shape as ``obs``: dates, numbers or strings. A different shape raises ``ValueError``.")),
                ("``m``", "int", "``2``", ("Число параметров, как в :ref:`metric-ssigma`: конечное неотрицательное число; отрицательное значение, NaN или inf вызывает ``ValueError``, не число вызывает ``TypeError``.", "The number of parameters, as in :ref:`metric-ssigma`: a finite non-negative number; a negative value, NaN or inf raises ``ValueError``, a non-number raises ``TypeError``."))],
    special=[("Пары с пропуском в ``obs`` или ``sim`` исключаются из своей группы при ``omit``; ``propagate`` возвращает NaN (в результате по парам NaN стоит на месте пропуска, а оценка группы считается по остальным значениям); ``raise`` вызывает ``ValueError``. Ось и веса не поддерживаются.",
              "Pairs with a gap in ``obs`` or ``sim`` are excluded from their group under ``omit``; ``propagate`` returns NaN (the per-pair result has NaN at the position of the gap and the group score is computed from the remaining values); ``raise`` raises ``ValueError``. Axis and weights are not supported.")],
    examples=ssd_examples,
    hydro=[("Внутри группы из десяти последовательных суток σ мала на межени и велика на половодье, поэтому одно и то же среднеквадратическое отклонение прогноза даёт разные отношения в разные сезоны. Сравнивать группы лучше внутри одного режима стока (см. пример выше).",
            "Within a group of ten consecutive days σ is small in low flow and large in the flood, so the same forecast RMSE gives different ratios in different seasons. Groups are better compared within one flow regime (see the example above)."),
           ("Размер группы должен быть заметно больше ``m``; для групп из трёх–четырёх значений оценка σ очень неустойчива.",
            "The group size must be well above ``m``; for groups of three or four values the estimate of σ is very unstable.")],
    related=["ssigma", "forecast_verification_delta", "forecast_verification", "rmse"],
    refs=True,
)

# ======================================================================= forecast_verification
def fv_examples(d):
    d.p(("Суточный гидрограф и модельный ряд. Прогноз оправдался, если ошибка меньше :math:`0.674\\,\\sigma` (σ по всем наблюдениям). Результат это доля оправдавшихся прогнозов.",
         "A daily hydrograph and a simulated series. A forecast is verified if its error is below :math:`0.674\\,\\sigma` (σ over all observations). The result is the fraction of verified forecasts."))
    d.code(*SETUP, show_output=False)
    d.code('''
result = hm.forecast_verification(q_obs, q_sim)
print(f"fraction verified = {float(result):.3f}")
''')
    d.p(("Независимый пересчёт и значения по парам (1 оправдался, 0 нет):",
         "An independent recalculation and per-pair values (1 verified, 0 not):"))
    d.code('''
threshold = 0.674 * q_obs.std(ddof=1)
by_hand = np.mean(np.abs(q_obs - q_sim) < threshold)
flags = hm.forecast_verification(q_obs, q_sim, reduction="none").value
print(round(float(by_hand), 3), flags[:8], round(float(threshold), 1))
''')
    d.p(("Порог постоянен для всего ряда, поэтому на межени прогнозы оправдываются легче, чем в половодье. Доля по сезонам:",
         "The threshold is the same for the whole series, so forecasts are verified more easily in low flow than in the flood. Fraction by season:"))
    d.code('''
in_flood = q_obs > 100
print(round(float(flags[in_flood].mean()), 3), round(float(flags[~in_flood].mean()), 3))
''')
    d.p(("Прогнозы на 1–10 суток: доля оправдавшихся по заблаговременности.",
         "Forecasts for 1 to 10 days: the verified fraction by lead time."))
    d.code(*FORECAST_SETUP, show_output=False)
    d.code('''
fc_flags = hm.forecast_verification(obs_fc, sim_fc, reduction="none").value
print(np.round(fc_flags.reshape(-1, 10).mean(axis=0), 2))
''')
    d.p(("Вдоль оси σ считается по каждому створу, а результат остаётся массивом флагов; доля по створам берётся вручную:",
         "Along an axis σ is computed per gauge and the result stays an array of flags; the fraction per gauge is taken by hand:"))
    d.code(*STATIONS, show_output=False)
    d.code('''
flags_st = hm.forecast_verification(q_obs_st, q_sim_st, axis=0).value
print(flags_st.shape, np.round(flags_st.mean(axis=0), 3))
''')


def fv_hydro(ns):
    thr = float(ns["threshold"])
    hi, lo = float(ns["flags"][ns["in_flood"]].mean()), float(ns["flags"][~ns["in_flood"]].mean())
    return [
        (f"Порог привязан к σ всего ряда, а σ определяется половодьем. В примере допуск равен {fmt(thr)} м³/с; доля оправдавшихся прогнозов {fmt(hi)} при расходе выше 100 м³/с и {fmt(lo)} при меньшем. Оправдываемость по всему ряду смешивает два режима с разной долей попаданий.",
         f"The threshold is tied to σ of the whole series, and σ is set by the flood. In the example the tolerance is {fmt(thr)} m³/s; the verified fraction is {fmt(hi)} at discharge above 100 m³/s and {fmt(lo)} below it. The verified share over the whole series mixes two regimes with different hit rates."),
        ("Метрика бинарна и не показывает, насколько прогноз не попал. Дополняйте её :ref:`metric-rmse` и :ref:`metric-pbias`.",
         "The metric is binary and does not show by how much a forecast missed. Complement it with :ref:`metric-rmse` and :ref:`metric-pbias`."),
    ]


FV = dict(
    name="forecast_verification",
    title=("Оправдываемость прогноза по допустимой погрешности 0,674σ", "Forecast verification against the permissible error 0.674σ"),
    short=[("Прогноз считается оправдавшимся, если абсолютная ошибка меньше 0,674 стандартного отклонения всех наблюдений :footcite:p:`georgievsky2007`. Для каждой пары получается 1, 0 или NaN, а итог это доля оправдавшихся прогнозов.",
            "A forecast is considered verified if its absolute error is below 0.674 times the standard deviation of all observations :footcite:p:`georgievsky2007`. Each pair yields 1, 0 or NaN, and the result is the fraction of verified forecasts.")],
    formula=[r"V_i = \mathbb{1}\left(\left|O_i - S_i\right| < c\,\sigma_O\right), \qquad c = 0.674, \qquad \sigma_O = \sqrt{\frac{1}{n-1}\sum_{j=1}^{n}\left(O_j-\bar{O}\right)^2}",
             r"\text{result} = \frac{1}{n}\sum_{i=1}^{n} V_i"],
    symbols=[(r":math:`\mathbb{1}` индикатор, :math:`\sigma_O` стандартное отклонение (``ddof=1``) наблюдений вдоль ``axis`` (по всем элементам при ``axis=None``). Коэффициент 0,674 хранится в константе ``PROBABLE_ERROR_COEFFICIENT`` модуля ``hydrometrics.backends.numpy``; это вероятное отклонение нормального закона, 0,6745σ, округлённое до трёх знаков. Среднее берётся по парам, для которых :math:`V_i` определено. " + GEORG_NOT_READ[0],
              r":math:`\mathbb{1}` is the indicator, :math:`\sigma_O` the standard deviation (``ddof=1``) of the observations along ``axis`` (over all elements with ``axis=None``). The coefficient 0.674 is stored in the constant ``PROBABLE_ERROR_COEFFICIENT`` of the module ``hydrometrics.backends.numpy``; it is the probable deviation of the normal law, 0.6745σ, rounded to three decimals. The mean is taken over the pairs for which :math:`V_i` is defined. " + GEORG_NOT_READ[1])],
    deviation=[("Неравенство строгое. Порог одинаков для всего ряда и не зависит ни от сезона, ни от заблаговременности. Это отличается от :ref:`metric-forecast_verification_delta`, где порог берётся по ошибкам внутри группы. Формула подтверждена автором библиотеки.",
                "The inequality is strict. The threshold is the same for the whole series and does not depend on season or lead time. This differs from :ref:`metric-forecast_verification_delta`, where the threshold comes from the errors within a group. The formula was confirmed by the library author.")],
    range="[0, 1]", optimum="1", dir="up",
    bounds=[("Результат лежит в [0, 1]. По парам функция возвращает 1.0, 0.0 или NaN; NaN означает, что ошибка или порог не определены. При постоянных наблюдениях порог равен нулю, строгое неравенство не выполняется ни для одной пары, и результат равен 0, а не NaN.",
             "The result lies in [0, 1]. Per pair the function returns 1.0, 0.0 or NaN; NaN means that the error or the threshold is undefined. For constant observations the threshold is zero, the strict inequality holds for no pair, and the result is 0, not NaN.")],
    interp=[("Это доля попаданий в допуск, а не мера ошибки: 0,5 означает, что половина прогнозов уложилась в 0,674σ. Для нормального распределения ошибок с нулевым средним и стандартным отклонением, равным σ, ожидаемая доля около 0,5; это свойство нормального закона, а не порог качества.",
             "This is the share of hits within a tolerance, not a measure of error: 0.5 means that half of the forecasts fell within 0.674σ. For normally distributed errors with zero mean and a standard deviation equal to σ the expected share is about 0.5; this is a property of the normal law, not a quality threshold."),
            ("Градации качества не приводятся: источник :footcite:p:`georgievsky2007` недоступен для чтения, пороги других источников подтвердить не удалось (см. :doc:`/user_guide/known_limits`).",
             "No rating scale is given: the source :footcite:p:`georgievsky2007` is unavailable for reading and thresholds from other sources could not be confirmed (see :doc:`/user_guide/known_limits`).")],
    red_doc=("По умолчанию без оси возвращается доля оправдавшихся прогнозов, а при заданной оси массив флагов формы входа; ``\"mean\"`` усредняет флаги.",
             "By default without an axis the fraction of verified forecasts is returned, and with an axis an array of flags of the input shape; ``\"mean\"`` averages the flags."),
    axis_doc=("Ось, вдоль которой считается σ. Результат сохраняет форму входа (флаги по парам).", "The axis along which σ is computed. The result keeps the input shape (flags per pair)."),
    special=[("Пара с пропуском в ``obs`` или ``sim`` при ``omit`` исключается, и σ считается по остальным наблюдениям; ``propagate`` даёт NaN; ``raise`` вызывает ``ValueError``. Значение ``inf`` в ``obs`` делает σ бесконечной, порог бесконечным, и все остальные прогнозы считаются оправдавшимися. Один элемент даёт NaN (σ не определена).",
              "Under ``omit`` a pair with a gap in ``obs`` or ``sim`` is dropped and σ is computed from the remaining observations; ``propagate`` gives NaN; ``raise`` raises ``ValueError``. An ``inf`` in ``obs`` makes σ and the threshold infinite and all other forecasts count as verified. A single element gives NaN (σ is undefined).")],
    examples=fv_examples,
    hydro=fv_hydro,
    related=["forecast_verification_delta", "ssigma", "ssigma_delta", "accuracy"],
    refs=True,
)

# ================================================================== forecast_verification_delta
def fvd_examples(d):
    d.p(("Прогнозы на 1–10 суток, выпускаемые каждые 10 суток. Порог для каждого выпуска равен :math:`0.674` от стандартного отклонения ошибок внутри этого выпуска.",
         "Forecasts for 1 to 10 days issued every 10 days. The threshold for each issue is :math:`0.674` times the standard deviation of the errors within that issue."))
    d.code(*SETUP, show_output=False)
    d.code(*FORECAST_SETUP, show_output=False)
    d.code('''
result = hm.forecast_verification_delta(obs_fc, sim_fc, ref_date=issue_date)
print(f"fraction verified = {float(result):.3f}")
''')
    d.p(("Пересчёт для первой группы и доля оправдавшихся по заблаговременности:",
         "Recalculation for the first group and the verified fraction by lead time:"))
    d.code('''
flags = hm.forecast_verification_delta(obs_fc, sim_fc, ref_date=issue_date, reduction="none").value
err = sim_fc[:10] - obs_fc[:10]
by_hand = np.abs(err) < 0.674 * err.std(ddof=1)
print(by_hand.astype(float), flags[:10])
print(np.round(flags.reshape(-1, 10).mean(axis=0), 2))
''')
    d.p(("Если ошибки группы почти постоянны (смещение без разброса), порог близок к нулю и прогнозы не оправдываются, хотя ошибка мала. Это свойство определения, а не сбой:",
         "If the errors of a group are almost constant (a bias without spread) the threshold is near zero and forecasts are not verified although the error is small. This is a property of the definition, not a failure:"))
    d.code('''
steady = hm.forecast_verification_delta(obs_fc[:10], obs_fc[:10] + 0.5, ref_date=issue_date[:10], reduction="none")
print(steady.value)
''')
    d.p(("На pandas метки группы передаются тем же аргументом:", "On pandas the group label is passed in the same argument:"))
    d.code('''
import pandas as pd

print(round(float(hm.forecast_verification_delta(pd.Series(obs_fc), pd.Series(sim_fc), ref_date=issue_date)), 3))
''')


FVD = dict(
    name="forecast_verification_delta",
    title=("Оправдываемость прогноза по допустимой погрешности 0,674σ_Δ внутри группы", "Forecast verification against the permissible error 0.674σ_Δ within a group"),
    short=[("Прогноз считается оправдавшимся, если абсолютная ошибка меньше 0,674 стандартного отклонения ошибок прогнозов внутри группы ``ref_date`` :footcite:p:`georgievsky2007`. Результат это доля оправдавшихся прогнозов.",
            "A forecast is considered verified if its absolute error is below 0.674 times the standard deviation of the forecast errors within the ``ref_date`` group :footcite:p:`georgievsky2007`. The result is the fraction of verified forecasts.")],
    sig="ref_date, ",
    formula=[r"V_i = \mathbb{1}\left(\left|O_i - S_i\right| < c\,\sigma_{\Delta,d(i)}\right), \qquad c = 0.674",
             r"\sigma_{\Delta,d} = \sqrt{\frac{1}{n_d-1}\sum_{j\in G_d}\left(\Delta_j-\bar{\Delta}_d\right)^2}, \qquad \Delta_j = S_j - O_j"],
    symbols=[(r":math:`G_d` группа с меткой :math:`d`, :math:`d(i)` метка группы пары :math:`i`, :math:`\Delta_j` ошибка прогноза, :math:`\bar{\Delta}_d` её среднее в группе, :math:`n_d` число действительных ошибок. Результат функции это среднее :math:`V_i` по парам, для которых оно определено. Группа с менее чем двумя действительными ошибками даёт NaN. " + GEORG_NOT_READ[0],
              r":math:`G_d` is the group with label :math:`d`, :math:`d(i)` the group label of pair :math:`i`, :math:`\Delta_j` the forecast error, :math:`\bar{\Delta}_d` its mean in the group, :math:`n_d` the number of valid errors. The function result is the mean of :math:`V_i` over the pairs for which it is defined. A group with fewer than two valid errors gives NaN. " + GEORG_NOT_READ[1])],
    deviation=[("Здесь :math:`\\sigma_\\Delta` это разброс ошибок прогноза внутри группы, то есть он зависит от того, насколько ошибки группы похожи друг на друга, а не от изменчивости самой величины. Из этого следует, что постоянное смещение не оправдывает прогноз: при одинаковых ошибках разброс равен нулю (см. пример). Формула подтверждена автором библиотеки и не менялась.",
                "Here :math:`\\sigma_\\Delta` is the spread of the forecast errors within a group, so it depends on how similar the errors of the group are to each other, not on the variability of the quantity itself. It follows that a constant bias does not verify a forecast: with identical errors the spread is zero (see the example). The formula was confirmed by the library author and is unchanged.")],
    range="[0, 1]", optimum="1", dir="up",
    bounds=[("Результат лежит в [0, 1]. По парам возвращаются 1.0, 0.0 или NaN; NaN означает, что ошибка пропущена или в группе меньше двух действительных ошибок.",
             "The result lies in [0, 1]. Per pair 1.0, 0.0 or NaN is returned; NaN means that the error is missing or the group has fewer than two valid errors.")],
    interp=[("Это доля попаданий в допуск, зависящий от группы. Значение 0,5 не имеет универсальной трактовки: допуск каждой группы определяется разбросом её собственных ошибок, поэтому группа с хорошим, но однородным прогнозом может иметь низкую долю. Градации качества не приводятся: источник :footcite:p:`georgievsky2007` недоступен для чтения (см. :doc:`/user_guide/known_limits`).",
             "This is the share of hits within a tolerance that depends on the group. The value 0.5 has no universal reading: the tolerance of each group is set by the spread of its own errors, so a group with a good but uniform forecast can have a low share. No rating scale is given: the source :footcite:p:`georgievsky2007` is unavailable for reading (see :doc:`/user_guide/known_limits`).")],
    params_req=[("``ref_date``", ("массив", "array"), ("обязателен", "required"),
                 ("Метки групп (например дата выпуска) той же формы, что ``obs``. Другая форма вызывает ``ValueError``.",
                  "Group labels (for example the issue date) of the same shape as ``obs``. A different shape raises ``ValueError``."))],
    special=[("При ``omit`` пары с пропуском исключаются из своей группы, ``propagate`` возвращает NaN (в результате по парам NaN стоит на месте пропуска); ``raise`` вызывает ``ValueError``. Группа из одной пары даёт NaN. Ось и веса не поддерживаются.",
              "Under ``omit`` pairs with a gap are excluded from their group; ``propagate`` returns NaN (the per-pair result has NaN at the position of the gap); ``raise`` raises ``ValueError``. A group with a single pair gives NaN. Axis and weights are not supported.")],
    examples=fvd_examples,
    hydro=[("Метрика оценивает однородность ошибок в группе, а не их величину: группа с большим, но стабильным смещением не оправдывается, а группа с малым, но неустойчивым разбросом оправдывается частично. Для оценки смещения используйте :ref:`metric-pbias` или :ref:`metric-bias`.",
            "The metric assesses the uniformity of errors in a group, not their magnitude: a group with a large but stable bias is not verified, while a group with a small but unstable spread is partly verified. To assess bias use :ref:`metric-pbias` or :ref:`metric-bias`."),
           ("При малых группах (до 5–10 значений) оценка :math:`\\sigma_\\Delta` ненадёжна, и доля оправдавшихся прогнозов сильно колеблется между выпусками.",
            "With small groups (up to 5 to 10 values) the estimate of :math:`\\sigma_\\Delta` is unreliable and the verified fraction fluctuates strongly between issues.")],
    related=["forecast_verification", "ssigma_delta", "ssigma", "bias"],
    refs=True,
)

FAMILY1 = {"regNSE": REGNSE, "nse_variance_weighted": NVW, "ssigma": SSIGMA, "ssigma_delta": SSD,
           "forecast_verification": FV, "forecast_verification_delta": FVD}
