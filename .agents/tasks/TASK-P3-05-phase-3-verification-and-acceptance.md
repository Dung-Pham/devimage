# Task Specification: TASK-P3-05-phase-3-verification-and-acceptance

## Metadata
- **Task ID**: `TASK-P3-05-phase-3-verification-and-acceptance`
- **Phase**: Phase 3 — Developer Tools
- **Feature**: Phase 3 Verification & Acceptance
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Claimed By Session**: session-20260925-phase3
- **Lock Lease Seconds**: 300
- **Created**: 2026-09-25 15:30:00 +07:00
- **Completed**: 2026-09-25 16:32:00 +07:00

---

## 1. Objective & Scope
Perform end-to-end integration, GUI smoke, and acceptance verification for all Developer Tools in Phase 3 (Inspector, Color Picker, Batch Rename, and Copy Path). Verify that all 4 tools load cleanly inside the application shell, handle various image formats, maintain non-blocking UI, and provide reliable developer utilities.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- `src/devimage/tools/inspector/controller.py`
- `src/devimage/tools/color_picker/controller.py`
- `src/devimage/tools/rename/controller.py`
- `src/devimage/tools/copy_path/controller.py`
- `src/devimage/ui/qml/AppShell.qml`

### Files to Create / Modify
- `tests/test_developer_tools.py`
- `.agents/state/CURRENT.md`
- `.agents/state/QUEUE.md`
- `.agents/state/RUN.md`
- `.agents/state/V2_RUN.json`

---

## 3. Implementation Steps
1. Create `tests/test_developer_tools.py`:
   - Acceptance tests for Inspector (metadata, EXIF, JSON export).
   - Acceptance tests for Color Picker (RGB, HEX, HSL, CSS variable export).
   - Acceptance tests for Batch Rename (pattern substitution, conflict resolution).
   - Acceptance tests for Copy Path (path formats, Markdown/HTML snippets).
   - Headless QML interaction tests verifying navigation to all Phase 3 tools.
2. Run full verification suite (`ruff check`, `ruff format --check`, `pytest`).
3. Update state checkpoints and prepare for human approval gate `GATE-PHASE`.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Format Check**: `uv run ruff format --check src/ tests/`
- **Test Suite**: `uv run pytest` (100% passing across all suites)

---

## 5. Human Approval Gates
- **Gate Required**: GATE-PHASE
- **Gate Rationale**: Transition gate from Phase 3 (Developer Tools) to Phase 4 (OCR / Remove Background / AI Tools).

---

## 6. Completion Checkpoint
- **Commit Type**: test
- **Commit Scope**: devtools
- **Commit Message**: `test(devtools): add comprehensive acceptance tests for Phase 3 developer tools`
- **Commit Hash**: 
- **Push Confirmed**: NO
