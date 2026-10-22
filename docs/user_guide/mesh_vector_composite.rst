Mesh & Multi-Layer Vector Composites
====================================

Earth science workflows frequently require plotting 3D numerical model grids alongside GIS vector layers, such as watershed boundaries, river networks, flight routes, shipping corridors, or administrative borders.

The :func:`pyearthviz3d.animate_mesh_with_vector_files` pipeline is designed specifically for multi-layer composites.

VectorLayerConfig
-----------------

The :class:`pyearthviz3d.VectorLayerConfig` class provides per-layer control over line appearance, opacity, variable widths, and Z-ordering:

.. code-block:: python

   from pyearthviz3d import VectorLayerConfig

   flights_cfg = VectorLayerConfig(
       color="crimson",
       linewidth=2.0,
       opacity=0.9,
       layer_name="Commercial Flight Corridors",
       z_order=10,  # Render on top of base mesh
   )

   shipping_cfg = VectorLayerConfig(
       color="gold",
       linewidth=1.5,
       opacity=0.75,
       layer_name="Maritime Shipping Routes",
       z_order=5,
   )

Variable Line Width from Attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can dynamically scale line thickness based on feature attributes in your GIS file (such as stream order or traffic volume):

.. code-block:: python

   rivers_cfg = VectorLayerConfig(
       color="royalblue",
       linewidth_attribute="stream_order",
       linewidth_range=(0.8, 4.5), # Scale stream orders from 0.8px to 4.5px
       layer_name="River Network",
       z_order=15,
   )

Combining Mesh and Vectors
--------------------------

Pass the list of vector file paths and their matching configurations to :func:`pyearthviz3d.animate_mesh_with_vector_files`:

.. code-block:: python

   import pyearthviz3d as pev

   # Setup configurations
   viz_config = pev.VisualizationConfig(
       longitude_focus=10.0,
       latitude_focus=20.0,
       zoom_factor=0.8,
       base_layer="blue_marble",
   )

   # Vector files and their respective style configs
   vector_files = ["data/routes_air.geojson", "data/routes_sea.geojson"]
   vector_configs = [flights_cfg, shipping_cfg]

   # Composite rendering
   pev.animate_mesh_with_vector_files(
       pMesh=mesh,
       aValid_cell_indices=valid_indices,
       sScalar="elevation",
       sUnit="m",
       aFilename_vector_in=vector_files,
       aVector_config=vector_configs,
       pConfig=viz_config,
       sFilename_out="composite_mesh_vector.png",
   )

Supported Vector File Formats
-----------------------------

Through GDAL/OGR integration, ``pyearthviz3d`` supports all standard GIS formats:
* GeoJSON (``.geojson``, ``.json``)
* ESRI Shapefile (``.shp``)
* OGC GeoPackage (``.gpkg``)
* Keyhole Markup Language (``.kml``)
* GPS Exchange Format (``.gpx``)

Coordinates are automatically transformed to the WGS84 spherical coordinate system.
