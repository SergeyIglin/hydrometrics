"""Metric pages, family 3: NSE variants, volume and ratio metrics, KGE 2009 and the KGE components.

log_nse, modified_nse, nse_bounded, rsr, ve, kge_2009, kge_components,
r_component, alpha_component, beta_component, gamma_component.
"""
import numpy as np

from exkit import basic, setup, stations, xr_dim, years
from lib import fmt
from metricpage import STATIONS
from specs_regr import NAN_STD, ONE_ELEMENT

CONST_NAN = ("Постоянный ряд даёт NaN, потому что стандартное отклонение или дисперсия равны нулю.",
             "A constant series gives NaN because the standard deviation or the variance is zero.")


def flow(name, check=None, kw="", extra=None, xr=True, with_stations=True):
    def run(d):
        setup(d)
        basic(d, name, kw)
        if check:
            d.p(check[0])
            d.code(*check[1:])
        if extra:
            extra(d)
        if with_stations:
            stations(d, name, kw)
        years(d, name, kw)
        if xr:
            xr_dim(d, name)
    return run


# =================================================================================== log_nse
def log_nse_extra(d):
    d.p(("Одно нулевое значение расхода в наблюдениях при ``eps=1e-10`` превращается в :math:`\\ln 10^{-10}\\approx-23`, и результат резко падает. Аргумент ``eps`` задаёт добавку явно; ниже она равна 1 % от среднего расхода:",
         "A single zero discharge value in the observations becomes :math:`\\ln 10^{-10}\\approx-23` at ``eps=1e-10`` and the result drops sharply. The argument ``eps`` sets the offset explicitly; below it is 1 % of the mean discharge:"))
    d.code('''
q_dry = q_obs.copy()
q_dry[10] = 0.0  # одни сутки пересыхания
default_eps = float(hm.log_nse(q_dry, q_sim))
scaled_eps = float(hm.log_nse(q_dry, q_sim, eps=0.01 * q_obs.mean()))
print(round(float(hm.log_nse(q_obs, q_sim)), 3), round(default_eps, 3), round(scaled_eps, 3))
''', '''
q_dry = q_obs.copy()
q_dry[10] = 0.0  # one day of drying up
default_eps = float(hm.log_nse(q_dry, q_sim))
scaled_eps = float(hm.log_nse(q_dry, q_sim, eps=0.01 * q_obs.mean()))
print(round(float(hm.log_nse(q_obs, q_sim)), 3), round(default_eps, 3), round(scaled_eps, 3))
''')


def log_nse_hydro(ns):
    return [
        (f"Логарифм сжимает пики и растягивает межень, поэтому ``log_nse`` оценивает ту часть гидрографа, которую :ref:`metric-nse` почти не видит. В примере ``NSE = {fmt(float(ns['result']))}``, а ``log_nse = {fmt(float(ns['log_result']))}`` на тех же данных: модель хуже воспроизводит межень, чем пик.",
         f"The logarithm compresses peaks and stretches low flow, so ``log_nse`` assesses the part of the hydrograph that :ref:`metric-nse` hardly sees. In the example ``NSE = {fmt(float(ns['result']))}`` while ``log_nse = {fmt(float(ns['log_result']))}`` on the same data: the model reproduces low flow worse than the peak."),
        (f"Результат зависит от добавки ``eps``, особенно при нулевых расходах. В примере одни нулевые сутки опускают ``log_nse`` с {fmt(float(ns['log_result']))} до {fmt(ns['default_eps'])}, а добавка в 1 % среднего даёт {fmt(ns['scaled_eps'])}. Выбор добавки нужно указывать при публикации результатов. Krause et al. рассматривают логарифмическую форму для оценки низких расходов :footcite:p:`krause2005`.",
         f"The result depends on the offset ``eps``, especially with zero discharge. In the example a single zero day lowers ``log_nse`` from {fmt(float(ns['log_result']))} to {fmt(ns['default_eps'])}, while an offset of 1 % of the mean gives {fmt(ns['scaled_eps'])}. The choice of the offset should be reported with the results. Krause et al. consider the logarithmic form for assessing low flows :footcite:p:`krause2005`."),
    ]


def log_nse_examples(d):
    setup(d)
    d.code('''
result = hm.nse(q_obs, q_sim)
log_result = hm.log_nse(q_obs, q_sim)
print(f"NSE = {float(result):.3f}, log NSE = {float(log_result):.3f}")
''')
    log_nse_extra(d)
    stations(d, "log_nse")
    years(d, "log_nse")
    xr_dim(d, "log_nse")


LOG_NSE = dict(
    name="log_nse",
    title=("Критерий Нэша–Сатклиффа для логарифмов расходов (logNSE)", "Nash–Sutcliffe efficiency of log-transformed discharge (logNSE)"),
    short=[("logNSE это :ref:`metric-nse`, вычисленная для натуральных логарифмов расходов. Логарифм увеличивает вклад малых значений, поэтому метрика отражает качество воспроизведения межени.",
            "logNSE is :ref:`metric-nse` computed on the natural logarithms of discharge. The logarithm increases the contribution of small values, so the metric reflects how well low flow is reproduced.")],
    sig_opt=", eps=1e-10",
    formula=[r"\mathrm{logNSE} = 1 - \frac{\sum_{i} w_i\,\left(\ln(O_i+\varepsilon) - \ln(S_i+\varepsilon)\right)^2}{\sum_{i} w_i\,\left(\ln(O_i+\varepsilon) - \overline{\ln(O+\varepsilon)}\right)^2}"],
    symbols=[(r":math:`\varepsilon` добавка ``eps`` (по умолчанию :math:`10^{-10}`), :math:`w_i` вес, черта обозначает (взвешенное) среднее логарифмов наблюдений. Пара, для которой :math:`O_i+\varepsilon\le 0` или :math:`S_i+\varepsilon\le 0`, не имеет логарифма и исключается из обеих сумм.",
              r":math:`\varepsilon` is the offset ``eps`` (default :math:`10^{-10}`), :math:`w_i` the weight, the bar denotes the (weighted) mean of the logarithms of the observations. A pair for which :math:`O_i+\varepsilon\le 0` or :math:`S_i+\varepsilon\le 0` has no logarithm and drops out of both sums.")],
    deviation=[("В коде источником указана Krause et al. :footcite:p:`krause2005`, где логарифмическая форма рассмотрена в разделе о NSE для логарифмированных значений. Добавка :math:`\\varepsilon` фиксированная и абсолютная, а не доля от среднего расхода; в практике калибровки встречаются и относительные добавки.",
                "The code names Krause et al. :footcite:p:`krause2005` as the source, where the logarithmic form is considered in the section on NSE of logarithmic values. The offset :math:`\\varepsilon` is fixed and absolute, not a fraction of the mean discharge; relative offsets also occur in calibration practice.")],
    range="(-∞, 1]", optimum="1", dir="up",
    bounds=[("Верхняя граница достигается при совпадении рядов, снизу значение не ограничено. Значение 0 соответствует прогнозу средним логарифма наблюдений, то есть геометрическим средним. При постоянных наблюдениях результат NaN.",
             "The upper bound is reached when the series coincide, there is no lower bound. The value 0 corresponds to a forecast by the mean of the logarithm of the observations, that is the geometric mean. For constant observations the result is NaN.")],
    interp=[("Общепринятых градаций для logNSE нет. Градации Moriasi et al. :footcite:p:`moriasi2007` относятся к NSE на нелогарифмированных данных (месячный шаг) и на logNSE не переносятся.",
             "There are no accepted ratings for logNSE. The ratings of Moriasi et al. :footcite:p:`moriasi2007` refer to NSE on untransformed data (monthly time step) and do not carry over to logNSE.")],
    params_opt=[("``eps``", "float", "``1e-10``", ("Добавка перед логарифмом. Исключает логарифм нуля; влияет на результат при нулевых и очень малых расходах.", "Offset before the logarithm. It avoids the logarithm of zero; it affects the result at zero and very small discharge."))],
    special=[NAN_STD, ("Отрицательные значения не имеют логарифма: пара исключается из расчёта, а если пар не остаётся, результат NaN. Ряд из нулей даёт NaN.",
                       "Negative values have no logarithm: the pair is excluded and if no pair remains the result is NaN. An all-zero series gives NaN.")],
    examples=log_nse_examples,
    hydro=log_nse_hydro,
    related=["nse", "modified_nse", "ve", "kge_2012"],
    refs=True,
)

