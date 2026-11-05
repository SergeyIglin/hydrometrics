"""Template of a metric page. Sections 8-10 are measured by running the library."""
from __future__ import annotations

import warnings

import numpy as np

from lib import Doc, fmt

import hydrometrics as hm
import inventory_probe as probe

SETUP = (
'''
import numpy as np
import hydrometrics as hm

rng = np.random.default_rng(42)
dates = np.arange("2010-10-01", "2013-10-01", dtype="datetime64[D]")
doy = (dates - dates.astype("datetime64[Y]")).astype(int)
# Половодье в конце апреля поверх зимней и летней межени, м³/с
q_obs = 12 + 240 * np.exp(-(((doy - 118) / 16.0) ** 2)) + rng.gamma(2.0, 2.5, doy.size)
# Модель запаздывает на двое суток и срезает пик
q_sim = np.clip(0.88 * np.roll(q_obs, 2) + 3 + rng.normal(0, 5, doy.size), 0.1, None)
''',
'''
import numpy as np
import hydrometrics as hm

rng = np.random.default_rng(42)
dates = np.arange("2010-10-01", "2013-10-01", dtype="datetime64[D]")
doy = (dates - dates.astype("datetime64[Y]")).astype(int)
# Spring flood in late April on top of winter and summer low flow, m³/s
q_obs = 12 + 240 * np.exp(-(((doy - 118) / 16.0) ** 2)) + rng.gamma(2.0, 2.5, doy.size)
# The model lags by two days and clips the peak
q_sim = np.clip(0.88 * np.roll(q_obs, 2) + 3 + rng.normal(0, 5, doy.size), 0.1, None)
''')

STATIONS = (
'''
# Три створа: столбцы массива (время, створ)
q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])
''',
'''
# Three gauges: columns of a (time, gauge) array
q_obs_st = np.column_stack([q_obs, 0.4 * q_obs + 2, 1.7 * q_obs + 5])
q_sim_st = np.column_stack([q_sim, 0.35 * q_sim + 4, 1.9 * q_sim])
''')

FRAME = (
'''
import pandas as pd

df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
# Водный год начинается 1 октября и назван по году окончания
df["water_year"] = df.index.year + (df.index.month >= 10)
''',
'''
import pandas as pd

df = pd.DataFrame({"q_obs": q_obs, "q_sim": q_sim}, index=pd.to_datetime(dates))
# The water year starts on 1 October and is named after its final year
df["water_year"] = df.index.year + (df.index.month >= 10)
''')

DIR = {
    "up": ("больше лучше", "higher is better"),
    "down": ("меньше лучше", "lower is better"),
    "zero": ("лучше ближе к 0", "closer to 0 is better"),
    "one": ("лучше ближе к 1", "closer to 1 is better"),
}

WEIGHT_UNSUPPORTED = {"spearman_r", "kendall_tau", "roc_auc", "pr_auc", "ssigma", "ssigma_delta",
                      "forecast_verification", "forecast_verification_delta", "regNSE", "nse_variance_weighted"}
AXIS_NOT_SUPPORTED = {"ssigma_delta", "forecast_verification_delta", "regNSE", "nse_variance_weighted"}

BINARY = probe.BINARY_SCORE | probe.BINARY_LABEL


def _short(res):
    v = res.value if hasattr(res, "value") else res
    if isinstance(v, dict):
        v = next(iter(v.values()))
        v = v.value if hasattr(v, "value") else v
        return "r = " + _short_val(v)
    return _short_val(v)


def _short_val(v):
    if isinstance(v, tuple):
        return f"tuple[{len(v)}]"
    arr = np.asarray(v)
    if arr.ndim == 0:
        return fmt(arr)
    return "array" + str(arr.shape).replace(" ", "")


