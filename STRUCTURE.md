# Project Structure

## Overview

`pyearthviz3d` is a lightweight Python package for 3D visualization of Earth science data.  The repository follows a conventional Python layout that is easy to navigate for developers and contributors.

## Directory Layout

```
.
├── pyearthviz3d/            # Main package source
│   ├── __init__.py          # Package imports
│   ├── map/                 # Mapping utilities
│   ├── plot/                # Plotting helpers
│   └── utils/               # Miscellaneous utilities
├── tests/                    # Test suite (pytest)
├── docs/                     # Documentation source (Sphinx / MkDocs)
├── examples/                # Example scripts and notebooks
├── .pre-commit-config.yaml   # Pre‑commit hook configuration
├── pyproject.toml            # Build system & tool configuration
├── setup.cfg                 # Optional legacy config (e.g., flake8)
└── README.md                 # Project overview (this file)
```

## Modules

- **`pyearthviz3d.map`** – Functions for raster and vector map creation.
- **`pyearthviz3d.plot`** – Higher‑level plotting wrappers (time‑series, statistical plots, animations).
- **`pyearthviz3d.utils`** – Helper utilities (color palettes, data loading, coordinate transforms).

## Development Workflow

1. **Fork** the repository and clone your fork.
2. **Create a virtual environment** (`conda env create -f environment.yml` or `python -m venv .venv`).
3. **Install the package in editable mode**:
   ```bash
   pip install -e .[dev]
   ```
4. **Run pre‑commit** to ensure code quality before committing:
   ```bash
   pre-commit run --all-files
   ```
5. **Write tests** under `tests/` and run them with `pytest`.
6. **Submit a Pull Request** targeting the `main` branch.

## Testing

- Unit tests are located in `tests/` and use `pytest`.
- Run the full test suite with:
  ```bash
  pytest -vv
  ```
- Coverage can be checked via `pytest-cov`:
  ```bash
  pytest --cov=pyearthviz3d
  ```

## Continuous Integration (CI)

The repository is set up with GitHub Actions that automatically:
- Install dependencies.
- Run the test suite.
- Enforce the configured pre‑commit hooks.

## Pre‑commit Configuration

The `.pre-commit-config.yaml` file (see next section) includes a curated set of hooks:
- Code formatting with **Black**.
- Import sorting with **isort**.
- Linting with **flake8** and **pyproject‑flask**.
- Type checking with **mypy**.
- Documentation style checks with **pydocstyle**.
- Detecting trailing whitespace, mixed line endings, and other common issues.

Developers should run `pre-commit install` once after cloning the repo to enable automatic checks on each `git commit`.
