# DevImage Autonomous Build Controller

## 1. Overview & Core Mission

The **Autonomous Build Controller** governs the end-to-end execution loop for DevImage. It operates directly within the repository environment, ensuring deterministic, crash-safe, and self-verifying implementation of features defined in [plan.md](file:///plan.md) and [prompt-build.md](file:///prompt-build.md).

The Controller relies exclusively on repository state (Git history, state files, and task specifications). It maintains context efficiency through strict task isolation and halts only at designated **Human Approval Gates** or unresolved blockers.

---

## 2. The 12-Step Controller Execution Loop

For each autonomous execution turn, the Controller follows this strict 12-step cycle:

```
[1. Read State] ──> [2. Git Inspection] ──> [3. Interruption Check]
       │
       ▼
[4. Queue Select / Decompose] ──> [5. Human Gate Check]
       │                                     │ (if gate triggered: HALT & REPORT)
       ▼                                     ▼
[6. Context Isolation] ──> [7. Worker Implement] ──> [8. Verification Runner]
                                                            │
                     ┌──────────────────────────────────────┘
                     ▼
           [Passed / Failed?]
              ├── Failed ──> [9. Surgical Fix Loop] (Max 3 retries -> BLOCKED)
              │
              └── Passed ──> [10. State Update]
                                   │
                                   ▼
                             [11. Commit & Push & Remote Verify]
                                   │
                                   ▼
                             [12. Loop / Advance Queue]
```

### Step 1: Read Project State
Read [.agents/state/CURRENT.md](file:///.agents/state/CURRENT.md), [.agents/state/RUN.md](file:///.agents/state/RUN.md), and [.agents/state/QUEUE.md](file:///.agents/state/QUEUE.md). Determine active phase, current feature, running mode, and queue contents.

### Step 2: Git Environment Inspection
Execute `git status -u`, verify active branch (`git branch --show-current`), and inspect recent commits (`git log -n 5 --oneline`). Confirm remote synchronization with GitHub.

### Step 3: Interruption & Crash Recovery
If uncommitted changes exist from a prior interrupted session:
- Run `git diff` to identify modified files.
- Inspect [.agents/state/RUN.md](file:///.agents/state/RUN.md) to locate the in-flight task ID.
- Do NOT run destructive reset commands.
- Resume verification or complete the in-flight task before starting any new task.

### Step 4: Queue Management & Task Selection
Inspect [.agents/state/QUEUE.md](file:///.agents/state/QUEUE.md):
- If an `IN_PROGRESS` task exists, resume it.
- If no active task exists, select the first `PENDING` task in the queue.
- If the queue is empty, invoke [.agents/workers/decomposer.md](file:///.agents/workers/decomposer.md) to decompose the current feature or phase into atomic task files under `.agents/tasks/`.

### Step 5: Human Approval Gate Check
Check whether the target task or impending transition matches any condition in [.agents/controller/gates.md](file:///.agents/controller/gates.md):
- Phase completion transition (e.g., Phase 0 -> Phase 1).
- Unplanned external dependency addition.
- Destructive filesystem or Git operations.
- Merging feature branch into `main`.
- Production release tagging.
If a gate is triggered, mark task `HUMAN_GATE`, update state, and halt execution to await human approval.

### Step 6: Task Context Isolation
Load the selected task specification file (e.g., `.agents/tasks/TASK-xxx.md`). Read **only** the files declared in the task's `Target Context` section. Avoid loading unrelated documentation or code.

### Step 7: Worker Implementation
Dispatch task requirements to [.agents/workers/implementer.md](file:///.agents/workers/implementer.md). The Implementer writes or modifies code adhering strictly to [.agents/rules/coding.md](file:///.agents/rules/coding.md) (Python-first, QML presentation separation, non-blocking threading).

### Step 8: Verification Runner
Run automated verification steps specified in [.agents/verification/verification-runner.md](file:///.agents/verification/verification-runner.md):
- Python syntax and linting checks (`ruff check`).
- Type and structure validation.
- Unit and integration tests (`pytest`).
- Smoke / headless GUI initialization tests if applicable.

### Step 9: Self-Healing & Fix Loop
If verification fails:
- Dispatch failure logs to [.agents/workers/fixer.md](file:///.agents/workers/fixer.md).
- Apply targeted surgical fixes without expanding scope.
- Re-run verification.
- Enforce retry budget (maximum 3 attempts). If still failing, mark task as `BLOCKED`, record diagnostic notes, and pause.

### Step 10: State Update
Upon successful verification:
- Update task specification status to `COMPLETED`.
- Update [.agents/state/QUEUE.md](file:///.agents/state/QUEUE.md) marking the task `COMPLETED`.
- Update [.agents/state/CURRENT.md](file:///.agents/state/CURRENT.md) (active pointer, completed items, next concrete action).
- Update [.agents/state/RUN.md](file:///.agents/state/RUN.md) (execution timestamps, step counter).

### Step 11: Git Commit, Push & Remote Verification
Follow [.agents/rules/git.md](file:///.agents/rules/git.md):
- Stage intended source and state files: `git add <files>`.
- Commit with Conventional Commit: `git commit -m "<type>(<scope>): <action>"`.
- Push immediately to remote: `git push origin <branch>`.
- Verify remote synchronization: `git status`.

### Step 12: Loop Continuation / Advance Queue
Inspect [.agents/state/QUEUE.md](file:///.agents/state/QUEUE.md) for remaining `PENDING` tasks. If more tasks exist, seamlessly advance to Step 3 for the next task. If all tasks for the current feature are complete, mark feature complete and transition to the next feature or trigger phase completion gate.

---

## 3. Operational Invariants

1. **One Task at a Time**: Never execute multiple queue items concurrently.
2. **Crash-Safe Checkpoints**: Every task completion ends with a verified Git push.
3. **No Phantom Progress**: State files only declare tasks completed when verification passes and commits are pushed.
4. **Zero Out-of-Scope Architecture**: The Controller never introduces servers, containers, databases, or cloud infrastructure.
