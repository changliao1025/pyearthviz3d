"""
Enhanced visualization module combining mesh data with multiple vector file overlays.

This module provides functionality to create animated or static visualizations that combine:
- Mesh data with scalar fields (from map_single_frame.py)
- Multiple vector file overlays with individual styling (from animate_polyline_file_on_sphere.py)

Key Features:
- Support for multiple vector files with individual or shared styling
- Mesh + vector combination or vector-only visualization
- Animation support with rotating camera
- Z-order control for layer rendering
- Comprehensive error handling and validation

Author: pyearthviz3d
Date: 2026-05-15
Version: 1.0.0
"""

import os
import logging
import traceback
import math
from typing import Optional, List, Union, Dict, Any, Tuple
import numpy as np
from osgeo import gdal, ogr, osr

# Import from utility module
from pyearthviz3d.geovista.utility import (
    VisualizationConfig,
    ScalarBarConfig,
    AnimationConfig,
    PlotterManager,
    MeshHandler,
    CameraController,
    configure_camera_enhanced,
    add_geographic_context_enhanced,
    add_mesh_to_plotter,
    validate_output_filename,
    get_system_info,
    VALID_IMAGE_FORMATS,
    VALID_ANIMATION_FORMATS,
)

# Set up logging
logger = logging.getLogger(__name__)


class VectorLayerConfig:
    """Configuration for vector layer styling."""

    def __init__(
        self,
        color: str = "royalblue",
        linewidth: float = 2.0,
        linewidth_attribute: Optional[str] = None,
        linewidth_range: Tuple[float, float] = (0.5, 3.0),
        style: str = "line",
        opacity: float = 1.0,
        point_size: float = 5.0,
        show_points: bool = False,
        layer_name: Optional[str] = None,
        z_order: int = 0,
    ):
        """
        Initialize vector layer configuration.

        Args:
            color: Color for vector features (named color or hex code)
            linewidth: Default line width
            linewidth_attribute: Attribute name for variable width
            linewidth_range: (min, max) for width scaling
            style: Rendering style for lines ('line', 'tube', 'ribbon')
            opacity: Layer opacity (0.0 to 1.0)
            point_size: Size for point geometries
            show_points: Whether to show line vertices as points
            layer_name: Optional descriptive name for the layer
            z_order: Rendering order (higher values render on top)
        """
        self.color = color
        self.linewidth = linewidth
        self.linewidth_attribute = linewidth_attribute
        self.linewidth_range = linewidth_range
        self.style = style
        self.opacity = np.clip(opacity, 0.0, 1.0)
        self.point_size = point_size
        self.show_points = show_points
        self.layer_name = layer_name
        self.z_order = z_order

    def __repr__(self):
        name = f"'{self.layer_name}'" if self.layer_name else "unnamed"
        return f"VectorLayerConfig({name}, color={self.color}, linewidth={self.linewidth})"


