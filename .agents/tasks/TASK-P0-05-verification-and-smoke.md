# Task Specification: TASK-P0-05 — End-to-End Headless Smoke Test & Phase 0 Acceptance

## Metadata
- **Task ID**: `TASK-P0-05-verification-and-smoke`
- **Phase**: Phase 0 — Foundation & Project Setup
- **Feature**: Automated Verification & Phase Acceptance
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 08:40
- **Completed**: 2026-09-25 08:53

---

## 1. Objective & Scope
Implement the headless GUI smoke test suite `tests/test_gui_smoke.py` validating that the PySide6 QML engine initializes offscreen, loads `Main.qml` without errors, confirms Python-to-QML and QML-to-Python signal/property communication, and executes the complete verification suite (`ruff` + `pytest`). Verify all Phase 0 acceptance criteria.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Section 35 Phase 0 Acceptance)
- [.agents/verification/verification-runner.md](file:///.agents/verification/verification-runner.md)
- [.agents/verification/acceptance-matrix.md](file:///.agents/verification/acceptance-matrix.md)

### Files to Create / Modify
- `tests/test_gui_smoke.py`
- `tests/conftest.py`

---

## 3. Implementation Steps
1. Create `tests/conftest.py` with standard Qt offscreen fixtures and environment settings (`QT_QPA_PLATFORM=offscreen`).
2. Create `tests/test_gui_smoke.py`:
   - Test application startup and QML engine component instantiation.
   - Test that backend bridge properties (`appName`, `version`, `settings`) are accessible in QML.
   - Test that signal emissions from Python reach QML slots / handlers.
3. Run the full verification suite (`ruff check`, `pytest tests/ -v`).
4. Validate all acceptance requirements for Phase 0.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Test Command**: `uv run pytest tests/ -v`
- **Smoke Command**: `uv run python -m devimage.main --dry-run` or headless test.
- **Expected Outcome**: 100% tests passing, zero lint warnings, verified Phase 0 acceptance.

---

## 5. Human Approval Gates
- **Gate Required**: GATE-PHASE (upon completion of TASK-P0-05, Phase 0 concludes and requires human sign-off before Phase 1).
- **Gate Rationale**: Formal phase gate required by `.agents/controller/gates.md`.

---

## 6. Completion Checkpoint
- **Commit Type**: test
- **Commit Scope**: smoke
- **Commit Message**: `test(smoke): add headless gui smoke tests and verify Phase 0 acceptance`
- **Commit Hash**: ea9b4d2
- **Push Confirmed**: YES
