# Autonomous Build System v2 Safety Invariants

## Non-Negotiable Rules for Agents

All AI agents interacting with DevImage in v2 mode must adhere strictly to these rules:

1. **Preserve v1 Intact**:
   - Never delete or modify the formatting of `CURRENT.md`, `QUEUE.md`, `RUN.md`, `BUILD_CONTROLLER.md`, or `gates.md`.
2. **Never Destructively Alter Git**:
   - `git reset --hard`, `git clean -fd`, and `git push --force` are strictly forbidden.
3. **No UI Automation Hacks**:
   - Do not attempt to synthesize user inputs or simulate GUI clicks to create Antigravity sessions. All session transitions must occur via explicit protocol steps.
4. **Git Remote Push is Durable Ground Truth**:
   - A task is never complete until its commit exists on the remote Git branch.
5. **Respect Human Approval Gates**:
   - When encountering `GATE-PHASE`, `GATE-DEPS`, `GATE-MERGE`, `GATE-RELEASE`, or `GATE-BLOCKED`, the agent MUST halt execution and present a summary to the user.
6. **Task Lock Exclusivity**:
   - An agent must NEVER steal an active lock with an unexpired lease.
7. **Ephemeral Lock Separation**:
   - Never commit lock files in `.agents/locks/runtime/` to Git.
