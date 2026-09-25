# Task Specification: TASK-P3-02-color-picker-tool

## Metadata
- **Task ID**: `TASK-P3-02-color-picker-tool`
- **Phase**: Phase 3 — Developer Tools
- **Feature**: Color Picker
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Claimed By Session**: session-20260925-phase3
- **Lock Lease Seconds**: 300
- **Created**: 2026-09-25 15:30:00 +07:00
- **Completed**: 2026-09-25 16:09:00 +07:00 

---

## 1. Objective & Scope
Implement the pure-Python `ColorService`, PySide6 `ColorPickerController` bridge, and QML view `ColorPickerTool.qml` for pixel sampling, color space conversions (RGB, HEX, HSL, CSS variable formatting), and clipboard export.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- `src/devimage/ui/qml/tools/ToolShell.qml`
- `src/devimage/tools/inspector/service.py`

### Files to Create / Modify
- `src/devimage/tools/color_picker/__init__.py`
- `src/devimage/tools/color_picker/service.py`
- `src/devimage/tools/color_picker/controller.py`
- `src/devimage/ui/qml/tools/ColorPickerTool.qml`
- `src/devimage/app/application.py`
- `src/devimage/ui/qml/tools/ToolShell.qml`
- `tests/unit/test_color_picker_tool.py`

---

## 3. Implementation Steps
1. Create `src/devimage/tools/color_picker/service.py`:
   - Sample pixel color (x, y) from image.
   - Convert between RGB, HEX, HSL, and CSS variable string (`--color-primary: #...`).
   - Extract dominant / palette colors from image.
2. Create `src/devimage/tools/color_picker/controller.py`:
   - Connect mouse hover/click coordinates on image preview to pixel sampling.
   - Expose properties (`currentHex`, `currentRgb`, `currentHsl`, `paletteColors`).
   - Provide clipboard copy slots (`copyHex()`, `copyRgb()`, `copyHsl()`, `copyCss()`, `copyJson()`).
3. Create `src/devimage/ui/qml/tools/ColorPickerTool.qml`:
   - Swatch display, live magnified loupe or coordinate readout, color code inputs, copy buttons.
4. Integrate with `ToolShell.qml` and `application.py`.
5. Add unit tests in `tests/unit/test_color_picker_tool.py`.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Format Check**: `uv run ruff format --check src/ tests/`
- **Unit Tests**: `uv run pytest tests/unit/test_color_picker_tool.py -v`

---

## 5. Human Approval Gates
- **Gate Required**: None

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: color-picker
- **Commit Message**: `feat(color-picker): implement pixel color sampling service, controller bridge, and QML view`
- **Commit Hash**: 
- **Push Confirmed**: NO
