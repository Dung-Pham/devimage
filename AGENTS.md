# AGENTS.md — DevImage AI Agent Entry Point

Welcome to the **DevImage** project. This file is the primary entry point and mandatory routing guide for AI agents working in this repository.

---

## 1. First Actions on Every Turn

Before taking any development action:
1. **Read Current State**: Read [.agents/state/CURRENT.md](file:///.agents/state/CURRENT.md) first to determine the active phase, feature, and immediate next action.
2. **Inspect Git Environment**: Run `git status`, verify current branch, and inspect recent commits (`git log -n 5 --oneline`).
3. **Check Routing Index**: Consult [.agents/map/PROJECT_MAP.md](file:///.agents/map/PROJECT_MAP.md) before opening any additional documentation or source files.
4. **Selective Documentation Discipline**: Read *only* the specific files relevant to your current unit of work. Do not load the entire documentation tree.

---

## 2. Source of Truth & Durable Memory

- **Repository Over Chat**: Never assume previous conversation context or memory is the source of truth.
- The actual codebase, passing tests, Git history, and `.agents/state/CURRENT.md` constitute the project's durable memory.
- If chat context is lost or a fresh session begins, all project state can be reconstructed directly from the repository.

---

## 3. Mandatory Governance Rules

All agents must strictly adhere to the project rules in `.agents/rules/`:
- **Interruption Recovery**: Follow [.agents/rules/agent-continuity.md](file:///.agents/rules/agent-continuity.md) for crash recovery, state preservation, and uncommitted change handling.
- **Git & Backup Safety**: Follow [.agents/rules/git.md](file:///.agents/rules/git.md) for branching, Conventional Commits, and remote push-verification requirements.
- **Coding & Architecture**: Follow [.agents/rules/coding.md](file:///.agents/rules/coding.md) for Python-first desktop conventions, PySide6/QML separation, and testing standards.

---

## 4. Interruption & "Continue" Recovery Sequence

When the user says **"Continue"**, **"Tiếp tục"**, **"Resume"**, or starts a new session without instructions:
1. Read `.agents/state/CURRENT.md`.
2. Inspect Git working tree (`git status`) to protect uncommitted work.
3. Identify current branch and verify remote synchronization.
4. Identify latest verified commit and push state.
5. Identify current phase and current feature.
6. Identify current unfinished task.
7. Look up relevant documentation paths in `.agents/map/PROJECT_MAP.md`.
8. Continue execution directly from the documented `Next Action`.
9. **Never restart the project from scratch or repeat already completed tasks.**

---

## 5. State Maintenance & Granularity

- Keep `CURRENT.md` short (20–50 lines). It is a live pointer, not an append-only historical log.
- Overwrite and update `CURRENT.md` whenever a meaningful milestone is completed or the active task changes.
- Ensure all commits follow Conventional Commits and are pushed and verified remotely before declaring a task complete.
