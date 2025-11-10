# 🚀 Hướng Dẫn Build All-in-One Installer - Đơn Giản Nhất

## 🎯 Mục Tiêu

Tạo **1 file .exe duy nhất** user chỉ cần double-click để cài đặt TẤT CẢ:
- ✅ Python 3.11 (tự động)
- ✅ Tesseract OCR Vietnamese (tự động)
- ✅ Desktop App (tự động)

**User KHÔNG cần:**
- ❌ Cài Python manually
- ❌ Cài Tesseract manually
- ❌ Cài pip packages manually
- ❌ Config PATH manually

**Chỉ cần: Double-click → Đợi → Done!** ✅

---

## 📋 Chuẩn Bị (Developer)

### 1. Cài NSIS (1 lần duy nhất)

**Download:**
```
URL: https://nsis.sourceforge.io/Download
File: nsis-3.09-setup.exe
```

**Install:**
- Double-click installer
- Next → Next → Install
- Verify: `C:\Program Files (x86)\NSIS\makensis.exe`

---

### 2. Download Dependencies (2 files)

**A. Python Installer (~30MB):**
```
URL: https://www.python.org/downloads/windows/
Tìm: Python 3.11.8 - Windows installer (64-bit)
File: python-3.11.8-amd64.exe
```

**B. Tesseract Installer (~50MB):**
```
URL: https://github.com/UB-Mannheim/tesseract/wiki
Tìm: tesseract-ocr-w64-setup-5.3.3.exe (hoặc version mới nhất)
File: tesseract-ocr-w64-setup-5.3.3.exe
```

**Save cả 2 files vào:**
```
desktop-app/installers/
├── python-3.11.8-amd64.exe
└── tesseract-ocr-w64-setup-5.3.3.exe
```

**Tạo folder nếu chưa có:**
```batch
cd desktop-app
mkdir installers
```

---

## 🚀 Build Steps (Cực Đơn Giản!)

### Bước 1: Chạy Script

```batch
cd desktop-app
build-allinone.bat
```

**Script sẽ tự động:**
1. ✅ Check NSIS installed
2. ✅ Build React app (yarn build)
3. ✅ Build Electron package (yarn electron-build)
4. ✅ Check Python installer exists
5. ✅ Check Tesseract installer exists
6. ✅ Create LICENSE.txt (nếu chưa có)
7. ✅ Build with NSIS → **90dayChonThanh-AllInOne-Setup.exe**

---

### Bước 2: Đợi Build Complete

**Console output:**
```
====================================================================
 BUILD ALL-IN-ONE INSTALLER
====================================================================

[1/5] Checking NSIS...
  [OK] NSIS found

[2/5] Building Electron app...
  [OK] React build complete

[2.5/5] Building Electron package...
  [OK] Electron package complete

[3/5] Checking dependencies...
  [OK] Python installer found
  [OK] Tesseract installer found

[4/5] Checking LICENSE.txt...
  [OK] LICENSE.txt exists

[5/5] Building All-in-One installer with NSIS...
  ... NSIS output ...

====================================================================
 BUILD COMPLETE!
====================================================================

 Output: 90dayChonThanh-AllInOne-Setup.exe

 Installer includes:
   - Python 3.11 (auto-install)
   - Tesseract OCR (auto-install)
   - Desktop App

 User can now double-click this ONE file to install everything!

====================================================================
```

---

## 📦 Output

**File được tạo:**
```
desktop-app/90dayChonThanh-AllInOne-Setup.exe (~150-200MB)
```

**Bao gồm:**
- Python installer (30MB)
- Tesseract installer (50MB)
- App files (70-120MB)

---

## 🎯 User Installation Flow

**User chỉ cần:**

1. **Download** `90dayChonThanh-AllInOne-Setup.exe`

2. **Double-click** file .exe

3. **Next → Next → Install**

4. **Đợi ~5-10 phút** (cài Python, Tesseract, App)

5. **Done!** Desktop có icon, click để mở app

**App sẽ:**
- ✅ Tự detect Python (đã cài bởi installer)
- ✅ Tự detect Tesseract (đã cài bởi installer)
- ✅ Offline OCR work ngay (không cần config)
- ✅ Cloud OCR ready (chỉ cần add API key)

---

## 🐛 Troubleshooting

### Q: Build script báo lỗi "Python installer not found"?

**A:** Download Python installer vào đúng folder:
```batch
cd desktop-app
mkdir installers
REM Download python-3.11.8-amd64.exe vào installers/
```

---

### Q: Build script báo lỗi "Tesseract installer not found"?

**A:** Download Tesseract installer:
```
https://github.com/UB-Mannheim/tesseract/wiki
→ tesseract-ocr-w64-setup-5.3.3.exe
→ Copy vào desktop-app/installers/
```

---

### Q: NSIS build failed?

**A:** Check:
1. NSIS installed đúng chưa?
2. `dist/win-unpacked/` folder có chưa? (từ electron-build)
3. `LICENSE.txt` có chưa?

Run từng bước manually:
```batch
yarn build
yarn electron-build
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
```

---

### Q: Installer size quá lớn (>200MB)?

**A:** Normal! Bao gồm:
- Python: ~30MB
- Tesseract: ~50MB
- App: ~70-120MB
- **Total: ~150-200MB**

Nếu muốn nhỏ hơn → Online installer (download Python/Tesseract khi cài)

---

## ⚡ Quick Reference

**One command build:**
```batch
cd desktop-app
build-allinone.bat
```

**Prerequisites:**
- [x] NSIS installed
- [x] `installers/python-3.11.8-amd64.exe`
- [x] `installers/tesseract-ocr-w64-setup-5.3.3.exe`

**Output:**
```
90dayChonThanh-AllInOne-Setup.exe
```

**User experience:**
```
Double-click → Install → Done!
No manual Python/Tesseract setup needed!
```

---

## 📊 Installer Features

**Automatic:**
- ✅ Detect Python (skip if installed)
- ✅ Detect Tesseract (skip if installed)
- ✅ Install Python packages (pytesseract, Pillow, etc.)
- ✅ Add to PATH
- ✅ Create shortcuts (Desktop + Start Menu)
- ✅ Registry entries (for uninstall)

**Silent Install:**
- Python: `/quiet` mode
- Tesseract: `/S` mode
- Minimal user interaction

**Smart:**
- Skip already installed components
- Resume if partially installed
- Uninstaller included

---

## 🎁 Bonus

**Installer cũng cài thêm:**
- ✅ Python packages từ `requirements.txt`
- ✅ Vietnamese language data cho Tesseract
- ✅ PATH environment variables
- ✅ Uninstaller

**User không cần config gì thêm!**

---

**Last Updated:** December 2024  
**Version:** 1.0 - All-in-One Build