# ================================================================================ modified_nse
def mnse_extra(d):
    d.p(("Единичный выброс в модельном ряду: сравните снижение каждой метрики относительно значения без выброса.",
         "A single outlier in the simulated series: compare the drop of each metric relative to its value without the outlier."))
    d.code('''
q_spike = q_sim.copy()
q_spike[500] += 400.0  # единичный сбой модели
for label, metric in (("NSE", hm.nse), ("mNSE", hm.modified_nse)):
    print(label, round(float(metric(q_obs, q_sim)), 3), "->", round(float(metric(q_obs, q_spike)), 3))
''', '''
q_spike = q_sim.copy()
q_spike[500] += 400.0  # a single model failure
for label, metric in (("NSE", hm.nse), ("mNSE", hm.modified_nse)):
    print(label, round(float(metric(q_obs, q_sim)), 3), "->", round(float(metric(q_obs, q_spike)), 3))
''')


MNSE = dict(
    name="modified_nse",
    title=("Модифицированный критерий Нэша–Сатклиффа (mNSE)", "Modified Nash–Sutcliffe efficiency (mNSE)"),
    short=[("mNSE заменяет квадраты разностей в :ref:`metric-nse` их модулями. Ошибки входят линейно, поэтому метрика менее чувствительна к отдельным крупным промахам и пикам.",
            "mNSE replaces the squared differences of :ref:`metric-nse` with their absolute values. Errors enter linearly, so the metric is less sensitive to single large misses and peaks.")],
    sig_opt=", norm=None",
    formula=[r"\mathrm{mNSE} = 1 - \frac{\sum_{i} w_i\,\left|O_i - S_i\right|}{\sum_{i} w_i\,\left|O_i - \bar{O}\right|}"],
    symbols=[(r":math:`\bar{O}` среднее наблюдений (взвешенное при заданных весах) либо значение ``norm``, :math:`w_i` вес. Суммирование идёт по оси ``axis``. В коде источником указана Krause et al. :footcite:p:`krause2005`; формула взята из реализации.",
              r":math:`\bar{O}` is the mean of the observations (weighted when weights are given) or the value ``norm``, :math:`w_i` the weight. The sum runs along ``axis``. The code names Krause et al. :footcite:p:`krause2005` as the source; the formula is taken from the implementation.")],
    deviation=[("Это вариант с первой степенью модуля. В литературе встречаются и другие модифицированные формы NSE (с иными степенями и с иной опорой); сравнивать значения нужно только для одной и той же формы. Заданный ``norm`` заменяет :math:`\\bar{O}` в знаменателе.",
                "This is the variant with the first power of the absolute value. Other modified forms of NSE (with other powers and other benchmarks) occur in the literature; values should be compared only within one form. A given ``norm`` replaces :math:`\\bar{O}` in the denominator.")],
    range="(-∞, 1]", optimum="1", dir="up",
    bounds=[("Верхняя граница достигается при совпадении рядов, снизу значение не ограничено. Значение 0 означает, что сумма модулей ошибок равна сумме модулей отклонений наблюдений от среднего, как у постоянного прогноза средним. При постоянных наблюдениях результат NaN.",
             "The upper bound is reached when the series coincide, there is no lower bound. The value 0 means that the sum of absolute errors equals the sum of absolute deviations of the observations from the mean, as for a constant forecast at the mean. For constant observations the result is NaN.")],
    interp=[("Общепринятых градаций для mNSE нет. Градации Moriasi et al. :footcite:p:`moriasi2007` построены для NSE с квадратами и на mNSE не переносятся, поскольку шкала значений другая.",
             "There are no accepted ratings for mNSE. The ratings of Moriasi et al. :footcite:p:`moriasi2007` were built for NSE with squares and do not carry over to mNSE because the value scale differs.")],
    params_opt=[("``norm``", ("число или массив", "float or array"), "``None``", ("Опорное значение вместо среднего наблюдений.", "Reference value instead of the observed mean."))],
    special=[NAN_STD, CONST_NAN],
    examples=flow("modified_nse", extra=mnse_extra),
    hydro=[("Линейная ошибка меньше подчёркивает пики половодья, чем квадратичная, и даёт более сбалансированную оценку по сезонам; но по-прежнему слабо отражает межень, для которой лучше :ref:`metric-log_nse`.",
            "A linear error emphasises flood peaks less than a quadratic one and gives a more balanced assessment over the seasons; it still reflects low flow poorly, for which :ref:`metric-log_nse` is better.")],
    related=["nse", "mae", "log_nse", "ve"],
    refs=True,
)

