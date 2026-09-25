# PROJECT_MAP.md — DevImage Documentation & Routing Index

This file is the documentation and code routing index for AI agents working on DevImage.
Agents must consult this map to answer *"Where should I look for this information?"* without reading the entire repository.

---

## 1. Project State & Tracking

- **Active State Pointer**: [.agents/state/CURRENT.md](file:///.agents/state/CURRENT.md)
  *Always read first. Contains current phase, active feature, next concrete action, and git sync status.*
- **Active Task Queue**: [.agents/state/QUEUE.md](file:///.agents/state/QUEUE.md)
  *Prioritized list of in-flight, pending, and completed tasks.*
- **Autonomous Run State**: [.agents/state/RUN.md](file:///.agents/state/RUN.md)
  *Autonomous loop execution metadata, retry counter, and gate flags.*
- **Task Specifications**: `.agents/tasks/`
  *Self-contained, independently executable task specifications.*
- **Phase State Archives**: `.agents/state/phases/`
  *Archived summary records created when individual development phases are completed.*
- **Feature State Checkpoints**: `.agents/state/features/`
  *Granular feature progress files created when tracking complex multi-step features.*

---

## 2. Autonomous Build Control System

- **Build Controller**: [.agents/controller/BUILD_CONTROLLER.md](file:///.agents/controller/BUILD_CONTROLLER.md)
  *12-step autonomous loop algorithm for queue execution, testing, and continuous deployment.*
- **Human Approval Gates**: [.agents/controller/gates.md](file:///.agents/controller/gates.md)
  *Mandatory stop conditions for phase transitions, dependencies, and branch merges.*
- **Worker Protocols**: `.agents/workers/`
  *Task Decomposer ([decomposer.md](file:///.agents/workers/decomposer.md)), Task Implementer ([implementer.md](file:///.agents/workers/implementer.md)), Surgical Fixer ([fixer.md](file:///.agents/workers/fixer.md)).*
- **Verification Engine**: `.agents/verification/`
  *Multi-layer Verification Runner ([verification-runner.md](file:///.agents/verification/verification-runner.md)) and Acceptance Matrix ([acceptance-matrix.md](file:///.agents/verification/acceptance-matrix.md)).*
- **Autonomous Governance Rule**: [.agents/rules/autonomous-execution.md](file:///.agents/rules/autonomous-execution.md)
- **Autonomous Architecture Guide**: [docs/architecture/autonomous-build-system.md](file:///docs/architecture/autonomous-build-system.md)

---

## 3. Agent Governance Rules

- **Autonomous Execution**: [.agents/rules/autonomous-execution.md](file:///.agents/rules/autonomous-execution.md)
  *Autonomous loop invariants, task isolation, and mandatory checkpointing.*
- **Continuity & Recovery**: [.agents/rules/agent-continuity.md](file:///.agents/rules/agent-continuity.md)
  *Mandatory startup recovery, "Continue" protocol, checkpointing, and uncommitted work protection.*
- **Git & Backup Workflow**: [.agents/rules/git.md](file:///.agents/rules/git.md)
  *Branching strategy, Conventional Commits, remote push verification, and prohibition of destructive commands.*
- **Coding Standards**: [.agents/rules/coding.md](file:///.agents/rules/coding.md)
  *Python-first desktop architecture, PySide6/QML separation, non-blocking workers, offline-first image tools.*

---

## 3. Master Specifications & Roadmaps

- **Master Implementation Plan**: [plan.md](file:///plan.md)
  *Comprehensive blueprint covering Phase 0 to Phase 12, product requirements, and system design.*
- **Prompt & Build Directives**: [prompt-build.md](file:///prompt-build.md)
  *Phase execution prompts, prompt workflows, safety procedures, and step-by-step guidance.*
- **Agent System Specifications**: [3-prompt-build-control-tree.md](file:///3-prompt-build-control-tree.md)
  *Control tree and verification prompts for the persistent agent management structure.*

---

## 4. Architecture Documentation (Planned / Modular)

- **System Architecture Overview**: `docs/architecture/system.md`
  *Overall application layering, component communication, and process lifecycle.*
- **QML / PySide6 Frontend Layer**: `docs/architecture/frontend.md`
  *UI layout patterns, QML component organization, and Qt property/signal bridges.*
- **Application Services Layer**: `docs/architecture/services.md`
  *Service registry, lifecycle management, and tool-service boundaries.*
- **Image Processing Engine**: `docs/architecture/image_engine.md`
  *Pillow, OpenCV, and NumPy processing pipelines, color space conversions, and caching.*
- **AI Processing Engine**: `docs/architecture/ai_engine.md`
  *ONNX Runtime setup, Rembg background removal models, OCR integrations, and Gemini Vision client.*
- **Worker & Threading Architecture**: `docs/architecture/workers.md`
  *Background thread pools, cancellation tokens, and asynchronous progress reporting.*

---

## 5. Feature Documentation (Planned / Modular — 13 MVP Tools)

### Image Tools
- **Remove Background Tool**: `docs/features/remove_background.md`
- **Resize Tool**: `docs/features/resize.md`
- **Compress Tool**: `docs/features/compress.md`
- **Convert Tool**: `docs/features/convert.md`
- **Crop Tool**: `docs/features/crop.md`

### Developer Tools
- **Image Inspector**: `docs/features/inspector.md`
- **Color Picker**: `docs/features/color_picker.md`
- **Batch Rename**: `docs/features/rename.md`
- **Copy Path**: `docs/features/copy_path.md`
- **OCR Text Extraction**: `docs/features/ocr.md`

### AI Tools
- **AI Image Analysis**: `docs/features/analyze.md`
- **Alt Text Generator**: `docs/features/alt_text.md`
- **AI Command**: `docs/features/ai_command.md`

---

## 6. Source Code Locations (src/devimage/)

- **Application Entry Point**: `src/devimage/main.py`
- **Application Lifecycle, Settings & Paths**: `src/devimage/app/`
- **Core Models, Errors, Signals & Types**: `src/devimage/core/`
- **Engines (Pillow, OpenCV, ONNX, Rembg, RapidOCR, Gemini)**: `src/devimage/engine/` (`image/`, `background_removal/`, `ocr/`, `ai/`)
- **Independent Tool Implementations**: `src/devimage/tools/`
- **Shared Application Services**: `src/devimage/services/`
- **Background Worker Threads & ThreadPool**: `src/devimage/workers/`
- **UI Presentation (QML) & Backend Bridges**: `src/devimage/ui/` (`qml/`, `bridge/`)

---

## 7. Testing & Quality Assurance

- **Unit Tests**: `tests/unit/`
- **Integration Tests**: `tests/integration/`
- **Test Fixtures & Assets**: `tests/fixtures/`

---

## 8. Packaging, Deployment & Assets

- **PyInstaller Specification**: `packaging/devimage.spec`
- **Windows Installer (Inno Setup)**: `packaging/installer/`
- **Automation Scripts**: `scripts/` (`dev.ps1`, `test.ps1`, `build.ps1`)
- **Assets & Branding**: `assets/` (`icons/`, `branding/`)
- **Local AI Models Storage**: `models/`

---

## 9. Architectural Decisions & Records

- **ADR Documents**: `docs/decisions/`
