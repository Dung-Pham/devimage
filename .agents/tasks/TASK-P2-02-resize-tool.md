# Task Specification: TASK-P2-02 — Resize Service, Controller, and Presentation View

## Metadata
- **Task ID**: `TASK-P2-02-resize-tool`
- **Phase**: Phase 2 — Core Image Tools
- **Feature**: Resize Tool
- **Status**: PENDING
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 13:45
- **Completed**: 

---

## 1. Objective & Scope
Implement the independent Resize tool adhering to the plan specification: pure-Python resize service (`src/devimage/tools/resize/`), PySide6 controller bridge with width, height, aspect ratio locking, resize modes (fit/contain, fill/cover, stretch), upscale prevention ("don't enlarge"), resolution presets (1920, 1600, 1200, 1024, 768, 480), and QML view `ResizeTool.qml` integrating into `ToolShell.qml`.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Phase MVP, Section 2: Resize)
- `src/devimage/ui/qml/tools/ToolShell.qml`
- `src/devimage/engine/image/processor.py`

### Files to Create / Modify
- `src/devimage/tools/__init__.py`
- `src/devimage/tools/resize/__init__.py`
- `src/devimage/tools/resize/service.py`
- `src/devimage/tools/resize/controller.py`
- `src/devimage/ui/qml/tools/ResizeTool.qml`
- `src/devimage/ui/qml/AppShell.qml`
- `src/devimage/app/application.py`
- `tests/unit/test_resize_tool.py`

---

## 3. Implementation Steps
1. Create `src/devimage/tools/resize/service.py` implementing exact resize calculation and execution (contain, cover, stretch, don't enlarge, aspect locking).
2. Create `src/devimage/tools/resize/controller.py` (`QObject`) exposing properties and slots to QML for parameters, target dimension calculation, and async execution via worker pool.
3. Create `src/devimage/ui/qml/tools/ResizeTool.qml` hosting dimension inputs, preset chips, aspect ratio toggle, mode selector, and triggering process action in `ToolShell`.
4. Register resize controller in `DevImageApp` and wire tool navigation in `AppShell.qml`.
5. Write unit tests in `tests/unit/test_resize_tool.py` testing dimension math, aspect locking, scaling filters, and output files.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Unit Tests**: `uv run pytest tests/unit/test_resize_tool.py -v`
- **Expected Outcome**: All resize calculations match expected bounding boxes; output files correctly written.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: Standard core offline tool.

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: resize
- **Commit Message**: `feat(resize): implement resize service, controller bridge, and QML view`
- **Commit Hash**: 
- **Push Confirmed**: NO
