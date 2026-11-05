"""Compare the public metrics with the pages in docs/metrics/.

A page counts as written if it is not a stub: a stub is marked ``:orphan:`` and has no
"Signature" section. Exit code 1 if any public metric has no written page.

Run from the repository root: ``python docs/_dev/check_metric_pages.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import hydrometrics as hm  # noqa: E402
from hydrometrics.core.base import MetricFunction  # noqa: E402

PAGES = ROOT / "docs" / "metrics"


def main() -> int:
    public = [n for n in hm.__all__ if isinstance(getattr(hm, n, None), MetricFunction) or hasattr(getattr(hm, n, None), "direction")]
    written, stubs, missing = [], [], []
    for name in public:
        page = PAGES / f"{name}.rst"
        if not page.exists():
            missing.append(name)
        elif page.read_text(encoding="utf-8").lstrip().startswith(":orphan:"):
            stubs.append(name)
        else:
            written.append(name)
    extra = sorted(p.stem for p in PAGES.glob("*.rst") if p.stem not in public and p.stem != "index")
    print(f"public metrics: {len(public)}; written pages: {len(written)}; stubs: {len(stubs)}; without a file: {len(missing)}")
    if stubs:
        print("stubs:", ", ".join(stubs))
    if missing:
        print("missing:", ", ".join(missing))
    if extra:
        print("pages without a metric:", ", ".join(extra))
    return 1 if stubs or missing or extra else 0


if __name__ == "__main__":
    sys.exit(main())
