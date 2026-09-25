# Task Specification: {TASK_ID}

## Metadata
- **Task ID**: `{TASK_ID}`
- **Phase**: {Phase Name}
- **Feature**: {Feature Name}
- **Status**: PENDING
- **Assigned Worker**: Implementer
- **Claimed By Session**: None
- **Lock Lease Seconds**: 300
- **Created**: {YYYY-MM-DD HH:MM}
- **Completed**: 

---

## 1. Objective & Scope
{Concise, unambiguous description of what this task delivers and what it does NOT touch.}

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- `{Reference File 1}`
- `{Reference File 2}`

### Files to Create / Modify
- `{Target File 1}`
- `{Target File 2}`
- `tests/{Target Test File}`

---

## 3. Implementation Steps
1. {Step 1}
2. {Step 2}
3. {Step 3}
4. {Step 4}

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Format Check**: `uv run ruff format --check src/ tests/`
- **Unit & Integration Tests**: `uv run pytest tests/{test_file} -v`
- **Expected Outcome**: {Measurable success criteria}

---

## 5. Human Approval Gates
- **Gate Required**: {None / GATE-PHASE / GATE-DEPS / GATE-MERGE}
- **Gate Rationale**: {Explanation if a gate applies}

---

## 6. Completion Checkpoint
- **Commit Type**: {feat / fix / refactor / test / chore}
- **Commit Scope**: {scope}
- **Commit Message**: `{type}({scope}): {action description}`
- **Commit Hash**: 
- **Push Confirmed**: NO
