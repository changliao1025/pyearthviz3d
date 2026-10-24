# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import re
import sys
from datetime import datetime
from unittest.mock import MagicMock

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here.
sys.path.insert(0, os.path.abspath(".."))

# Mock heavy binary / GUI / C-extension modules early in sys.modules so imports
# and Sphinx doc building succeed cleanly in any environment (including ReadTheDocs
# which does not have system libgdal-dev or OpenGL/VTK binaries).
MOCK_MODULES = [
    "osgeo",
    "osgeo.gdal",
    "osgeo.ogr",
    "osgeo.osr",
    "gdal",
    "ogr",
    "osr",
    "geovista",
    "geovista.geodesic",
    "geovista.theme",
    "pyvista",
    "pyvista.core",
    "pyvista.core.dataset",
    "vtk",
    "trame",
    "trame.widgets",
    "trame.widgets.html",
    "trame_vtk",
    "trame_vtk.modules",
    "trame_vtk.modules.vtk",
    "trame_vtk.modules.vtk.protocols",
    "trame_vtk.modules.vtk.protocols.mouse_handler",
    "trame_vuetify",
    "imageio",
]
for mod_name in MOCK_MODULES:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()


def get_version() -> str:
    """Safely extract __version__ from pyearthviz3d/__init__.py without side effects."""
    init_path = os.path.join(os.path.abspath(".."), "pyearthviz3d", "__init__.py")
    try:
        with open(init_path, encoding="utf-8") as f:
            match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', f.read(), re.M)
            if match:
                return match.group(1)
    except Exception:
        pass
    return "0.1.3"


# -- Project information -----------------------------------------------------
project = "pyearthviz3d"
author = "Chang Liao"
current_year = datetime.now().year
copyright = f"2022-{current_year}, Battelle Memorial Institute and Chang Liao"
release = get_version()
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "myst_parser",
]

# Optional copybutton if installed
try:
    import sphinx_copybutton  # noqa: F401

    extensions.append("sphinx_copybutton")
except ImportError:
    pass

# Mock list for Sphinx autodoc
autodoc_mock_imports = MOCK_MODULES

# Source suffix configuration
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document
master_doc = "index"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Napoleon settings for docstring parsing
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
}
autosummary_generate = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pyvista": ("https://docs.pyvista.org/", None),
}

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files.
html_static_path = ["_static"]
