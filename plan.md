# DEVIMAGE — DEVELOPER IMAGE TOOLBOX

## Master Implementation Plan

## 1. Mục tiêu sản phẩm

Xây dựng một phần mềm desktop Windows tên **DevImage**, là bộ công cụ xử lý ảnh độc lập dành cho Developer, Web Developer, Designer kỹ thuật và nhân viên Ecommerce/Marketing.

DevImage KHÔNG phải Photoshop.

DevImage KHÔNG phải một image editor phức tạp.

DevImage là một "Developer Image Toolbox":

* mở nhanh
* chọn đúng công cụ
* kéo ảnh vào
* chỉnh vài thông số
* xử lý
* lưu kết quả
* kết thúc

Mỗi tính năng hoạt động độc lập.

Ví dụ:

* Resize chỉ Resize.
* Compress chỉ Compress.
* Convert chỉ Convert.
* Crop chỉ Crop.
* Remove Background chỉ Remove Background.

Không tự động nối các thao tác thành pipeline.

Không yêu cầu người dùng tạo project.

Không yêu cầu database.

Không yêu cầu account.

Không yêu cầu server.

Các chức năng xử lý ảnh thông thường phải hoạt động hoàn toàn offline.

AI chỉ được gọi khi người dùng chủ động sử dụng tính năng AI.

---

# 2. Kiến trúc công nghệ được chốt

## Desktop

Python-first desktop application.

Stack:

* Python 3.13.x
* PySide6
* Qt Quick / QML
* Python backend logic
* PyInstaller
* Windows Installer

Không sử dụng Electron cho phiên bản này.

Không sử dụng FastAPI.

Không sử dụng Node.js cho runtime của ứng dụng.

Frontend và backend nằm trong cùng một Python desktop application.

Kiến trúc:

```
DevImage
    │
    ├── PySide6
    │     └── QML UI
    │
    ├── Application Layer
    │
    ├── Tool Services
    │
    ├── Image Engine
    │     ├── Pillow
    │     ├── OpenCV
    │     └── NumPy
    │
    ├── AI Engine
    │     ├── ONNX Runtime
    │     ├── Background Removal
    │     ├── OCR
    │     └── Gemini API
    │
    └── File System
```

---

# 3. Nguyên tắc kiến trúc

## 3.1. Mỗi tool độc lập

Không xây pipeline engine.

Không cho phép tool này tự động gọi tool khác.

Mỗi tool có:

* UI riêng
* service riêng
* configuration riêng
* validation riêng
* processing function riêng
* test riêng

Ví dụ:

```
tools/
    resize/
    compress/
    convert/
    crop/
    remove_background/
    inspector/
    color_picker/
    rename/
    ocr/
    ai/
```

---

# 4. Các tính năng

## PHASE MVP

### 1. Remove Background

Tính năng quan trọng nhất.

Input:

* JPG
* JPEG
* PNG
* WebP
* BMP
* các format mà engine hỗ trợ

Output:

* PNG
* WebP

UI:

* Drag & Drop
* Browse
* Original / Result preview
* zoom preview
* transparent checkerboard
* xử lý một ảnh
* batch nhiều ảnh
* progress
* cancel
* save
* open output folder

Options:

* Crop transparent area
* Keep original dimensions
* Center result
* Output PNG/WebP
* Preserve/remove metadata nếu khả thi

Processing:

* local AI model
* ONNX Runtime
* background removal engine
* không gửi ảnh lên cloud

Thiết kế model phải tách biệt khỏi UI.

Ví dụ:

```
BackgroundRemovalEngine
    ├── model manager
    ├── inference
    ├── alpha matte
    └── result export
```

Cho phép thay model về sau.

---

## 2. Resize

Chức năng độc lập.

Options:

* Width
* Height
* Keep aspect ratio
* Don't enlarge
* Contain
* Cover
* Stretch

Presets:

* 1920
* 1600
* 1200
* 1024
* 768
* 480

