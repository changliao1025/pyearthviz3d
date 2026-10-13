"""Vector data loading and geometry conversion helpers."""

import logging
import math
import os
import traceback
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from osgeo import gdal, ogr, osr

logger = logging.getLogger(__name__)


def transform_vectors_sph_to_cart(theta, phi, r, u, v, w):
    """Transform vectors from spherical (r, phi, theta) to cartesian coordinates (z, y, x).

    Note the "reverse" order of arrays's axes, commonly used in geosciences.

    Parameters
    ----------
    theta : array_like[float]
        Azimuthal angle in degrees ``[0, 360]`` of shape (M,)
    phi : array_like[float]
        Polar (zenith) angle in degrees ``[0, 180]`` of shape (N,)
    r : array_like[float]
        Distance (radius) from the point of origin of shape (P,)
    u : array_like[float]
        X-component of the vector of shape (P, N, M)
    v : array_like[float]
        Y-component of the vector of shape (P, N, M)
    w : array_like[float]
        Z-component of the vector of shape (P, N, M)

    Returns
    -------
    u_t, v_t, w_t : :class:`numpy.ndarray`
        Arrays of transformed x-, y-, z-components, respectively.
    """
    xx, yy, _ = np.meshgrid(np.radians(theta), np.radians(phi), r, indexing="ij")
    th, ph = xx.squeeze(), yy.squeeze()

    u_t = np.sin(ph) * np.cos(th) * w + np.cos(ph) * np.cos(th) * v - np.sin(th) * u
    v_t = np.sin(ph) * np.sin(th) * w + np.cos(ph) * np.sin(th) * v + np.cos(th) * u
    w_t = np.cos(ph) * w - np.sin(ph) * v

    return u_t, v_t, w_t


def normalize_vector_inputs(
    aFilename_vector_in: Union[str, List[str], None],
    aVector_config: Any = None,
    default_config_factory: Any = None,
) -> Tuple[List[str], List[Any]]:
    """Normalize vector inputs and configs to parallel lists.

    Args:
        aFilename_vector_in: Single file path or list of file paths
        aVector_config: Single config or list of configs
        default_config_factory: Callable returning a default config instance

    Returns:
        Tuple of (list of file paths, list of configs)
    """
    if aFilename_vector_in is None:
        return [], []

    if isinstance(aFilename_vector_in, str):
        file_paths = [aFilename_vector_in]
    else:
        file_paths = list(aFilename_vector_in)

    if aVector_config is None:
        if default_config_factory is not None:
            configs = [default_config_factory() for _ in file_paths]
        else:
            configs = [None for _ in file_paths]
    elif not isinstance(aVector_config, (list, tuple)):
        configs = [aVector_config for _ in file_paths]
    else:
        configs = list(aVector_config)
        if len(configs) != len(file_paths):
            raise ValueError(
                f"Number of vector configs ({len(configs)}) must match "
                f"number of vector files ({len(file_paths)})"
            )

    return file_paths, configs


