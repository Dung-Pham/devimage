# DevImage Autonomous Build Controller v2

## 1. Mission & Architecture Overview

The **Autonomous Build Controller v2** builds upon the foundation of v1 ([BUILD_CONTROLLER.md](file:///.agents/controller/BUILD_CONTROLLER.md)) by introducing resilient multi-session lifecycle management, distributed task locking, deterministic crash recovery, and machine-readable runtime state.

### Primary v2 Capabilities
1. **Machine-Readable Runtime State**: Complements human-readable Markdown files (`CURRENT.md`, `QUEUE.md`, `RUN.md`) with strictly typed JSON state (`V2_RUN.json`, `SESSION.json`).
2. **Lease-Based Task Locking**: Enforces single-session task ownership through [.agents/locks/LOCK_PROTOCOL.md](file:///.agents/locks/LOCK_PROTOCOL.md), preventing conflicting concurrent agent sessions.
3. **Session Handoff & Auto-Resume**: Allows any fresh conversation to reconstruct the full development context and resume safely using [.agents/handoff/RESUME_PROTOCOL.md](file:///.agents/handoff/RESUME_PROTOCOL.md).
4. **Deterministic Crash Recovery**: Evaluates Git working tree, unpushed commits, and stale heartbeats using [.agents/recovery/CRASH_RECOVERY.md](file:///.agents/recovery/CRASH_RECOVERY.md).
5. **Absolute Backward Compatibility**: All v1 state files and execution steps remain 100% functional and respected.

---

## 2. Source-of-Truth Hierarchy

When reading project state, v2 strictly enforces the following resolution hierarchy:

```
1. Actual source code (src/) & Verified Tests (tests/)
   └── Passing tests establish ground truth of implementation reality.
2. Git History & Remote Synchronization State
   └── Pushed commits on GitHub are the durable ledger of finished work.
3. V1 Markdown State (.agents/state/CURRENT.md, QUEUE.md, RUN.md)
   └── Canonical human-readable state pointers.
4. V2 Machine-Readable Runtime State (V2_RUN.json, SESSION.json)
   └── Live session leases, heartbeats, and controller mode.
5. Task Specifications (.agents/tasks/*.md)
   └── Granular acceptance criteria and isolation boundary.
6. Architectural & Project Documentation (docs/, plan.md)
   └── Contextual design guides.
7. Transient LLM Conversation Transcript
   └── Non-durable; MUST NOT be treated as ground truth.
```

---

## 3. The 14-Step v2 Controller Loop

The v2 Controller expands the v1 12-step cycle with explicit session lease heartbeats and handoff checkpoints:

```
[1. Session Bootstrap & Registry Check]
       │
       ▼
[2. Lock Acquisition / Task Claim] ──(Conflict?)──> [HALT: WAIT_FOR_LOCK / STALE_RECOVERY]
       │
       ▼
[3. Read Durable State] (CURRENT.md, QUEUE.md, RUN.md, Git)
       │
       ▼
[4. Git Safety Inspection] (Working tree, unpushed commits)
       │
       ▼
[5. Crash / Interruption Triage] (CRASH_RECOVERY.md)
       │
       ▼
[6. Queue Selection & Context Isolation]
       │
       ▼
[7. Human Approval Gate Evaluation] ──(Gate Active?)──> [HALT: GATE-PHASE / GATE-*]
       │
       ▼
[8. Worker Implementation] (Implementer)
       │
       ▼
[9. Automated Verification Suite] (ruff, pytest, GUI smoke)
       │
       ▼
[10. Self-Healing / Fix Loop] (Fixer, max 3 attempts)
       │
       ▼
[11. State Synchronization] (Update v1 MD + v2 JSON simultaneously)
       │
       ▼
[12. Git Commit, Push & Remote Verification]
       │
       ▼
[13. Session Heartbeat & Handoff Preparation]
       │
       ▼
[14. Task Release / Advance Loop]
```

---

## 4. Operating Modes

The Controller v2 operates in one of three mutually exclusive modes:

1. **`OBSERVE_ONLY`**:
   - Active during audits, migrations, and read-only inspections.
   - Disallowed: claiming locks, advancing tasks, writing code, or committing.
2. **`AUTONOMOUS_V1_COMPAT`**:
   - Executes standard v1 tasks while updating v2 machine state in the background.
3. **`AUTONOMOUS_V2_FULL`**:
   - Full lease-locking, session registry tracking, and automated handoffs active.

---

## 5. Human Approval Gate Discipline

Under no circumstances does v2 bypass human gates. Gates defined in [.agents/controller/gates.md](file:///.agents/controller/gates.md) (`GATE-PHASE`, `GATE-DEPS`, `GATE-MERGE`, `GATE-RELEASE`, `GATE-BLOCKED`) halt execution immediately with a structured report.
