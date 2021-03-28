# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from setuptools.config import read_configuration

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../wsiprocess'))


# -- Project information -----------------------------------------------------

project = 'wsiprocess'
copyright = '2021, Takumi Ando'
author = 'Takumi Ando'

# The short X.Y version
version = 'v0.8'

# The full version, including alpha/beta/rc tags
release = 'v0.8'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.autodoc',
    'sphinxemoji.sphinxemoji'
]
conf = read_configuration("../setup.cfg")
autodoc_mock_imports = [i.strip() for i in conf["options"]["install_requires"]]
autodoc_mock_imports.extend(["cv2", "openslide"])

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    'wsiprocess/cli.py',
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['../images']

# -- Master doc renamed ------------------------------------------------------
master_doc = 'wsiprocess'