Cho phép batch processing.

UI phải hiển thị:

* original dimensions
* target dimensions
* estimated output size nếu có thể

Không thay đổi file gốc.

---

## 3. Compress

Chức năng độc lập.

Options:

* Quality
* format giữ nguyên
* WebP
* JPEG
* PNG optimization
* remove metadata

Preview:

```
Original
3.2 MB

Estimated
680 KB

Reduction
78.7%
```

Cho phép:

* Single
* Batch

Không tự convert sang WebP nếu người dùng không chọn.

---

## 4. Convert

Chức năng độc lập.

Input:

* PNG
* JPG/JPEG
* WebP
* BMP
* TIFF
* các format được engine hỗ trợ

Output:

* PNG
* JPEG
* WebP
* AVIF nếu environment hỗ trợ ổn định

Options:

* quality
* metadata
* output filename
* output folder

Ví dụ:

```
product.png
      ↓
WebP
      ↓
product.webp
```

Không resize.

Không compress thêm ngoài logic cần thiết của format.

---

## 5. Crop

Chức năng độc lập.

Modes:

* Original
* 1:1
* 4:3
* 3:4
* 16:9
* 9:16
* Custom

Có crop rectangle kéo bằng chuột.

Có:

* zoom
* pan
* reset
* rotate 90°
* center crop

Không xây thành Photoshop.

Không có:

* brush
* layer
* mask editor
* filter editor
* complex retouching

---

# 5. Developer Tools

## 6. Image Inspector

Không xử lý file.

Chỉ đọc và phân tích.

Hiển thị:

* filename
* full path
* extension
* format
* width
* height
* aspect ratio
* file size
* color mode
* alpha
* DPI
* EXIF
* metadata
* estimated optimization information

Có:

```
Copy All
```

và:

```
Copy JSON
```

Ví dụ:

```
{
  "filename": "product.webp",
  "width": 1200,
  "height": 1200,
  "format": "WEBP",
  "size": 284312,
  "has_alpha": true
}
```

---

## 7. Color Picker

Cho phép click vào ảnh.

Hiển thị:

* HEX
* RGB
* HSL

Ví dụ:

```
HEX
#D9A441

RGB
217, 164, 65
```

Có nút:

* Copy HEX
* Copy RGB
* Copy CSS

Có thể export:

```
--color-primary: #D9A441;
```

và:

```
{
  "hex": "#D9A441",
  "rgb": [217,164,65]
}
```

---

## 8. Rename

Batch rename.

Ví dụ:

```
product-01.jpg
product-02.jpg
product-03.jpg
```

Pattern:

```
product-{n}
```

Options:

* starting number
* zero padding
* lowercase
* uppercase
* replace spaces
* remove special characters

Trước khi thực hiện phải có preview:

```
old-name.jpg
    ↓
product-001.webp
```

Không rename nếu có conflict mà không cảnh báo.

---

## 9. Copy Path

Context menu:

* Copy Path
* Copy Filename
* Copy Directory
* Open Folder

Ví dụ:

```
D:\Projects\addp\images\product.webp
```

Có thể hỗ trợ keyboard shortcut.

---

# 6. OCR

## 10. OCR Tool

Hoạt động độc lập.

Input:

* image
* screenshot

Output:

* extracted text

UI:

```
Image Preview
        │
        ▼
     OCR
        │
        ▼
Detected Text
```

Có:

* Copy Text
* Copy as Markdown
* Copy as plain text

Cho phép chọn ngôn ngữ nếu engine hỗ trợ.

Ưu tiên:

* Vietnamese
* English
* German

Ưu tiên OCR local.

Sử dụng RapidOCR + ONNX Runtime hoặc engine tương đương nếu compatibility tốt hơn.

Không sử dụng OCR cloud mặc định.

---

# 7. AI Tools

## 11. Analyze Image

AI được gọi chỉ khi user bấm.

Input:

* image

