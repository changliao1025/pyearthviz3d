Contributing to PyEarthViz3D
=============================

Contributions to ``pyearthviz3d`` are welcome! Whether reporting bugs, suggesting features, improving documentation, or submitting pull requests, your help is appreciated.

Development Setup
-----------------

1. Fork and clone the repository:

.. code-block:: bash

   git clone https://github.com/changliao1025/pyearthviz3d.git
   cd pyearthviz3d

2. Create the conda development environment:

.. code-block:: bash

   conda env create -f environment.yml
   conda activate pyearthviz3d

3. Install editable package with development and documentation dependencies:

.. code-block:: bash

   pip install -e .[dev,docs]

Code Style and Quality
----------------------

The project uses `black`, `flake8`, and `mypy` to maintain code standards:

.. code-block:: bash

   # Format code
   black pyearthviz3d test

   # Run linter
   flake8 pyearthviz3d test

   # Run type checker
   mypy pyearthviz3d

Running Tests
-------------

Execute test suites via `pytest`:

.. code-block:: bash

   pytest test/ -v

Building Documentation Locally
------------------------------

To build the HTML documentation locally:

.. code-block:: bash

   cd docs
   make html

The generated documentation will be available in ``docs/_build/html/index.html``.
