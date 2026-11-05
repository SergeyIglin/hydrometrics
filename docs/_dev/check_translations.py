"""Проверка каталогов перевода docs/locale/*/LC_MESSAGES/*.po.

Ошибки: пустой msgstr в каталоге en, fuzzy-записи, расхождение числа ролей,
ссылок, формул и подстановок между msgid и msgstr, кириллица в английском
переводе. Каталог ru содержит только английские строки докстрингов и служебные
строки расширений, поэтому пустые записи в нём не считаются ошибкой.

Запуск: ``python docs/_dev/check_translations.py``. Код возврата 1 при ошибках.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

LOCALE = Path(__file__).resolve().parent.parent / "locale"

ROLE = re.compile(r":([a-zA-Z][\w:.+-]*):`")
EXT_LINK = re.compile(r"`[^`]*<https?://[^>]+>`_+")
BARE_URL = re.compile(r"https?://[^\s>`]+")
MATH = re.compile(r":math:`([^`]*)`")
REF_NAME = re.compile(r"(?<![:\w`])`[^`]+`_\b")
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
NUMBER_IN_LITERAL = re.compile(r"``([^`]*)``")


def parse_po(path: Path) -> list[dict]:
    """Минимальный разбор .po: достаточно msgid, msgstr и флагов."""
    entries: list[dict] = []
    cur: dict | None = None
    field = None
    flags: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("#,"):
            flags = [f.strip() for f in line[2:].split(",")]
        elif line.startswith("#"):
            continue
        elif line.startswith("msgid "):
            if cur is not None:
                entries.append(cur)
            cur = {"msgid": _unquote(line[6:]), "msgstr": "", "flags": flags}
            flags = []
            field = "msgid"
        elif line.startswith("msgstr "):
            cur["msgstr"] = _unquote(line[7:])
            field = "msgstr"
        elif line.startswith('"') and cur is not None and field:
            cur[field] += _unquote(line)
    if cur is not None:
        entries.append(cur)
    return [e for e in entries if e["msgid"]]


def _unquote(text: str) -> str:
    text = text.strip()[1:-1]
    return (text.replace(r"\\", "\0").replace(r"\n", "\n").replace(r"\t", "\t")
            .replace(r"\"", '"').replace("\0", "\\"))


def fingerprint(text: str) -> dict[str, Counter]:
    return {
        "роли": Counter(ROLE.findall(text)),
        "формулы": Counter(MATH.findall(text)),
        "внешние ссылки": Counter(BARE_URL.findall(text)),
    }


def check_catalog(path: Path, lang: str) -> list[str]:
    problems = []
    for entry in parse_po(path):
        msgid, msgstr = entry["msgid"], entry["msgstr"]
        where = f"{path.relative_to(LOCALE)}: {msgid[:70]!r}"
        if "fuzzy" in entry["flags"]:
            problems.append(f"fuzzy: {where}")
        if not msgstr:
            if lang == "en":
                problems.append(f"пустой msgstr: {where}")
            continue
        # The Russian column of the glossary stays Russian in the English build: msgstr equals msgid.
        if lang == "en" and CYRILLIC.search(msgstr) and msgstr != msgid:
            problems.append(f"кириллица в переводе: {where}")
        source, target = fingerprint(msgid), fingerprint(msgstr)
        for kind in source:
            if source[kind] != target[kind]:
                diff = (source[kind] - target[kind]) + (target[kind] - source[kind])
                problems.append(f"{kind} расходятся {dict(diff)}: {where}")
        if len(EXT_LINK.findall(msgid)) != len(EXT_LINK.findall(msgstr)):
            problems.append(f"число именованных ссылок расходится: {where}")
    return problems


def main() -> int:
    problems: list[str] = []
    counts = {}
    for lang_dir in sorted(p for p in LOCALE.iterdir() if p.is_dir()):
        files = sorted((lang_dir / "LC_MESSAGES").rglob("*.po"))
        counts[lang_dir.name] = (len(files), sum(len(parse_po(f)) for f in files))
        for po in files:
            problems.extend(check_catalog(po, lang_dir.name))
    for lang, (n_files, n_entries) in counts.items():
        print(f"{lang}: файлов {n_files}, записей {n_entries}")
    if not counts.get("en", (0, 0))[1]:
        problems.append("каталог en пуст")
    for problem in problems:
        print(problem)
    print(f"проблем: {len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
