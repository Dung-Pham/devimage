# Task Specification: TASK-P2-04 — Convert Service, Controller, and Presentation View

## Metadata
- **Task ID**: `TASK-P2-04-convert-tool`
- **Phase**: Phase 2 — Core Image Tools
- **Feature**: Convert Tool
- **Status**: PENDING
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 13:45
- **Completed**: 

---

## 1. Objective & Scope
Implement the independent Convert tool: pure-Python format conversion service (`src/devimage/tools/convert/`), PySide6 controller bridge supporting input formats (PNG, JPG/JPEG, WebP, BMP, TIFF) and output formats (PNG, JPEG, WebP), quality options, transparency preservation (e.g. RGBA -> RGB with white background for JPEG), metadata preservation options, and QML view `ConvertTool.qml` integrating into `ToolShell.qml`.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Phase MVP, Section 4: Convert)
- `src/devimage/ui/qml/tools/ToolShell.qml`
- `src/devimage/engine/image/processor.py`

### Files to Create / Modify
- `src/devimage/tools/convert/__init__.py`
- `src/devimage/tools/convert/service.py`
- `src/devimage/tools/convert/controller.py`
- `src/devimage/ui/qml/tools/ConvertTool.qml`
- `src/devimage/ui/qml/AppShell.qml`
- `src/devimage/app/application.py`
- `tests/unit/test_convert_tool.py`

---

## 3. Implementation Steps
1. Create `src/devimage/tools/convert/service.py` implementing robust format conversion, handling color space transitions (RGBA to RGB background compositing when target format lacks alpha).
2. Create `src/devimage/tools/convert/controller.py` (`QObject`) exposing target format selection, quality slider, custom output directory/filename patterns, and async execution.
3. Create `src/devimage/ui/qml/tools/ConvertTool.qml` with target format selector chips (PNG, JPEG, WebP), quality settings, output naming preview, and convert action.
4. Register convert controller in `DevImageApp` and wire tool navigation in `AppShell.qml`.
5. Add unit tests in `tests/unit/test_convert_tool.py` verifying cross-format conversion integrity and RGBA-to-RGB flattening.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Unit Tests**: `uv run pytest tests/unit/test_convert_tool.py -v`
- **Expected Outcome**: Accurate format conversion preserving image visual fidelity and handling transparency gracefully.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: Standard core offline tool.

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: convert
- **Commit Message**: `feat(convert): implement convert service, controller bridge, and QML view`
- **Commit Hash**: 
- **Push Confirmed**: NO
