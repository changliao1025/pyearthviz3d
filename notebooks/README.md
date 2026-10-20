# `pyearthviz3d` Interactive Jupyter Notebooks

This directory contains interactive Jupyter notebooks mirroring and expanding upon the Python example scripts in [`examples/`](../examples). These notebooks prioritize **interactive 3D globe visualization** using GeoVista and PyVista, allowing you to freely explore, rotate, pan, and zoom into planetary data directly from JupyterLab, Jupyter Notebook, or Visual Studio Code.

---

## Notebooks Catalog

| Notebook | Focus & Topic | Input Data | Interactive 3D Features Demonstrated |
| :--- | :--- | :--- | :--- |
| [`01_single_frame_structured_mesh.ipynb`](01_single_frame_structured_mesh.ipynb) | Structured Climate Mesh | NetCDF-4 (`data/structured/`) | Interactive 3D globe of surface temperature and topography, `geovista.Transform.from_1d`, custom scalar bars |
| [`02_unstructured_geodesic_mesh.ipynb`](02_unstructured_geodesic_mesh.ipynb) | Unstructured Geodesic Mesh | UGRID-1.0 NetCDF (`data/unstructured/`) | Interactive inspection of triangular geodesic cells with highlighted wireframe edges (`show_edges=True`), vorticity & SSH |
| [`03_mesh_with_vector_overlays.ipynb`](03_mesh_with_vector_overlays.ipynb) | 3D Mesh + Multi-Layer Vectors | GeoJSON (`data/vector/`) + Base Mesh | Interactive 3D composite globe with flight corridors (crimson) and maritime shipping lanes (gold) via `VectorLayerConfig` |
| [`04_discrete_scalar_colorbar.ipynb`](04_discrete_scalar_colorbar.ipynb) | Categorical & Discrete Data | Synthetic Land Cover Classes | Interactive 3D inspection of discrete classification boundaries with labeled category swatches via `ScalarBarConfig` |
| [`05_rotating_animation.ipynb`](05_rotating_animation.ipynb) | Rotating 3D Globe Animation | Synthetic Planetary Wave Mesh | Interactive 3D mesh inspection, key camera preview frame generation, and 360-degree rotating GIF/MP4 export |

---

## Interactive 3D Mouse Controls

When running any notebook cell with `sFilename_out=None` (the default mode in these notebooks):

- **Left Click + Drag**: Freely rotate the 3D globe around any axis.
- **Scroll Wheel / Right Click + Drag**: Zoom smoothly into specific features, terrain elevations, or mesh cells.
- **Shift + Left Click + Drag**: Pan the camera across the globe.
- **Close the 3D Window**: Once you finish exploring, close the 3D viewer window to return execution control to the next notebook cell.

---

## Prerequisites & Launching

### 1. Ensure Dependencies are Installed
Activate your conda environment with `pyearthviz3d` installed:

```bash
conda activate uraster
```

### 2. Launch JupyterLab or Notebook
Start Jupyter from the repository root:

```bash
jupyter lab
```

Or open any notebook directly within Visual Studio Code by selecting the `uraster` kernel.

### 3. Interactive In-Cell 3D Rendering (WebGL)
The notebooks are configured to use PyVista's embeddable `"html"` backend (`pv.set_jupyter_backend("html")`), which packages the 3D WebGL scene inline. This avoids iframe port-blocking issues in VS Code webviews and provides smooth, immediate mouse rotation and zooming right inside your notebook cells.
