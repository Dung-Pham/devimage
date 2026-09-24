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
# 33. Git / GitHub Management — MANDATORY

GitHub đã được kết nối sẵn với môi trường làm việc.

Không cần cấu hình lại authentication, GitHub account hoặc remote nếu đã tồn tại.

Git phải được sử dụng như cơ chế version control + backup liên tục cho toàn bộ project.

## 33.1. Nguyên tắc bắt buộc

Mọi thay đổi code quan trọng phải được commit và push lên GitHub ngay sau khi hoàn thành một đơn vị chức năng có thể kiểm chứng.

KHÔNG làm một lượng lớn chức năng rồi mới commit.

KHÔNG giữ hàng trăm thay đổi local chưa commit.

Do ổ lưu trữ hiện tại không đáng tin cậy, ưu tiên:

```
Code xong
↓
Test
↓
Commit
↓
Push GitHub
↓
Tiếp tục chức năng tiếp theo
```

GitHub remote phải luôn có bản code mới nhất có thể sử dụng.

---

# 33.2. Branch strategy

Branch chính:

```
main
```

Không phát triển trực tiếp trên `main` trừ các thay đổi cực kỳ nhỏ như sửa documentation hoặc cấu hình đơn giản.

Mỗi chức năng lớn phải có một branch riêng.

Naming:

```
feature/<feature-name>
```

Ví dụ:

```
feature/project-foundation
feature/home-ui
feature/resize
feature/compress
feature/convert
feature/crop
feature/remove-background
feature/image-inspector
feature/color-picker
feature/rename
feature/copy-path
feature/ocr
feature/ai-analyze
feature/alt-text
feature/ai-command
feature/packaging
```

Bug fix:

```
fix/<short-description>
```

Ví dụ:

```
fix/resize-aspect-ratio
fix/background-model-loading
fix/ocr-memory-leak
```

Packaging/build changes:

```
chore/<short-description>
```

Ví dụ:

```
chore/pyinstaller-config
chore/github-release
```

---

# 33.3. One feature = one branch

Không gom nhiều chức năng độc lập vào cùng một feature branch.

Ví dụ:

ĐÚNG:

```
feature/resize
feature/compress
feature/convert
feature/remove-background
```

KHÔNG:

```
feature/all-image-tools
```

Mỗi branch phải có scope rõ ràng.

Ví dụ:

```
feature/resize
```

chỉ chứa:

* Resize UI
* Resize service
* Resize worker integration
* Resize tests
* Resize documentation nếu cần

Không thêm Compress hoặc Convert vào branch này.

---

# 33.4. Trước khi bắt đầu một branch

Luôn kiểm tra:

```
git status
git branch --show-current
git remote -v
```

Sau đó đồng bộ branch chính:

```
git fetch origin
```

Nếu cần tạo feature branch mới:

```
git switch main
git pull --ff-only origin main
git switch -c feature/<feature-name>
```

Không tự ý dùng:

```
git reset --hard

git clean -fd

git push --force

git push --force-with-lease
```

trừ khi có chỉ dẫn rõ ràng từ người dùng.

Không được sử dụng các lệnh có khả năng làm mất code hiện tại.

---

# 33.5. Commit strategy

Commit phải nhỏ, rõ ràng và có ý nghĩa.

Sử dụng Conventional Commits.

Examples:

```
feat(resize): add resize service

feat(resize): add resize tool UI

feat(resize): add batch processing

test(resize): add resize service tests

fix(resize): prevent image enlargement

chore(packaging): configure pyinstaller

docs: update setup instructions
```

Không dùng commit message kiểu:

```
update

changes

fix stuff

test

final

final2

final-final
```

---

# 33.6. Commit after each completed unit

Khi hoàn thành một unit có thể kiểm chứng:

1. Run relevant tests.
2. Check `git diff`.
3. Check `git status`.
4. Stage only intended files.
5. Create meaningful commit.
6. Push immediately.

