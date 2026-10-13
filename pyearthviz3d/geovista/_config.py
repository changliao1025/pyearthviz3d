"""Configuration and shared constants for GeoVista visualizations."""

import logging
import math
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)

CRS = "EPSG:4326"


DEFAULT_EARTH_RADIUS = 1.0


DEFAULT_CAMERA_DISTANCE_MULTIPLIER = 3.0


DEFAULT_ZOOM_FACTOR = 0.7


DEFAULT_FRAMERATE = 30


DEFAULT_ANIMATION_FRAMES = 36


DEFAULT_ANIMATION_SPEED = 10.0  # degrees per frame


VALID_ANIMATION_FORMATS = ["mp4", "gif", "avi"]


VALID_IMAGE_FORMATS = ["png", "jpg", "jpeg", "svg", "tif", "tiff", "pdf", "ps"]


COORDINATE_BOUNDS = {"longitude": (-180, 180), "latitude": (-90, 90)}


class CameraPosition(NamedTuple):
    """Immutable camera position data structure."""

    focal_point: Tuple[float, float, float]
    camera_position: Tuple[float, float, float]


class VisualizationConfig:
    """Configuration class for visualization parameters."""

    def __init__(
        self,
        longitude_focus: float = 0.0,
        latitude_focus: float = 0.0,
        zoom_factor: float = DEFAULT_ZOOM_FACTOR,
        show_coastlines: bool = True,
        show_graticule: bool = True,
        base_layer: Optional[str] = None,
        color: str = "blue",
        colormap: str = "viridis",
        coastline_color: str = "black",
        coastline_width: float = 1.0,
        verbose: bool = False,
        window_size: Tuple[int, int] = (800, 600),
        image_scale: float = 1.0,
        use_xvfb: Optional[bool] = None,
        force_xvfb: bool = False,
        base_layer_opacity: float = 1.0,
        mesh_opacity: float = 1.0,
    ):
        """
        Initialize visualization configuration.

        Args:
            longitude_focus: Camera focal point longitude in degrees (-180 to 180)
            latitude_focus: Camera focal point latitude in degrees (-90 to 90)
            zoom_factor: Camera zoom level (positive float)
            show_coastlines: Whether to show coastline overlay
            show_graticule: Whether to show coordinate grid
            base_layer: Base layer texture for the globe. Options:
                - None: No base layer (empty globe)
                - "natural_earth_hypsometric": Natural Earth hypsometric texture (default)
                - "natural_earth_1": Natural Earth I texture
                - "blue_marble": NASA Blue Marble texture
            colormap: Matplotlib colormap name for scalar visualization
            coastline_color: Color for coastlines
            coastline_width: Line width for coastlines
            verbose: Enable verbose logging
            window_size: Window size as (width, height)
            image_scale: Image scaling factor
            use_xvfb: Whether to use Xvfb (None=auto-detect)
            force_xvfb: Force Xvfb even if not detected as needed
        """
        self.longitude_focus = self._validate_longitude(longitude_focus)
        self.latitude_focus = self._validate_latitude(latitude_focus)
        self.zoom_factor = self._validate_zoom_factor(zoom_factor)
        self.show_coastlines = show_coastlines
        self.show_graticule = show_graticule
        self.base_layer = self._validate_base_layer(base_layer)
        self.color = color
        self.colormap = colormap
        self.coastline_color = coastline_color
        self.coastline_width = coastline_width
        self.verbose = verbose
        self.window_size = window_size
        self.image_scale = image_scale
        self.use_xvfb = use_xvfb  # None=auto-detect, True=force use, False=don't use
        self.force_xvfb = force_xvfb
        # Opacity controls (0.0 transparent .. 1.0 opaque)
        self.base_layer_opacity = self._validate_opacity(base_layer_opacity, "base_layer")
        self.mesh_opacity = self._validate_opacity(mesh_opacity, "mesh")

    def _validate_opacity(self, value: float, name: str) -> float:
        """Validate opacity in range [0.0, 1.0]."""
        try:
            val = float(value)
        except Exception:
            logger.warning(f"Invalid {name} opacity '{value}', using 1.0")
            return 1.0
        if val < 0.0 or val > 1.0:
            logger.warning(f"{name} opacity {val} out of range [0,1], clamping")
            return float(np.clip(val, 0.0, 1.0))
        return val

    def _validate_longitude(self, lon: float) -> float:
        """Validate and clamp longitude to valid range."""
        if not (-180 <= lon <= 180):
            logger.warning(f"Longitude {lon} out of range [-180, 180], clamping")
            return np.clip(lon, -180, 180)
        return lon

    def _validate_latitude(self, lat: float) -> float:
        """Validate and clamp latitude to valid range."""
        if not (-90 <= lat <= 90):
            logger.warning(f"Latitude {lat} out of range [-90, 90], clamping")
            return np.clip(lat, -90, 90)
        return lat

    def _validate_zoom_factor(self, zoom: float) -> float:
        """Validate zoom factor."""
        if zoom <= 0:
            logger.warning(f"Invalid zoom factor {zoom}, using default {DEFAULT_ZOOM_FACTOR}")
            return DEFAULT_ZOOM_FACTOR
        return zoom

    def _validate_base_layer(self, layer: Optional[str]) -> Optional[str]:
        """
        Validate base layer name.

        Args:
            layer: Base layer name or None

        Returns:
            Validated base layer name or None
        """
        if layer is None:
            return None

        valid_layers = [
            "natural_earth_hypsometric",
            "natural_earth_1",
            "blue_marble",
        ]

        if layer not in valid_layers:
            logger.warning(
                f"Unknown base layer '{layer}'. Valid options: {valid_layers}. Using None."
            )
            return None

        return layer


