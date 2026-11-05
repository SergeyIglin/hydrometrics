"""Skip guards for optional dependencies (numpy is the only required package).

``spearman_r`` and ``kendall_tau`` import scipy lazily, so tests that are parametrised over
metric names are skipped for exactly these two names when scipy is not installed.
Backend-specific modules and tests skip through ``pytest.importorskip`` where they build inputs.
"""

from __future__ import annotations

import importlib.util

import pytest

SCIPY_METRICS = frozenset({"spearman_r", "kendall_tau"})
HAS_SCIPY = importlib.util.find_spec("scipy") is not None


def pytest_collection_modifyitems(config, items):
    if HAS_SCIPY:
        return
    skip = pytest.mark.skip(reason="scipy is not installed (needed by spearman_r and kendall_tau)")
    for item in items:
        callspec = getattr(item, "callspec", None)
        if callspec is None:
            continue
        candidates = list(callspec.params.values()) + callspec.id.split("-")
        candidates += [v[0] for v in callspec.params.values() if isinstance(v, (tuple, list)) and v]
        if any(isinstance(v, str) and v in SCIPY_METRICS for v in candidates):
            item.add_marker(skip)