Ví dụ:

```
Resize service hoàn thành
    ↓
pytest tests/unit/tools/resize
    ↓
git diff
    ↓
git add ...
    ↓
git commit -m "feat(resize): add resize service"
    ↓
git push -u origin feature/resize
```

Sau đó mới tiếp tục Resize UI.

Không chờ đến khi toàn bộ Resize hoàn thành mới push.

---

# 33.7. Push immediately

Sau mỗi commit quan trọng phải push ngay.

Ví dụ:

```
git push origin feature/resize
```

Sau lần push đầu tiên có thể thiết lập upstream:

```
git push -u origin feature/resize
```

Từ đó:

```
git push
```

Mục tiêu:

Nếu máy local bị hỏng ngay sau đó, code đã được lưu trên GitHub.

---

# 33.8. Backup checkpoints

Ngoài feature completion, phải tạo backup checkpoint khi:

* hoàn thành architecture foundation
* hoàn thành application shell
* hoàn thành một tool
* hoàn thành local AI model integration
* hoàn thành OCR
* hoàn thành Gemini integration
* hoàn thành packaging
* sửa bug quan trọng

Nếu có thay đổi đang dang dở nhưng đủ an toàn để lưu checkpoint, có thể commit với message rõ ràng:

```
checkpoint(remove-background): model loading working
```

Không dùng checkpoint để thay thế việc chia commit hợp lý.

---

# 33.9. Merge strategy

Sau khi một feature branch:

* hoàn thành
* test pass
* application chạy được
* không có known blocking issue

thì merge vào `main`.

Quy trình:

```
feature/resize
      ↓
tests pass
      ↓
commit
      ↓
push branch
      ↓
merge → main
      ↓
push main
```

Sau khi merge:

```
git switch main
git pull --ff-only origin main
```

Sau đó tạo branch tiếp theo từ `main`.

Không xây feature mới dựa trên branch feature cũ nếu không thực sự cần.

---

# 33.10. Preserve working states

`main` phải luôn ở trạng thái tương đối ổn định.

Không merge code rõ ràng đang hỏng vào `main`.

Nếu một feature chưa hoàn thành:

```
feature/remove-background
```

giữ tất cả thay đổi ở branch đó.

Có thể push branch nhiều lần để backup mà không ảnh hưởng `main`.

---

# 33.11. Recovery-first principle

Nếu Git hoặc filesystem có dấu hiệu bất thường, ưu tiên backup code trước khi tiếp tục phát triển.

Ví dụ:

```
git status
git log --oneline -10
git remote -v
```

Nếu commit hiện tại chưa được push:

```
git push
```

Không tiếp tục viết thêm code trong tình trạng chưa xác định lịch sử Git.

---

# 33.12. Before destructive changes

Trước các thay đổi lớn như:

* architecture refactor
* dependency replacement
* packaging changes
* model replacement
* major UI rewrite

phải tạo một commit checkpoint trước.

Ví dụ:

```
git commit -m "chore: checkpoint before architecture refactor"
```

Sau đó push.

Chỉ bắt đầu refactor lớn sau khi checkpoint đã được push thành công lên GitHub.

---

# 33.13. Git status discipline

Không để repository có trạng thái không rõ ràng.

Cuối mỗi meaningful work session phải kiểm tra:

```
git status
```

AI agent phải biết chính xác:

* branch hiện tại
* commit mới nhất
* thay đổi chưa commit
* remote đã được push hay chưa

Không tuyên bố hoàn thành khi vẫn còn thay đổi quan trọng chưa commit/push.

---

# 33.14. Feature implementation example

Ví dụ triển khai Resize:

```
main
  │
  └── feature/resize
          │
          ├── commit 1
          │   feat(resize): add resize service
          │
          ├── push
          │
          ├── commit 2
          │   feat(resize): add resize UI
          │
          ├── push
          │
          ├── commit 3
          │   test(resize): add resize tests
          │
          ├── push
          │
          └── final verification
                  ↓
               merge main
                  ↓
               push main
```

