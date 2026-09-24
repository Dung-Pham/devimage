prompt 1:
You are working on the DevImage project.

Your task is to create ONLY the persistent AI-agent project management structure.

Do NOT implement application features yet.

Do NOT create unnecessary documentation.

Do NOT create large Markdown files.

The purpose of this structure is:

* persistent project memory
* interruption recovery
* selective documentation routing
* Git-aware development
* allowing a fresh AI session to continue from where the previous session stopped

## REQUIRED STRUCTURE

Create exactly this initial structure:

devimage/
├── AGENTS.md
└── .agents/
├── map/
│   └── PROJECT_MAP.md
│
├── rules/
│   ├── agent-continuity.md
│   ├── git.md
│   └── coding.md
│
└── state/
├── CURRENT.md
├── phases/
└── features/

Do not create feature state files yet unless the feature already exists in the repository.

Do not create phase files yet unless the corresponding phase already exists.

## FILE PURPOSES

### AGENTS.md

This is the top-level entry point for AI agents.

It must be short.

Target size: approximately 40–100 lines.

It must tell the agent:

1. Read `.agents/state/CURRENT.md` first.
2. Check Git status and current branch.
3. Read `.agents/map/PROJECT_MAP.md` when additional project information is required.
4. Read only relevant documentation.
5. Follow the Git workflow.
6. Follow the recovery procedure when the user says "Continue".
7. Never assume previous conversation context is the source of truth.

Do NOT put the complete project architecture or complete Git policy into AGENTS.md.

It should mainly provide routing and mandatory top-level instructions.

---

### .agents/map/PROJECT_MAP.md

This is the project documentation routing index.

It must answer:

"Where should the agent look for this information?"

Keep it short.

Target size: approximately 80–150 lines.

Include sections for:

* project state
* agent rules
* architecture
* features
* tests
* packaging
* decisions
* source code locations

The map should use paths rather than copying documentation content.

Example:

Current state:
`.agents/state/CURRENT.md`

Git:
`.agents/rules/git.md`

Coding:
`.agents/rules/coding.md`

Architecture:
`docs/architecture/`

Feature documentation:
`docs/features/`

Source:
`src/devimage/`

The map must be designed to grow gradually as the project grows.

Do not invent dozens of files that do not exist yet.

---

### .agents/rules/agent-continuity.md

This must be an always-on agent rule.

Its purpose is interruption recovery.

Include:

* startup recovery
* "Continue" behavior
* project state verification
* Git verification
* current task identification
* selective reading
* protection of uncommitted work
* updating CURRENT.md
* checkpointing
* commit/push requirements

Critical rule:

When the user says:

"Continue"

"Tiếp tục"

"Resume"

or equivalent,

the agent must first:

1. Read `.agents/state/CURRENT.md`
2. Check `git status`
3. Check current branch
4. Check recent commits
5. Verify whether the latest work was pushed
6. Determine current phase
7. Determine current feature
8. Determine current unfinished task
9. Read only relevant documentation
10. Continue from the documented next action

Do NOT immediately start coding before recovery inspection.

---

### .agents/rules/git.md

This must contain the complete Git workflow for the project.

Include:

* main branch policy
* feature branch policy
* branch naming
* Conventional Commits
* commit frequency
* push frequency
* backup checkpoints
* merge rules
* recovery after interruption
* handling push failures
* protection against destructive commands

Important project-specific rule:

The local storage environment is not considered reliable.

Therefore:

```
meaningful work
↓
test
↓
commit
↓
push
↓
verify push
↓
continue
```

Do NOT claim work is backed up until push succeeds.

Never casually use:

* git reset --hard
* git clean -fd
* git push --force
* history rewriting

unless explicitly required and safe.

---

### .agents/rules/coding.md

Create a concise project coding rule.

Include:

* Python-first architecture
* modular feature structure
* one responsibility per service
* QML handles UI only
* Python handles application logic
* heavy processing must not block UI
* tests required for meaningful functionality
* avoid unnecessary abstractions
* avoid unnecessary dependencies
* preserve existing functionality
* inspect existing code before changing it

Do NOT duplicate the full architecture here.

---

### .agents/state/CURRENT.md

This is the current project pointer.

It MUST remain short.

Target size: approximately 20–50 lines.

It must contain only:

# Current phase

# Current feature

# Current branch

# Status

# Completed

# In progress

# Next action

# Last verified commit

# Last verified push

# Tests

# Known issues

# Relevant documents

# Last updated

Do NOT turn this into a historical journal.

Do NOT append old status entries.

When the project progresses, overwrite the current state.

---

## IMPORTANT DESIGN RULE

Do not create one giant Markdown file.

The project uses this model:

AGENTS.md
↓
CURRENT.md
↓
PROJECT_MAP.md
↓
Relevant rule/document
↓
Source code
↓
Tests

The agent must read the smallest relevant amount of information.

---

## INITIAL CONTENT

Because the application has not necessarily been implemented yet, use honest placeholder state.

For example:

Phase:
Phase 0 — Foundation

Feature:
Project setup

Branch:
Use the actual current branch after checking Git.

Status:
Not Started / Initial Setup

Completed:
Agent management structure created.

In Progress:
None.

Next Action:
Start Phase 0 project foundation.

Last verified commit:
Use the actual Git state. Never invent a commit hash.

