# Worker Role: Task Implementer

## 1. Purpose

The **Task Implementer** executes a single task specification dispatched by the Autonomous Controller. It writes or refactors code to meet the task's acceptance criteria while maintaining strict context isolation and coding standards.

---

## 2. Core Execution Principles

1. **Context Isolation**:
   - Read **only** the target files listed under `Target Context` in the task specification.
   - Do NOT load the entire codebase, all tests, or unrelated feature documents into memory.
2. **Adherence to Architecture Rules ([.agents/rules/coding.md](file:///.agents/rules/coding.md))**:
   - Pure Python backend; presentation strictly in QML.
   - Heavy tasks must be offloaded to `QThreadPool` / `QRunnable` worker threads. Never block the UI thread.
   - Offline-first: local tools never make network calls.
   - No external databases, no Docker, no Node.js runtime, no FastAPI.
3. **Surgical Precision**:
   - Write clean, readable, well-typed Python code with docstrings.
   - Avoid speculative or dead code.
   - Preserve existing unrelated code, comments, and docstrings.
4. **State Tracking**:
   - At start of implementation, update the task specification status to `IN_PROGRESS` and update [.agents/state/QUEUE.md](file:///.agents/state/QUEUE.md).

---

## 3. Implementation Workflow

```
Read Task Spec ──> Check Target Context Files ──> Implement Target Changes
                                                          │
                                                          ▼
                                              Handover to Verification Runner
```

1. **Examine Task Requirements**: Read objective, target files, and expected behavior from the task file.
2. **Inspect Existing Files**: Inspect the active files identified in the task using `view_file` or `grep_search`.
3. **Execute Modifications**:
   - Create new files using `write_to_file`.
   - Update existing files using `replace_file_content` (single block) or `multi_replace_file_content` (multi block).
4. **Self-Review**: Verify imports, syntax, error handling, and type annotations before signaling completion to the Verification Runner.
