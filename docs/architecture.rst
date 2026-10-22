Architecture & Design
=====================

``pyearthviz3d`` is built according to a strict **3-Tier Layering Hierarchy** designed to prevent circular dependencies, decouple data ingestion from graphics rendering, and ensure maintainability.

Layering Hierarchy
------------------

.. code-block:: text

   Tier 3: Interfaces & Pipelines
   (map_single_frame, animate_rotating_frames, animate_mesh_with_vector_files, ...)
                           │
                           ▼
   Tier 2: Core Domain & Transformation Engines
   (_camera, _mesh, _vector, _plotter)
                           │
                           ▼
   Tier 1: Primitives & Foundations
   (_config, _environment)
                           │
                           ▼
   External Dependencies
   (NumPy, GeoVista, PyVista, VTK, GDAL)

Key Architectural Principles
----------------------------

1. **Unidirectional Dependencies**: Higher tiers consume lower tiers, never vice versa. No module in Tier 1 or Tier 2 imports any pipeline module in Tier 3.
2. **Decoupled Engines**: Tier 2 modules (camera, mesh, vector, plotter) do not cross-import one another. Coordination occurs solely within Tier 3 pipeline orchestration.
3. **Decoupled Vector Ingestion**: The vector engine (``_vector.py``) operates as a pure data pipeline using GDAL/OGR and direct spherical trigonometry :math:`(\theta, \phi \to x, y, z)` to generate PyVista PolyData objects at :math:`O(N)` vector speed, avoiding iterative actor allocations.
4. **Standardized Config & Result Models**: All configuration options are encapsulated in validated dataclasses (``VisualizationConfig``, ``AnimationConfig``, ``ScalarBarConfig``, ``VectorLayerConfig``), and runs return structured result summaries (``SingleFrameResult``, ``AnimationResult``).
5. **Headless Execution Robustness**: Off-screen rendering and Xvfb detection are encapsulated in ``_environment.py``, preventing VTK segmentation faults when running inside containerized CI runners or remote headless compute nodes.
