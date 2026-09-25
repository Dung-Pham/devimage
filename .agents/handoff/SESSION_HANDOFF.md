# Session Handoff Protocol

## 1. Objective

Provide a structured, durable mechanism for transferring development continuity between different AI agent conversation sessions without relying on truncated chat history.

---

## 2. Handoff Triggers

A session handoff is triggered under any of the following events:
1. **Context Window Saturation**: Approaching token context limits.
2. **Phase / Milestone Completion**: Clean stopping point at a human approval gate (`GATE-PHASE`, `GATE-MERGE`).
3. **Session Interruption / Crash**: Unexpected disconnection or error.
4. **Planned Transfer**: User starts a new conversation or switches workstations.

---

## 3. Handoff Payload Structure

Every session producing a handoff must ensure:
1. **Uncommitted Work Protected**: If dirty work exists, either commit as an explicit WIP or record exact file list in handoff notes.
2. **Durable State Updated**: `CURRENT.md`, `QUEUE.md`, `V2_RUN.json`, and `SESSION.json` reflect the exact progress.
3. **Registry Updated**: Write a timestamped entry to `SESSION_REGISTRY.md`.
4. **Task Lock Handled**: If exiting cleanly, release the active lock; if handing off in-flight work, flag lock status as `HANDOFF_READY`.

---

## 4. Handoff Consumption

The incoming session loads the handoff using [.agents/handoff/RESUME_PROTOCOL.md](file:///.agents/handoff/RESUME_PROTOCOL.md), verifies Git state against the payload, and continues execution seamlessly.
