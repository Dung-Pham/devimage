# Task Specification: TASK-P2-05 — Crop Service, Controller, and Interactive View

## Metadata
- **Task ID**: `TASK-P2-05-crop-tool`
- **Phase**: Phase 2 — Core Image Tools
- **Feature**: Crop Tool
- **Status**: PENDING
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 13:45
- **Completed**: 

---

## 1. Objective & Scope
Implement the independent Crop tool: pure-Python crop service (`src/devimage/tools/crop/`), PySide6 controller bridge with bounding box coordinate transformations, aspect ratio constraints (Free, 1:1, 4:3, 3:4, 16:9, 9:16), 90-degree rotation, center crop, and QML view `CropTool.qml` with an interactive draggable crop rectangle overlay over the preview canvas.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Phase MVP, Section 5: Crop)
- `src/devimage/ui/qml/tools/ToolShell.qml`
- `src/devimage/ui/qml/components/ImagePreview.qml`
- `src/devimage/engine/image/processor.py`

### Files to Create / Modify
- `src/devimage/tools/crop/__init__.py`
- `src/devimage/tools/crop/service.py`
- `src/devimage/tools/crop/controller.py`
- `src/devimage/ui/qml/tools/CropTool.qml`
- `src/devimage/ui/qml/components/CropOverlay.qml`
- `src/devimage/ui/qml/AppShell.qml`
- `src/devimage/app/application.py`
- `tests/unit/test_crop_tool.py`

---

## 3. Implementation Steps
1. Create `src/devimage/tools/crop/service.py` with bounding box cropping, boundary clamping, and 90-degree CW/CCW rotation functions.
2. Create `src/devimage/tools/crop/controller.py` (`QObject`) managing normalized crop coordinates (x, y, width, height: 0.0 to 1.0), aspect ratio constraints, and rotation state.
3. Create `src/devimage/ui/qml/components/CropOverlay.qml` providing an interactive crop box with corner and edge drag handles and darkened mask surroundings.
4. Create `src/devimage/ui/qml/tools/CropTool.qml` embedding `ToolShell` with aspect ratio buttons, rotate buttons, reset, and live dimension indicators.
5. Register crop controller in `DevImageApp` and wire tool navigation in `AppShell.qml`.
6. Add unit tests in `tests/unit/test_crop_tool.py` checking coordinate math, edge constraints, aspect snapping, and rotation.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Unit Tests**: `uv run pytest tests/unit/test_crop_tool.py -v`
- **Expected Outcome**: Accurate pixel cropping matching selected rectangle coordinates without visual artifacts.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: Standard core offline tool.

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: crop
- **Commit Message**: `feat(crop): implement crop service, interactive crop overlay, and QML view`
- **Commit Hash**: 
- **Push Confirmed**: NO
