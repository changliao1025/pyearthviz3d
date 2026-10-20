#!/usr/bin/env python
"""
Example 4: Categorical & Discrete Classification Visualization.

Demonstrates:
- Creating integer-classified data (Land Use / Land Cover categories).
- Defining discrete color palettes and human-readable label annotations with `ScalarBarConfig`.
- Interactive 3D visualization using GeoVista engine or exporting to a PNG image with `map_single_frame`.

Usage:
    # Interactive 3D globe (rotate, pan, zoom with mouse)
    python examples/04_discrete_scalar_colorbar.py --interactive

    # Export to PNG image
    python examples/04_discrete_scalar_colorbar.py --export discrete_categories.png
"""

import argparse
import os

import geovista as gv
import numpy as np

from pyearthviz3d import (
    ScalarBarConfig,
    VisualizationConfig,
    map_single_frame,
)
from pyearthviz3d.geovista._environment import detect_headless_environment


def main():
    parser = argparse.ArgumentParser(
        description="Discrete classification 3D globe visualization (interactive or PNG export)."
    )
    parser.add_argument(
        "--export",
        nargs="?",
        const="discrete_categories_output.png",
        default=None,
        help="Export rendered globe to PNG image file (e.g. --export or --export output.png).",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch interactive 3D GeoVista window (default if display is available).",
    )
    args = parser.parse_args()

    print("Generating discrete categorical Earth mesh...")
    lons = np.linspace(-180, 180, 73)
    lats = np.linspace(-90, 90, 37)
    mesh = gv.Transform.from_1d(lons, lats)

    # Synthetic land classification categories (1 to 5)
    # 1: Water / Ocean
    # 2: Forest
    # 3: Grassland / Savannah
    # 4: Desert / Barren
    # 5: Ice / Tundra
    lon_grid, lat_grid = np.meshgrid(
        np.radians((lons[:-1] + lons[1:]) / 2.0),
        np.radians((lats[:-1] + lats[1:]) / 2.0),
    )

    classes = np.ones_like(lat_grid, dtype=int)
    classes[np.abs(lat_grid) > np.radians(65)] = 5  # Polar ice
    classes[
        (np.abs(lat_grid) <= np.radians(65)) & (np.abs(lat_grid) > np.radians(35))
    ] = 2  # Forest
    classes[
        (np.abs(lat_grid) <= np.radians(35)) & (np.abs(lat_grid) > np.radians(15))
    ] = 3  # Grassland
    classes[
        (np.abs(lat_grid) <= np.radians(15)) & (np.abs(lon_grid) < np.radians(40))
    ] = 4  # Desert

    mesh.cell_data["land_cover"] = classes.ravel()
    valid_indices = np.arange(mesh.n_cells)

    # Define human-readable labels and distinct category colors
    discrete_labels = {
        1: "Water / Ocean",
        2: "Temperate Forest",
        3: "Grassland / Savannah",
        4: "Arid / Desert",
        5: "Polar Ice / Tundra",
    }

    value_colors = {
        1: "#1f77b4",  # Blue
        2: "#2ca02c",  # Green
        3: "#bcbd22",  # Yellow-green
        4: "#ff7f0e",  # Orange
        5: "#aec7e8",  # Light blue
    }

    # Determine execution mode: export to file or interactive window
    if args.export:
        output_filename = os.path.abspath(args.export)
        print(f"Mode: Exporting to {output_filename}...")
    elif args.interactive or not detect_headless_environment():
        output_filename = None
        print(
            "Mode: Interactive 3D GeoVista window (rotate/pan/zoom with mouse). Close window to finish."
        )
    else:
        output_filename = os.path.join(
            os.path.dirname(__file__), "discrete_categories_output.png"
        )
        print(f"Headless environment detected. Mode: Exporting to {output_filename}...")

    # Configure discrete colorbar
    scalar_config = ScalarBarConfig(
        title="Land Cover Classification",
        discrete_labels=discrete_labels,
        value_colors=value_colors,
        title_font_size=12,
        label_font_size=9,
        orientation="horizontal",
    )

    # Configure visualization
    viz_config = VisualizationConfig(
        longitude_focus=20.0,  # Centered over Africa / Europe
        latitude_focus=20.0,
        zoom_factor=0.85,
        show_coastlines=True,
        show_graticule=True,
        coastline_color="black",
        coastline_width=1.0,
        verbose=True,
    )

    result = map_single_frame(
        pMesh=mesh,
        aValid_cell_indices=valid_indices,
        pConfig=viz_config,
        sScalar="land_cover",
        sFilename_out=output_filename,
        scalar_config=scalar_config,
        return_detailed_result=True,
    )

    if hasattr(result, "get_summary"):
        print(result.get_summary())

    if output_filename and os.path.exists(output_filename):
        print(
            f"Successfully generated: {output_filename} ({os.path.getsize(output_filename) // 1024} KB)"
        )


if __name__ == "__main__":
    main()
