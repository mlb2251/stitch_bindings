# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'stitch_core'
copyright = '2022, Matt Bowers'
author = 'Matt Bowers'

release = '0.1.11'
version = '0.1.11'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_static_path = ['../static']

html_theme = 'sphinx_rtd_theme'

html_style = 'css/custom.css'

# -- Options for EPUB output
epub_show_urls = 'footnote'

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'css/custom.css',
]