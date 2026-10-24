"""
pyearthviz3d: 3D Globe Visualization Tools for Geospatial Data

pyearthviz3d provides 3D visualization capabilities on spherical earth using GeoVista and PyVista:
- 3D globe rendering
- Polyline/polygon visualization on sphere
- Rotating animations
- Time series animations on globe
- Interactive 3D views

Example:
    >>> from pyearthviz3d.geovista import map_single_frame
    >>>
    >>> # Visualize vector data on 3D globe
    >>> map_single_frame(
    ...     'data.geojson',
    ...     'globe.png',
    ...     title='Global Data'
    ... )
"""

__version__ = "0.1.3"
__author__ = "Chang Liao"
__email__ = "changliao.climate@gmail.com"
__url__ = "https://github.com/changliao1025/pyearthviz3d"

# Apply compatibility patch between modern PyVista and GeoVista if needed
try:
    import pyvista as pv

    if hasattr(pv, "core") and hasattr(pv.core, "dataset"):
        ActiveArrayInfoTuple = getattr(pv.core.dataset, "ActiveArrayInfoTuple", None)
        if ActiveArrayInfoTuple is not None and not hasattr(
            ActiveArrayInfoTuple, "_namedtuple"
        ):
            ActiveArrayInfoTuple._namedtuple = property(lambda self: self)
except Exception:
    pass

# Apply runtime compatibility safeguard for trame-vtk client-side wheel zoom
try:
    from trame_vtk.modules.vtk.protocols import mouse_handler

    if hasattr(mouse_handler, "vtkWebMouseHandler"):
        _orig_update_zoomFromWheel = (
            mouse_handler.vtkWebMouseHandler.update_zoomFromWheel
        )

        def _safe_update_zoomFromWheel(self, event):
            interactor = self.get_interactor(event)
            if interactor is not None and interactor.GetInteractorStyle() is None:
                return
            return _orig_update_zoomFromWheel(self, event)

        mouse_handler.vtkWebMouseHandler.update_zoomFromWheel = (
            _safe_update_zoomFromWheel
        )
except Exception:
    pass

# Import main geovista functions for convenience
from .geovista import (
    AnimationConfig,
    AnimationResult,
    ScalarBarConfig,
    VectorLayerConfig,
    VisualizationConfig,
    animate_mesh_with_vector_files,
    animate_polyline_file_on_sphere,
    animate_rotating_frames,
    animate_time_series_frames,
    map_single_frame,
)

__all__ = [
    "map_single_frame",
    "animate_polyline_file_on_sphere",
    "animate_rotating_frames",
    "animate_time_series_frames",
    "animate_mesh_with_vector_files",
    "VisualizationConfig",
    "AnimationConfig",
    "ScalarBarConfig",
    "VectorLayerConfig",
    "AnimationResult",
]
