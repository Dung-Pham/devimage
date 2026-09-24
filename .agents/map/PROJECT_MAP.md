# PROJECT_MAP.md — DevImage Documentation & Routing Index

This file is the documentation and code routing index for AI agents working on DevImage.
Agents must consult this map to answer *"Where should I look for this information?"* without reading the entire repository.

---

## 1. Project State & Tracking

- **Active State Pointer**: [.agents/state/CURRENT.md](file:///.agents/state/CURRENT.md)
  *Always read first. Contains current phase, active feature, next concrete action, and git sync status.*
- **Phase State Archives**: `.agents/state/phases/`
  *Archived summary records created when individual development phases are completed.*
- **Feature State Checkpoints**: `.agents/state/features/`
  *Granular feature progress files created when tracking complex multi-step features.*

---

## 2. Agent Governance Rules

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

## 5. Feature Documentation (Planned / Modular)

- **Resize Tool**: `docs/features/resize.md`
- **Compress Tool**: `docs/features/compress.md`
- **Convert Tool**: `docs/features/convert.md`
- **Crop Tool**: `docs/features/crop.md`
- **Watermark Tool**: `docs/features/watermark.md`
- **Exif Metadata Tool**: `docs/features/exif.md`
- **Color Palette & Eyedropper**: `docs/features/color.md`
- **Base64 Converter**: `docs/features/base64.md`
- **App Icon Generator**: `docs/features/app_icon.md`
- **Social Media Resizer**: `docs/features/social_resizer.md`
- **Remove Background**: `docs/features/remove_background.md`
- **OCR Text Extraction**: `docs/features/ocr.md`
- **Gemini Vision Assistant**: `docs/features/gemini_vision.md`
- **Batch Processing Manager**: `docs/features/batch.md`
- **Preset Management**: `docs/features/presets.md`

---

## 6. Source Code Locations (src/devimage/)

- **Application Entry Point**: `src/devimage/main.py`
- **Core Configuration & Base Types**: `src/devimage/core/`
- **UI Presentation Layer (QML)**: `src/devimage/ui/`
- **Tool Service Implementations**: `src/devimage/services/`
- **Image Processing Engines (Pillow, OpenCV, NumPy)**: `src/devimage/engines/image/`
- **AI Processing Engines (ONNX, Rembg, OCR, Gemini)**: `src/devimage/engines/ai/`
- **Background Worker Threads**: `src/devimage/workers/`
- **Common Utilities & Helpers**: `src/devimage/utils/`

---

## 7. Testing & Quality Assurance

- **Unit Tests**: `tests/unit/`
- **Integration Tests**: `tests/integration/`
- **Service Verification Tests**: `tests/services/`
- **Test Fixtures & Assets**: `tests/fixtures/`

---

## 8. Packaging & Deployment

- **PyInstaller Bundler**: `packaging/pyinstaller/`
- **Windows Installer (Inno Setup / NSIS)**: `packaging/windows/`
- **Build Automation Scripts**: `scripts/build/`

---

## 9. Architectural Decisions & Records

- **ADR Documents**: `docs/decisions/`