def run(func, *a, **k):
    """Return a compact result string; a leading ⚠ marks a RuntimeWarning."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            s = _short(func(*a, **k))
        except Exception as exc:  # noqa: BLE001
            return exc.__class__.__name__
    return s + (" (RuntimeWarning)" if any(issubclass(w.category, RuntimeWarning) for w in caught) else "")


def typename(func, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            r = func(*a, **k)
        except Exception as exc:  # noqa: BLE001
            return exc.__class__.__name__
    v = r.value if hasattr(r, "value") else r
    if not hasattr(r, "value"):
        return "dict[str, MetricResult]"
    if isinstance(v, dict):
        return "dict"
    if isinstance(v, tuple):
        return f"tuple ({len(v)})"
    if isinstance(v, np.ndarray):
        return "numpy.ndarray " + str(v.shape).replace(" ", "")
    return type(v).__name__ if not isinstance(v, np.floating) else "numpy.float64"


def edge_table(d: Doc, name: str):
    func = getattr(hm, name)
    obs, sim = probe.data_for(name)
    kw = probe.extras(name)
    n = obs.copy()
    n[5] = np.nan
    inf = obs.copy()
    inf[5] = np.inf
    rows = [
        (("NaN в одной паре, ``nan_policy=\"omit\"`` (умолчание)", "NaN in one pair, ``nan_policy=\"omit\"`` (default)"),
         run(func, n, sim, nan_policy="omit", **kw)),
        (("NaN в одной паре, ``nan_policy=\"propagate\"``", "NaN in one pair, ``nan_policy=\"propagate\"``"), run(func, n, sim, nan_policy="propagate", **kw)),
        (("NaN в одной паре, ``nan_policy=\"raise\"``", "NaN in one pair, ``nan_policy=\"raise\"``"), run(func, n, sim, nan_policy="raise", **kw)),
        (("все ``obs`` равны NaN", "all ``obs`` are NaN"), run(func, np.full_like(obs, np.nan), sim, **kw)),
        (("``inf`` в ``obs``", "``inf`` in ``obs``"), run(func, inf, sim, **kw)),
        (("постоянный ``obs`` (нулевая дисперсия)", "constant ``obs`` (zero variance)"), run(func, np.full_like(obs, obs[0]), sim, **kw)),
        (("``obs`` и ``sim`` из одних нулей", "``obs`` and ``sim`` all zero"), run(func, np.zeros_like(obs), np.zeros_like(sim), **kw)),
    ]
    if name not in BINARY and probe.FAMILY[name] in ("regression", "hydro"):
        rows.append((("отрицательные значения (ряд минус его среднее)", "negative values (series minus its mean)"),
                     run(func, obs - obs.mean(), sim - obs.mean(), **kw)))
    rows += [
        (("пустой ввод", "empty input"), run(func, np.array([], dtype=float), np.array([], dtype=float), **probe.extras(name, 0))),
        (("разная длина ``obs`` и ``sim``", "``obs`` and ``sim`` of different length"), run(func, obs, sim[:-1], **kw)),
    ]
    d.table((("Случай", "Case"), ("Результат", "Result")), rows, widths=[60, 40])


def backend_rows(name):
    func = getattr(hm, name)
    obs, sim = probe.data_for(name)
    kw = probe.extras(name)
    rows = []
    twod = not kw
    if twod:
        o2, s2 = np.column_stack([obs, obs, obs]), np.column_stack([sim, sim, sim])
    for be in ("numpy", "pandas", "polars", "xarray"):
        o, s = probe.wrap(be, obs), probe.wrap(be, sim)
        base = typename(func, o, s, **kw)
        if twod:
            oo, ss = probe.wrap(be, o2), probe.wrap(be, s2)
            if be == "xarray":
                ax = "``dim=\"time\"``: " + typename(func, oo, ss, dim="time").replace("DataArray", "xarray.DataArray")
            elif be == "numpy":
                ax = "``axis=0``: " + typename(func, oo, ss, axis=0)
            else:
                ax = "``axis=0``: " + typename(func, oo, ss, axis=0)
        else:
            ax = None
        rows.append((be, base, ax))
    return rows


def metric_page(s: dict) -> Doc:
    name = s["name"]
    d = Doc(f"metrics/{name}.rst", label=f"metric-{name}")
    d.title(s["title"])
    d.p(*s["short"])

    d.h(("Сигнатура", "Signature"))
    extra_sig = s.get("sig", "")
    d.block(f'hydrometrics.{name}(obs, sim, *, {extra_sig}axis=None, nan_policy="omit",\n'
            f'    sample_weight=None, weight=None, reduction=None, align="strict"{s.get("sig_opt", "")})')
    d.p((f"Запись в справочнике API: :func:`hydrometrics.{name}`. На xarray вместо ``axis`` используется ``dim``; остальные параметры одинаковы на всех бэкендах.",
         f"API reference entry: :func:`hydrometrics.{name}`. On xarray ``dim`` is used instead of ``axis``; the other parameters are the same on every backend."))

    d.h(("Математическое определение", "Mathematical definition"))
    for latex in s["formula"]:
        d.math(latex)
    d.p(*s["symbols"])
    d.h3(("Отличия от классического определения", "Differences from the classical definition"))
    d.p(*s["deviation"])

    d.h(("Диапазон значений и оптимум", "Range and optimum"))
    d.table((("Диапазон", "Range"), ("Оптимум", "Optimum"), ("Направление", "Direction")),
            [(s["range"], s["optimum"], DIR[s["dir"]])])
    d.p(*s["bounds"])

    d.h(("Интерпретация и критерии оценки", "Interpretation and rating criteria"))
    s["interp"](d) if callable(s["interp"]) else d.p(*s["interp"])

    d.h(("Параметры", "Parameters"))
    rows = [("``obs``", ("массив", "array"), ("обязателен", "required"), s.get("obs_doc", ("Наблюдённые значения.", "Observed values."))),
            ("``sim``", ("массив", "array"), ("обязателен", "required"), s.get("sim_doc", ("Модельные или прогнозные значения той же формы.", "Simulated or forecast values of the same shape.")))]
    rows += s.get("params_req", [])
    if name in AXIS_NOT_SUPPORTED:
        ax = ("Не поддерживается: любое значение, кроме ``None``, вызывает ``NotImplementedError``.",
              "Not supported: any value other than ``None`` raises ``NotImplementedError``.")
    else:
        ax = s.get("axis_doc", ("Ось суммирования; ``None`` объединяет все значения. На xarray вместо неё используется ``dim`` (или ``axis``, он переводится в имя измерения).",
                                "Summation axis; ``None`` pools all values. On xarray use ``dim`` (or ``axis``, which is translated to a dimension name)."))
    rows.append(("``axis``", "int | None", "``None``", ax))
    rows.append(("``nan_policy``", "str", "``\"omit\"``", ("``\"omit\"`` удаляет пары с пропуском, ``\"propagate\"`` даёт NaN, ``\"raise\"`` вызывает ``ValueError``; см. раздел о пропусках ниже и :doc:`/user_guide/missing_values`.",
                                                           "``\"omit\"`` drops pairs with a gap, ``\"propagate\"`` gives NaN, ``\"raise\"`` raises ``ValueError``; see the section on missing values below and :doc:`/user_guide/missing_values`.")))
    if name in WEIGHT_UNSUPPORTED:
        wd = ("Не поддерживается: вызывает ``NotImplementedError``.", "Not supported: raises ``NotImplementedError``.")
    else:
        wd = s.get("weight_doc", ("Веса той же формы, что ``obs``, неотрицательные; NaN делает пару недействительной. ``weight`` принимается как алиас, обе формы сразу вызывают ``TypeError``.",
                                  "Weights of the same shape as ``obs``, non-negative; NaN makes the pair invalid. ``weight`` is accepted as an alias, both at once raise ``TypeError``."))
    rows.append(("``sample_weight``", ("массив | None", "array | None"), "``None``", wd))
    rows.append(("``reduction``", "str | None", "``None``", s.get("red_doc", ("Свёртка результата с ``ndim > 0``: ``\"mean\"``, ``\"sum\"`` или ``\"none\"``. По умолчанию при заданной оси возвращается массив по оставшимся измерениям, без оси среднее.",
                                                                          "Reduction of a result with ``ndim > 0``: ``\"mean\"``, ``\"sum\"`` or ``\"none\"``. By default an axis gives the array over the remaining dimensions and no axis gives the mean."))))
    rows.append(("``align``", "str", "``\"strict\"``", ("``\"strict\"`` требует равных индексов pandas и координат xarray, ``\"inner\"`` оставляет общие метки в порядке ``obs``. Без меток ``\"inner\"`` вызывает ``ValueError``.",
                                                     "``\"strict\"`` requires equal pandas indexes and xarray coordinates, ``\"inner\"`` keeps the common labels in the order of ``obs``. Without labels ``\"inner\"`` raises ``ValueError``.")))
    rows += s.get("params_opt", [])
    d.table((("Имя", "Name"), ("Тип", "Type"), ("По умолчанию", "Default"), ("Описание", "Description")), rows, widths=[18, 16, 14, 52])

    be = backend_rows(name)
    d.h(("Возвращаемое значение", "Return value"))
    d.p(("Функция возвращает :class:`~hydrometrics.MetricResult`; значение лежит в поле ``value``. В таблице указан фактический тип ``value`` при одномерном вводе и при вычислении по оси.",
         "The function returns a :class:`~hydrometrics.MetricResult`; the value is in the ``value`` field. The table shows the actual type of ``value`` for one-dimensional input and for a computation along an axis.") if name != "kge_components" else
        ("На всех бэкендах функция возвращает :class:`~hydrometrics.MetricResult` со словарём в поле ``value``; значения словаря свёрнуты по тому же правилу ``reduction``.",
         "On every backend the function returns a :class:`~hydrometrics.MetricResult` holding a dictionary in ``value``; the dictionary values are reduced by the same ``reduction`` rule."))
    d.table((("Бэкенд", "Backend"), ("Одномерный ввод", "One-dimensional input"), ("По оси, ввод формы (1096, 3)", "Along an axis, input of shape (1096, 3)")),
            [(b, t, a if a else ("не применимо: метрика требует одномерного ввода", "not applicable: the metric requires one-dimensional input")) for b, t, a in be],
            widths=[15, 35, 50])
    if s.get("ret_note"):
        d.p(*s["ret_note"])

    d.h(("Пропуски и особые случаи", "Missing values and special cases"))
    d.p(("Результаты получены запуском на numpy при сборке этой страницы. Ряд содержит 1096 суточных значений. Пометка ``RuntimeWarning`` означает, что предупреждение numpy выходит наружу.",
         "Results come from running the NumPy path when this page was generated. The series has 1096 daily values. The ``RuntimeWarning`` mark means a NumPy warning reaches the caller."))
    edge_table(d, name)
    d.p(*s["special"])

    d.h(("Поддержка бэкендов", "Backend support"))
    no = ("нет", "no")
    w = no if name in WEIGHT_UNSUPPORTED else "``sample_weight``, ``weight``"
    ax_plain = no if name in AXIS_NOT_SUPPORTED else "``axis``"
    ax_xr = no if name in AXIS_NOT_SUPPORTED else "``dim``, ``axis``"
    d.table((("Бэкенд", "Backend"), ("Веса", "Weights"), ("Ось", "Axis"), ("``nan_policy``", "``nan_policy``"), ("``reduction``", "``reduction``")),
            [("numpy", w, ax_plain, ("да", "yes"), ("да", "yes")),
             ("pandas", w, ax_plain, ("да", "yes"), ("да", "yes")),
             ("polars", w, ax_plain, ("да", "yes"), ("да", "yes")),
             ("xarray", w, ax_xr, ("да", "yes"), ("да", "yes"))])
    if s.get("backend_note"):
        d.p(*s["backend_note"])
    else:
        d.p(("Индексы pandas и координаты xarray проверяются параметром ``align``: по умолчанию несовпадающие метки дают ``ValueError``, ``align=\"inner\"`` оставляет общие (см. :doc:`/user_guide/input_data`).",
             "pandas indexes and xarray coordinates are checked by the parameter ``align``: by default differing labels raise ``ValueError``, ``align=\"inner\"`` keeps the common ones (see :doc:`/user_guide/input_data`)."))

    d.h(("Примеры", "Examples"))
    s["examples"](d)

    d.h(("Особенности применения в гидрологии", "Application in hydrology"))
    hydro = s["hydro"]
    d.p(*(hydro(d.ns) if callable(hydro) else hydro))

    d.h(("Связанные метрики", "Related metrics"))
    d.ul([f":ref:`metric-{r}`" for r in s["related"]])
    if s.get("related_note"):
        d.p(*s["related_note"])

    d.h(("Литература", "References"))
    if s.get("refs"):
        d.raw(".. footbibliography::")
    else:
        d.p(("Специальной литературы для этой страницы нет: метрика определяется общепринятой формулой.",
             "No dedicated literature for this page: the metric is defined by a standard formula."))
    return d