Sau đó:

```
main
  │
  └── feature/compress
```

Không làm tất cả tools trong một branch duy nhất.

---

# 33.15. Git checkpoints during long implementation

Nếu một feature lớn cần nhiều ngày hoặc nhiều bước, vẫn phải push thường xuyên.

Ví dụ Remove Background:

```
feature/remove-background

commit:
feat(remove-bg): add model manager
push

commit:
feat(remove-bg): add inference engine
push

commit:
feat(remove-bg): add single image processing
push

commit:
feat(remove-bg): add batch processing
push

commit:
feat(remove-bg): add preview UI
push

commit:
test(remove-bg): add processing tests
push
```

Không cần chờ toàn bộ feature hoàn thiện mới backup.

---

# 33.16. Never lose work for cleanliness

Không được xóa hoặc reset code chỉ vì muốn repository "sạch" nếu chưa chắc thay đổi đó đã được backup.

Ưu tiên:

```
Preserve
↓
Commit
↓
Push
↓
Clean up
```

thay vì:

```
Delete
↓
Reset
↓
Risk losing work
```

---

# 33.17. Dependency changes

Khi thêm hoặc thay dependency:

1. Modify dependency configuration.
2. Install.
3. Verify application.
4. Run tests.
5. Commit dependency changes.
6. Push.

Ví dụ:

```
chore(deps): add onnxruntime
```

hoặc:

```
chore(deps): pin compatible pillow version
```

Không thay đổi hàng loạt dependency không cần thiết.

---

# 33.18. Release tags

Khi hoàn thành một MVP hoặc phiên bản ổn định:

```
main
  ↓
git tag v0.1.0
  ↓
git push origin v0.1.0
```

Version format:

```
v0.1.0
v0.2.0
v1.0.0
```

Không tạo release tag cho code chưa qua acceptance test.

---

# 33.19. Final Git verification

Trước khi kết thúc mỗi major phase:

```
git status
```

phải cho biết không còn thay đổi quan trọng chưa lưu.

Kiểm tra:

```
git log --oneline --decorate -20
```

Kiểm tra branch:

```
git branch -a
```

Kiểm tra remote:

```
git remote -v
```

Đảm bảo branch cần thiết đã được push.

Nếu có commit local chưa push:

```
git push
```

Không được kết thúc phase khi code quan trọng chỉ tồn tại trên local machine.

---

# 33.20. Absolute Git rules

MUST:

* Use feature branches.
* Keep functions separated by branch.
* Commit frequently.
* Push immediately after meaningful commits.
* Keep `main` stable.
* Use meaningful commit messages.
* Create checkpoints before major refactors.
* Verify push success.
* Protect existing work.

MUST NOT:

* Work on everything in one giant branch.
* Accumulate huge uncommitted changes.
* Force push.
* Reset hard casually.
* Delete uncommitted work.
* Rewrite Git history unnecessarily.
* Commit secrets/API keys.
* Commit large AI model binaries unless explicitly required.
* Claim work is backed up until push succeeds.

The primary objective is:

**At any point, the latest meaningful work must exist on GitHub so a local disk failure does not destroy the project.**


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



# 34. Agent Continuity, Recovery & Interrupted Session Management — MANDATORY

The development environment may experience unexpected interruptions at any time:

* Internet disconnection
* Electricity outage
* PC restart
* Antigravity crash
* Agent process termination
* Terminal crash
* Model/API interruption
* Windows update/restart
* Manual interruption
* Background task failure

The project MUST be designed so that the agent can safely recover and continue without relying exclusively on the previous conversation memory.

The repository itself must contain enough verified state for another agent session to understand where development stopped.

---

# 34.1. Recovery principle

Conversation history is useful context.

Git is the source of truth for code.

Project state files are the source of truth for development progress.

