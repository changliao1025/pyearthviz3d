Installation
============

Because ``pyearthviz3d`` relies on geospatial and 3D graphics libraries (such as GDAL, VTK, and GeoVista), installing via **conda / mamba** is strongly recommended.

Recommended: Conda / Mamba Installation
---------------------------------------

To install ``pyearthviz3d`` and its compiled dependencies from conda-forge:

.. code-block:: bash

   conda install -c conda-forge pyearthviz3d

Or using ``mamba``:

.. code-block:: bash

   mamba install -c conda-forge pyearthviz3d

Installing from Source
----------------------

If you are developing ``pyearthviz3d`` or working from the latest repository source code:

1. Clone the repository:

.. code-block:: bash

   git clone https://github.com/changliao1025/pyearthviz3d.git
   cd pyearthviz3d

2. Create an environment using the provided ``environment.yml``:

.. code-block:: bash

   conda env create -f environment.yml
   conda activate pyearthviz3d

3. Install ``pyearthviz3d`` in editable development mode:

.. code-block:: bash

   pip install -e .

Installing via Pip
------------------

If you already have system GDAL and VTK packages installed:

.. code-block:: bash

   pip install pyearthviz3d

Optional Dependencies
---------------------

* **Development tools** (testing, linting, type-checking):

  .. code-block:: bash

     pip install pyearthviz3d[dev]

* **Jupyter interactive widgets** (Trame, ipywidgets):

  .. code-block:: bash

     pip install pyearthviz3d[jupyter]

* **Documentation tools** (Sphinx, ReadTheDocs theme, MyST parser):

  .. code-block:: bash

     pip install pyearthviz3d[docs]

Headless Linux Environments
---------------------------

When running on Linux compute nodes, continuous integration (CI) runners, or cloud containers without an attached X11 display, VTK and PyVista require a virtual framebuffer such as **Xvfb**.

Install Xvfb on Debian/Ubuntu:

.. code-block:: bash

   sudo apt-get update && sudo apt-get install -y xvfb libgl1-mesa-glx

``pyearthviz3d`` includes built-in headless detection via ``detect_headless_environment()`` and will automatically configure an off-screen renderer or virtual framebuffer when required.
