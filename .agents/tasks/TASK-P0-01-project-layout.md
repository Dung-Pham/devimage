# Task Specification: TASK-P0-01 — Project Layout & Environment Setup

## Metadata
- **Task ID**: `TASK-P0-01-project-layout`
- **Phase**: Phase 0 — Foundation & Project Setup
- **Feature**: Project Layout & Build Configuration
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 08:40
- **Completed**: 2026-09-25 08:43

---

## 1. Objective & Scope
Initialize the root `.gitignore`, `pyproject.toml` with packaging configuration and tool configurations (ruff, pytest), set up the Python virtual environment with core dependencies (`PySide6`, `pytest`, `pytest-qt`, `ruff`), and establish standard package directory layout.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Sections 21, 35)
- [prompt-build.md](file:///prompt-build.md) (Section 5)
- [.agents/rules/coding.md](file:///.agents/rules/coding.md)

### Files to Create / Modify
- `.gitignore`
- `pyproject.toml`
- `README.md`
- `src/devimage/__init__.py`
- `tests/__init__.py`
- `tests/unit/__init__.py`

---

## 3. Implementation Steps
1. Create comprehensive `.gitignore` for Python, PySide6/Qt (cache, `__pycache__`, `.venv`, `.pytest_cache`, `logs/`, build artifacts).
2. Create `pyproject.toml` using `hatchling` or `setuptools` build backend, defining metadata, dependencies (`PySide6>=6.8.0`, `ruff`, `pytest`, `pytest-qt`), and tool configs for `ruff` and `pytest`.
3. Create project skeleton directory tree under `src/devimage/` and `tests/`.
4. Create `.venv` using `uv venv` and install the package and development dependencies.

---

## 4. Verification Requirements
- **Environment Check**: `uv run python -c "import PySide6; print(PySide6.__version__)"`
- **Lint Check**: `uv run ruff check src/ tests/`
- **Test Command**: `uv run pytest tests/`
- **Expected Outcome**: Dependencies installed, environment verified, ruff passes with zero errors.

---

## 5. Human Approval Gates
- **Gate Required**: None (all dependencies in approved core stack).
- **Gate Rationale**: N/A

---

## 6. Completion Checkpoint
- **Commit Type**: chore
- **Commit Scope**: foundation
- **Commit Message**: `chore(foundation): setup project layout and environment`
- **Commit Hash**:
- **Push Confirmed**: NO
