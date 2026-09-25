Create a new Git branch for the **Autonomous Build System v2** migration:

```text
feature/autonomous-build-v2
```

Before creating the branch:

1. Check the current branch.
2. Run `git status`.
3. Confirm there are no uncommitted changes.
4. Do NOT modify, reset, stash, clean, or discard any existing work.
5. Do NOT modify any DevImage source code.
6. Do NOT modify `.agents/state/QUEUE.md`, `CURRENT.md`, or `RUN.md`.
7. Do NOT interfere with the currently active Phase 2 task.

Then:

1. Create and checkout:
   `feature/autonomous-build-v2`
2. Set the branch to track the appropriate remote branch only if safe and necessary.
3. Push the new branch to GitHub.
4. Verify:

   * current branch is `feature/autonomous-build-v2`
   * working tree is clean
   * remote tracking is correct
   * push succeeded

Do not implement Autonomous Build System v2 yet.

This step is ONLY for safely creating and pushing the dedicated v2 branch.

Finally, report:

* previous branch
* new branch
* Git status
* remote tracking status
* push result
* latest commit hash

If any uncommitted changes, active task conflict, or other safety issue is detected, STOP and report it instead of modifying anything.



Implement **Autonomous Build System v2** for DevImage, but do not break or replace the currently working v1 system.

## Primary objective

Add:

* Session Handoff
* Resume Protocol
* Task Claim/Lock
* Crash Recovery
* Stale Session Detection
* Safe takeover by a new conversation
* Machine-readable runtime state

The existing v1 system must remain compatible and usable throughout the migration.

## Mandatory safety rules

1. Do not delete, rename, or replace existing v1 files.
2. Do not change the current format of:

   * `.agents/state/CURRENT.md`
   * `.agents/state/QUEUE.md`
   * `.agents/state/RUN.md`
   * `.agents/controller/BUILD_CONTROLLER.md`
   * existing task files
3. Do not modify DevImage application source code.
4. Do not reset, clean, force-push, or discard uncommitted work.
5. Do not mark a task completed without verification, commit, push, and remote verification.
6. Do not automatically advance across a `GATE-*`.
7. Do not use UI automation or unofficial hacks to create Antigravity conversations.
8. Do not run destructive migration steps automatically.
9. Preserve all existing v1 behavior.
10. If any conflict or ambiguity is found, stop and report `GATE-BLOCKED`.

## Required migration strategy

Use additive migration:

### Stage 0 — Audit

Inspect and document:

* existing `.agents/` structure
* `AGENTS.md`
* `PROJECT_MAP.md`
* `CURRENT.md`
* `QUEUE.md`
* `RUN.md`
* `BUILD_CONTROLLER.md`
* current Git branch
* current Git status
* recent commits

Do not modify active task state during this stage.

### Stage 1 — Add v2 infrastructure

Create, without replacing v1:

* `.agents/controller/BUILD_CONTROLLER_V2.md`
* `.agents/controller/migration.md`
* `.agents/workers/session-bootstrap.md`
* `.agents/handoff/SESSION_HANDOFF.md`
* `.agents/handoff/RESUME_PROTOCOL.md`
* `.agents/handoff/SESSION_REGISTRY.md`
* `.agents/handoff/handoff-template.md`
* `.agents/locks/LOCK_PROTOCOL.md`
* `.agents/recovery/CRASH_RECOVERY.md`
* `.agents/recovery/stale-session-policy.md`
* `.agents/rules/v2-safety-rules.md`
* `.agents/state/V2_RUN.json`
* `.agents/state/SESSION.json`
* `.agents/state/SESSION_REGISTRY.md`
* `.agents/tasks/templates/task-template-v2.md`

Use machine-readable JSON for runtime state and Markdown for human-readable documentation.

### Stage 2 — Compatibility layer

Define how v2 reads v1 state without changing its format.

The compatibility priority must be:

1. source code and verified tests
2. Git history
3. v1 state files
4. v2 runtime state
5. task documentation

Do not allow v2 to contradict verified Git history.

### Stage 3 — Observe-only mode

Initialize v2 in:

```text
OBSERVE_ONLY
```

In this mode v2 may:

* inspect state
* identify active task
* identify possible stale sessions
* report recovery recommendations

It must not:

* claim locks
* change queue status
* modify task status
* advance phases
* modify application code

### Stage 4 — Resume-only mode

Add a safe resume protocol for a new conversation:

1. Read `AGENTS.md`.
2. Read v1 state.
3. Read v2 state.
4. Check Git branch and status.
5. Inspect active lock.
6. Detect stale session.
7. Inspect uncommitted changes.
8. Determine whether the active task is safely resumable.
9. Continue only if ownership can be safely claimed.
10. Otherwise stop with a structured report.

### Stage 5 — Task claim/lock

Implement a lease-based task lock using a machine-readable file.

The lock must contain:

* task_id
* session_id
* branch
* claimed_at
* last_heartbeat_at
* lease_seconds
* status

Do not automatically delete expired locks. Mark them as stale candidates and require recovery checks before takeover.

### Stage 6 — Crash recovery

Document and implement recovery behavior for:

* crash before commit
* commit exists but push did not complete
* push completed but state was not synchronized
* state says completed but Git evidence is missing
* duplicate session claim
* uncommitted changes from a previous session
* stale heartbeat
* interrupted verification

Never use destructive Git recovery.

### Stage 7 — Validation

Create tests or deterministic validation procedures for:

* new-session resume
* valid lock
* expired lease
* stale session
* duplicate claim
* crash before commit
* crash after commit
* commit without push
* push without state synchronization
* state/Git mismatch
* safe lock release
* compatibility with v1 files

### Stage 8 — Git checkpoint

Before committing:

* show changed files
* show that no existing v1 file was deleted
* show that no DevImage source file was modified
* run relevant validation
* inspect `git diff --check`

Then create a Conventional Commit and push it to a dedicated branch:

```text
feature/autonomous-build-v2
```

Do not merge into the current feature branch automatically.

## Required final report

Report:

1. v1 files preserved
2. v2 files created
3. migration stage completed
4. current mode
5. active task and session status
6. lock behavior
7. crash recovery behavior
8. validation results
9. commit hash
10. push verification
11. next safe migration step

If the current task is active or uncommitted work is detected, do not interfere with it. Stop after the audit and report the safest next action.
