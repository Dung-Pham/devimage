# Task Specification: TASK-P1-03 — Common Components & Dialogs (Toast, ErrorDialog, SettingsDialog)

## Metadata
- **Task ID**: `TASK-P1-03-common-components-and-dialogs`
- **Phase**: Phase 1 — Application Shell
- **Feature**: Presentation Components & Modals
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 11:35
- **Completed**: 2026-09-25 11:44

---

## 1. Objective & Scope
Extract and enhance common UI components: `components/ToastBanner.qml` with slide-in animation, `dialogs/ErrorDialog.qml` implementing Plan Section 19 structured error view (Title, Description, Cause, Suggested Action), and `dialogs/SettingsDialog.qml` for editing theme, default quality, conflict mode, and output directory.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Section 19 Error Handling, Section 20 Settings)
- [.agents/rules/coding.md](file:///.agents/rules/coding.md)

### Files to Create / Modify
- `src/devimage/ui/qml/components/ToastBanner.qml`
- `src/devimage/ui/qml/dialogs/ErrorDialog.qml`
- `src/devimage/ui/qml/dialogs/SettingsDialog.qml`

---

## 3. Implementation Steps
1. Create `ToastBanner.qml` supporting queuing, automatic dismissal, severity colors (info, success, warning, error).
2. Create `ErrorDialog.qml` with clear developer-grade layout displaying error details, possible causes, and recovery buttons.
3. Create `SettingsDialog.qml` with form controls linked to `backend.settings` (theme selection, overwrite mode dropdown, slider for default quality).

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Test Command**: `uv run pytest tests/ -v`
- **Expected Outcome**: Dialogs instantiate cleanly without syntax or binding errors.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: N/A

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: ui
- **Commit Message**: `feat(ui): implement ToastBanner, ErrorDialog, and SettingsDialog components`
- **Commit Hash**: b3e811f
- **Push Confirmed**: YES
