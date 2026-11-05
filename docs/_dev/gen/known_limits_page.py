"""The user-guide page "Known limitations", written from docs/_dev/KNOWN_ISSUES.md without links to internal files."""
from lib import Doc

LIBRARY = [
    (("``edi`` и ``sedi``: значения в вырожденных случаях", "``edi`` and ``sedi``: values in degenerate cases"),
     ("Единица при ``H = 1``, ``F = 0`` задана по решению автора. При ``H = 1``, ``0 < F < 1`` EDI равен 1, а SEDI NaN; остальные вырожденные случаи NaN. Пределы по тексту первоисточника не проверены.",
      "The value 1 for ``H = 1``, ``F = 0`` is the decision of the library author. For ``H = 1``, ``0 < F < 1`` EDI is 1 and SEDI is NaN; the other degenerate cases are NaN. The limits were not checked against the text of the original source.")),
    (("``regNSE``: календарный год", "``regNSE``: calendar year"),
     ("Ранжирование идёт по календарному, а не водному году; неполный год сравнивается только с первыми рангами кривой режима. Ряд нужно готовить из полных календарных лет.",
      "Ranking runs within a calendar year, not a water year; an incomplete year is compared only with the first ranks of the regime curve. Prepare the record from whole calendar years.")),
    (("``ssigma_delta`` и ``forecast_verification_delta``", "``ssigma_delta`` and ``forecast_verification_delta``"),
     ("Расхождение с σ_Δ источника оставлено по решению автора и описано в докстрингах и на страницах метрик. Градации качества для S/σ не приводятся, потому что текст источника не читался.",
      "The difference from the σ_Δ of the source was kept by the decision of the author and is described in the docstrings and on the metric pages. No rating scale is given for S/σ because the text of the source was not read.")),
    (("``sharpness``, ``forecast_verification``, ``nse_variance_weighted``", "``sharpness``, ``forecast_verification``, ``nse_variance_weighted``"),
     ("``sharpness`` не проверяет диапазон ``sim`` и для постоянного прогноза даёт значение от 0 до порядка 1e-32. ``forecast_verification`` при постоянных ``obs`` даёт 0, а не NaN, и при ``inf`` в ``obs`` получает бесконечный порог. ``nse_variance_weighted`` исключает ``inf`` как пропуск, остальные метрики нет.",
      "``sharpness`` does not check the range of ``sim`` and gives a value from 0 to the order of 1e-32 for a constant forecast. ``forecast_verification`` gives 0, not NaN, for constant ``obs`` and gets an infinite threshold with ``inf`` in ``obs``. ``nse_variance_weighted`` excludes ``inf`` as a gap, the other metrics do not.")),
    (("``nrmse`` и ``r2``", "``nrmse`` and ``r2``"),
     ("Нормировки ``range`` и ``iqr`` в ``nrmse`` не учитывают веса. ``r2`` при всех нулевых весах даёт 1, тогда как ``nse`` даёт NaN.",
      "The ``range`` and ``iqr`` normalisations of ``nrmse`` ignore the weights. ``r2`` gives 1 for all-zero weights whereas ``nse`` gives NaN.")),
    (("``crpss`` и ``weighted_crps``", "``crpss`` and ``weighted_crps``"),
     ("По умолчанию опорой ``crpss`` служит среднее той же выборки, то есть оценка получена внутри выборки; при выраженной сезонности она завышает мастерство. Параметра ``fair`` у этих функций нет (решение автора).",
      "By default the reference of ``crpss`` is the mean of the same sample, so the score is in-sample; with a pronounced seasonal cycle it overstates skill. These functions have no ``fair`` parameter (decision of the author).")),
    (("Допуск нулевой дисперсии", "Tolerance for zero variance"),
     ("Относительный допуск ``ZERO_VARIANCE_RTOL = 1e-24`` фиксирован (решение автора); для рядов с очень малой изменчивостью он может принять реальную дисперсию за нулевую.",
      "The relative tolerance ``ZERO_VARIANCE_RTOL = 1e-24`` is fixed (decision of the author); for series with very small variability it may take a real variance for zero.")),
    (("Выравнивание рядов", "Alignment of series"),
     ("Сдвиг рядов обнаруживается только у двух объектов pandas или двух ``DataArray`` с метками. Для numpy, polars и входов разных типов пары идут по позиции, ``align=\"inner\"`` для них недопустим. Дополнительные массивы (``dates``, ``gauge``, ``ref_date``) и веса при ``align=\"inner\"`` не выравниваются, кроме весов с метками pandas или xarray.",
      "A shift of the series is detected only for two pandas objects or two labelled ``DataArray`` objects. For numpy, polars and inputs of different kinds the pairs go by position, and ``align=\"inner\"`` is not allowed. Additional arrays (``dates``, ``gauge``, ``ref_date``) are not aligned under ``align=\"inner\"``, except weights with pandas or xarray labels.")),
    (("Группировка", "Grouping"),
     ("``compute_grouped`` не режет дополнительные массивы и веса, работает только с метриками, возвращающими число, не читает объекты и имена столбцов polars, пропуск в группирующей переменной считает ошибкой; ``to_xarray`` работает с одной группирующей переменной. Во всех этих случаях вызывается исключение с подсказкой, см. :doc:`grouping`.",
      "``compute_grouped`` does not slice additional arrays and weights, works only with metrics that return a number, does not read polars objects or column names, treats a missing value in a grouping variable as an error; ``to_xarray`` works with one grouping variable. In all these cases an exception with a hint is raised, see :doc:`grouping`.")),
    (("Типы входов", "Input types"),
     ("``xarray.Dataset`` и ``polars.LazyFrame`` не поддерживаются.", "``xarray.Dataset`` and ``polars.LazyFrame`` are not supported.")),
    (("Результат", "Result"),
     ("``MetricResult.to_dict`` не годится для прямой записи в JSON: в границах есть ``-inf``, в параметрах массивы.",
      "``MetricResult.to_dict`` is not suitable for writing straight to JSON: the bounds hold ``-inf`` and the parameters arrays.")),
    (("Скорость", "Speed"),
     ("Ранговые метрики, ``roc_auc`` и ``pr_auc`` считают срезы по оси в цикле и медленнее остальных на больших массивах. Измерений скорости не проводилось.",
      "The rank metrics, ``roc_auc`` and ``pr_auc`` compute slices along an axis in a loop and are slower than the others on large arrays. No speed measurements were made.")),
]

