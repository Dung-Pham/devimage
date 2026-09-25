# Deterministic Session Resume Protocol

## 1. Overview

This protocol governs how a new conversation session resumes project work without relying on chat history or prior context memory.

---

## 2. 15-Step Execution Workflow for Fresh Sessions

Whenever an agent begins a session (or user triggers "Continue", "Resume", "Tiếp tục"):

```
 1. Read AGENTS.md
 2. Read .agents/map/PROJECT_MAP.md
 3. Read .agents/state/CURRENT.md
 4. Read .agents/state/RUN.md
 5. Read .agents/state/QUEUE.md
 6. Read .agents/state/SESSION.json (if exists)
 7. Read .agents/state/V2_RUN.json (if exists)
 8. Inspect Git branch and status (git status -u, git log -n 5 --oneline)
 9. Inspect active task lock (.agents/locks/runtime/active_task.lock)
10. Inspect session registry (.agents/handoff/SESSION_REGISTRY.md)
11. Determine session status (ACTIVE / STALE / COMPLETED / FREE)
12. Reconcile state against Git (verify pushed commits match CURRENT.md)
13. Determine deterministic resume outcome (see Section 3)
14. Claim task lock only when verified safe
15. Continue execution from documented Next Action
```

---

## 3. Deterministic Resume Outcomes

| Outcome Code | Condition | Action Required |
| :--- | :--- | :--- |
| **`RESUME_TASK`** | Lock free or owned by current session; in-flight task defined in `CURRENT.md`. | Claim lock, load task isolation context, proceed with implementation. |
| **`RESUME_VERIFICATION`** | Code changes present and complete for task, but verification runner not executed. | Run lint and tests; advance to state update on pass. |
| **`RESUME_FIX`** | Task failed verification in prior session; retry budget remaining (< 3). | Dispatch failure log to Fixer worker; apply surgical fix. |
| **`WAIT_FOR_GATE`** | Current task or phase completed and stopped at `GATE-*`. | Halt execution; display gate summary and prompt user for confirmation. |
| **`WAIT_FOR_LOCK`** | Lock held by an active session with valid recent heartbeat (< 120s). | Do not steal lock. Stop and inform user another session is actively working. |
| **`RECOVER_UNCOMMITTED_WORK`** | Working tree dirty from previous interrupted session. | Execute [CRASH_RECOVERY.md](file:///.agents/recovery/CRASH_RECOVERY.md) Scenario A. |
| **`STOP_AND_REPORT`** | Contradictory state detected between Git history and state files. | Halt immediately; report discrepancies to user without modifying files. |
