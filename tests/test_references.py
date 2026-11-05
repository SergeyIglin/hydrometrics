"""DOIs cited in the package must be verified (report section 5.3). No network access.

``verified_dois.json`` lists DOIs whose first author, year and journal were compared with
Crossref by ``docs/_dev/check_dois.py --package``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import hydrometrics as hm

PKG = Path(__file__).resolve().parent.parent / "hydrometrics"
VERIFIED = json.loads(Path(__file__).with_name("verified_dois.json").read_text(encoding="utf-8"))

WRONG = [
    "10.1080/02626667009493734", "10.1080/02626660109492123", "10.1016/j.jhydrol.2005.03.004",
    "10.1080/02626669909492012", "10.1029/2009WR008034", "10.5194/hess-16-1063-2012",
    "10.1016/j.jhydrol.2008.01.002", "10.1002/qj.49712656313", "10.1198/jasa.2011.ap09513",
    "10.1175/1520-0493(1950)078<0001:VOFE>2.0.CO;2", "10.1175/1520-0493(1973)101<0001:TVS>2.3.CO;2",
    "10.1175/JTECH2035.1", "10.1029/1999WR900093", "10.1002/qj.822",
    "10.1175/1520-0493(1981)109<0225:OTUOSA>2.0.CO;2", "10.1016/j.jhydrol.2012.02.021",
]
DOI = re.compile(r"10\.\d{4,9}/[^\s\"']+")


def extract_dois(text: str) -> list[str]:
    found = []
    for m in DOI.finditer(text):
        doi = m.group(0)
        while doi and doi[-1] in ".,;":
            doi = doi[:-1]
        while doi.endswith(")") and doi.count(")") > doi.count("("):
            doi = doi[:-1]
        found.append(doi)
    return found


def _sources():
    return {p: p.read_text(encoding="utf-8") for p in sorted(PKG.rglob("*.py"))}


def test_every_doi_in_sources_is_verified():
    unknown = {}
    for path, text in _sources().items():
        for doi in extract_dois(text):
            if doi not in VERIFIED:
                unknown.setdefault(doi, []).append(path.name)
    assert not unknown, unknown


@pytest.mark.parametrize("doi", WRONG)
def test_known_wrong_dois_are_gone(doi):
    assert not any(doi in text for text in _sources().values())


def test_seibert_is_not_cited():
    """#5.3: the Seibert DOI was nonexistent and the article does not define log NSE."""
    assert not any("Seibert" in text for text in _sources().values())


METRICS = [n for n in hm.__all__ if hasattr(getattr(hm, n), "direction")]


@pytest.mark.parametrize("name", METRICS)
def test_metric_reference_attribute_has_verified_doi(name):
    reference = getattr(hm, name).reference
    for doi in extract_dois(reference):
        assert doi in VERIFIED, (name, doi)


def test_metric_list_is_complete():
    assert len(METRICS) == 44
