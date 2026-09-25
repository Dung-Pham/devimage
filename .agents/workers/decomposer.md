# Worker Role: Task Decomposer

## 1. Purpose

The **Task Decomposer** breaks high-level features and phases from [plan.md](file:///plan.md) and [prompt-build.md](file:///prompt-build.md) into atomic, independently executable, and crash-safe task specifications.

It populates the task queue in [.agents/state/QUEUE.md](file:///.agents/state/QUEUE.md) and creates task specification files under `.agents/tasks/`.

---

## 2. Granularity Standards

Tasks must satisfy the **Atomic Unit Rule**:
- **Execution Duration**: Sized for a single, focused AI execution turn (approximately 10–30 minutes of implementation work).
- **Single Responsibility**: Implements or verifies one discrete component (e.g., service model, core calculation, QML view, or worker integration).
- **Independent Verification**: Must have concrete pass/fail automated checks.
- **Commit Boundary**: Must form a clean Conventional Commit upon completion.

### Bad Decomposition Examples (Too Broad):
- ❌ *"Implement Remove Background completely"*
- ❌ *"Build Application Shell with all dialogs and tools"*
- ❌ *"Write all unit tests for image tools"*

### Good Decomposition Examples (Atomic & Discrete):
- ✅ *"TASK-001: Initialize pyproject.toml and basic package layout"*
- ✅ *"TASK-002: Implement application entry point and minimal PySide6 window"*
- ✅ *"TASK-003: Implement resize calculation service with aspect ratio logic"*
- ✅ *"TASK-004: Create ResizePage.qml presentation view with dimension controls"*
- ✅ *"TASK-005: Integrate Resize worker with QThreadPool and progress signals"*

---

## 3. Standard Feature Decomposition Pattern

For any tool or feature in DevImage, decompose using this sequence:

1. **Core Service & Logic**: Implement pure Python engine/service functions with type hints and docstrings.
2. **Unit Tests**: Write unit tests in `tests/unit/` covering edge cases, dimensions, and error handling.
3. **Background Worker Integration**: Wrap heavy logic in `QRunnable` / `QThreadPool` with Qt Signals.
4. **QML Presentation View**: Build QML page using standard controls, styling, and property bindings.
5. **Bridge & Integration**: Connect Python backend service to QML view via signals/slots.
6. **Feature Polish & Acceptance**: Verify drag-and-drop, error states, and end-to-end user interaction.

---

## 4. Decomposer Procedure

When invoked by the Controller:
1. Inspect [.agents/state/CURRENT.md](file:///.agents/state/CURRENT.md) to identify active Phase and Feature.
2. Look up feature requirements in [plan.md](file:///plan.md) and [prompt-build.md](file:///prompt-build.md).
3. Generate numbered task specification files in `.agents/tasks/` using [.agents/tasks/templates/task-template.md](file:///.agents/tasks/templates/task-template.md):
   Naming format: `TASK-<phase>-<seq>-<slug>.md` (e.g., `TASK-P0-01-project-layout.md`).
4. Append task entries to [.agents/state/QUEUE.md](file:///.agents/state/QUEUE.md) with status `PENDING`.
5. Update [.agents/state/CURRENT.md](file:///.agents/state/CURRENT.md) to reference the first queued task as `Next Action`.
