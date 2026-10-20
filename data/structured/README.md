# Structured Earth Science Data

This directory contains structured rectilinear and curvilinear geospatial grid datasets formatted for 3D spherical rendering in `pyearthviz3d`.

## Dataset Specification

### `structured_global_climate.nc`
- **Format**: NetCDF-4 (Classic model)
- **Conventions**: CF-1.8 (Climate and Forecast Metadata Conventions)
- **Grid Type**: Regular Rectilinear Latitude-Longitude Grid ($73 \times 144$)
- **Spatial Resolution**: $2.5^\circ \times 2.5^\circ$
- **Geographic Extent**: Latitude $[-90.0^\circ, 90.0^\circ]$, Longitude $[-180.0^\circ, 180.0^\circ]$

### Variables & Metadata

| Variable Name | Dimensions | Units | Standard Name | Description |
| :--- | :--- | :--- | :--- | :--- |
| `lat` | `(lat: 73)` | `degrees_north` | `latitude` | 1D latitude coordinates (Y-axis) |
| `lon` | `(lon: 144)` | `degrees_east` | `longitude` | 1D longitude coordinates (X-axis) |
| `temperature` | `(lat, lon)` | `K` | `air_temperature` | Global surface temperature with planetary latitudinal gradient and diurnal thermal wave |
| `elevation` | `(lat, lon)` | `m` | `surface_altitude` | Topographic relief altitude field |
| `wind_speed` | `(lat, lon)` | `m s-1` | `wind_speed` | Near-surface zonal/meridional wind speed |

---

## Python Usage Example

```python
import netCDF4 as nc
import geovista as gv
import numpy as np
from pyearthviz3d import map_single_frame, VisualizationConfig

# 1. Open structured NetCDF
with nc.Dataset("data/structured/structured_global_climate.nc") as ds:
    lats = ds.variables["lat"][:]
    lons = ds.variables["lon"][:]
    temp = ds.variables["temperature"][:]

# 2. Transform 1D coordinate arrays into a 3D spherical mesh
mesh = gv.Transform.from_1d(lons, lats)

# 3. Associate cell-centered scalar values
cell_temp = (temp[:-1, :-1] + temp[1:, :-1] + temp[:-1, 1:] + temp[1:, 1:]) / 4.0
mesh.cell_data["temperature"] = cell_temp.ravel()

# 4. Render with GeoVista engine
config = VisualizationConfig(longitude_focus=-95.0, latitude_focus=35.0, colormap="plasma")
map_single_frame(mesh, np.arange(mesh.n_cells), config, sScalar="temperature", sUnit="K")
```
