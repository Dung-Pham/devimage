# Lease-Based Task Locking Protocol

## 1. Purpose

The **Task Lock Protocol** guarantees mutual exclusion across AI agent sessions working in the repository. It prevents race conditions, conflicting file edits, or duplicate commits when multiple sessions are spawned or when an interrupted session is being resumed.

---

## 2. Lock Storage & Git Hygiene

- **Lock File Location**: `.agents/locks/runtime/active_task.lock`
- **Git Exclusion**: The directory `.agents/locks/runtime/` is strictly ephemeral and excluded from Git via `.gitignore`. Machine-specific runtime locks MUST NEVER be committed to Git.
- **Durable Ground Truth**: Git history and `CURRENT.md` supersede any lock state in case of conflicting claims.

---

## 3. Lock Schema (JSON)

```json
{
  "task_id": "TASK-P3-01-image-inspector",
  "session_id": "session-20260925-151020-abc123",
  "branch": "feature/developer-tools",
  "claimed_at": "2026-09-25T15:10:20+07:00",
  "last_heartbeat_at": "2026-09-25T15:12:00+07:00",
  "lease_seconds": 300,
  "status": "ACTIVE"
}
```

### Valid Lock Statuses
- `ACTIVE`: The lock is held by a healthy session whose heartbeat is recent (`now - last_heartbeat_at <= lease_seconds`).
- `STALE_CANDIDATE`: Heartbeat expired (`now - last_heartbeat_at > lease_seconds`), but recovery verification has not completed.
- `RELEASED`: The owner session released the task cleanly upon completion or explicit yield.
- `COMPLETED`: The task associated with the lock has been committed and verified on remote.

---

## 4. Acquisition & Renewal Rules

1. **Acquiring a Lock**:
   - Check if `.agents/locks/runtime/active_task.lock` exists.
   - If not, create atomically with `status: "ACTIVE"`.
   - If it exists and status is `RELEASED` or `COMPLETED`, overwrite atomically with new session details.
   - If it exists and status is `ACTIVE` with current timestamp within `lease_seconds`, do NOT acquire. Emit `WAIT_FOR_LOCK`.
2. **Heartbeat Renewal**:
   - The owning session must update `last_heartbeat_at` at every loop step (at least every 60-120 seconds).
3. **Releasing a Lock**:
   - Upon task completion, verification, and remote push, set status to `COMPLETED` and remove or archive the lock.

---

## 5. Stale Lock Takeover Policy

- An expired lease (`now - last_heartbeat_at > lease_seconds`) alone is **insufficient** to steal a lock.
- The new session must verify:
  1. No active background OS process belongs to the owning session.
  2. Git working tree has not been modified within the last `lease_seconds`.
  3. No in-flight commit is currently undergoing push.
- Once confirmed stale, the takeover is logged in `SESSION_REGISTRY.md` before re-claiming the lock.
