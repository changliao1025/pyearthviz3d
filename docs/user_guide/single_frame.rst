Single Frame Visualization
===========================

The primary entry point for static and interactive 3D visualizations is :func:`pyearthviz3d.map_single_frame`.

Function Overview
-----------------

.. code-block:: python

   from pyearthviz3d import map_single_frame, VisualizationConfig, ScalarBarConfig

   result = map_single_frame(
       pMesh=mesh,
       aValid_cell_indices=valid_indices,
       pConfig=config,
       style="surface",
       sScalar="temperature",
       sUnit="K",
       sFilename_out="globe.png",
       scalar_config=None,
       validate_inputs=True,
       retry_on_failure=True,
       return_detailed_result=False,
       show_edges=False,
       edge_color="black",
   )

Configuring the View
--------------------

The :class:`pyearthviz3d.VisualizationConfig` controls the camera viewpoint, globe styling, overlays, and rendering backend:

.. code-block:: python

   config = VisualizationConfig(
       longitude_focus=-120.0,    # Longitude centered in view (-180 to 180)
       latitude_focus=35.0,       # Latitude centered in view (-90 to 90)
       zoom_factor=0.8,           # Camera zoom (higher values zoom in)
       show_coastlines=True,      # Render global coastlines
       show_graticule=True,       # Render coordinate lines (parallels and meridians)
       coastline_color="black",   # Color for coastline paths
       coastline_width=1.0,       # Width of coastline paths
       base_layer="natural_earth_hypsometric", # Globe texture
       colormap="viridis",        # Colormap for scalar field
       window_size=(1024, 768),   # Resolution of output window / snapshot
   )

Available Base Layer Textures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``base_layer`` argument supports the following options:

* ``None``: Clean blank globe (only your mesh and coastlines are visible).
* ``"natural_earth_hypsometric"``: Natural Earth shaded relief with hypsometric tints (default).
* ``"natural_earth_1"``: Natural Earth I satellite-style basemap.
* ``"blue_marble"``: NASA Blue Marble texture.

Mesh Edge Highlighting
-----------------------

When working with unstructured grids (such as MPAS or geodesic meshes), inspecting cell boundaries is essential. Pass ``show_edges=True`` and choose an ``edge_color``:

.. code-block:: python

   map_single_frame(
       mesh,
       valid_indices,
       config,
       sScalar="vorticity",
       show_edges=True,
       edge_color="white",
       sFilename_out="unstructured_mesh_edges.png",
   )

Detailed Result Diagnostics
---------------------------

By setting ``return_detailed_result=True``, ``map_single_frame`` returns an instance of :class:`pyearthviz3d.SingleFrameResult` rather than a simple boolean:

.. code-block:: python

   result = map_single_frame(
       mesh,
       valid_indices,
       config,
       sScalar="temperature",
       sFilename_out="output.png",
       return_detailed_result=True,
   )

   if result.success:
       print(result.get_summary())
       print(f"Generated file: {result.file_info.get('filename')}")
       print(f"File size: {result.file_info.get('size_kb'):.2f} KB")
   else:
       print(f"Error: {result.message}")
