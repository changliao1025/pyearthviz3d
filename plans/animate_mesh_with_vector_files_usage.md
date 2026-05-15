# Usage Guide: animate_mesh_with_vector_files

## Quick Start

```python
from pyearthviz3d.geovista import (
    animate_mesh_with_vector_files,
    VectorLayerConfig,
)
from pyearthviz3d.geovista.utility import (
    VisualizationConfig,
    AnimationConfig,
)

# Basic usage: Mesh + single vector file
config = VisualizationConfig(
    longitude_focus=-100,
    latitude_focus=40,
    base_layer="blue_marble",
)

result = animate_mesh_with_vector_files(
    pMesh=your_mesh,
    aValid_cell_indices=valid_indices,
    sScalar="temperature",
    sUnit="°C",
    aFilename_vector_in="paths.shp",
    aVector_config=VectorLayerConfig(color="red"),
    pConfig=config,
    sFilename_out="output.png",
)
```

## Key Features

1. **Multiple Vector Files**: Pass a list of file paths
2. **Individual Styling**: Configure each layer separately
3. **Flexible Input**: Mesh-only, vector-only, or combined
4. **Animation Support**: Create rotating globe animations
5. **Z-Order Control**: Control layer rendering order

## Usage Patterns

### Pattern 1: Multiple Files with Individual Styling

```python
vector_files = ["roads.shp", "rails.shp", "cities.geojson"]
vector_configs = [
    VectorLayerConfig(color="gray", linewidth=1.0, z_order=1),
    VectorLayerConfig(color="black", linewidth=2.0, z_order=2),
    VectorLayerConfig(color="red", point_size=8.0, z_order=3),
]

animate_mesh_with_vector_files(
    pMesh=mesh,
    aValid_cell_indices=indices,
    sScalar="landuse",
    aFilename_vector_in=vector_files,
    aVector_config=vector_configs,
    pConfig=config,
    sFilename_out="output.mp4",
)
```

### Pattern 2: Multiple Files with Shared Styling

```python
track_files = ["track1.shp", "track2.shp", "track3.shp"]
shared_config = VectorLayerConfig(color="blue", linewidth=1.5)

animate_mesh_with_vector_files(
    aFilename_vector_in=track_files,
    aVector_config=shared_config,  # Applied to all
    pConfig=config,
    sFilename_out="tracks.mp4",
)
```

### Pattern 3: Vector-Only (No Mesh)

```python
animate_mesh_with_vector_files(
    aFilename_vector_in=["rivers.shp", "lakes.shp"],
    aVector_config=[
        VectorLayerConfig(color="blue"),
        VectorLayerConfig(color="cyan", opacity=0.6),
    ],
    pConfig=config,
    sFilename_out="water.png",
)
```

### Pattern 4: Variable Line Width from Attributes

```python
vector_config = VectorLayerConfig(
    color="blue",
    linewidth_attribute="speed",  # Attribute name in shapefile
    linewidth_range=(0.5, 4.0),   # Min/max width
)

animate_mesh_with_vector_files(
    aFilename_vector_in="ship_tracks.shp",
    aVector_config=vector_config,
    pConfig=config,
    sFilename_out="ships.mp4",
)
```

## Configuration Reference

### VectorLayerConfig Parameters

- `color`: Color name or hex code (default: "royalblue")
- `linewidth`: Default line width (default: 2.0)
- `linewidth_attribute`: Attribute name for variable width (optional)
- `linewidth_range`: (min, max) for width scaling (default: (0.5, 3.0))
- `style`: Rendering style (default: "line")
- `opacity`: Layer opacity 0.0-1.0 (default: 1.0)
- `point_size`: Size for point geometries (default: 5.0)
- `show_points`: Show line vertices as points (default: False)
- `layer_name`: Descriptive name (optional)
- `z_order`: Rendering order, higher=on top (default: 0)

### Function Parameters

**Mesh inputs** (optional):
- `pMesh`: GeoVista mesh object
- `aValid_cell_indices`: Valid cell indices
- `sScalar`: Scalar field name
- `sUnit`: Unit string for scalar bar

