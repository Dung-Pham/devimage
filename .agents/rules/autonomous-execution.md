# Autonomous Execution & Build System Governance Rule

## 1. Core Mandate

When operating in autonomous mode, the AI agent must act strictly through the **DevImage Autonomous Build Controller** defined in [.agents/controller/BUILD_CONTROLLER.md](file:///.agents/controller/BUILD_CONTROLLER.md).

No rogue changes, out-of-scope implementations, or arbitrary architectural additions are permitted.

---

## 2. Fundamental Autonomous Invariants

1. **One Task per Cycle**:
   - The agent executes exactly one atomic task from [.agents/state/QUEUE.md](file:///.agents/state/QUEUE.md) per cycle.
   - Never implement ahead of the queue or combine multiple features into an uncommitted batch.
2. **Context Isolation**:
   - Limit file loading strictly to the files listed in the task specification's `Target Context`.
   - Do not load the complete documentation tree or entire codebase.
3. **Commit & Push Discipline**:
   - Every completed task MUST result in an immediate Conventional Commit and `git push`.
   - Work is NEVER considered done until `git status` confirms the remote branch is in sync.
4. **Human Approval Gates**:
   - When encountering any condition in [.agents/controller/gates.md](file:///.agents/controller/gates.md), the agent MUST halt execution, output the structured gate alert, and await user instructions.
   - Never automatically bypass or simulate human sign-off for phase completion, third-party dependency additions, or git merges.
5. **Bounded Self-Healing**:
   - On verification failures, invoke [.agents/workers/fixer.md](file:///.agents/workers/fixer.md) for up to 3 surgical fix attempts.
   - If the issue cannot be resolved within 3 attempts, record diagnostic notes, mark the task `BLOCKED`, and trigger `GATE-BLOCKED`.
6. **No External Stack Invasions**:
   - Do NOT introduce Docker, Node.js, Electron, FastAPI, databases, or cloud servers.
   - DevImage is a pure Python 3.13 + PySide6/QML offline-first desktop toolbox.