def load_vector_geometries(
    filename: str,
    linewidth_attribute: Optional[str] = None,
    default_linewidth: float = 2.0,
    linewidth_range: Tuple[float, float] = (0.5, 3.0),
    layer_name: Optional[str] = None,
    allowed_geom_types: Optional[List[str]] = None,
    verbose: bool = False,
) -> Tuple[List[Any], List[float], Dict[str, Any]]:
    """Load vector data from file using GDAL/OGR and convert to WGS84.

    Args:
        filename: Path to vector file
        linewidth_attribute: Optional feature attribute name for variable line width
        default_linewidth: Fallback / uniform line width
        linewidth_range: (min, max) tuple for scaling line width
        layer_name: Optional descriptive layer name
        allowed_geom_types: Optional list of allowed geometry types (e.g. ['LINESTRING', 'MULTILINESTRING'])
        verbose: Enable verbose logging

    Returns:
        Tuple of (geometries, linewidths, info_dict)
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Vector file not found: {filename}")

    if allowed_geom_types is None:
        allowed_types = [
            "LINESTRING",
            "MULTILINESTRING",
            "POINT",
            "MULTIPOINT",
            "POLYGON",
            "MULTIPOLYGON",
        ]
    else:
        allowed_types = [t.upper() for t in allowed_geom_types]

    try:
        dataset = ogr.Open(filename, gdal.GA_ReadOnly)
        if dataset is None:
            raise RuntimeError(f"Could not open vector file: {filename}")

        layer = dataset.GetLayer(0)
        if layer is None:
            raise RuntimeError("Could not get layer from dataset")

        feature_count = layer.GetFeatureCount()
        if verbose:
            logger.info(f"Loading {feature_count} features from {os.path.basename(filename)}")

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

        geometries = []
        linewidth_values = []

        layer.ResetReading()
        for feature in layer:
            geometry = feature.GetGeometryRef()
            if geometry is None:
                continue

            geom_name = geometry.GetGeometryName().upper()

            if geom_name in allowed_types:
                geom_clone = geometry.Clone()

                if transform is not None:
                    geom_clone.Transform(transform)

                geometries.append(geom_clone)

                if linewidth_attribute is not None:
                    try:
                        width_value = feature.GetField(linewidth_attribute)
                        if width_value is not None:
                            linewidth_values.append(float(width_value))
                        else:
                            linewidth_values.append(default_linewidth)
                    except Exception as e:
                        if verbose:
                            logger.warning(f"Could not read attribute {linewidth_attribute}: {e}")
                        linewidth_values.append(default_linewidth)
                else:
                    linewidth_values.append(default_linewidth)

        if len(geometries) == 0:
            raise RuntimeError("No valid geometries found in file")

        # Scale linewidths if attribute was used
        scaled_widths = []
        if linewidth_attribute is not None and len(linewidth_values) > 0:
            data_min, data_max = min(linewidth_values), max(linewidth_values)
            if data_max > data_min:
                min_w, max_w = linewidth_range
                for val in linewidth_values:
                    scaled_width = min_w + (val - data_min) / (data_max - data_min) * (
                        max_w - min_w
                    )
                    scaled_widths.append(scaled_width)
                if verbose:
                    logger.info(
                        f'Using variable line widths from attribute "{linewidth_attribute}" '
                        f"(range: {data_min:.2f} to {data_max:.2f})"
                    )
            else:
                scaled_widths = [default_linewidth] * len(geometries)
        else:
            scaled_widths = linewidth_values

        info_dict = {
            "filename": filename,
            "features": len(geometries),
            "name": layer_name or os.path.basename(filename),
        }

        return geometries, scaled_widths, info_dict

    except Exception as e:
        logger.error(f"Failed to load vector data from {filename}: {e}")
        raise


def geometries_to_polydata(
    geometries: List[Any],
    radius: float = 1.0,
    verbose: bool = False,
) -> Optional[Any]:
    """Convert a collection of OGR geometries on a sphere into a PyVista PolyData mesh.

    Args:
        geometries: List of OGR geometry objects in WGS84 (lon, lat)
        radius: Sphere radius (default 1.0)
        verbose: Enable verbose logging

    Returns:
        pyvista.PolyData instance, or None if conversion fails
    """
    try:
        import pyvista as pv

        all_points = []
        all_lines = []
        point_offset = 0

        for i, geometry in enumerate(geometries):
            points = geometry.GetPoints()
            if points is None or len(points) < 2:
                continue

            lons = np.array([point[0] for point in points])
            lats = np.array([point[1] for point in points])

            lons_rad = np.deg2rad(lons)
            lats_rad = np.deg2rad(lats)

            x = radius * np.cos(lats_rad) * np.cos(lons_rad)
            y = radius * np.cos(lats_rad) * np.sin(lons_rad)
            z = radius * np.sin(lats_rad)

            for j in range(len(points)):
                all_points.append([x[j], y[j], z[j]])

            n_points = len(points)
            line = [n_points] + list(range(point_offset, point_offset + n_points))
            all_lines.append(line)
            point_offset += n_points

            if verbose and len(geometries) > 10000 and (i + 1) % 50000 == 0:
                logger.info(f"  Processed {i + 1}/{len(geometries)} geometries...")

        if len(all_points) == 0:
            logger.error("No valid points found to construct PolyData")
            return None

        points_array = np.array(all_points, dtype=np.float64)

        lines_flat = []
        for line in all_lines:
            lines_flat.extend(line)
        lines_array = np.array(lines_flat, dtype=np.int64)

        return pv.PolyData(points_array, lines=lines_array)

    except Exception as e:
        logger.error(f"Failed to convert geometries to PolyData: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None
