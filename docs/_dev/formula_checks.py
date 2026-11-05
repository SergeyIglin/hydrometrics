"""Numerical check of every metric against its documented formula.

The checks live in ``tests/test_metric_formulas.py``: each of the 44 metrics is compared with an
independent numpy implementation written from the published definition, has a hand example with a
known answer and is tested for the optimum on a perfect forecast. This script runs them.

Run from the repository root: ``python docs/_dev/formula_checks.py``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_metric_formulas.py", "-q", "-o", "addopts=", "-p", "no:cacheprovider"],
        cwd=ROOT,
    )
    sys.exit(result.returncode)
