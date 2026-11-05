# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "hydrometrics"
copyright = "2024, Sergey Iglin"
author = "Sergey Iglin"

# The full version, including alpha/beta/rc tags
release = "0.1.0"
version = "0.1.0"

# -- Bilingual configuration -------------------------------------------------

# English language build
language = "en"

# Supported languages
languages = {
    "ru": "Русский",
    "en": "English",
}

# Directory structure for each language
# We use a flat structure with language-specific subdirectories
# docs/ru/ - Russian documentation
# docs/en/ - English documentation

# Root document for English build
root_doc = "en/index"
master_doc = "en/index"

# Source file suffixes
source_suffix = [".rst", ".md"]

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.todo",
    "myst_parser",
    "nbsphinx",
    "sphinx_copybutton",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb_checkpoints",
    # Obsolete summary pages (replaced by individual metric pages)
    "metric_reference/hydro_kge.md",
    "metric_reference/hydro_nse.md",
    "metric_reference/hydro_other.md",
    # Non-public metrics
    "ru/metric_reference/hydro/kge_np.md",
    "ru/metric_reference/hydro/pbias.md",
    "en/metric_reference/hydro/kge_np.md",
    "en/metric_reference/hydro/pbias.md",
    # Russian metric pages (built separately for Russian language)
    "ru/metric_reference/**",
    # Language-specific index pages (handled separately)
    "ru/index.md",
    "en/index.md",
    # Russian root files
    "index.md",
    "installation.md",
    "quickstart.md",
    "user_guide/**",
    "examples/**",
    "api_reference.md",
    "metric_reference/regression.md",
    "metric_reference/probabilistic.md",
    "metric_reference/classification.md",
]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
    "language_selector": True,
}

html_static_path = ["_static"]
html_logo = "_static/logo.svg"
html_favicon = "_static/logo.svg"

# Language-specific HTML options
html_baseurl = "https://hydrometrics.readthedocs.io/"

# -- Options for autodoc -----------------------------------------------------

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}

autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# -- Options for autosummary -------------------------------------------------

autosummary_generate = True
autosummary_imported_members = False

# -- Options for napoleon ----------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for MyST --------------------------------------------------------

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

myst_heading_anchors = 3

# -- Options for nbsphinx ----------------------------------------------------

nbsphinx_execute = "never"  # Don't execute notebooks during build
nbsphinx_allow_errors = True

# -- Intersphinx mapping -----------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "xarray": ("https://docs.xarray.dev/en/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
}

# -- Custom configuration ----------------------------------------------------

# Suppress specific warnings
suppress_warnings = [
    "autodoc.import_object",
    "toc.not_readable",
    "myst.xref_missing",
]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_css_files = [
    "custom.css",
]

# -- Setup -------------------------------------------------------------------

def setup(app):
    app.add_css_file("custom.css")
    
    # Add language switcher to the template context
    def add_language_links(app, pagename, templatename, context, doctree):
        if "current_language" not in context:
            context["current_language"] = getattr(app, "language", "en")
        context["languages"] = languages
    
    app.connect("html-page-context", add_language_links)