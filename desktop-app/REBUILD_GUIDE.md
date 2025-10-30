# 🔄 REBUILD TỪ ĐẦU - HƯỚNG DẪN HOÀN CHỈNH

## 📋 CHUẨN BỊ

**Yêu cầu:**
- ✅ Node.js 16+ đã cài
- ✅ Python 3.9+ đã cài
- ✅ ~5GB dung lượng trống
- ✅ Internet ổn định

---

## 🚀 CÁCH 1: DÙNG SCRIPT TỰ ĐỘNG (KHUYẾN NGHỊ)

### Bước 1: Chạy script
```cmd
cd C:\desktop-app
rebuild-from-scratch.bat
```

Script sẽ tự động:
1. ✅ Dọn dẹp tất cả (dist, build, node_modules)
2. ✅ Update package.json
3. ✅ Cài dependencies
4. ✅ Build React
5. ✅ Kiểm tra Python folder
6. ✅ Build Windows installer
7. ✅ Verify kết quả

### Bước 2: Đợi hoàn tất (10-15 phút lần đầu)

### Bước 3: Test
```cmd
dist\win-unpacked\90dayChonThanh.exe
```

---

## 🔧 CÁCH 2: THỦ CÔNG (NẾU SCRIPT KHÔNG CHẠY)

### Bước 1: Xóa sạch
```cmd
cd C:\desktop-app
taskkill /f /im electron.exe 2>nul
rd /s /q dist
rd /s /q build
rd /s /q node_modules
yarn cache clean
```

### Bước 2: Update package.json

**Mở Notepad:**
```cmd
notepad package.json
```

**XÓA HẾT, paste nội dung này:**

```json
{
  "name": "90daychonhanh-desktop",
  "version": "1.1.0",
  "description": "Desktop OCR app for Vietnamese land documents",
  "main": "public/electron.js",
  "homepage": ".",
  "author": "90dayChonThanh",
  "scripts": {
    "start": "set PORT=3001 && react-scripts start",
    "build": "react-scripts build",
    "electron": "electron .",
    "electron-dev": "concurrently \"set PORT=3001 && yarn start\" \"wait-on http://localhost:3001 && electron .\"",
    "electron-pack": "yarn build && electron-builder --dir",
    "electron-build": "yarn build && electron-builder"
  },
  "build": {
    "appId": "com.90daychonhanh.app",
    "productName": "90dayChonThanh",
    "asar": false,
    "files": [
      "build/**/*",
      "public/electron.js",
      "public/preload.js",
      "python/**/*",
      "node_modules/**/*",
      "package.json"
    ],
    "directories": {
      "buildResources": "assets",
      "output": "dist"
    },
    "win": {
      "target": "nsis",
      "icon": "assets/icon.png"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  },
  "dependencies": {
    "@dnd-kit/core": "^6.3.1",
    "@dnd-kit/sortable": "^10.0.0",
    "@dnd-kit/utilities": "^3.2.2",
    "axios": "^1.12.2",
    "date-fns": "^2.29.3",
    "electron-store": "^8.1.0",
    "form-data": "^4.0.4",
    "lucide-react": "latest",
    "pdf-lib": "^1.17.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "tailwindcss": "^3.4.1"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.14",
    "concurrently": "^8.2.2",
    "electron": "^28.0.0",
    "electron-builder": "^24.9.1",
    "postcss": "^8.4.21",
    "react-scripts": "5.0.1",
    "wait-on": "^7.2.0"
  }
}
```

**Lưu (Ctrl+S) và đóng**

### Bước 3: Cài dependencies
```cmd
yarn install
```

Đợi 3-5 phút.

### Bước 4: Build React
```cmd
yarn build
```

Đợi 1-2 phút.

### Bước 5: Kiểm tra Python folder
```cmd
dir python\*.py
```

Phải thấy:
- `process_document.py`
- `ocr_engine_gemini_flash.py`
- `rule_classifier.py`
- ... (các file khác)

### Bước 6: Build Windows
```cmd
npx electron-builder --win --x64
```

Đợi 3-5 phút.

### Bước 7: Verify
```cmd
dir dist\*.exe
dir dist\win-unpacked\resources\app\python
dir dist\win-unpacked\resources\app\node_modules
```

**Phải có:**
- ✅ `90dayChonThanh Setup 1.1.0.exe` (~90-100 MB)
- ✅ `python` folder trong app
- ✅ `node_modules` folder trong app

---

## ✅ TEST SAU KHI BUILD

### Test 1: Chạy portable
```cmd
dist\win-unpacked\90dayChonThanh.exe
```

### Test 2: Kiểm tra Python path
Mở app → Nhấn F12 → Console tab → Chạy:

```javascript
const path = require('path');
const app = require('electron').remote.app;
console.log('App path:', app.getAppPath());
console.log('Python path:', path.join(app.getAppPath(), 'python'));
```

### Test 3: Cài installer và test OCR
```cmd
"dist\90dayChonThanh Setup 1.1.0.exe"
```

Sau khi cài:
1. Mở app
2. Settings → Chọn "Gemini Flash (BYOK)"
3. Nhập API key
4. Test quét 1 file ảnh

---

## 🐛 TROUBLESHOOTING

### Lỗi: "offline_failed"

**Nguyên nhân:** Python script không tìm thấy hoặc không chạy được

**Check:**
```cmd
REM Tìm nơi app cài
dir "%LOCALAPPDATA%\Programs\90daychonhanh-desktop\resources\app\python"
```

**Nếu không có folder python:**
```cmd
REM Copy thủ công
xcopy /E /I "C:\desktop-app\python" "%LOCALAPPDATA%\Programs\90daychonhanh-desktop\resources\app\python"
```

### Lỗi: Build bị fail

**Giải pháp:**
1. Đảm bảo không có process nào đang chạy
2. Xóa hết và build lại
3. Check antivirus không block

### App chậm khi mở

**Bình thường với asar: false**
- Lần đầu: 5-10 giây
- Lần sau: 3-5 giây

---

## 📊 EXPECTED RESULTS

| Item | Expected | Status |
|------|----------|--------|
| Installer size | ~90-100 MB | ✅ |
| win-unpacked | ~225 MB | ✅ |
| Python folder | In app/ | ✅ |
| node_modules | In app/ | ✅ |
| OCR works | Yes | ✅ |

---

## 💡 NOTES

**Config này:**
- ✅ Đơn giản nhất (`asar: false`)
- ✅ Python chắc chắn có trong build
- ✅ node_modules đầy đủ
- ⚠️ Startup hơi chậm (acceptable)
- ⚠️ File size lớn hơn (~100MB vs 82MB)

**Trade-off:** Ổn định > Tốc độ

---

## 🎯 NEXT STEPS

Sau khi build thành công:

1. **Test kỹ:**
   - ✅ App mở được
   - ✅ Settings hoạt động
   - ✅ Gemini Flash quét được
   - ✅ File output đúng

2. **Nếu muốn tối ưu:**
   - Bật lại asar
   - Exclude files không cần
   - Lazy load modules

3. **Deploy:**
   - Upload installer
   - Viết hướng dẫn user
   - Test trên máy khác

---

**Chúc may mắn! 🚀**