# ================================================================================ nse_bounded
def nse_bounded_extra(d):
    d.p(("Метрика монотонно зависит от NSE, поэтому ранжирует модели так же; она лишь сжимает шкалу в :math:`(-1, 1]`.",
         "The metric depends monotonically on NSE, so it ranks models the same way; it only compresses the scale into :math:`(-1, 1]`."))
    d.code('''
nse_value = float(hm.nse(q_obs, q_sim))
print(round(float(hm.nse_bounded(q_obs, q_sim)), 4), round(nse_value / (2 - nse_value), 4))
''')


NSE_BOUNDED = dict(
    name="nse_bounded",
    title=("Ограниченный критерий Нэша–Сатклиффа (nse_bounded)", "Bounded Nash–Sutcliffe efficiency (nse_bounded)"),
    short=[("``nse_bounded`` это преобразование :ref:`metric-nse`, которое переводит неограниченную снизу шкалу в интервал :math:`(-1, 1]`. Значение 0 остаётся ориентиром модели, равной постоянному прогнозу средним.",
            "``nse_bounded`` is a transformation of :ref:`metric-nse` that maps a scale unbounded below into the interval :math:`(-1, 1]`. The value 0 stays the reference of a model equal to a constant forecast at the mean.")],
    formula=[r"\mathrm{NSE}_b = \frac{\mathrm{NSE}}{2 - \mathrm{NSE}}"],
    symbols=[(r":math:`\mathrm{NSE}` значение :ref:`metric-nse` (без ``norm``) для тех же данных и тех же весов.",
              r":math:`\mathrm{NSE}` is the value of :ref:`metric-nse` (without ``norm``) for the same data and weights.")],
    deviation=[("Подтверждённого первоисточника именно этой формы найти не удалось (см. :doc:`/user_guide/known_limits`). В литературе встречается и другая форма, :math:`1/(2-\\mathrm{NSE})` с значениями в :math:`(0, 1]`, равная 0,5 при ``NSE = 0``; её источник также не подтверждён. Здесь реализована форма :math:`\\mathrm{NSE}/(2-\\mathrm{NSE})`, и при сравнении с опубликованными значениями нужно проверять, какая форма использована.",
                "No confirmed primary source for this exact form could be found (see :doc:`/user_guide/known_limits`). The literature also has another form, :math:`1/(2-\\mathrm{NSE})` with values in :math:`(0, 1]`, equal to 0.5 at ``NSE = 0``; its source is also unconfirmed. The form implemented here is :math:`\\mathrm{NSE}/(2-\\mathrm{NSE})`, and when comparing with published values one has to check which form was used.")],
    range="(-1, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 достигается при ``NSE = 1``. При ``NSE`` → −∞ значение стремится к −1, но не достигает его. Если NSE не определена (постоянные наблюдения), результат NaN.",
             "The value 1 is reached at ``NSE = 1``. As ``NSE`` → −∞ the value tends to −1 but does not reach it. If NSE is undefined (constant observations) the result is NaN.")],
    interp=[("Градации для ``nse_bounded`` подтвердить не удалось. Пересчёт градаций Moriasi et al. :footcite:p:`moriasi2007` из NSE в ``nse_bounded`` возможен через формулу, но это расчёт читателя, а не опубликованная шкала.",
             "Ratings for ``nse_bounded`` could not be confirmed. The ratings of Moriasi et al. :footcite:p:`moriasi2007` can be converted from NSE to ``nse_bounded`` with the formula, but that is a calculation by the reader, not a published scale.")],
    special=[NAN_STD, CONST_NAN],
    examples=flow("nse_bounded", extra=nse_bounded_extra),
    hydro=[("Сжатие шкалы делает ``nse_bounded`` удобной для усреднения по большому числу створов: один створ с очень плохой моделью не тянет среднее в минус бесконечность. Цена за это в том, что различия между плохими моделями почти исчезают: при ``NSE`` от −10 до −100 значение ``nse_bounded`` лежит между −0,83 и −0,98.",
            "The compressed scale makes ``nse_bounded`` convenient for averaging over many gauges: a single gauge with a very poor model does not pull the mean to minus infinity. The price is that differences between poor models almost vanish: for ``NSE`` from −10 to −100 the ``nse_bounded`` value lies between −0.83 and −0.98.")],
    related=["nse", "kge_2012", "log_nse"],
    related_note=[("В литературе именем nNSE обозначают форму :math:`1/(2-\\mathrm{NSE})` со значениями в :math:`(0, 1]`; ``nse_bounded`` считает другую величину, :math:`\\mathrm{NSE}/(2-\\mathrm{NSE})`, и сравнивать их значения нельзя.",
                   "In the literature the name nNSE denotes the form :math:`1/(2-\\mathrm{NSE})` with values in :math:`(0, 1]`; ``nse_bounded`` computes a different quantity, :math:`\\mathrm{NSE}/(2-\\mathrm{NSE})`, and their values cannot be compared.")],
    refs=True,
)

# ======================================================================================== rsr
def rsr_extra(d):
    d.p(("Связь с NSE следует из определений: :math:`\\mathrm{RSR}^2 = (1-\\mathrm{NSE})\\,(n-1)/n`. Формула Moriasi et al. без поправки ``ddof`` даёт чуть большее значение:",
         "The link to NSE follows from the definitions: :math:`\\mathrm{RSR}^2 = (1-\\mathrm{NSE})\\,(n-1)/n`. The formula of Moriasi et al. without the ``ddof`` correction gives a slightly larger value:"))
    d.code('''
n = q_obs.size
nse_value = float(hm.nse(q_obs, q_sim))
print(round(float(hm.rsr(q_obs, q_sim)), 5), round(float(np.sqrt((1 - nse_value) * (n - 1) / n)), 5))
moriasi = np.sqrt(np.sum((q_obs - q_sim) ** 2)) / np.sqrt(np.sum((q_obs - q_obs.mean()) ** 2))
print(round(float(moriasi), 5))
''')


