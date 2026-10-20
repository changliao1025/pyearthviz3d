#!/usr/bin/env python
"""
Example 3: Combining Global 3D Mesh with Vector GIS Overlays.

Demonstrates:
- Loading multi-layer vector GIS lines from GeoJSON files (`data/flight_routes.geojson`, `data/shipping_routes.geojson`).
- Styling each vector layer individually with `VectorLayerConfig` (color, line width, z-order).
- Interactive 3D visualization using GeoVista engine or exporting to a PNG image with `animate_mesh_with_vector_files`.

Usage:
    # Interactive 3D globe (rotate, pan, zoom with mouse)
    python examples/03_mesh_with_vector_overlays.py --interactive

    # Export to PNG image
    python examples/03_mesh_with_vector_overlays.py --export vector_mesh.png
"""

import argparse
import os

import geovista as gv
import numpy as np

from pyearthviz3d import (
    VectorLayerConfig,
    VisualizationConfig,
    animate_mesh_with_vector_files,
)
from pyearthviz3d.geovista._environment import detect_headless_environment


def main():
    parser = argparse.ArgumentParser(
        description="Composite mesh and vector overlay 3D visualization (interactive or PNG export)."
    )
    parser.add_argument(
        "--export",
        nargs="?",
        const="mesh_with_vectors_output.png",
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
    flights_geojson = os.path.join(repo_root, "data", "vector", "flight_routes.geojson")
    shipping_geojson = os.path.join(
        repo_root, "data", "vector", "shipping_routes.geojson"
    )

    # If dataset has not been generated yet, generate it on the fly
    if not os.path.exists(flights_geojson):
        print("Data files not found, running export script...")
        import subprocess
        import sys

        subprocess.run(
            [
                sys.executable,
                os.path.join(os.path.dirname(__file__), "00_export_sample_data.py"),
            ],
            check=True,
        )

    # 1. Create base spherical mesh with topography elevation scalar
    print("Generating base spherical topography mesh...")
    lons = np.linspace(-180, 180, 73)
    lats = np.linspace(-90, 90, 37)
    mesh = gv.Transform.from_1d(lons, lats)

    lon_grid, lat_grid = np.meshgrid(
        np.radians((lons[:-1] + lons[1:]) / 2.0),
        np.radians((lats[:-1] + lats[1:]) / 2.0),
    )
    topo = np.sin(2.0 * lat_grid) * np.cos(2.0 * lon_grid) * 3000.0
    mesh.cell_data["elevation"] = topo.ravel()
    valid_indices = np.arange(mesh.n_cells)

    # 2. Configure multiple vector layers with distinct styling and z-order
    flight_layer_config = VectorLayerConfig(
        color="crimson",
        linewidth=3.0,
        opacity=1.0,
        layer_name="Commercial Flight Corridors",
        z_order=10,
    )

    shipping_layer_config = VectorLayerConfig(
        color="gold",
        linewidth=2.5,
        opacity=0.9,
        layer_name="Global Shipping Corridors",
        z_order=5,
    )

    vector_files = [flights_geojson, shipping_geojson]
    vector_configs = [flight_layer_config, shipping_layer_config]

    # Filter to files that exist
    active_files = []
    active_configs = []
    for fpath, cfg in zip(vector_files, vector_configs):
        if os.path.exists(fpath):
            active_files.append(fpath)
            active_configs.append(cfg)
            print(f"Loaded vector dataset: {fpath}")

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
            os.path.dirname(__file__), "mesh_with_vectors_output.png"
        )
        print(f"Headless environment detected. Mode: Exporting to {output_filename}...")

    # 3. Configure visualization parameters
    viz_config = VisualizationConfig(
        longitude_focus=-30.0,
        latitude_focus=35.0,
        zoom_factor=0.85,
        show_coastlines=True,
        show_graticule=True,
        coastline_color="darkgray",
        colormap="terrain",
        verbose=True,
    )

    # 4. Render composite visualization
    result = animate_mesh_with_vector_files(
        pMesh=mesh,
        aValid_cell_indices=valid_indices,
        sScalar="elevation",
        sUnit="m",
        aFilename_vector_in=active_files,
        aVector_config=active_configs,
        pConfig=viz_config,
        sFilename_out=output_filename,
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
