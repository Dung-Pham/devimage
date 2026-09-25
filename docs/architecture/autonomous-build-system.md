# DevImage Autonomous Build System Architecture

## 1. Executive Summary

The **DevImage Autonomous Build System** provides deterministic, repository-driven orchestration for developing the DevImage application. It operates entirely within the Git repository and Antigravity execution environment, requiring zero external server orchestration, containers, databases, or cloud infrastructure.

Durable progress, crash recovery, and context efficiency are anchored in Git commits, push verifications, and structured state files under `.agents/`.

---

## 2. Directory Layout & Roles

```
.agents/
├── controller/
│   ├── BUILD_CONTROLLER.md     # 12-step autonomous loop algorithm
│   └── gates.md                # Human approval gate conditions & protocols
├── workers/
│   ├── decomposer.md           # Breaks phases/features into atomic task specs
│   ├── implementer.md          # Executes single task with context isolation
│   └── fixer.md                # Diagnoses & applies surgical fixes (max 3 retries)
├── verification/
│   ├── verification-runner.md  # Multi-layer test/lint/smoke runner
│   └── acceptance-matrix.md    # Definition of Done across milestones
├── rules/
│   ├── agent-continuity.md     # Startup inspection & recovery sequence
│   ├── autonomous-execution.md # Autonomous loop governance invariants
│   ├── coding.md               # Python-first, QML separation, non-blocking UI
│   └── git.md                  # Conventional commits & remote push verification
├── state/
│   ├── CURRENT.md              # Real-time project pointer (20-50 lines)
│   ├── QUEUE.md                # Prioritized active & pending task queue
│   ├── RUN.md                  # Autonomous run session state & retry counter
│   ├── phases/                 # Archived phase completion summaries
│   └── features/               # Feature progress checkpoints
└── tasks/
    ├── templates/
    │   └── task-template.md    # Standard task specification format
    └── TASK-*.md               # Concrete, independently executable tasks
```

---

## 3. Core Operational Lifecycles

### 3.1. Task Lifecycle
```
[Phase Requirement] ──> [Task Decomposer] ──> [Created in .agents/tasks/]
                                                       │
                                                       ▼
[State: COMPLETED] <── [Verification Passes] <── [State: IN_PROGRESS]
        │
        ▼
[Commit & Push] ──> [Queue Advances] ──> [Next Task]
```
1. **Decomposition**: Tasks are created using `task-template.md`, tagged with explicit `Target Context` (files to touch) and verification commands.
2. **Execution**: Implementer loads *only* the designated context files, implements code, and passes to the Verification Runner.
3. **Verification**: Linting (`ruff`), unit tests (`pytest`), and headless GUI checks must pass with zero errors.
4. **Self-Healing**: Up to 3 surgical fix attempts on failure; otherwise flagged `BLOCKED`.
5. **Finalization**: Conventional Commit and immediate `git push` to origin.

### 3.2. Interruption Recovery Lifecycle
If the session crashes, power is lost, or the user enters a fresh session with "Continue":
1. Read `.agents/state/CURRENT.md` and `.agents/state/RUN.md`.
2. Inspect Git working tree (`git status`) to protect uncommitted changes.
3. If an in-flight task was interrupted, test and complete it before proceeding.
4. Re-synchronize with remote branch.
5. Resume directly from the documented `Next Action` in `CURRENT.md`.

### 3.3. Git & Backup Lifecycle
- All development takes place on dedicated feature branches (`feature/<name>`).
- Work is committed after each completed atomic task using Conventional Commits.
- Every commit is pushed immediately to GitHub.
- Work is not marked complete until `git status` verifies the remote push.

### 3.4. Human Approval Gates
Autonomous loops automatically halt and alert the user upon:
- Major Phase completion (e.g., Phase 0 -> Phase 1).
- Proposed external dependencies outside the pre-approved stack.
- Feature branch merges into `main`.
- Release version tagging.
- Unresolved blockers after 3 failed fix retries.

---

## 4. Starting Autonomous Execution

To start or resume autonomous execution:
1. Ensure the working tree is clean on the active feature branch.
2. Direct the agent to follow [.agents/controller/BUILD_CONTROLLER.md](file:///.agents/controller/BUILD_CONTROLLER.md).
3. The controller will read state, decompose pending features into `.agents/tasks/`, populate `.agents/state/QUEUE.md`, and execute tasks sequentially with full verification and remote backup.
