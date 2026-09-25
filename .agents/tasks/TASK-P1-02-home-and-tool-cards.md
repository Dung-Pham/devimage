# Task Specification: TASK-P1-02 — Home View & Interactive Tool Cards Grid

## Metadata
- **Task ID**: `TASK-P1-02-home-and-tool-cards`
- **Phase**: Phase 1 — Application Shell
- **Feature**: Home Page & Tool Selection
- **Status**: COMPLETED
- **Assigned Worker**: Implementer
- **Created**: 2026-09-25 11:35
- **Completed**: 2026-09-25 11:39

---

## 1. Objective & Scope
Implement `src/devimage/ui/qml/Home.qml` and `src/devimage/ui/qml/components/ToolCard.qml` structured strictly per Section 8:
- IMAGE TOOLS: Remove Background, Resize, Compress, Convert, Crop
- DEVELOPER TOOLS: Image Inspector, Color Picker, OCR, Rename, Copy Path
- AI TOOLS: Analyze Image, Generate Alt Text, AI Command
Features include search/filter bar, category headers, hover animations, and signal dispatch upon clicking a card.

---

## 2. Target Context (Isolation Boundary)
### Read-Only References
- [prompt-build.md](file:///prompt-build.md) (Section 8 — Home page tool structure)
- [plan.md](file:///plan.md) (Section 8)

### Files to Create / Modify
- `src/devimage/ui/qml/Home.qml`
- `src/devimage/ui/qml/components/ToolCard.qml`
- `src/devimage/ui/qml/components/SearchInput.qml`

---

## 3. Implementation Steps
1. Create `components/ToolCard.qml`: Card rectangle with icon badge, title, subtitle description, category pill, hover transition, and click signal.
2. Create `components/SearchInput.qml`: Clean search box with clear button and keyboard focus.
3. Create `Home.qml`: Responsive grid organizing tools by category, filtering dynamically with search text, and triggering tool selection.

---

## 4. Verification Requirements
- **Lint Check**: `uv run ruff check src/ tests/`
- **Test Command**: `uv run pytest tests/ -v`
- **Expected Outcome**: All tool cards render properly in headless engine and react to tool selection signals.

---

## 5. Human Approval Gates
- **Gate Required**: None
- **Gate Rationale**: N/A

---

## 6. Completion Checkpoint
- **Commit Type**: feat
- **Commit Scope**: home
- **Commit Message**: `feat(home): implement Home view and categorized ToolCard grid`
- **Commit Hash**:
- **Push Confirmed**: NO
