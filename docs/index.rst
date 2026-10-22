.. pyearthviz3d documentation master file

Welcome to PyEarthViz3D's Documentation!
========================================

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.18827302.svg
   :target: https://doi.org/10.5281/zenodo.18827302
   :alt: DOI
.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/bjlittle/geovista/main/docs/assets/badge/v0.json
   :target: https://geovista.readthedocs.io/
   :alt: geovista
.. image:: https://img.shields.io/badge/license-BSD%203--Clause-blue.svg
   :target: https://opensource.org/licenses/BSD-3-Clause
   :alt: License

**PyEarthViz3D** is a Python package designed for high-performance 3D visualization of Earth science and geospatial data on a spherical globe. Built on top of `GeoVista <https://github.com/bjlittle/geovista>`_ and `PyVista <https://github.com/pyvista/pyvista>`_, it provides clean, robust pipelines for rendering structured grids, unstructured meshes (such as MPAS or geodesic grids), and multi-layer vector GIS geometries directly on a 3D Earth sphere.

Part of the PyEarthSuite Ecosystem
----------------------------------
PyEarthViz3D is a core component of the modular **PyEarthSuite**:

* `pyearth <https://github.com/changliao1025/pyearth>`_ — Core GIS operations, spatial toolbox, and system utilities.
* `pyearthviz <https://github.com/changliao1025/pyearthviz>`_ — 2D geospatial plotting and cartographic tools.
* **pyearthviz3d** (this package) — 3D globe visualization with GeoVista.
* `pyearthriver <https://github.com/changliao1025/pyearthriver>`_ — River network graph algorithms and data structures.
* `pyearthmesh <https://github.com/changliao1025/pyearthmesh>`_ — Mesh generation and manipulation tools.
* `pyearthhelp <https://github.com/changliao1025/pyearthhelp>`_ — Data access helpers (NWIS, NLDI, GSIM) and HPC utilities.

Key Features
------------
* **Spherical Mesh Mapping**: Native rendering of structured climate grids and unstructured polygonal/geodesic meshes on spherical Earth geometry.
* **Multi-Layer Vector GIS Overlays**: Direct plotting of Shapefiles, GeoJSON, and GeoPackages (lines, points, polygons) with customizable line widths, colors, and Z-order layering.
* **Dynamic Animations**: Seamless creation of rotating globe animations and time-series transitions saved as MP4, GIF, or AVI.
* **Configurable Scalar Bars**: Flexible colorbars supporting continuous gradients and discrete categorical swatches with custom labels.
* **Headless & Cloud-Ready**: Automated detection of headless environments with transparent virtual framebuffer (Xvfb) configuration for Linux CI/CD and servers.
* **Interactive Jupyter Integration**: Seamless 3D mouse interaction (rotate, zoom, pan) inside JupyterLab and VS Code via WebGL backends.

Quick Example
-------------

.. code-block:: python

   import pyearthviz3d as pev
   import geovista as gv

   # Load or create a mesh
   mesh = gv.Transform.from_1d(lons, lats, data=temperature, name="Temperature")
   valid_indices = ... # array of cell indices to display

   # Configure camera view
   config = pev.VisualizationConfig(
       longitude_focus=-100.0,
       latitude_focus=40.0,
       zoom_factor=0.8,
       base_layer="blue_marble",
   )

   # Render single frame (or save to PNG)
   pev.map_single_frame(
       mesh,
       valid_indices,
       config,
       sScalar="Temperature",
       sUnit="K",
       sFilename_out="temperature_globe.png",
   )

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started/installation
   getting_started/quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/index
   user_guide/concepts
   user_guide/single_frame
   user_guide/mesh_vector_composite
   user_guide/animations
   user_guide/scalar_bars
   user_guide/headless_and_cloud

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index
   api/pipelines
   api/configuration
   api/engines

.. toctree::
   :maxdepth: 1
   :caption: Architecture & Development

   architecture
   contributing

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
