Bạn là Lead Software Engineer chịu trách nhiệm xây dựng hoàn chỉnh một desktop application Windows tên **DevImage — Developer Image Toolbox**.

Mục tiêu: không chỉ lập kế hoạch. Hãy trực tiếp tạo code, cài dependency, chạy application, chạy test, sửa lỗi và build bản Windows.

## 1. Product concept

DevImage là một desktop toolbox xử lý ảnh dành cho Developer.

Không phải Photoshop.

Không phải image editor.

Không phải workflow/pipeline engine.

Mỗi tool hoạt động độc lập.

Ví dụ:

Resize → Resize xong.

Compress → Compress xong.

Convert → Convert xong.

Remove Background → Remove Background xong.

Không tự động nối các thao tác.

Không tạo database.

Không tạo account.

Không tạo cloud storage.

Không tạo server backend.

Các chức năng local phải chạy offline.

---

# 2. Technology stack — MUST FOLLOW

Use:

* Python 3.13.x
* PySide6
* Qt Quick / QML
* Pillow
* OpenCV
* NumPy
* Pydantic
* ONNX Runtime
* rembg hoặc background-removal engine tương thích tốt nhất
* RapidOCR cho OCR nếu compatibility ổn định
* google-genai cho Gemini
* pytest
* pytest-qt
* ruff
* PyInstaller

Do NOT use:

* Electron
* React
* Node.js runtime
* FastAPI
* Docker
* database
* web server

Python là application runtime chính.

---

# 3. Important compatibility rule

Before installing packages, inspect current package compatibility.

Python 3.13 is the target runtime.

Do not blindly install the newest version of every dependency.

Resolve a compatible dependency set.

Use pinned or constrained versions in the project configuration after compatibility is verified.

Do not upgrade Python to 3.14 merely because it is newer if the selected background-removal stack does not support it.

---

# 4. Start by inspecting the environment

First:

1. Inspect current working directory.
2. Determine whether an existing project exists.
3. Inspect existing files.
4. Preserve useful existing work if present.
5. If empty, initialize a new project.
6. Check Python version.
7. Check available GPU if relevant.
8. Check Windows environment.
9. Check Git status if repository exists.

Do not destroy existing files without reason.

Do not ask unnecessary clarification questions.

Use sensible defaults when requirements are already defined.

---

# 5. Create the project structure

Use the architecture defined below:

devimage/
pyproject.toml
README.md
LICENSE
.gitignore

```
src/
    devimage/
        main.py

        app/
            application.py
            settings.py
            paths.py

        core/
            models.py
            errors.py
            signals.py
            types.py

        engine/
            image/
            ai/
            background_removal/
            ocr/

        tools/
            resize/
            compress/
            convert/
            crop/
            remove_background/
            inspector/
            color_picker/
            rename/
            copy_path/
            ocr/
            analyze/
            alt_text/
            ai_command/

        workers/

        services/

        ui/
            qml/
                Main.qml
                AppShell.qml
                Home.qml
                components/
                dialogs/
                common/
                tools/

tests/
    unit/
    integration/
    fixtures/

assets/
    icons/
    branding/

models/

scripts/

packaging/
```

Keep this architecture unless a concrete technical problem requires a change.

---

# 6. Architecture principles

Use clear separation:

QML
↓
Application/UI layer
↓
Tool services
↓
Processing engines

QML must NOT perform image processing.

QML should only handle UI.

Python handles:

* file operations
* image operations
* AI
* model management
* workers
* configuration
* logging

---

# 7. Build order

Do NOT implement everything in one giant pass.

Implement in phases.

Complete and verify each phase before continuing.

## Phase 0

Build:

* project
* pyproject
* Python environment
* QML application
* logging
* settings
* testing
* linting

Acceptance:

Application launches successfully.

---

## Phase 1

Build:

* main window
* app shell
* Home
* tool cards
* navigation
* settings
* file picker
* drag/drop
* notification/toast
* dialogs
* preview component

The UI must already look like a real desktop application.

---

# 8. Home page

Use this tool structure:

IMAGE TOOLS

* Remove Background
* Resize
* Compress
* Convert
* Crop

DEVELOPER TOOLS

* Image Inspector
* Color Picker
* OCR
* Rename
* Copy Path

