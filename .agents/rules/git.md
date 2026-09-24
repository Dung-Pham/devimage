# Git & Remote Backup Workflow

## 1. Environment Safety Notice

The local environment is treated as transient and crash-prone. Local unpushed commits do NOT count as backed-up progress.
Work is only safe once pushed to GitHub and verified.

---

## 2. Mandatory Workflow Pipeline

For every meaningful unit of work:

```
Implement Small Unit
       ↓
Run Relevant Tests
       ↓
Update .agents/state/CURRENT.md
       ↓
Stage Intended Files (git add <files>)
       ↓
Commit (Conventional Commits)
       ↓
Push to Remote (git push)
       ↓
Verify Push Succeeded (git status)
       ↓
Proceed to Next Unit
```

**Never claim work is backed up until the remote push command returns success.**

---

## 3. Branching Strategy

- **`main` Branch**:
  - Contains stable, working code and verified project state checkpoints.
  - Releases and major milestone checkpoints are tagged on `main`.
- **Feature Branches**:
  - Name format: `feature/<feature-name>` (e.g., `feature/resize-tool`, `feature/remove-bg-service`).
  - Bug fixes: `fix/<issue-description>`.
  - Infrastructure/Chores: `chore/<task-name>`.
- Branches should be kept short-lived and merged into `main` once tests pass and features are complete.

---

## 4. Commit Message Standard (Conventional Commits)

Use standard Conventional Commits format:
`<type>(<scope>): <short description in present tense>`

Common types:
- `feat`: A new user-facing or architectural feature.
- `fix`: A bug fix.
- `refactor`: Code reorganization without functional changes.
- `test`: Adding or updating test cases.
- `chore`: Maintenance, dependencies, or agent state/context updates.
- `docs`: Documentation updates.

Examples:
- `feat(resize): implement aspect ratio calculation service`
- `test(resize): add unit tests for image downscaling`
- `chore(agent): update CURRENT.md for Phase 0 checkpoint`

---

## 5. Destructive Commands Strictly Prohibited

Unless explicitly requested by the user and confirmed safe, **NEVER run**:
- `git reset --hard`
- `git clean -fd`
- `git push --force` or `--force-with-lease`
- Interactive rebasing or history rewriting that alters published commits.

Always check `git status` and `git diff` before staging files. Avoid blind `git add .` or `git add -A` to avoid committing unwanted artifacts or credential leaks.

---

## 6. Handling Push Failures & Disconnections

If `git push` fails (e.g. network timeout or rejection):
1. **Do not panic and do not reset working state.**
2. Log the exact error.
3. Check `git status` and verify local commit was created.
4. Record in `.agents/state/CURRENT.md`:
   - `Last verified commit: <hash>`
   - `Last verified push: FAILED (offline/pending retry)`
5. When connectivity is restored, retry `git push` and update `CURRENT.md` once verified.