RSR = dict(
    name="rsr",
    title=("Отношение RMSE к стандартному отклонению наблюдений (RSR)", "Ratio of RMSE to the standard deviation of the observations (RSR)"),
    short=[("RSR это :ref:`metric-rmse`, делённая на стандартное отклонение наблюдений :footcite:p:`moriasi2007`. Метрика безразмерна и сочетает показатель ошибки с нормировкой на изменчивость наблюдений.",
            "RSR is :ref:`metric-rmse` divided by the standard deviation of the observations :footcite:p:`moriasi2007`. The metric is dimensionless and combines an error index with normalisation by the variability of the observations.")],
    formula=[r"\mathrm{RSR} = \frac{\mathrm{RMSE}}{\sigma_O} = \frac{\sqrt{\frac{1}{n}\sum_{i} w_i\,\left(O_i - S_i\right)^2}}{\sqrt{\frac{1}{n-1}\sum_{i} w_i\,\left(O_i - \bar{O}\right)^2}}"],
    symbols=[(r":math:`\sigma_O` стандартное отклонение наблюдений с ``ddof=1``, :math:`\bar{O}` среднее наблюдений, :math:`w_i` вес (в записи для случая без весов).",
              r":math:`\sigma_O` is the standard deviation of the observations with ``ddof=1``, :math:`\bar{O}` the mean of the observations, :math:`w_i` the weight (the notation is for the unweighted case).")],
    deviation=[("Moriasi et al. :footcite:p:`moriasi2007` записывают RSR как отношение корней сумм квадратов без делителей. Библиотека использует RMSE с делителем :math:`n` и стандартное отклонение с делителем :math:`n-1`, поэтому значение меньше формулы Moriasi et al. в :math:`\\sqrt{n/(n-1)}` раз; для длинных рядов разница пренебрежимо мала (пример ниже).",
                "Moriasi et al. :footcite:p:`moriasi2007` write RSR as the ratio of the roots of the sums of squares without divisors. The library uses the RMSE with divisor :math:`n` and the standard deviation with divisor :math:`n-1`, so the value is smaller than the Moriasi et al. formula by a factor of :math:`\\sqrt{n/(n-1)}`; for long series the difference is negligible (example below).")],
    range="[0, +∞)", optimum="0", dir="down",
    bounds=[("Значение 0 означает нулевую ошибку. Значение 1 соответствует ``NSE`` около 0 при большом :math:`n`. Верхней границы нет. При постоянных наблюдениях результат NaN.",
             "The value 0 means zero error. The value 1 corresponds to ``NSE`` near 0 for large :math:`n`. There is no upper bound. For constant observations the result is NaN.")],
    interp=[("Moriasi et al. :footcite:p:`moriasi2007` (таблица 4) оценивают RSR так: очень хорошо при :math:`0 \\le \\mathrm{RSR} \\le 0.50`, хорошо при 0,50–0,60, удовлетворительно при 0,60–0,70, неудовлетворительно выше 0,70. Эти значения даны для месячного шага и для непрерывного долгосрочного моделирования водосборов; авторы подчёркивают, что градации следует корректировать с учётом качества данных и временного шага.",
             "Moriasi et al. :footcite:p:`moriasi2007` (Table 4) rate RSR as follows: very good for :math:`0 \\le \\mathrm{RSR} \\le 0.50`, good for 0.50 to 0.60, satisfactory for 0.60 to 0.70, unsatisfactory above 0.70. These values were given for a monthly time step and for continuous long-term watershed simulation; the authors stress that the ratings should be adjusted for data quality and time step.")],
    special=[NAN_STD, CONST_NAN],
    examples=flow("rsr", extra=rsr_extra),
    hydro=[("RSR и NSE связаны взаимно однозначно, поэтому не дают независимой информации о качестве модели: это два способа записать одну и ту же сумму квадратов. Градации Moriasi et al. для NSE и RSR согласованы между собой.",
            "RSR and NSE are in one-to-one correspondence and so give no independent information on model quality: they are two ways of writing the same sum of squares. The Moriasi et al. ratings for NSE and RSR are consistent with each other."),
           ("Как и NSE, RSR определяется пиками и не видит смещения при малых расходах; дополняйте её :ref:`metric-pbias`.",
            "Like NSE, RSR is set by peaks and does not see bias at low flows; complement it with :ref:`metric-pbias`.")],
    related=["rmse", "nse", "nrmse", "pbias"],
    refs=True,
)

# ========================================================================================= ve
def ve_extra(d):
    d.p(("Модель, равная нулю, получает 0, а модель с завышением всех расходов в 2,5 раза отрицательное значение:",
         "A model equal to zero gets 0, and a model that overestimates all discharge by a factor of 2.5 gets a negative value:"))
    d.code('''
print(round(float(hm.ve(q_obs, np.zeros_like(q_obs))), 3), round(float(hm.ve(q_obs, 2.5 * q_obs)), 3))
''')


VE = dict(
    name="ve",
    title=("Объёмная эффективность (VE)", "Volumetric efficiency (VE)"),
    short=[("VE это единица минус суммарная абсолютная ошибка, отнесённая к суммарному объёму наблюдённого стока. Показывает долю объёма, воспроизведённую в нужное время.",
            "VE is one minus the total absolute error relative to the total observed runoff volume. It shows the share of the volume that is reproduced at the right time.")],
    formula=[r"\mathrm{VE} = 1 - \frac{\sum_{i} w_i\,\left|O_i - S_i\right|}{\sum_{i} w_i\,\left|O_i\right|}"],
    symbols=[(r":math:`O_i` наблюдённое, :math:`S_i` модельное значение, :math:`w_i` вес. Суммирование идёт по оси ``axis``. В коде источником указана Criss и Winston :footcite:p:`criss2008`; текст статьи прочитать не удалось, формула взята из реализации.",
              r":math:`O_i` is the observed and :math:`S_i` the simulated value, :math:`w_i` the weight. The sum runs along ``axis``. The code names Criss and Winston :footcite:p:`criss2008` as the source; the text of the paper could not be read and the formula is taken from the implementation.")],
    deviation=[("В знаменателе стоит сумма модулей наблюдений, поэтому для неотрицательных величин, например расхода, она равна объёму стока. Для величин, меняющих знак, смысл «доли объёма» теряется.",
                "The denominator is the sum of absolute values of the observations, so for non-negative variables such as discharge it equals the runoff volume. For variables that change sign the meaning of a share of volume is lost.")],
    range="(-∞, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 достигается при совпадении рядов, значение 0 соответствует модели, равной нулю, при неотрицательных наблюдениях. Отрицательное значение означает, что суммарная абсолютная ошибка больше суммарного стока. Если сумма наблюдений равна нулю, результат NaN.",
             "The value 1 is reached when the series coincide, the value 0 corresponds to a model equal to zero for non-negative observations. A negative value means that the total absolute error exceeds the total runoff. If the sum of the observations is zero the result is NaN.")],
    interp=[("Общепринятых градаций для VE в прочитанных источниках нет.", "There are no accepted ratings for VE in the sources that were read.")],
    special=[NAN_STD, ("Постоянный ряд наблюдений допустим: метрика не использует дисперсию. Ряд из нулей даёт NaN.", "A constant series of observations is allowed: the metric does not use the variance. An all-zero series gives NaN.")],
    examples=flow("ve", extra=ve_extra),
    hydro=[("В отличие от :ref:`metric-pbias`, где завышение и занижение объёма компенсируют друг друга, в VE ошибки разных знаков складываются по модулю, поэтому метрика учитывает ещё и распределение объёма во времени. При этом пики и межень входят линейно, без усиления пиков, как в :ref:`metric-nse`.",
            "Unlike :ref:`metric-pbias`, where overestimates and underestimates of volume cancel, VE adds errors of opposite signs in absolute value, so the metric also accounts for how volume is distributed in time. Peaks and low flow enter linearly, without the amplification of peaks seen in :ref:`metric-nse`.")],
    related=["pbias", "mae", "modified_nse", "bias"],
    refs=True,
)

