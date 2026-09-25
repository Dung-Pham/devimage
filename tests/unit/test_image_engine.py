"""Unit tests for DevImage core image processing engine and worker pool."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from devimage.core.errors import (
    FileNotFoundAppError,
    InvalidParameterError,
    UnsupportedFormatError,
)
from devimage.engine.image.metadata import extract_metadata
from devimage.engine.image.processor import (
    calculate_aspect_dimensions,
    calculate_contain_dimensions,
    calculate_cover_dimensions,
    crop_image,
    open_image,
    resize_image,
    rotate_image,
    save_image,
)
from devimage.workers.image_worker import ImageWorker
from devimage.workers.pool import get_thread_pool, submit_worker


@pytest.fixture
def sample_rgba_image(tmp_path: Path) -> Path:
    """Create a temporary 200x100 RGBA image."""
    img_path = tmp_path / "test_sample.png"
    img = Image.new("RGBA", (200, 100), (255, 0, 0, 128))
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_rgb_image(tmp_path: Path) -> Path:
    """Create a temporary 300x150 RGB image."""
    img_path = tmp_path / "test_sample.jpg"
    img = Image.new("RGB", (300, 150), (0, 128, 255))
    img.save(img_path, "JPEG", dpi=(150, 150))
    return img_path


# =============================================================================
# 1. Metadata Extraction Tests
# =============================================================================


def test_extract_metadata_rgba(sample_rgba_image: Path) -> None:
    meta = extract_metadata(sample_rgba_image)
    assert meta.width == 200
    assert meta.height == 100
    assert meta.format == "PNG"
    assert meta.mode == "RGBA"
    assert meta.has_transparency is True
    assert meta.aspect_ratio == 2.0
    assert meta.file_size_bytes > 0


def test_extract_metadata_rgb_with_dpi(sample_rgb_image: Path) -> None:
    meta = extract_metadata(sample_rgb_image)
    assert meta.width == 300
    assert meta.height == 150
    assert meta.format == "JPEG"
    assert meta.mode == "RGB"
    assert meta.has_transparency is False
    assert meta.dpi is not None
    assert meta.dpi[0] == 150.0


def test_extract_metadata_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundAppError):
        extract_metadata(tmp_path / "non_existent.png")


def test_extract_metadata_invalid_file(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.png"
    bad_file.write_text("not an image")
    with pytest.raises(UnsupportedFormatError):
        extract_metadata(bad_file)


# =============================================================================
# 2. Dimension & Calculation Tests
# =============================================================================


def test_calculate_aspect_dimensions_both_provided() -> None:
    # 200x100 (2:1 aspect ratio), target bounding box 100x100
    w, h = calculate_aspect_dimensions(200, 100, target_w=100, target_h=100, keep_aspect=True)
    assert w == 100
    assert h == 50


def test_calculate_aspect_dimensions_width_only() -> None:
    w, h = calculate_aspect_dimensions(200, 100, target_w=400, keep_aspect=True)
    assert w == 400
    assert h == 200


def test_calculate_aspect_dimensions_height_only() -> None:
    w, h = calculate_aspect_dimensions(200, 100, target_h=50, keep_aspect=True)
    assert w == 100
    assert h == 50


def test_calculate_aspect_dimensions_dont_enlarge() -> None:
    # Target 400x200 requested, but dont_enlarge is True -> should remain 200x100
    w, h = calculate_aspect_dimensions(
        200, 100, target_w=400, target_h=200, keep_aspect=True, dont_enlarge=True
    )
    assert w == 200
    assert h == 100


def test_calculate_contain_dimensions() -> None:
    w, h = calculate_contain_dimensions(1000, 500, 400, 400)
    assert w == 400
    assert h == 200


def test_calculate_cover_dimensions() -> None:
    w, h = calculate_cover_dimensions(1000, 500, 400, 400)
    assert w == 800
    assert h == 400


# =============================================================================
# 3. Processing Primitives Tests (Open, Save, Resize, Crop, Rotate)
# =============================================================================


def test_open_and_save_image(sample_rgba_image: Path, tmp_path: Path) -> None:
    img = open_image(sample_rgba_image)
    assert img.size == (200, 100)

    out_webp = tmp_path / "out.webp"
    saved_path = save_image(img, out_webp, quality=80)
    assert Path(saved_path).is_file()
    assert os.path.getsize(saved_path) > 0


def test_save_rgba_to_jpeg_flattens_alpha(sample_rgba_image: Path, tmp_path: Path) -> None:
    img = open_image(sample_rgba_image)
    out_jpeg = tmp_path / "out.jpg"
    saved_path = save_image(img, out_jpeg)

    saved_img = Image.open(saved_path)
    assert saved_img.mode == "RGB"


def test_resize_modes(sample_rgb_image: Path) -> None:
    img = open_image(sample_rgb_image)

    # Stretch
    stretched = resize_image(img, 100, 100, mode="stretch")
    assert stretched.size == (100, 100)

    # Contain (300x150 inside 100x100 -> 100x50)
    contained = resize_image(img, 100, 100, mode="contain")
    assert contained.size == (100, 50)

    # Cover (300x150 covering 100x100 -> exact 100x100 cropped)
    covered = resize_image(img, 100, 100, mode="cover")
    assert covered.size == (100, 100)


def test_crop_image(sample_rgb_image: Path) -> None:
    img = open_image(sample_rgb_image)  # 300x150
    cropped = crop_image(img, (50, 20, 150, 80))
    assert cropped.size == (100, 60)


def test_crop_image_invalid_coordinates(sample_rgb_image: Path) -> None:
    img = open_image(sample_rgb_image)
    with pytest.raises(InvalidParameterError):
        crop_image(img, (100, 100, 50, 50))


def test_rotate_image(sample_rgb_image: Path) -> None:
    img = open_image(sample_rgb_image)  # 300x150
    rot90 = rotate_image(img, 90)
    assert rot90.size == (150, 300)

    rot180 = rotate_image(img, 180)
    assert rot180.size == (300, 150)


# =============================================================================
# 4. Asynchronous ImageWorker Tests
# =============================================================================


def test_worker_pool_initialization() -> None:
    pool = get_thread_pool()
    assert pool.maxThreadCount() >= 2


def test_image_worker_execution(qtbot: Any) -> None:
    def sample_task(val: int, progress_callback: Any = None) -> int:
        if progress_callback:
            progress_callback(50.0, "Halfway done")
        return val * 2

    worker = ImageWorker(sample_task, 21, task_id="test-task-1")

    with qtbot.waitSignals(
        [worker.signals.started, worker.signals.progress, worker.signals.finished], timeout=5000
    ):
        submit_worker(worker)


def test_image_worker_cancellation(qtbot: Any) -> None:
    def long_task(cancel_check: Any = None) -> str:
        if cancel_check and cancel_check():
            return "cancelled"
        return "finished"

    worker = ImageWorker(long_task, task_id="test-cancel-task")
    worker.cancel()

    with qtbot.waitSignal(worker.signals.cancelled, timeout=3000):
        submit_worker(worker)
