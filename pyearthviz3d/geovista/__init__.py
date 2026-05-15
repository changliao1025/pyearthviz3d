"""
GeoVista-based 3D globe visualization module for pyearthviz3d.

This module provides functions for visualizing geospatial data on a 3D sphere
using GeoVista and PyVista.

Functions:
    map_single_frame: Create a single frame 3D globe visualization
    animate_polyline_file_on_sphere: Animate polylines on rotating sphere
    animate_rotating_frames: Create rotating globe animation
    animate_time_series_frames: Create time series animation on globe
    animate_mesh_with_vector_files: Combine mesh data with multiple vector file overlays (NEW)

Classes:
    VectorLayerConfig: Configuration for vector layer styling
    AnimationResult: Result object for animation operations
"""

from .map_single_frame import map_single_frame
from .animate_polyline_file_on_sphere import animate_polyline_file_on_sphere
from .animate_rotating_frames import animate_rotating_frames
from .animate_time_series_frames import animate_time_series_frames
from .animate_mesh_with_vector_files import (
    animate_mesh_with_vector_files,
    VectorLayerConfig,
    AnimationResult,
)

__all__ = [
    "map_single_frame",
    "animate_polyline_file_on_sphere",
    "animate_rotating_frames",
    "animate_time_series_frames",
    "animate_mesh_with_vector_files",
    "VectorLayerConfig",
    "AnimationResult",
]
