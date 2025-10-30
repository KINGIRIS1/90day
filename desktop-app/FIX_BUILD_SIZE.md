# 🔧 Sửa lỗi Build thiếu Dependencies

## ⚠️ Vấn đề

File build chỉ có **84MB** thay vì **150-200MB** → Thiếu dependencies quan trọng

## ✅ Đã sửa

1. **Cập nhật `package.json`**:
   - ✅ Thêm `node_modules/**/*` vào files
   - ✅ Thêm `asarUnpack` cho Python và electron-store
   - ✅ Xóa duplicate `extraResources`

2. **Cập nhật build scripts**:
   - ✅ `build-windows.bat` - Thêm bước clean dist/
   - ✅ `build-windows.ps1` - Thêm bước clean dist/
   - ✅ `verify-build.bat` - Script kiểm tra build

## 🚀 Hướng dẫn build lại

### Bước 1: Xóa build cũ
```bash
rmdir /s /q dist
rmdir /s /q build
```

### Bước 2: Clean install dependencies
```bash
rmdir /s /q node_modules
yarn cache clean
yarn install
```

### Bước 3: Build lại
```bash
build-windows.bat
```

### Bước 4: Kiểm tra build
```bash
verify-build.bat
```

## 📊 Checklist sau khi build

Kiểm tra các điều sau:

### 1. Kích thước file
```
dist\90dayChonThanh Setup 1.1.0.exe
```
- ✅ Size: **150-200 MB** (đúng)
- ❌ Size: **< 100 MB** (thiếu dependencies)

### 2. Cấu trúc thư mục
```
dist\
├── 90dayChonThanh Setup 1.1.0.exe
├── win-unpacked\
│   ├── 90daychonhanh-desktop.exe
│   ├── resources\
│   │   ├── app.asar (80-90 MB)
│   │   └── python\  (các OCR engines)
```

### 3. Kiểm tra app.asar
```bash
npx asar list dist\win-unpacked\resources\app.asar
```

Phải có:
- ✅ `/node_modules/` (nhiều packages)
- ✅ `/build/` (React build)
- ✅ `/public/electron.js`
- ✅ `/package.json`

### 4. Kiểm tra Python folder
```bash
dir dist\win-unpacked\resources\python\
```

Phải có các file:
- ✅ `ocr_engine_gemini_flash.py`
- ✅ `ocr_engine_tesseract.py`
- ✅ `process_document.py`
- ✅ `rule_classifier.py`
- ✅ `requirements.txt`

## 🐛 Debug nếu vẫn lỗi

### Lỗi 1: File quá nhỏ
**Nguyên nhân**: electron-builder đang exclude node_modules

**Giải pháp**:
1. Check `package.json` có đúng config chưa
2. Xóa cache: `yarn cache clean`
3. Build lại với flag verbose:
```bash
npx electron-builder --win --x64 --config.asar.unpack="**/*"
```

### Lỗi 2: App crash khi chạy
**Nguyên nhân**: Thiếu dependencies runtime

**Giải pháp**:
1. Check logs: `%APPDATA%\90daychonhanh-desktop\logs\`
2. Kiểm tra `node_modules` trong app.asar
3. Thêm vào `asarUnpack` trong package.json nếu cần

### Lỗi 3: Python OCR không chạy
**Nguyên nhân**: Folder `python/` không được copy

**Giải pháp**:
1. Kiểm tra `dist\win-unpacked\resources\python\`
2. Nếu thiếu, thêm vào `extraResources` trong package.json
3. Build lại

## 📝 Config đúng trong package.json

```json
{
  "build": {
    "files": [
      "build/**/*",
      "public/electron.js",
      "public/preload.js",
      "python/**/*",
      "node_modules/**/*",
      "package.json"
    ],
    "asarUnpack": [
      "python/**/*",
      "node_modules/electron-store/**/*"
    ],
    "extraResources": [
      {
        "from": "python",
        "to": "python",
        "filter": ["**/*"]
      }
    ]
  }
}
```

## ✅ Xác nhận build thành công

Sau khi build xong, chạy:
```bash
verify-build.bat
```

Script này sẽ kiểm tra:
1. ✅ Installer tồn tại
2. ✅ Size đúng (>100MB)
3. ✅ Cấu trúc thư mục đầy đủ
4. ✅ app.asar chứa node_modules
5. ✅ Python folder có đủ files

## 🎯 Kết quả mong đợi

Sau khi build đúng:
- **Installer size**: ~180-200 MB
- **win-unpacked size**: ~400-450 MB
- **app.asar size**: ~85-90 MB
- **resources/python**: ~2-3 MB

## 💡 Tips

1. **Lần build đầu**: Lâu hơn vì tải dependencies
2. **Clean build**: Luôn xóa `dist/` trước khi build
3. **Cache**: Nếu build lỗi, xóa cache: `yarn cache clean`
4. **Disk space**: Cần ~5GB trống cho build

---

**✅ Build lại với config mới này sẽ có size đúng ~180-200MB!**
