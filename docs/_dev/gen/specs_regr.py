"""Metric pages, family 2: error and correlation metrics on a continuous variable.

mae, mse, rmse, nrmse, bias, pbias, r2, pearson_r, spearman_r, kendall_tau, willmott_d.
"""
import numpy as np

from exkit import basic, setup, stations, xr_dim, years
from lib import fmt
from metricpage import SETUP

# ------------------------------------------------------------------------------ shared wording
NAN_STD = ("При умолчании ``nan_policy=\"omit\"`` пары с пропуском в ``obs`` или ``sim`` удаляются целиком, в том числе при заданной оси. ``\"propagate\"`` возвращает NaN, если в ряду (или в срезе вдоль оси) есть пропуск, ``\"raise\"`` вызывает ``ValueError``. Значение ``inf`` пропуском не считается; результат для него показан в таблице.",
           "With the default ``nan_policy=\"omit\"`` pairs with a gap in ``obs`` or ``sim`` are dropped whole, also along an axis. ``\"propagate\"`` returns NaN if the series (or the slice along the axis) contains a gap, ``\"raise\"`` raises ``ValueError``. An ``inf`` is not treated as a gap; the table shows the result for it.")
NEAR_ZERO = ("Если среднее наблюдений равно нулю лишь с точностью до округления, знаменатель не равен нулю точно, и результат огромен по модулю (в таблице строка с центрированным рядом). Для рядов с нулевым средним метрика не применяется.",
             "If the mean of the observations is zero only up to rounding the denominator is not exactly zero and the result is huge in magnitude (in the table the row with the centred series). The metric is not applied to series with a zero mean.")
ONE_ELEMENT = ("Один элемент даёт значение, вычисленное по единственной паре, а метрики, использующие стандартное отклонение, дают NaN.",
               "A single element gives the value computed from that pair, whereas metrics that use a standard deviation give NaN.")
NO_THRESH_SCALE = ("Общепринятых градаций качества для этой метрики нет. Значение выражено в единицах величины (для расхода воды м³/с) и зависит от размера реки, поэтому между створами напрямую не сравнивается.",
                   "There are no accepted quality ratings for this metric. The value is in the units of the variable (m³/s for discharge) and depends on the size of the river, so it is not compared directly across gauges.")


def std_examples(name, check=None, kw="", extra=None, xr=True, with_stations=True):
    """Common example flow: basic call, independent check, gauges, water years, xarray."""
    def run(d):
        setup(d)
        basic(d, name, kw)
        if check:
            d.p(check[0])
            d.code(check[1])
        if extra:
            extra(d)
        if with_stations:
            stations(d, name, kw)
        years(d, name, kw)
        if xr:
            xr_dim(d, name)
    return run


# ===================================================================================== mae
MAE = dict(
    name="mae",
    title=("Средняя абсолютная ошибка (MAE)", "Mean absolute error (MAE)"),
    short=[("MAE это среднее модуля разности между модельным и наблюдённым значением, в единицах самой величины. Каждая ошибка входит линейно, поэтому крупные промахи влияют на значение слабее, чем в :ref:`metric-rmse`.",
            "MAE is the mean of the absolute difference between the simulated and the observed value, in the units of the variable itself. Each error enters linearly, so large misses weigh less than in :ref:`metric-rmse`.")],
    formula=[r"\mathrm{MAE} = \frac{\sum_{i=1}^{n} w_i\,\left|O_i - S_i\right|}{\sum_{i=1}^{n} w_i}"],
    symbols=[(r":math:`O_i` наблюдённое, :math:`S_i` модельное значение, :math:`w_i` вес (1 без ``sample_weight``), :math:`n` число действительных пар. Суммирование идёт по оси ``axis``, а при ``axis=None`` по всем элементам.",
              r":math:`O_i` is the observed and :math:`S_i` the simulated value, :math:`w_i` the weight (1 without ``sample_weight``), :math:`n` the number of valid pairs. The sum runs along ``axis``, or over all elements with ``axis=None``.")],
    deviation=[("Совпадает с классическим определением; веса расширяют его до взвешенного среднего. Знак ошибки теряется, поэтому систематическое завышение и занижение MAE не различает (для знака используйте :ref:`metric-bias`).",
                "It matches the classical definition; weights extend it to a weighted mean. The sign of the error is lost, so MAE does not distinguish systematic over- and underestimation (use :ref:`metric-bias` for the sign).")],
    range="[0, +∞)", optimum="0", dir="down",
    bounds=[("Значение 0 достигается только при полном совпадении. Верхней границы нет. Для постоянного ``obs`` метрика определена, в отличие от метрик с нормировкой на дисперсию.",
             "The value 0 is reached only for a perfect match. There is no upper bound. For a constant ``obs`` the metric is defined, unlike metrics normalised by variance.")],
    interp=[NO_THRESH_SCALE,
            ("Сравнение MAE и RMSE как мер средней ошибки рассматривают Willmott и Matsuura :footcite:p:`willmott2005`; по прочитанному заглавию работы они обосновывают преимущества MAE, текст статьи не читался.",
             "The comparison of MAE and RMSE as measures of average error is discussed by Willmott and Matsuura :footcite:p:`willmott2005`; the title states the advantages of MAE, the text of the paper was not read.")],
    special=[NAN_STD, ONE_ELEMENT],
    examples=std_examples("mae", check=(
        ("Для любого ряда RMSE не меньше MAE. Их отношение растёт, когда ошибки распределены неравномерно:",
         "For any series RMSE is not smaller than MAE. Their ratio grows when errors are unevenly distributed:"),
        '''
print(round(float(hm.rmse(q_obs, q_sim)) / float(hm.mae(q_obs, q_sim)), 3))
''')),
    hydro=[("Линейный вес ошибок делает MAE менее зависимой от пиков, чем RMSE. Отношение RMSE к MAE в примере показывает вклад крупных ошибок: чем оно больше, тем сильнее значение RMSE определяют отдельные промахи, чаще всего на половодье.",
            "Linear weighting of errors makes MAE less dependent on peaks than RMSE. The RMSE to MAE ratio in the example shows the contribution of large errors: the larger it is, the more individual misses, most often in the flood, set the RMSE."),
           ("MAE не зависит от знака, поэтому занижение на половодье и завышение на межени взаимно не компенсируются, как в :ref:`metric-bias`.",
            "MAE does not depend on sign, so an underestimate in the flood and an overestimate in low flow do not cancel as in :ref:`metric-bias`.")],
    related=["mse", "rmse", "bias", "nse", "ve"],
    refs=True,
)

