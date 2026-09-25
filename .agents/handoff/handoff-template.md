# Session Handoff Payload Template

```markdown
# Session Handoff Checkpoint

- **From Session ID**: {outgoing_session_id}
- **Timestamp**: {iso8601_timestamp}
- **Active Branch**: {git_branch}
- **Last Verified Commit**: {commit_hash}
- **Remote Push Confirmed**: {YES / NO}

## Current Status
- **Phase**: {phase_name}
- **Feature**: {feature_name}
- **In-Flight Task ID**: {task_id or NONE}
- **Task Status**: {IN_PROGRESS / VERIFYING / COMPLETED / GATED}

## Uncommitted Working Tree
- **Modified Files**: {list of modified files or NONE}
- **Untracked Files**: {list of untracked files or NONE}

## Next Recommended Action
{concrete instructions for the incoming session}

## Gate Condition
- **Active Gate**: {GATE-PHASE / GATE-MERGE / NONE}
- **Requires Human Sign-off**: {YES / NO}
```
