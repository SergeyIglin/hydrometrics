"""Fill docs/locale/{en,ru} catalogs from the translation memory; drop obsolete entries."""
from __future__ import annotations

import json
import pathlib
import re
import sys

from babel.messages.pofile import read_po, write_po

HERE = pathlib.Path(__file__).parent
DOCS = pathlib.Path(__file__).resolve().parents[2]
TM = json.loads((HERE / "tm.json").read_text(encoding="utf-8"))
RU_PATH = HERE / "tm_ru.json"
TM_RU = json.loads(RU_PATH.read_text(encoding="utf-8")) if RU_PATH.exists() else {}
CYR = re.compile(r"[А-Яа-яЁё]")


def norm(s: str) -> str:
    return " ".join(s.split())


NORM_TM = {norm(k): v for k, v in TM.items()}
NORM_RU = {norm(k): v for k, v in TM_RU.items()}
missing, missing_ru = [], []

for po in sorted((DOCS / "locale" / "en" / "LC_MESSAGES").rglob("*.po")):
    with open(po, "rb") as fh:
        cat = read_po(fh, locale="en")
    cat.obsolete.clear()
    for msg in cat:
        if not msg.id:
            continue
        msg.flags.discard("fuzzy")
        msg.previous_id = []
        if msg.id in TM:
            msg.string = TM[msg.id]
        elif norm(msg.id) in NORM_TM and "\n" not in msg.id:
            msg.string = NORM_TM[norm(msg.id)]
        elif not CYR.search(msg.id):
            msg.string = msg.id
        else:
            msg.string = ""
            missing.append((po.name, msg.id[:110]))
    with open(po, "wb") as fh:
        write_po(fh, cat, width=0, omit_header=False, sort_output=False, include_previous=False)

# The Russian catalog holds only source strings written in English (docstrings, extensions).
ru_dir = DOCS / "locale" / "ru" / "LC_MESSAGES"
ru_dir.mkdir(parents=True, exist_ok=True)
for po in sorted((DOCS / "locale" / "en" / "LC_MESSAGES").rglob("*.po")):
    with open(po, "rb") as fh:
        cat = read_po(fh, locale="ru")
    out = ru_dir / po.relative_to(DOCS / "locale" / "en" / "LC_MESSAGES")
    keep = []
    for msg in cat:
        if not msg.id or CYR.search(msg.id):
            continue
        tr = TM_RU.get(msg.id) or NORM_RU.get(norm(msg.id))
        if tr:
            keep.append((msg.id, tr))
        elif re.search(r"[A-Za-z]{3}", msg.id) and po.stem in ("api", "auto_examples") and " " in msg.id:
            missing_ru.append((po.name, msg.id[:110]))
    new = read_po(iter(['msgid ""\n', 'msgstr "Content-Type: text/plain; charset=UTF-8\\n"\n']), locale="ru")
    for mid, tr in keep:
        new.add(mid, tr)
    if keep:
        with open(out, "wb") as fh:
            write_po(fh, new, width=0)
    elif out.exists():
        out.unlink()

print("en missing:", len(missing))
for name, mid in missing[:int(sys.argv[1]) if len(sys.argv) > 1 else 40]:
    print("  ", name, "|", mid)
print("ru (english sources) missing:", len(missing_ru))
(HERE / "missing_ru.json").write_text(json.dumps(missing_ru, ensure_ascii=False, indent=0), encoding="utf-8")
(HERE / "missing_en.json").write_text(json.dumps(missing, ensure_ascii=False, indent=0), encoding="utf-8")
