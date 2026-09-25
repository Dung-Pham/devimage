# Task Specification: TASK-P1-01 — MainWindow, AppShell, and Navigation Architecture

## Metadata
- **Task ID**: `TASK-P1-01-app-shell-and-navigation`
- **Phase**: Phase 1 — Application Shell
- **Feature**: Shell Layout & Navigation
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 11:35
- **Completed**: 2026-09-25 11:37

---

## 1. Objective & Scope
Refactor the QML root to use a modular `AppShell.qml` component containing a persistent header (branding, current view title / breadcrumb, settings button), a centralized view container (`StackView` or state-driven loader), and a footer bar. Implement navigation logic in Python and QML to smoothly switch between views.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Phase 1, Section 8, Section 35)
- [prompt-build.md](file:///prompt-build.md) (Section 5, 8)
- [.agents/rules/coding.md](file:///.agents/rules/coding.md)

### Files to Create / Modify
- `src/devimage/ui/qml/Main.qml`
- `src/devimage/ui/qml/AppShell.qml`
- `src/devimage/ui/qml/common/Header.qml`
- `src/devimage/ui/qml/common/Footer.qml`

---

## 3. Implementation Steps
1. Create `src/devimage/ui/qml/common/Header.qml` with branding, active section breadcrumb, back-button (when in a tool), and settings gear button.
2. Create `src/devimage/ui/qml/common/Footer.qml` with status indicator, privacy badge ("Offline-First"), and keyboard shortcut hint.
3. Create `src/devimage/ui/qml/AppShell.qml` hosting Header, active view container (StackView/Loader), and Footer.
4. Update `Main.qml` to embed `AppShell` and manage window state and global shortcut bindings.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **QML Offscreen Check**: Verify `DevImageApp.load_qml()` loads `Main.qml` and `AppShell.qml` without errors.
- **Unit & Smoke Tests**: `uv run pytest tests/ -v`
- **Expected Outcome**: Clean QML instantiation with zero property binding warnings.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: Standard pre-approved UI shell components.

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: shell
- **Commit Message**: `feat(shell): implement AppShell, Header, Footer, and navigation container`
- **Commit Hash**: 468fac0
- **Push Confirmed**: YES
