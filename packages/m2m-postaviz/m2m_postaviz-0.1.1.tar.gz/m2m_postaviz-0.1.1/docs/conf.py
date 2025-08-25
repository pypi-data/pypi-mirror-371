import os

extensions = [
    'sphinx_rtd_theme',
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]
source_suffix = ".rst"
master_doc = "index"
project = "m2m-postaviz"
year = "2023"
author = "Léonard Brindel, Clémence Frioux"
copyright = f"{year}, {author}"
version = release = "0.1.1"

pygments_style = "trac"
templates_path = ["."]
extlinks = {
    "issue": ("https://gitlab.inria.fr/postaviz/m2m-postaviz/issues/%s", "#"),
    "pr": ("https://gitlab.inria.fr/postaviz/m2m-postaviz/pull/%s", "PR #"),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

if not on_rtd:  # only set the theme if we are building docs locally
    html_theme = "sphinx_rtd_theme"

html_use_smartypants = True
html_last_updated_fmt = "%b %d, %Y"
html_split_index = False
html_sidebars = {
    "**": ["searchbox.html", "globaltoc.html", "sourcelink.html"],
}
html_short_title = f"{project}-{version}"

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False

html_theme = "sphinx_rtd_theme"