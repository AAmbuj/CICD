# ******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

"""Configuration file for the Sphinx documentation builder for CICD project.

This project demonstrates a simple CI/CD pipeline with Bazel and GitHub Actions,
including quality tools for C++ development.
"""

import os
import sys

# -- Project information --
project = 'CICD'
copyright = '2026, Contributors'
author = 'Contributors'
release = '1.0.0'

# GitHub Pages base URL is injected by the Pages workflow.
DOCS_BASE_URL = os.environ.get('DOCS_BASE_URL')

# -- General configuration ---
extensions = [
    'sphinx.ext.autodoc',      # Auto-generate documentation from docstrings
    'sphinx.ext.napoleon',     # Support for NumPy and Google style docstrings
    'sphinx.ext.viewcode',     # Add links to highlighted source code
    'myst_parser',             # Support for Markdown files
]

# MyST Parser configuration
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# MyST parser settings
myst_heading_anchors = 3
myst_enable_extensions = []
suppress_warnings = [
    'myst.xref_missing',
    'myst.anchor',
]
myst_commonmark_only = False
myst_all_links_external = False

# Add any paths that contain templates here
templates_path = ['_templates']

# List of patterns to ignore when looking for source files
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output --
html_theme = 'pydata_sphinx_theme'
if DOCS_BASE_URL:
    html_baseurl = DOCS_BASE_URL

# Professional theme configuration inspired by modern open-source projects
html_theme_options = {
    # Navigation settings
    'navigation_depth': 4,
    'collapse_navigation': False,
    'show_nav_level': 2,
    'show_toc_level': 2,

    # Header layout
    'navbar_align': 'left',
    'navbar_start': ['navbar-logo'],
    'navbar_center': ['navbar-nav'],
    'navbar_end': ['theme-switcher'],

    # Search configuration
    'search_bar_text': 'Search documentation...',

    # Footer configuration
    'footer_start': ['copyright'],
    'footer_end': ['sphinx-version'],

    # Navigation buttons
    'show_prev_next': True,
    'navigation_with_keys': False,

    # Logo configuration
    'logo': {
        'text': 'CICD',
    },

}

# Add custom styling
html_static_path = ['_static']
html_css_files = [
    'css/default_custom.css',
]
html_js_files = []
