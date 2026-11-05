"""Stage E of task_5: numpy is the only required dependency; the version has one source."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import hydrometrics as hm

ROOT = Path(__file__).resolve().parents[1]


def run_blocked(blocked, code):
    """Run ``code`` in a fresh interpreter in which the ``blocked`` packages cannot be imported."""
    prelude = "import sys\n" + "".join(f"sys.modules[{name!r}] = None\n" for name in blocked)
    return subprocess.run(
        [sys.executable, "-c", prelude + textwrap.dedent(code)],
        capture_output=True, text=True, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT), "PYTHONUTF8": "1"},
    )


NUMPY_ONLY = ["pandas", "polars", "xarray", "scipy"]


def test_import_and_numpy_metrics_without_any_optional_package():
    result = run_blocked(NUMPY_ONLY, """
        import numpy as np
        import hydrometrics as hm
        obs = np.array([1.0, 2.0, 3.0, 5.0]); sim = np.array([1.1, 1.9, 3.2, 4.8])
        print(round(float(hm.nse(obs, sim)), 6), round(float(hm.kge_2012(obs, sim)), 6), round(float(hm.crps(obs, sim)), 6))
        print(hm.compute_grouped(hm.mae, None, obs, sim, group_by={"g": [1, 1, 2, 2]}).values.round(3).tolist())
        print(hm.nse([1.0, 2.0, 4.0], [1.0, 2.0, 3.0]).value)
        print(hasattr(hm, "HAS_PANDAS_BACKEND") and hm.HAS_PANDAS_BACKEND, hm.HAS_XARRAY_BACKEND, hm.HAS_POLARS_BACKEND)
    """)
    assert result.returncode == 0, result.stderr
    assert "False False False" in result.stdout


def test_rank_metrics_explain_the_missing_scipy():
    result = run_blocked(NUMPY_ONLY, """
        import numpy as np
        import hydrometrics as hm
        try:
            hm.spearman_r(np.arange(5.0), np.arange(5.0) ** 2)
        except ImportError as exc:
            print("ImportError", exc)
        print(round(float(hm.pearson_r(np.arange(5.0), np.arange(5.0) ** 2)), 4))
    """)
    assert result.returncode == 0, result.stderr
    assert "ImportError" in result.stdout and "scipy" in result.stdout


@pytest.mark.parametrize("present", ["pandas", "polars", "xarray"])
def test_each_backend_works_alone(present):
    pytest.importorskip(present)
    # xarray itself needs pandas, so pandas cannot be hidden when xarray is the backend under test
    needed = {"pandas": {"pandas"}, "polars": {"polars"}, "xarray": {"xarray", "pandas"}}[present]
    others = [p for p in ("pandas", "polars", "xarray") if p not in needed] + ["scipy"]
    make = {"pandas": "import pandas as pd; o, s = pd.Series(a), pd.Series(b)",
            "polars": "import polars as pl; o, s = pl.Series(a), pl.Series(b)",
            "xarray": "import xarray as xr; o, s = xr.DataArray(a, dims='t'), xr.DataArray(b, dims='t')"}[present]
    result = run_blocked(others, f"""
        import numpy as np
        import hydrometrics as hm
        a = np.array([1.0, 2.0, 3.0, 5.0]); b = np.array([1.1, 1.9, 3.2, 4.8])
        {make}
        print(round(float(hm.nse(o, s)), 6), round(float(hm.nse(a, b)), 6))
        print(hm.HAS_PANDAS_BACKEND, hm.HAS_XARRAY_BACKEND, hm.HAS_POLARS_BACKEND)
    """)
    assert result.returncode == 0, result.stderr
    first, second = result.stdout.splitlines()[0].split()
    assert first == second
    flags = dict(zip(("pandas", "xarray", "polars"), result.stdout.splitlines()[1].split()))
    assert flags[present] == "True"
    assert all(flags[name] == "False" for name in flags if name not in needed)


def test_version_comes_from_the_package_metadata_and_matches_pyproject():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    declared = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M).group(1)
    assert hm.__version__ == declared
    assert re.fullmatch(r"\d+\.\d+\.\d+.*", hm.__version__)
