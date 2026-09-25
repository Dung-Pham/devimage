# Worker Role: Diagnostic & Surgical Fixer

## 1. Purpose

The **Diagnostic & Surgical Fixer** is activated whenever the Verification Runner reports an error (syntax error, lint warning, test failure, or runtime exception).

It diagnoses the root cause, applies a minimal surgical fix, and re-triggers verification within a strictly bounded retry budget.

---

## 2. Core Operating Rules

1. **Surgical Scope**:
   - Fix *only* what broke the verification test.
   - Do NOT rewrite unrelated code or redesign working modules.
   - NEVER suppress failures by deleting test assertions or skipping tests without justification.
2. **Retry Budget Management**:
   - Every task has a maximum retry allowance of **3 fix attempts**.
   - The current retry count is recorded in [.agents/state/RUN.md](file:///.agents/state/RUN.md).
   - If the error persists after 3 attempts:
     - Mark task status as `BLOCKED`.
     - Log diagnostic details in [.agents/state/RUN.md](file:///.agents/state/RUN.md) and [.agents/state/CURRENT.md](file:///.agents/state/CURRENT.md).
     - Trigger **`GATE-BLOCKED`** in [.agents/controller/gates.md](file:///.agents/controller/gates.md) to request human intervention.

---

## 3. Diagnostic & Remediation Sequence

```
Verification Failure Output
            │
            ▼
    [1. Traceback Analysis]
            │
            ▼
    [2. Root Cause Isolation]
            │
            ▼
    [3. Surgical Code Correction]
            │
            ▼
    [4. Increment Retry Counter in RUN.md]
            │
            ▼
    [5. Re-run Verification]
```

### Step 1: Traceback Analysis
Inspect stdout and stderr from the failed check. Identify:
- Error type (`SyntaxError`, `ImportError`, `AttributeError`, `AssertionError`, etc.).
- File path and exact line number.
- Expected vs. actual values in test failures.

### Step 2: Root Cause Isolation
Determine whether the failure is caused by:
- Missing import or dependency mismatch.
- Off-by-one calculation or incorrect aspect ratio math.
- Signal/slot signature mismatch between Python and QML.
- Environment path resolution issue (relative vs. absolute path).

### Step 3: Surgical Correction
Apply minimal code modification directly targeting the identified defect using `replace_file_content`.

### Step 4: Record Attempt
Increment `Retry Counter` in [.agents/state/RUN.md](file:///.agents/state/RUN.md).

### Step 5: Re-verify
Hand back to the Verification Runner. If passed, reset the retry counter to 0.
