# Task Specification: TASK-P3-04-copy-path-tool

## Metadata
- **Task ID**: `TASK-P3-04-copy-path-tool`
- **Phase**: Phase 3 — Developer Tools
- **Feature**: Copy Path
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Claimed By Session**: session-20260925-phase3
- **Lock Lease Seconds**: 300
- **Created**: 2026-09-25 15:30:00 +07:00
- **Completed**: 2026-09-25 16:26:00 +07:00

---

## 1. Objective & Scope
Implement the pure-Python `PathService`, PySide6 `CopyPathController` bridge, and QML view `CopyPathTool.qml` to parse, format, and copy file paths in various developer formats (Windows, POSIX, file:// URI, relative path, HTML <img> tag, Markdown ![image](), CSS url(), and base64 data URI), plus revealing in Windows Explorer.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- `src/devimage/ui/qml/tools/ToolShell.qml`
- `src/devimage/app/paths.py`

### Files to Create / Modify
- `src/devimage/tools/copy_path/__init__.py`
- `src/devimage/tools/copy_path/service.py`
- `src/devimage/tools/copy_path/controller.py`
- `src/devimage/ui/qml/tools/CopyPathTool.qml`
- `src/devimage/app/application.py`
- `src/devimage/ui/qml/tools/ToolShell.qml`
- `tests/unit/test_copy_path_tool.py`

---

## 3. Implementation Steps
1. Create `src/devimage/tools/copy_path/service.py`:
   - Compute: Windows absolute path, POSIX forward-slash path, file URI, relative path to current directory, HTML snippet, Markdown snippet, CSS snippet, base64 data URI.
   - Reveal in Explorer helper (`explorer /select,<path>`).
2. Create `src/devimage/tools/copy_path/controller.py`:
   - Expose properties for all formatted snippets.
   - Provide copy slots and show toast notifications upon copy.
3. Create `src/devimage/ui/qml/tools/CopyPathTool.qml`:
   - Card list of formatted path variants with instant copy buttons and Explorer reveal button.
4. Integrate with `ToolShell.qml` and `application.py`.
5. Add unit tests in `tests/unit/test_copy_path_tool.py`.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Format Check**: `uv run ruff format --check src/ tests/`
- **Unit Tests**: `uv run pytest tests/unit/test_copy_path_tool.py -v`

---

## 5. Human Approval Gates
- **Gate Required**: None

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: copy-path
- **Commit Message**: `feat(copy-path): implement developer path and snippet formatting service, controller, and QML view`
- **Commit Hash**: e741742
- **Push Confirmed**: YES
