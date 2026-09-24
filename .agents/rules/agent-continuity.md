# Agent Continuity & Interruption Recovery Rule

## 1. Core Principle

The local working environment and AI chat sessions are subject to interruptions (network disconnection, crash, session reset, power loss).
Therefore, **the repository and Git history are the single source of truth**, not past chat transcripts or agent memory.

Every AI session must be able to resume immediately and safely from repository state.

---

## 2. Recovery on "Continue", "Tiếp tục", "Resume", or Fresh Session

Whenever the user prompts with **"Continue"**, **"Tiếp tục"**, **"Resume"**, or whenever a new session starts without explicit instructions:

**Mandatory 10-Step Inspection Sequence (Execute BEFORE any code modifications):**

1. **Read Active State**: Read `.agents/state/CURRENT.md`.
2. **Inspect Working Tree**: Run `git status` to detect uncommitted or untracked changes.
3. **Verify Current Branch**: Check active branch (`git branch --show-current`).
4. **Inspect Recent Commits**: Check the last 5 commits (`git log -n 5 --oneline`).
5. **Verify Remote Sync**: Check if local commits are pushed to remote (`git status` ahead/behind count, `git log origin/<branch>..HEAD`).
6. **Identify Current Phase**: Read phase information from `CURRENT.md`.
7. **Identify Current Feature**: Read active feature target from `CURRENT.md`.
8. **Identify Current Unfinished Task**: Locate the exact work item under "In Progress" or "Next Action".
9. **Selective Documentation Routing**: Look up required files in `.agents/map/PROJECT_MAP.md` and read only what is strictly necessary.
10. **Resume Execution**: Continue directly from the documented `Next Action`.

**NEVER restart the project from scratch or repeat already implemented work.**

---

## 3. Durable Memory Hierarchy

When determining project truth or resolving contradictions, prioritize in this order:

1. **Actual Source Code & Passing Tests**: Ground truth of what works.
2. **Git History**: Commits and verified diffs.
3. **GitHub Remote**: Confirmed pushed checkpoints.
4. **State Pointer**: `.agents/state/CURRENT.md`.
5. **Project Map & Specifications**: `.agents/map/PROJECT_MAP.md`, `plan.md`.
6. **Agent Rules**: `.agents/rules/`.
7. **Conversation History**: Ephemeral context only.

---

## 4. Protection of Uncommitted Work

1. If local uncommitted changes exist upon session startup, inspect them with `git diff`.
2. Never run destructive Git commands (`git reset --hard`, `git clean -fd`, `git checkout -- .`) without explicit user instruction.
3. If uncommitted work belongs to the current task, test it, commit it, and push it before moving forward.

---

## 5. Granular Checkpointing & "Done" Definition

Break tasks into small, crash-safe, independently verifiable units:
- Do not attempt multi-feature implementations in a single uncommitted block.
- Standard unit flow:
  `Implement Small Unit → Run Tests → Update CURRENT.md → Commit → Push → Verify Push → Proceed`

**A unit of work is NOT complete until:**
- Tests pass.
- State in `CURRENT.md` is updated.
- Commit is created following Conventional Commits.
- Commit is successfully pushed to the remote repository.

---

## 6. Maintaining CURRENT.md

- `CURRENT.md` is a real-time pointer, not an append-only historical journal.
- Keep it concise (20–50 lines).
- When a task or feature finishes:
  - Move it to "Completed".
  - Update "Current Feature" to the next objective.
  - Set concrete, unambiguous "Next Action" so another agent can continue immediately.
