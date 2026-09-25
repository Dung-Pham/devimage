# Task Specification: [TASK-ID] — [Task Title]

## Metadata
- **Task ID**: `TASK-<PHASE>-<SEQ>-<SLUG>`
- **Phase**: [e.g. Phase 0 — Foundation]
- **Feature**: [e.g. Project Setup]
- **Status**: PENDING  <!-- PENDING | IN_PROGRESS | VERIFYING | COMPLETED | BLOCKED | HUMAN_GATE -->
- **Assigned Worker**: Implementer
- **Created**: YYYY-MM-DD HH:MM
- **Completed**: <!-- Filled upon completion -->

---

## 1. Objective & Scope
<!-- Concise 1-3 sentence description of exactly what this task implements. -->

---

## 2. Target Context (Isolation Boundary)
<!-- Strictly list files to read or modify. Agents must read ONLY these files. -->
### Read-Only References
- [e.g. plan.md](file:///plan.md)
- [e.g. .agents/rules/coding.md](file:///.agents/rules/coding.md)

### Files to Create / Modify
- `src/devimage/...`
- `tests/unit/...`

---

## 3. Implementation Steps
1. [Step 1: Description]
2. [Step 2: Description]
3. [Step 3: Description]

---

## 4. Verification Requirements
- **Lint Check**: `ruff check <paths>`
- **Test Command**: `pytest <test_file> -v`
- **Expected Outcome**: All tests pass with zero errors.

---

## 5. Human Approval Gates
- **Gate Required**: None <!-- None | GATE-PHASE | GATE-DEPS | GATE-MERGE | GATE-EXTERNAL -->
- **Gate Rationale**: <!-- If applicable -->

---

## 6. Completion Checkpoint
- **Commit Type**: [feat | fix | test | chore]
- **Commit Scope**: [<scope>]
- **Commit Message**: `<type>(<scope>): <summary>`
- **Commit Hash**: <!-- Filled upon commit -->
- **Push Confirmed**: <!-- YES / NO -->