AI TOOLS

* Analyze Image
* Generate Alt Text
* AI Command

Use a clean modern developer-tool visual style.

Do not make a giant sidebar.

The main purpose of Home is to select a tool quickly.

---

# 9. Tool implementation order

Implement exactly:

### 1. Resize

Requirements:

* single image
* batch
* width
* height
* aspect ratio
* don't enlarge
* contain
* cover
* stretch
* presets
* preview
* output
* progress
* cancel
* error handling
* tests

### 2. Compress

Requirements:

* quality
* preserve format
* optional format selection
* metadata removal
* size comparison
* batch
* progress
* tests

### 3. Convert

Requirements:

* PNG
* JPEG
* WebP
* AVIF when supported
* quality
* metadata
* output naming
* batch
* tests

### 4. Crop

Requirements:

* crop rectangle
* zoom
* pan
* aspect ratios
* custom ratio
* reset
* batch
* tests

---

# 10. Remove Background

This is the most important feature.

Build it carefully.

Use local inference.

Recommended architecture:

BackgroundRemovalService
↓
BackgroundRemovalEngine
↓
ModelManager
↓
ONNX Runtime model

Requirements:

* JPG
* JPEG
* PNG
* WebP
* single image
* batch
* transparency checkerboard
* original/result preview
* zoom
* progress
* cancel
* output PNG
* output WebP
* optional crop transparent area
* optional keep original dimensions
* error handling

Model Manager must:

* detect model
* download if missing
* verify downloaded file
* keep version information
* reuse loaded model/session
* provide useful errors
* not redownload unnecessarily

Do NOT store model binaries in Git.

---

# 11. Image Inspector

Read-only.

Show:

* filename
* path
* size
* width
* height
* format
* color mode
* alpha
* DPI
* metadata
* EXIF

Allow:

* copy information
* copy JSON

Tests required.

---

# 12. Color Picker

Requirements:

* click image
* HEX
* RGB
* HSL
* copy HEX
* copy RGB
* copy CSS
* zoom/pan

The UI must feel smooth.

---

# 13. Rename

Requirements:

* multiple files
* pattern
* numbering
* zero padding
* lowercase
* uppercase
* whitespace normalization
* collision detection
* preview old/new
* confirm before execution

Never silently overwrite another file.

---

# 14. Copy Path

Context actions:

* Copy Path
* Copy Filename
* Copy Directory
* Open Folder

Use native Windows behavior where appropriate.

---

# 15. OCR

Use RapidOCR + ONNX Runtime if compatibility is good.

Requirements:

* image input
* OCR
* extracted text
* copy text
* Vietnamese
* English
* German when supported
* local processing
* error handling
* tests

OCR model must be managed separately.

---

# 16. Gemini

Use the official Python Gemini SDK.

Create:

GeminiService

and keep network access isolated.

Features:

### Analyze Image

Return structured information.

### Generate Alt Text

Return clean web-ready alt text.

### AI Command

Convert natural language into validated JSON.

For example:

User:

"Resize these images to 1200px and convert them to WebP."

Gemini result:

{
"operation": "resize",
"width": 1200,
"keep_aspect_ratio": true
}

OR for one operation at a time:

{
"operation": "convert",
"format": "webp",
"quality": 82
}

Do not allow arbitrary code.

Do not allow shell execution.

Do not allow AI to directly control the OS.

AI output must pass Pydantic validation.

The application must show the interpreted action before executing it.

---

# 17. File system rules

Never use a database.

Never copy user images into an internal asset database.

Use filesystem paths.

Do not overwrite source files by default.

Default output:

<source folder>/DevImage_Output/

Allow custom output directory.

Handle duplicate names safely.

---

# 18. Preview system

Never load gigantic source images directly into the UI at full resolution unless necessary.

Generate resized preview/proxy images.

Use a cache.

Release image resources properly.

---

# 19. Worker system

All heavy operations must run away from the UI thread.

Use:

* QThreadPool
* QRunnable
* Qt signals

Workers must provide:

* started
* progress
* result
* error
* finished
* cancelled

The UI must remain responsive.

---

# 20. Batch architecture

Batch means:

ONE TOOL
+
MANY FILES

It does NOT mean pipeline.

For example:

