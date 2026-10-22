Animations & Video Export
=========================

``pyearthviz3d`` provides high-level pipelines for producing smooth, publication-quality 3D animations and rotating planetary movies.

Rotating Globe Animation
------------------------

The :func:`pyearthviz3d.animate_rotating_frames` function rotates the camera orbit around the 3D globe while keeping the data stationary.

.. code-block:: python

   import pyearthviz3d as pev

   # Configure rotation dynamics
   anim_config = pev.AnimationConfig(
       frames=120,           # Total frames in the animation
       speed=3.0,            # 3.0 degrees of longitude rotation per frame
       framerate=30,         # 30 frames per second (4-second duration)
       format="mp4",         # 'mp4', 'gif', or 'avi'
       amplitude_deg=15.0,   # Latitude oscillation amplitude for dynamic elevation
       cycles=1.0,           # Number of vertical undulation cycles
       longitude_start=0.0,  # Initial rotation longitude
       latitude_start=20.0,  # Initial rotation latitude
   )

   viz_config = pev.VisualizationConfig(
       zoom_factor=0.75,
       base_layer="natural_earth_hypsometric",
       colormap="plasma",
   )

   # Export movie
   result = pev.animate_rotating_frames(
       mesh,
       valid_indices,
       viz_config,
       anim_config,
       sScalar="relative_humidity",
       sUnit="%",
       sFilename_out="rotating_humidity.mp4",
       return_detailed_result=True,
   )

   print(result.get_summary())

Generating Animation Previews
-----------------------------

Rendering large 3D animations can be compute-intensive. To verify lighting, zoom, and colorbar settings before rendering all frames, use :func:`pyearthviz3d.geovista.animate_rotating_frames.create_animation_preview`:

.. code-block:: python

   from pyearthviz3d.geovista.animate_rotating_frames import create_animation_preview

   preview = create_animation_preview(
       mesh,
       valid_indices,
       viz_config,
       anim_config,
       preview_frames=4,         # Generate 4 keyframe snapshots
       scalar_name="relative_humidity",
       unit="%",
       output_dir="previews",
   )

   print(f"Preview frames generated: {preview['generated_files']}")

Time-Series Animation
---------------------

For multi-timestep datasets (e.g. hourly or monthly model outputs), :func:`pyearthviz3d.animate_time_series_frames` allows animating physical state transitions over time while updating the 3D spherical mesh or rotating camera angles.

Stand-Alone Polyline Animation
------------------------------

To create an animated focus or rotation around vector polyline trajectories without requiring a base numerical mesh, use :func:`pyearthviz3d.animate_polyline_file_on_sphere`:

.. code-block:: python

   pev.animate_polyline_file_on_sphere(
       sFilename_polyline_in="routes.shp",
       sFilename_animation_out="flight_routes.png",
       dLongitude_focus_in=-75.0,
       dLatitude_focus_in=40.0,
       sColor_polyline_in="crimson",
       dLinewidth_in=2.5,
   )