# ===================================================================================== mse
MSE = dict(
    name="mse",
    title=("Среднеквадратическая ошибка (MSE)", "Mean squared error (MSE)"),
    short=[("MSE это среднее квадрата разности между модельным и наблюдённым значением. Единица измерения это квадрат единицы величины (для расхода воды м⁶/с²), поэтому на практике чаще используют корень, :ref:`metric-rmse`.",
            "MSE is the mean of the squared difference between the simulated and the observed value. Its unit is the square of the unit of the variable (m⁶/s² for discharge), which is why the root, :ref:`metric-rmse`, is more common in practice.")],
    formula=[r"\mathrm{MSE} = \frac{\sum_{i=1}^{n} w_i\,\left(O_i - S_i\right)^2}{\sum_{i=1}^{n} w_i}",
             r"\mathrm{MSE} = \bar{e}^{\,2} + \sigma_e^2, \qquad e_i = S_i - O_i"],
    symbols=[(r":math:`O_i` наблюдённое, :math:`S_i` модельное значение, :math:`w_i` вес, :math:`n` число действительных пар. Вторая запись это разложение без весов: :math:`\bar{e}` среднее ошибки (это :ref:`metric-bias`), :math:`\sigma_e^2` её дисперсия с делителем :math:`n`.",
              r":math:`O_i` is the observed and :math:`S_i` the simulated value, :math:`w_i` the weight, :math:`n` the number of valid pairs. The second line is the decomposition without weights: :math:`\bar{e}` is the mean error (the :ref:`metric-bias`), :math:`\sigma_e^2` its variance with divisor :math:`n`.")],
    deviation=[("Совпадает с классическим определением. Разложение на квадрат смещения и дисперсию ошибки выполняется точно и проверяется в примере.",
                "It matches the classical definition. The decomposition into the squared bias and the error variance is exact and is checked in the example.")],
    range="[0, +∞)", optimum="0", dir="down",
    bounds=[("Значение 0 достигается только при полном совпадении, верхней границы нет. Для постоянного ``obs`` метрика определена.",
             "The value 0 is reached only for a perfect match and there is no upper bound. For a constant ``obs`` the metric is defined.")],
    interp=[NO_THRESH_SCALE],
    special=[NAN_STD, ONE_ELEMENT],
    examples=std_examples("mse", check=(
        ("Разложение MSE на квадрат смещения и дисперсию ошибки:",
         "Decomposition of MSE into squared bias and error variance:"),
        '''
error = q_sim - q_obs
print(round(float(hm.mse(q_obs, q_sim)), 3), round(float(hm.bias(q_obs, q_sim)) ** 2 + np.var(error), 3))
''')),
    hydro=[("Квадрат усиливает крупные ошибки: единичный промах на пике половодья может дать больше, чем тысячи малых ошибок на межени. Для сопоставления с наблюдениями используйте :ref:`metric-rmse`, для сопоставления с изменчивостью наблюдений :ref:`metric-nse`.",
            "Squaring amplifies large errors: a single miss at the flood peak can outweigh thousands of small errors in low flow. For comparison with the observations use :ref:`metric-rmse`, for comparison with the variability of the observations :ref:`metric-nse`.")],
    related=["rmse", "mae", "bias", "nse"],
    refs=False,
)

# ==================================================================================== rmse
RMSE = dict(
    name="rmse",
    title=("Среднеквадратическая ошибка, корень (RMSE)", "Root mean squared error (RMSE)"),
    short=[("RMSE это корень из :ref:`metric-mse`: ошибка в единицах самой величины, для расхода воды в м³/с. Крупные ошибки в ней весят больше, чем в :ref:`metric-mae`.",
            "RMSE is the square root of :ref:`metric-mse`: an error in the units of the variable itself, m³/s for discharge. Large errors weigh more in it than in :ref:`metric-mae`.")],
    formula=[r"\mathrm{RMSE} = \sqrt{\frac{\sum_{i=1}^{n} w_i\,\left(O_i - S_i\right)^2}{\sum_{i=1}^{n} w_i}}"],
    symbols=[(r":math:`O_i` наблюдённое, :math:`S_i` модельное значение, :math:`w_i` вес, :math:`n` число действительных пар. Суммирование идёт по оси ``axis``, при ``axis=None`` по всем элементам.",
              r":math:`O_i` is the observed and :math:`S_i` the simulated value, :math:`w_i` the weight, :math:`n` the number of valid pairs. The sum runs along ``axis``, over all elements with ``axis=None``.")],
    deviation=[("Совпадает с классическим определением. При ``reduction=\"mean\"`` по оси результат это среднее RMSE по срезам, а не RMSE по всем значениям сразу: корень не коммутирует со средним.",
                "It matches the classical definition. With ``reduction=\"mean\"`` over an axis the result is the mean of the slice RMSE values, not the RMSE over all values at once: the root does not commute with the mean.")],
    range="[0, +∞)", optimum="0", dir="down",
    bounds=[("Значение 0 достигается только при полном совпадении, верхней границы нет.",
             "The value 0 is reached only for a perfect match and there is no upper bound.")],
    interp=[NO_THRESH_SCALE,
            ("Для нормировки на изменчивость наблюдений Moriasi et al. :footcite:p:`moriasi2007` предложили :ref:`metric-rsr`; их градации относятся к RSR, а не к RMSE.",
             "To normalise by the variability of the observations Moriasi et al. :footcite:p:`moriasi2007` proposed :ref:`metric-rsr`; their ratings refer to RSR, not to RMSE.")],
    special=[NAN_STD, ONE_ELEMENT],
    examples=std_examples("rmse", check=(
        ("RMSE равна корню из MSE; в единицах расхода она всегда не меньше MAE:",
         "RMSE equals the root of MSE; in discharge units it is never smaller than MAE:"),
        '''
print(round(float(hm.rmse(q_obs, q_sim)), 3), round(float(np.sqrt(hm.mse(q_obs, q_sim).value)), 3), round(float(hm.mae(q_obs, q_sim)), 3))
''')),
    hydro=[("RMSE определяется пиками: вклады ошибки в 30 м³/с на вершине половодья и ошибки в 3 м³/с на межени в сумму квадратов различаются в 100 раз. Поэтому одно значение RMSE мало говорит о качестве межени; считайте её отдельно для сезонов или используйте :ref:`metric-log_nse`.",
            "RMSE is dominated by peaks: the contributions of an error of 30 m³/s at the top of the flood and of an error of 3 m³/s in low flow to the sum of squares differ by a factor of 100. A single RMSE therefore says little about low-flow quality; compute it by season or use :ref:`metric-log_nse`."),
           ("Автокорреляция остатков не меняет значение RMSE, но делает эффективное число независимых наблюдений меньше длины ряда; доверительные интервалы по формулам для независимых ошибок завышают точность.",
            "Autocorrelation of residuals does not change the RMSE value but makes the effective number of independent observations smaller than the length of the series; confidence intervals based on formulas for independent errors overstate the precision.")],
    related=["mae", "mse", "nrmse", "rsr", "nse"],
    refs=True,
)

