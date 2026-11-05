"""Glossary: one term, one concept, in both languages. Writes the user-guide page and GLOSSARY.md."""
from lib import DOCS, TM, Doc, tr

TERMS = [
    # (ru, en, short explanation ru, en)
    ("расход воды", "discharge", ("объём воды, проходящий через створ за единицу времени, м³/с", "volume of water passing a gauge per unit time, m³/s")),
    ("сток", "runoff, streamflow", ("вода, стекающая с водосбора; в тексте «сток» относится к ряду расходов или к объёму", "water draining from a catchment; in the text it refers to a series of discharge or to a volume")),
    ("гидрограф", "hydrograph", ("график изменения расхода воды во времени", "a plot of discharge over time")),
    ("створ", "gauge, station", ("место измерения расхода на реке", "the place on a river where discharge is measured")),
    ("водосбор, бассейн", "catchment, basin", ("территория, с которой вода стекает к створу", "the area from which water drains to a gauge")),
    ("половодье", "spring flood", ("ежегодное длительное повышение расходов в одну и ту же фазу года", "a yearly prolonged rise of discharge in the same phase of the year")),
    ("паводок", "flood (event)", ("кратковременный подъём расходов, не связанный с сезоном", "a short rise of discharge not tied to the season")),
    ("пик", "flood peak", ("наибольший расход половодья или паводка", "the largest discharge of a flood")),
    ("межень", "low flow", ("период наименьших расходов", "the period of smallest discharge")),
    ("водный год", "water year", ("год, который в примерах начинается 1 октября и называется по году окончания", "a year that starts on 1 October in the examples and is named after its final year")),
    ("обеспеченность", "exceedance probability", ("вероятность превышения расхода", "the probability that a discharge is exceeded")),
    ("кривая обеспеченности", "flow duration curve", ("расходы, упорядоченные по убыванию", "discharges ordered from largest to smallest")),
    ("невязка, ошибка", "residual, error", ("разность модельного и наблюдённого значения", "the difference between the simulated and the observed value")),
    ("ряд наблюдений", "observed series, record", ("измеренные значения во времени", "measured values in time")),
    ("модельный ряд", "simulated series", ("значения, рассчитанные моделью", "values computed by a model")),
    ("калибровка", "calibration", ("подбор параметров модели; термин «валидация» в тексте не используется", "tuning of model parameters; the term validation is not used in the text")),
    ("верификация", "verification", ("проверка модели или прогноза на данных, не участвовавших в калибровке", "checking a model or forecast against data not used in calibration")),
    ("контрольный период", "verification period", ("период, на котором выполняется верификация", "the period on which verification is carried out")),
    ("прогноз", "forecast", ("значение величины, заданное до наблюдения", "a value of a quantity given before it is observed")),
    ("заблаговременность", "lead time", ("интервал между выпуском прогноза и прогнозируемым моментом", "the interval between the issue of a forecast and the forecast time")),
    ("ансамблевый прогноз", "ensemble forecast", ("набор прогнозов (членов ансамбля) для одного момента", "a set of forecasts (ensemble members) for one time")),
    ("опорный прогноз", "reference forecast, benchmark", ("прогноз, с которым сравнивается проверяемый", "the forecast against which the verified one is compared")),
    ("допустимая погрешность", "permissible error", ("предел ошибки, внутри которого прогноз считается оправдавшимся", "the error limit within which a forecast counts as verified")),
    ("попадание, ложная тревога, пропуск", "hit, false alarm, miss", ("элементы таблицы сопряжённости прогноза события", "elements of the contingency table of an event forecast")),
    ("метрика", "metric", ("общий термин для любого показателя качества; названия вроде «критерий Нэша–Сатклиффа» даны по литературе", "the general term for any quality measure; names such as the Nash–Sutcliffe efficiency follow the literature")),
    ("оценка", "score", ("значение, выдаваемое оценочной функцией, например оценка Брайера", "a value given by a scoring function, for example the Brier score")),
    ("индекс мастерства", "skill score", ("относительное улучшение по сравнению с опорным прогнозом", "relative improvement over a reference forecast")),
    ("оптимум", "optimum", ("значение метрики у безошибочной модели", "the value of a metric for an error-free model")),
    ("надёжность", "reliability", ("совпадение прогнозных вероятностей с частотами событий", "agreement of forecast probabilities with event frequencies")),
    ("чёткость", "sharpness", ("концентрация прогнозных вероятностей у крайних значений", "concentration of forecast probabilities at the extremes")),
    ("бэкенд", "backend", ("реализация метрики для одного типа данных: numpy, pandas, polars, xarray", "an implementation of a metric for one data type: numpy, pandas, polars, xarray")),
    ("диспетчеризация", "dispatch", ("выбор бэкенда по типу входа", "selection of the backend from the type of the input")),
    ("ядро", "kernel", ("функция расчёта на numpy-массивах, общая для всех бэкендов", "the computing function on numpy arrays shared by all backends")),
    ("ось", "axis", ("измерение массива, вдоль которого считается метрика", "the array dimension along which a metric is computed")),
    ("пропуск (в данных)", "missing value, gap", ("значение NaN в ряду", "a NaN value in a series")),
    ("политика обработки пропусков", "missing-value policy", ("аргумент ``nan_policy``: omit, propagate, raise", "the argument ``nan_policy``: omit, propagate, raise")),
    ("вес", "weight", ("множитель вклада пары в сумму и среднее", "a factor for the contribution of a pair to sums and means")),
    ("свёртка", "reduction", ("превращение массива значений в одно число или сохранение массива (``reduction``)", "turning an array of values into one number or keeping the array (``reduction``)")),
    ("группировка", "grouping", ("раздельный расчёт метрики по группам значений", "computing a metric separately for groups of values")),
]


def glossary_page() -> Doc:
    d = Doc("user_guide/glossary.rst", label="glossary")
    d.title(("Глоссарий", "Glossary"))
    d.p(("Один термин означает одно понятие во всём тексте и в обоих языках. Таблица фиксирует соответствия русских и английских терминов.",
         "One term means one concept throughout the text and in both languages. The table fixes the correspondence of Russian and English terms."))
    # The Russian column keeps the Russian term in the English build, so it maps to itself.
    rows = [".. list-table::", "   :header-rows: 1", "   :class: hm-table", "   :widths: 26 26 48", ""]
    for i, cell in enumerate((("Русский термин", "Russian term"), ("Английский термин", "English term"), ("Смысл", "Meaning"))):
        rows.append(("   * - " if i == 0 else "     - ") + tr(cell))
    for ru, en, gloss in TERMS:
        TM[ru] = ru
        rows += ["   * - " + ru, "     - " + en, "     - " + tr(gloss)]
    d.raw("\n".join(rows))
    return d


def write_markdown():
    lines = ["# Глоссарий (ru ↔ en)", "",
             "Один термин означает одно понятие во всём тексте и в обоих языках. Страница документации `user_guide/glossary`",
             "строится из того же списка (`docs/_dev/gen/glossary_page.py`).", "",
             "| Русский | English | Смысл |", "|---|---|---|"]
    for ru, en, (g_ru, _) in TERMS:
        lines.append(f"| {ru} | {en} | {g_ru} |")
    (DOCS / "_dev" / "GLOSSARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
