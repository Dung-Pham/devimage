"""PySide6 QObject controller bridge for Color Picker tool."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication

from devimage.app.logging import get_logger
from devimage.app.settings import SettingsManager
from devimage.core.signals import AppSignalBridge
from devimage.tools.color_picker.service import ColorService, build_color_bundle, hex_to_rgb

logger = get_logger("tools.color_picker.controller")


class ColorPickerController(QObject):
    """QObject bridge between Python ColorService and QML ColorPickerTool interface."""

    colorChanged = Signal()
    paletteChanged = Signal()
    imageLoaded = Signal()

    def __init__(
        self,
        service: ColorService | None = None,
        signals: AppSignalBridge | None = None,
        settings: SettingsManager | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service or ColorService()
        self._signals = signals
        self._settings = settings

        self._current_path: str = ""
        self._current_color: dict[str, Any] = build_color_bundle(64, 128, 255, 255)
        self._palette_colors: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # Properties for QML
    # ---------------------------------------------------------

    @Property(bool, notify=imageLoaded)
    def hasImage(self) -> bool:
        """Whether a valid image is loaded."""
        return bool(self._current_path and Path(self._current_path).is_file())

    @Property(str, notify=imageLoaded)
    def currentImagePath(self) -> str:
        """Absolute file path to current loaded image."""
        return self._current_path

    @Property(str, notify=colorChanged)
    def currentHex(self) -> str:
        """Active hex color code (e.g. #3B82F6)."""
        return self._current_color.get("hex", "#3B82F6")

    @Property(str, notify=colorChanged)
    def currentHexAlpha(self) -> str:
        """Active hex color code with alpha (e.g. #3B82F6FF)."""
        return self._current_color.get("hex_alpha", "#3B82F6FF")

    @Property(str, notify=colorChanged)
    def currentRgb(self) -> str:
        """Active CSS RGB/RGBA string (e.g. rgb(59, 130, 246))."""
        return self._current_color.get("rgb_str", "rgb(59, 130, 246)")

    @Property(str, notify=colorChanged)
    def currentHsl(self) -> str:
        """Active CSS HSL/HSLA string (e.g. hsl(217, 91%, 60%))."""
        return self._current_color.get("hsl_str", "hsl(217, 91%, 60%)")

    @Property(str, notify=colorChanged)
    def currentCssVar(self) -> str:
        """Active CSS variable declaration."""
        return self._current_color.get("css_var", "--color-sampled: #3B82F6;")

    @Property(int, notify=colorChanged)
    def r(self) -> int:
        """Red channel (0-255)."""
        return int(self._current_color.get("r", 59))

    @Property(int, notify=colorChanged)
    def g(self) -> int:
        """Green channel (0-255)."""
        return int(self._current_color.get("g", 130))

    @Property(int, notify=colorChanged)
    def b(self) -> int:
        """Blue channel (0-255)."""
        return int(self._current_color.get("b", 246))

    @Property(int, notify=colorChanged)
    def a(self) -> int:
        """Alpha channel (0-255)."""
        return int(self._current_color.get("a", 255))

    @Property(int, notify=colorChanged)
    def coordX(self) -> int:
        """Sampled pixel X coordinate."""
        return int(self._current_color.get("x", 0))

    @Property(int, notify=colorChanged)
    def coordY(self) -> int:
        """Sampled pixel Y coordinate."""
        return int(self._current_color.get("y", 0))

    @Property(str, notify=colorChanged)
    def contrastText(self) -> str:
        """Optimal contrast text color (#ffffff or #000000)."""
        return self._current_color.get("contrast_text", "#ffffff")

    @Property("QVariantList", notify=paletteChanged)
    def paletteColors(self) -> list[dict[str, Any]]:
        """List of dominant palette colors extracted from image."""
        return self._palette_colors

    # ---------------------------------------------------------
    # Slots
    # ---------------------------------------------------------

    @Slot(str)
    def loadImage(self, file_path: str) -> None:
        """Load image, extract dominant color palette, and sample center pixel."""
        if not file_path:
            return

        clean_path = file_path
        if clean_path.startswith("file:"):
            clean_path = QUrl(file_path).toLocalFile()

        try:
            # 1. Extract dominant palette
            self._palette_colors = self._service.extract_palette(clean_path, max_colors=8)
            self._current_path = clean_path

            # 2. Sample center pixel or first palette color
            img = self._service._get_image(clean_path)
            w, h = img.size
            self._current_color = self._service.sample_pixel(clean_path, w // 2, h // 2)

            logger.info(
                "Loaded %s for Color Picker (found %d palette colors)",
                clean_path,
                len(self._palette_colors),
            )
            self.imageLoaded.emit()
            self.paletteChanged.emit()
            self.colorChanged.emit()
        except Exception as err:
            logger.error("Failed to load image for color picker %s: %s", clean_path, err)
            if self._signals:
                self._signals.triggerError(
                    "Color Picker Failed",
                    f"Unable to read colors from {clean_path}",
                    str(err),
                    "Verify the image is a readable, uncorrupted picture file.",
                )

    @Slot(int, int)
    def sampleAt(self, x: int, y: int) -> None:
        """Sample pixel color at image coordinate (x, y)."""
        if not self._current_path:
            return

        try:
            self._current_color = self._service.sample_pixel(self._current_path, x, y)
            self.colorChanged.emit()
        except Exception as err:
            logger.error("Failed to sample color at (%d, %d): %s", x, y, err)

    @Slot(str)
    def selectColor(self, hex_code: str) -> None:
        """Select a color directly by hex string (e.g. from palette item)."""
        try:
            r, g, b, a = hex_to_rgb(hex_code)
            self._current_color = build_color_bundle(r, g, b, a, x=self.coordX, y=self.coordY)
            self.colorChanged.emit()
        except Exception as err:
            logger.warning("Failed to select hex color %s: %s", hex_code, err)

    @Slot()
    def copyHex(self) -> None:
        """Copy active HEX color string to clipboard."""
        val = self.currentHex
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(val)
            if self._signals:
                self._signals.showToast("success", "Copied", f"{val} copied to clipboard", 2000)

    @Slot()
    def copyRgb(self) -> None:
        """Copy active RGB/RGBA string to clipboard."""
        val = self.currentRgb
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(val)
            if self._signals:
                self._signals.showToast("success", "Copied", f"{val} copied to clipboard", 2000)

    @Slot()
    def copyHsl(self) -> None:
        """Copy active HSL/HSLA string to clipboard."""
        val = self.currentHsl
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(val)
            if self._signals:
                self._signals.showToast("success", "Copied", f"{val} copied to clipboard", 2000)

    @Slot()
    def copyCssVar(self) -> None:
        """Copy active CSS variable declaration to clipboard."""
        val = self.currentCssVar
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(val)
            if self._signals:
                self._signals.showToast("success", "Copied", f"{val} copied to clipboard", 2000)

    @Slot()
    def copyJson(self) -> None:
        """Copy JSON representation of all color formats to clipboard."""
        data = {
            "hex": self.currentHex,
            "hex_alpha": self.currentHexAlpha,
            "rgb": self.currentRgb,
            "hsl": self.currentHsl,
            "channels": {"r": self.r, "g": self.g, "b": self.b, "a": self.a},
            "coordinates": {"x": self.coordX, "y": self.coordY},
            "css_variable": self.currentCssVar,
        }
        json_str = json.dumps(data, indent=2)
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(json_str)
            if self._signals:
                self._signals.showToast("success", "Copied", "Color JSON copied to clipboard", 2000)

    @Slot()
    def copyPaletteCss(self) -> None:
        """Copy entire palette as CSS variables."""
        if not self._palette_colors:
            return
        lines = [":root {"]
        for i, col in enumerate(self._palette_colors, start=1):
            lines.append(f"  --color-palette-{i}: {col.get('hex')};")
        lines.append("}")
        css_str = "\n".join(lines)

        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(css_str)
            if self._signals:
                self._signals.showToast(
                    "success", "Copied", "Palette CSS variables copied to clipboard", 2000
                )