Output:

* short description
* objects
* subject
* background
* visible text
* likely use case

Không chỉnh sửa ảnh.

---

## 12. Generate Alt Text

Input:

* image

Output:

Một đoạn alt text phù hợp cho web.

Ví dụ:

```
Product package of Glucare Plus dietary supplement
displayed on a clean background.
```

Có:

* Generate
* Regenerate
* Copy

---

## 13. AI Command

Đây là tính năng AI nâng cao.

User nhập:

```
"Resize ảnh này xuống 1200px"
```

hoặc:

```
"Convert tất cả ảnh này sang webp quality 82"
```

AI không được tự viết code.

AI phải trả về một cấu trúc JSON đã được schema hóa.

Ví dụ:

```
{
  "operation": "resize",
  "width": 1200,
  "keep_aspect_ratio": true
}
```

Application phải validate JSON.

Sau đó gọi local tool tương ứng.

AI chỉ quyết định "user muốn làm gì".

Python engine mới thực sự xử lý ảnh.

Không cho AI thực thi:

* shell
* Python code
* arbitrary command
* filesystem command

---

# 8. Home UI

Home phải cực kỳ đơn giản.

Header:

```
DevImage                         Settings
```

Hero:

```
Developer Image Toolbox

Fast image utilities for developers.
```

Tool cards.

IMAGE TOOLS:

```
Remove Background
Resize
Compress
Convert
Crop
```

DEVELOPER TOOLS:

```
Inspector
Color Picker
OCR
Rename
Copy Path
```

AI:

```
Analyze Image
Alt Text
AI Command
```

Mỗi tool card:

* icon
* title
* short description
* keyboard shortcut nếu có

Không tạo sidebar quá lớn.

Mục tiêu:

User mở app trong 2 giây phải hiểu:

"Tool nào mình cần?"

---

# 9. Tool Page Architecture

Mỗi tool page có cấu trúc:

```
Header
    ← Back
    Tool name
    Settings

Input Area

Options

Preview

Action

Result

Save
```

Không dùng một workspace chung cho tất cả tool.

Ví dụ:

```
/tools/resize
/tools/compress
/tools/convert
/tools/crop
/tools/remove-background
```

---

# 10. Drag & Drop

Global application support:

* drag file vào tool
* drag nhiều file
* drag folder nếu tool hỗ trợ batch

Tool tự kiểm tra format.

Nếu không hỗ trợ:

```
Unsupported file format
```

Không crash.

---

# 11. Batch Processing

Batch không phải pipeline.

Batch chỉ có nghĩa:

```
1 operation
+
multiple files
```

Ví dụ:

```
25 JPG
   ↓
Resize
   ↓
25 resized JPG
```

hoặc:

```
25 JPG
   ↓
Remove Background
   ↓
25 PNG
```

Không được:

```
Remove BG
   ↓
Resize
   ↓
Compress
```

trừ khi sau này user chủ động tạo một tính năng workflow riêng.

MVP không có workflow.

---

# 12. Processing Architecture

Tạo abstraction chung:

```
ImageProcessor
```

Nhưng không biến nó thành pipeline.

Các service:

```
ResizeService
CompressService
ConvertService
CropService
BackgroundRemovalService
InspectorService
ColorService
RenameService
OCRService
AIService
```

Mỗi service chịu trách nhiệm duy nhất cho chức năng của nó.

---

# 13. Threading / Worker

Không chạy image processing nặng trên UI thread.

Sử dụng:

* QThreadPool
* QRunnable
* signal/slot
* worker abstraction

Ví dụ:

```
UI
  ↓
Worker
  ↓
Image Service
  ↓
Result
  ↓
UI
```

UI phải luôn responsive.

Trong batch:

```
File 1  ████████
File 2  █████
File 3  ███
File 4  waiting
```

Có:

* percentage
* current file
* total files
* cancel

---

# 14. File Handling

Ứng dụng không copy ảnh vào database.