# ================================================================================== kge_2009
def kge09_examples(d):
    setup(d)
    d.code('''
result = hm.kge_2009(q_obs, q_sim)
print(f"kge_2009 = {float(result):.4f}")
''')
    d.p(("Независимый пересчёт по трём компонентам:", "An independent recalculation from the three components:"))
    d.code('''
r = np.corrcoef(q_obs, q_sim)[0, 1]
alpha = q_sim.std(ddof=1) / q_obs.std(ddof=1)
beta = q_sim.mean() / q_obs.mean()
by_hand = 1 - np.sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)
print(f"{by_hand:.4f}")
''')
    d.p(("От :ref:`metric-kge_2012` версия 2009 г. отличается заменой :math:`\\gamma` на :math:`\\alpha`; на тех же данных:",
         "The 2009 version differs from :ref:`metric-kge_2012` by using :math:`\\alpha` instead of :math:`\\gamma`; on the same data:"))
    d.code('''
print(round(float(hm.kge_2009(q_obs, q_sim)), 4), round(float(hm.kge_2012(q_obs, q_sim)), 4))
''')
    stations(d, "kge_2009")
    years(d, "kge_2009")
    xr_dim(d, "kge_2009")


KGE09 = dict(
    name="kge_2009",
    title=("Критерий Клинга–Гупты, версия 2009 (KGE 2009)", "Kling–Gupta efficiency, 2009 version (KGE 2009)"),
    short=[("KGE 2009 г. измеряет евклидово расстояние от идеальной точки в пространстве корреляции :math:`r`, отношения стандартных отклонений :math:`\\alpha` и отношения средних :math:`\\beta` :footcite:p:`gupta2009`. Метрика получена разложением NSE на эти три компоненты.",
            "KGE 2009 measures the Euclidean distance from the ideal point in the space of the correlation :math:`r`, the ratio of standard deviations :math:`\\alpha` and the ratio of means :math:`\\beta` :footcite:p:`gupta2009`. The metric derives from the decomposition of NSE into these three components.")],
    formula=[r"\mathrm{KGE}_{2009} = 1 - \sqrt{(r-1)^2 + (\alpha-1)^2 + (\beta-1)^2}",
             r"\alpha = \frac{\sigma_S}{\sigma_O}, \qquad \beta = \frac{\mu_S}{\mu_O}"],
    symbols=[(r":math:`r` коэффициент корреляции Пирсона, :math:`\sigma` стандартное отклонение с ``ddof=1``, :math:`\mu` среднее, индексы :math:`O` и :math:`S` обозначают наблюдения и модель.",
              r":math:`r` is the Pearson correlation coefficient, :math:`\sigma` the standard deviation with ``ddof=1``, :math:`\mu` the mean, and the subscripts :math:`O` and :math:`S` denote observations and simulation.")],
    deviation=[("Совпадает с определением Gupta et al. :footcite:p:`gupta2009`. Версия 2012 г. :ref:`metric-kge_2012` заменяет :math:`\\alpha` отношением коэффициентов вариации :math:`\\gamma`; значения двух версий нельзя сравнивать между собой.",
                "It matches the definition of Gupta et al. :footcite:p:`gupta2009`. The 2012 version :ref:`metric-kge_2012` replaces :math:`\\alpha` with the ratio of coefficients of variation :math:`\\gamma`; values of the two versions cannot be compared with each other.")],
    range="(-∞, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 достигается при :math:`r=\\alpha=\\beta=1`. Снизу значение не ограничено. При среднем наблюдений, близком к нулю, :math:`\\beta` не определена или очень велика. Если ряд постоянен, корреляция не определена и результат NaN.",
             "The value 1 is reached at :math:`r=\\alpha=\\beta=1`. There is no lower bound. When the observed mean is close to zero :math:`\\beta` is undefined or very large. If a series is constant the correlation is undefined and the result is NaN.")],
    interp=[("Общепринятых порогов качества для KGE нет. Значение не имеет встроенного ориентира, подобного ``NSE = 0``: Knoben et al. :footcite:p:`knoben2019` показывают, что прогноз средним расходом даёт :math:`1-\\sqrt{2}\\approx-0.41`, а не 0, и требуют явно указывать опорную модель.",
             "There are no accepted quality thresholds for KGE. The value has no built-in reference similar to ``NSE = 0``: Knoben et al. :footcite:p:`knoben2019` show that a mean-flow forecast yields :math:`1-\\sqrt{2}\\approx-0.41`, not 0, and call for stating the benchmark explicitly.")],
    special=[NAN_STD, ("Постоянный ряд даёт NaN из-за корреляции. Один элемент даёт NaN.", "A constant series gives NaN because of the correlation. A single element gives NaN.")],
    backend_note=[("Функция возвращает :class:`~hydrometrics.MetricResult` со скаляром на всех бэкендах. Компоненты возвращает :func:`~hydrometrics.kge_components` с ``version=\"2009\"``.",
                   "The function returns a :class:`~hydrometrics.MetricResult` with a scalar on every backend. The components are returned by :func:`~hydrometrics.kge_components` with ``version=\"2009\"``.")],
    examples=kge09_examples,
    hydro=[("Gupta et al. :footcite:p:`gupta2009` показывают, что NSE складывается из тех же трёх компонент, и что при данной корреляции NSE достигает максимума при :math:`\\alpha = r`, то есть оптимальная по NSE модель занижает изменчивость стока. KGE штрафует отклонение :math:`\\alpha` от 1 прямо.",
            "Gupta et al. :footcite:p:`gupta2009` show that NSE is built from the same three components and that, for a given correlation, NSE reaches its maximum at :math:`\\alpha = r`, so a model optimal in terms of NSE underestimates flow variability. KGE penalises the deviation of :math:`\\alpha` from 1 directly."),
           ("Mizukami et al. :footcite:p:`mizukami2019` сообщают, что калибровка по KGE (форма 2009 г.) воспроизводит годовые максимумы стока лучше, чем калибровка по NSE.",
            "Mizukami et al. :footcite:p:`mizukami2019` report that calibration on KGE (the 2009 form) reproduces annual peak flows better than calibration on NSE.")],
    related=["kge_2012", "kge_components", "nse", "r_component", "alpha_component", "beta_component"],
    refs=True,
)

