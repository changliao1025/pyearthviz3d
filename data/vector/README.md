# Vector GIS Overlays

This directory contains vector line layers in standard GeoJSON format for multi-layer composition on 3D spherical meshes in `pyearthviz3d`.

## Available Vector Datasets

### 1. `flight_routes.geojson`
- **Format**: GeoJSON FeatureCollection (`LineString`)
- **Coordinate System**: WGS84 (EPSG:4326)
- **Features**: Transcontinental commercial flight corridors (Transatlantic, Transpacific, Asia-Middle East, Transpolar South, Africa-Europe).
- **Properties**:
  - `route_id`: Airport IATA pair code (e.g. `LHR-JFK`, `HND-SFO`)
  - `name`: Full descriptive route name
  - `traffic_index`: Flight density weight ($2.0 - 5.0$)
  - `category`: Geographic corridor classification

---

### 2. `shipping_routes.geojson`
- **Format**: GeoJSON FeatureCollection (`LineString`)
- **Coordinate System**: WGS84 (EPSG:4326)
- **Features**: Major international maritime trade arteries through navigational choke points (Strait of Malacca, Bab-el-Mandeb, Suez Canal, Panama Canal, Trans-Pacific).
- **Properties**:
  - `corridor`: Trade corridor name
  - `chokepoints`: Strategic maritime straits traversed
  - `density`: Cargo volume score

---

## Python Usage with `VectorLayerConfig`

```python
from pyearthviz3d import VectorLayerConfig, animate_mesh_with_vector_files

# Define individual layer styling and z-order
flight_cfg = VectorLayerConfig(
    color="crimson",
    linewidth=3.0,
    opacity=1.0,
    layer_name="Flight Corridors",
    z_order=10
)

shipping_cfg = VectorLayerConfig(
    color="gold",
    linewidth=2.5,
    opacity=0.9,
    layer_name="Shipping Corridors",
    z_order=5
)

# Pass multiple files and configurations to the pipeline
animate_mesh_with_vector_files(
    pMesh=mesh,
    aValid_cell_indices=indices,
    sScalar="elevation",
    aFilename_vector_in=["data/vector/flight_routes.geojson", "data/vector/shipping_routes.geojson"],
    aVector_config=[flight_cfg, shipping_cfg],
    pConfig=viz_config
)
```
