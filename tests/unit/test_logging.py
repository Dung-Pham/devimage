"""Unit tests for logging subsystem."""

import logging
from pathlib import Path

from devimage.app.logging import get_logger, setup_logging


def test_setup_logging(tmp_path: Path):
    """Verify setup_logging creates app.log and errors.log and dispatches messages."""
    log_dir = tmp_path / "logs"
    logger = setup_logging(level=logging.DEBUG, log_dir=log_dir, console=False)

    test_child = get_logger("test_module")
    test_child.info("Test informative message")
    test_child.error("Test error message")

    app_log = log_dir / "app.log"
    error_log = log_dir / "errors.log"

    assert app_log.exists()
    assert error_log.exists()

    app_content = app_log.read_text(encoding="utf-8")
    error_content = error_log.read_text(encoding="utf-8")

    assert "Test informative message" in app_content
    assert "Test error message" in app_content
    # info shouldn't appear in errors.log
    assert "Test informative message" not in error_content
    assert "Test error message" in error_content

    # Clean up handlers so other tests don't write here
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