# ==================================================================================== nrmse
def nrmse_extra(d):
    d.p(("Выбор нормировки меняет значение на порядок. При ``normalization=\"std\"`` результат совпадает с :ref:`metric-rsr`:",
         "The choice of normalisation changes the value by an order of magnitude. With ``normalization=\"std\"`` the result equals :ref:`metric-rsr`:"))
    d.code('''
for mode in ("mean", "std", "range", "iqr"):
    print(mode, round(float(hm.nrmse(q_obs, q_sim, normalization=mode)), 4))
print(round(float(hm.rsr(q_obs, q_sim)), 4))
''')


NRMSE = dict(
    name="nrmse",
    title=("Нормированная среднеквадратическая ошибка (NRMSE)", "Normalised root mean squared error (NRMSE)"),
    short=[("NRMSE это :ref:`metric-rmse`, делённая на характеристику наблюдений: среднее, стандартное отклонение, размах или межквартильный размах. Результат безразмерный.",
            "NRMSE is :ref:`metric-rmse` divided by a characteristic of the observations: the mean, the standard deviation, the range or the interquartile range. The result is dimensionless.")],
    sig_opt=", normalization=\"mean\"",
    formula=[r"\mathrm{NRMSE} = \frac{\mathrm{RMSE}}{N}, \qquad N \in \{\bar{O},\ \sigma_O,\ O_{\max}-O_{\min},\ Q_{75}-Q_{25}\}"],
    symbols=[(r":math:`\bar{O}` среднее наблюдений (взвешенное при заданных весах), :math:`\sigma_O` стандартное отклонение с ``ddof=1``, :math:`Q_{75}-Q_{25}` межквартильный размах. Нормировка выбирается аргументом ``normalization``; по умолчанию ``\"mean\"``.",
              r":math:`\bar{O}` is the mean of the observations (weighted when weights are given), :math:`\sigma_O` the standard deviation with ``ddof=1``, :math:`Q_{75}-Q_{25}` the interquartile range. The normalisation is chosen by the argument ``normalization``; the default is ``\"mean\"``.")],
    deviation=[("В литературе встречаются все четыре нормировки, единого определения NRMSE нет, поэтому значения нужно сопровождать указанием нормировки. Размах и межквартильный размах считаются по ``obs`` без учёта весов; среднее и стандартное отклонение взвешиваются. Если нормировка равна нулю (например, нулевое среднее), результат NaN. При отрицательном среднем нормировка ``\"mean\"`` даёт отрицательное значение.",
                "All four normalisations occur in the literature and there is no single definition of NRMSE, so the values should be accompanied by the normalisation used. The range and the interquartile range are computed from ``obs`` without weights; the mean and the standard deviation are weighted. If the normaliser is zero (for example a zero mean) the result is NaN. With a negative mean the ``\"mean\"`` normalisation gives a negative value.")],
    range="[0, +∞)", optimum="0", dir="down",
    bounds=[("Значение 0 означает полное совпадение. Верхней границы нет. Для величины с нулевым средним нормировка ``\"mean\"`` не определена.",
             "The value 0 means a perfect match. There is no upper bound. The ``\"mean\"`` normalisation is undefined for a variable with zero mean.")],
    interp=[("Градаций для NRMSE нет, потому что значение зависит от выбранной нормировки. Для нормировки на стандартное отклонение (``\"std\"``) смысл совпадает с :ref:`metric-rsr`, для которого Moriasi et al. :footcite:p:`moriasi2007` приводят градации (месячный шаг).",
             "There are no ratings for NRMSE because the value depends on the chosen normalisation. For normalisation by the standard deviation (``\"std\"``) the meaning coincides with :ref:`metric-rsr`, for which Moriasi et al. :footcite:p:`moriasi2007` give ratings (monthly time step).")],
    params_opt=[("``normalization``", "str", "``\"mean\"``",
                 ("``\"mean\"``, ``\"std\"``, ``\"range\"`` или ``\"iqr\"``. Другое значение вызывает ``ValueError``.",
                  "``\"mean\"``, ``\"std\"``, ``\"range\"`` or ``\"iqr\"``. Any other value raises ``ValueError``."))],
    special=[NAN_STD, NEAR_ZERO],
    examples=std_examples("nrmse", extra=nrmse_extra),
    hydro=[("Нормировка на среднее удобна для сравнения створов, но на реке с большим половодьем среднее мало отличается от межени, а RMSE определяется пиком; нормировка на стандартное отклонение (то есть RSR) учитывает изменчивость и менее зависит от того, какую долю года занимает межень.",
            "Normalisation by the mean is convenient for comparing gauges, but on a river with a large flood the mean is close to the low-flow level while the RMSE is set by the peak; normalisation by the standard deviation (that is, RSR) accounts for variability and depends less on the share of the year occupied by low flow."),
           ("Нормировка на размах определяется одним экстремумом ряда и поэтому нестабильна при смене периода наблюдений.",
            "Normalisation by the range is set by a single extreme of the series and is therefore unstable when the observation period changes.")],
    related=["rmse", "rsr", "pbias", "nse"],
    refs=True,
)