SOURCES = [
    (("Георгиевский и Шаночкин (2007)", "Georgievsky and Shanochkin (2007)"),
     ("Источник ``ssigma``, ``ssigma_delta``, ``forecast_verification``, ``forecast_verification_delta``; текст не читался, записи в списке литературы нет DOI, издание и объём не проверены.",
      "The source of ``ssigma``, ``ssigma_delta``, ``forecast_verification``, ``forecast_verification_delta``; the text was not read, the reference list entry has no DOI and the edition and page count were not checked.")),
    (("Формулы по реализации", "Formulas taken from the implementation"),
     ("Формулы ``log_nse``, ``modified_nse``, ``ve``, ``edi``, ``sedi`` и ``regNSE`` приведены по коду; тексты Krause et al., Criss и Winston, Ferro и Stephenson, Гарцмана (2023) для них не сверялись.",
      "The formulas of ``log_nse``, ``modified_nse``, ``ve``, ``edi``, ``sedi`` and ``regNSE`` are given from the code; the texts of Krause et al., Criss and Winston, Ferro and Stephenson and Gartsman (2023) were not compared for them.")),
    (("Moriasi et al. (2015)", "Moriasi et al. (2015)"),
     ("Прочитана только аннотация; таблица критериев недоступна.", "Only the abstract was read; the table of criteria was not available.")),
    (("``nse_bounded``", "``nse_bounded``"),
     ("Источник формы ``NSE / (2 - NSE)`` не найден. В литературе имя nNSE используется для формы ``1 / (2 - NSE)``; источник этой формы тоже не подтверждён.",
      "No source was found for the form ``NSE / (2 - NSE)``. In the literature the name nNSE is used for the form ``1 / (2 - NSE)``; the source of that form is not confirmed either.")),
    (("Работы, прочитанные не полностью", "Works that were not read in full"),
     ("Hersbach (2000), Willmott и Matsuura (2005), Brier (1950), Murphy (1973), Bröcker и Smith (2007), Gneiting и Ranjan (2011), Gneiting и Raftery (2007), Ferro (2014): подтверждены существование, авторы, год и журнал.",
      "Hersbach (2000), Willmott and Matsuura (2005), Brier (1950), Murphy (1973), Bröcker and Smith (2007), Gneiting and Ranjan (2011), Gneiting and Raftery (2007), Ferro (2014): the existence, authors, year and journal were confirmed.")),
]


def known_limits_page() -> Doc:
    d = Doc("user_guide/known_limits.rst", label="known-limits")
    d.title(("Известные ограничения", "Known limitations"))
    d.p(("Перечень того, что библиотека делает не так, как можно ожидать, и того, что в тексте не подтверждено. Каждый пункт описан также на странице соответствующей метрики или в разделе руководства.",
         "A list of what the library does differently from what one might expect and of what is not confirmed in the text. Each item is also described on the page of the metric or in the section of the guide concerned."))
    d.h(("Библиотека", "The library"))
    d.table((("Тема", "Topic"), ("Ограничение", "Limitation")), LIBRARY, widths=[28, 72])
    d.h(("Источники", "Sources"))
    d.table((("Источник", "Source"), ("Что не подтверждено", "What is not confirmed")), SOURCES, widths=[28, 72])
    return d
