Colorbars & Scalar Legends
===========================

The :class:`pyearthviz3d.ScalarBarConfig` class provides comprehensive configuration for scalar colorbars, supporting both continuous color gradients and discrete categorical classifications.

Continuous Colorbars
--------------------

For continuous variables (temperature, precipitation, wind speed, elevation):

.. code-block:: python

   from pyearthviz3d import ScalarBarConfig

   colorbar_cfg = ScalarBarConfig(
       title="Surface Air Temperature",
       title_font_size=12,
       label_font_size=10,
       n_labels=6,
       fmt="%.1f",
       orientation="horizontal",  # 'horizontal' or 'vertical'
       position_x=0.3,
       position_y=0.06,
       width=0.4,
       height=0.06,
       shadow=True,
   )

   # Pass to map_single_frame or animate_rotating_frames
   pev.map_single_frame(
       mesh,
       valid_indices,
       viz_config,
       sScalar="tas",
       sUnit="K",
       scalar_config=colorbar_cfg,
       sFilename_out="temperature_with_custom_bar.png",
   )

Discrete & Categorical Legends
------------------------------

For integer or classification data (such as Land Use / Land Cover, biome classes, or discrete risk levels), ``ScalarBarConfig`` supports explicit category swatches and label dictionaries:

.. code-block:: python

   # Define category names and hex colors
   discrete_labels = {
       1: "Water Bodies",
       2: "Evergreen Forest",
       3: "Deciduous Forest",
       4: "Grasslands",
       5: "Croplands",
       6: "Urban / Built-up",
   }

   value_colors = {
       1: "#1f77b4",
       2: "#2ca02c",
       3: "#98df8a",
       4: "#bcbd22",
       5: "#ff7f0e",
       6: "#d62728",
   }

   discrete_cfg = ScalarBarConfig(
       title="Land Cover Classification",
       orientation="vertical",
       discrete_labels=discrete_labels,
       value_colors=value_colors,
       position_x=0.82,
       position_y=0.2,
       width=0.08,
       height=0.6,
   )

   pev.map_single_frame(
       mesh,
       valid_indices,
       viz_config,
       sScalar="land_cover",
       scalar_config=discrete_cfg,
       sFilename_out="land_cover_globe.png",
   )

When discrete labels and colors are supplied, the mesh rendering engine automatically builds a lookup table (LUT) and formats discrete annotations without numeric interpolation artifacts.
