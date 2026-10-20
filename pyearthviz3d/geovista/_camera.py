"""Camera positioning and configuration helpers."""

import logging
import math
from functools import lru_cache
from typing import Any, Dict, List, Tuple, Union

from ._config import (
    DEFAULT_CAMERA_DISTANCE_MULTIPLIER,
    DEFAULT_EARTH_RADIUS,
    DEFAULT_ZOOM_FACTOR,
    AnimationConfig,
    CameraPosition,
    VisualizationConfig,
)

logger = logging.getLogger(__name__)


class CameraController:
    """Enhanced camera positioning and movement calculations."""

    _position_cache: Dict[Any, Any] = {}  # Cache for frequently used positions

    @staticmethod
    @lru_cache(maxsize=128)
    def calculate_camera_position(
        longitude: float, latitude: float, zoom_factor: float = DEFAULT_ZOOM_FACTOR
    ) -> CameraPosition:
        """
        Calculate camera position and focal point from geographic coordinates with caching.

        Args:
            longitude: Longitude in degrees [-180, 180]
            latitude: Latitude in degrees [-90, 90]
            zoom_factor: Camera zoom level (positive float)

        Returns:
            CameraPosition: Named tuple containing focal_point and camera_position as tuples

        Raises:
            ValueError: If coordinates are out of valid ranges
        """
        # Validate inputs
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude {longitude} must be in range [-180, 180]")
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude {latitude} must be in range [-90, 90]")
        if zoom_factor <= 0:
            raise ValueError(f"Zoom factor {zoom_factor} must be positive")

        # Convert to radians
        lon_rad = math.radians(longitude)
        lat_rad = math.radians(latitude)

        # Calculate positions
        earth_radius = DEFAULT_EARTH_RADIUS
        camera_distance = (
            earth_radius * DEFAULT_CAMERA_DISTANCE_MULTIPLIER / zoom_factor
        )

        # Focal point on Earth surface
        x_focal = earth_radius * math.cos(lat_rad) * math.cos(lon_rad)
        y_focal = earth_radius * math.cos(lat_rad) * math.sin(lon_rad)
        z_focal = earth_radius * math.sin(lat_rad)

        # Camera position away from Earth
        x_camera = camera_distance * math.cos(lat_rad) * math.cos(lon_rad)
        y_camera = camera_distance * math.cos(lat_rad) * math.sin(lon_rad)
        z_camera = camera_distance * math.sin(lat_rad)

        focal_point = (x_focal, y_focal, z_focal)
        camera_position = (x_camera, y_camera, z_camera)

        return CameraPosition(focal_point, camera_position)

    @staticmethod
    def calculate_animation_camera_position(
        longitude: float, latitude: float, frame_idx: int, config: "AnimationConfig"
    ) -> CameraPosition:
        """
        Calculate camera position for animation frame with enhanced latitude movement.

        Args:
            longitude: Base longitude in degrees
            latitude: Base latitude in degrees
            frame_idx: Current frame index
            config: Animation configuration

        Returns:
            CameraPosition: Camera position for this frame
        """
        # Calculate current longitude with rotation
        longitude_current = config.longitude_start + (frame_idx * config.speed)
        longitude_current = longitude_current % 360.0  # Keep within [0, 360)
        if longitude_current > 180.0:
            longitude_current -= 360.0  # Convert to [-180, 180]

        # Enhanced latitude movement: sine-wave oscillation for dynamic viewing
        frames_div = float(config.frames) if config.frames > 0 else 1.0
        theta = (
            2.0 * math.pi * (float(frame_idx) / frames_div) * config.cycles
            + config.phase
        )
        latitude_current = float(
            config.latitude_start
        ) + config.amplitude_deg * math.sin(theta)

        # Clamp latitude to avoid pole singularities
        latitude_current = max(-89.9, min(89.9, latitude_current))

        # Convert to radians for calculations
        lon_rad = math.radians(longitude_current)
        lat_rad = math.radians(latitude_current)

        # Calculate positions
        earth_radius = DEFAULT_EARTH_RADIUS
        camera_distance = earth_radius * DEFAULT_CAMERA_DISTANCE_MULTIPLIER

        # Calculate focal point on Earth surface
        x_focal = earth_radius * math.cos(lat_rad) * math.cos(lon_rad)
        y_focal = earth_radius * math.cos(lat_rad) * math.sin(lon_rad)
        z_focal = earth_radius * math.sin(lat_rad)

        # Calculate camera position away from Earth
        x_camera = camera_distance * math.cos(lat_rad) * math.cos(lon_rad)
        y_camera = camera_distance * math.cos(lat_rad) * math.sin(lon_rad)
        z_camera = camera_distance * math.sin(lat_rad)

        focal_point = (x_focal, y_focal, z_focal)
        camera_position = (x_camera, y_camera, z_camera)

        return CameraPosition(focal_point, camera_position)

    @staticmethod
    def validate_camera_setup(
        focal_point: Union[List[float], Tuple[float, ...]],
        camera_position: Union[List[float], Tuple[float, ...]],
    ) -> bool:
        """
        Validate camera setup to ensure proper positioning.

        Args:
            focal_point: Focal point coordinates [x, y, z]
            camera_position: Camera position coordinates [x, y, z]

        Returns:
            bool: True if camera setup is valid
        """
        try:
            if len(focal_point) != 3 or len(camera_position) != 3:
                return False

            distance = math.sqrt(
                sum((c - f) ** 2 for c, f in zip(camera_position, focal_point))
            )
            return distance >= 0.1  # Minimum distance threshold
        except Exception:
            return False

    @staticmethod
    def apply_camera_to_plotter(
        plotter, camera_pos: CameraPosition, zoom_factor: float = 1.0
    ) -> bool:
        """
        Apply camera position to plotter with error handling.

        Args:
            plotter: GeoVista plotter instance
            camera_pos: Camera position data
            zoom_factor: Additional zoom factor

        Returns:
            bool: True if successful
        """
        try:
            plotter.camera.focal_point = camera_pos.focal_point
            plotter.camera.position = camera_pos.camera_position
            plotter.camera.up = [0, 0, 1]  # Z-up orientation
            if zoom_factor != 1.0:
                plotter.camera.zoom(zoom_factor)
            return True
        except Exception as e:
            logger.error(f"Failed to apply camera settings: {e}")
            return False