class ScalarBarConfig:
    """Configuration class for scalar bar parameters."""

    def __init__(
        self,
        title: str = "",
        title_font_size: int = 12,
        label_font_size: int = 10,
        fmt: str = "%.2f",
        n_labels: int = 5,
        shadow: bool = True,
        orientation: str = "horizontal",
        position_x: float = None,
        position_y: float = None,
        width: float = None,
        height: float = None,
        discrete_labels: Optional[Dict] = None,
        value_colors: Optional[Dict] = None,
    ):
        self.title = str(title)
        self.title_font_size = max(8, int(title_font_size))
        self.label_font_size = max(6, int(label_font_size))
        self.fmt = str(fmt)
        self.n_labels = max(2, int(n_labels))
        self.shadow = bool(shadow)

        # Store discrete colorbar parameters
        self.discrete_labels = discrete_labels
        self.value_colors = value_colors

        # Validate and set orientation
        self.orientation = self._validate_orientation(orientation)

        # Set default positions based on orientation
        self.position_x, self.position_y, self.width, self.height = self._set_default_dimensions(
            position_x, position_y, width, height, self.orientation
        )

    def _validate_orientation(self, orientation: str) -> str:
        """Validate and normalize orientation parameter."""
        valid_orientations = ["horizontal", "vertical"]
        orientation_lower = str(orientation).lower()

        if orientation_lower not in valid_orientations:
            logger.warning(f'Invalid orientation "{orientation}", using "horizontal"')
            return "horizontal"

        return orientation_lower

    def _set_default_dimensions(
        self,
        position_x: Optional[float],
        position_y: Optional[float],
        width: Optional[float],
        height: Optional[float],
        orientation: str,
    ) -> Tuple[float, float, float, float]:
        """Set default dimensions based on orientation."""
        if orientation == "vertical":
            # Default values for vertical scalar bar
            # Positioned to avoid overlap with axes widget in bottom-left
            default_position_x = 0.85
            default_position_y = 0.25
            default_width = 0.05
            default_height = 0.5
        else:  # horizontal
            # Default values for horizontal scalar bar
            # Positioned at bottom center, avoiding axes widget
            default_position_x = 0.5
            default_position_y = 0.05
            default_width = 0.4
            default_height = 0.08

        # Use provided values or defaults
        final_position_x = np.clip(
            position_x if position_x is not None else default_position_x, 0.0, 1.0
        )
        final_position_y = np.clip(
            position_y if position_y is not None else default_position_y, 0.0, 1.0
        )
        final_width = np.clip(width if width is not None else default_width, 0.01, 0.5)
        final_height = np.clip(height if height is not None else default_height, 0.01, 1.0)

        return final_position_x, final_position_y, final_width, final_height

    def to_dict(self, scalar_name: str = "", unit: str = "") -> Dict[str, Any]:
        """Convert to dictionary format for GeoVista scalar_bar_args."""
        # If unit is provided, use only the unit as title
        # Otherwise, use scalar_name or self.title
        if unit:
            title = unit
        else:
            title = scalar_name or self.title
        result = {
            "title": title,
            "shadow": self.shadow,
            "title_font_size": self.title_font_size,
            "label_font_size": self.label_font_size,
            "fmt": self.fmt,
            "n_labels": self.n_labels,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "width": self.width,
            "height": self.height,
            "vertical": (self.orientation == "vertical"),
        }

        # Add discrete colorbar parameters if provided
        if self.discrete_labels is not None:
            result["discrete_labels"] = self.discrete_labels
        if self.value_colors is not None:
            result["value_colors"] = self.value_colors

        return result


