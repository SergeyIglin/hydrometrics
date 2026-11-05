"""Проверка DOI: запрос к Crossref (при неудаче к doi.org), печать метаданных источника.

Запуск: ``python docs/_dev/check_dois.py [файл.json]`` или с DOI в аргументах;
без аргументов DOI берутся из ``docs/references.bib``. Результат пишется в
``docs/_dev/doi_check.json``.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
UA = {"User-Agent": "hydrometrics-docs-doi-check/1.0 (https://github.com/SergeyIglin/hydrometrics)"}


def crossref(doi: str) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as resp:
            msg = json.load(resp)["message"]
    except urllib.error.HTTPError as exc:
        return resolve_doi_org(doi, f"crossref HTTP {exc.code}")
    except Exception as exc:  # noqa: BLE001
        return {"doi": doi, "status": "error", "detail": str(exc)[:120]}
    date = (msg.get("issued", {}).get("date-parts") or [[None]])[0]
    authors = [a.get("family", a.get("name", "?")) for a in msg.get("author", [])]
    return {"doi": doi, "status": "crossref-ok", "year": date[0], "authors": authors,
            "title": (msg.get("title") or [""])[0], "journal": (msg.get("container-title") or [""])[0],
            "volume": msg.get("volume"), "issue": msg.get("issue"), "pages": msg.get("page")}


def resolve_doi_org(doi: str, why: str) -> dict:
    """DOI не из Crossref (DataCite, mEDRA и др.): проверяем, что он разрешается через doi.org."""
    req = urllib.request.Request("https://doi.org/api/handles/" + urllib.parse.quote(doi, safe="/"), headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        code = data.get("responseCode")
        urls = [v["data"]["value"] for v in data.get("values", []) if v.get("type") == "URL"]
        return {"doi": doi, "status": "doi-org-ok" if code == 1 else f"doi-org-code-{code}", "url": urls, "note": why}
    except urllib.error.HTTPError as exc:
        return {"doi": doi, "status": "not-found", "detail": f"{why}; doi.org HTTP {exc.code}"}
    except Exception as exc:  # noqa: BLE001
        return {"doi": doi, "status": "error", "detail": str(exc)[:120]}


def from_bib(path: pathlib.Path) -> list[str]:
    return re.findall(r"doi\s*=\s*[{\"]([^}\"]+)[}\"]", path.read_text(encoding="utf-8"), flags=re.I)


def check_package() -> int:
    """Compare every DOI cited in hydrometrics/ with Crossref: first author, year (+-1), journal.

    Expected values come from tests/verified_dois.json. Returns the number of problems.
    """
    import html
    import time

    root = HERE.parent.parent
    verified = json.loads((root / "tests" / "verified_dois.json").read_text(encoding="utf-8"))
    sys.path.insert(0, str(root / "tests"))
    from test_references import extract_dois  # same extraction as the offline test

    cited: dict[str, list[str]] = {}
    for path in sorted((root / "hydrometrics").rglob("*.py")):
        for doi in extract_dois(path.read_text(encoding="utf-8")):
            cited.setdefault(doi, []).append(path.name)

    problems = 0
    for doi in cited:
        if doi not in verified:
            print(f"NOT VERIFIED  {doi}  in {sorted(set(cited[doi]))}")
            problems += 1
    for doi, expected in verified.items():
        time.sleep(0.3)
        r = crossref(doi)
        if r["status"] != "crossref-ok":
            print(f"FAIL {doi}: {r['status']} {r.get('detail', '')}")
            problems += 1
            continue
        authors = [a.lower() for a in r["authors"]]
        journal = html.unescape(r["journal"]).lower()
        errors = []
        if not authors or expected["author"].lower() not in authors[0]:
            errors.append(f"first author {r['authors'][:1]} != {expected['author']}")
        if r["year"] is None or abs(r["year"] - expected["year"]) > 1:
            errors.append(f"year {r['year']} != {expected['year']}")
        if expected["journal"].lower() not in journal:
            errors.append(f"journal {r['journal']!r} != {expected['journal']!r}")
        status = "OK  " if not errors else "FAIL"
        print(f"{status} {doi}  {expected['cited_as']}  ->  {r['authors'][:1]} {r['year']} {r['journal'][:45]}"
              + ("" if not errors else "   " + "; ".join(errors)))
        problems += bool(errors)
    unused = [d for d in verified if d not in cited]
    print(f"cited in package: {len(cited)}, verified list: {len(verified)}, not cited (kept for docs): {len(unused)}")
    print(f"problems: {problems}")
    return problems


if __name__ == "__main__":
    if sys.argv[1:] == ["--package"]:
        sys.exit(1 if check_package() else 0)
    dois = sys.argv[1:] or from_bib(HERE.parent / "references.bib")
    results = [crossref(d) for d in dois]
    for r in results:
        if r["status"] == "crossref-ok":
            print(f"OK  {r['doi']}\n    {r['year']} | {', '.join(r['authors'][:4])} | {r['title'][:90]} | {r['journal']} {r['volume']}({r['issue']}) {r['pages']}")
        else:
            print(f"{r['status'].upper()}  {r['doi']}  {r.get('url') or r.get('detail') or ''}")
    if not sys.argv[1:]:
        (HERE / "doi_check.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