def configure_camera(pPlotter, pConfig: VisualizationConfig) -> bool:
    """
    Configure camera position and orientation.

    Args:
        pPlotter: GeoVista plotter instance
        pConfig: Visualization configuration

    Returns:
        bool: True if camera configured successfully, False otherwise
    """
    try:
        aFocal_point, aCamera_position = CameraController.calculate_camera_position(
            pConfig.longitude_focus, pConfig.latitude_focus, pConfig.zoom_factor
        )

        # Validate camera setup
        if not CameraController.validate_camera_setup(aFocal_point, aCamera_position):
            logger.warning("Camera and focal point are too close, using default view")
            raise ValueError("Invalid camera positioning")

        pPlotter.camera.focal_point = aFocal_point
        pPlotter.camera.position = aCamera_position
        pPlotter.camera.zoom(pConfig.zoom_factor)
        pPlotter.camera.up = [0, 0, 1]  # Z-up orientation

        if pConfig.verbose:
            logger.debug(f"Camera configured successfully:")
            logger.debug(f"  Focal point: {aFocal_point}")
            logger.debug(f"  Camera position: {aCamera_position}")

        return True

    except Exception as e:
        logger.warning(f"Error setting camera position: {e}. Using default view.")
        try:
            pPlotter.reset_camera()
        except Exception:
            pass
        return False


def configure_camera_enhanced(
    plotter, config: VisualizationConfig, use_enhanced_controller: bool = True
) -> bool:
    """
    Configure camera position with enhanced error handling and recovery.

    Args:
        plotter: GeoVista plotter instance
        config: Visualization configuration
        use_enhanced_controller: Whether to use enhanced camera controller

    Returns:
        bool: True if camera configured successfully, False otherwise
    """
    if use_enhanced_controller:
        try:
            camera_pos = CameraController.calculate_camera_position(
                config.longitude_focus, config.latitude_focus, config.zoom_factor
            )

            if CameraController.validate_camera_setup(
                camera_pos.focal_point, camera_pos.camera_position
            ):
                success = CameraController.apply_camera_to_plotter(
                    plotter, camera_pos, config.zoom_factor
                )
                if success and config.verbose:
                    logger.debug(f"Enhanced camera configured successfully")
                    logger.debug(f"  Focal point: {camera_pos.focal_point}")
                    logger.debug(f"  Camera position: {camera_pos.camera_position}")
                return success
            else:
                logger.warning(
                    "Enhanced camera validation failed, trying legacy method"
                )
        except Exception as e:
            logger.warning(
                f"Enhanced camera configuration failed: {e}, trying legacy method"
            )

    # Legacy/fallback camera configuration
    try:
        # Calculate positions using legacy method for backward compatibility
        lon_rad = math.radians(config.longitude_focus)
        lat_rad = math.radians(config.latitude_focus)

        earth_radius = DEFAULT_EARTH_RADIUS
        camera_distance = earth_radius * DEFAULT_CAMERA_DISTANCE_MULTIPLIER

        # Focal point on Earth surface
        x_focal = earth_radius * math.cos(lat_rad) * math.cos(lon_rad)
        y_focal = earth_radius * math.cos(lat_rad) * math.sin(lon_rad)
        z_focal = earth_radius * math.sin(lat_rad)

        # Camera position away from Earth
        x_camera = camera_distance * math.cos(lat_rad) * math.cos(lon_rad)
        y_camera = camera_distance * math.cos(lat_rad) * math.sin(lon_rad)
        z_camera = camera_distance * math.sin(lat_rad)

        focal_point = [x_focal, y_focal, z_focal]
        camera_position = [x_camera, y_camera, z_camera]

        # Apply camera settings
        plotter.camera.focal_point = focal_point
        plotter.camera.position = camera_position
        plotter.camera.up = [0, 0, 1]  # Z-up orientation
        plotter.camera.zoom(config.zoom_factor)

        if config.verbose:
            logger.debug("Legacy camera configured successfully")

        return True

    except Exception as e:
        logger.error(
            f"All camera configuration methods failed: {e}. Using default view."
        )
        try:
            plotter.reset_camera()
            return True  # Default view is still usable
        except Exception:
            logger.error("Could not even reset camera to default view")
            return False
