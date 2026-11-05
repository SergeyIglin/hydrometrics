"""Package hygiene (report items #31, #32 and section 5.5)."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # Python 3.10: tomli is the same parser (pytest depends on it there)
    tomllib = pytest.importorskip("tomli")

import hydrometrics as hm

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "hydrometrics"
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _min_python() -> tuple[int, int]:
    spec = PYPROJECT["project"]["requires-python"]
    major, minor = re.search(r">=\s*(\d+)\.(\d+)", spec).groups()
    return int(major), int(minor)


def _module_level_unions(path: Path) -> list[int]:
    """Lines of ``X | Y`` expressions evaluated at import time (not inside annotations)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    lines = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom)):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.BinOp) and isinstance(sub.op, ast.BitOr):
                lines.append(sub.lineno)
    return lines


def test_requires_python_allows_runtime_unions():
    """#31: ``A | B`` between classes at import time needs Python 3.10."""
    offenders = {p.name: _module_level_unions(p) for p in PKG.rglob("*.py")}
    offenders = {k: v for k, v in offenders.items() if v}
    if offenders:
        assert _min_python() >= (3, 10), f"runtime unions in {offenders}"


def test_classifiers_not_below_requires_python():
    low = _min_python()
    for classifier in PYPROJECT["project"]["classifiers"]:
        m = re.fullmatch(r"Programming Language :: Python :: (\d+)\.(\d+)", classifier)
        if m:
            assert (int(m.group(1)), int(m.group(2))) >= low, classifier


def test_readme_exists_and_is_declared():
    """#32: ``readme = "README.md"`` must point to an existing, non-empty file."""
    declared = PYPROJECT["project"]["readme"]
    path = ROOT / declared
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "hydrometrics" in text and "pip install" in text and "import hydrometrics" in text


def test_license_file_is_mit_with_author():
    path = ROOT / "LICENSE"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert text.startswith("MIT License")
    assert PYPROJECT["project"]["authors"][0]["name"] in text


def test_no_backup_files_in_package():
    assert not list(PKG.rglob("*.bak"))
    assert "*.bak" in (ROOT / ".gitignore").read_text(encoding="utf-8").split()


def test_regnse_registered_once():
    source = (PKG / "__init__.py").read_text(encoding="utf-8")
    assert len(re.findall(r'^\s*\("regNSE",', source, flags=re.M)) == 1
    assert source.count('regNSE = registry.get_dispatcher("regNSE")') == 1


def test_private_helper_is_not_imported_into_package_root():
    assert not hasattr(hm, "_annual_day_index")
    assert "_annual_day_index" not in (PKG / "__init__.py").read_text(encoding="utf-8")


def test_numpy_backend_imports_numpy_once():
    source = (PKG / "backends" / "numpy.py").read_text(encoding="utf-8")
    assert len(re.findall(r"^import numpy as np$", source, flags=re.M)) == 1


def test_grouping_has_no_empty_loop():
    tree = ast.parse((PKG / "core" / "grouping.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            assert not all(isinstance(stmt, ast.Pass) for stmt in node.body), node.lineno


@pytest.mark.parametrize("name", ["OPEN_QUESTIONS.md", "DEAD_CODE.md"])
def test_author_decision_files_exist(name):
    assert (ROOT / "docs" / "_dev" / name).is_file()


def test_changelog_exists():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "Изменено поведение" in text or "Changed behavior" in text
