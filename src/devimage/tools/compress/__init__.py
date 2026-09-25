"""DevImage Compress Tool service and controller."""

from __future__ import annotations

from devimage.tools.compress.controller import CompressController
from devimage.tools.compress.service import CompressOptions, CompressResult, CompressService

__all__ = ["CompressController", "CompressOptions", "CompressResult", "CompressService"]