Last verified push:
Verify actual remote state.

Tests:
Not started.

Known issues:
None known.

Do not invent implementation progress.

---

## SAFETY

Before creating files:

1. Inspect the repository.
2. Check whether these files already exist.
3. Preserve existing useful content.
4. Do not overwrite existing rules blindly.
5. If a file already contains valuable project information, merge carefully rather than deleting it.

After creation:

1. Verify the complete directory structure.
2. Open and inspect every created Markdown file.
3. Ensure there is no duplicated or contradictory instruction.
4. Ensure CURRENT.md is short.
5. Ensure PROJECT_MAP.md is an index, not a documentation dump.

Do not implement DevImage features in this task.





prompt 2: 

Now initialize the DevImage persistent agent-management system.

Do NOT implement application features.

Do NOT redesign the application architecture.

Focus only on making the AI-agent context system operational.

## STEP 1 — Inspect

Read:

* AGENTS.md
* .agents/rules/agent-continuity.md
* .agents/rules/git.md
* .agents/rules/coding.md
* .agents/map/PROJECT_MAP.md
* .agents/state/CURRENT.md

Also inspect:

* current Git branch
* git status
* recent commits
* remote configuration

Do not read unrelated application files unless necessary.

## STEP 2 — Make the system internally consistent

Check that:

AGENTS.md
↓
CURRENT.md
↓
PROJECT_MAP.md
↓
rules
↓
actual repository

all agree.

Fix contradictions.

Do not duplicate large content across files.

## STEP 3 — Configure recovery behavior

Ensure the rules explicitly tell the agent that:

When the user says "Continue":

1. Read CURRENT.md.
2. Inspect Git.
3. Identify current branch.
4. Identify latest verified commit.
5. Identify whether the latest work was pushed.
6. Identify current phase.
7. Identify current feature.
8. Identify unfinished work.
9. Follow relevant paths in PROJECT_MAP.md.
10. Continue from Next Action.

The agent must not restart the project from scratch.

## STEP 4 — Configure state updates

Ensure the agent updates CURRENT.md after meaningful progress.

CURRENT.md must always describe the current state, not the entire history.

When a feature is completed, move the project pointer to the next feature.

When a feature is in progress, record the exact next action.

Example:

Current feature:
Resize

Status:
In Progress

Completed:

* resize service
* basic UI

In progress:

* batch worker

Next action:
Connect batch worker progress signals to QML.

The next action must be concrete enough that a new agent session can continue immediately.

## STEP 5 — Configure selective reading

The agent must NOT read the entire docs tree.

It must use:

.agents/map/PROJECT_MAP.md

to find relevant information.

For example:

Resize task:

* resize feature documentation
* backend architecture
* worker architecture
* resize source
* resize tests

Do not read OCR, Gemini, packaging, and unrelated documentation.

## STEP 6 — Verify

Test the recovery logic conceptually.

Pretend the previous AI session disappeared.

Assume the user starts a completely new session and types:

Continue

Determine whether the repository contains enough information to identify:

* current phase
* current feature
* current branch
* last verified checkpoint
* next action
* relevant documents

If not, improve the state structure.

Do not create huge files to solve the problem.

## STEP 7 — Git

After the agent-management structure is correct:

1. Check git diff.
2. Stage only the intended management files.
3. Commit with:

chore(agent): initialize persistent project context

4. Push the branch to GitHub.
5. Verify that the push succeeded.

Do not claim backup until the remote push is confirmed.

At the end, report:

* files created
* files modified
* current branch
* commit hash
* push status
* next project action



prompt 3: 
Perform a final audit of the DevImage AI-agent project-management system.

Do NOT implement application features.

## Audit the following:

### 1. Entry point

Verify:

AGENTS.md

is short and clearly tells the agent where to start.

### 2. Current state

Verify:

.agents/state/CURRENT.md

is short, factual, and actionable.

It must clearly identify:

* phase
* feature
* branch
* status
* next action
* latest verified commit
* push status

### 3. Documentation routing

Verify:

.agents/map/PROJECT_MAP.md

works as a routing index.

An agent should be able to answer:

"Where is information about X?"

without reading the entire repository.

### 4. Rules

Verify:

* agent-continuity.md
* git.md
* coding.md

do not contradict each other.

### 5. Recovery

Simulate:

Scenario A:
Internet disconnects.

Scenario B:
Power is lost.

Scenario C:
Antigravity session is interrupted.

Scenario D:
Agent starts in a new conversation.

Scenario E:
User says only:

Continue

For each scenario, determine whether the agent can reconstruct the current development state from the repository.

### 6. Git safety

Verify that the rules require:

* frequent commits
* immediate pushes
* feature branches
* meaningful commit messages
* no destructive commands without explicit justification
* verification of push success

### 7. Context efficiency

Verify that:

CURRENT.md remains small.

PROJECT_MAP.md remains an index.

Feature documentation is separated from state.

Historical information remains in Git rather than giant Markdown files.

### 8. Final correction

Fix any problems discovered.

Do not expand documentation unnecessarily.

Do not create duplicate documentation.

## Final report

Return:

1. Context structure status
2. Recovery readiness
3. Git safety status
4. Context efficiency status
5. Any corrections made
6. Current branch
7. Latest commit
8. Push status
9. Exact next development action
