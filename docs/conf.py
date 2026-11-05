"""Конфигурация Sphinx для документации hydrometrics.

Базовый язык исходных текстов русский, английская версия собирается через
gettext: ``sphinx-build -b html -D language=en docs docs/_build/html/en``.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import hydrometrics  # noqa: E402

project = "hydrometrics"
author = "Sergey Iglin"
copyright = "2026, Sergey Iglin"  # noqa: A001
version = hydrometrics.__version__
release = hydrometrics.__version__

language = "ru"
locale_dirs = ["locale"]
gettext_compact = True
gettext_uuid = False
gettext_location = False
# Литеральные блоки тоже переводятся: в примерах кода есть русские комментарии.
gettext_additional_targets = ["literal-block", "doctest-block"]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.intersphinx",
    "sphinx.ext.doctest",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_gallery.gen_gallery",
    "sphinxcontrib.bibtex",
]

root_doc = "index"
source_suffix = {".rst": "restructuredtext"}
templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "_dev",
    "_legacy",
    "auto_examples/*.ipynb",
    "auto_examples/*.py",
    "auto_examples/*.codeobj.json",
    "auto_examples/*.zip",
    "auto_examples/*.md5",
    "examples/GALLERY_HEADER.rst",
]

# Литература
bibtex_bibfiles = ["references.bib"]
bibtex_default_style = "plain"
bibtex_reference_style = "author_year"
bibtex_foot_reference_style = "foot"

# Автодокументация
autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "none"
napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_use_rtype = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "polars": ("https://docs.pola.rs/api/python/stable/", None),
    "xarray": ("https://docs.xarray.dev/en/stable/", None),
}
intersphinx_timeout = 30

# Исполняемые примеры
doctest_global_setup = """
import warnings
warnings.simplefilter("ignore", RuntimeWarning)
"""
doctest_test_doctest_blocks = ""

sphinx_gallery_conf = {
    "examples_dirs": "examples",
    "gallery_dirs": "auto_examples",
    "filename_pattern": r"/plot_",
    "abort_on_example_error": True,
    "download_all_examples": False,
    "write_computation_times": False,
    "show_memory": False,
    "remove_config_comments": True,
    "within_subsection_order": "FileNameSortKey",
    "matplotlib_animations": False,
}

# Подсказка копированию: приглашения и вывод не копируются.
copybutton_exclude = ".linenos, .gp, .go"

# Оформление
html_theme = "pydata_sphinx_theme"
html_title = "hydrometrics"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_logo = "_static/logo.png"
html_show_sourcelink = False
html_theme_options = {
    "github_url": "https://github.com/SergeyIglin/hydrometrics",
    "navbar_end": ["lang-switch", "theme-switcher", "navbar-icon-links"],
    "show_toc_level": 2,
    "navigation_with_keys": False,
    "use_edit_page_button": False,
}
html_sidebars = {"index": []}

# Переключатель языка. На RTD адрес строится от канонического URL перевода.
_canonical = os.environ.get("READTHEDOCS_CANONICAL_URL", "")
_match = re.match(r"(https?://[^/]+/)([^/]+)/([^/]+)/?$", _canonical)
html_context = {
    "rtd_root": _match.group(1) if _match else "",
    "rtd_version": _match.group(3) if _match else "",
}
if _canonical:
    html_baseurl = _canonical

linkcheck_timeout = 30
linkcheck_retries = 2
linkcheck_workers = 4
# Издатели отвечают 403 автоматическим клиентам; DOI проверяются check_dois.py.
linkcheck_ignore = [
    r"https://doi\.org/.*",
    r"https://github\.com/SergeyIglin/hydrometrics.*",
    r"https://hydrometrics\.readthedocs\.io.*",
]

suppress_warnings = ["config.cache"]
