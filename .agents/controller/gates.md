# Human Approval Gates

## 1. Principle & Purpose

While the DevImage build system operates autonomously, critical architectural transitions, security boundaries, external network actions, and branch merges require explicit human confirmation.

A **Human Approval Gate** pauses the autonomous execution loop, records the gate condition in [.agents/state/RUN.md](file:///.agents/state/RUN.md) and [.agents/state/CURRENT.md](file:///.agents/state/CURRENT.md), and presents a clear decision report to the user.

---

## 2. Mandatory Gate Triggers

The Autonomous Controller MUST stop and await human confirmation upon encountering any of the following triggers:

| Gate ID | Trigger Condition | Rationale & Safety Impact |
| :--- | :--- | :--- |
| **GATE-PHASE** | **Phase Completion & Transition** (e.g. Phase 0 → Phase 1) | Requires end-to-end acceptance review of the completed phase before proceeding to the next major milestone. |
| **GATE-DEPS** | **New Third-Party Dependency** not in approved core stack | Prevents dependency bloat and unintended license/security incompatibilities. |
| **GATE-MERGE** | **Merge to `main` Branch** | Protects the stability of the production/mainline codebase. |
| **GATE-RELEASE** | **Production Release Tagging** (e.g. `v0.1.0`) | Formal verification before distributing installers or binary packages. |
| **GATE-EXTERNAL** | **External Model Download / API Credentials** | Requires user consent before downloading local AI models or sending images via Gemini API. |
| **GATE-BLOCKED** | **Retry Budget Exhaustion** (3 consecutive fix failures) | Prevents infinite loop oscillations when facing fundamental architectural or environment errors. |
| **GATE-DESTRUCT** | **Destructive File/Dir Operations** | Prevents accidental deletion of source code or unbacked data. |

---

## 3. Approved Core Dependencies (Exempt from GATE-DEPS)

The following libraries are pre-approved in [plan.md](file:///plan.md) and do NOT trigger `GATE-DEPS`:
- Runtime: `PySide6`, `pillow`, `opencv-python`, `numpy`, `pydantic`
- Local AI / OCR: `onnxruntime`, `rembg`, `rapidocr-onnxruntime`
- Remote AI: `google-genai`
- Dev & Test: `pytest`, `pytest-qt`, `ruff`, `pyinstaller`

Any package outside this list triggers **GATE-DEPS**.

---

## 4. Gate Presentation & Notification Format

When a gate is reached, the Controller outputs a structured notification:

```markdown
================================================================================
🚨 HUMAN APPROVAL GATE TRIGGERED: [<GATE_ID>]
================================================================================
Phase: <Current Phase>
Feature: <Current Feature>
Task: <Task ID>
Reason: <Specific rationale for the pause>

Summary of Work Completed:
- <Milestone item 1>
- <Milestone item 2>

Decision Required:
- <Exact decision requested from user>

How to Proceed:
- Type "Approve" or "Continue" to proceed past this gate.
- Provide instructions or corrections to alter the proposed course.
================================================================================
```

---

## 5. Gate Clearance & Resumption Protocol

1. **User Sign-Off**: The user provides approval or guidance.
2. **Record in State**: The Controller records gate clearance in [.agents/state/RUN.md](file:///.agents/state/RUN.md) under `Gate History`.
3. **Task Status Update**: If a task was in `HUMAN_GATE` status, it transitions back to `IN_PROGRESS` or `COMPLETED`.
4. **Autonomous Continuation**: The Controller resumes execution from Step 10 or Step 12 of the Controller Execution Loop.
