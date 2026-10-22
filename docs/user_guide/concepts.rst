Core Concepts
=============

Understanding how ``pyearthviz3d`` coordinates between GeoVista, PyVista, VTK, and GIS vectors is key to making the most of the package.

Spherical Coordinate Representation
-----------------------------------

Traditional 2D mapping libraries project geographic coordinates :math:`(\lambda, \phi)` onto a flat plane using cartographic projections (e.g. Plate Carrée, Mercator, Robinson). While convenient for 2D paper maps, planar projections distort area, angles, or distances near the poles and break continuity across the antimeridian (:math:`\pm 180^\circ`).

``pyearthviz3d`` visualizes data directly in 3D Cartesian coordinates :math:`(x, y, z)` on a sphere of radius :math:`R`:

.. math::

   x = R \cos(\phi) \cos(\lambda)

   y = R \cos(\phi) \sin(\lambda)

   z = R \sin(\phi)

where :math:`\lambda` is longitude (radians) and :math:`\phi` is latitude (radians).

By mapping data onto a true 3D manifold, polar singularities and antimeridian seams are naturally eliminated, allowing seamless global inspection and rotating views.

The Three-Tier Architecture
---------------------------

The codebase is structured around a strict 3-tier layering model:

1. **Tier 1: Primitives & Foundations** (``_config.py``, ``_environment.py``)
   Houses immutable data classes (``VisualizationConfig``, ``AnimationConfig``, ``ScalarBarConfig``, ``VectorLayerConfig``, ``AnimationResult``), parameter validators, and headless/Xvfb system diagnostics. Tier 1 has zero dependencies on rendering or pipeline logic.

2. **Tier 2: Core Domain & Transformation Engines** (``_camera.py``, ``_mesh.py``, ``_vector.py``, ``_plotter.py``)
   Pure algorithmic engines focused on single responsibilities:
   * **CameraController**: Computes 3D camera look-at rays, position vectors, and orbit paths.
   * **MeshHandler**: Extracts valid cell subsets, validates scalar field bounds, and maps continuous/discrete colormaps.
   * **Vector Engine**: Reads GIS formats via GDAL/OGR and reprojects geometries into 3D Cartesian spherical ``pv.PolyData`` lines at :math:`O(N)` efficiency.
   * **PlotterManager**: Instantiates GeoPlotters with graceful fallback strategies and attaches contextual layers (coastlines, textures, graticules).

3. **Tier 3: Interfaces & Pipelines** (``map_single_frame.py``, ``animate_rotating_frames.py``, ``animate_mesh_with_vector_files.py``, etc.)
   User-facing high-level functions orchestrating Tier 2 engines to produce interactive windows, image exports, or movie sequences.

Supported Mesh Types
--------------------

Structured Grids
~~~~~~~~~~~~~~~~
Regular or rectilinear latitude-longitude grids (e.g., from CMIP6, ERA5, GFS NetCDF files). Created using ``geovista.Transform.from_1d(lons, lats, data=...)`` or ``Transform.from_2d(lons_2d, lats_2d, data=...)``.

Unstructured Meshes
~~~~~~~~~~~~~~~~~~~
Flexible polygonal grids commonly used in modern Earth system models (MPAS, FVCOM, ICON, geodesic icosahedral grids, UGRID-1.0 standards). Created using ``geovista.Transform.from_unstructured(lons, lats, connectivity=..., data=...)``.
Mesh cell edges can be highlighted by setting ``show_edges=True`` in ``map_single_frame``.
