"""Thread pool manager for background worker execution."""

from __future__ import annotations

import os

from PySide6.QtCore import QRunnable, QThreadPool

from devimage.app.logging import get_logger

logger = get_logger("workers.pool")

_pool_instance: QThreadPool | None = None


def get_thread_pool() -> QThreadPool:
    """Get or initialize the shared background QThreadPool."""
    global _pool_instance
    if _pool_instance is None:
        _pool_instance = QThreadPool.globalInstance()
        # Default thread count based on CPU cores (min 2, max 8 for desktop responsiveness)
        cpu_count = os.cpu_count() or 4
        optimal_threads = max(2, min(8, cpu_count))
        _pool_instance.setMaxThreadCount(optimal_threads)
        logger.info(
            "Initialized QThreadPool with max %d thread workers",
            _pool_instance.maxThreadCount(),
        )
    return _pool_instance


def submit_worker(worker: QRunnable) -> None:
    """Submit a QRunnable task to the thread pool for async execution."""
    pool = get_thread_pool()
    pool.start(worker)
