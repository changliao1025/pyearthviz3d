#!/usr/bin/env python
"""
Example 2: Unstructured Geodesic Mesh (UGRID NetCDF).

Demonstrates:
- Loading an unstructured triangular geodesic mesh from NetCDF (UGRID-1.0 format).
- Constructing a 3D spherical mesh from nodes and face connectivity with `geovista.Transform.from_unstructured`.
- Interactive 3D visualization using the GeoVista engine (default) or exporting to a PNG image with mesh cell edges highlighted.

Usage:
    # Interactive 3D globe (rotate, pan, zoom with mouse)
    python examples/02_unstructured_geodesic_mesh.py --interactive

    # Export to PNG image
    python examples/02_unstructured_geodesic_mesh.py --export unstructured_mesh.png
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


def load_unstructured_ugrid_dataset(nc_path: str):
    """Load unstructured mesh topology and scalar fields from UGRID NetCDF file."""
    with nc.Dataset(nc_path, "r") as ds:
        node_lons = ds.variables["Mesh2_node_x"][:]
        node_lats = ds.variables["Mesh2_node_y"][:]
        face_nodes = ds.variables["Mesh2_face_nodes"][:]
        vorticity = ds.variables["vorticity"][:]
        ssh = ds.variables["sea_surface_height"][:]

    return node_lons, node_lats, face_nodes, vorticity, ssh


def main():
    parser = argparse.ArgumentParser(
        description="Unstructured geodesic mesh 3D visualization (interactive or PNG export)."
    )
    parser.add_argument(
        "--export",
        nargs="?",
        const="unstructured_mesh_output.png",
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
        repo_root, "data", "unstructured", "unstructured_geodesic_mesh.nc"
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

    print(f"Loading unstructured UGRID dataset from {nc_path}...")
    node_lons, node_lats, face_nodes, vorticity, ssh = load_unstructured_ugrid_dataset(
        nc_path
    )
    print(f"Loaded {len(node_lons)} nodes and {len(face_nodes)} triangular faces.")

    # Build unstructured 3D spherical mesh via GeoVista bridge
    print("Constructing 3D spherical mesh from unstructured connectivity...")
    mesh = gv.Transform.from_unstructured(
        xs=node_lons,
        ys=node_lats,
        connectivity=face_nodes,
        data=vorticity,
        name="vorticity",
        start_index=0,
    )
    mesh.cell_data["sea_surface_height"] = ssh
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
        output_filename = os.path.join(
            os.path.dirname(__file__), "unstructured_mesh_output.png"
        )
        print(f"Headless environment detected. Mode: Exporting to {output_filename}...")

    # Configure visualization with cell edges enabled to highlight unstructured triangulation
    viz_config = VisualizationConfig(
        longitude_focus=15.0,
        latitude_focus=30.0,
        zoom_factor=0.85,
        show_coastlines=True,
        show_graticule=True,
        coastline_color="black",
        coastline_width=1.2,
        colormap="coolwarm",
        verbose=True,
    )

    scalar_config = ScalarBarConfig(
        title="Relative Vorticity",
        title_font_size=12,
        label_font_size=10,
        fmt="%.2e",
        n_labels=5,
        orientation="horizontal",
    )

    result = map_single_frame(
        pMesh=mesh,
        aValid_cell_indices=valid_indices,
        pConfig=viz_config,
        sScalar="vorticity",
        sUnit="s⁻¹",
        sFilename_out=output_filename,
        scalar_config=scalar_config,
        show_edges=True,
        edge_color="dimgray",
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
