"""Logging subsystem for DevImage.

Implements structured logging to console, general application log (app.log),
and error-only log (errors.log) with automatic log rotation.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from devimage.app.paths import get_logs_dir

_ROOT_LOGGER_NAME = "devimage"
_DEFAULT_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_BACKUP_COUNT = 3


def setup_logging(
    level: int = logging.INFO,
    log_dir: Path | None = None,
    console: bool = True,
) -> logging.Logger:
    """Configure and initialize root DevImage logger handlers."""
    if log_dir is None:
        log_dir = get_logs_dir()
    else:
        log_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger(_ROOT_LOGGER_NAME)
    root_logger.setLevel(level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    formatter = logging.Formatter(_DEFAULT_FORMAT, datefmt=_DATE_FORMAT)

    # 1. Console stream handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 2. General app.log handler (logs all events at current level)
    app_log_file = log_dir / "app.log"
    app_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    app_handler.setLevel(level)
    app_handler.setFormatter(formatter)
    root_logger.addHandler(app_handler)

    # 3. errors.log handler (ERROR and CRITICAL only)
    error_log_file = log_dir / "errors.log"
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    root_logger.info("Logging initialized. Output dir: %s", log_dir)
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger child of the root devimage logger."""
    if name.startswith(f"{_ROOT_LOGGER_NAME}."):
        return logging.getLogger(name)
    return logging.getLogger(f"{_ROOT_LOGGER_NAME}.{name}")