class AnimationConfig:
    """Enhanced configuration class for animation parameters."""

    def __init__(
        self,
        frames: Union[int, str] = DEFAULT_ANIMATION_FRAMES,
        speed: Union[float, str] = DEFAULT_ANIMATION_SPEED,
        format: str = "mp4",
        framerate: Union[int, str] = DEFAULT_FRAMERATE,
        amplitude_deg: float = 20.0,
        cycles: float = 1.0,
        phase: float = 0.0,
        longitude_start: float = 0.0,
        latitude_start: float = 0.0,
        latitude_focus: float = 0.0,
        # Legacy parameter support (deprecated)
        dLongitude_start: Optional[float] = None,
        dLatitude_start: Optional[float] = None,
    ):

        # Handle legacy parameters
        if dLongitude_start is not None:
            logger.warning("Parameter 'dLongitude_start' is deprecated, use 'longitude_start'")
            longitude_start = dLongitude_start
        if dLatitude_start is not None:
            logger.warning("Parameter 'dLatitude_start' is deprecated, use 'latitude_start'")
            latitude_start = dLatitude_start

        # Validate and set frames
        self.frames = self._validate_int_parameter(
            frames, "frames", DEFAULT_ANIMATION_FRAMES, min_val=1
        )

        # Validate and set speed (degrees per frame)
        self.speed = self._validate_float_parameter(
            speed, "speed", DEFAULT_ANIMATION_SPEED, min_val=0.1
        )

        # Validate and set framerate
        self.framerate = self._validate_int_parameter(
            framerate, "framerate", DEFAULT_FRAMERATE, min_val=1, max_val=120
        )

        # Validate format
        self.format = format.lower()
        if self.format not in VALID_ANIMATION_FORMATS:
            logger.warning(f"Invalid animation format {format}, using mp4")
            self.format = "mp4"

        # Animation motion parameters
        self.amplitude_deg = self._validate_float_parameter(
            amplitude_deg, "amplitude_deg", 20.0, min_val=0.0, max_val=90.0
        )
        self.cycles = self._validate_float_parameter(cycles, "cycles", 1.0, min_val=0.1)
        self.phase = math.radians(phase) if isinstance(phase, (int, float)) else 0.0

        # Starting position parameters
        self.longitude_start = self._validate_coordinate(longitude_start, "longitude")
        self.latitude_start = self._validate_coordinate(latitude_start, "latitude")
        self.latitude_focus = self._validate_coordinate(latitude_focus, "latitude")

        # Computed properties
        self.total_rotation = self.frames * self.speed
        self.estimated_duration = self.frames / self.framerate

    def _validate_int_parameter(
        self,
        value: Union[int, str],
        param_name: str,
        default: int,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
    ) -> int:
        """Validate and convert integer parameters."""
        try:
            int_val = int(value) if isinstance(value, str) else int(value)
            if min_val is not None and int_val < min_val:
                logger.warning(
                    f"{param_name} {int_val} below minimum {min_val}, using {max(min_val, default)}"
                )
                return max(min_val, default)
            if max_val is not None and int_val > max_val:
                logger.warning(
                    f"{param_name} {int_val} above maximum {max_val}, using {min(max_val, default)}"
                )
                return min(max_val, default)
            return int_val
        except (ValueError, TypeError):
            logger.warning(f"Invalid {param_name} value {value}, using default {default}")
            return default

    def _validate_float_parameter(
        self,
        value: Union[float, str],
        param_name: str,
        default: float,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> float:
        """Validate and convert float parameters."""
        try:
            float_val = float(value) if isinstance(value, str) else float(value)
            if min_val is not None and float_val < min_val:
                logger.warning(
                    f"{param_name} {float_val} below minimum {min_val}, using {max(min_val, default)}"
                )
                return max(min_val, default)
            if max_val is not None and float_val > max_val:
                logger.warning(
                    f"{param_name} {float_val} above maximum {max_val}, using {min(max_val, default)}"
                )
                return min(max_val, default)
            return float_val
        except (ValueError, TypeError):
            logger.warning(f"Invalid {param_name} value {value}, using default {default}")
            return default

    def _validate_coordinate(self, coord: float, coord_type: str) -> float:
        """Validate coordinate values."""
        bounds = COORDINATE_BOUNDS.get(coord_type, (-180, 180))
        if not (bounds[0] <= coord <= bounds[1]):
            logger.warning(f"{coord_type} {coord} out of range {bounds}, clamping")
            return np.clip(coord, bounds[0], bounds[1])
        return coord

    @property
    def dLongitude_start(self) -> float:
        """Legacy property for backward compatibility."""
        return self.longitude_start

    @property
    def dLatitude_start(self) -> float:
        """Legacy property for backward compatibility."""
        return self.latitude_start

    def get_animation_info(self) -> str:
        """Get formatted animation information string."""
        return (
            f"Animation: {self.frames} frames, {self.framerate} FPS, "
            f"{self.estimated_duration:.1f}s duration, {self.total_rotation:.1f}° total rotation"
        )


class AnimationResult:
    """Result object for animation operations."""

    def __init__(
        self,
        success: bool,
        message: str = "",
        file_info: Optional[Dict[str, Any]] = None,
        animation_info: Optional[Dict[str, Any]] = None,
        frame_info: Optional[Dict[str, Any]] = None,
        layer_info: Optional[Dict[str, Any]] = None,
        system_info: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.message = message
        self.file_info = file_info or {}
        self.animation_info = animation_info or {}
        self.frame_info = frame_info or {}
        self.layer_info = layer_info or {}
        self.system_info = system_info or {}

    def __str__(self) -> str:
        return f"AnimationResult(success={self.success}, message='{self.message}')"

    def __repr__(self) -> str:
        return self.__str__()

    def get_summary(self) -> str:
        """Get formatted summary of animation result."""
        if not self.success:
            return f"Operation failed: {self.message}"

        lines = ["Operation completed successfully"]

        if self.file_info:
            lines.append(f"?? File: {self.file_info.get('filename', 'N/A')}")
            size_mb = self.file_info.get("size_mb", 0)
            if size_mb > 0:
                lines.append(f"?? Size: {size_mb:.2f} MB")

        if self.layer_info:
            if "mesh" in self.layer_info:
                lines.append(f"???  Mesh: {self.layer_info['mesh'].get('cells', 0)} cells")
            if "vectors" in self.layer_info:
                n_layers = len(self.layer_info["vectors"])
                lines.append(f"?? Vector layers: {n_layers}")
                for i, vinfo in enumerate(self.layer_info["vectors"], 1):
                    name = vinfo.get("name", f"Layer {i}")
                    features = vinfo.get("features", 0)
                    lines.append(f"   {i}. {name}: {features} features")

        if self.animation_info:
            frames = self.animation_info.get("total_frames", self.animation_info.get("frames", 0))
            duration = self.animation_info.get("duration", 0)
            framerate = self.animation_info.get("framerate", 0)
            if frames > 0:
                lines.append(f"?? Frames: {frames}")
            if duration > 0:
                lines.append(f"?? Duration: {duration:.1f}s")
            if framerate > 0:
                lines.append(f"?? FPS: {framerate}")

        return "\n".join(lines)
