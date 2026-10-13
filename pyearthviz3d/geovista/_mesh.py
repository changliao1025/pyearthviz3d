"""Mesh validation and rendering helpers."""

import logging
from typing import Any, Dict, Optional

import numpy as np

from ._config import ScalarBarConfig

logger = logging.getLogger(__name__)


class MeshHandler:
    """Utility class for handling mesh operations."""

    @staticmethod
    def validate_mesh_data(mesh, valid_indices: np.ndarray) -> bool:
        """Validate mesh and indices for visualization."""
        try:
            if mesh is None:
                logger.error("Mesh is None")
                return False

            if valid_indices is None or len(valid_indices) == 0:
                logger.error("No valid cell indices provided")
                return False

            # Check if indices are within bounds
            if hasattr(mesh, "n_cells") and np.max(valid_indices) >= mesh.n_cells:
                logger.error("Cell indices exceed mesh size")
                return False

            return True
        except Exception as e:
            logger.error(f"Error validating mesh data: {e}")
            return False

    @staticmethod
    def extract_valid_mesh(mesh, valid_indices: np.ndarray):
        """Extract valid cells from mesh with error handling."""
        try:
            if not MeshHandler.validate_mesh_data(mesh, valid_indices):
                return None
            return mesh.extract_cells(valid_indices)
        except Exception as e:
            logger.error(f"Error extracting valid mesh cells: {e}")
            return None

    @staticmethod
    def get_scalar_info(mesh, scalar_name: str) -> Dict[str, Any]:
        """Get information about scalar data in mesh."""
        try:
            if not hasattr(mesh, "array_names") or scalar_name not in mesh.array_names:
                return {"exists": False, "range": None, "dtype": None}

            scalar_data = mesh[scalar_name]
            return {
                "exists": True,
                "range": (np.nanmin(scalar_data), np.nanmax(scalar_data)),
                "dtype": scalar_data.dtype,
                "has_nan": np.any(np.isnan(scalar_data)),
                "shape": scalar_data.shape,
            }
        except Exception as e:
            logger.error(f"Error getting scalar info: {e}")
            return {"exists": False, "range": None, "dtype": None}