# ============================================================================== kge_components
def kge_components_examples(d):
    setup(d)
    d.code('''
parts = hm.kge_components(q_obs, q_sim).value
print({name: round(float(value), 3) for name, value in parts.items()})
''')
    d.p(("Версия 2009 г. возвращает три компоненты, без :math:`\\gamma`:", "The 2009 version returns three components, without :math:`\\gamma`:"))
    d.code('''
parts_2009 = hm.kge_components(q_obs, q_sim, version="2009").value
print(list(parts_2009))
''')
    d.p(("По створам с ``reduction=\"none\"`` каждое значение словаря это массив по створам:", "By gauge with ``reduction=\"none\"`` each dictionary value is an array over the gauges:"))
    d.code(*STATIONS, show_output=False)
    d.code('''
per_station = hm.kge_components(q_obs_st, q_sim_st, axis=0, reduction="none").value
print({name: np.round(value, 3) for name, value in per_station.items()})
''')
    d.p(("На xarray компоненты возвращаются как ``DataArray`` по оставшимся измерениям:", "On xarray the components are returned as ``DataArray`` over the remaining dimensions:"))
    d.code('''
import xarray as xr

coords = {"time": dates, "station": ["upper", "middle", "lower"]}
obs_da = xr.DataArray(q_obs_st, dims=["time", "station"], coords=coords)
sim_da = xr.DataArray(q_sim_st, dims=["time", "station"], coords=coords)
beta_da = hm.kge_components(obs_da, sim_da, dim="time").value["beta"]
print(beta_da.round(3).to_series().to_dict())
''')


KGE_COMP = dict(
    name="kge_components",
    title=("Компоненты KGE (r, α, β, γ)", "KGE components (r, α, β, γ)"),
    short=[("Функция возвращает словарь компонент, из которых строятся :ref:`metric-kge_2009` и :ref:`metric-kge_2012`: корреляцию :math:`r`, отношение стандартных отклонений :math:`\\alpha`, отношение средних :math:`\\beta` и отношение коэффициентов вариации :math:`\\gamma`.",
            "The function returns a dictionary of the components from which :ref:`metric-kge_2009` and :ref:`metric-kge_2012` are built: the correlation :math:`r`, the ratio of standard deviations :math:`\\alpha`, the ratio of means :math:`\\beta` and the ratio of coefficients of variation :math:`\\gamma`.")],
    sig_opt=", version=\"2012\"",
    formula=[r"r,\qquad \alpha = \frac{\sigma_S}{\sigma_O},\qquad \beta = \frac{\mu_S}{\mu_O},\qquad \gamma = \frac{\sigma_S/\mu_S}{\sigma_O/\mu_O}"],
    symbols=[(r"Обозначения как на странице :ref:`metric-kge_2009`. Ключ ``gamma`` присутствует только при ``version=\"2012\"``. Каждое значение словаря обрабатывается так же, как результат отдельной компоненты: :ref:`metric-r_component`, :ref:`metric-alpha_component`, :ref:`metric-beta_component`, :ref:`metric-gamma_component`.",
              r"Notation as on the page :ref:`metric-kge_2009`. The key ``gamma`` is present only with ``version=\"2012\"``. Each dictionary value is handled like the result of the separate component: :ref:`metric-r_component`, :ref:`metric-alpha_component`, :ref:`metric-beta_component`, :ref:`metric-gamma_component`.")],
    deviation=[("Версия влияет только на состав словаря: значения :math:`r`, :math:`\\alpha` и :math:`\\beta` от неё не зависят. Для ``version=\"2012\"`` ключ ``alpha`` возвращается для информации, он не входит в :ref:`metric-kge_2012`.",
                "The version affects only the content of the dictionary: the values of :math:`r`, :math:`\\alpha` and :math:`\\beta` do not depend on it. For ``version=\"2012\"`` the key ``alpha`` is returned for information, it is not a term of :ref:`metric-kge_2012`.")],
    range=("по компонентам", "per component"), optimum="1", dir="one",
    bounds=[("Оптимум каждой компоненты равен 1. Диапазоны: :math:`r` в [-1, 1], :math:`\\alpha` не меньше 0, :math:`\\beta` и :math:`\\gamma` определены при ненулевых средних наблюдений и модели. Недопустимое значение ``version`` вызывает ``ValueError``.",
             "The optimum of each component is 1. Ranges: :math:`r` in [-1, 1], :math:`\\alpha` not below 0, :math:`\\beta` and :math:`\\gamma` defined for non-zero means of observations and simulation. An invalid ``version`` raises ``ValueError``.")],
    interp=[("Компоненты интерпретируются относительно 1: :math:`\\beta > 1` означает завышение объёма, :math:`\\alpha < 1` занижение изменчивости (часто срезанные пики), :math:`r` показывает совпадение фазы и формы. Пороги качества не приняты.",
             "The components are read relative to 1: :math:`\\beta > 1` means overestimated volume, :math:`\\alpha < 1` underestimated variability (often clipped peaks), :math:`r` shows agreement of phase and shape. No quality thresholds are accepted.")],
    params_opt=[("``version``", "str", "``\"2012\"``", ("``\"2009\"`` или ``\"2012\"``. Определяет состав словаря: ``gamma`` только для ``\"2012\"``.", "``\"2009\"`` or ``\"2012\"``. Determines the content of the dictionary: ``gamma`` only for ``\"2012\"``."))],
    special=[NAN_STD, ("Постоянный ряд даёт NaN для :math:`r`, :math:`\\alpha` и :math:`\\gamma`, поскольку они используют стандартное отклонение.", "A constant series gives NaN for :math:`r`, :math:`\\alpha` and :math:`\\gamma` since they use the standard deviation.")],
    backend_note=[("На всех бэкендах значение это словарь, значения которого имеют тип, зависящий от бэкенда (на xarray это ``DataArray``).",
                   "On every backend the value is a dictionary whose values have a backend-dependent type (``DataArray`` on xarray).")],
    examples=kge_components_examples,
    hydro=[("Сами компоненты полезнее итога: по ним видно, чем плоха модель. Типичная картина для калибровки по NSE это :math:`\\alpha < 1` при :math:`\\beta` около 1: пики срезаны, объём сохранён (в примере выше :math:`\\alpha \\approx 0.89`).",
            "The components are more useful than the total: they show what is wrong with a model. A typical picture for NSE calibration is :math:`\\alpha < 1` at :math:`\\beta` near 1: peaks are clipped, volume is preserved (in the example above :math:`\\alpha \\approx 0.89`).")],
    related=["kge_2009", "kge_2012", "r_component", "alpha_component", "beta_component", "gamma_component"],
    refs=True,
)

