# Task Specification: TASK-P2-06 — Phase 2 Acceptance Verification and Transition Gate

## Metadata
- **Task ID**: `TASK-P2-06-phase-2-verification-and-acceptance`
- **Phase**: Phase 2 — Core Image Tools
- **Feature**: Phase 2 Acceptance Verification
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 13:45
- **Completed**: 2026-09-25 15:00

---

## 1. Objective & Scope
Perform comprehensive integration and acceptance testing for all four Phase 2 Core Image Tools (Resize, Compress, Convert, Crop). Verify non-blocking async execution, headless UI instantiations, file generation, error boundary handling, and full compliance with plan.md requirements. Trigger GATE-PHASE-2 upon clearance.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Phase MVP, Sections 2-5)
- [.agents/controller/gates.md](file:///.agents/controller/gates.md)

### Files to Create / Modify
- `tests/test_core_image_tools.py`
- `.agents/state/CURRENT.md`
- `.agents/state/RUN.md`
- `.agents/state/QUEUE.md`

---

## 3. Implementation Steps
1. Create `tests/test_core_image_tools.py` executing headless user journeys for Resize, Compress, Convert, and Crop.
2. Verify all operations run asynchronously without hanging the Qt event loop.
3. Validate output image file integrity across various input types (PNG with alpha, JPEG, WebP).
4. Run full linter (`ruff check src/ tests/`) and entire test suite (`pytest`).
5. Prepare Phase 2 completion summary and gate report for GATE-PHASE-2.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Full Test Suite**: `uv run pytest tests/ -v`
- **Expected Outcome**: 100% test pass rate across all unit and integration tests.

---

## 5. Human Approval Gates
- **Gate Required**: GATE-PHASE
- **Gate Rationale**: Formal phase gate transitioning from Phase 2 (Core Image Tools) to Phase 3 (Developer Tools: Inspector, Color Picker, Rename, Copy Path).

---

## 6. Completion Checkpoint
- **Commit Type**: test
- **Commit Scope**: tools
- **Commit Message**: `test(tools): add comprehensive acceptance tests for Phase 2 core image tools`
- **Commit Hash**: 88f2cc9
- **Push Confirmed**: YES