When recovering from an interruption:

```
Repository
    ↓
Git status
    ↓
Current branch
    ↓
Latest pushed commit
    ↓
Project state
    ↓
Tests / actual code
    ↓
Continue from verified state
```

Never assume that the last conversation message accurately represents the actual state of the code.

The codebase and Git history have priority over conversational assumptions.

---

# 34.2. Persistent project state

Create:

```
.agents/
    rules/
    state/
```

and maintain:

```
.agents/state/PROJECT_STATUS.md
```

This file is part of the repository and MUST be committed and pushed.

It must contain:

```
# DevImage Project Status

## Current Phase
Phase 2 — Core Image Tools

## Current Feature
Resize

## Current Branch
feature/resize

## Last Verified Commit
abc1234

## Last Verified Push
origin/feature/resize

## Completed
- Resize service
- Aspect ratio handling
- Basic resize UI

## In Progress
- Batch processing UI

## Next Step
Implement batch progress handling.

## Tests
- Unit tests: PASS
- Integration tests: PASS
- GUI tests: NOT YET RUN

## Known Issues
- Large images need preview optimization

## Important Decisions
- Use Pillow for standard resize
- Heavy processing runs through QThreadPool

## Recovery Notes
Last safe checkpoint:
`abc1234`
```

The file must be factual.

Do not write future intentions as completed work.

---

# 34.3. State update rule

Update PROJECT_STATUS.md whenever one of these occurs:

* feature starts
* meaningful sub-feature completes
* test milestone completes
* important architecture decision is made
* bug is fixed
* major blocker is discovered
* checkpoint commit is created
* feature is completed

Do not update status merely to create noise.

The goal is that another agent can understand the project in less than a few minutes.

---

# 34.4. State must reflect verified reality

Never write:

```
Resize completed
```

unless:

* implementation exists
* relevant tests pass
* application behavior has been verified

Never write:

```
pushed successfully
```

unless the push command actually succeeded.

Never write:

```
feature complete
```

while important work remains.

Status is evidence-based.

---

# 34.5. Atomic checkpoint rule

For every meaningful development checkpoint:

```
Implement
   ↓
Test
   ↓
Verify
   ↓
Update PROJECT_STATUS.md
   ↓
Commit
   ↓
Push
   ↓
Verify push
   ↓
Continue
```

The status file must be committed together with the code state it describes.

This is important.

Do not update the state file in one commit while the corresponding code exists only in another unpushed commit.

---

# 34.6. Every feature must have a recovery checkpoint

Example:

```
feature/remove-background
```

Checkpoint 1:

```
model manager working
```

Checkpoint 2:

```
model inference working
```

Checkpoint 3:

```
single image processing working
```

Checkpoint 4:

```
batch processing working
```

Checkpoint 5:

```
UI integration working
```

Checkpoint 6:

```
tests passing
```

Each checkpoint:

```
code
+
PROJECT_STATUS.md
↓
commit
↓
push
```

---

# 34.7. Interruption-safe development

Assume the machine may shut down immediately after any command.

Therefore:

* Do not accumulate large uncommitted changes.
* Do not keep important progress only in memory.
* Do not assume the agent will finish the current task.
* Commit meaningful progress frequently.
* Push immediately after commits.
* Keep PROJECT_STATUS.md reasonably current.

The safest state is always:

```
Working code
+
Git commit
+
GitHub push
+
Accurate PROJECT_STATUS.md
```

---

# 34.8. Recovery protocol

Whenever the agent starts a new conversation and the user says:

```
Continue
```

or:

```
Tiếp tục
```

or:

```
Continue from where you stopped.
```

The agent MUST NOT immediately start coding.

First perform a recovery inspection.

### Step 1 — Identify repository

Check:

```
pwd
git rev-parse --show-toplevel
```

Confirm the correct project.

### Step 2 — Check Git

Run:

```
git status
git branch --show-current
git log --oneline --decorate -10
git remote -v
```

