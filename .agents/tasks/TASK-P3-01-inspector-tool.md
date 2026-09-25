# Task Specification: TASK-P3-01-inspector-tool

## Metadata
- **Task ID**: `TASK-P3-01-inspector-tool`
- **Phase**: Phase 3 — Developer Tools
- **Feature**: Image Inspector
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Claimed By Session**: session-20260925-phase3
- **Lock Lease Seconds**: 300
- **Created**: 2026-09-25 15:30:00 +07:00
- **Completed**: 2026-09-25 15:35:00 +07:00

---

## 1. Objective & Scope
Implement the pure-Python `InspectorService`, PySide6 `InspectorController` bridge, and QML view `InspectorTool.qml` for the Image Inspector feature. The tool provides non-destructive inspection of image metadata, dimensions, color mode, alpha channel, DPI, EXIF tags, and optimization potential, with "Copy All" and "Copy JSON" clipboard facilities.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- `src/devimage/engine/image/metadata.py`
- `src/devimage/tools/resize/service.py`
- `src/devimage/tools/resize/controller.py`
- `src/devimage/ui/qml/tools/ToolShell.qml`

### Files to Create / Modify
- `src/devimage/tools/inspector/__init__.py`
- `src/devimage/tools/inspector/service.py`
- `src/devimage/tools/inspector/controller.py`
- `src/devimage/ui/qml/tools/InspectorTool.qml`
- `src/devimage/app/application.py` (register InspectorController)
- `src/devimage/ui/qml/tools/ToolShell.qml` (wire InspectorTool loader)
- `tests/unit/test_inspector_tool.py`

---

## 3. Implementation Steps
1. Create `src/devimage/tools/inspector/service.py`:
   - Inspect dimensions, format, filesize, aspect ratio, color mode, has_alpha, DPI, and human-readable EXIF dict.
   - Calculate optimization advice (e.g. potential WebP/compress benefit).
   - Generate structured dict, JSON string, and formatted clipboard report.
2. Create `src/devimage/tools/inspector/controller.py`:
   - Expose inspection properties to QML (`filename`, `dimensions`, `colorMode`, `fileSize`, `hasAlpha`, `dpi`, `exifSummary`, `jsonSummary`).
   - Implement `copyJson()` and `copyAll()` copying to system clipboard via `QGuiApplication.clipboard()`.
3. Create `src/devimage/ui/qml/tools/InspectorTool.qml`:
   - Clean developer-centric metadata card view with sections: File Info, Geometry, Color & Channels, EXIF / Technical, and Copy action buttons.
4. Integrate into `ToolShell.qml` and `application.py`:
   - Wire loader and controller context property.
5. Create comprehensive unit tests in `tests/unit/test_inspector_tool.py`.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Format Check**: `uv run ruff format --check src/ tests/`
- **Unit Tests**: `uv run pytest tests/unit/test_inspector_tool.py -v`
- **Full Suite**: `uv run pytest` (all tests passing)

---

## 5. Human Approval Gates
- **Gate Required**: None (Standard Phase 3 in-progress task)

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: inspector
- **Commit Message**: `feat(inspector): implement image metadata inspector service, controller bridge, and QML view`
- **Commit Hash**: `0d5a33c`
- **Push Confirmed**: YES