# =================================================================================== components
def comp_flow(name, extra):
    return flow(name, extra=extra)


def r_extra(d):
    d.p(("Компонента :math:`r` совпадает с :ref:`metric-pearson_r`:", "The component :math:`r` coincides with :ref:`metric-pearson_r`:"))
    d.code('''
print(round(float(hm.r_component(q_obs, q_sim)), 6), round(float(hm.pearson_r(q_obs, q_sim)), 6))
''')


R_COMP = dict(
    name="r_component",
    title=("Компонента r критерия KGE (корреляция)", "KGE component r (correlation)"),
    short=[("Коэффициент корреляции Пирсона между наблюдённым и модельным рядами как компонента :ref:`metric-kge_2009` и :ref:`metric-kge_2012`. Измеряет совпадение фазы и формы гидрографа.",
            "The Pearson correlation coefficient between the observed and simulated series as a component of :ref:`metric-kge_2009` and :ref:`metric-kge_2012`. It measures agreement in the phase and shape of the hydrograph.")],
    formula=[r"r = \frac{\sum_{i} w_i\,(O_i-\bar{O})(S_i-\bar{S})}{\sqrt{\sum_{i} w_i\,(O_i-\bar{O})^2}\,\sqrt{\sum_{i} w_i\,(S_i-\bar{S})^2}}"],
    symbols=[("Обозначения как на странице :ref:`metric-pearson_r`.", "Notation as on the page :ref:`metric-pearson_r`.")],
    deviation=[("Результат тождественен :ref:`metric-pearson_r`; функция существует как часть набора компонент KGE (Gupta et al. :footcite:p:`gupta2009`).",
                "The result is identical to :ref:`metric-pearson_r`; the function exists as part of the set of KGE components (Gupta et al. :footcite:p:`gupta2009`).")],
    range="[-1, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 означает точную положительную линейную связь. Для постоянного ряда результат NaN.", "The value 1 means an exact positive linear relation. For a constant series the result is NaN.")],
    interp=[("Общепринятых градаций нет; см. :ref:`metric-pearson_r`.", "There are no accepted ratings; see :ref:`metric-pearson_r`.")],
    special=[NAN_STD, ("Постоянный ряд и один элемент дают NaN.", "A constant series and a single element give NaN.")],
    examples=comp_flow("r_component", r_extra),
    hydro=[("Корреляция не зависит от смещения и масштаба, поэтому её нужно читать вместе с :ref:`metric-alpha_component` и :ref:`metric-beta_component`.",
            "Correlation does not depend on bias and scale, so it should be read together with :ref:`metric-alpha_component` and :ref:`metric-beta_component`.")],
    related=["pearson_r", "kge_components", "alpha_component", "beta_component"],
    refs=True,
)


def alpha_extra(d):
    d.p(("Аргумент ``version`` проверяется, но на значение не влияет:", "The argument ``version`` is validated but does not affect the value:"))
    d.code('''
print(round(float(hm.alpha_component(q_obs, q_sim, version="2009")), 6), round(float(hm.alpha_component(q_obs, q_sim, version="2012")), 6))
''')


ALPHA_COMP = dict(
    name="alpha_component",
    title=("Компонента α критерия KGE (отношение стандартных отклонений)", "KGE component α (ratio of standard deviations)"),
    short=[("Отношение стандартного отклонения модельного ряда к стандартному отклонению наблюдений. Значение меньше 1 означает, что модель занижает изменчивость стока.",
            "The ratio of the standard deviation of the simulated series to that of the observations. A value below 1 means the model underestimates the variability of flow.")],
    sig_opt=", version=\"2012\"",
    formula=[r"\alpha = \frac{\sigma_S}{\sigma_O}"],
    symbols=[(r":math:`\sigma` стандартное отклонение с ``ddof=1``; при заданных весах оно взвешенное.", r":math:`\sigma` is the standard deviation with ``ddof=1``; it is weighted when weights are given.")],
    deviation=[("Для обеих версий вычисляется одинаково; ``version`` лишь проверяется. Компонента :math:`\\alpha` входит в :ref:`metric-kge_2009` и не входит в :ref:`metric-kge_2012`, где вместо неё стоит :ref:`metric-gamma_component`.",
                "It is computed identically for both versions; ``version`` is only validated. The component :math:`\\alpha` is a term of :ref:`metric-kge_2009` and is not a term of :ref:`metric-kge_2012`, where :ref:`metric-gamma_component` replaces it.")],
    range="[0, +∞)", optimum="1", dir="one",
    bounds=[("Значение 1 означает совпадающую изменчивость. Значение 0 возникает у постоянного модельного ряда. Если наблюдения постоянны, результат NaN.", "The value 1 means matching variability. The value 0 occurs for a constant simulated series. If the observations are constant the result is NaN.")],
    interp=[("Порогов нет. :math:`\\alpha < 1` указывает на срезанные пики и сглаженный гидрограф, :math:`\\alpha > 1` на завышенную амплитуду.", "There are no thresholds. :math:`\\alpha < 1` points to clipped peaks and a smoothed hydrograph, :math:`\\alpha > 1` to an exaggerated amplitude.")],
    params_opt=[("``version``", "str", "``\"2012\"``", ("``\"2009\"`` или ``\"2012\"``; другое значение вызывает ``ValueError``. На результат не влияет.", "``\"2009\"`` or ``\"2012\"``; any other value raises ``ValueError``. It does not affect the result."))],
    special=[NAN_STD, ("Постоянные наблюдения дают NaN. Один элемент даёт NaN.", "Constant observations give NaN. A single element gives NaN.")],
    examples=comp_flow("alpha_component", alpha_extra),
    hydro=[("По разложению Gupta et al. :footcite:p:`gupta2009` модель, оптимальная по NSE, имеет :math:`\\alpha` равное корреляции, то есть меньше 1: калибровка по NSE систематически занижает амплитуду стока. Смещение среднего на :math:`\\alpha` не влияет.",
            "By the decomposition of Gupta et al. :footcite:p:`gupta2009` a model optimal in terms of NSE has :math:`\\alpha` equal to the correlation, that is below 1: NSE calibration systematically underestimates flow amplitude. A bias in the mean does not affect :math:`\\alpha`.")],
    related=["kge_2009", "gamma_component", "beta_component", "kge_components"],
    refs=True,
)


