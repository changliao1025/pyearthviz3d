# `pyearthviz3d` Usage Examples

This folder contains runnable examples demonstrating both **interactive 3D globe visualization** and **image/animation export**, testing the full feature set of `pyearthviz3d` across structured grids, unstructured meshes, and vector GIS layers.

---

## Examples Overview

| Script | Data Format | Dual Mode (Interactive & Export) | Key Features Tested |
| :--- | :--- | :--- | :--- |
| [`00_export_sample_data.py`](00_export_sample_data.py) | NetCDF & GeoJSON | Data Export | Generates structured NetCDF (`structured_global_climate.nc`), unstructured UGRID (`unstructured_geodesic_mesh.nc`), and GeoJSON routes into `data/` |
| [`01_single_frame_structured_mesh.py`](01_single_frame_structured_mesh.py) | Structured NetCDF-4 | Interactive 3D / PNG | Loads structured $73 \times 144$ climate grid, builds 3D sphere via `Transform.from_1d`, custom colorbar, camera focus |
| [`02_unstructured_geodesic_mesh.py`](02_unstructured_geodesic_mesh.py) | Unstructured UGRID-1.0 | Interactive 3D / PNG | Loads 1,280-face triangular geodesic mesh, constructs topology with `Transform.from_unstructured`, highlights mesh cell edges |
| [`03_mesh_with_vector_overlays.py`](03_mesh_with_vector_overlays.py) | Mesh + GeoJSON Lines | Interactive 3D / PNG | Multi-layer composite visualization combining 3D mesh topography with flight and maritime corridors using `VectorLayerConfig` |
| [`04_discrete_scalar_colorbar.py`](04_discrete_scalar_colorbar.py) | Categorical Data | Interactive 3D / PNG | Discrete integer classification (Land Use / Land Cover) with custom named color swatches and human-readable annotations |
| [`05_rotating_animation.py`](05_rotating_animation.py) | Animated 3D Mesh | Previews / Movie Export | Rotates camera around the globe, generates preview frame snapshots, and exports `.gif` / `.mp4` animation |

---

## How to Run

### Step 1: Export Sample Datasets (Optional - Auto-generated if Missing)
Generate the structured NetCDF, unstructured UGRID NetCDF, and GeoJSON files in the `data/` folder:
```bash
python examples/00_export_sample_data.py
```

### Step 2: Interactive 3D Visualization Mode
Launch the interactive 3D GeoVista window (rotate, pan, and zoom with the mouse):
```bash
# Structured mesh (surface temperature)
python examples/01_single_frame_structured_mesh.py --interactive

# Unstructured geodesic triangulation (vorticity with cell edges)
python examples/02_unstructured_geodesic_mesh.py --interactive

# 3D mesh with vector GIS flight and shipping corridors
python examples/03_mesh_with_vector_overlays.py --interactive

# Discrete categorical classification
python examples/04_discrete_scalar_colorbar.py --interactive
```

### Step 3: Image / Movie Export Mode
Export high-resolution static PNG snapshots or rotating animations:
```bash
# Export structured mesh to PNG
python examples/01_single_frame_structured_mesh.py --export my_structured_globe.png

# Export unstructured geodesic mesh to PNG
python examples/02_unstructured_geodesic_mesh.py --export my_unstructured_globe.png

# Export composite mesh + vector GIS to PNG
python examples/03_mesh_with_vector_overlays.py --export my_vector_mesh.png

# Export discrete classification to PNG
python examples/04_discrete_scalar_colorbar.py --export my_discrete_globe.png

# Export rotating globe animation (.gif or .mp4)
python examples/05_rotating_animation.py
```
*(In headless Linux environments without an X11 display, scripts automatically fall back to off-screen export mode using Xvfb).*
