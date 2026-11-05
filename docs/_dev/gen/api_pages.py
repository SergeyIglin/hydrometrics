"""API reference: the index, the metrics, the core objects and a note on the backends."""
from lib import Doc, tr

from index_page import FAMILIES


def autosummary(names):
    return ".. autosummary::\n   :toctree: generated\n\n" + "".join(f"   {n}\n" for n in names)


def api_index() -> Doc:
    d = Doc("api/index.rst", label="api-index")
    d.title(("Справочник API", "API reference"))
    d.p(("Справочник построен автоматически из докстрингов. Определения, формулы, интерпретация и примеры находятся на страницах метрик; здесь только сигнатуры и описание параметров, поэтому тексты не дублируются.",
         "The reference is built automatically from docstrings. Definitions, formulas, interpretation and examples are on the metric pages; here are only signatures and parameter descriptions, so the texts are not duplicated."))
    d.p(("Докстринги написаны на английском и не переводятся: русская версия документации показывает их на английском языке.",
         "The docstrings are written in English and are not translated: the Russian version of the documentation shows them in English."))
    d.ul([("Метрики: :doc:`metrics`", "Metrics: :doc:`metrics`"),
          ("Результаты, группировка, декоратор метрики и реестр: :doc:`core`", "Results, grouping, the metric decorator and the registry: :doc:`core`"),
          ("Бэкенды: :doc:`backends`", "Backends: :doc:`backends`"),
          ("Функции режимных кривых и реестр: :doc:`helpers`", "Functions for regime curves and the registry: :doc:`helpers`")])
    d.raw(".. toctree::\n   :hidden:\n\n   metrics\n   core\n   backends\n   helpers\n")
    return d


def api_metrics() -> Doc:
    d = Doc("api/metrics.rst", label="api-metrics")
    d.title(("Метрики", "Metrics"))
    for title, items in FAMILIES:
        d.h(title)
        d.raw(autosummary([f"hydrometrics.{n}" for n, _ in items]))
    return d


def api_core() -> Doc:
    d = Doc("api/core.rst", label="api-core")
    d.title(("Результаты, группировка и ядро", "Results, grouping and the core"))
    d.h(("Результаты", "Results"))
    d.raw(autosummary(["hydrometrics.MetricResult", "hydrometrics.GroupedResult", "hydrometrics.compute_grouped"]))
    d.h(("Создание метрик", "Defining metrics"))
    d.raw(autosummary(["hydrometrics.core.base.metric", "hydrometrics.core.base.MetricFunction"]))
    d.h(("Проверка входных данных", "Input validation"))
    d.raw(autosummary(["hydrometrics.validate_inputs"]))
    return d


def api_backends() -> Doc:
    d = Doc("api/backends.rst", label="api-backends")
    d.title(("Бэкенды", "Backends"))
    d.p(("Модули ``hydrometrics.backends.numpy``, ``hydrometrics.backends.pandas``, ``hydrometrics.backends.polars`` и ``hydrometrics.backends.xarray`` не предназначены для прямого вызова. Модуль numpy содержит ядра расчёта (функции с префиксом ``_``), остальные модули переводят входы в массивы numpy и упаковывают результат. Пользователь вызывает функции верхнего уровня ``hydrometrics.<имя метрики>``, диспетчер сам выбирает бэкенд (см. :doc:`/user_guide/backends`).",
         "The modules ``hydrometrics.backends.numpy``, ``hydrometrics.backends.pandas``, ``hydrometrics.backends.polars`` and ``hydrometrics.backends.xarray`` are not meant to be called directly. The numpy module holds the computing kernels (functions with the prefix ``_``); the other modules convert inputs to numpy arrays and pack the result. A user calls the top-level functions ``hydrometrics.<metric name>``, and the dispatcher selects the backend itself (see :doc:`/user_guide/backends`)."))
    d.p(("Из модуля numpy публичны две функции для режимных кривых: :func:`~hydrometrics.mean_annual_hydrograph` и :func:`~hydrometrics.mean_annual_hydrograph_duration_curve` (:doc:`helpers`). Ядра метрик отдельно не документируются: их описание это определение на странице метрики.",
         "Two functions for regime curves are public in the numpy module: :func:`~hydrometrics.mean_annual_hydrograph` and :func:`~hydrometrics.mean_annual_hydrograph_duration_curve` (:doc:`helpers`). The metric kernels are not documented separately: their description is the definition on the metric page."))
    return d


def all_pages():
    return [api_index(), api_metrics(), api_core(), api_backends()]