def beta_extra(d):
    d.p(("Связь с процентным смещением: :math:`\\mathrm{PBIAS} = 100\\,(\\beta - 1)` без весов.", "The link to the percent bias: :math:`\\mathrm{PBIAS} = 100\\,(\\beta - 1)` without weights."))
    d.code('''
beta = float(hm.beta_component(q_obs, q_sim))
print(round(beta, 4), round(float(hm.pbias(q_obs, q_sim)), 3), round(100 * (beta - 1), 3))
''')


BETA_COMP = dict(
    name="beta_component",
    title=("Компонента β критерия KGE (отношение средних)", "KGE component β (ratio of means)"),
    short=[("Отношение среднего модельного ряда к среднему наблюдений. Значение больше 1 означает завышение объёма стока, меньше 1 занижение.",
            "The ratio of the mean of the simulated series to the mean of the observations. A value above 1 means overestimated runoff volume, below 1 underestimated.")],
    formula=[r"\beta = \frac{\mu_S}{\mu_O}"],
    symbols=[(r":math:`\mu` среднее; при заданных весах оно взвешенное.", r":math:`\mu` is the mean; it is weighted when weights are given.")],
    deviation=[("Совпадает с определением Gupta et al. :footcite:p:`gupta2009`. Это отношение, а не относительная разность, поэтому оптимум равен 1, а не 0.",
                "It matches the definition of Gupta et al. :footcite:p:`gupta2009`. It is a ratio, not a relative difference, so the optimum is 1, not 0.")],
    range="(-∞, +∞)", optimum="1", dir="one",
    bounds=[("Для неотрицательных величин значение не меньше 0. Если среднее наблюдений равно нулю, результат NaN.", "For non-negative variables the value is not below 0. If the mean of the observations is zero the result is NaN.")],
    interp=[("Порогов нет. Для процентной шкалы используйте :ref:`metric-pbias`.", "There are no thresholds. For a percent scale use :ref:`metric-pbias`.")],
    special=[NAN_STD, ("Нулевое среднее наблюдений даёт NaN; постоянный ряд допустим.", "A zero mean of the observations gives NaN; a constant series is allowed.")],
    examples=comp_flow("beta_component", beta_extra),
    hydro=[("Компонента измеряет только объём. Модель с :math:`\\beta = 1` может неверно описывать сезонное распределение стока; смотрите её вместе с :ref:`metric-r_component`.",
            "The component measures volume only. A model with :math:`\\beta = 1` can describe the seasonal distribution of flow incorrectly; read it together with :ref:`metric-r_component`.")],
    related=["pbias", "kge_2009", "kge_2012", "bias"],
    refs=True,
)


def gamma_extra(d):
    d.p(("Отношение коэффициентов вариации выражается через две другие компоненты: :math:`\\gamma = \\alpha / \\beta`.", "The ratio of coefficients of variation is expressed through the other two components: :math:`\\gamma = \\alpha / \\beta`."))
    d.code('''
alpha = float(hm.alpha_component(q_obs, q_sim))
beta = float(hm.beta_component(q_obs, q_sim))
print(round(float(hm.gamma_component(q_obs, q_sim)), 6), round(alpha / beta, 6))
''')


GAMMA_COMP = dict(
    name="gamma_component",
    title=("Компонента γ критерия KGE (отношение коэффициентов вариации)", "KGE component γ (ratio of coefficients of variation)"),
    short=[("Отношение коэффициента вариации модельного ряда к коэффициенту вариации наблюдений. В отличие от :ref:`metric-alpha_component`, не зависит от смещения среднего :footcite:p:`kling2012`.",
            "The ratio of the coefficient of variation of the simulated series to that of the observations. Unlike :ref:`metric-alpha_component`, it does not depend on a bias in the mean :footcite:p:`kling2012`.")],
    formula=[r"\gamma = \frac{\mathrm{CV}_S}{\mathrm{CV}_O} = \frac{\sigma_S/\mu_S}{\sigma_O/\mu_O}"],
    symbols=[(r":math:`\mathrm{CV}` коэффициент вариации, то есть отношение стандартного отклонения (``ddof=1``) к среднему.", r":math:`\mathrm{CV}` is the coefficient of variation, that is the ratio of the standard deviation (``ddof=1``) to the mean.")],
    deviation=[("Совпадает с определением Kling et al. :footcite:p:`kling2012`. Тождественно :math:`\\gamma = \\alpha/\\beta`, что проверяется в примере.", "It matches the definition of Kling et al. :footcite:p:`kling2012`. It is identically :math:`\\gamma = \\alpha/\\beta`, which the example checks.")],
    range="(-∞, +∞)", optimum="1", dir="one",
    bounds=[("Для положительных величин значение не меньше 0. Если среднее наблюдений или модели равно нулю, а также при постоянных наблюдениях, результат NaN.", "For positive variables the value is not below 0. If the mean of the observations or of the simulation is zero, and also for constant observations, the result is NaN.")],
    interp=[("Порогов нет. :math:`\\gamma` близко к 1, если относительная изменчивость воспроизведена, даже при смещённом среднем.", "There are no thresholds. :math:`\\gamma` is close to 1 if the relative variability is reproduced even with a biased mean.")],
    special=[NAN_STD, ("Постоянные наблюдения дают NaN. Постоянный модельный ряд даёт 0.", "Constant observations give NaN. A constant simulated series gives 0.")],
    examples=comp_flow("gamma_component", gamma_extra),
    hydro=[("Компонента позволяет оценить изменчивость независимо от объёма. При среднем, близком к нулю, значение теряет смысл; для расходов это редкость, для рядов с вычтенным средним метрика непригодна.",
            "The component makes it possible to assess variability independently of volume. With a mean close to zero the value loses meaning; for discharge this is rare, and for series with the mean removed the metric is unsuitable.")],
    related=["kge_2012", "alpha_component", "beta_component", "kge_components"],
    refs=True,
)

FAMILY3 = {s["name"]: s for s in (LOG_NSE, MNSE, NSE_BOUNDED, RSR, VE, KGE09, KGE_COMP, R_COMP, ALPHA_COMP, BETA_COMP, GAMMA_COMP)}
