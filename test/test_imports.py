#!/usr/bin/env python
"""
Test script to verify all imports work correctly in pyearthviz3d.
This tests the import structure to ensure no circular dependencies or missing exports.
"""

import sys
import traceback

def test_import(import_statement, description):
    """Test a single import and report results."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Import: {import_statement}")
    print(f"{'='*60}")
    try:
        exec(import_statement)
        print("✓ SUCCESS")
        return True
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all import tests."""
    print("pyearthviz3d Import Test Suite")
    print("="*60)

    results = []

    # Test 1: Import the main package
    results.append(test_import(
        "import pyearthviz3d",
        "Main package import"
    ))

    # Test 2: Import geovista submodule
    results.append(test_import(
        "import pyearthviz3d.geovista",
        "GeoVista submodule import"
    ))

    # Test 3: Import individual functions from geovista submodule
    results.append(test_import(
        "from pyearthviz3d.geovista import map_single_frame",
        "map_single_frame function"
    ))

    results.append(test_import(
        "from pyearthviz3d.geovista import animate_polyline_file_on_sphere",
        "animate_polyline_file_on_sphere function"
    ))

    results.append(test_import(
        "from pyearthviz3d.geovista import animate_rotating_frames",
        "animate_rotating_frames function"
    ))

    results.append(test_import(
        "from pyearthviz3d.geovista import animate_time_series_frames",
        "animate_time_series_frames function"
    ))

    # Test 4: Import from top-level package (convenience imports)
    results.append(test_import(
        "from pyearthviz3d import map_single_frame",
        "map_single_frame from top-level"
    ))

    results.append(test_import(
        "from pyearthviz3d import animate_polyline_file_on_sphere",
        "animate_polyline_file_on_sphere from top-level"
    ))

    results.append(test_import(
        "from pyearthviz3d import animate_rotating_frames",
        "animate_rotating_frames from top-level"
    ))

    results.append(test_import(
        "from pyearthviz3d import animate_time_series_frames",
        "animate_time_series_frames from top-level"
    ))

    # Test 5: Import directly from module file
    results.append(test_import(
        "from pyearthviz3d.geovista.animate_time_series_frames import animate_time_series_frames",
        "animate_time_series_frames directly from module file"
    ))

    results.append(test_import(
        "from pyearthviz3d.geovista.map_single_frame import map_single_frame",
        "map_single_frame directly from module file"
    ))

    results.append(test_import(
        "from pyearthviz3d.geovista.animate_rotating_frames import animate_rotating_frames",
        "animate_rotating_frames directly from module file"
    ))

    results.append(test_import(
        "from pyearthviz3d.geovista.animate_polyline_file_on_sphere import animate_polyline_file_on_sphere",
        "animate_polyline_file_on_sphere directly from module file"
    ))

    # Test 6: Check __all__ exports
    results.append(test_import(
        "from pyearthviz3d import __all__; assert 'animate_time_series_frames' in __all__",
        "Verify animate_time_series_frames in __all__"
    ))

    results.append(test_import(
        "from pyearthviz3d.geovista import __all__; assert 'animate_time_series_frames' in __all__",
        "Verify animate_time_series_frames in geovista.__all__"
    ))

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("\n✓ All imports successful! No import issues detected.")
        return 0
    else:
        print(f"\n✗ {total - passed} import(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
