# DevImage Build System Migration Guide: v1 to v2

## 1. Overview

This document specifies the additive migration protocol from **Autonomous Build System v1** to **v2**.

### Migration Principles
1. **Zero Downtime**: The existing v1 pipeline remains operable throughout and after the migration.
2. **Format Invariance**: Do not change the syntax or structure of existing v1 state files (`CURRENT.md`, `QUEUE.md`, `RUN.md`).
3. **Dual State Synchronization**: When running in v2, every state transition updates both the v1 Markdown pointers and the v2 JSON stores.
4. **Git Non-Interference**: Migration artifacts must not modify application code in `src/` or product test suites in `tests/`.

---

## 2. Stage-by-Stage Progression

- **Stage 0 (Audit)**: Verification of clean branch baseline and existing v1 state.
- **Stage 1 (Infrastructure)**: Addition of v2 specification, handoff, locking, and recovery files.
- **Stage 2 (Compatibility Layer)**: Explicit reconciliation between v1 Markdown and v2 JSON.
- **Stage 3 (Observe-Only Mode)**: Safe initialization with no write locks.
- **Stage 4 (Resume Protocol)**: Complete workflow for new session takeover.
- **Stage 5 (Task Claim & Lock Protocol)**: Lease-based concurrency protection.
- **Stage 6 (Crash Recovery Protocol)**: Deterministic recovery actions for all failure modes.
- **Stage 7 (Validation Suite)**: Deterministic Python test suite verifying all 12 edge cases.
- **Stage 8 (Git Checkpoint)**: Conventional commit and push verification on `feature/autonomous-build-v2`.

---

## 3. Rollback Protocol

If any conflict occurs during v2 execution:
1. Revert operating mode in `.agents/state/V2_RUN.json` to `"OBSERVE_ONLY"`.
2. Delete any runtime lock file in `.agents/locks/runtime/`.
3. Rely strictly on v1 controller [.agents/controller/BUILD_CONTROLLER.md](file:///.agents/controller/BUILD_CONTROLLER.md).
