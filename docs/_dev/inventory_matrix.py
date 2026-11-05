"""Сводит результат inventory_probe.py в матрицу поведения метрик (Markdown).

Запуск: ``python docs/_dev/inventory_matrix.py inventory_probe.json``.
"""

from __future__ import annotations

import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))


def val(c):
    v = c.get("value", {})
    while v.get("kind") == "MetricResult":
        v = v["value"]
    return v


def shape(c):
    if c is None:
        return "н/п"
    if not c["ok"]:
        return f"ошибка {c['exc']}"
    v = val(c)
    k = v.get("kind")
    if k == "dict":
        return "dict: " + shape({"ok": True, "value": next(iter(v["items"].values()))})
    if k == "tuple":
        return f"tuple({len(v['items'])})"
    if k == "DataArray":
        return "DataArray" + str(tuple(v["shape"])).replace(" ", "")
    if k == "ndarray":
        return ("0-d" if not v["shape"] else str(tuple(v["shape"])).replace(" ", ""))
    return "скаляр"


def num(c):
    if c is None or not c["ok"]:
        return None
    v = val(c)
    if v.get("kind") == "dict":
        v = next(iter(v["items"].values()))
    return v.get("value")


def same(a, b):
    x, y = num(a), num(b)
    if x is None or y is None:
        return False
    if x != x and y != y:
        return True
    return x == y


def nan_cell(n):
    c = n.get("nan_propagate")
    if not c["ok"]:
        return f"ошибка {c['exc']}"
    x = num(c)
    if x is None:
        return "массив"
    if x != x:
        return "NaN"
    return "число"


def omit_cell(n):
    c = n.get("nan_omit")
    return "работает" if c["ok"] else f"{c['exc']}"


def weight_cell(n):
    c = n.get("sample_weight")
    if not c["ok"]:
        return f"ошибка {c['exc']}"
    return "игнор." if same(c, n["base"]) else "учитыв."


print("| Метрика | base numpy | propagate с NaN | omit с NaN | sample_weight | axis=0, none (numpy) | axis=1, none (numpy) | axis=0 (pandas) | axis=0 (polars) | axis= (xarray) | dim=time (xarray) | base pandas |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for m, r in d["metrics"].items():
    n, p, pl, x = r["numpy"], r["pandas"], r["polars"], r["xarray"]
    print(f"| `{m}` | {shape(n['base'])} | {nan_cell(n)} | {omit_cell(n)} | {weight_cell(n)} | {shape(n.get('axis0_rednone'))} | {shape(n.get('axis1_rednone'))} | {shape(p.get('axis0'))} | {shape(pl.get('axis0'))} | {shape(x.get('axis0'))} | {shape(x.get('dim_time'))} | {shape(p['base'])} |")

print()
print("| Метрика | inf в obs | все NaN | постоянный obs | obs=sim | нули | отрицательные | пустой ввод | разная длина |")
print("|---|---|---|---|---|---|---|---|---|")


def edge(c):
    if c is None:
        return "н/п"
    if not c["ok"]:
        return c["exc"]
    v = num(c)
    w = " ⚠" if c.get("warnings") else ""
    if v is None:
        return shape(c) + w
    return f"{v:.4g}{w}"


for m, r in d["metrics"].items():
    n = r["numpy"]
    print("| `%s` | %s |" % (m, " | ".join(edge(n.get(k)) for k in ("inf", "all_nan", "const_obs", "identical", "zeros", "negative", "empty", "length_mismatch"))))
