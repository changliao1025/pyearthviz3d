#!/usr/bin/env python
"""
Example 1: Structured Global Climate Mesh (NetCDF-4).

Demonstrates:
- Loading a structured rectilinear global climate dataset from NetCDF-4 (`data/structured_global_climate.nc`).
- Constructing a 3D spherical mesh with `geovista.Transform.from_1d`.
- Interactive 3D visualization using the GeoVista engine (default) or exporting to a PNG image.

Usage:
    # Interactive 3D globe (rotate, pan, zoom with mouse)
    python examples/01_single_frame_structured_mesh.py --interactive

    # Export to PNG image
    python examples/01_single_frame_structured_mesh.py --export structured_mesh.png
"""

import argparse
import os

import geovista as gv
import netCDF4 as nc
import numpy as np

from pyearthviz3d import (
    ScalarBarConfig,
    VisualizationConfig,
    map_single_frame,
)
from pyearthviz3d.geovista._environment import detect_headless_environment


def load_structured_climate_dataset(nc_path: str):
    """Load coordinates and scalar fields from structured NetCDF file."""
    with nc.Dataset(nc_path, "r") as ds:
        lats = ds.variables["lat"][:]
        lons = ds.variables["lon"][:]
        temp = ds.variables["temperature"][:]
        elev = ds.variables["elevation"][:]

    return lons, lats, temp, elev


def main():
    parser = argparse.ArgumentParser(
        description="Structured global climate 3D visualization (interactive or PNG export)."
    )
    parser.add_argument(
        "--export",
        nargs="?",
        const="structured_mesh_output.png",
        default=None,
        help="Export rendered globe to PNG image file (e.g. --export or --export output.png).",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch interactive 3D GeoVista window (default if display is available).",
    )
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(__file__))
    nc_path = os.path.join(
        repo_root, "data", "structured", "structured_global_climate.nc"
    )

    # If dataset has not been generated yet, generate it on the fly
    if not os.path.exists(nc_path):
        print(f"Data file not found at {nc_path}, running export script...")
        import subprocess
        import sys

        subprocess.run(
            [
                sys.executable,
                os.path.join(os.path.dirname(__file__), "00_export_sample_data.py"),
            ],
            check=True,
        )

    print(f"Loading structured NetCDF dataset from {nc_path}...")
    lons, lats, temp, elev = load_structured_climate_dataset(nc_path)
    print(f"Grid dimensions: {len(lats)} latitudes x {len(lons)} longitudes.")

    # Create 3D spherical mesh from structured coordinates
    print("Constructing 3D spherical mesh...")
    mesh = gv.Transform.from_1d(lons, lats)

    # Attach cell-centered scalars
    temp_cells = (temp[:-1, :-1] + temp[1:, :-1] + temp[:-1, 1:] + temp[1:, 1:]) / 4.0
    mesh.cell_data["temperature"] = temp_cells.ravel()

    elev_cells = (elev[:-1, :-1] + elev[1:, :-1] + elev[:-1, 1:] + elev[1:, 1:]) / 4.0
    mesh.cell_data["elevation"] = elev_cells.ravel()
    valid_indices = np.arange(mesh.n_cells)

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
        # Headless fallback
        output_filename = os.path.join(
            os.path.dirname(__file__), "structured_mesh_output.png"
        )
        print(f"Headless environment detected. Mode: Exporting to {output_filename}...")

    # Configure visualization
    viz_config = VisualizationConfig(
        longitude_focus=-95.0,  # Center over North America
        latitude_focus=35.0,
        zoom_factor=0.85,
        show_coastlines=True,
        show_graticule=True,
        coastline_color="black",
        coastline_width=1.2,
        colormap="plasma",
        verbose=True,
    )

    scalar_config = ScalarBarConfig(
        title="Surface Temperature",
        title_font_size=12,
        label_font_size=10,
        fmt="%.1f",
        n_labels=6,
        orientation="horizontal",
    )

    result = map_single_frame(
        pMesh=mesh,
        aValid_cell_indices=valid_indices,
        pConfig=viz_config,
        sScalar="temperature",
        sUnit="K",
        sFilename_out=output_filename,
        scalar_config=scalar_config,
        show_edges=False,
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