Không database.

Không cloud storage.

Nguyên tắc:

```
Input file
    ↓
Process in memory / temporary file
    ↓
Output file
```

Mặc định:

```
<input folder>\DevImage_Output\
```

hoặc cho phép user chọn:

```
Save As
```

Không overwrite file gốc mặc định.

Nếu tên output tồn tại:

```
file (1).webp
file (2).webp
```

hoặc cho phép:

* overwrite
* skip
* rename

---

# 15. Preview Engine

Không load ảnh full-resolution trực tiếp cho UI nếu ảnh cực lớn.

Tạo thumbnail/proxy để preview.

Nguyên tắc:

```
Original 8000x6000
      ↓
Preview 1600x1200
```

Processing vẫn dùng original.

Preview sử dụng image cache.

Cache nằm trong thư mục temporary của app.

---

# 16. Settings

Settings page:

## General

* Theme
* Language
* Default output folder
* Auto open output folder
* Confirm before overwrite

## Processing

* Default quality
* Default output format
* Batch concurrency

## AI

* Gemini API Key
* Model
* Enable AI
* Network permission

## Models

* Background Removal Model
* OCR Model

Có:

```
Installed
Download
Update
Remove
```

API key không được hard-code.

Không lưu API key plain text trong source.

Sử dụng Windows credential/keyring mechanism.

---

# 17. Model Management

Các model AI lớn không nên nhét trực tiếp vào source code.

Tách:

```
app/
models/
```

Ví dụ:

```
models/
    background-removal/
        model.onnx
        metadata.json

    ocr/
        det/
        cls/
        rec/
```

Model Manager chịu trách nhiệm:

* kiểm tra tồn tại
* version
* checksum
* download
* update
* delete
* validate

First launch:

```
Background Removal Model
[Download]
```

Không bắt user tải model nếu họ chưa dùng tính năng đó.

---

# 18. AI Network Architecture

Phần local:

```
Resize
Compress
Convert
Crop
Inspector
Color Picker
Rename
OCR
Background Removal
```

phải không cần internet.

Phần cần Internet:

```
Analyze Image
Generate Alt Text
AI Command
```

Gemini API chỉ được gọi khi user bấm.

Không upload ảnh ngầm.

UI phải thể hiện:

```
This feature sends the selected image to Gemini.
```

---

# 19. Error Handling

Không để exception hiện ra thành stack trace cho user.

Tất cả lỗi phải chuyển thành:

```
Title
Description
Possible cause
Suggested action
```

Ví dụ:

```
Unable to process image

The selected file may be corrupted or unsupported.

[Try Another File]
```

Log kỹ thuật phải lưu riêng.

Ví dụ:

```
logs/
    app.log
    errors.log
```

Không log:

* API key
* sensitive file contents
* image binary data

---

# 20. Logging

Dùng Python logging.

Levels:

