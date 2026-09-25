# Task Specification: TASK-P0-04 — QML Application & Python Engine Integration

## Metadata
- **Task ID**: `TASK-P0-04-qml-application`
- **Phase**: Phase 0 — Foundation & Project Setup
- **Feature**: PySide6 Application & QML Engine Setup
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 08:40
- **Completed**: 2026-09-25 08:51

---

## 1. Objective & Scope
Implement the application entry point and PySide6 / QML integration: `src/devimage/app/application.py` creating `QGuiApplication`, initializing `QQmlApplicationEngine`, registering context properties / singletons (signal bridge, settings, app metadata), and loading `src/devimage/ui/qml/Main.qml`. Implement `src/devimage/main.py` entrypoint script with CLI argument parsing (e.g. `--debug`).

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Sections 21, 35)
- [prompt-build.md](file:///prompt-build.md) (Sections 5, 6)
- [.agents/rules/coding.md](file:///.agents/rules/coding.md)

### Files to Create / Modify
- `src/devimage/main.py`
- `src/devimage/app/application.py`
- `src/devimage/ui/__init__.py`
- `src/devimage/ui/qml/Main.qml`
- `src/devimage/ui/qml/qmldir`

---

## 3. Implementation Steps
1. Create `src/devimage/ui/qml/Main.qml` with a modern developer-styled desktop window (frameless or standard styled window, dark-theme default, responsive layout container, verification text/status).
2. Create `src/devimage/app/application.py`:
   - Initialize `QGuiApplication` with high-DPI scaling enabled.
   - Configure Qt Quick style.
   - Initialize `QQmlApplicationEngine`.
   - Expose backend bridge (SignalBridge and SettingsManager) to QML root context.
   - Handle QML loading errors gracefully (`engine.warnings` / `quit()`).
3. Create `src/devimage/main.py`:
   - Configure exception hooks and signal handling.
   - Parse CLI arguments (e.g., `--debug`).
   - Run `create_app()` and `sys.exit(app.exec())`.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/`
- **QML Syntax / Compilation Check**: Validate QML file loading via Python script in offscreen mode.
- **Expected Outcome**: Engine loads QML root component cleanly without syntax or unresolved property errors.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: N/A

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: ui
- **Commit Message**: `feat(ui): implement PySide6 QML application engine and Main.qml window`
- **Commit Hash**:
- **Push Confirmed**: NO