class AnimationResult:
    """Result object for animation operations."""

    def __init__(
        self,
        success: bool,
        message: str = "",
        file_info: Optional[Dict[str, Any]] = None,
        animation_info: Optional[Dict[str, Any]] = None,
        layer_info: Optional[Dict[str, Any]] = None,
        system_info: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.message = message
        self.file_info = file_info or {}
        self.animation_info = animation_info or {}
        self.layer_info = layer_info or {}
        self.system_info = system_info or {}

    def __str__(self) -> str:
        return f"AnimationResult(success={self.success}, message='{self.message}')"

    def __repr__(self) -> str:
        return self.__str__()

    def get_summary(self) -> str:
        """Get formatted summary of animation result."""
        if not self.success:
            return f"❌ Visualization failed: {self.message}"

        lines = ["✅ Visualization completed successfully"]

        if self.file_info:
            lines.append(f"📁 File: {self.file_info.get('filename', 'N/A')}")
            size_mb = self.file_info.get('size_mb', 0)
            if size_mb > 0:
                lines.append(f"📏 Size: {size_mb:.2f} MB")

        if self.layer_info:
            if 'mesh' in self.layer_info:
                lines.append(f"🗺️  Mesh: {self.layer_info['mesh'].get('cells', 0)} cells")
            if 'vectors' in self.layer_info:
                n_layers = len(self.layer_info['vectors'])
                lines.append(f"📍 Vector layers: {n_layers}")
                for i, vinfo in enumerate(self.layer_info['vectors'], 1):
                    name = vinfo.get('name', f'Layer {i}')
                    features = vinfo.get('features', 0)
                    lines.append(f"   {i}. {name}: {features} features")

        if self.animation_info:
            frames = self.animation_info.get('frames', 0)
            duration = self.animation_info.get('duration', 0)
            if frames > 0:
                lines.append(f"🎬 Animation: {frames} frames, {duration:.1f}s")

        return "\n".join(lines)


def _normalize_vector_inputs(
    aFilename_vector_in: Union[str, List[str], None],
    aVector_config: Union[VectorLayerConfig, List[VectorLayerConfig], None],
) -> Tuple[List[str], List[VectorLayerConfig]]:
    """
    Normalize vector inputs to lists.

    Handles:
    - Single file + single config
    - Single file + no config (use default)
    - List of files + single config (apply to all)
    - List of files + list of configs (one-to-one)
    - List of files + no config (use defaults)

    Args:
        aFilename_vector_in: Single file path or list of file paths
        aVector_config: Single config or list of configs

    Returns:
        Tuple of (list of file paths, list of configs)

    Raises:
        ValueError: If config list length doesn't match file list length
    """
    # Handle None inputs
    if aFilename_vector_in is None:
        return [], []

    # Normalize file paths to list
    if isinstance(aFilename_vector_in, str):
        file_paths = [aFilename_vector_in]
    else:
        file_paths = list(aFilename_vector_in)

    # Normalize configs to list
    if aVector_config is None:
        # Use default config for all files
        configs = [VectorLayerConfig() for _ in file_paths]
    elif isinstance(aVector_config, VectorLayerConfig):
        # Single config - apply to all files
        configs = [aVector_config for _ in file_paths]
    else:
        # List of configs
        configs = list(aVector_config)
        if len(configs) != len(file_paths):
            raise ValueError(
                f"Number of vector configs ({len(configs)}) must match "
                f"number of vector files ({len(file_paths)})"
            )

    return file_paths, configs


def _load_vector_data(
    filename: str,
    config: VectorLayerConfig,
    verbose: bool = False,
) -> Tuple[List[Any], List[float], Dict[str, Any]]:
    """
    Load vector data from file using GDAL/OGR.

    Args:
        filename: Path to vector file
        config: Vector layer configuration
        verbose: Enable verbose logging

    Returns:
        Tuple of (geometries, linewidths, info_dict)
        - geometries: List of OGR geometry objects
        - linewidths: List of line widths (scaled if attribute specified)
        - info_dict: Dictionary with layer information

    Raises:
        FileNotFoundError: If file doesn't exist
        RuntimeError: If file cannot be opened or read
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Vector file not found: {filename}")

    try:
        # Open the vector dataset
        dataset = ogr.Open(filename, gdal.GA_ReadOnly)
        if dataset is None:
            raise RuntimeError(f"Could not open vector file: {filename}")

        # Get the first layer
        layer = dataset.GetLayer(0)
        if layer is None:
            raise RuntimeError("Could not get layer from dataset")

        feature_count = layer.GetFeatureCount()
        if verbose:
            logger.info(f"Loading {feature_count} features from {os.path.basename(filename)}")

        # Get spatial reference and setup transformation if needed
        spatial_ref = layer.GetSpatialRef()
        wgs84_srs = osr.SpatialReference()
        wgs84_srs.ImportFromEPSG(4326)

        transform = None
        if spatial_ref is not None:
            spatial_ref_wkt = spatial_ref.ExportToWkt()
            wgs84_wkt = wgs84_srs.ExportToWkt()
            if spatial_ref_wkt != wgs84_wkt:
                if verbose:
                    logger.info("Setting up coordinate transformation to WGS84")
                transform = osr.CoordinateTransformation(spatial_ref, wgs84_srs)

        # Collect geometries and attributes
        geometries = []
        linewidth_values = []

        layer.ResetReading()
        for feature in layer:
            geometry = feature.GetGeometryRef()
            if geometry is None:
                continue

            geom_name = geometry.GetGeometryName()

            # Support LineString, MultiLineString, Point, MultiPoint
            if geom_name in ["LINESTRING", "MULTILINESTRING", "POINT", "MULTIPOINT", "POLYGON", "MULTIPOLYGON"]:
                # Clone geometry
                geom_clone = geometry.Clone()

                # Transform to WGS84 if needed
                if transform is not None:
                    geom_clone.Transform(transform)

                geometries.append(geom_clone)

                # Extract line width attribute if specified
                if config.linewidth_attribute is not None:
                    try:
                        width_value = feature.GetField(config.linewidth_attribute)
                        if width_value is not None:
                            linewidth_values.append(float(width_value))
                        else:
                            linewidth_values.append(config.linewidth)
                    except Exception as e:
                        if verbose:
                            logger.warning(
                                f"Could not read attribute {config.linewidth_attribute}: {e}"
                            )
                        linewidth_values.append(config.linewidth)
                else:
                    linewidth_values.append(config.linewidth)

        if len(geometries) == 0:
            raise RuntimeError("No valid geometries found in file")

        # Scale linewidths if attribute was used
        scaled_widths = []
        if config.linewidth_attribute is not None and len(linewidth_values) > 0:
            data_min, data_max = min(linewidth_values), max(linewidth_values)
            if data_max > data_min:
                for val in linewidth_values:
                    scaled_width = config.linewidth_range[0] + (val - data_min) / (
                        data_max - data_min
                    ) * (config.linewidth_range[1] - config.linewidth_range[0])
                    scaled_widths.append(scaled_width)
                if verbose:
                    logger.info(
                        f'Using variable line widths from attribute "{config.linewidth_attribute}" '
                        f'(range: {data_min:.2f} to {data_max:.2f})'
                    )
            else:
                scaled_widths = [config.linewidth] * len(geometries)
        else:
            scaled_widths = linewidth_values

        info_dict = {
            "filename": filename,
            "features": len(geometries),
            "name": config.layer_name or os.path.basename(filename),
        }

        return geometries, scaled_widths, info_dict

    except Exception as e:
        logger.error(f"Failed to load vector data from {filename}: {e}")
        raise


def _add_vector_layer(
    plotter,
    geometries: List[Any],
    linewidths: List[float],
    config: VectorLayerConfig,
    verbose: bool = False,
) -> bool:
    """
    Add a single vector layer to the plotter.

    Args:
        plotter: GeoVista plotter instance
        geometries: List of OGR geometry objects
        linewidths: List of line widths for each geometry
        config: Vector layer configuration
        verbose: Enable verbose logging

    Returns:
        bool: True if successful
    """
    try:
        import pyvista as pv
        import geovista as gv

        if verbose:
            logger.info(f"Processing {len(geometries)} geometries...")

        # Convert lat/lon to Cartesian coordinates directly
        # This is much faster than using gv_line for each geometry
        all_points = []
        all_lines = []
        point_offset = 0

        for i, geometry in enumerate(geometries):
            points = geometry.GetPoints()
            if points is None or len(points) < 2:
                continue

            # Extract coordinates
            lons = np.array([point[0] for point in points])
            lats = np.array([point[1] for point in points])

            # Convert to Cartesian coordinates (sphere with radius 1)
            # Using standard spherical to Cartesian conversion
            lons_rad = np.deg2rad(lons)
            lats_rad = np.deg2rad(lats)

            x = np.cos(lats_rad) * np.cos(lons_rad)
            y = np.cos(lats_rad) * np.sin(lons_rad)
            z = np.sin(lats_rad)

            # Add points
            for j in range(len(points)):
                all_points.append([x[j], y[j], z[j]])

            # Create line connectivity
            n_points = len(points)
            line = [n_points] + list(range(point_offset, point_offset + n_points))
            all_lines.append(line)
            point_offset += n_points

            # Progress reporting for large datasets
            if verbose and len(geometries) > 10000 and (i + 1) % 50000 == 0:
                logger.info(f"  Processed {i + 1}/{len(geometries)} geometries...")

        if len(all_points) == 0:
            logger.error("No valid geometries found")
            return False

        if verbose:
            logger.info(f"Creating mesh with {len(all_points)} points and {len(all_lines)} lines...")

        # Create PyVista PolyData directly
        points_array = np.array(all_points, dtype=np.float64)

        # Flatten lines array for PyVista
        lines_flat = []
        for line in all_lines:
            lines_flat.extend(line)
        lines_array = np.array(lines_flat, dtype=np.int64)

        # Create mesh
        combined_mesh = pv.PolyData(points_array, lines=lines_array)

        if verbose:
            logger.info(f"Mesh created successfully with {combined_mesh.n_points} points and {combined_mesh.n_cells} cells")

        # Add to plotter with uniform width (variable width would require per-point data)
        plotter.add_mesh(
            combined_mesh,
            color=config.color,
            line_width=config.linewidth,
            opacity=config.opacity,
            name=config.layer_name or "vector_layer",
        )

        if verbose:
            logger.info(
                f"✓ Added vector layer '{config.layer_name or 'unnamed'}' "
                f"with {len(all_lines)} features"
            )

        return True

    except Exception as e:
        logger.error(f"Failed to add vector layer: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def _add_multiple_vector_layers(
    plotter,
    file_paths: List[str],
    configs: List[VectorLayerConfig],
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Add multiple vector layers to plotter.

    Args:
        plotter: GeoVista plotter instance
        file_paths: List of vector file paths
        configs: List of vector layer configurations
        verbose: Enable verbose logging

    Returns:
        Dictionary with layer information
    """
    layer_info = {"vectors": []}

    # Sort by z_order for proper rendering
    sorted_items = sorted(
        zip(file_paths, configs), key=lambda x: x[1].z_order
    )

    for file_path, config in sorted_items:
        try:
            # Load vector data
            geometries, linewidths, info = _load_vector_data(
                file_path, config, verbose
            )

            # Add to plotter
            success = _add_vector_layer(
                plotter, geometries, linewidths, config, verbose
            )

            if success:
                layer_info["vectors"].append(info)

        except Exception as e:
            logger.error(f"Failed to process vector file {file_path}: {e}")
            if verbose:
                logger.error(f"Traceback: {traceback.format_exc()}")
            # Continue with other files

    return layer_info


def _create_animation_frames(
    plotter,
    config: VisualizationConfig,
    animation_config: AnimationConfig,
    output_filename: str,
    verbose: bool = False,
) -> bool:
    """
    Create animation frames with rotating camera.

    Args:
        plotter: GeoVista plotter instance with all layers added
        config: Visualization configuration
        animation_config: Animation configuration
        output_filename: Output file path
        verbose: Enable verbose logging

    Returns:
        bool: True if successful
    """
    try:
        if verbose:
            logger.info(
                f"Creating {animation_config.frames} frames for animation..."
            )

        # Open movie file
        plotter.open_movie(output_filename, framerate=animation_config.framerate)

        # Generate frames
        for i in range(animation_config.frames):
            # Calculate camera position for this frame
            camera_pos = CameraController.calculate_animation_camera_position(
                config.longitude_focus,
                config.latitude_focus,
                i,
                animation_config,
            )

            # Update camera
            plotter.camera.focal_point = camera_pos.focal_point
            plotter.camera.position = camera_pos.camera_position
            plotter.camera.up = [0, 0, 1]

            # Render and write frame
            plotter.render()
            plotter.write_frame()

            # Progress reporting
            if verbose and (i + 1) % max(1, animation_config.frames // 10) == 0:
                progress_pct = (i + 1) / animation_config.frames * 100
                logger.info(f"  Frame {i+1}/{animation_config.frames} ({progress_pct:.1f}%)")

        # Close movie file
        plotter.close_movie()

        if verbose:
            logger.info("✓ Animation created successfully")

        return True

    except Exception as e:
        logger.error(f"Failed to create animation: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        try:
            plotter.close_movie()
        except:
            pass
        return False


def animate_mesh_with_vector_files(
    # Mesh inputs (optional)
    pMesh=None,
    aValid_cell_indices=None,
    sScalar=None,
    sUnit=None,
    # Vector inputs (optional)
    aFilename_vector_in=None,
    aVector_config=None,
    # Visualization configuration
    pConfig=None,
    # Animation configuration
    animation_config=None,
    # Output
    sFilename_out=None,
    # Advanced options
    style="surface",
    scalar_config=None,
    validate_inputs=True,
    return_detailed_result=False,
) -> Union[bool, AnimationResult]:
    """
    Create animated visualization combining mesh data and multiple vector file overlays.

    This function combines the capabilities of:
    - map_single_frame: Mesh visualization with scalar fields
    - animate_polyline_file_on_sphere: Vector file visualization with animation

    **NEW: Supports multiple vector files with individual styling!**

    Args:
        pMesh: GeoVista mesh object (optional if only showing vectors)
        aValid_cell_indices: Valid cell indices for mesh
        sScalar: Scalar field name to visualize on mesh
        sUnit: Unit string for scalar bar

        aFilename_vector_in: Vector file path(s). Can be:
            - Single string: "roads.shp"
            - List of strings: ["roads.shp", "rails.shp", "cities.geojson"]
        aVector_config: Vector styling configuration(s). Can be:
            - Single VectorLayerConfig: Applied to single file or all files
            - List of VectorLayerConfig: One per file (must match length)
            - None: Use default styling for all files

        pConfig: VisualizationConfig for camera, base layer, etc.
        animation_config: AnimationConfig for rotation parameters

        sFilename_out: Output file path (.mp4, .gif, .png)

        style: Mesh rendering style ('surface', 'wireframe', 'points')
        scalar_config: ScalarBarConfig for scalar bar customization
        validate_inputs: Whether to validate inputs
        return_detailed_result: Return detailed result object

    Returns:
        bool or AnimationResult: Success status or detailed result

    Examples:
        See design document for comprehensive examples.
    """
    # Use default config if not provided
    if pConfig is None:
        pConfig = VisualizationConfig()

    verbose = pConfig.verbose

    try:
        # Normalize vector inputs
        vector_files, vector_configs = _normalize_vector_inputs(
            aFilename_vector_in, aVector_config
        )

        # Validate inputs
        if pMesh is None and len(vector_files) == 0:
            error_msg = "At least one of pMesh or aFilename_vector_in must be provided"
            logger.error(error_msg)
            result = AnimationResult(False, error_msg, system_info=get_system_info())
            return result if return_detailed_result else False

        # Validate output filename if provided
        if sFilename_out:
            is_valid, validation_msg = validate_output_filename(
                sFilename_out, VALID_IMAGE_FORMATS + VALID_ANIMATION_FORMATS
            )
            if not is_valid:
                error_msg = f"Output filename validation failed: {validation_msg}"
                logger.error(error_msg)
                result = AnimationResult(False, error_msg)
                return result if return_detailed_result else False

        # Determine if this is an animation or static frame
        is_animation = False
        if sFilename_out:
            ext = os.path.splitext(sFilename_out.lower())[1].lstrip(".")
            is_animation = ext in VALID_ANIMATION_FORMATS

        # Create plotter
        if verbose:
            logger.info("🎨 Creating GeoVista plotter...")

        plotter = PlotterManager.setup_geovista_plotter(
            off_screen=(sFilename_out is not None),
            verbose=verbose,
            window_size=pConfig.window_size,
            use_xvfb=pConfig.use_xvfb,
            force_xvfb=pConfig.force_xvfb,
        )

        if plotter is None:
            error_msg = "Failed to create GeoVista plotter"
            logger.error(error_msg)
            result = AnimationResult(False, error_msg, system_info=get_system_info())
            return result if return_detailed_result else False

        # Add base layer if specified
        if pConfig.base_layer is not None:
            try:
                import geovista as gv
                if pConfig.base_layer == "natural_earth_hypsometric":
                    plotter.add_base_layer(texture=gv.natural_earth_hypsometric())
                elif pConfig.base_layer == "natural_earth_1":
                    plotter.add_base_layer(texture=gv.natural_earth_1())
                elif pConfig.base_layer == "blue_marble":
                    plotter.add_base_layer(texture=gv.blue_marble())
                if verbose:
                    logger.info(f"🌍 Added base layer: {pConfig.base_layer}")
            except Exception as e:
                logger.warning(f"Failed to add base layer: {e}")

        layer_info = {}

        # Add mesh if provided
        if pMesh is not None and aValid_cell_indices is not None:
            if verbose:
                logger.info("📐 Adding mesh data to plotter...")

            mesh_success = add_mesh_to_plotter(
                plotter=plotter,
                mesh=pMesh,
                style=style,
                valid_indices=aValid_cell_indices,
                scalar_name=sScalar,
                scalar_config=scalar_config,
                colormap=pConfig.colormap,
                color= pConfig.color,
                unit=sUnit or "",
                validate_data=validate_inputs,
                opacity=getattr(pConfig, "mesh_opacity", 1.0),
            )

            if mesh_success:
                layer_info["mesh"] = {"cells": len(aValid_cell_indices)}

        # Add vector layers if provided
        if len(vector_files) > 0:
            if verbose:
                logger.info(f"📍 Adding {len(vector_files)} vector layer(s)...")

            vector_layer_info = _add_multiple_vector_layers(
                plotter, vector_files, vector_configs, verbose
            )
            layer_info.update(vector_layer_info)

        # Configure camera
        if verbose:
            logger.info("📷 Configuring camera position...")

        configure_camera_enhanced(plotter=plotter, config=pConfig)

        # Add geographic context
        if verbose:
            logger.info("🌍 Adding geographic context...")

        add_geographic_context_enhanced(plotter=plotter, config=pConfig)

        # Handle output
        file_info = {}
        animation_info = {}

        if sFilename_out:
            if is_animation:
                # Create animation
                if animation_config is None:
                    animation_config = AnimationConfig()

                if verbose:
                    logger.info(f"🎬 Creating animation: {sFilename_out}")

                anim_success = _create_animation_frames(
                    plotter, pConfig, animation_config, sFilename_out, verbose
                )

                if not anim_success:
                    error_msg = "Failed to create animation"
                    result = AnimationResult(False, error_msg, layer_info=layer_info)
                    return result if return_detailed_result else False

                animation_info = {
                    "frames": animation_config.frames,
                    "duration": animation_config.estimated_duration,
                }
            else:
                # Save static frame
                if verbose:
                    logger.info(f"💾 Saving visualization to: {sFilename_out}")

                ext = os.path.splitext(sFilename_out.lower())[1].lstrip(".")
                if ext in ["png", "jpg", "jpeg"]:
                    plotter.screenshot(sFilename_out)
                else:
                    plotter.save_graphic(sFilename_out, raster=False)

            # Verify file
            if os.path.exists(sFilename_out):
                file_size = os.path.getsize(sFilename_out)
                file_info = {
                    "filename": sFilename_out,
                    "size_bytes": file_size,
                    "size_kb": file_size / 1024,
                    "size_mb": file_size / (1024 * 1024),
                    "exists": True,
                }
                if verbose:
                    logger.info(f"✅ Visualization saved successfully")
                    logger.info(f"📁 File: {sFilename_out}")
                    logger.info(f"📏 Size: {file_info['size_mb']:.2f} MB")
        else:
            # Interactive display
            if verbose:
                logger.info("🖥️ Opening interactive visualization window...")

            plotter.show()

        # Success
        result = AnimationResult(
            success=True,
            message="Visualization completed successfully",
            file_info=file_info,
            animation_info=animation_info,
            layer_info=layer_info,
            system_info=get_system_info() if return_detailed_result else {},
        )

        return result if return_detailed_result else True

    except Exception as e:
        error_msg = f"Unexpected error in visualization: {e}"
        logger.error(error_msg)
        logger.error(f"Traceback: {traceback.format_exc()}")

        result = AnimationResult(False, error_msg, system_info=get_system_info())
        return result if return_detailed_result else False

    finally:
        # Cleanup
        if 'plotter' in locals() and plotter is not None:
            try:
                plotter.close()
                if verbose:
                    logger.debug("Plotter resources cleaned up")
            except Exception as e:
                logger.warning(f"Error during plotter cleanup: {e}")