"""The front page: what the library is and the three entry points."""
from lib import Doc, tr


def toctree(caption, entries):
    return ".. toctree::\n   :maxdepth: 1\n   :caption: " + tr(caption) + "\n\n" + "".join(f"   {e}\n" for e in entries)


def front_page() -> Doc:
    d = Doc("index.rst")
    d.title(("hydrometrics", "hydrometrics"))
    d.p(("Библиотека на Python для оценки гидрологических моделей и прогнозов: критерии эффективности стока, ошибки и корреляции, оценки ансамблевых и вероятностных прогнозов, показатели прогнозов событий. Одинаковый вызов работает с массивами numpy, таблицами pandas и polars и объектами xarray.",
         "A Python library for evaluating hydrological models and forecasts: efficiency criteria for runoff, errors and correlations, scores for ensemble and probabilistic forecasts, and verification scores for event forecasts. The same call works with numpy arrays, pandas and polars tables and xarray objects."))
    d.p(("Для каждой метрики есть страница с формулой, диапазоном, интерпретацией, особыми случаями и примером, который выполняется при сборке документации. Начните с :doc:`user_guide/quickstart`; выбор метрики описан в :doc:`user_guide/choosing`.",
         "Every metric has a page with the formula, the range, the interpretation, the special cases and an example that runs when the documentation is built. Start with :doc:`user_guide/quickstart`; the choice of a metric is covered in :doc:`user_guide/choosing`."))
    d.raw(toctree(("Руководство пользователя", "User guide"),
                  ["user_guide/quickstart", "user_guide/concept", "user_guide/input_data", "user_guide/backends", "user_guide/missing_values",
                   "user_guide/axes", "user_guide/weights", "user_guide/grouping", "user_guide/results", "user_guide/choosing",
                   "user_guide/pitfalls", "user_guide/limits", "user_guide/extending", "user_guide/known_limits", "user_guide/glossary"]))
    d.raw(toctree(("Справочник метрик", "Metric reference"), ["metrics/index"]))
    d.raw(toctree(("Справочник API", "API reference"), ["api/index"]))
    return d
