# Unstructured Earth Science Data

This directory contains unstructured flexible mesh datasets (geodesic triangulation) formatted according to **UGRID-1.0** and **VTK PolyData** conventions for spherical Earth visualization.

## Dataset Specification

### 1. `unstructured_geodesic_mesh.nc`
- **Format**: NetCDF-4
- **Conventions**: CF-1.8, UGRID-1.0 (Unstructured Grid Conventions for Earth System Models)
- **Mesh Type**: Spherical Icosahedral Subdivision Triangulation
- **Topology Elements**:
  - `nMesh2_node`: 642 nodes on the unit sphere
  - `nMesh2_face`: 1,280 triangular faces
  - `nMaxMesh2_face_nodes`: 3 nodes per face

#### Topology & Data Variables

| Variable Name | Dimensions | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `Mesh2` | *Scalar* | `cf_role="mesh_topology"`, `topology_dimension=2`, `node_coordinates="Mesh2_node_x Mesh2_node_y"`, `face_node_connectivity="Mesh2_face_nodes"` | UGRID topology container descriptor |
| `Mesh2_node_x` | `(nMesh2_node: 642)` | `units="degrees_east"`, `standard_name="longitude"` | Longitude of mesh vertices |
| `Mesh2_node_y` | `(nMesh2_node: 642)` | `units="degrees_north"`, `standard_name="latitude"` | Latitude of mesh vertices |
| `Mesh2_face_nodes` | `(nMesh2_face: 1280, 3)` | `cf_role="face_node_connectivity"`, `start_index=0` | 0-based face-to-node vertex index connectivity |
| `vorticity` | `(nMesh2_face: 1280)` | `units="s-1"`, `mesh="Mesh2"`, `location="face"` | Relative vorticity field defined on cell faces |
| `sea_surface_height` | `(nMesh2_face: 1280)` | `units="m"`, `mesh="Mesh2"`, `location="face"` | Dynamic ocean sea surface height anomaly |

---

### 2. `unstructured_geodesic_mesh.vtk`
- **Format**: Legacy VTK PolyData (ASCII / Binary)
- **Structure**: Pre-computed 3D Cartesian coordinates $(x, y, z)$ on the unit sphere, triangle connectivity cells, and embedded cell attributes (`vorticity`, `sea_surface_height`).
- **Purpose**: Direct zero-overhead loading via `pyvista.read()` or GeoVista without needing external NetCDF UGRID parsers.

---

## Python Usage Example

```python
import netCDF4 as nc
import geovista as gv
import numpy as np
from pyearthviz3d import map_single_frame, VisualizationConfig

# 1. Load UGRID coordinates and connectivity
with nc.Dataset("data/unstructured/unstructured_geodesic_mesh.nc") as ds:
    lons = ds.variables["Mesh2_node_x"][:]
    lats = ds.variables["Mesh2_node_y"][:]
    connectivity = ds.variables["Mesh2_face_nodes"][:]
    vorticity = ds.variables["vorticity"][:]

# 2. Build 3D spherical mesh from unstructured connectivity
mesh = gv.Transform.from_unstructured(
    xs=lons,
    ys=lats,
    connectivity=connectivity,
    data=vorticity,
    name="vorticity",
    start_index=0
)

# 3. Visualize with mesh edges highlighted
config = VisualizationConfig(longitude_focus=15.0, latitude_focus=30.0, colormap="coolwarm")
map_single_frame(
    mesh, np.arange(mesh.n_cells), config,
    sScalar="vorticity", sUnit="s⁻¹", show_edges=True, edge_color="dimgray"
)
```
