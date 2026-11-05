"""Generate the metric pages written so far and orphan stubs for the metrics still to be done."""
from lib import DOCS, save_tm
import metricpage as mp
import specs_after as sa
import specs_hydro as sh
import specs_nse as sn
import specs_prob as sp
import specs_regr as sr
from helpers_page import helpers_page
from index_page import index_page
import userguide_pages
import userguide_pages2
from front_page import front_page
import glossary_page
import api_pages
import known_limits_page
from inventory_probe import ALL_METRICS

# name -> spec; the order is the order in the index toctree
SPECS = {"nse": sa.NSE, "kge_2012": sa.KGE12, "crps": sa.CRPS, **sp.FAMILY4, **sn.FAMILY3, **sr.FAMILY2, **sh.FAMILY1}

sa.NSE["hydro"] = []
doc = mp.metric_page(sa.NSE)
sa._s.NSE["hydro"] = sa._s.nse_hydro(doc.ns)
for name, spec in SPECS.items():
    mp.metric_page(spec).write()
helpers_page().write()

for name in ALL_METRICS:
    if name not in SPECS:
        (DOCS / "metrics" / f"{name}.rst").write_text(f":orphan:\n\n.. _metric-{name}:\n\n{name}\n{'=' * len(name)}\n", encoding="utf-8")


def write(path, text):
    p = DOCS / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


index_page(SPECS).write()
for page in userguide_pages.all_pages() + userguide_pages2.all_pages():
    page.write()
front_page().write()
glossary_page.glossary_page().write()
glossary_page.write_markdown()
known_limits_page.known_limits_page().write()
for page in api_pages.all_pages():
    page.write()
write("examples/GALLERY_HEADER.rst", "Примеры\n=======\n")
save_tm()
print("ok", len(SPECS), "pages")
