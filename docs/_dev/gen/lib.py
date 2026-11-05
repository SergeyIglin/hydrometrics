"""Bilingual page authoring: emits Russian RST and a ru->en translation memory."""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import re
import sys
import warnings

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
DOCS = ROOT / "docs"
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DOCS / "_dev"))

CYR = re.compile(r"[А-Яа-яЁё]")
TM_PATH = HERE / "tm.json"
TM: dict[str, str] = json.loads(TM_PATH.read_text(encoding="utf-8")) if TM_PATH.exists() else {}


def save_tm():
    TM_PATH.write_text(json.dumps(TM, ensure_ascii=False, indent=0), encoding="utf-8")


def tr(pair) -> str:
    """Return the Russian text; record its translation."""
    if isinstance(pair, str):
        if CYR.search(pair):
            raise ValueError("no translation for: " + pair[:80])
        return pair
    ru, en = pair
    ru, en = " ".join(ru.split()), " ".join(en.split())
    if CYR.search(en):
        raise ValueError("cyrillic in en: " + en[:80])
    if TM.get(ru, en) != en:
        print("TM conflict:", ru[:70])
    TM[ru] = en
    return ru


class Doc:
    def __init__(self, path: str, label: str | None = None):
        self.path = DOCS / path
        self.out: list[str] = []
        self.ns: dict = {}
        if label:
            self.out += [f".. _{label}:", ""]

    def raw(self, text: str):
        self.out += [text, ""]

    def title(self, pair):
        t = tr(pair)
        self.out += ["=" * (len(t) + 2), t, "=" * (len(t) + 2), ""]

    def h(self, pair, ch="-"):
        t = tr(pair)
        self.out += [t, ch * (len(t) + 2), ""]

    def h3(self, pair):
        self.h(pair, "~")

    def p(self, *pairs):
        for pair in pairs:
            self.out += [tr(pair), ""]

    def ul(self, items):
        for it in items:
            self.out.append("- " + tr(it))
        self.out.append("")

    def note(self, pair, kind="note"):
        self.out += [f".. {kind}::", "", "   " + tr(pair), ""]

    def warn(self, pair):
        self.note(pair, "warning")

    def math(self, latex: str, label: str | None = None):
        self.out += [".. math::"]
        if label:
            self.out += [f"   :label: {label}"]
        self.out += [""]
        self.out += ["   " + l for l in latex.strip().splitlines()]
        self.out += [""]

    def table(self, header, rows, widths=None):
        self.out += [".. list-table::", "   :header-rows: 1", "   :class: hm-table"]
        if widths:
            self.out += ["   :widths: " + " ".join(map(str, widths))]
        self.out += [""]
        for row in [header, *rows]:
            for i, cell in enumerate(row):
                lead = "   * - " if i == 0 else "     - "
                text = tr(cell)
                self.out.append(lead + (text if text else ""))
        self.out.append("")

    def block(self, text: str, lang="python"):
        self.out += [f".. code-block:: {lang}", ""]
        self.out += ["   " + l if l else "" for l in text.strip("\n").splitlines()]
        self.out += [""]

    def code(self, code, en: str | None = None, show_output=True):
        """Show code, run it now, and embed the real output as a checked testoutput."""
        code = code.strip("\n")
        if CYR.search(code):
            if en is None:
                raise ValueError("code with cyrillic needs en version: " + code[:60])
            TM[code] = en.strip("\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            exec(compile(code, "<doc>", "exec"), self.ns)
        output = buf.getvalue().rstrip("\n")
        if CYR.search(output):
            raise ValueError("cyrillic in output: " + output[:60])
        self.out += [".. testcode::", ""]
        self.out += ["   " + l if l else "" for l in code.splitlines()]
        self.out += [""]
        if output and show_output:
            self.out += [".. testoutput::", "   :options: +NORMALIZE_WHITESPACE", ""]
            self.out += ["   " + l for l in output.splitlines()]
            self.out += [""]
        return output

    def write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        text = "\n".join(self.out).rstrip() + "\n"
        self.path.write_text(text, encoding="utf-8")


def fmt(v) -> str:
    """Compact, stable rendering of a computed number."""
    v = float(v)
    if np.isnan(v):
        return "NaN"
    if np.isinf(v):
        return "inf" if v > 0 else "-inf"
    if v != 0 and (abs(v) >= 1e5 or abs(v) < 1e-3):
        return f"{v:.3e}"
    return f"{v:.4g}"
