# Deterministic Crash Recovery Protocol

## 1. Core Mission & Invariants

The **Crash Recovery Protocol** defines deterministic recovery procedures for all unexpected agent interruptions, disconnections, and partial failures.

### Non-Destructive Invariant
- **NEVER** run `git reset --hard`, `git clean -fd`, or `git checkout .`.
- **NEVER** discard uncommitted code without human review.
- The protocol must resolve state ambiguity using Git as the primary factual ledger.

---

## 2. Failure Scenarios & Triage Matrix

### Scenario A: Crash Before Commit (Dirty Working Tree)
- **Symptom**: `git status` shows modified/untracked files; no commit exists for the active task.
- **Triage**:
  1. Run `git diff` and compare changed files against the `Target Context` in `.agents/tasks/TASK-xxx.md`.
  2. If the edits match the active task, run `uv run ruff check` and `uv run pytest`.
  3. If verification passes, proceed directly to Step 10 (State Update) and Step 11 (Commit & Push).
  4. If edits are partial/broken and cannot be fixed within budget, stop and output `RECOVER_UNCOMMITTED_WORK` for user review.

### Scenario B: Commit Exists but Push Failed
- **Symptom**: `git status` shows branch is ahead of remote by 1 or more commits; `git log -n 1` shows the completed task commit.
- **Triage**:
  1. Inspect latest commit message to confirm task ID and Conventional Commit format.
  2. Run `git push origin <branch>`.
  3. Verify remote tracking shows branch is up-to-date with `origin/<branch>`.
  4. Advance state pointer in `CURRENT.md` and release task lock.

### Scenario C: Push Succeeded but State Update Failed
- **Symptom**: Remote has the task commit, but `CURRENT.md` or `QUEUE.md` still lists the task as `IN_PROGRESS` or `PENDING`.
- **Triage**:
  1. Treat pushed commit as ground truth.
  2. Mark task `COMPLETED` in `QUEUE.md` and task specification file with commit hash.
  3. Update `CURRENT.md` pointing to the next task.
  4. Commit state synchronization: `chore(agent): synchronize state for TASK-xxx`.
  5. Push to remote.

### Scenario D: State says COMPLETED but Git Has No Evidence
- **Symptom**: `CURRENT.md` or `QUEUE.md` claims task is done, but neither local git log nor remote contains the commit.
- **Triage**:
  1. Do NOT assume task is complete.
  2. Revert task status in `QUEUE.md` to `PENDING` or `BLOCKED`.
  3. Output `STOP_AND_REPORT` alerting user of missing commit evidence.

### Scenario E: Duplicate Session Task Claims
- **Symptom**: Two active agent sessions attempt to claim the same task ID or have active locks simultaneously.
- **Triage**:
  1. Do not arbitrarily choose a winner.
  2. Both sessions must halt immediately and output `STOP_AND_REPORT`.
  3. Await user clarification or manual lock release.

### Scenario F: Stale Session Detection & Takeover
- **Symptom**: Lock file exists, but `last_heartbeat_at` is older than `lease_seconds` (> 300s).
- **Triage**: Follow [.agents/recovery/stale-session-policy.md](file:///.agents/recovery/stale-session-policy.md).