# ===================================================================================== bias
def bias_extra(d):
    d.p(("Знак смещения: положительное значение означает завышение. Смещение за половодье и за остальные месяцы может иметь разный знак:",
         "Sign of the bias: a positive value means overestimation. The bias in the flood and in the other months can have different signs:"))
    d.code('''
import pandas as pd

frame = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
flood = frame.index.month.isin([4, 5, 6])
print(round(float(hm.bias(frame.q_obs[flood], frame.q_sim[flood])), 3), round(float(hm.bias(frame.q_obs[~flood], frame.q_sim[~flood])), 3))
''')


BIAS = dict(
    name="bias",
    title=("Смещение (среднее значение ошибки, bias)", "Bias (mean error)"),
    short=[("Bias это среднее разности «модель минус наблюдение», в единицах величины. Положительное значение означает завышение, отрицательное занижение.",
            "Bias is the mean of the difference simulated minus observed, in the units of the variable. A positive value means overestimation, a negative one underestimation.")],
    formula=[r"\mathrm{bias} = \frac{\sum_{i=1}^{n} w_i\,\left(S_i - O_i\right)}{\sum_{i=1}^{n} w_i}"],
    symbols=[(r":math:`O_i` наблюдённое, :math:`S_i` модельное значение, :math:`w_i` вес, :math:`n` число действительных пар. Суммирование идёт по оси ``axis``.",
              r":math:`O_i` is the observed and :math:`S_i` the simulated value, :math:`w_i` the weight, :math:`n` the number of valid pairs. The sum runs along ``axis``.")],
    deviation=[("Знак задан как «модель минус наблюдение», как и в :ref:`metric-pbias`. В литературе встречается и обратный знак. Метрика не является мерой точности: ошибки разных знаков компенсируются.",
                "The sign is simulated minus observed, as in :ref:`metric-pbias`. The opposite sign also occurs in the literature. The metric is not a measure of accuracy: errors of opposite signs cancel.")],
    range="(-∞, +∞)", optimum="0", dir="zero",
    bounds=[("Нижней и верхней границ нет. Значение 0 не означает точной модели: оно означает лишь отсутствие среднего смещения.",
             "There are neither lower nor upper bounds. The value 0 does not mean an accurate model: it only means the absence of a mean bias.")],
    interp=[NO_THRESH_SCALE,
            ("Для относительной оценки смещения используйте :ref:`metric-pbias`.", "For a relative measure of the bias use :ref:`metric-pbias`.")],
    special=[NAN_STD, ONE_ELEMENT],
    examples=std_examples("bias", extra=bias_extra),
    hydro=[("Произведение смещения на длительность периода и на число секунд даёт ошибку объёма стока, поэтому bias удобно связать с водным балансом. Значение за год скрывает противоположные по знаку сезонные смещения, как в примере выше.",
            "The product of the bias with the length of the period and the number of seconds gives the runoff volume error, so bias can be related to the water balance. The annual value hides seasonal biases of opposite signs, as in the example above.")],
    related=["pbias", "mae", "ve", "beta_component"],
    refs=False,
)

# ==================================================================================== pbias
PBIAS = dict(
    name="pbias",
    title=("Процентное смещение (PBIAS)", "Percent bias (PBIAS)"),
    short=[("PBIAS это суммарное смещение модели в процентах от суммы наблюдений, то есть относительная ошибка объёма стока за период :footcite:p:`moriasi2007`. Положительное значение означает завышение.",
            "PBIAS is the total bias of the model as a percentage of the sum of the observations, that is the relative runoff volume error over the period :footcite:p:`moriasi2007`. A positive value means overestimation.")],
    formula=[r"\mathrm{PBIAS} = 100\cdot\frac{\sum_{i=1}^{n} w_i\,\left(S_i - O_i\right)}{\sum_{i=1}^{n} w_i\,O_i}"],
    symbols=[(r":math:`O_i` наблюдённое, :math:`S_i` модельное значение, :math:`w_i` вес, :math:`n` число действительных пар. Суммирование идёт по оси ``axis``.",
              r":math:`O_i` is the observed and :math:`S_i` the simulated value, :math:`w_i` the weight, :math:`n` the number of valid pairs. The sum runs along ``axis``.")],
    deviation=[("Знак противоположен определению Moriasi et al. :footcite:p:`moriasi2007`, где в числителе стоит :math:`O_i - S_i` (со ссылкой на Gupta et al. :footcite:p:`gupta1999`) и положительное значение означает занижение. Модуль совпадает, поэтому градации Moriasi et al. применяются к ``abs(pbias)``. Знак в библиотеке согласован с :ref:`metric-bias`.",
                "The sign is opposite to the definition of Moriasi et al. :footcite:p:`moriasi2007`, who put :math:`O_i - S_i` in the numerator (citing Gupta et al. :footcite:p:`gupta1999`), so that a positive value means underestimation. The magnitude is the same, so the ratings of Moriasi et al. apply to ``abs(pbias)``. The sign in the library is consistent with :ref:`metric-bias`.")],
    range="(-∞, +∞)", optimum="0", dir="zero",
    bounds=[("Границ нет. Если сумма наблюдений равна нулю, результат NaN. Для величин, которые меняют знак, и для рядов с отрицательным средним метрика теряет смысл: знак результата инвертируется.",
             "There are no bounds. If the sum of the observations is zero the result is NaN. For variables that change sign, and for series with a negative mean, the metric loses its meaning: the sign of the result is inverted.")],
    interp=[("Moriasi et al. :footcite:p:`moriasi2007` (таблица 4) оценивают качество моделирования стока по модулю PBIAS: очень хорошо при :math:`|\\mathrm{PBIAS}|<10\\,\\%`, хорошо при 10–15 %, удовлетворительно при 15–25 %, неудовлетворительно при 25 % и более. Градации даны для непрерывного долгосрочного моделирования водосборов, а по стоку авторы связывают их с неопределённостью измеренных данных.",
             "Moriasi et al. :footcite:p:`moriasi2007` (Table 4) rate streamflow simulation by the magnitude of PBIAS: very good for :math:`|\\mathrm{PBIAS}|<10\\,\\%`, good for 10 to 15 %, satisfactory for 15 to 25 %, unsatisfactory for 25 % and more. The ratings were given for continuous long-term watershed simulation, and for streamflow the authors tie them to the uncertainty of the measured data."),
            ("Пороги эмпирические и зависят от качества данных; для короткого или малоизмеренного створа их нужно ослаблять.",
             "The thresholds are empirical and depend on data quality; for a short or poorly measured gauge they should be relaxed.")],
    special=[NAN_STD, ("Нулевая сумма наблюдений даёт NaN (в таблице: ряд из нулей).", "A zero sum of observations gives NaN (in the table: the all-zero series)."), NEAR_ZERO],
    examples=std_examples("pbias"),
    hydro=[("PBIAS измеряет только объём: модель с нулевым PBIAS может искажать фазу и форму гидрографа. Moriasi et al. :footcite:p:`moriasi2007` со ссылкой на Gupta et al. отмечают, что PBIAS для стока заметно сильнее меняется между методами автокалибровки в маловодные годы, чем в многоводные; это нужно учитывать при раздельной калибровке и верификации.",
            "PBIAS measures volume only: a model with zero PBIAS can still distort the phase and shape of the hydrograph. Moriasi et al. :footcite:p:`moriasi2007`, citing Gupta et al., note that PBIAS for streamflow varies more among autocalibration methods in dry years than in wet years; this should be considered when splitting calibration and verification."),
           ("Дополняйте PBIAS показателем формы гидрографа: :ref:`metric-nse` или :ref:`metric-kge_2012`.",
            "Complement PBIAS with a measure of hydrograph shape: :ref:`metric-nse` or :ref:`metric-kge_2012`.")],
    related=["bias", "ve", "beta_component", "nse", "rsr"],
    refs=True,
)

