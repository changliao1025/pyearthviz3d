"""Plotter management and geographic context helpers."""

import logging
from typing import Any, Dict, Optional, Tuple

from ._config import VisualizationConfig
from ._environment import detect_headless_environment, setup_xvfb_if_needed

logger = logging.getLogger(__name__)


def setup_geovista_plotter(
    iFlag_off_screen: bool = False, iFlag_verbose_in: bool = False
):
    """
    Legacy wrapper for backward compatibility.

    Args:
        iFlag_off_screen: Whether to create off-screen plotter
        iFlag_verbose_in: Enable verbose logging

    Returns:
        GeoVista plotter instance or None if failed
    """
    logger.warning(
        "setup_geovista_plotter is deprecated, use PlotterManager.setup_geovista_plotter"
    )
    return PlotterManager.setup_geovista_plotter(
        off_screen=iFlag_off_screen,
        verbose=iFlag_verbose_in,
        use_xvfb=None,  # Auto-detect
        force_xvfb=False,
    )


def add_geographic_context(pPlotter, pConfig: VisualizationConfig):
    """
    Add geographic context (coastlines, graticule, axes) to plotter.

    Args:
        pPlotter: GeoVista plotter instance
        pConfig: Visualization configuration
    """
    # Add coastlines
    if pConfig.show_coastlines:
        try:
            # You can set coastline color using the 'color' parameter
            # Common options: 'black', 'white', 'red', 'blue', 'gray', etc.
            # You can also use RGB tuples like (1.0, 0.0, 0.0) for red
            pPlotter.add_coastlines(
                color=pConfig.coastline_color, line_width=pConfig.coastline_width
            )
            if pConfig.verbose:
                logger.debug(
                    f"Added coastlines overlay (color: {pConfig.coastline_color}, width: {pConfig.coastline_width})"
                )
        except Exception as e:
            logger.warning(f"Could not add coastlines: {e}")

    # Add coordinate axes with smaller viewport to avoid large labels
    try:
        # Use viewport parameter to make axes smaller and less intrusive
        # Viewport format: (x_min, y_min, x_max, y_max) in normalized coordinates (0-1)
        pPlotter.add_axes(viewport=(0.0, 0.0, 0.15, 0.15))
        if pConfig.verbose:
            logger.debug("Added coordinate axes with reduced size")
    except Exception as e:
        logger.warning(f"Could not add axes: {e}")

    # Add graticule (coordinate grid)
    if pConfig.show_graticule:
        try:
            pPlotter.add_graticule(show_labels=True)
            if pConfig.verbose:
                logger.debug("Added coordinate graticule with labels")
        except Exception as e:
            logger.warning(f"Could not add graticule: {e}")


class PlotterManager:
    """Enhanced plotter management with error recovery."""

    @staticmethod
    def setup_geovista_plotter(
        off_screen: bool = False,
        verbose: bool = False,
        window_size: Tuple[int, int] = (800, 600),
        theme: str = "default",
        use_xvfb: Optional[bool] = None,
        force_xvfb: bool = False,
    ) -> Optional[Any]:
        """
        Set up GeoVista plotter with comprehensive error handling and recovery.

        Args:
            off_screen: Whether to create off-screen plotter
            verbose: Enable verbose logging
            window_size: Window size for interactive mode (width, height)
            theme: Plotter theme ('default', 'dark', 'paraview')
            use_xvfb: None=auto-detect, True=force use xvfb, False=don't use xvfb
            force_xvfb: Force xvfb even if not detected as needed

        Returns:
            GeoVista plotter instance or None if failed
        """
        # Handle xvfb setup for headless environments
        if use_xvfb is None:
            # Auto-detect if xvfb is needed
            should_use_xvfb = detect_headless_environment() or force_xvfb
        else:
            should_use_xvfb = use_xvfb

        if should_use_xvfb:
            if verbose:
                logger.info("Setting up Xvfb for headless environment...")
            xvfb_success = setup_xvfb_if_needed(force_xvfb=force_xvfb, verbose=verbose)
            if not xvfb_success:
                logger.warning(
                    "Failed to setup xvfb, attempting to continue without it"
                )

        try:
            import geovista as gv

            if verbose:
                logger.info("GeoVista library imported successfully")
        except ImportError as e:
            logger.error(
                "GeoVista library not available. Install with: pip install geovista"
            )
            logger.error(f"Import error: {e}")
            return None

        # Try multiple plotter creation strategies
        creation_strategies = [
            (
                "standard",
                lambda: PlotterManager._create_standard_plotter(
                    gv, off_screen, window_size, theme
                ),
            ),
            (
                "fallback",
                lambda: PlotterManager._create_fallback_plotter(gv, off_screen),
            ),
            ("minimal", lambda: PlotterManager._create_minimal_plotter(gv, off_screen)),
        ]

        for strategy_name, create_func in creation_strategies:
            try:
                plotter = create_func()
                if verbose:
                    logger.info(
                        f"Successfully created plotter using {strategy_name} strategy"
                    )
                return plotter
            except Exception as e:
                if verbose:
                    logger.warning(
                        f"Failed to create plotter with {strategy_name} strategy: {e}"
                    )
                continue

        logger.error("All plotter creation strategies failed")
        return None

    @staticmethod
    def _create_standard_plotter(
        gv, off_screen: bool, window_size: Tuple[int, int], theme: str
    ):
        """Create plotter with standard configuration."""
        kwargs: Dict[str, Any] = {"off_screen": off_screen}
        kwargs["window_size"] = window_size
        if theme != "default":
            kwargs["theme"] = theme
        return gv.GeoPlotter(**kwargs)

    @staticmethod
    def _create_fallback_plotter(gv, off_screen: bool):
        """Create plotter with minimal configuration."""
        return gv.GeoPlotter(off_screen=off_screen)

    @staticmethod
    def _create_minimal_plotter(gv, off_screen: bool):
        """Create the most basic plotter possible."""
        if off_screen:
            return gv.GeoPlotter(off_screen=True)
        else:
            return gv.GeoPlotter()


