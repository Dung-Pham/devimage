# Task Specification: TASK-P1-05 — Preview Component & Tool Shell Layout

## Metadata
- **Task ID**: `TASK-P1-05-preview-component-and-tool-shell`
- **Phase**: Phase 1 — Application Shell
- **Feature**: Image Preview & Tool Container
- **Status**: PENDING
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 11:35
- **Completed**:

---

## 1. Objective & Scope
Implement `components/ImagePreview.qml` (supporting image pan, zoom with mouse wheel, fit-to-view toggle, dimension badge, and transparency checkerboard background) and `tools/ToolShell.qml` (reusable two-pane workspace layout: left/top tool options panel and central interactive preview canvas, with "Back to Home" navigation).

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [plan.md](file:///plan.md) (Phase 1 Acceptance, Section 10)
- [prompt-build.md](file:///prompt-build.md) (Section 5, 8)

### Files to Create / Modify
- `src/devimage/ui/qml/components/ImagePreview.qml`
- `src/devimage/ui/qml/tools/ToolShell.qml`

---

## 3. Implementation Steps
1. Create `components/ImagePreview.qml` with `Flickable`, `Image` source bindings, zoom controls, fit-to-window button, and image resolution metadata badge.
2. Create `tools/ToolShell.qml` providing the canonical layout for all Phase 2 tools:
   - Header with tool title, description, and "Back to Home" button.
   - Side panel for tool-specific settings (dimension inputs, quality slider, format picker).
   - Main area displaying DropZone (when empty) or ImagePreview (when image loaded).

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Test Command**: `uv run pytest tests/ -v`
- **Expected Outcome**: Preview component and ToolShell load cleanly without unresolved symbols.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: N/A

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: ui
- **Commit Message**: `feat(ui): implement ImagePreview and reusable ToolShell page layout`
- **Commit Hash**:
- **Push Confirmed**: NO