# ======================================================================================== r2
def r2_extra(d):
    d.p(("Функция ``r2`` не равна квадрату коэффициента корреляции. Для модели с систематическим занижением квадрат корреляции остаётся высоким, а ``r2`` падает:",
         "The function ``r2`` is not the squared correlation coefficient. For a model with a systematic underestimate the squared correlation stays high while ``r2`` falls:"))
    d.code('''
q_low = 0.6 * q_obs  # занижение всех расходов на 40 %
print(round(float(hm.r2(q_obs, q_low)), 3), round(float(hm.pearson_r(q_obs, q_low)) ** 2, 3))
''', '''
q_low = 0.6 * q_obs  # underestimate all discharge by 40 %
print(round(float(hm.r2(q_obs, q_low)), 3), round(float(hm.pearson_r(q_obs, q_low)) ** 2, 3))
''')
    d.p(("На тех же данных ``r2`` и :func:`~hydrometrics.nse` совпадают:", "On the same data ``r2`` and :func:`~hydrometrics.nse` coincide:"))
    d.code('''
print(round(float(hm.r2(q_obs, q_sim)), 6), round(float(hm.nse(q_obs, q_sim)), 6))
''')


R2 = dict(
    name="r2",
    title=("Коэффициент детерминации (R²)", "Coefficient of determination (R²)"),
    short=[("``r2`` это доля дисперсии наблюдений, объяснённая моделью, в определении «1 минус отношение суммы квадратов остатков к полной сумме квадратов». Это не квадрат коэффициента корреляции.",
            "``r2`` is the share of the variance of the observations explained by the model, defined as one minus the ratio of the residual sum of squares to the total sum of squares. It is not the squared correlation coefficient.")],
    formula=[r"R^2 = 1 - \frac{\sum_{i=1}^{n} w_i\,\left(O_i - S_i\right)^2}{\sum_{i=1}^{n} w_i\,\left(O_i - \bar{O}\right)^2}"],
    symbols=[(r":math:`O_i` наблюдённое, :math:`S_i` модельное значение, :math:`\bar{O}` среднее наблюдений (взвешенное при заданных весах), :math:`w_i` вес, :math:`n` число действительных пар.",
              r":math:`O_i` is the observed and :math:`S_i` the simulated value, :math:`\bar{O}` the mean of the observations (weighted when weights are given), :math:`w_i` the weight, :math:`n` the number of valid pairs.")],
    deviation=[("В литературе по гидрологическим моделям :math:`r^2` чаще означает квадрат коэффициента корреляции, и он, в отличие от этой метрики, не чувствителен к смещению и масштабу :footcite:p:`krause2005`. Здесь используется определение из регрессионного анализа. Формула совпадает с :ref:`metric-nse` без ``norm``; различаются только вырожденные случаи: при постоянном ``obs`` ``r2`` равна 1 для точного совпадения и NaN иначе, а при отсутствии действительных пар NaN; при всех нулевых весах результат 1.",
                "In the literature on hydrological models :math:`r^2` more often means the squared correlation coefficient, which, unlike this metric, is insensitive to bias and scale :footcite:p:`krause2005`. The definition used here is that of regression analysis. The formula coincides with :ref:`metric-nse` without ``norm``; only degenerate cases differ: for a constant ``obs`` ``r2`` is 1 for an exact match and NaN otherwise, and NaN when there is no valid pair; with all weights zero the result is 1.")],
    range="(-∞, 1]", optimum="1", dir="up",
    bounds=[("Верхняя граница достигается при совпадении рядов. Значение 0 означает, что модель не лучше постоянного прогноза средним наблюдений, отрицательное значение что хуже. Нижней границы нет.",
             "The upper bound is reached when the series coincide. The value 0 means the model is no better than a constant forecast at the observed mean, a negative value that it is worse. There is no lower bound.")],
    interp=[("Градаций именно для этой формы нет; поскольку формула совпадает с NSE, на неё распространяются те же ориентиры, что приведены на странице :ref:`metric-nse` (в том числе оговорки об их происхождении).",
             "There are no ratings for this particular form; since the formula coincides with NSE, the same reference points apply as given on the page :ref:`metric-nse` (including the caveats about their origin).")],
    special=[NAN_STD, ("Постоянный ``obs`` даёт NaN, если ряды не совпадают, и 1, если совпадают. Один элемент даёт NaN.", "A constant ``obs`` gives NaN if the series differ and 1 if they coincide. A single element gives NaN.")],
    examples=std_examples("r2", extra=r2_extra),
    hydro=[("Те же свойства, что у :ref:`metric-nse`: значение определяется крупными расходами, межень почти не влияет. Не путайте ``r2`` с квадратом корреляции: в литературе и в других пакетах под :math:`R^2` нередко понимают его.",
            "The same properties as :ref:`metric-nse`: the value is set by high flows and low flow hardly matters. Do not confuse ``r2`` with the squared correlation: in the literature and in other packages :math:`R^2` often means the latter.")],
    related=["nse", "pearson_r", "willmott_d", "kge_2012"],
    refs=True,
)

