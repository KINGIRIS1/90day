# 🏗️ Kiến trúc Desktop App - OCR Engine

## 📊 Tổng quan

Đây là **Desktop Application** (Electron), KHÔNG phải web app.
→ **KHÔNG CẦN** backend server riêng!

## 🔄 Luồng hoạt động

```
┌─────────────────────────────────────────────────────────────┐
│                    DESKTOP APP                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [React Frontend]                                           │
│         ↓ IPC (Inter-Process Communication)                 │
│  [Electron Main Process]                                    │
│         ↓ Spawn Python Process                              │
│  [Python Scripts]                                           │
│         ↓ HTTP Request                                      │
│  [Gemini API] (Google Cloud)                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📂 Cấu trúc

### 1. Frontend (React)
**Location**: `/app/desktop-app/src/`

**Components**:
- `DesktopScanner.js` - Tab quét file đơn
- `OnlyGCNScanner.js` - Tab Only GCN
- `Settings.js`, `CloudSettings.js` - Cài đặt

**Role**: 
- UI/UX
- User interactions
- Gọi Electron APIs qua IPC

### 2. Electron Main Process
**Location**: `/app/desktop-app/public/electron.js`

**Role**: 
- "Backend" của desktop app
- Quản lý window
- Xử lý IPC requests từ frontend
- Spawn Python processes
- File system operations
- PDF merge operations

**Key Functions**:
```javascript
ipcMain.handle('process-document-offline', ...)  // Quét file
ipcMain.handle('merge-by-short-code', ...)       // Gộp PDF
ipcMain.handle('select-files', ...)              // File picker
ipcMain.handle('open-external', ...)             // Mở file
```

### 3. Python Scripts
**Location**: `/app/desktop-app/python/`

**Main Scripts**:
- `process_document.py` - Xử lý OCR cho 1 file
- `batch_processor.py` - Xử lý batch nhiều files
- `ocr_engine_gemini_flash.py` - Gemini API integration
- `pdf_splitter.py` - Tách PDF thành pages

**Role**:
- OCR processing
- Gọi Gemini API
- Image processing
- PDF handling

### 4. Gemini API (External)
**Provider**: Google Cloud

**Models Used**:
- `gemini-2.5-flash` - OCR và classification

**API Calls**:
```python
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content([prompt, image])
```

## ⚙️ Cách hoạt động OCR

### Flow chi tiết:

```
1. User chọn file trong UI (React)
   ↓
2. Frontend gọi: window.electronAPI.processDocumentOffline(filePath)
   ↓
3. Electron nhận IPC request
   ↓
4. Electron spawn Python process:
   python process_document.py <filePath> <apiKey> <settings>
   ↓
5. Python script:
   - Load image/PDF
   - Nếu PDF → Split thành pages (pdf_splitter.py)
   - Resize image nếu cần
   - Encode base64
   - Call Gemini API với prompt + image
   ↓
6. Gemini API xử lý:
   - OCR text từ image
   - Phân loại document type
   - Extract metadata (ngày cấp, etc.)
   - Trả về JSON response
   ↓
7. Python script parse response
   ↓
8. Python print JSON kết quả ra stdout
   ↓
9. Electron đọc stdout, parse JSON
   ↓
10. Electron trả kết quả về Frontend qua IPC
   ↓
11. Frontend hiển thị kết quả trong UI
```

## 🔑 API Key Management

### Lưu trữ:
- **Location**: Electron store (local machine)
- **File**: `~/.config/90dayChonThanh/config.json` (Linux/Mac)
- **File**: `%APPDATA%\90dayChonThanh\config.json` (Windows)

### Cách set:
1. Mở Settings → Cloud Settings
2. Nhập Gemini API key
3. Click "Lưu cài đặt"
4. Key được lưu local, KHÔNG gửi lên server

### Sử dụng:
```javascript
// electron.js
const store = new Store();
const apiKey = store.get('geminiApiKey');

// Pass to Python
spawn(python, ['process_document.py', filePath, apiKey, ...])
```

## 🚀 Batch Processing

### Sequential Mode:
```
File 1 → Gemini API → Result 1
File 2 → Gemini API → Result 2
File 3 → Gemini API → Result 3
```
- Chậm nhất
- Đơn giản
- Ít lỗi

### Smart Batch Mode:
```
Batch [File 1, 2, 3] → Gemini API (1 call) → Results [1, 2, 3]
Batch [File 4, 5, 6] → Gemini API (1 call) → Results [4, 5, 6]
```
- Nhanh hơn 5-10x
- Tiết kiệm 80-90% chi phí
- Batch size tùy chỉnh (2-20 files)

## 📁 PDF Processing

### Multi-page PDF:
```
1. User chọn PDF 34 trang
   ↓
2. Python: pdf_splitter.py
   - Convert PDF → 34 images (png)
   - Save to /tmp/
   ↓
3. Batch processing:
   - Batch 1: Pages 1-8 → Gemini
   - Batch 2: Pages 9-16 → Gemini
   - ...
   ↓
4. Merge results
   ↓
5. Return 34 page results to frontend
   ↓
6. Frontend displays 34 separate cards
```

## ❓ Câu hỏi thường gặp

### Q: Có cần setup backend server không?
**A**: **KHÔNG**. Đây là desktop app, Electron chính là backend.

### Q: API key lưu ở đâu?
**A**: Local trên máy user (Electron store), KHÔNG lên cloud.

### Q: Data có gửi lên server không?
**A**: KHÔNG. Chỉ gửi lên Gemini API (Google) để OCR.

### Q: Cần internet không?
**A**: CẦN. Để gọi Gemini API. Không có offline mode.

### Q: Có thể dùng API key riêng không?
**A**: CÓ. Nhập API key của bạn trong Settings.

### Q: Gemini API free không?
**A**: Có free tier với giới hạn. Chi tiết: https://ai.google.dev/pricing

### Q: Data có bị lưu trên Google không?
**A**: Gemini API không lưu data theo policy. Chi tiết: https://ai.google.dev/gemini-api/terms

## 🔧 Setup Requirements

### User cần:
1. ✅ Gemini API key (lấy tại: https://makersuite.google.com/app/apikey)
2. ✅ Python 3.8+ (bundled trong app)
3. ✅ Poppler (để xử lý PDF)
4. ✅ Internet connection

### KHÔNG CẦN:
- ❌ Backend server
- ❌ Database
- ❌ Docker
- ❌ Cloud deployment
- ❌ API endpoint riêng

## 📊 Performance

### Factors:
1. **Internet speed** - Ảnh hưởng API calls
2. **Batch size** - Lớn hơn = nhanh hơn (nhưng rủi ro timeout)
3. **Image size** - Lớn hơn = chậm hơn (auto resize to 2000x2800)
4. **API quota** - Free tier có giới hạn requests/minute

### Optimization:
- Resize images before sending
- Use batch mode for multiple files
- Smart batch size selection (8 recommended)
- Timeout 300s for large PDFs

## 🎯 Summary

**Kiến trúc**: Desktop app (Electron + React + Python)
**Backend**: Electron main process (local)
**OCR Engine**: Gemini API (Google Cloud)
**API Key**: Local storage (user's machine)
**Setup**: Chỉ cần API key, KHÔNG cần backend server

→ **App hoàn toàn standalone, không cần infrastructure backend riêng!**
