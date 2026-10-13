"""Output validation and runtime environment helpers."""

import logging
import os
import sys
from typing import Any, Dict, List, Tuple

from ._config import VALID_ANIMATION_FORMATS, VALID_IMAGE_FORMATS

logger = logging.getLogger(__name__)


def is_running_in_notebook() -> bool:
    """
    Detect if the code is running in a Jupyter/IPython notebook environment.

    Returns:
        bool: True if running in a notebook, False otherwise

    Note:
        This function checks for the presence of IPython/Jupyter kernel modules
        and verifies that we're actually in a notebook context (not just IPython shell).
    """
    try:
        # Check for IPython/Jupyter kernel modules
        in_notebook = "ipykernel" in sys.modules or "IPython" in sys.modules
        if in_notebook:
            # Additional check: verify we're actually in a notebook, not just IPython
            try:
                from IPython import get_ipython

                ipython = get_ipython()
                in_notebook = ipython is not None and "IPKernelApp" in str(type(ipython))
            except (ImportError, AttributeError):
                in_notebook = False
        return in_notebook
    except Exception:
        return False


def validate_output_filename(filename: str, expected_formats: List[str] = None) -> Tuple[bool, str]:
    """
    Validate output filename and format.

    Args:
        filename: Output filename to validate
        expected_formats: List of expected file extensions

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename or not isinstance(filename, str):
        return False, "Filename must be a non-empty string"

    if expected_formats is None:
        expected_formats = VALID_IMAGE_FORMATS + VALID_ANIMATION_FORMATS

    # Check file extension
    file_ext = os.path.splitext(filename.lower())[1].lstrip(".")
    if expected_formats and file_ext not in expected_formats:
        return False, f"Invalid file format '{file_ext}'. Expected: {expected_formats}"

    # Check directory exists or can be created
    directory = os.path.dirname(filename)
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            return False, f"Cannot create output directory: {e}"

    return True, ""


def detect_headless_environment() -> bool:
    """
    Detect if we're running in a headless Linux environment without graphics.

    Returns:
        bool: True if headless environment detected (needs xvfb), False otherwise
    """
    # Check if we're on Linux
    if sys.platform != "linux":
        return False

    # Check if DISPLAY environment variable is set
    display = os.environ.get("DISPLAY")
    if display:
        # DISPLAY is set, but check if it's accessible
        try:
            # Try to connect to the display
            import subprocess

            result = subprocess.run(["xdpyinfo"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return False  # Display is accessible
        except (subprocess.TimeoutExpired, FileNotFoundError, ImportError):
            pass

    # Check for common headless environment indicators
    headless_indicators = [
        not display,  # No DISPLAY variable
        os.environ.get("SSH_CLIENT") is not None,  # SSH connection
        os.environ.get("SSH_TTY") is not None,  # SSH TTY
        os.environ.get("CI") == "true",  # CI environment
        os.environ.get("DEBIAN_FRONTEND") == "noninteractive",  # Non-interactive mode
    ]

    return any(headless_indicators)


def setup_xvfb_if_needed(force_xvfb: bool = False, verbose: bool = False) -> bool:
    """
    Set up Xvfb (X Virtual Framebuffer) if running in headless Linux environment.

    Args:
        force_xvfb: Force xvfb setup even if not detected as headless
        verbose: Enable verbose logging

    Returns:
        bool: True if xvfb was set up or already available, False if setup failed
    """
    try:
        import pyvista as pv
    except ImportError:
        if verbose:
            logger.warning("PyVista not available, cannot setup xvfb")
        return False

    # Check if we need xvfb
    needs_xvfb = force_xvfb or detect_headless_environment()

    if not needs_xvfb:
        if verbose:
            logger.debug("Display available, xvfb not needed")
        return True

    # Check if xvfb is already running (DISPLAY set by xvfb)
    if os.environ.get("DISPLAY") and not force_xvfb:
        if verbose:
            logger.debug("DISPLAY already set, assuming xvfb is running")
        return True

    try:
        if verbose:
            logger.info("🖥️ Setting up Xvfb for headless environment...")

        # Start xvfb using PyVista
        pv.start_xvfb()

        if verbose:
            logger.info("✅ Xvfb started successfully")

        # check if it is in a notebook
        if is_running_in_notebook():
            if verbose:
                logger.info("Running in a notebook, ensuring DISPLAY is set for notebook")
            # might need to set up the backend for notebook
            try:
                pv.set_jupyter_backend("trame")  # this is for mybinder
            except Exception as e:
                if verbose:
                    logger.warning(f"Could not set jupyter backend: {e}")

        return True

    except Exception as e:
        if verbose:
            logger.error(f"❌ Failed to start xvfb: {e}")
        logger.warning(f"Could not start xvfb: {e}")
        return False


def get_system_info() -> Dict[str, Any]:
    """Get system information for troubleshooting visualization issues."""
    info = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "os_name": os.name,
        "cwd": os.getcwd(),
        "display_available": os.environ.get("DISPLAY") is not None,
        "headless_detected": detect_headless_environment(),
        "geovista_available": False,
        "pyvista_available": False,
        "vtk_available": False,
    }

    try:
        import geovista

        info["geovista_available"] = True
        info["geovista_version"] = getattr(geovista, "__version__", "unknown")
    except ImportError:
        pass

    try:
        import pyvista

        info["pyvista_available"] = True
        info["pyvista_version"] = getattr(pyvista, "__version__", "unknown")
    except ImportError:
        pass

    try:
        import vtk

        info["vtk_available"] = True
        info["vtk_version"] = getattr(vtk, "vtkVersion", lambda: vtk.VTK_VERSION)().GetVTKVersion()
    except ImportError:
        pass

    return info
