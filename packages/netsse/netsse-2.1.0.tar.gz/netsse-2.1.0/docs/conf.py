# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'NetSSE'
copyright = '2023-2025 Technical University of Denmark, Raphaël E. G. Mounet'
author = 'REGMO'

release = 'latest'
version = '2.1'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx_copybutton',
    'autoapi.extension',
    'sphinx_design',
    'myst_nb',
]

todo_include_todos = True

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']
exclude_patterns = ["_build"]

numfig = True

# -- Internationalisation
# specifying the natural language populates some key tags
language = "en"

# -- Options for HTML output

html_theme = 'pydata_sphinx_theme'
html_logo = '_static/NetSSE_2_logo_bare-03.png'
html_favicon = '_static/NetSSE_2_logo_bare-03.png'
html_context = {
    "gitlab_url": "https://gitlab.gbar.dtu.dk",
    "gitlab_user": "regmo",
    "gitlab_repo": "NetSSE",
    "gitlab_version": "master",
    "doc_path": "docs/",
}
html_static_path = ["_static"]
html_css_files = [
    'css/custom.css',
]
html_js_files = [
   "pypi-icon.js",
]
html_last_updated_fmt = ''
html_theme_options = {
"navbar_start": ["navbar-logo", "version"],
# "sidebarwidth": 270,
"article_header_end": ["last-updated"],
"logo": {
    # Because the logo is also a homepage link, including "home" in the
    # alt text is good practice
    "image_light": "NetSSE_2_logo_bare-01.png",
    "image_dark": "NetSSE_2_logo_bare-02.png",
    "text": "NetSSE",
    "alt_text": "NetSSE Documentation - Home",
},
"announcement": "NetSSE has a newsletter through which updates are sent occasionally.\
                 For more information and sign-up, please visit\
                 <a href='http://eepurl.com/iSaEus'>this page</a>.",
"icon_links": [
    {
        "name": "GitLab",
        "url": "https://gitlab.gbar.dtu.dk/regmo/NetSSE",
        "icon": "fa-brands fa-square-gitlab",
        "type": "fontawesome",
    },
    {
        "name": "PyPI",
        "url": "https://pypi.org/project/netsse/",
        "icon": "fa-custom fa-pypi",
        "type": "fontawesome",
    },
    {
        "name": "DTU Data",
        "url": "https://doi.org/10.11583/DTU.26379811",
        "icon": "_static/DTU_Red.svg",
        "type": "local",
    },
],
"icon_links_label": "Quick Links",
"use_edit_page_button": True,
"footer_start": ["copyright",],
"footer_center": ["sphinx-version"],
}

# -- Options for autosummary/autodoc output
autosummary_generate = True  # Turn on sphinx.ext.autosummary
numpydoc_show_class_members = False
# autodoc_typehints = "description"
# autodoc_member_order = "groupwise"

# -- Options for autoapi 
autoapi_type = "python"
autoapi_dirs = ["../src/netsse"]
autoapi_keep_files = False
autoapi_root = "api"
autoapi_options = ['members','inherited-members','private-members','show-inheritance',\
                   'show-module-summary',]
# autoapi_member_order = "groupwise"
autoapi_own_page_level = "method"
autoapi_python_class_content = "init"

# -- Options for EPUB output
epub_show_urls = 'footnote'

# -- Options for PDF LaTeX output
# sd_fontawesome_latex = True

# -- Napoleon settings
napoleon_type_aliases = {
    "array-like": ":term:`array-like <array_like>`",
    "array_like": ":term:`array_like`",
}

# -- myst_nb options
nb_execution_allow_errors = True  # Allow errors in notebooks, to see the error online
nb_execution_mode = "auto"
nb_merge_streams = True
myst_enable_extensions = ["colon_fence", "linkify", "substitution","dollarmath", "amsmath"]
myst_dmath_double_inline = True
myst_heading_anchors = 2
myst_substitutions = {"rtd": "[Read the Docs](https://readthedocs.org/)"}