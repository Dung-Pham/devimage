"""PathService for generating developer path formats, code snippets, and base64 data URIs."""

from __future__ import annotations

import base64
import os
import platform
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import quote

from PIL import Image

from devimage.app.logging import get_logger

logger = get_logger("tools.copy_path.service")

MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".bmp": "image/bmp",
    ".ico": "image/x-icon",
    ".avif": "image/avif",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}


class PathService:
    """Service to format file paths, code snippets, and generate base64 data URIs."""

    @staticmethod
    def get_mime_type(suffix: str) -> str:
        """Return the appropriate MIME type for an image extension."""
        return MIME_MAP.get(suffix.lower(), "application/octet-stream")

    @staticmethod
    def format_windows_path(path: Path) -> str:
        """Return backslash Windows path."""
        return str(path)

    @staticmethod
    def format_posix_path(path: Path) -> str:
        """Return forward-slash POSIX-style path."""
        return path.as_posix()

    @staticmethod
    def format_file_uri(path: Path) -> str:
        """Return standards-compliant file:// URI."""
        posix = path.as_posix()
        if not posix.startswith("/"):
            posix = f"/{posix}"
        return f"file://{quote(posix, safe='/:')}"

    @staticmethod
    def format_relative_path(path: Path, base_dir: Path | None = None) -> str:
        """Return relative path to base directory, or simple ./filename fallback."""
        try:
            target_base = base_dir or Path.cwd()
            rel = os.path.relpath(path, target_base)
            posix_rel = rel.replace("\\", "/")
            if not posix_rel.startswith((".", "/")):
                return f"./{posix_rel}"
            return posix_rel
        except Exception:
            return f"./{path.name}"

    @staticmethod
    def generate_base64_data_uri(path: Path, max_bytes: int = 15 * 1024 * 1024) -> tuple[str, int]:
        """Generate base64 Data URI string. Returns (data_uri, byte_size)."""
        if not path.is_file():
            return "", 0

        size = path.stat().st_size
        if size > max_bytes:
            logger.warning(
                "File %s exceeds %d bytes; skipping base64 encoding", path.name, max_bytes
            )
            return f"[File size {size} exceeds 15MB limit for inline base64]", size

        data = path.read_bytes()
        mime = PathService.get_mime_type(path.suffix)
        encoded = base64.b64encode(data).decode("ascii")
        return f"data:{mime};base64,{encoded}", size

    def get_path_bundle(self, file_path: str, base_dir: str | None = None) -> dict[str, Any]:
        """Compute all path variations, code snippets, and metadata for a file."""
        p = Path(file_path)
        if not p.is_file():
            return {
                "has_file": False,
                "file_path": file_path,
                "filename": p.name or file_path,
                "snippets": [],
            }

        abs_win = self.format_windows_path(p)
        abs_posix = self.format_posix_path(p)
        file_uri = self.format_file_uri(p)
        rel_path = self.format_relative_path(p, Path(base_dir) if base_dir else None)
        filename = p.name
        stem = p.stem
        ext = p.suffix

        # Dimensions if image
        width, height = 0, 0
        try:
            with Image.open(p) as img:
                width, height = img.size
        except Exception:
            pass

        dim_attr = f' width="{width}" height="{height}"' if width > 0 else ""

        # Code snippets
        html_snippet = f'<img src="{rel_path}" alt="{stem}"{dim_attr} />'
        markdown_snippet = f"![{stem}]({rel_path})"
        css_snippet = f"background-image: url('{rel_path}');"
        react_snippet = f'import {stem.replace("-", "_").replace(" ", "_")} from "{rel_path}";'

        # Base64 data URI
        base64_uri, file_size = self.generate_base64_data_uri(p)

        snippets = [
            {
                "key": "windows",
                "title": "Windows Path",
                "description": "Standard Windows backslash path",
                "value": abs_win,
                "icon": "🪟",
            },
            {
                "key": "posix",
                "title": "POSIX Path",
                "description": "Web/Unix forward-slash path",
                "value": abs_posix,
                "icon": "🌐",
            },
            {
                "key": "uri",
                "title": "File URI",
                "description": "Standards-compliant file:// URL",
                "value": file_uri,
                "icon": "🔗",
            },
            {
                "key": "relative",
                "title": "Relative Path",
                "description": "Relative to workspace root",
                "value": rel_path,
                "icon": "📁",
            },
            {
                "key": "filename",
                "title": "Filename",
                "description": "Basename with extension",
                "value": filename,
                "icon": "📄",
            },
            {
                "key": "html",
                "title": "HTML <img> Tag",
                "description": "HTML image element with dimensions",
                "value": html_snippet,
                "icon": "🏷️",
            },
            {
                "key": "markdown",
                "title": "Markdown Image",
                "description": "Markdown image embed syntax",
                "value": markdown_snippet,
                "icon": "📝",
            },
            {
                "key": "css",
                "title": "CSS Background",
                "description": "CSS background-image rule",
                "value": css_snippet,
                "icon": "🎨",
            },
            {
                "key": "react",
                "title": "ES6 Import",
                "description": "JavaScript/TypeScript asset import",
                "value": react_snippet,
                "icon": "⚡",
            },
            {
                "key": "base64",
                "title": "Base64 Data URI",
                "description": f"Inline data URL ({file_size} bytes)",
                "value": base64_uri,
                "icon": "📦",
            },
        ]

        return {
            "has_file": True,
            "file_path": str(p),
            "filename": filename,
            "stem": stem,
            "ext": ext,
            "width": width,
            "height": height,
            "file_size": file_size,
            "windows_path": abs_win,
            "posix_path": abs_posix,
            "file_uri": file_uri,
            "relative_path": rel_path,
            "html_snippet": html_snippet,
            "markdown_snippet": markdown_snippet,
            "css_snippet": css_snippet,
            "react_snippet": react_snippet,
            "base64_uri": base64_uri,
            "snippets": snippets,
        }

    @staticmethod
    def reveal_in_file_manager(file_path: str) -> bool:
        """Open the operating system file manager and select the target file."""
        path = Path(file_path)
        if not path.exists():
            logger.warning("Cannot reveal non-existent path: %s", file_path)
            return False

        system = platform.system().lower()
        try:
            if "windows" in system:
                subprocess.Popen(["explorer", f"/select,{os.path.normpath(str(path))}"])
                return True
            if "darwin" in system:
                subprocess.Popen(["open", "-R", str(path)])
                return True
            # Linux fallback
            subprocess.Popen(["xdg-open", str(path.parent)])
            return True
        except Exception as e:
            logger.error("Failed to reveal file in file manager: %s", e)
            return False