def add_geographic_context_enhanced(
    plotter, config: VisualizationConfig, retry_on_failure: bool = True
) -> Dict[str, bool]:
    """
    Add geographic context with comprehensive error handling and recovery.

    Args:
        plotter: GeoVista plotter instance
        config: Visualization configuration
        retry_on_failure: Whether to retry failed operations with alternative methods

    Returns:
        Dict indicating success/failure of each context element
    """
    results = {"coastlines": False, "axes": False, "graticule": False}

    # Add coastlines with fallback options
    if config.show_coastlines:
        coastline_strategies = [
            (
                "standard",
                lambda: plotter.add_coastlines(
                    color=config.coastline_color, line_width=config.coastline_width
                ),
            ),
            ("simple", lambda: plotter.add_coastlines()),
            ("basic", lambda: plotter.add_coastlines(color="black")),
        ]

        for strategy_name, add_func in coastline_strategies:
            try:
                add_func()
                results["coastlines"] = True
                if config.verbose:
                    logger.debug(f"Added coastlines using {strategy_name} method")
                break
            except Exception as e:
                if config.verbose:
                    logger.warning(f"Coastlines {strategy_name} method failed: {e}")
                if not retry_on_failure:
                    break
                continue

    # Add coordinate axes with fallback (use smaller viewport to avoid large labels)
    axes_strategies = [
        ("standard", lambda: plotter.add_axes(viewport=(0.0, 0.0, 0.15, 0.15))),
        (
            "simple",
            lambda: (
                plotter.add_axes(interactive=False, viewport=(0.0, 0.0, 0.15, 0.15))
                if hasattr(plotter, "add_axes")
                else None
            ),
        ),
    ]

    for strategy_name, add_func in axes_strategies:
        try:
            result = add_func()
            if result is not None or not hasattr(plotter, "add_axes"):
                results["axes"] = True
                if config.verbose:
                    logger.debug(f"Added axes using {strategy_name} method")
                break
        except Exception as e:
            if config.verbose:
                logger.warning(f"Axes {strategy_name} method failed: {e}")
            if not retry_on_failure:
                break
            continue

    # Add graticule with fallback options
    if config.show_graticule:
        graticule_strategies = [
            ("labeled", lambda: plotter.add_graticule(show_labels=True)),
            ("unlabeled", lambda: plotter.add_graticule(show_labels=False)),
            ("basic", lambda: plotter.add_graticule()),
        ]

        for strategy_name, add_func in graticule_strategies:
            try:
                add_func()
                results["graticule"] = True
                if config.verbose:
                    logger.debug(f"Added graticule using {strategy_name} method")
                break
            except Exception as e:
                if config.verbose:
                    logger.warning(f"Graticule {strategy_name} method failed: {e}")
                if not retry_on_failure:
                    break
                continue

    return results