**Vector inputs** (optional):
- `aFilename_vector_in`: Single path or list of paths
- `aVector_config`: Single config or list of configs

**Configuration**:
- `pConfig`: VisualizationConfig object
- `animation_config`: AnimationConfig for animations
- `scalar_config`: ScalarBarConfig for scalar bar

**Output**:
- `sFilename_out`: Output file path (.png, .mp4, .gif, etc.)

**Advanced**:
- `style`: Mesh rendering style (default: "surface")
- `validate_inputs`: Enable validation (default: True)
- `return_detailed_result`: Return AnimationResult object (default: False)

## Return Values

### Simple Mode (return_detailed_result=False)
Returns `bool`: True if successful, False otherwise

### Detailed Mode (return_detailed_result=True)
Returns `AnimationResult` object with:
- `success`: Boolean success status
- `message`: Status message
- `file_info`: Output file information
- `layer_info`: Mesh and vector layer details
- `animation_info`: Animation parameters
- `system_info`: System information

```python
result = animate_mesh_with_vector_files(
    ...,
    return_detailed_result=True,
)

print(result.get_summary())
# Output:
# ✅ Visualization completed successfully
# 📁 File: output.mp4
# 📏 Size: 45.23 MB
# 🗺️  Mesh: 50000 cells
# 📍 Vector layers: 3
#    1. Roads: 1250 features
#    2. Rails: 850 features
#    3. Cities: 150 features
# 🎬 Animation: 360 frames, 12.0s
```

## Supported File Formats

**Vector files**:
- Shapefile (.shp)
- GeoJSON (.geojson, .json)
- KML (.kml)
- GPX (.gpx)

**Output formats**:
- Images: .png, .jpg, .jpeg, .svg, .tif, .tiff, .pdf, .ps
- Animations: .mp4, .gif, .avi

## Tips and Best Practices

1. **Layer Order**: Use `z_order` to control which layers render on top
2. **Performance**: Fewer frames = faster rendering
3. **File Size**: MP4 is more efficient than GIF for animations
4. **Opacity**: Use opacity < 1.0 to see layers beneath
5. **Validation**: Keep `validate_inputs=True` during development
6. **Verbose Mode**: Set `pConfig.verbose=True` for detailed logging

## Error Handling

The function includes comprehensive error handling:
- Invalid file paths
- Mismatched config/file list lengths
- Unsupported file formats
- Missing required parameters
- Coordinate transformation issues

Errors are logged and returned in the result object when using `return_detailed_result=True`.

## Integration with Existing Code

### From animate_polyline_file_on_sphere

**Before**:
```python
animate_polyline_file_on_sphere(
    sFilename_polyline_in="paths.shp",
    sFilename_animation_out="output.mp4",
    dLongitude_focus_in=0.0,
    sColor_polyline_in="blue",
)
```

**After**:
```python
animate_mesh_with_vector_files(
    aFilename_vector_in="paths.shp",
    aVector_config=VectorLayerConfig(color="blue"),
    pConfig=VisualizationConfig(longitude_focus=0.0),
    sFilename_out="output.mp4",
)
```

### From map_single_frame

**Before**:
```python
map_single_frame(
    pMesh=mesh,
    aValid_cell_indices=indices,
    pConfig=config,
    sScalar="temperature",
    sFilename_out="output.png",
)
```

**After** (add vector overlay):
```python
animate_mesh_with_vector_files(
    pMesh=mesh,
    aValid_cell_indices=indices,
    pConfig=config,
    sScalar="temperature",
    aFilename_vector_in="overlay.shp",  # NEW
    aVector_config=VectorLayerConfig(),  # NEW
    sFilename_out="output.png",
)
```

## See Also

- [Design Document](animate_mesh_with_vector_files_design.md) - Full architectural design
- [`utility.py`](../pyearthviz3d/geovista/utility.py) - Shared utility functions
- [`animate_polyline_file_on_sphere.py`](../pyearthviz3d/geovista/animate_polyline_file_on_sphere.py) - Vector-only visualization
- [`map_single_frame.py`](../pyearthviz3d/geovista/map_single_frame.py) - Mesh-only visualization