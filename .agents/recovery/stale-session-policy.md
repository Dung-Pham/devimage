# Stale Session Detection and Takeover Policy

## 1. Definition of a Stale Session

An agent session is classified as a **Stale Candidate** if and only if:
1. An active task lock file exists in `.agents/locks/runtime/active_task.lock`.
2. The current UTC timestamp exceeds `last_heartbeat_at + lease_seconds`.
3. The lock status is still marked `ACTIVE`.

---

## 2. Three-Point Stale Verification

Before an incoming session may declare a stale session dead and take over ownership, it must verify:

1. **Process Liveness**:
   - Check if the recorded `session_id` corresponds to any currently active subagent or background task.
   - If a background process or active runner is confirmed alive, the session is NOT stale. Extend lease observation window.
2. **Git Activity Silence**:
   - Inspect `git status` and file modification times.
   - If no repository files have been written within the last `lease_seconds`, file activity is confirmed silent.
3. **Remote Push Verification**:
   - Verify that no in-flight push or rebase is pending.

---

## 3. Takeover Procedure

Once the three points above are confirmed:
1. Update old lock status in memory to `STALE_OVERTAKEN`.
2. Append takeover event to [.agents/handoff/SESSION_REGISTRY.md](file:///.agents/handoff/SESSION_REGISTRY.md):
   `session-xxx overtook stale session-yyy on TASK-zzz at YYYY-MM-DD HH:MM:SS`.
3. Overwrite `.agents/locks/runtime/active_task.lock` with the new session ID and reset heartbeat timestamp.
4. Execute [CRASH_RECOVERY.md](file:///.agents/recovery/CRASH_RECOVERY.md) to reconcile any uncommitted work from the old session.
5. Resume task execution.
