# Task Specification: TASK-P3-03-batch-rename-tool

## Metadata
- **Task ID**: `TASK-P3-03-batch-rename-tool`
- **Phase**: Phase 3 — Developer Tools
- **Feature**: Batch Rename
- **Status**: PENDING
- **Assigned Worker**: Implementer
- **Claimed By Session**: None
- **Lock Lease Seconds**: 300
- **Created**: 2026-09-25 15:30:00 +07:00
- **Completed**: 

---

## 1. Objective & Scope
Implement the pure-Python `RenameService`, PySide6 `RenameController` bridge, and QML view `RenameTool.qml` for template-based batch renaming (patterns like `prefix-{n}`, start indices, padding, case conversions, collision checks) with real-time preview.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- `src/devimage/ui/qml/tools/ToolShell.qml`
- `src/devimage/app/settings.py`

### Files to Create / Modify
- `src/devimage/tools/rename/__init__.py`
- `src/devimage/tools/rename/service.py`
- `src/devimage/tools/rename/controller.py`
- `src/devimage/ui/qml/tools/RenameTool.qml`
- `src/devimage/app/application.py`
- `src/devimage/ui/qml/tools/ToolShell.qml`
- `tests/unit/test_rename_tool.py`

---

## 3. Implementation Steps
1. Create `src/devimage/tools/rename/service.py`:
   - Pattern substitution with `{n}`, `{name}`, `{ext}`, `{date}`, `{width}x{height}`.
   - Zero-padding support (e.g. `{n:03d}`).
   - Case transforms (lowercase, UPPERCASE, kebab-case, snake_case).
   - Collision detection and dry-run preview generation.
   - Safe atomic renaming with rollback on error.
2. Create `src/devimage/tools/rename/controller.py`:
   - Manage file list and dry-run preview model.
   - Expose properties (`pattern`, `startIndex`, `zeroPadding`, `caseTransform`).
   - Execute batch rename.
3. Create `src/devimage/ui/qml/tools/RenameTool.qml`:
   - Input fields for pattern, numbering, case.
   - Real-time preview comparison table (Original Name -> Target Name, Status).
4. Integrate with `ToolShell.qml` and `application.py`.
5. Add unit tests in `tests/unit/test_rename_tool.py`.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Format Check**: `uv run ruff format --check src/ tests/`
- **Unit Tests**: `uv run pytest tests/unit/test_rename_tool.py -v`

---

## 5. Human Approval Gates
- **Gate Required**: None

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: rename
- **Commit Message**: `feat(rename): implement batch file rename service, controller bridge, and QML view`
- **Commit Hash**: 
- **Push Confirmed**: NO
