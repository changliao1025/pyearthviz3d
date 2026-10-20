# Sample Earth Science Datasets

This directory provides structured, unstructured, and vector geospatial datasets formatted for testing and demonstrating `pyearthviz3d` pipelines without external network dependencies.

## Directory Structure

```
data/
├── README.md                          # Directory overview and index (this file)
│
├── structured/                        # Structured grid datasets (CF-1.8 NetCDF)
│   ├── README.md                      # Detailed metadata, dimensions, and usage instructions
│   └── structured_global_climate.nc   # Rectilinear lat/lon grid (73 x 144, 2.5°) with T, elevation, wind
│
├── unstructured/                      # Unstructured mesh datasets (UGRID-1.0 & VTK)
│   ├── README.md                      # Topology conventions, node/face indexing, and usage instructions
│   ├── unstructured_geodesic_mesh.nc  # 1,280-face triangular geodesic mesh with vorticity & SSH
│   └── unstructured_geodesic_mesh.vtk # Direct VTK PolyData representation of the spherical geodesic mesh
│
└── vector/                            # Vector GIS line overlays (GeoJSON)
    ├── README.md                      # Feature schemas, properties, and styling guidelines
    ├── flight_routes.geojson          # Intercontinental aviation corridors
    └── shipping_routes.geojson        # Maritime navigation routes & chokepoints
```

---

## Subdirectory Details

| Subdirectory | Standards | Primary Datasets | Target Pipelines |
| :--- | :--- | :--- | :--- |
| [`structured/`](structured/README.md) | NetCDF-4, CF-1.8 | `structured_global_climate.nc` | `map_single_frame`, `animate_rotating_frames`, `animate_time_series_frames` |
| [`unstructured/`](unstructured/README.md) | UGRID-1.0, VTK | `unstructured_geodesic_mesh.nc`, `unstructured_geodesic_mesh.vtk` | `map_single_frame` with `from_unstructured`, cell edge visualization |
| [`vector/`](vector/README.md) | GeoJSON (EPSG:4326) | `flight_routes.geojson`, `shipping_routes.geojson` | `animate_mesh_with_vector_files`, `animate_polyline_file_on_sphere` |

---

## Automatic Data Regeneration

All datasets can be regenerated at any time using the example export script:

```bash
python examples/00_export_sample_data.py
```
