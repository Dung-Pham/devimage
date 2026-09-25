# Task Specification: TASK-P2-01 — Core Image Engine and Asynchronous Worker Pool

## Metadata
- **Task ID**: `TASK-P2-01-image-engine-and-worker-pool`
- **Phase**: Phase 2 — Core Image Tools
- **Feature**: Image Engine & Worker Infrastructure
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 13:45
- **Completed**: 2026-09-25 13:48

---

## 1. Objective & Scope
Implement the core pure-Python image processing engine (`src/devimage/engine/image/`) wrapping Pillow for safe loading, saving, format normalization, aspect ratio calculations, dimension constraints, and EXIF/metadata preservation. Implement an asynchronous worker abstraction (`src/devimage/workers/`) using PySide6 `QRunnable` and `QThreadPool` with progress, cancellation, and result signals to ensure the QML UI never blocks during processing.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Section 2, Section 3, Section 8)
- [.agents/rules/coding.md](file:///.agents/rules/coding.md)
- `src/devimage/core/models.py`
- `src/devimage/core/signals.py`

### Files to Create / Modify
- `src/devimage/engine/__init__.py`
- `src/devimage/engine/image/__init__.py`
- `src/devimage/engine/image/processor.py`
- `src/devimage/engine/image/metadata.py`
- `src/devimage/workers/__init__.py`
- `src/devimage/workers/pool.py`
- `src/devimage/workers/image_worker.py`
- `tests/unit/test_image_engine.py`

---

## 3. Implementation Steps
1. Create `src/devimage/engine/image/metadata.py` for extracting dimensions, color mode, format, alpha channel detection, and EXIF info safely.
2. Create `src/devimage/engine/image/processor.py` with pure-Python image manipulation functions: `open_image`, `save_image`, calculate aspect ratios, contain/cover/stretch bounds calculation.
3. Create `src/devimage/workers/image_worker.py` inheriting from `QRunnable` with a dedicated `QObject` signal carrier (progress, completed, failed, cancelled).
4. Create `src/devimage/workers/pool.py` providing a shared singleton/managed `QThreadPool` for non-blocking operations.
5. Add comprehensive unit tests in `tests/unit/test_image_engine.py` verifying aspect ratio logic, format checks, metadata extraction, and async worker execution.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Unit Tests**: `uv run pytest tests/unit/test_image_engine.py -v`
- **Full Test Suite**: `uv run pytest tests/ -v`
- **Expected Outcome**: All tests passing without errors or thread lock issues.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: Built on pre-approved Pillow and PySide6 foundation.

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: engine
- **Commit Message**: `feat(engine): implement core image engine primitives and async worker pool`
- **Commit Hash**: 
- **Push Confirmed**: NO
