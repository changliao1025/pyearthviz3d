#!/usr/bin/env python
"""
Example 5: Rotating 3D Globe Animation.

Demonstrates:
- Creating a rotating camera animation around a global mesh.
- Configuring animation parameters (number of frames, speed, framerate).
- Creating quick preview snapshots with `create_animation_preview`.
- Generating an animation file (.mp4 or .gif) with `animate_rotating_frames`.

Usage:
    python examples/05_rotating_animation.py
"""

import os

import geovista as gv
import numpy as np

from pyearthviz3d import (
    AnimationConfig,
    VisualizationConfig,
    animate_rotating_frames,
)
from pyearthviz3d.geovista.animate_rotating_frames import (
    create_animation_preview,
)


def create_synthetic_wave_mesh(n_lons: int = 49, n_lats: int = 25):
    """Create a spherical mesh with spherical harmonic wave pattern."""
    lons = np.linspace(-180, 180, n_lons)
    lats = np.linspace(-90, 90, n_lats)

    mesh = gv.Transform.from_1d(lons, lats)

    lon_grid, lat_grid = np.meshgrid(
        np.radians((lons[:-1] + lons[1:]) / 2.0),
        np.radians((lats[:-1] + lats[1:]) / 2.0),
    )
    # Wave number 3 Rossby-like pattern
    anomaly = np.cos(3.0 * lon_grid) * np.sin(2.0 * lat_grid)

    mesh.cell_data["vorticity"] = anomaly.ravel()
    valid_indices = np.arange(mesh.n_cells)
    return mesh, valid_indices


def main():
    print("Generating synthetic wave mesh...")
    mesh, valid_indices = create_synthetic_wave_mesh()

    examples_dir = os.path.dirname(__file__)
    preview_dir = os.path.join(examples_dir, "animation_previews")
    output_anim = os.path.join(examples_dir, "rotating_globe.gif")

    viz_config = VisualizationConfig(
        longitude_focus=0.0,
        latitude_focus=25.0,
        zoom_factor=0.8,
        show_coastlines=True,
        show_graticule=True,
        colormap="coolwarm",
        verbose=False,
    )

    anim_config = AnimationConfig(
        frames=12,  # Short duration for quick demonstration
        speed=30.0,  # 30 degrees per frame = 360 deg total
        framerate=6,
    )

    # 1. Preview key camera positions before rendering full movie
    print(f"Generating preview frames in {preview_dir}...")
    preview_result = create_animation_preview(
        mesh=mesh,
        valid_cell_indices=valid_indices,
        viz_config=viz_config,
        anim_config=anim_config,
        preview_frames=4,
        scalar_name="vorticity",
        unit="1/s",
        output_dir=preview_dir,
    )
    print(f"Generated {len(preview_result.get('generated_files', []))} preview frames.")

    # 2. Render full animation
    print(f"Rendering rotating animation to {output_anim}...")

    def on_progress(frame_idx, total_frames, pct):
        print(f"  Frame {frame_idx}/{total_frames} ({pct:.0f}%)", end="\r")

    anim_result = animate_rotating_frames(
        pMesh=mesh,
        aValid_cell_indices=valid_indices,
        pConfig=viz_config,
        pConfig_anima=anim_config,
        sScalar="vorticity",
        sUnit="1/s",
        sFilename_out=output_anim,
        progress_callback=on_progress,
        return_detailed_result=True,
    )

    print()
    if hasattr(anim_result, "get_summary"):
        print(anim_result.get_summary())

    if os.path.exists(output_anim):
        print(
            f"Successfully generated: {output_anim} ({os.path.getsize(output_anim) // 1024} KB)"
        )


if __name__ == "__main__":
    main()
