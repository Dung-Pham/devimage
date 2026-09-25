"""Main executable entrypoint for DevImage."""

from __future__ import annotations

import argparse
import logging
import sys

import devimage
from devimage.app.application import DevImageApp
from devimage.app.logging import get_logger, setup_logging


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line flags."""
    parser = argparse.ArgumentParser(
        prog="devimage",
        description="DevImage: Desktop image toolbox tailored for developers and technical creators",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"DevImage {devimage.__version__}",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug logging to console and app.log",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Initialize application runtime and launch UI."""
    args = parse_args(argv)

    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(level=log_level)
    logger = get_logger("main")
    logger.info("Starting DevImage v%s (Python %s)", devimage.__version__, sys.version.split()[0])

    try:
        app = DevImageApp(sys.argv)
        if not app.load_qml():
            logger.critical("Fatal: QML engine failed to instantiate root interface.")
            return 1
        return app.exec()
    except Exception as e:
        logger.critical("Unhandled exception during application execution: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