### Step 3 — Inspect project state

Read:

```
.agents/state/PROJECT_STATUS.md
```

If it does not exist, inspect:

```
AGENTS.md
GEMINI.md
README.md
implementation plans
task documentation
```

### Step 4 — Compare state with reality

Do not blindly trust PROJECT_STATUS.md.

Compare it against:

* current branch
* latest commit
* working tree
* tests
* actual source code

If state says:

```
Resize UI completed
```

but Git/source code shows otherwise, treat the actual repository state as authoritative and correct PROJECT_STATUS.md.

### Step 5 — Determine recovery point

Identify:

```
Current phase
Current feature
Last verified commit
Last pushed commit
Uncommitted changes
Pending task
Last known error
```

### Step 6 — Protect current work

If uncommitted changes exist:

Do NOT delete them.

Do NOT run:

```
git reset --hard
```

Do NOT run:

```
git clean -fd
```

Do NOT overwrite files blindly.

Inspect the changes first.

### Step 7 — Resume

Only after establishing the current state should implementation continue.

---

# 34.9. Recovery message

After recovery inspection, provide a concise status summary before editing.

Use this format:

```
RECOVERY CHECK

Project:
DevImage

Branch:
feature/remove-background

Last commit:
abc1234 feat(remove-bg): add single image inference

Push status:
Confirmed pushed to origin

Completed:
- Model manager
- Single image inference

In progress:
- Batch processing

Next step:
Implement batch worker + progress signals

Tests:
18 passed

Uncommitted changes:
2 files
```

Then continue the implementation.

Do not ask the user to repeat previous context unless the repository genuinely does not contain enough information.

---

# 34.10. Recovery must prioritize Git over conversation

When these disagree:

Conversation says:

```
"Batch processing was completed."
```

But repository shows:

```
batch processing unfinished.
```

The repository wins.

If:

Conversation says:

```
"We were implementing Remove Background."
```

But current branch is:

```
feature/resize
```

and project state confirms Resize:

Continue from the current repository state.

Never resurrect assumptions merely because they existed in conversation history.

---

# 34.11. Conversation naming

Long-running feature conversations should be renamed clearly.

Examples:

```
DevImage — Foundation
DevImage — Home UI
DevImage — Resize
DevImage — Remove Background
DevImage — OCR
DevImage — Gemini
DevImage — Packaging
```

Do not create vague names such as:

```
New Chat
Continue
Test
Fix
```

This makes conversation recovery easier.

Antigravity supports persistent conversation history and resuming previous development threads. Use that capability where available, but still rely on repository state as the durable source of truth.

---

# 34.12. Implementation Plan continuity

For large features, create an Implementation Plan before execution.

The plan should contain:

* objective
* scope
* affected files
* architecture
* implementation tasks
* verification steps
* acceptance criteria

The implementation plan should remain available as an Artifact.

When recovering from an interruption:

1. Find the existing plan.
2. Read it.
3. Compare it with actual Git/source state.
4. Continue from the first unfinished task.

Do not regenerate the entire architecture from scratch unless the existing plan is demonstrably obsolete.

---

# 34.13. Task checklist

Maintain a task checklist for the current phase.

Example:

```
Phase 3 — Remove Background

[x] Model manager
[x] Download model
[x] Verify checksum
[x] Load model
[x] Single image processing
[ ] Batch processing
[ ] Progress UI
[ ] Cancel operation
[ ] Preview
[ ] Save result
[ ] Integration tests
```

After each meaningful completion:

1. Update checklist.
2. Run tests.
3. Update PROJECT_STATUS.md.
4. Commit.
5. Push.

---

# 34.14. Checkpoint commit format

Use:

```
checkpoint(<feature>): <state>
```

Examples:

```
checkpoint(remove-bg): single image inference working

checkpoint(ocr): local OCR integration working

checkpoint(packaging): packaged app launches
```

