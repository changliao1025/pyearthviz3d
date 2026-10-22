Examples Gallery
================

The ``examples/`` directory in the repository provides practical scripts illustrating both **interactive 3D exploration** and **file export** modes.

Runnable Example Scripts
------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Script
     - Data Type
     - Description
   * - ``00_export_sample_data.py``
     - NetCDF & GeoJSON
     - Generates structured NetCDF, unstructured UGRID geodesic NetCDF, and GeoJSON corridors into ``data/``.
   * - ``01_single_frame_structured_mesh.py``
     - Structured NetCDF-4
     - Visualizes global climate grids (73x144) on a 3D spherical globe with custom colormaps and camera positioning.
   * - ``02_unstructured_geodesic_mesh.py``
     - Unstructured UGRID-1.0
     - Renders a 1,280-face triangular geodesic mesh with cell edge wireframes highlighted.
   * - ``03_mesh_with_vector_overlays.py``
     - Mesh + GeoJSON Lines
     - Composite scene overlaying aviation and maritime corridors on 3D terrain using ``VectorLayerConfig``.
   * - ``04_discrete_scalar_colorbar.py``
     - Categorical NetCDF
     - Discrete land-use / land-cover classification with custom color swatches and annotated labels.
   * - ``05_rotating_animation.py``
     - Animated Mesh
     - Renders preview snapshots and generates smooth 360-degree rotating MP4 / GIF animations.

Running the Examples
--------------------

Interactive Exploration
~~~~~~~~~~~~~~~~~~~~~~~

To launch an interactive 3D window (enabling mouse rotation, pan, and zoom):

.. code-block:: bash

   # Structured climate mesh
   python examples/01_single_frame_structured_mesh.py --interactive

   # Unstructured geodesic mesh with cell edges
   python examples/02_unstructured_geodesic_mesh.py --interactive

   # Composite 3D mesh with vector GIS layers
   python examples/03_mesh_with_vector_overlays.py --interactive

   # Categorical discrete classification
   python examples/04_discrete_scalar_colorbar.py --interactive

Exporting High-Resolution Images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To save the visualization directly to an image:

.. code-block:: bash

   python examples/01_single_frame_structured_mesh.py --export my_globe.png
   python examples/02_unstructured_geodesic_mesh.py --export my_unstructured.png
   python examples/03_mesh_with_vector_overlays.py --export composite.png
   python examples/04_discrete_scalar_colorbar.py --export discrete.png

Exporting Rotating Animation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To generate preview frames and render a rotating video:

.. code-block:: bash

   python examples/05_rotating_animation.py

Jupyter Notebooks
-----------------

Interactive Jupyter notebooks mirroring each example script are available in ``notebooks/``:

* ``01_single_frame_structured_mesh.ipynb``
* ``02_unstructured_geodesic_mesh.ipynb``
* ``03_mesh_with_vector_overlays.ipynb``
* ``04_discrete_scalar_colorbar.ipynb``
* ``05_rotating_animation.ipynb``
