# Task Specification: TASK-P0-02 — Application Foundation (Paths, Logging, Settings)

## Metadata
- **Task ID**: `TASK-P0-02-app-foundation`
- **Phase**: Phase 0 — Foundation & Project Setup
- **Feature**: Application Foundation
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 08:40
- **Completed**: 2026-09-25 08:45

---

## 1. Objective & Scope
Implement the core application runtime foundations: `src/devimage/app/paths.py` (cross-platform path resolution for config, cache, and logs), `src/devimage/app/logging.py` (structured logging with file rotation and console output per plan specifications), and `src/devimage/app/settings.py` (typed settings persistence with JSON backend, default settings schema). Add automated unit tests.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Sections 19, 20, 21)
- [.agents/rules/coding.md](file:///.agents/rules/coding.md)

### Files to Create / Modify
- `src/devimage/app/__init__.py`
- `src/devimage/app/paths.py`
- `src/devimage/app/logging.py`
- `src/devimage/app/settings.py`
- `tests/unit/test_paths.py`
- `tests/unit/test_logging.py`
- `tests/unit/test_settings.py`

---

## 3. Implementation Steps
1. Implement `paths.py`: Provide `get_app_dir()`, `get_config_dir()`, `get_cache_dir()`, `get_logs_dir()`, and ensure directories are automatically created.
2. Implement `logging.py`: Provide `setup_logging(level, log_dir)` with console stream handler and file handlers (`logs/app.log`, `logs/errors.log`), adhering to privacy rules (no sensitive data).
3. Implement `settings.py`: Provide `SettingsManager` that loads, validates, modifies, and persists application preferences to `settings.json` in the config directory.
4. Implement unit tests in `tests/unit/` for paths resolution, logging initialization, and settings get/set/save/load.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Test Command**: `uv run pytest tests/unit/test_paths.py tests/unit/test_logging.py tests/unit/test_settings.py -v`
- **Expected Outcome**: 100% test pass rate, clean ruff lint.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: N/A

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: app
- **Commit Message**: `feat(app): implement paths, logging, and settings foundation`
- **Commit Hash**: 245b100
- **Push Confirmed**: YES
