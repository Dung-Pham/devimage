# DevImage Acceptance Matrix & Definition of Done

## 1. Overview

This matrix defines the explicit criteria required to transition work across development milestones: **Task**, **Feature**, **Phase**, and **Production Release**.

No milestone may be marked complete without satisfying all corresponding criteria.

---

## 2. Milestone Acceptance Criteria

### Level 1: Task Completion (Smallest Atomic Unit)
- [ ] Implementation satisfies all items in the task specification.
- [ ] No regression introduced to existing modules.
- [ ] Targeted tests pass (`pytest <target_test>`).
- [ ] Code is formatted and lint-clean (`ruff check`).
- [ ] Task status set to `COMPLETED` in task file and [.agents/state/QUEUE.md](file:///.agents/state/QUEUE.md).
- [ ] [.agents/state/CURRENT.md](file:///.agents/state/CURRENT.md) updated with next concrete action.
- [ ] Conventional Commit created and successfully pushed to remote branch.
- [ ] Remote push verified via `git status`.

---

### Level 2: Feature Completion
- [ ] All queued tasks for the feature are marked `COMPLETED`.
- [ ] Tool operates independently according to [plan.md](file:///plan.md) (no pipeline coupling).
- [ ] Single image and batch processing verified.
- [ ] QML presentation connects cleanly to backend service via non-blocking worker threads.
- [ ] Feature documentation exists under `docs/features/<feature>.md`.
- [ ] Feature state recorded in `.agents/state/features/<feature>.md`.
- [ ] Full unit and integration test suite passes.

---

### Level 3: Phase Completion
- [ ] All features within the phase satisfy Feature Completion criteria.
- [ ] Full application launches and passes headless smoke tests.
- [ ] Phase summary archive created in `.agents/state/phases/phase-<N>.md`.
- [ ] Human Approval Gate **`GATE-PHASE`** presented and cleared by user.
- [ ] Feature branch merged to `main` (if designated) or tagged accordingly.

---

### Level 4: Production MVP Release (Phase 8 Definition of Done)
- [ ] Standalone Windows executable packaged with PyInstaller (`onedir` + Inno Setup installer).
- [ ] Application installs and launches cleanly on a Windows machine with NO Python, Node.js, Docker, or external runtimes installed.
- [ ] All 13 MVP tools verified operational:
  - Image: Remove Background, Resize, Compress, Convert, Crop.
  - Developer: Inspector, Color Picker, Rename, Copy Path, OCR.
  - AI: Analyze Image, Alt Text, AI Command.
- [ ] Local tools execute 100% offline; Gemini features securely handle API keys via Windows credential store.
- [ ] Zero database, zero accounts, zero cloud storage requirements.