# ==================================================================================== pearson
def pearson_extra(d):
    d.p(("Корреляция не замечает смещения и масштаба: ряд, завышенный втрое, коррелирует с наблюдениями так же, как исходный.",
         "Correlation does not see bias or scale: a series inflated threefold correlates with the observations exactly as the original."))
    d.code('''
print(round(float(hm.pearson_r(q_obs, q_sim)), 4), round(float(hm.pearson_r(q_obs, 3 * q_sim)), 4))
''')
    d.p(("С :ref:`metric-nse` её связывает разложение: NSE = 2αr − α² − β_n², где α отношение стандартных отклонений, β_n смещение в долях стандартного отклонения наблюдений :footcite:p:`gupta2009`. Проверка:",
         "It is linked to :ref:`metric-nse` by the decomposition NSE = 2αr − α² − β_n², where α is the ratio of standard deviations and β_n the bias in units of the observed standard deviation :footcite:p:`gupta2009`. A check:"))
    d.code('''
r = np.corrcoef(q_obs, q_sim)[0, 1]
alpha = q_sim.std() / q_obs.std()
beta_n = (q_sim.mean() - q_obs.mean()) / q_obs.std()
print(round(2 * alpha * r - alpha ** 2 - beta_n ** 2, 6), round(float(hm.nse(q_obs, q_sim)), 6))
''')


PEARSON = dict(
    name="pearson_r",
    title=("Коэффициент корреляции Пирсона (r)", "Pearson correlation coefficient (r)"),
    short=[("Коэффициент измеряет линейную связь между наблюдённым и модельным рядами: совпадение по фазе и форме, независимо от смещения и масштаба. Он служит компонентой :ref:`metric-kge_2012`.",
            "The coefficient measures the linear relation between the observed and simulated series: agreement in phase and shape regardless of bias and scale. It is a component of :ref:`metric-kge_2012`.")],
    formula=[r"r = \frac{\sum_{i} w_i\,(O_i-\bar{O})(S_i-\bar{S})}{\sqrt{\sum_{i} w_i\,(O_i-\bar{O})^2}\,\sqrt{\sum_{i} w_i\,(S_i-\bar{S})^2}}"],
    symbols=[(r":math:`\bar{O}` и :math:`\bar{S}` средние наблюдённого и модельного рядов (взвешенные при заданных весах), :math:`w_i` вес. В коде ковариация и дисперсии нормируются на ``n - 1`` (при весах на сумму весов минус 1); при отсутствии весов это совпадает с формулой выше.",
              r":math:`\bar{O}` and :math:`\bar{S}` are the means of the observed and simulated series (weighted when weights are given), :math:`w_i` the weight. In the code the covariance and the variances are normalised by ``n - 1`` (by the sum of weights minus 1 with weights); without weights this coincides with the formula above.")],
    deviation=[("Совпадает с классическим определением. Веса расширяют его до взвешенной корреляции.", "It matches the classical definition. Weights extend it to a weighted correlation.")],
    range="[-1, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 означает точную линейную зависимость с положительным наклоном, -1 с отрицательным. Для постоянного ряда корреляция не определена, результат NaN.",
             "The value 1 means an exact linear relation with positive slope, -1 with negative slope. For a constant series the correlation is undefined and the result is NaN.")],
    interp=[("Общепринятых градаций качества нет. Высокая корреляция не означает точной модели: она допускает любое смещение и любой масштаб (пример выше).",
             "There are no accepted quality ratings. A high correlation does not mean an accurate model: it allows any bias and any scale (the example above).")],
    special=[NAN_STD, ("Постоянный ряд и один элемент дают NaN.", "A constant series and a single element give NaN.")],
    examples=std_examples("pearson_r", extra=pearson_extra),
    hydro=[("Корреляция чувствительна к выбросам и, как все квадратичные метрики, определяется пиками половодья: при резком сезонном ходе она высока почти для любой модели, воспроизводящей сезонность. Автокорреляция суточного стока делает число независимых наблюдений намного меньше длины ряда, поэтому проверка значимости, рассчитанная на независимые наблюдения, к такому ряду неприменима без поправки.",
            "The correlation is sensitive to outliers and, like all quadratic metrics, is set by the flood peaks: with a sharp seasonal cycle it is high for almost any model that reproduces seasonality. Autocorrelation of daily flow makes the number of independent observations much smaller than the length of the series, so a significance test designed for independent observations does not apply to such a series without a correction."),
           ("Дополняйте её метриками объёма и амплитуды: :ref:`metric-pbias`, :ref:`metric-alpha_component`.",
            "Complement it with metrics of volume and amplitude: :ref:`metric-pbias`, :ref:`metric-alpha_component`.")],
    related=["spearman_r", "kendall_tau", "r2", "r_component", "kge_2012"],
    refs=True,
)

