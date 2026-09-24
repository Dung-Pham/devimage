# Coding Standards & Architecture Principles

## 1. Core Technology Stack

- **Runtime**: Python 3.13+ (PySide6 / Qt Quick)
- **Frontend / View**: QML (Qt Quick Controls)
- **Backend / Logic**: Pure Python services and core modules
- **Image Processing**: Pillow, OpenCV, NumPy (offline-first)
- **AI Processing**: ONNX Runtime, Rembg, Tesseract/OCR, Gemini API (opt-in only)
- **Packaging**: PyInstaller + Inno Setup for Windows distribution

---

## 2. Separation of Concerns (UI vs. Backend)

- **QML is for Presentation**:
  - Handles visual layout, animations, user input bindings, and view state.
  - QML MUST NOT execute business logic, file I/O, or image transformations.
- **Python is for Logic**:
  - Exposes services and controllers via `QObject` with Qt Signals, Slots, and Properties (`Property`).
  - Implements all tool business logic, image processing pipelines, and persistence.

---

## 3. Asynchronous & Non-Blocking Execution

- **Zero UI Freezes**:
  - Heavy operations (image loading, scaling, compression, background removal, batch processing) must NEVER run on the Qt GUI main thread.
  - Offload heavy tasks to background workers (`QRunnable`, `QThreadPool`, or dedicated worker threads).
  - Communicate progress and completion back to QML via Qt Signals (`pyqtSignal` / `Signal`).

---

## 4. Modularity & Single Responsibility

- **Standalone Tool Services**:
  - Each tool (Resize, Compress, Convert, Crop, Watermark, etc.) is an independent service with a dedicated interface.
  - Avoid creating monolithic processing pipelines or unnecessary coupling between independent tools.
- **Keep Abstractions Minimal**:
  - Write straightforward, readable Python code.
  - Do not create premature design patterns, deep inheritance trees, or boilerplate interfaces unless justified.

---

## 5. Offline-First & Privacy First

- Standard image editing and conversions MUST operate completely offline with no network calls.
- AI features requiring remote APIs (like Gemini Vision) are strictly opt-in and must handle offline/key errors gracefully.

---

## 6. Code Integrity & Testing

- **Inspect First**: Always inspect existing code and related tests before making modifications.
- **Preserve Existing Functionality**: Maintain backward compatibility and do not break working features.
- **Mandatory Tests**: Every new service, utility, or business logic function must be accompanied by unit tests in `tests/`.
- Ensure all tests pass before committing any changes.
