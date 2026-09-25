# Task Specification: TASK-P1-06 — Phase 1 End-to-End Headless Acceptance Suite

## Metadata
- **Task ID**: `TASK-P1-06-phase-1-verification-and-acceptance`
- **Phase**: Phase 1 — Application Shell
- **Feature**: Acceptance Testing & Phase 1 Sign-Off
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 11:35
- **Completed**: 2026-09-25 11:55

---

## 1. Objective & Scope
Implement comprehensive automated headless test suite `tests/test_app_shell.py` validating all Phase 1 acceptance criteria:
- Open app
- Select tool from Home tool cards
- Return back to Home
- Open / drop image into workspace
- View preview in preview component
- Open settings dialog and toggle preferences
Verify full verification suite (`ruff` + `pytest`).

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Phase 1 Acceptance criteria)
- [.agents/verification/acceptance-matrix.md](file:///.agents/verification/acceptance-matrix.md)

### Files to Create / Modify
- `tests/test_app_shell.py`

---

## 3. Implementation Steps
1. Create `tests/test_app_shell.py` with tests for:
   - Tool card catalog completeness (all 13 tools present: 5 image tools, 5 developer tools, 3 AI tools).
   - Navigation from Home to a selected tool and returning back to Home.
   - DropZone file acceptance and signal dispatch.
   - ImagePreview property binding.
   - Settings dialog interaction.
2. Run full verification runner (`ruff check`, `pytest tests/ -v`).

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Test Command**: `uv run pytest tests/ -v`
- **Expected Outcome**: 100% test pass rate with zero errors or warnings.

---

## 5. Human Approval Gates
- **Gate Required**: GATE-PHASE (upon Phase 1 completion before starting Phase 2).
- **Gate Rationale**: Transition gate from Phase 1 to Phase 2.

---

## 6. Completion Checkpoint
- **Commit Type**: test
- **Commit Scope**: shell
- **Commit Message**: `test(shell): add headless acceptance tests for Phase 1 user flows`
- **Commit Hash**: 7965530
- **Push Confirmed**: YES