# =================================================================================== spearman
def rank_extra(name):
    def run(d):
        d.p(("Ранговые коэффициенты не зависят от монотонного преобразования: утроенный ряд даёт тот же результат, тогда как нелинейное преобразование меняет корреляцию Пирсона:",
             "Rank coefficients do not depend on a monotone transformation: a tripled series gives the same result, whereas a nonlinear transformation changes the Pearson correlation:"))
        d.code(f'''
squared = q_obs ** 2
print(round(float(hm.{name}(q_obs, squared)), 4), round(float(hm.pearson_r(q_obs, squared)), 4))
''')
        d.p(("В примере с половодьем коэффициент заметно ниже корреляции Пирсона, потому что большая часть дней приходится на межень с шумом, и порядок значений там определяется шумом:",
             "In the flood example the coefficient is clearly lower than the Pearson correlation, because most days fall in low flow with noise, and the order of values there is set by the noise:"))
        d.code(f'''
print(round(float(hm.{name}(q_obs, q_sim)), 3), round(float(hm.pearson_r(q_obs, q_sim)), 3))
''')
    return run


SPEARMAN = dict(
    name="spearman_r",
    title=("Ранговая корреляция Спирмена (ρ)", "Spearman rank correlation (ρ)"),
    short=[("ρ это корреляция Пирсона между рангами наблюдённых и модельных значений :footcite:p:`spearman1904`. Она измеряет монотонную связь и не зависит от масштаба и формы связи.",
            "ρ is the Pearson correlation between the ranks of the observed and simulated values :footcite:p:`spearman1904`. It measures a monotone relation and does not depend on the scale or the shape of the relation.")],
    formula=[r"\rho = \frac{\sum_i (R_i - \bar{R})(T_i - \bar{T})}{\sqrt{\sum_i (R_i - \bar{R})^2}\,\sqrt{\sum_i (T_i - \bar{T})^2}}"],
    symbols=[(r":math:`R_i` и :math:`T_i` ранги :math:`O_i` и :math:`S_i`; при совпадающих значениях берётся средний ранг. Расчёт выполняет ``scipy.stats.spearmanr`` отдельно для каждого среза вдоль оси.",
              r":math:`R_i` and :math:`T_i` are the ranks of :math:`O_i` and :math:`S_i`; tied values receive the mean rank. The computation is done by ``scipy.stats.spearmanr`` separately for each slice along the axis.")],
    deviation=[("Совпадает с классическим определением. Веса не поддерживаются: ``sample_weight`` вызывает ``NotImplementedError``. Пары с пропуском удаляются; при менее чем двух парах результат NaN.",
                "It matches the classical definition. Weights are not supported: ``sample_weight`` raises ``NotImplementedError``. Pairs with a gap are dropped; with fewer than two pairs the result is NaN.")],
    range="[-1, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 означает строго одинаковый порядок значений, -1 противоположный. Для постоянного ряда результат NaN.",
             "The value 1 means an identical order of values, -1 the opposite. For a constant series the result is NaN.")],
    interp=[("Общепринятых градаций качества нет. Монотонная связь допускает любое смещение и любую нелинейную деформацию масштаба, поэтому высокий ρ не говорит о точности значений.",
             "There are no accepted quality ratings. A monotone relation allows any bias and any nonlinear deformation of the scale, so a high ρ says nothing about the accuracy of the values.")],
    special=[("С ``nan_policy=\"omit\"`` пары с пропуском удаляются; ``\"propagate\"`` возвращает NaN, ``\"raise\"`` вызывает ``ValueError``. Значение ``inf`` не считается пропуском и получает наибольший ранг, поэтому результат остаётся числом.",
              "With ``nan_policy=\"omit\"`` pairs with a gap are dropped; ``\"propagate\"`` returns NaN, ``\"raise\"`` raises ``ValueError``. An ``inf`` is not treated as a gap and receives the highest rank, so the result stays a number.")],
    examples=std_examples("spearman_r", extra=rank_extra("spearman_r")),
    hydro=[("Ранговая корреляция не замечает систематического занижения пиков и объёма, поэтому её используют для проверки порядка значений (например, ранжирования створов или лет по водности), а не для оценки точности расхода. В рядах суточного стока с длинной меженью ρ определяется порядком шумовых значений межени, как в примере выше.",
            "Rank correlation does not notice a systematic underestimate of peaks or volume, so it is used to check the order of values (for example the ranking of gauges or years by water abundance), not to assess discharge accuracy. In daily flow series with a long low-flow period ρ is set by the order of noisy low-flow values, as in the example above.")],
    related=["kendall_tau", "pearson_r", "kge_2012"],
    refs=True,
)

