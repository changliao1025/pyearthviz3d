Quickstart
==========

This guide walks you through basic 3D visualizations using ``pyearthviz3d``, from interactive globe rendering to exporting static images and rotating animations.

1. Creating a Structured Mesh
-----------------------------

You can visualize standard latitude-longitude climate grids by transforming NumPy coordinate arrays into a spherical 3D surface using GeoVista:

.. code-block:: python

   import numpy as np
   import geovista as gv
   import pyearthviz3d as pev

   # Define regular coordinate grid (e.g. 73 lats x 144 lons)
   lats = np.linspace(-90, 90, 73)
   lons = np.linspace(-180, 180, 144)

   # Create synthetic temperature field
   lon2d, lat2d = np.meshgrid(lons, lats)
   temperature = 288.15 - 40.0 * np.sin(np.radians(np.abs(lat2d)))**2

   # Construct spherical mesh
   mesh = gv.Transform.from_1d(lons, lats, data=temperature, name="Temperature")
   valid_indices = np.arange(mesh.n_cells)

2. Displaying a Single Frame
----------------------------

Configure the camera and base layer, then render the 3D globe:

.. code-block:: python

   # Configure camera perspective
   config = pev.VisualizationConfig(
       longitude_focus=-95.0,
       latitude_focus=38.0,
       zoom_factor=0.75,
       show_coastlines=True,
       show_graticule=True,
       base_layer="natural_earth_hypsometric",
       colormap="coolwarm",
   )

   # Interactive view (pass sFilename_out=None to pop up an interactive 3D window)
   pev.map_single_frame(
       mesh,
       valid_indices,
       config,
       sScalar="Temperature",
       sUnit="K",
       sFilename_out=None,
   )

   # Or export directly to a high-resolution image
   pev.map_single_frame(
       mesh,
       valid_indices,
       config,
       sScalar="Temperature",
       sUnit="K",
       sFilename_out="temperature_snapshot.png",
   )

3. Overlaying Vector GIS Geometries
-----------------------------------

You can combine mesh layers with vector files (e.g., GeoJSON, Shapefile) such as shipping lanes, flight paths, or river networks:

.. code-block:: python

   # Define styling for vector layers
   vector_config = pev.VectorLayerConfig(
       color="gold",
       linewidth=2.5,
       layer_name="Trade Routes",
       z_order=10,
   )

   # Render composite scene
   pev.animate_mesh_with_vector_files(
       pMesh=mesh,
       aValid_cell_indices=valid_indices,
       sScalar="Temperature",
       sUnit="K",
       aFilename_vector_in="routes.geojson",
       aVector_config=vector_config,
       pConfig=config,
       sFilename_out="mesh_with_vectors.png",
   )

4. Creating a Rotating Globe Animation
--------------------------------------

To create a 360-degree rotation animation:

.. code-block:: python

   # Configure animation parameters
   anim_config = pev.AnimationConfig(
       frames=72,        # 72 frames for smooth rotation
       speed=5.0,        # 5 degrees per frame
       framerate=24,     # 24 FPS
       format="mp4",     # Output format: mp4 or gif
   )

   # Generate animation
   result = pev.animate_rotating_frames(
       mesh,
       valid_indices,
       config,
       anim_config,
       sScalar="Temperature",
       sUnit="K",
       sFilename_out="globe_rotation.mp4",
       return_detailed_result=True,
   )

   print(result.get_summary())

Interactive Mouse Controls
--------------------------

When running interactive modes (e.g., in Python scripts or Jupyter):

* **Left Click + Drag**: Rotate the globe in 3D space.
* **Scroll Wheel / Right Click + Drag**: Zoom into regions or surface details.
* **Shift + Left Click + Drag**: Pan the camera.
* **Key 'r'**: Reset camera view.
* **Key 'q'**: Close interactive viewer.
