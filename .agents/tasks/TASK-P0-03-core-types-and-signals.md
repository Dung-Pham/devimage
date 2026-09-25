# Task Specification: TASK-P0-03 — Core Models, Types, Errors, and Signal Layer

## Metadata
- **Task ID**: `TASK-P0-03-core-types-and-signals`
- **Phase**: Phase 0 — Foundation & Project Setup
- **Feature**: Core Models & Event Architecture
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 08:40
- **Completed**: 2026-09-25 08:48

---

## 1. Objective & Scope
Implement the domain primitives in `src/devimage/core/`: `models.py` (data structures for images, tasks, tool state), `types.py` (enums for supported formats, tool identifiers, execution status), `errors.py` (structured `AppError` per plan.md section 19: title, description, cause, suggested action), and `signals.py` (central Qt Signal bridge `AppSignalBridge` based on `QObject` for communication between Python background services and QML).

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Sections 6, 19, 21)
- [.agents/rules/coding.md](file:///.agents/rules/coding.md)

### Files to Create / Modify
- `src/devimage/core/__init__.py`
- `src/devimage/core/types.py`
- `src/devimage/core/models.py`
- `src/devimage/core/errors.py`
- `src/devimage/core/signals.py`
- `tests/unit/test_core.py`

---

## 3. Implementation Steps
1. Implement `types.py` with enums: `ImageFormat`, `ToolType`, `TaskStatus`, `ThemeMode`.
2. Implement `errors.py`: Define `AppError(Exception)` with `title`, `description`, `cause`, `suggested_action`, and serialization helper for UI/toast display.
3. Implement `models.py`: Define `ImageItem`, `ProcessingOptions`, `ProcessingResult` dataclasses / pydantic models.
4. Implement `signals.py`: Define `AppSignalBridge(QObject)` with Qt Signals for global notifications, progress updates, tool state transitions, and error events.
5. Implement unit tests in `tests/unit/test_core.py`.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Test Command**: `uv run pytest tests/unit/test_core.py -v`
- **Expected Outcome**: All core types, models, errors, and Qt signal bridge instantiate and test cleanly.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: N/A

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: core
- **Commit Message**: `feat(core): implement core models, types, structured errors, and signal bridge`
- **Commit Hash**:
- **Push Confirmed**: NO
