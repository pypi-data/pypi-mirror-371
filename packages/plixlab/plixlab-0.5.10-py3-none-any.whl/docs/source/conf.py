# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import os
import sys
import shutil
import glob
from datetime import datetime
from setuptools_scm import get_version

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../../'))  # Add path to plixlab module

# -- Project information -----------------------------------------------------

project = 'plixlab'
author = 'Giuseppe Romano'
copyright = f"{datetime.now().year}, {author}"

try:
    
    release = get_version(root='../../', relative_to=__file__)
    release = '.'.join(release.split('.')[:3])

except Exception:
    release = '0.0.0+dev'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx_copybutton',
    'import_example',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
    'sphinx.ext.napoleon',
]

typehints_use_rtype = False
typehints_document_rtype = True

# Autosummary settings
autosummary_generate = True

# Templates
templates_path = ['_templates']

# Files to exclude
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------



html_theme = 'sphinx_book_theme'

html_favicon = '_static/favicon.ico'
html_static_path = ['_static']
html_css_files = ['custom.css']
