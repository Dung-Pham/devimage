"""Batch file rename service for template-based file renaming with conflict detection and rollback."""

from __future__ import annotations

import os
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image

from devimage.app.logging import get_logger

logger = get_logger("tools.rename.service")

# Characters disallowed in Windows filenames
INVALID_FILENAME_CHARS = set('<>:"/\\|?*')


@dataclass
class RenameItem:
    """Represents a single file in the batch rename operation."""

    source_path: str
    source_name: str
    target_name: str
    target_path: str
    status: str  # "ok", "collision", "exists", "invalid", "unchanged"
    message: str
    original_size: int = 0
    width: int = 0
    height: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert item to dictionary for QML and serialization."""
        return asdict(self)


class RenameService:
    """Pure-Python batch renaming engine supporting patterns, case transforms, and conflict checks."""

    def __init__(self) -> None:
        self._dim_cache: dict[str, tuple[int, int]] = {}

    def get_image_dimensions(self, file_path: str) -> tuple[int, int]:
        """Read image width and height with caching, returning (0, 0) on failure."""
        if file_path in self._dim_cache:
            return self._dim_cache[file_path]

        try:
            with Image.open(file_path) as img:
                w, h = img.size
                self._dim_cache[file_path] = (w, h)
                return w, h
        except Exception:
            self._dim_cache[file_path] = (0, 0)
            return (0, 0)

    @staticmethod
    def apply_case_transform(text: str, transform: str) -> str:
        """Apply case transformation to a text string."""
        mode = transform.lower().strip()
        if mode in ("none", ""):
            return text
        if mode == "lowercase":
            return text.lower()
        if mode == "uppercase":
            return text.upper()
        if mode in ("kebab", "kebab-case"):
            # Replace whitespace, underscores with hyphens and convert to lowercase
            clean = re.sub(r"[\s_]+", "-", text)
            # Insert hyphen before capitals if camelCase: fooBar -> foo-bar
            clean = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", clean)
            clean = re.sub(r"-+", "-", clean).strip("-")
            return clean.lower()
        if mode in ("snake", "snake_case"):
            clean = re.sub(r"[\s\-]+", "_", text)
            clean = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", clean)
            clean = re.sub(r"_+", "_", clean).strip("_")
            return clean.lower()
        if mode in ("title", "title-case"):
            return text.title()
        return text

    def build_target_name(
        self,
        source_path: str,
        index: int,
        pattern: str,
        padding: int = 3,
        case_transform: str = "none",
        find_text: str = "",
        replace_text: str = "",
    ) -> str:
        """Generate the new target filename given template parameters."""
        path = Path(source_path)
        stem = path.stem
        ext = path.suffix.lstrip(".")

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        year_str = now.strftime("%Y")
        month_str = now.strftime("%m")
        day_str = now.strftime("%d")
        time_str = now.strftime("%H-%M-%S")

        w, h = self.get_image_dimensions(source_path)
        w_str = str(w) if w > 0 else ""
        h_str = str(h) if h > 0 else ""

        # Default padded index string
        default_index_str = str(index).zfill(max(1, padding))

        result = pattern

        # Handle custom formatted index patterns like {n:04d} or {index:02d}
        def format_index_match(m: re.Match[str]) -> str:
            spec = m.group(1) or ""
            if spec:
                try:
                    return f"{index:{spec}}"
                except Exception:
                    pass
            return default_index_str

        result = re.sub(
            r"\{(?:n|index|i)(?::([0-9a-zA-Z]+))?\}",
            format_index_match,
            result,
            flags=re.IGNORECASE,
        )

        # Token replacement dictionary
        tokens = {
            "{name}": stem,
            "{stem}": stem,
            "{ext}": ext.lower(),
            "{EXT}": ext.upper(),
            "{date}": date_str,
            "{year}": year_str,
            "{YYYY}": year_str,
            "{month}": month_str,
            "{MM}": month_str,
            "{day}": day_str,
            "{DD}": day_str,
            "{time}": time_str,
            "{w}": w_str,
            "{width}": w_str,
            "{h}": h_str,
            "{height}": h_str,
        }

        for token, val in tokens.items():
            result = result.replace(token, val)

        # If user did not specify extension token or extension in pattern, preserve original extension
        if not re.search(r"\.[a-zA-Z0-9]+$", result):
            if path.suffix:
                result = f"{result}{path.suffix}"

        # Extract stem and extension of the newly formatted target name for case transform
        target_path_obj = Path(result)
        target_stem = target_path_obj.stem
        target_ext = target_path_obj.suffix

        # Apply case transform on the stem
        transformed_stem = self.apply_case_transform(target_stem, case_transform)

        # Apply find and replace if find_text is provided
        if find_text:
            transformed_stem = transformed_stem.replace(find_text, replace_text)

        final_name = f"{transformed_stem}{target_ext}"
        return final_name

    def generate_preview(
        self,
        file_paths: list[str],
        pattern: str = "{name}_{n}",
        start_index: int = 1,
        padding: int = 3,
        case_transform: str = "none",
        find_text: str = "",
        replace_text: str = "",
    ) -> list[RenameItem]:
        """Generate a dry-run preview with in-batch collision and filesystem checks."""
        items: list[RenameItem] = []
        target_counts: dict[str, int] = {}

        # First pass: construct target names
        for i, src_str in enumerate(file_paths):
            src_path = Path(src_str)
            src_name = src_path.name

            try:
                size = src_path.stat().st_size if src_path.exists() else 0
            except Exception:
                size = 0

            w, h = self.get_image_dimensions(src_str)

            if not pattern.strip():
                target_name = src_name
            else:
                target_name = self.build_target_name(
                    source_path=src_str,
                    index=start_index + i,
                    pattern=pattern,
                    padding=padding,
                    case_transform=case_transform,
                    find_text=find_text,
                    replace_text=replace_text,
                )

            target_path = str(src_path.parent / target_name)
            target_norm = target_path.lower()
            target_counts[target_norm] = target_counts.get(target_norm, 0) + 1

            items.append(
                RenameItem(
                    source_path=src_str,
                    source_name=src_name,
                    target_name=target_name,
                    target_path=target_path,
                    status="ok",
                    message="Ready to rename",
                    original_size=size,
                    width=w,
                    height=h,
                )
            )

        # Second pass: validate collisions and path legality
        for item in items:
            src_p = Path(item.source_path)
            tgt_p = Path(item.target_path)
            target_norm = item.target_path.lower()

            # Check for invalid filename characters in target name
            if any(ch in INVALID_FILENAME_CHARS for ch in tgt_p.name):
                item.status = "invalid"
                item.message = 'Target contains invalid characters (< > : " / \\ | ? *)'
                continue

            if not tgt_p.name.strip():
                item.status = "invalid"
                item.message = "Target filename cannot be empty"
                continue

            # In-batch duplicate collision
            if target_counts.get(target_norm, 0) > 1:
                item.status = "collision"
                item.message = "Duplicate target name in current batch"
                continue

            # Unchanged
            if item.source_name == item.target_name:
                item.status = "unchanged"
                item.message = "Filename unchanged"
                continue

            # Check if target already exists on disk
            if tgt_p.exists():
                try:
                    # On Windows, check if it's the exact same file (e.g. case-only change)
                    if src_p.resolve() == tgt_p.resolve():
                        item.status = "ok"
                        item.message = "Case modification on existing file"
                    else:
                        item.status = "exists"
                        item.message = "A different file already exists at target destination"
                except Exception:
                    item.status = "exists"
                    item.message = "Target file already exists on disk"
            else:
                item.status = "ok"
                item.message = "Ready"

        return items

    def execute_rename(self, items: list[RenameItem]) -> tuple[int, list[str]]:
        """Safely execute batch renaming with atomic rollback on any failure.

        Returns (renamed_count, list_of_error_strings).
        """
        # Filter for items that actually need renaming and are valid
        valid_items = [
            item for item in items if item.status == "ok" and item.source_name != item.target_name
        ]

        if not valid_items:
            # Check if any errors or collisions prevented renaming
            errors = [
                f"{item.source_name}: {item.message}"
                for item in items
                if item.status in ("collision", "invalid", "exists")
            ]
            return 0, errors

        executed_history: list[
            tuple[str, str]
        ] = []  # List of (current_path, original_path) for rollback
        errors: list[str] = []

        try:
            for item in valid_items:
                src = Path(item.source_path)
                tgt = Path(item.target_path)

                if not src.exists():
                    msg = f"Source file not found: {src.name}"
                    errors.append(msg)
                    raise FileNotFoundError(msg)

                # Case-only rename on Windows NTFS needs intermediate step
                is_case_only = False
                try:
                    is_case_only = src.resolve() == tgt.resolve() and src.name != tgt.name
                except Exception:
                    pass

                if is_case_only:
                    temp_name = f"{src.name}.tmp_{uuid.uuid4().hex[:8]}"
                    temp_path = src.parent / temp_name
                    os.replace(src, temp_path)
                    try:
                        os.replace(temp_path, tgt)
                    except Exception as e:
                        # Roll back to original
                        if temp_path.exists():
                            os.replace(temp_path, src)
                        raise e
                else:
                    os.replace(src, tgt)

                executed_history.append((str(tgt), str(src)))

            logger.info(
                "Batch rename successfully completed: %d files renamed", len(executed_history)
            )
            return len(executed_history), []

        except Exception as ex:
            logger.error("Error during batch rename, initiating rollback: %s", ex)
            errors.append(str(ex))

            # Roll back in reverse order
            rollback_errors: list[str] = []
            for curr_path_str, orig_path_str in reversed(executed_history):
                try:
                    curr_p = Path(curr_path_str)
                    orig_p = Path(orig_path_str)
                    if curr_p.exists():
                        os.replace(curr_p, orig_p)
                except Exception as rb_ex:
                    rollback_errors.append(f"Rollback failed for {curr_path_str}: {rb_ex}")

            if rollback_errors:
                errors.extend(rollback_errors)

            return 0, errors