20 files → Remove Background

is valid.

But:

20 files → Remove Background → Resize → Compress

is NOT part of MVP.

---

# 21. Settings

Create settings:

General:

* theme
* output folder
* auto-open folder
* overwrite behavior

Processing:

* quality
* default format
* batch concurrency

AI:

* Gemini API key
* Gemini model
* connection test

Models:

* background removal
* OCR

Store sensitive API key using a secure Windows-compatible credential mechanism.

Never put the key in:

* source code
* Git
* .env committed to repository
* plain example files

---

# 22. Error handling

No raw stack traces in production UI.

Create typed application errors.

UI should show:

Title

What happened

Why it might happen

What user can do

Technical details only in logs.

---

# 23. Logging

Use Python logging.

Write to application log directory.

Log:

* startup
* tool invocation
* processing duration
* model loading
* errors
* AI requests without secrets

Never log:

* Gemini API key
* image binary
* sensitive user data

---

# 24. Testing

Every tool requires unit tests.

At minimum:

Resize:

* dimensions
* aspect ratio
* don't enlarge

Compress:

* quality
* output exists
* smaller size where expected

Convert:

* output format

Crop:

* dimensions
* aspect ratio

Inspector:

* metadata extraction

Rename:

* pattern
* numbering
* conflicts

Color:

* RGB/HEX conversion

OCR:

* known fixture text

Remove Background:

* output
* alpha channel
* dimensions
* batch

AI Command:

* valid JSON
* invalid JSON
* unsupported operation
* invalid parameters

---

# 25. Performance testing

Create benchmark scripts.

Benchmark:

* 1 image
* 10 images
* 100 images
* large images
* background removal

Measure:

* execution time
* RAM
* CPU
* GPU if used

Do not prematurely optimize.

---

# 26. Packaging

Use PyInstaller.

First build an onedir package.

Verify:

* application opens on clean Windows machine
* Python is not required
* dependencies are bundled
* models resolve correctly
* settings resolve correctly
* logs resolve correctly

Then create an installer.

Also create a portable build if practical.

---

# 27. Production path handling

Never assume current working directory.

Use application-aware paths.

Separate:

* bundled resources
* writable user data
* models
* logs
* cache
* output

Never try to write user settings or logs into the read-only bundled application directory.

---

# 28. UX rules

The application should follow:

* common actions require few clicks
* drag/drop first
* clear buttons
* obvious Save button
* clear progress
* clear error
* no unnecessary wizard
* no unnecessary confirmation
* no complex project system

Every tool should work independently.

---

# 29. Scope discipline

Do NOT add:

* Photoshop features
* layers
* brush
* advanced masks
* video editing
* database
* cloud
* login
* accounts
* project manager
* collaboration
* autonomous agents
* workflow builder
* plugin marketplace

Do not add architecture just because it "might be useful later".

---

# 30. Implementation behavior

While coding:

1. Inspect.
2. Implement.
3. Run.
4. Test.
5. Fix.
6. Refactor only where useful.
7. Continue.

Do not stop at scaffolding.

Do not tell me to manually implement the remaining code.

When something fails:

* inspect the error
* identify root cause
* fix code
* rerun
* continue

Do not hide failures.

---

# 31. Required deliverables

At the end provide:

1. Working source code
2. README
3. Development setup instructions
4. Test suite
5. Build script
6. PyInstaller spec
7. Windows installer
8. Portable build if possible
9. Architecture documentation
10. Configuration documentation
11. Known limitations
12. Release notes

---

# 32. Final acceptance test

Before declaring the project finished, perform a full end-to-end test:

Launch app.

Test:

* Home
* Resize
* Compress
* Convert
* Crop
* Remove Background
* Inspector
* Color Picker
* Rename
* Copy Path
* OCR
* Gemini Analyze
* Alt Text
* AI Command
* Batch
* Cancel
* Save
* Error states
* Settings
* API key configuration
* Model management

Then:

1. Build production package.
2. Launch packaged application.
3. Test core features again.
4. Fix packaging-specific bugs.
5. Rebuild.
6. Verify final installer.

Do not declare success merely because the source code compiles.

The final criterion is:

**A normal Windows user can install DevImage and use it without installing Python, Node.js, Docker, or any development dependency.**