Normal completed implementation should still use normal Conventional Commit messages.

Checkpoint commits are specifically useful for recovery.

---

# 34.15. Emergency checkpoint

If the agent determines that an interruption may happen soon, or the environment is unstable:

Create a safe checkpoint.

Example:

```
git status

update PROJECT_STATUS.md

git add <intended files>

git commit -m "checkpoint(remove-bg): preserve current implementation"

git push
```

Only then continue.

---

# 34.16. If network fails during push

Do not assume the code is backed up.

Determine:

```
commit exists locally?
push succeeded?
push failed?
```

If push fails:

```
STOP declaring the work backed up.
```

Retry the push when network connectivity is restored.

Until successful:

```
GitHub backup = NOT CONFIRMED
```

Do not tell the user that the work is safely backed up until remote push succeeds.

---

# 34.17. If electricity is suddenly lost

After restart:

1. Open the project.
2. Inspect Git.
3. Inspect PROJECT_STATUS.md.
4. Inspect latest commit.
5. Inspect working tree.
6. Run targeted tests if necessary.
7. Determine whether the last changes were committed.
8. If safe, continue.
9. If local uncommitted changes exist, preserve them and inspect them before doing anything destructive.

Never assume the last task was completed.

---

# 34.18. If Antigravity conversation is lost

Do NOT restart the project mentally from zero.

Use:

```
Git
+
PROJECT_STATUS.md
+
AGENTS.md
+
Implementation Plan
+
README
+
source code
+
tests
```

These together form the project's durable memory.

The agent must be able to continue even with zero access to the previous conversation.

---

# 34.19. If agent starts with a fresh conversation

The user should be able to type only:

```
Continue.
```

The agent must interpret that as:

```
Recover project state first.
Do not start a new implementation plan blindly.
Determine the current unfinished work.
Continue from the verified checkpoint.
```

---

# 34.20. Do not repeat completed work

Before implementing any feature, verify:

```
Does the code already exist?
```

Check:

* source
* tests
* Git history
* project status
* current branch

If implementation already exists, do not recreate it.

Instead:

* test it
* inspect it
* fix it if necessary
* continue with the next unfinished step.

---

# 34.21. Crash-safe task granularity

Break large features into small recoverable units.

Bad:

```
"Implement Remove Background completely."
```

Good:

```
"Create model manager."
```

Then:

```
"Implement local inference."
```

Then:

```
"Implement single-image processing."
```

Then:

```
"Implement batch worker."
```

Then:

```
"Implement preview."
```

Then:

```
"Implement tests."
```

Every unit should be independently commit-able.

---

# 34.22. Final state after each agent turn

Before ending a meaningful work session, the agent should know:

```
What did I finish?
What did I verify?
What did I commit?
What did I push?
What remains?
What should happen next?
```

These answers must exist in PROJECT_STATUS.md.

Do not rely solely on the final chat message.

---

# 34.23. Durable memory hierarchy

Use this priority:

```
1. Actual source code
2. Git history
3. GitHub remote
4. PROJECT_STATUS.md
5. Implementation Plan / Artifacts
6. AGENTS.md / project rules
7. Previous conversation
```

Conversation is context.

Repository is truth.

---

# 34.24. Absolute continuity rule

At any point in time, another AI agent should be able to clone the repository, read the project instructions and project state, inspect Git, and determine:

* where the project currently is
* what is already complete
* what is currently being developed
* what remains
* what branch to work on
* what the next task is
* what tests have passed
* what known problems exist

without asking the original agent to explain the project.

This is mandatory for the entire DevImage project.


# 35. Context Mapping & Selective Documentation — MANDATORY

The project uses a mapped documentation architecture.

The agent MUST NOT read every documentation file at the beginning of every task.

The purpose of the project map is to minimize unnecessary context consumption.

## 35.1. Primary navigation files

Always start from:

```
AGENTS.md
```

Then:

