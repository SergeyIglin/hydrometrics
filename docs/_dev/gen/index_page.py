"""The metrics index page: a summary table per family and a hidden toctree of all pages."""
from lib import Doc
from metricpage import DIR

FAMILIES = [
    (("Ошибки и корреляция", "Errors and correlation"), [
        ("mae", ("средняя абсолютная ошибка в единицах величины", "mean absolute error in the units of the variable")),
        ("mse", ("средний квадрат ошибки", "mean squared error")),
        ("rmse", ("корень из среднего квадрата ошибки", "root of the mean squared error")),
        ("nrmse", ("RMSE, нормированная на среднее, СКО, размах или IQR", "RMSE normalised by the mean, standard deviation, range or IQR")),
        ("bias", ("среднее значение ошибки со знаком", "mean signed error")),
        ("pbias", ("суммарное смещение в процентах от объёма наблюдений", "total bias as a percentage of the observed volume")),
        ("pearson_r", ("линейная корреляция рядов", "linear correlation of the series")),
        ("spearman_r", ("ранговая корреляция Спирмена", "Spearman rank correlation")),
        ("kendall_tau", ("ранговая корреляция Кендалла", "Kendall rank correlation")),
        ("r2", ("доля объяснённой дисперсии (1 − SSres/SStot)", "share of explained variance (1 − SSres/SStot)")),
        ("willmott_d", ("индекс согласия Уилмотта 1981 г.", "Willmott index of agreement (1981)")),
    ]),
    (("Критерии эффективности, производные от NSE", "Efficiency criteria derived from NSE"), [
        ("nse", ("критерий Нэша–Сатклиффа", "Nash–Sutcliffe efficiency")),
        ("log_nse", ("NSE логарифмов расходов, для межени", "NSE of log-transformed discharge, for low flow")),
        ("modified_nse", ("NSE с модулями вместо квадратов", "NSE with absolute values instead of squares")),
        ("nse_bounded", ("NSE, сжатая в интервал (−1, 1]", "NSE compressed into the interval (−1, 1]")),
        ("nse_variance_weighted", ("NSE по створам с весами-дисперсиями", "multi-gauge NSE weighted by variances")),
        ("regNSE", ("NSE годовых кривых обеспеченности относительно режима", "NSE of annual duration curves relative to the regime")),
        ("rsr", ("отношение RMSE к стандартному отклонению наблюдений", "ratio of RMSE to the standard deviation of the observations")),
        ("ve", ("объёмная эффективность", "volumetric efficiency")),
    ]),
    (("Критерий Клинга–Гупты и его компоненты", "Kling–Gupta efficiency and its components"), [
        ("kge_2009", ("KGE по Gupta et al. (2009): r, α, β", "KGE after Gupta et al. (2009): r, α, β")),
        ("kge_2012", ("KGE′ по Kling et al. (2012): r, β, γ", "KGE′ after Kling et al. (2012): r, β, γ")),
        ("kge_components", ("словарь компонент r, α, β, γ", "dictionary of the components r, α, β, γ")),
        ("r_component", ("компонента r: корреляция", "component r: correlation")),
        ("alpha_component", ("компонента α: отношение стандартных отклонений", "component α: ratio of standard deviations")),
        ("beta_component", ("компонента β: отношение средних", "component β: ratio of means")),
        ("gamma_component", ("компонента γ: отношение коэффициентов вариации", "component γ: ratio of coefficients of variation")),
    ]),
    (("Оценка гидрологических прогнозов по допустимой погрешности", "Assessment of hydrological forecasts against a permissible error"), [
        ("ssigma", ("отношение S/σ", "the S/σ ratio")),
        ("ssigma_delta", ("S/σ по группам прогнозов", "S/σ by forecast group")),
        ("forecast_verification", ("доля прогнозов с ошибкой меньше 0,674σ", "share of forecasts with an error below 0.674σ")),
        ("forecast_verification_delta", ("то же с σ ошибок внутри группы", "the same with σ of the errors within a group")),
    ]),
    (("Вероятностные прогнозы", "Probabilistic forecasts"), [
        ("crps", ("непрерывная ранжированная вероятностная оценка", "continuous ranked probability score")),
        ("weighted_crps", ("CRPS, взвешенная функцией от наблюдения", "CRPS weighted by a function of the observation")),
        ("crpss", ("индекс мастерства CRPS относительно опоры", "CRPS skill score against a reference")),
        ("brier_score", ("оценка Брайера вероятности события", "Brier score of an event probability")),
        ("reliability", ("надёжность: член разложения оценки Брайера", "reliability: a term of the Brier score decomposition")),
        ("sharpness", ("чёткость: дисперсия вероятностей", "sharpness: variance of the probabilities")),
    ]),
    (("Бинарные события", "Binary events"), [
        ("accuracy", ("доля верных меток", "fraction of correct labels")),
        ("precision", ("доля оправдавшихся прогнозов события", "share of event forecasts that proved right")),
        ("recall", ("доля обнаруженных событий", "share of events that were detected")),
        ("f1_score", ("гармоническое среднее precision и recall", "harmonic mean of precision and recall")),
        ("roc_auc", ("площадь под ROC-кривой", "area under the ROC curve")),
        ("pr_auc", ("средняя точность, площадь под кривой PR", "average precision, area under the PR curve")),
        ("edi", ("индекс экстремальной зависимости для редких событий", "extremal dependence index for rare events")),
        ("sedi", ("симметричный вариант EDI", "symmetric version of EDI")),
    ]),
]


def index_page(specs: dict) -> Doc:
    listed = [n for _, items in FAMILIES for n, _ in items]
    missing = set(specs) - set(listed)
    if missing or len(listed) != len(set(listed)):
        raise ValueError(f"index families do not match the pages: {missing}")
    d = Doc("metrics/index.rst", label="metrics-index")
    d.title(("Метрики", "Metrics"))
    d.p(("Сводные таблицы по семействам метрик. Диапазон и оптимум взяты из метаданных функций, направление указывает, в какую сторону значение улучшается. Каждая страница построена по одному плану: определение, формула, диапазон, интерпретация, параметры, возвращаемое значение, особые случаи, бэкенды, примеры, особенности применения в гидрологии, связанные метрики, литература.",
         "Summary tables by family of metrics. The range and the optimum come from the function metadata, the direction shows which way the value improves. Every page follows one outline: definition, formula, range, interpretation, parameters, return value, special cases, backends, examples, notes on hydrological use, related metrics, references."))
    for (title, items) in FAMILIES:
        d.h(title)
        rows = []
        for name, purpose in items:
            s = specs[name]
            rows.append((f":ref:`{name} <metric-{name}>`", s["range"], s["optimum"], DIR[s["dir"]], purpose))
        d.table((("Метрика", "Metric"), ("Диапазон", "Range"), ("Оптимум", "Optimum"), ("Направление", "Direction"), ("Назначение", "Purpose")),
                rows, widths=[20, 14, 9, 17, 40])
    d.raw(".. toctree::\n   :hidden:\n\n" + "".join(f"   {n}\n" for n in listed))
    return d
