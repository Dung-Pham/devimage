# Task Specification: TASK-P2-03 — Compress Service, Controller, and Presentation View

## Metadata
- **Task ID**: `TASK-P2-03-compress-tool`
- **Phase**: Phase 2 — Core Image Tools
- **Feature**: Compress Tool
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 13:45
- **Completed**: 2026-09-25 14:34

---

## 1. Objective & Scope
Implement the independent Compress tool: pure-Python compress service (`src/devimage/tools/compress/`), PySide6 controller bridge with quality slider (1-100), format retention or target format choice (Original, WebP, JPEG), PNG palette/lossless optimization, EXIF/metadata stripping toggle, file size estimation calculation, and QML view `CompressTool.qml` integrating into `ToolShell.qml`.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Phase MVP, Section 3: Compress)
- `src/devimage/ui/qml/tools/ToolShell.qml`
- `src/devimage/engine/image/processor.py`

### Files to Create / Modify
- `src/devimage/tools/compress/__init__.py`
- `src/devimage/tools/compress/service.py`
- `src/devimage/tools/compress/controller.py`
- `src/devimage/ui/qml/tools/CompressTool.qml`
- `src/devimage/ui/qml/AppShell.qml`
- `src/devimage/app/application.py`
- `tests/unit/test_compress_tool.py`

---

## 3. Implementation Steps
1. Create `src/devimage/tools/compress/service.py` implementing quality compression for JPEG, WebP, and PNG optimization without altering original files.
2. Create `src/devimage/tools/compress/controller.py` (`QObject`) exposing properties (quality, target format, strip metadata, estimated size reduction) and async execution slot.
3. Create `src/devimage/ui/qml/tools/CompressTool.qml` with visual quality slider, reduction percentage preview badge, format radio chips, and metadata switch.
4. Register compress controller in `DevImageApp` and wire tool navigation in `AppShell.qml`.
5. Add unit tests in `tests/unit/test_compress_tool.py` verifying file size reduction, visual quality bounds, and metadata stripping.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Unit Tests**: `uv run pytest tests/unit/test_compress_tool.py -v`
- **Expected Outcome**: Verified compression with correct reduction calculation and non-destructive output.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: Standard core offline tool.

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: compress
- **Commit Message**: `feat(compress): implement compress service, controller bridge, and QML view`
- **Commit Hash**: 7475cd8
- **Push Confirmed**: YES
