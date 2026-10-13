# Code Architecture Analysis

This document records a static analysis of the `pyearthviz3d` codebase as a working list for future improvements. Findings are ordered by architectural concern, not as a commitment to make every change. Address them one at a time, validating behavior as changes are made.

## Architecture overview

The package is centered on `pyearthviz3d.geovista`. The broad dependency flow is:

```text
package facades (pyearthviz3d, geovista)
    -> visualization modules (map_single_frame, animate_*)
        -> focused internal modules (_config, _camera, _mesh, _plotter, _environment, _vector)
           [and utility.py as a backward-compatibility facade]
            -> GeoVista / PyVista and related dependencies (plus GDAL/OGR via _vector)
```

Vector-file visualization paths additionally depend on GDAL/OGR. No direct internal circular import was identified in the static review.

## Findings

### 1. The shared utility module has broad responsibilities

**Status: Implemented.** The implementation has been split into focused internal modules: [`_config.py`](../pyearthviz3d/geovista/_config.py), [`_camera.py`](../pyearthviz3d/geovista/_camera.py), [`_mesh.py`](../pyearthviz3d/geovista/_mesh.py), [`_plotter.py`](../pyearthviz3d/geovista/_plotter.py), and [`_environment.py`](../pyearthviz3d/geovista/_environment.py). [`utility.py`](../pyearthviz3d/geovista/utility.py) remains as a small compatibility facade that re-exports the existing names and preserves historic imports.

The split retains the existing implementations and APIs while narrowing each module's responsibilities. Future changes should generally target the focused module rather than adding implementation back to `utility.py`.

### 2. Vector ingestion and rendering are coupled

**Status: Implemented.** Vector I/O, OGR coordinate transformation to WGS84, attribute scaling, and PyVista spherical PolyData construction have been extracted into [`_vector.py`](../pyearthviz3d/geovista/_vector.py).

Both [`animate_polyline_file_on_sphere.py`](../pyearthviz3d/geovista/animate_polyline_file_on_sphere.py) and [`animate_mesh_with_vector_files.py`](../pyearthviz3d/geovista/animate_mesh_with_vector_files.py) now delegate vector parsing and geometry-to-mesh conversion to these helpers, separating data loading/conversion from visualization orchestration.

### 3. The public API differs between package levels

[`pyearthviz3d/__init__.py`](../pyearthviz3d/__init__.py) and [`geovista/__init__.py`](../pyearthviz3d/geovista/__init__.py) expose different sets of names. In addition, [`animate_rotating_frames.py`](../pyearthviz3d/geovista/animate_rotating_frames.py) defines an `AnimationResult` distinct from the result type exported by the `geovista` facade.

**Suggested direction:** decide which APIs are public at each package level, document that decision, and clarify or consolidate result types without breaking existing callers unintentionally.

### 4. Test discovery and test structure may be misaligned

[`pyproject.toml`](../pyproject.toml) configures pytest to discover tests under `tests/`, while the repository contains [`test/test_imports.py`](../test/test_imports.py). The import-check file appears to be a standalone script rather than a conventional set of pytest tests.

**Suggested direction:** align pytest's configured test path with the repository layout, then add focused behavioral tests for shared helpers and visualization orchestration.

### 5. Dependency requirements differ across project metadata

The minimum `pyearth` version appears to differ between [`pyproject.toml`](../pyproject.toml), [`environment.yml`](../environment.yml), and [`README.md`](../README.md).

**Suggested direction:** choose an authoritative dependency declaration where practical, or keep duplicated declarations synchronized and add a lightweight review check.

## Suggested improvement order

1. Align test discovery and add a small set of baseline tests before restructuring shared code.
2. Separate vector ingestion/conversion from rendering.
3. Split `utility.py` into focused modules while preserving compatibility.
4. Clarify package exports and result types.
5. Reconcile dependency version declarations.

## Scope and caveats

This is a static architecture review, not a test run. The recommendations should be checked against actual callers and supported compatibility expectations before implementation.
