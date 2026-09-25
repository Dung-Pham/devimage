# Session Bootstrap Worker Specification

## 1. Purpose

The **Session Bootstrap Worker** is the first routine executed when an AI agent initiates a new turn or starts a new conversation session. It performs discovery, lock inspection, and state reconciliation before any development action is taken.

---

## 2. Bootstrap Sequence

```
1. Generate / Identify Session ID
   └── Format: "session-<timestamp>-<short_random_or_pid>"
2. Inspect Git Environment
   └── Branch, uncommitted working tree changes, recent commits.
3. Read Durable v1 Files
   └── CURRENT.md, RUN.md, QUEUE.md.
4. Read Runtime v2 Files
   └── V2_RUN.json, SESSION.json, SESSION_REGISTRY.md.
5. Inspect Active Task Lock
   └── Check .agents/locks/runtime/active_task.lock.
6. Evaluate Session Ownership
   ├── Case A: Lock free -> Eligible to claim next task.
   ├── Case B: Lock owned by current session -> Continue task.
   ├── Case C: Lock owned by active third-party session -> Yield (WAIT_FOR_LOCK).
   └── Case D: Lock owned by stale session -> Trigger STALE_RECOVERY.
7. Record Session in SESSION_REGISTRY.md & SESSION.json.
```

---

## 3. Invariants
- Bootstrap must complete within 2 seconds.
- Bootstrap is strictly non-destructive.