```
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Production mặc định:

```
INFO
```

Development:

```
DEBUG
```

Có log:

* app startup
* tool start
* tool complete
* duration
* error
* model loading
* model version

Không spam console.

---

# 21. Project Structure

Tạo repository:

```
devimage/
│
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
│
├── src/
│   └── devimage/
│       │
│       ├── main.py
│       │
│       ├── app/
│       │   ├── application.py
│       │   ├── settings.py
│       │   └── paths.py
│       │
│       ├── core/
│       │   ├── models.py
│       │   ├── errors.py
│       │   ├── signals.py
│       │   └── types.py
│       │
│       ├── engine/
│       │   ├── image/
│       │   │   ├── pillow_engine.py
│       │   │   ├── opencv_engine.py
│       │   │   └── metadata.py
│       │   │
│       │   ├── ai/
│       │   │   ├── gemini.py
│       │   │   └── command_parser.py
│       │   │
│       │   ├── background_removal/
│       │   │   ├── engine.py
│       │   │   └── model_manager.py
│       │   │
│       │   └── ocr/
│       │       ├── engine.py
│       │       └── model_manager.py
│       │
│       ├── tools/
│       │   ├── resize/
│       │   ├── compress/
│       │   ├── convert/
│       │   ├── crop/
│       │   ├── remove_background/
│       │   ├── inspector/
│       │   ├── color_picker/
│       │   ├── rename/
│       │   ├── copy_path/
│       │   ├── ocr/
│       │   ├── analyze/
│       │   ├── alt_text/
│       │   └── ai_command/
│       │
│       ├── workers/
│       │   ├── task.py
│       │   └── worker_pool.py
│       │
│       ├── services/
│       │   ├── file_service.py
│       │   ├── preview_service.py
│       │   ├── clipboard_service.py
│       │   └── model_service.py
│       │
│       └── ui/
│           ├── qml/
│           │   ├── Main.qml
│           │   ├── AppShell.qml
│           │   ├── Home.qml
│           │   │
│           │   ├── components/
│           │   ├── dialogs/
│           │   ├── common/
│           │   │
│           │   └── tools/
│           │       ├── ResizePage.qml
│           │       ├── CompressPage.qml
│           │       ├── ConvertPage.qml
│           │       ├── CropPage.qml
│           │       ├── RemoveBackgroundPage.qml
│           │       ├── InspectorPage.qml
│           │       ├── ColorPickerPage.qml
│           │       ├── RenamePage.qml
│           │       ├── OcrPage.qml
│           │       ├── AnalyzePage.qml
│           │       ├── AltTextPage.qml
│           │       └── AiCommandPage.qml
│           │
│           └── bridge/
│               └── backend_bridge.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── assets/
│   ├── icons/
│   └── branding/
│
├── models/
│
├── scripts/
│   ├── dev.ps1
│   ├── test.ps1
│   └── build.ps1
│
└── packaging/
    ├── devimage.spec
    └── installer/
```

---

# 22. Dependency Strategy

Core:

```
PySide6
Pillow
OpenCV
NumPy
Pydantic
```

AI/local vision:

```
onnxruntime
rembg
rapidocr
```

AI cloud:

```
google-genai
```

Development:

```
pytest
pytest-qt
ruff
mypy nếu thực sự cần
PyInstaller
```

Không cài PyTorch trừ khi một model thực sự cần nó.

Không cài quá nhiều framework AI chỉ để "cho có".

---

# 23. Thiết kế UI

Phong cách:

```
Modern
Minimal
Developer-oriented
Fast
Clean
```

Không làm giao diện giống Photoshop.

Có thể lấy cảm hứng từ:

* VS Code
* Raycast
* PowerToys
* modern developer tools

Màu sắc:

* nền sáng/xám rất nhẹ hoặc dark mode
* accent duy nhất
* card gọn
* icon rõ
* typography sạch

Không để màn hình có quá nhiều text.

---

# 24. Keyboard shortcuts

Nên hỗ trợ:

```
Ctrl + O       Open
Ctrl + S       Save
Ctrl + Shift + O
               Open Output Folder

Esc            Cancel/close dialog
```

Tool-specific shortcut có thể thêm sau.

---

# 25. Accessibility

Ít nhất:

* keyboard navigation
* visible focus state
* readable contrast
* minimum clickable area
* clear error state
* không chỉ dựa vào màu để báo trạng thái

---

# 26. Test Strategy

## Unit tests

Test:

* resize calculation
* aspect ratio
* crop calculation
* compression config
* format conversion
* filename generation
* collision handling
* metadata extraction
* color conversion
* AI command JSON validation

## Integration tests

Test:

```
image input
    ↓
service
    ↓
