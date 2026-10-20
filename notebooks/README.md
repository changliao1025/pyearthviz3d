# `pyearthviz3d` Jupyter Notebooks

This directory contains interactive Jupyter notebooks mirroring and expanding upon the Python example scripts in [`examples/`](../examples). These notebooks allow interactive step-by-step exploration, inspection of datasets, inline rendering of 3D globes, and animation playback directly within JupyterLab, Jupyter Notebook, or Visual Studio Code.

---

## Notebooks Catalog

| Notebook | Focus & Topic | Input Data | Key APIs & Capabilities Demonstrated |
| :--- | :--- | :--- | :--- |
| [`01_single_frame_structured_mesh.ipynb`](01_single_frame_structured_mesh.ipynb) | Structured Climate Mesh | NetCDF-4 (`data/structured/`) | `geovista.Transform.from_1d`, `VisualizationConfig`, `ScalarBarConfig`, `map_single_frame` |
| [`02_unstructured_geodesic_mesh.ipynb`](02_unstructured_geodesic_mesh.ipynb) | Unstructured Geodesic Mesh | UGRID-1.0 NetCDF (`data/unstructured/`) | `geovista.Transform.from_unstructured`, cell wireframe edge highlighting, vorticity & SSH |
| [`03_mesh_with_vector_overlays.ipynb`](03_mesh_with_vector_overlays.ipynb) | 3D Mesh + Multi-layer Vectors | GeoJSON (`data/vector/`) + Base Mesh | `VectorLayerConfig`, multi-layer styling (color, width, z-order), `animate_mesh_with_vector_files` |
| [`04_discrete_scalar_colorbar.ipynb`](04_discrete_scalar_colorbar.ipynb) | Categorical & Discrete Data | Synthetic Land Cover Classes | `ScalarBarConfig.is_discrete`, custom discrete color swatches, human-readable labels |
| [`05_rotating_animation.ipynb`](05_rotating_animation.ipynb) | Rotating 3D Globe Animation | Synthetic Planetary Wave Mesh | `AnimationConfig`, `create_animation_preview`, `animate_rotating_frames`, GIF/MP4 generation |

---

## Prerequisites & Launching

### 1. Ensure Dependencies are Installed
Activate your conda or virtual environment with `pyearthviz3d` installed:

```bash
conda activate uraster
# or
pip install -e ".[dev]"
```

Ensure Jupyter or JupyterLab is available:
```bash
conda install -c conda-forge jupyterlab
# or
pip install jupyterlab ipywidgets
```

### 2. Launch JupyterLab or Notebook
Start Jupyter from the repository root:

```bash
jupyter lab
```

Then open any notebook under the `notebooks/` directory.

### 3. Rendering in Notebooks
Each notebook renders high-resolution figures inline using `IPython.display.Image` by default, making them fully viewable without needing a separate X11 or graphics window.

If you have a local desktop display and prefer full 3D mouse interaction (rotate, zoom, pan):
- Set `sFilename_out=None` in `map_single_frame(...)` to launch an interactive GeoVista / VTK window.
- Or use PyVista's client/trame Jupyter backend:
  ```python
  import pyvista as pv
  pv.set_jupyter_backend('client')  # or 'trame' / 'static'
  ```
