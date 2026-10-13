"""Compatibility facade for the GeoVista visualization helpers.

Implementations live in focused internal modules; these re-exports preserve the
historic ``pyearthviz3d.geovista.utility`` import paths.
"""

import logging

from ._camera import CameraController, configure_camera, configure_camera_enhanced
from ._config import (
    AnimationConfig,
    CameraPosition,
    COORDINATE_BOUNDS,
    CRS,
    DEFAULT_ANIMATION_FRAMES,
    DEFAULT_ANIMATION_SPEED,
    DEFAULT_CAMERA_DISTANCE_MULTIPLIER,
    DEFAULT_EARTH_RADIUS,
    DEFAULT_FRAMERATE,
    DEFAULT_ZOOM_FACTOR,
    ScalarBarConfig,
    VALID_ANIMATION_FORMATS,
    VALID_IMAGE_FORMATS,
    VisualizationConfig,
)
from ._environment import (
    detect_headless_environment,
    get_system_info,
    is_running_in_notebook,
    setup_xvfb_if_needed,
    validate_output_filename,
)
from ._mesh import MeshHandler, add_mesh_to_plotter
from ._plotter import (
    PlotterManager,
    add_geographic_context,
    add_geographic_context_enhanced,
    setup_geovista_plotter,
)

logger = logging.getLogger(__name__)
