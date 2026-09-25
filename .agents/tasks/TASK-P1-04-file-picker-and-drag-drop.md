# Task Specification: TASK-P1-04 — Native File Picker & Drag-and-Drop DropZone

## Metadata
- **Task ID**: `TASK-P1-04-file-picker-and-drag-drop`
- **Phase**: Phase 1 — Application Shell
- **Feature**: File Input & Drag/Drop
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 11:35
- **Completed**: 2026-09-25 11:47

---

## 1. Objective & Scope
Implement `components/DropZone.qml` with visual drag hover states, validation for supported image extensions (PNG, JPG, JPEG, WEBP, BMP, TIFF, GIF, ICO, AVIF), integration with native Qt file dialogs (`FileDialog` / Python backend file helper), and updating `backend.settings` recent files list.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Phase 1, Sections 10, 11)
- [.agents/rules/coding.md](file:///.agents/rules/coding.md)

### Files to Create / Modify
- `src/devimage/ui/qml/components/DropZone.qml`
- `src/devimage/core/signals.py`
- `src/devimage/app/application.py`

---

## 3. Implementation Steps
1. Create `components/DropZone.qml` supporting `DropArea`, visual dashed border glow when dragging, file acceptance filtering, and click-to-browse trigger.
2. Integrate `FileDialog` for single and multi-file selection.
3. Add backend method to handle file path validation and add to recent files.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Test Command**: `uv run pytest tests/ -v`
- **Expected Outcome**: DropArea signals and file validation functions pass unit tests.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: N/A

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: shell
- **Commit Message**: `feat(shell): implement DropZone and native file picker integration`
- **Commit Hash**: 007e779
- **Push Confirmed**: YES