```
.agents/map/PROJECT_MAP.md
```

For current state:

```
.agents/state/CURRENT.md
```

These files act as the entry point.

---

## 35.2. Selective reading

After reading PROJECT_MAP.md, identify the smallest set of files relevant to the current task.

Example:

Resize task:

```
.agents/state/CURRENT.md
.agents/state/features/resize.md
docs/features/resize.md
docs/architecture/backend.md
docs/architecture/workers.md
```

Do NOT read:

```
docs/features/ocr.md
docs/features/gemini.md
docs/features/remove-background.md
```

unless the current implementation actually depends on them.

---

## 35.3. Current state is not project history

`.agents/state/CURRENT.md` must remain short.

It describes only:

* current phase
* current branch
* current feature
* completed work
* current task
* next action
* last verified commit
* last verified push
* tests
* known issues
* relevant documentation

Do NOT turn CURRENT.md into a historical journal.

---

## 35.4. Historical information

Historical information belongs in:

```
Git history
feature state files
phase state files
ADR documents
```

Do not continuously append historical events to CURRENT.md.

---

## 35.5. Feature knowledge vs feature state

Separate these concepts.

Feature specification:

```
docs/features/<feature>.md
```

Feature progress:

```
.agents/state/features/<feature>.md
```

Architecture:

```
docs/architecture/
```

Current project state:

```
.agents/state/CURRENT.md
```

Do not duplicate the same large content across multiple files.

---

## 35.6. Documentation routing

Whenever a feature document references:

```
Related Architecture
Related Services
Related Decisions
Related Tests
```

follow only those references that are relevant to the current task.

Do not recursively read unrelated documentation.

---

## 35.7. Source code is always inspected

Documentation is a guide, not proof.

Before modifying code:

1. Read the relevant documentation.
2. Inspect actual source code.
3. Inspect tests.
4. Compare documentation with implementation.

If documentation conflicts with source code, treat actual verified code as authoritative and update the relevant documentation/state.

---

## 35.8. Search before reading large files

If the required information is inside a large file, search for the relevant symbol, heading, class, function or keyword first.

Read the smallest useful section.

Do not load an entire large file when only one section is required.

---

## 35.9. Context budget discipline

Minimize unnecessary context.

Prefer:

```
map
→
relevant state
→
relevant specification
→
relevant architecture
→
source
→
tests
```

Avoid:

```
entire documentation tree
+
entire source tree
+
entire Git history
```

unless the task genuinely requires repository-wide analysis.

---

## 35.10. Resume behavior

When the user says:

```
Continue
```

first read:

```
AGENTS.md
.agents/map/PROJECT_MAP.md
.agents/state/CURRENT.md
```

Then inspect Git:

```
git status
git branch --show-current
git log --oneline -10
```

Use CURRENT.md to determine what to read next.

Do not restart project analysis from zero.

Do not reread unrelated documentation.

---

## 35.11. Update routing

After meaningful work:

Update only the relevant state files.

For example:

Remove Background:

```
.agents/state/features/remove-background.md
.agents/state/CURRENT.md
```

Do not rewrite unrelated feature states.

---

## 35.12. Documentation maintenance

When implementation changes an architecture decision, API, file location or behavior:

Update the smallest relevant documentation file.

Do not create a giant new document.

Keep documentation modular.

---

## 35.13. Mapping must remain accurate

Whenever:

* a feature is added
* a feature file moves
* architecture documentation moves
* a state file is created
* an important project directory changes

update:

```
.agents/map/PROJECT_MAP.md
```

The map is the index of the project and must remain accurate.

---

## 35.14. Core rule

The agent should always be able to answer:

```
"Where is the information I need?"
```

before asking:

```
"What is written in that information?"
```

Use PROJECT_MAP.md as the routing layer.

The goal is:

```
FIND → READ → IMPLEMENT
```

not:

```
READ EVERYTHING → THINK → IMPLEMENT
```
