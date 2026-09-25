# DevImage Verification Runner

## 1. Purpose

The **Verification Runner** executes automated verification suites to ensure every code change is syntactically sound, lint-clean, functionally correct, and non-breaking before state transition, commit, or remote push.

---

## 2. Multi-Layer Verification Suite

```
[Layer 1: Static Lint & Syntax] ──> [Layer 2: Unit & Integration Tests] ──> [Layer 3: Smoke / Headless GUI]
```

### Layer 1: Static Linting & Syntax Validation
- **Tool**: `ruff`
- **Commands**:
  ```bash
  ruff check src/ tests/
  ```
- **Criteria**: Zero errors. Any lint violations must be fixed prior to testing.

### Layer 2: Automated Unit & Service Tests
- **Tool**: `pytest`
- **Commands**:
  - Task-targeted test:
    ```bash
    pytest tests/unit/<target_subfolder>/ -v
    ```
  - Full test suite (executed before feature/phase completion):
    ```bash
    pytest tests/ -v
    ```
- **Criteria**: 100% pass rate. Zero failed or erroring tests.

### Layer 3: Headless GUI & QML Smoke Tests
- **Tool**: `pytest-qt` with offscreen platform plugin.
- **Commands**:
  ```bash
  $env:QT_QPA_PLATFORM="offscreen"; pytest tests/test_gui_smoke.py -v
  ```
- **Criteria**:
  - Application initializes without segmentation fault or unhandled exception.
  - QML engine loads components with zero syntax or unresolved property errors.

### Layer 4: Git & State Verification
- **Checks**:
  - `git status -u`: Confirm only intended files are modified.
  - Confirm no credential files, API keys, or large ONNX model binaries are staged.
  - Confirm [.agents/state/CURRENT.md](file:///.agents/state/CURRENT.md) and task specifications reflect actual results.

---

## 3. Verification Report Format

Upon completion of checks, the runner produces a verification summary for the Controller:

```markdown
### Verification Report: [TASK-ID]
- Static Lint (Ruff): PASS
- Unit Tests (Pytest): PASS (X passed, 0 failed)
- GUI Smoke Test: PASS / SKIPPED
- Git Working Tree: CLEAN (Intended files only)
- Status: READY FOR COMMIT
```
