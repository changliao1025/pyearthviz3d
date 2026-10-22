Headless Rendering & Cloud Environments
========================================

High Performance Computing (HPC) clusters, cloud VMs (AWS, GCP, Azure), Docker containers, and GitHub Actions CI runners typically lack an attached physical monitor (X11 display).

Understanding Headless Operation
--------------------------------

3D graphics engines like VTK depend on OpenGL context creation. On Linux without an active X server, attempting to render an OpenGL window directly results in segmentation faults or ``vtkXOpenGLRenderWindow`` connection errors.

``pyearthviz3d`` provides built-in utilities in ``_environment.py`` to handle headless environments gracefully:

* :func:`~pyearthviz3d.geovista._environment.detect_headless_environment`: Checks environment variables (``DISPLAY``, ``WAYLAND_DISPLAY``), operating system details, and session flags.
* :func:`~pyearthviz3d.geovista._environment.setup_xvfb_if_needed`: Automatically initializes a virtual X11 framebuffer via `Xvfb` (using `pyvista.start_xvfb()` or `xvfbwrapper`) if off-screen rendering is required.

Configuring Headless Mode Explicitly
------------------------------------

While ``pyearthviz3d`` auto-detects headless environments, you can also control Xvfb behavior explicitly via :class:`pyearthviz3d.VisualizationConfig`:

.. code-block:: python

   config = pyearthviz3d.VisualizationConfig(
       use_xvfb=True,    # Force Xvfb offscreen rendering
       force_xvfb=True,  # Force even if a display is present
   )

Jupyter Notebooks & JupyterLab
------------------------------

In Jupyter environments, ``pyearthviz3d`` leverages PyVista's WebGL and Trame backends for embedded interactive rendering.

Recommended Jupyter Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the following setup at the top of your notebook:

.. code-block:: python

   import pyvista as pv

   # Set Jupyter backend to embed self-contained interactive WebGL scenes
   pv.set_jupyter_backend("html")

With ``"html"`` set as the backend:
* The 3D scene is bundled directly inside the notebook cell.
* No websocket server or iframe port routing is needed.
* Interactive 3D mouse rotation, pan, and zoom work out of the box in JupyterLab, classic Notebooks, and Visual Studio Code webviews.

Docker Deployment
-----------------

When running ``pyearthviz3d`` inside a Docker container, include ``xvfb`` and Mesa in your ``Dockerfile``:

.. code-block:: dockerfile

   FROM condaforge/miniforge3:latest

   RUN apt-get update && apt-get install -y --no-install-recommends \
       xvfb \
       libgl1-mesa-glx \
       libglib2.0-0 \
       && rm -rf /var/lib/apt/lists/*

   COPY environment.yml .
   RUN conda env create -f environment.yml

   SHELL ["conda", "run", "-n", "pyearthviz3d", "/bin/bash", "-c"]
   ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "pyearthviz3d"]