output file
```

Cho từng tool.

## GUI tests

Test:

* open app
* navigate tool
* drop image
* process
* save
* error state

## Background removal tests

Có test fixture thực tế.

Kiểm tra:

* output tồn tại
* alpha channel
* dimensions
* file opens correctly
* batch correctness

## OCR tests

Test bằng fixture chứa:

* English
* Vietnamese
* numbers

---

# 27. Performance Targets

Không đưa ra con số tuyệt đối khi chưa benchmark.

Thay vào đó phải benchmark:

### Startup

* cold startup
* warm startup

### Resize

* 1 image
* 20 images
* 100 images

### Compress

* JPG
* PNG
* WebP

### Background Removal

* 1 image
* 10 images
* large image

### OCR

* screenshot
* product image

Theo dõi:

* execution time
* memory
* CPU
* GPU nếu có

Không tối ưu mù.

Benchmark trước, tối ưu sau.

---

# 28. Resource Management

Ứng dụng phải tự giải phóng:

* PIL images
* OpenCV matrices
* ONNX sessions
* model memory
* temporary files
* worker references

Không giữ full-resolution image trong RAM nếu không cần.

Batch concurrency không được mở quá nhiều worker mặc định.

Background removal model phải được load một lần và reuse trong cùng session nếu engine hỗ trợ.

---

# 29. Build Strategy

Trong development:

```
python -m devimage
```

hoặc tương đương.

Build:

```
PyInstaller
```

Ưu tiên:

```
onedir
```

Sau đó dùng installer để đóng gói.

Installer phải cài:

```
DevImage
    ├── application
    ├── Python runtime
    ├── libraries
    ├── models nếu được bundle
    └── assets
```

Người dùng cuối không cần:

* Python
* pip
* Node.js
* Docker
* runtime dependency riêng

---

# 30. Portable Mode

Nên hỗ trợ sau MVP:

```
DevImage-Portable.zip
```

User giải nén và chạy.

Không cần installer.

---

# 31. First Launch

Lần đầu mở:

```
Welcome to DevImage

Fast image tools for developers.

[Continue]
```

Sau đó:

```
Optional AI Models

Background Removal
[Download]

OCR
[Download]
```

Có thể Skip.

App vẫn dùng được toàn bộ các tool local cơ bản.

---

# 32. Gemini API

Settings:

```
Gemini API Key
[****************]

[Test Connection]
```

Không bắt buộc.

Nếu không có API key:

```
Local tools continue working.
```

AI tools hiển thị:

```
Gemini API key is not configured.

