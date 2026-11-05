"""Docstrings must parse with plain numpydoc/napoleon section names (report section 5.4, #5)."""

from __future__ import annotations

import ast
import re
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent / "hydrometrics"
KNOWN = {
    "Parameters", "Returns", "Yields", "Raises", "Warns", "See Also", "Notes", "References",
    "Examples", "Attributes", "Methods", "Other Parameters", "Receives", "Warnings",
}
SECTION = re.compile(r"^(?P<indent>[ \t]*)(?P<title>[A-Za-z][A-Za-z ]*?)\n(?P=indent)(?P<rule>-{3,})$", re.M)


def _docstrings():
    for path in sorted(PKG.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                doc = ast.get_docstring(node, clean=True)
                if doc:
                    yield path.name, getattr(node, "name", "<module>"), doc


def test_all_section_titles_are_standard():
    bad = []
    for file, name, doc in _docstrings():
        for m in SECTION.finditer(doc):
            if m.group("title").strip() not in KNOWN:
                bad.append((file, name, m.group("title")))
    assert not bad, bad


def test_no_singular_reference_or_steps_heading():
    bad = []
    for file, name, doc in _docstrings():
        for line in doc.splitlines():
            if line.strip() in ("Reference", "Steps"):
                bad.append((file, name, line.strip()))
    assert not bad, bad


def test_references_underline_matches_title_length():
    bad = []
    for file, name, doc in _docstrings():
        lines = doc.splitlines()
        for i, line in enumerate(lines[:-1]):
            if line.strip() == "References" and set(lines[i + 1].strip()) == {"-"}:
                if len(lines[i + 1].strip()) < len("References"):
                    bad.append((file, name))
    assert not bad, bad