KENDALL = dict(
    name="kendall_tau",
    title=("Ранговая корреляция Кендалла (τ)", "Kendall rank correlation (τ)"),
    short=[("τ оценивает согласованность порядка: долю пар наблюдений, в которых наблюдённый и модельный ряды упорядочены одинаково, за вычетом доли пар, упорядоченных противоположно :footcite:p:`kendall1938`.",
            "τ assesses agreement of order: the share of pairs of observations in which the observed and simulated series are ordered the same way minus the share ordered oppositely :footcite:p:`kendall1938`.")],
    formula=[r"\tau = \frac{n_c - n_d}{\sqrt{(n_0 - n_1)(n_0 - n_2)}}"],
    symbols=[(r":math:`n_c` и :math:`n_d` числа согласованных и несогласованных пар, :math:`n_0 = n(n-1)/2`, :math:`n_1` и :math:`n_2` поправки на совпадающие значения в каждом ряду. Это вариант τ-b; расчёт выполняет ``scipy.stats.kendalltau`` с умолчанием ``variant=\"b\"`` для каждого среза вдоль оси.",
              r":math:`n_c` and :math:`n_d` are the numbers of concordant and discordant pairs, :math:`n_0 = n(n-1)/2`, :math:`n_1` and :math:`n_2` the corrections for tied values in each series. This is the τ-b variant; the computation is done by ``scipy.stats.kendalltau`` with the default ``variant=\"b\"`` for each slice along the axis.")],
    deviation=[("Совпадает с классическим определением τ-b. Веса не поддерживаются. Пары с пропуском удаляются; при менее чем двух парах результат NaN.",
                "It matches the classical τ-b. Weights are not supported. Pairs with a gap are dropped; with fewer than two pairs the result is NaN.")],
    range="[-1, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 означает полностью согласованный порядок, -1 противоположный. Значения τ обычно меньше значений ρ для тех же данных, потому что шкалы различаются; прямо сравнивать их нельзя. Для постоянного ряда результат NaN.",
             "The value 1 means a fully concordant order, -1 the opposite. τ is usually smaller than ρ for the same data because the scales differ; they cannot be compared directly. For a constant series the result is NaN.")],
    interp=[("Общепринятых градаций качества нет. Для интерпретации используется вероятностный смысл: :math:`(1+\\tau)/2` при отсутствии совпадающих значений равно вероятности того, что случайно взятая пара упорядочена в обоих рядах одинаково.",
             "There are no accepted quality ratings. The probabilistic reading applies: with no tied values :math:`(1+\\tau)/2` equals the probability that a randomly chosen pair is ordered the same way in both series.")],
    special=[("С ``nan_policy=\"omit\"`` пары с пропуском удаляются; ``\"propagate\"`` возвращает NaN, ``\"raise\"`` вызывает ``ValueError``. Значение ``inf`` получает наибольший ранг.",
              "With ``nan_policy=\"omit\"`` pairs with a gap are dropped; ``\"propagate\"`` returns NaN, ``\"raise\"`` raises ``ValueError``. An ``inf`` receives the highest rank.")],
    examples=std_examples("kendall_tau", extra=rank_extra("kendall_tau")),
    hydro=[("Как и :ref:`metric-spearman_r`, τ оценивает порядок, а не величину расхода. Она менее чувствительна к отдельным выбросам, чем ρ, но ряд суточного стока с множеством близких значений межени даёт много поправок на совпадения.",
            "Like :ref:`metric-spearman_r`, τ assesses order, not discharge magnitude. It is less sensitive to single outliers than ρ, but a daily flow series with many close low-flow values produces many tie corrections.")],
    related=["spearman_r", "pearson_r"],
    refs=True,
)

# =================================================================================== willmott
def willmott_extra(d):
    d.p(("Диапазон индекса сжат у верхней границы: модель с завышением всех расходов в 1,5 раза получает d заметно выше, чем ``NSE``.",
         "The range of the index is compressed towards the upper bound: a model that overestimates all discharge by a factor of 1.5 gets a d noticeably higher than its ``NSE``."))
    d.code('''
q_high = 1.5 * q_obs
print(round(float(hm.willmott_d(q_obs, q_high)), 3), round(float(hm.nse(q_obs, q_high)), 3))
''')


WILLMOTT = dict(
    name="willmott_d",
    title=("Индекс согласия Уилмотта (d)", "Willmott index of agreement (d)"),
    short=[("d сравнивает сумму квадратов ошибок с «потенциальной ошибкой», суммой квадратов отклонений обоих рядов от среднего наблюдений :footcite:p:`willmott1981`. Значение лежит от 0 до 1.",
            "d compares the sum of squared errors with the potential error, the sum of squared deviations of both series from the observed mean :footcite:p:`willmott1981`. The value lies between 0 and 1.")],
    formula=[r"d = 1 - \frac{\sum_{i} w_i\,\left(O_i - S_i\right)^2}{\sum_{i} w_i\,\left(\left|S_i - \bar{O}\right| + \left|O_i - \bar{O}\right|\right)^2}"],
    symbols=[(r":math:`\bar{O}` среднее наблюдений (взвешенное при заданных весах), :math:`w_i` вес. Суммирование идёт по оси ``axis``.",
              r":math:`\bar{O}` is the mean of the observations (weighted when weights are given), :math:`w_i` the weight. The sum runs along ``axis``.")],
    deviation=[("Реализован исходный индекс Уилмотта 1981 г. Модифицированные индексы и уточнённый индекс 2012 г. :footcite:p:`willmott2012` в библиотеке не реализованы.",
                "The original index of Willmott (1981) is implemented. The modified indices and the refined index of 2012 :footcite:p:`willmott2012` are not implemented in the library.")],
    range="[0, 1]", optimum="1", dir="up",
    bounds=[("Значение 1 означает полное совпадение, 0 отсутствие согласия (например, модельный ряд, равный среднему наблюдений). Если знаменатель равен нулю (все значения равны среднему), результат NaN.",
             "The value 1 means a perfect match, 0 no agreement (for example a simulated series equal to the observed mean). If the denominator is zero (all values equal the mean) the result is NaN.")],
    interp=[("Общепринятых градаций для d в прочитанных источниках нет. Из-за квадратов в знаменателе d принимает высокие значения даже при заметных ошибках (пример выше), поэтому его сопоставляют с другими метриками.",
             "There are no accepted ratings for d in the sources that were read. Because of the squares in the denominator d takes high values even with noticeable errors (the example above), so it is compared with other metrics.")],
    special=[NAN_STD, ("Один элемент даёт 0, ряд из нулей NaN.", "A single element gives 0, an all-zero series NaN.")],
    examples=std_examples("willmott_d", extra=willmott_extra),
    hydro=[("Индекс, как и NSE, определяется крупными расходами, но ограничен сверху и снизу, поэтому лучше различает слабые модели, чем сильные: разница между 0,95 и 0,98 соответствует заметно разным ошибкам. Для сравнения моделей используйте его вместе с :ref:`metric-nse` и :ref:`metric-pbias`.",
            "Like NSE the index is dominated by high flows, but it is bounded above and below, so it separates weak models better than strong ones: the difference between 0.95 and 0.98 corresponds to noticeably different errors. When comparing models use it together with :ref:`metric-nse` and :ref:`metric-pbias`.")],
    related=["nse", "r2", "pearson_r", "ve"],
    refs=True,
)

FAMILY2 = {s["name"]: s for s in (MAE, MSE, RMSE, NRMSE, BIAS, PBIAS, R2, PEARSON, SPEARMAN, KENDALL, WILLMOTT)}
