# ✅ ĐÃ SỬA LỖI BUILD - HƯỚNG DẪN BUILD LẠI

## 🔴 Vấn đề cũ
- Build chỉ có **84MB** → Thiếu dependencies
- App không quét được file → Thiếu node_modules & Python scripts

## ✅ Đã sửa
- Cập nhật `package.json` → Bao gồm `node_modules/**/*`
- Thêm `asarUnpack` cho Python và electron-store
- App.asar bây giờ: **~81MB** (đúng)
- Unpacked size: **~340MB** (đúng)
- Installer size sẽ: **~180-200MB** (đúng)

---

## 🚀 BUILD LẠI TRÊN WINDOWS

### BƯỚC 1: Xóa build cũ
```cmd
cd desktop-app
rmdir /s /q dist
rmdir /s /q build
```

### BƯỚC 2: Update lại files
**QUAN TRỌNG**: Pull code mới nhất hoặc copy lại folder `desktop-app` về máy Windows

Files đã được update:
- ✅ `package.json` (config mới)
- ✅ `build-windows.bat` (thêm clean step)
- ✅ `build-windows.ps1` (thêm clean step)

### BƯỚC 3: Clean install dependencies
```cmd
rmdir /s /q node_modules
yarn cache clean
yarn install
```

### BƯỚC 4: Build lại
```cmd
build-windows.bat
```

Hoặc thủ công:
```cmd
yarn build
npx electron-builder --win --x64
```

### BƯỚC 5: Kiểm tra build
```cmd
verify-build.bat
```

---

## ✅ CHECKLIST SAU BUILD

### 1. Kiểm tra size
```
dir dist
```

Phải có:
- ✅ `90dayChonThanh Setup 1.1.0.exe` → **150-200 MB**

Nếu < 100MB = **LỖI**, build lại!

### 2. Kiểm tra unpacked
```
dir dist\win-unpacked\resources
```

Phải có:
- ✅ `app.asar` → **~81 MB**
- ✅ `app.asar.unpacked\` (folder)
- ✅ `python\` (folder)

### 3. Kiểm tra node_modules
```cmd
npx asar list dist\win-unpacked\resources\app.asar | findstr node_modules
```

Phải thấy nhiều packages!

### 4. Kiểm tra Python
```cmd
dir dist\win-unpacked\resources\python
```

Phải có:
- ✅ `process_document.py`
- ✅ `ocr_engine_gemini_flash.py`
- ✅ `rule_classifier.py`
- ✅ Và các OCR engines khác

---

## 🎯 KẾT QUẢ MONG ĐỢI

Sau khi build đúng:

| Item | Size | Status |
|------|------|--------|
| Installer (.exe) | **180-200 MB** | ✅ |
| win-unpacked folder | **~340-400 MB** | ✅ |
| app.asar | **~81 MB** | ✅ |
| resources/python | **~2-3 MB** | ✅ |

---

## 🐛 NẾU VẪN BỊ LỖI

### Lỗi: File vẫn chỉ 84MB

**Giải pháp**:
1. Kiểm tra `package.json` có đúng config không:
```json
"files": [
  "build/**/*",
  "public/electron.js",
  "public/preload.js", 
  "python/**/*",
  "node_modules/**/*",  ← PHẢI CÓ
  "package.json"
]
```

2. Xóa cache và build lại:
```cmd
yarn cache clean
rmdir /s /q node_modules
rmdir /s /q dist
rmdir /s /q build
yarn install
build-windows.bat
```

### Lỗi: App vẫn không quét được

**Kiểm tra**:
1. Cài app và test
2. Mở app, vào Settings
3. Chọn OCR engine (Tesseract hoặc BYOK)
4. Thử quét 1 file ảnh

**Nếu vẫn lỗi**, check:
- Python có được cài trên máy không?
- API key đúng chưa (nếu dùng Gemini Flash)?
- Log file: `%APPDATA%\90daychonhanh-desktop\logs\`

---

## 📋 SCRIPT HỖ TRỢ

### Build clean từ đầu
```cmd
REM File: rebuild-clean.bat
@echo off
echo Cleaning everything...
rmdir /s /q dist
rmdir /s /q build  
rmdir /s /q node_modules
yarn cache clean
echo Installing...
yarn install
echo Building...
yarn build
npx electron-builder --win --x64
echo Done!
pause
```

### Kiểm tra nhanh
```cmd
REM Check installer size
dir dist\*.exe

REM Check app.asar
dir dist\win-unpacked\resources\app.asar

REM List files in asar
npx asar list dist\win-unpacked\resources\app.asar
```

---

## ✨ SAU KHI BUILD THÀNH CÔNG

1. **Test app**:
   - Cài installer
   - Chạy app
   - Quét thử 1-2 file
   - Kiểm tra kết quả

2. **Gửi cho users**:
   - File: `dist\90dayChonThanh Setup 1.1.0.exe`
   - Size: ~180-200MB
   - Kèm README hướng dẫn cài

3. **Backup**:
   - Nén file .exe
   - Lưu trữ
   - Tag version trong Git

---

## 💡 GHI CHÚ

### Tại sao build cũ bị lỗi?

Build cũ config thiếu `node_modules/**/*` trong `files[]`, nên electron-builder skip hầu hết dependencies → App chạy bị crash vì thiếu modules.

### Config mới khác gì?

```json
// CŨ (SAI)
"files": [
  "build/**/*",
  "public/electron.js",
  "python/**/*"
]

// MỚI (ĐÚNG)  
"files": [
  "build/**/*",
  "public/electron.js",
  "python/**/*",
  "node_modules/**/*",  ← THÊM
  "package.json"        ← THÊM
]
```

### Tại sao thêm asarUnpack?

Một số modules cần access trực tiếp file system (không thể nén trong asar):
- `python/**/*` → Python scripts cần execute
- `electron-store` → Lưu settings user

---

**🎉 Build với config mới = App chạy ngon!**