def add_mesh_to_plotter(
    plotter,
    mesh,
    valid_indices: np.ndarray,
    scalar_name: Optional[str] = None,
    scalar_config: Optional[ScalarBarConfig] = None,
    style: str = "surface",
    color: str = "white",
    colormap: str = "viridis",
    unit: str = "",
    opacity: float = 1.0,
    show_edges: bool = False,
    edge_color: str = "black",
    validate_data: bool = True,
) -> bool:
    """
    Add mesh to plotter with comprehensive validation and error handling.

    Args:
        plotter: GeoVista plotter instance
        mesh: Mesh object to visualize
        valid_indices: Indices of valid cells
        scalar_name: Name of scalar field to visualize
        scalar_config: Scalar bar configuration
        style: Mesh rendering style ('surface', 'wireframe', 'points')
        color: Mesh color (used when no scalars)
        colormap: Colormap name for scalar visualization
        unit: Unit string for scalar bar
        opacity: Mesh opacity (0.0 to 1.0)
        show_edges: Whether to show mesh edges
        edge_color: Color of mesh edges
        validate_data: Whether to validate mesh data before processing

    Returns:
        bool: True if successful
    """
    try:
        # Validate inputs
        if validate_data and not MeshHandler.validate_mesh_data(mesh, valid_indices):
            logger.error("Mesh validation failed")
            return False

        # Extract valid mesh
        mesh_valid = MeshHandler.extract_valid_mesh(mesh, valid_indices)
        if mesh_valid is None:
            logger.error("Failed to extract valid mesh")
            return False

        # Configure scalar visualization
        if scalar_name and colormap is not None:
            # Get scalar information
            scalar_info = MeshHandler.get_scalar_info(mesh_valid, scalar_name)
            if not scalar_info["exists"]:
                logger.warning(f"Scalar '{scalar_name}' not found in mesh, adding without scalars")
                plotter.add_mesh(mesh_valid)
                return True

            # Configure scalar bar
            if scalar_config is None:
                scalar_config = ScalarBarConfig()

            scalar_args = scalar_config.to_dict(scalar_name, unit)

            # Handle discrete colorbars
            discrete_labels = scalar_args.pop("discrete_labels", None)
            value_colors = scalar_args.pop("value_colors", None)

            if discrete_labels is not None and value_colors is not None:
                # Create custom colormap for discrete values
                from matplotlib.colors import ListedColormap, BoundaryNorm

                # Get actual unique values present in the mesh data
                mesh_data_values = mesh_valid[scalar_name]
                actual_unique_values = np.unique(mesh_data_values[np.isfinite(mesh_data_values)])

                # Special treatment for missing data: convert negative values to 0
                actual_unique_values[actual_unique_values <= 0] = 0

                # Get unique values after conversion and convert to int list
                actual_unique_values = np.unique(actual_unique_values)  # Re-unique after conversion
                actual_unique_values = [int(v) for v in actual_unique_values]

                # Filter to only include values that are in the provided discrete_labels
                # and actually present in the data
                unique_values = sorted([v for v in actual_unique_values if v in discrete_labels])

                if len(unique_values) == 0:
                    # Fall back to all provided labels if no match found
                    logger.warning(
                        "No matching discrete labels found in data, using all provided labels"
                    )
                    unique_values = sorted(discrete_labels.keys())

                # Create a remapped scalar field where values are mapped to sequential indices
                # This ensures colors align properly with labels
                n_categories = len(unique_values)
                value_to_index = {val: idx for idx, val in enumerate(unique_values)}

                # Remap the scalar values to sequential indices (0, 1, 2, ...)
                # All values in discrete_labels (including 0 for "No Data") are treated as valid categories
                remapped_scalars = np.copy(mesh_valid[scalar_name]).astype(int)

                # Remap all provided discrete values to sequential indices
                for val, idx in value_to_index.items():
                    mask = mesh_valid[scalar_name] == val
                    count = np.sum(mask)
                    if count > 0:
                        remapped_scalars[mask] = idx

                # Add remapped scalars to mesh
                mesh_valid[f"{scalar_name}_remapped"] = remapped_scalars

                # Create discrete colormap for PyVista
                from matplotlib.colors import to_rgb, ListedColormap
                import matplotlib.pyplot as plt

                # Create color list from value_colors dictionary in correct order
                colors_rgb = [to_rgb(value_colors.get(val, "#FFFFFF")) for val in unique_values]

                # Create discrete colormap with N=n_categories
                # Use a unique name for this specific colormap
                cmap_name = f"discrete_lucc_{id(value_colors)}"
                cmap = ListedColormap(colors_rgb, name=cmap_name, N=n_categories)

                # Register the colormap with matplotlib
                try:
                    plt.cm.unregister_cmap(cmap_name)
                except:
                    pass
                plt.cm.register_cmap(cmap=cmap, name=cmap_name)

                # Create annotations dictionary mapping sequential indices to labels
                annotations = {
                    idx: discrete_labels.get(unique_values[idx], str(unique_values[idx]))
                    for idx in range(n_categories)
                }

                # Hide default numeric labels - annotations will provide the text labels
                scalar_args["n_labels"] = 0
                scalar_args["fmt"] = ""

                # Debug output
                print(f"\n{'='*60}")
                print(f"DEBUG: Creating discrete colorbar with {n_categories} categories")
                print(f"DEBUG: Unique values (sorted): {unique_values}")
                print(f"DEBUG: Colormap name: {cmap_name}")
                print(f"DEBUG: Color mapping:")
                for idx, val in enumerate(unique_values):
                    hex_color = value_colors.get(val, "#FFFFFF")
                    rgb = colors_rgb[idx]
                    print(
                        f"  Index {idx} -> Value {val} -> Hex {hex_color} -> RGB {rgb} -> Label '{discrete_labels.get(val)}'"
                    )
                print(
                    f"DEBUG: Remapped scalars range: {remapped_scalars.min()} to {remapped_scalars.max()}"
                )
                print(f"DEBUG: Remapped unique values: {np.unique(remapped_scalars)}")
                print(f"{'='*60}\n")

                # For discrete colorbars with categories=True, PyVista uses the colormap
                # to assign colors directly to sequential indices. We pass the colormap object
                # directly without clim to let PyVista handle it properly.
                plotter.add_mesh(
                    mesh_valid,
                    scalars=f"{scalar_name}_remapped",
                    style=style,
                    categories=True,  # Treat scalars as categorical for discrete colorbar
                    scalar_bar_args=scalar_args,
                    clim=(-0.5, n_categories - 0.5),  # Set clim to match the number of categories
                    cmap=cmap,  # Pass colormap object directly for categories=True
                    annotations=annotations,
                    opacity=opacity,
                    show_edges=show_edges,
                    edge_color=edge_color,
                )
            else:
                # Add mesh with continuous scalars
                plotter.add_mesh(
                    mesh_valid,
                    scalars=scalar_name,
                    style=style,
                    scalar_bar_args=scalar_args,
                    cmap=colormap,
                    opacity=opacity,
                    show_edges=show_edges,
                    edge_color=edge_color,
                )

            if scalar_info["has_nan"]:
                logger.warning(f"Scalar field '{scalar_name}' contains NaN values")
        else:
            # Add mesh without scalars
            plotter.add_mesh(
                mesh_valid,
                style=style,
                color=color,
                opacity=opacity,
                show_edges=show_edges,
                edge_color=edge_color,
            )

        return True

    except Exception as e:
        logger.error(f"Failed to add mesh to plotter: {e}")
        return False