[Open Settings]
```

Không crash.

---

# 33. AI Command Security

AI Command chỉ cho phép schema:

```
resize
compress
convert
crop
rename
```

Ví dụ:

```
{
  "operation": "convert",
  "format": "webp",
  "quality": 82
}
```

Application phải:

1. Parse JSON
2. Validate schema
3. Validate allowed operation
4. Validate parameters
5. Show user preview
6. User presses Apply
7. Local service executes

Không bao giờ:

```
AI → arbitrary Python code
```

---

# 34. Không làm trong MVP

KHÔNG triển khai:

* layers
* brush
* clone stamp
* Photoshop-like editor
* timeline
* animation editor
* video editing
* cloud storage
* account
* collaboration
* database
* asset management system
* website builder
* screenshot-to-code
* full website audit
* autonomous AI agent
* custom workflow builder
* plugin marketplace

Những thứ này chỉ được xem xét sau khi core product ổn định.

---

# 35. Thứ tự triển khai

## Phase 0 — Foundation

1. Tạo repository
2. Setup Python
3. Setup virtual environment
4. Setup pyproject.toml
5. Setup PySide6
6. Setup QML
7. Setup logging
8. Setup settings
9. Setup testing
10. Setup linting
11. Setup Git

Acceptance:

* app mở được
* cửa sổ desktop xuất hiện
* QML load
* Python/QML communication hoạt động
* test chạy được

---

## Phase 1 — Application Shell

1. MainWindow
2. AppShell
3. Home
4. Navigation
5. Header
6. Tool Cards
7. Settings
8. Toast
9. Error Dialog
10. File picker
11. Drag and Drop

Acceptance:

User có thể:

```
mở app
chọn tool
quay lại home
mở ảnh
xem preview
```

---

## Phase 2 — Core Image Tools

Triển khai từng tool riêng:

1. Resize
2. Compress
3. Convert
4. Crop

Mỗi tool phải hoàn chỉnh trước khi sang tool tiếp theo.

Không tạo abstraction quá mức chỉ để "DRY".

Acceptance mỗi tool:

* UI hoàn chỉnh
* single image
* batch
* progress
* error handling
* output
* tests

---

## Phase 3 — Remove Background

1. Model Manager
2. Download model
3. Verify model
4. Load model
5. Single processing
6. Batch processing
7. Preview
8. Transparency checker
9. Progress
10. Cancel
11. Save
12. Memory cleanup

Acceptance:

10 ảnh xử lý liên tiếp mà app không crash và UI vẫn responsive.

---

## Phase 4 — Developer Tools

Triển khai:

1. Inspector
2. Color Picker
3. Rename
4. Copy Path

Mỗi tool độc lập.

---

## Phase 5 — OCR

1. RapidOCR integration
2. Model management
3. OCR service
4. OCR UI
5. Copy result
6. Language configuration
7. Tests

---

## Phase 6 — AI

1. Gemini client
2. Secure API key storage
3. Connection test
4. Analyze Image
5. Generate Alt Text
6. AI Command
7. JSON schema
8. Pydantic validation
9. Preview before execute
10. Error handling

---

## Phase 7 — Polish

1. Dark mode
2. Light mode
3. Animations
4. keyboard shortcuts
5. empty states
6. loading states
7. progress states
8. better error messages
9. icons
10. application icon
11. About dialog

---

## Phase 8 — Packaging

1. PyInstaller
2. one-folder build
3. model path handling
4. packaged runtime testing
5. installer
6. uninstall
7. portable build
8. clean-machine testing

---

# 36. Definition of Done

DevImage MVP chỉ được coi là hoàn thành khi:

* build được trên Windows
* cài được từ installer
* chạy trên máy không cài Python
* Resize hoạt động
* Compress hoạt động
* Convert hoạt động
* Crop hoạt động
* Remove Background hoạt động
* Inspector hoạt động
* Color Picker hoạt động
* Rename hoạt động
* Copy Path hoạt động
* OCR hoạt động
* AI Analyze hoạt động
* Alt Text hoạt động
* AI Command hoạt động
* batch hoạt động
* cancel hoạt động
* error handling hoạt động
* logs hoạt động
* settings hoạt động
* không yêu cầu database
* không yêu cầu server
* local features không cần Internet

---

# 37. Nguyên tắc quan trọng nhất cho AI coding agent

AI implementation agent phải:

1. Đọc toàn bộ architecture trước khi code.
2. Không tự ý thay đổi tech stack.
3. Không thêm Electron.
4. Không thêm FastAPI.
5. Không thêm database.
6. Không biến app thành pipeline.
7. Không gộp mọi image operation vào một service khổng lồ.
8. Không viết code xử lý ảnh trong QML.
9. Không gọi network cho local tools.
10. Không hard-code API key.
11. Không commit model binary lớn vào Git.
12. Mỗi feature phải có test.
13. Mỗi phase phải chạy được trước khi sang phase tiếp theo.
14. Ưu tiên code đơn giản, dễ bảo trì hơn abstraction phức tạp.
15. Không thêm feature ngoài scope nếu không cần thiết.

---

# 38. Mục tiêu cuối cùng

DevImage phải cho người dùng cảm giác:

```
"Tôi cần xử lý một việc với ảnh."

Mở DevImage.

Chọn tool.

Kéo ảnh.

Xử lý.

Lưu.

Xong.
```

Đó là sản phẩm.

Không phải một Photoshop mini.

Không phải một workflow engine.

Không phải một AI agent phức tạp.

Đây là một **Developer Image Toolbox**.
