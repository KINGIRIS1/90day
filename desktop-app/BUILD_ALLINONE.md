# 📦 Hướng Dẫn Build All-in-One Installer

## 🎯 Mục tiêu

Tạo **1 file .exe duy nhất** cài đặt tất cả:
- ✅ Python 3.11
- ✅ Tesseract OCR (Vietnamese)
- ✅ Python packages (pytesseract, Pillow)
- ✅ 90dayChonThanh Desktop App

**User chỉ cần:** Double click 1 file .exe → Đợi → Done!

---

## 🔧 Yêu cầu (Cho Developer)

### 1. NSIS Installer (Nullsoft Scriptable Install System)

**Download:**
- URL: https://nsis.sourceforge.io/Download
- File: `nsis-3.09-setup.exe`

**Install:**
1. Download NSIS
2. Run installer
3. Install với default settings
4. Verify: `C:\Program Files (x86)\NSIS\makensis.exe`

---

### 2. Download Dependencies

**A. Python Installer:**
```
URL: https://www.python.org/downloads/windows/
File: python-3.11.8-amd64.exe (~30MB)
Save to: desktop-app/installers/python-3.11.8-amd64.exe
```

**B. Tesseract Installer:**
```
URL: https://github.com/UB-Mannheim/tesseract/wiki
File: tesseract-ocr-w64-setup-5.3.3.exe (~50MB)
Save to: desktop-app/installers/tesseract-ocr-w64-setup-5.3.3.exe
```

---

## 📁 Cấu trúc Folder

```
desktop-app/
├── installers/                          ← TẠO FOLDER NÀY
│   ├── python-3.11.8-amd64.exe         ← Download vào đây
│   └── tesseract-ocr-w64-setup-5.3.3.exe
├── installer.nsi                        ← Script đã tạo
├── dist/
│   └── win-unpacked/                    ← Từ electron-builder
├── assets/
│   └── icon.ico
└── LICENSE.txt
```

---

## 🚀 Build Steps

### Bước 1: Build Electron App

```batch
cd desktop-app
build.bat

# Chọn option 1 (chỉ cần unpacked)
# Output: dist/win-unpacked/
```

### Bước 2: Tạo Installers Folder

```batch
mkdir installers
cd installers
```

### Bước 3: Download Dependencies

**Python:**
1. Vào: https://www.python.org/downloads/windows/
2. Download: `python-3.11.8-amd64.exe`
3. Copy vào: `desktop-app/installers/`

**Tesseract:**
1. Vào: https://github.com/UB-Mannheim/tesseract/wiki
2. Download: `tesseract-ocr-w64-setup-5.3.3.exe`
3. Copy vào: `desktop-app/installers/`

### Bước 4: Tạo LICENSE.txt

```batch
cd desktop-app
echo MIT License > LICENSE.txt
```

### Bước 5: Build NSIS Installer

**Right-click method:**
1. Right-click `installer.nsi`
2. "Compile NSIS Script"
3. Đợi build (vài phút)

**Command-line method:**
```batch
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
```

### Bước 6: Kiểm tra Output

```
desktop-app/
└── 90dayChonThanh-AllInOne-Setup.exe  ← File này! (~250MB)
```

---

## 🧪 Test Installer

### Test trên VM hoặc máy clean:

1. Copy file: `90dayChonThanh-AllInOne-Setup.exe`
2. Double-click
3. Follow wizard:
   - Welcome → Next
   - License → I Agree
   - Directory → Next
   - Installing... (5-10 phút)
   - Finish
4. Desktop icon → Open app
5. Test quét offline

**Expected behavior:**
- Python tự động cài (silent)
- Tesseract tự động cài (silent, Vietnamese)
- Pip packages tự động install
- App shortcuts created
- Everything works!

---

## 📊 File Sizes

| Component | Size |
|-----------|------|
| Python installer | ~30MB |
| Tesseract installer | ~50MB |
| App (unpacked) | ~150MB |
| NSIS overhead | ~5MB |
| **Total** | **~235MB** |

**Trade-off:**
- ❌ Larger file size
- ✅ Much better user experience!

---

## 🎨 Customization

### Change App Icon

```nsis
; In installer.nsi, line 12:
!define MUI_ICON "assets\your-icon.ico"
```

### Change Welcome Message

```nsis
; Line 16-17:
!define MUI_WELCOMEPAGE_TEXT "Your custom message here"
```

### Add Custom Pages

```nsis
; After line 23:
!insertmacro MUI_PAGE_COMPONENTS
```

---

## 🔍 Troubleshooting

### Build error: "Can't open file"

**Fix:**
```
Check paths:
- installers/python-3.11.8-amd64.exe exists?
- installers/tesseract-ocr-w64-setup-5.3.3.exe exists?
- dist/win-unpacked/ exists?
```

### Installer runs but Python not installed

**Fix:**
```nsis
; In installer.nsi, check silent install flags:
ExecWait '"$TEMP\python-3.11.8-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1'
```

### App runs but can't find Python/Tesseract

**Fix:**
```
PATH might not be updated
User needs to:
1. Restart computer
2. Or logout/login
```

---

## 💡 Advanced Options

### Option 1: Portable Bundle

Create portable version with Python embedded:

```
1. Download Python embeddable: python-3.11.8-embed-amd64.zip
2. Extract to: app/python/
3. Include in electron-builder files
4. Update getPythonPath() to use bundled Python
```

**Pros:** Truly portable, no install needed
**Cons:** Larger app (~80MB more)

### Option 2: Separate Installers

Keep 3 separate files:
```
1. python-installer.exe
2. tesseract-installer.exe  
3. app-installer.exe
+ install-all.bat (runs all 3)
```

**Pros:** Smaller individual files
**Cons:** User clicks multiple files

### Option 3: MSI Installer

Use WiX Toolset instead of NSIS:
```
Pros: More professional, can be deployed via GPO
Cons: More complex to build
```

---

## 📝 Build Script

**Tạo file: `build-allinone.bat`**

```batch
@echo off
echo Building All-in-One Installer...

REM Check requirements
if not exist "installers\python-3.11.8-amd64.exe" (
    echo [ERROR] Python installer not found
    echo Download from: python.org
    pause
    exit /b 1
)

if not exist "installers\tesseract-ocr-w64-setup-5.3.3.exe" (
    echo [ERROR] Tesseract installer not found
    echo Download from: github.com/UB-Mannheim/tesseract/wiki
    pause
    exit /b 1
)

REM Build Electron app first
echo Building Electron app...
call yarn build
call yarn electron-pack

REM Build NSIS installer
echo Building NSIS installer...
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi

echo.
echo Done! Output: 90dayChonThanh-AllInOne-Setup.exe
pause
```

---

## ✅ Checklist

**Before building:**
- [ ] NSIS installed
- [ ] Python installer downloaded
- [ ] Tesseract installer downloaded
- [ ] Electron app built (dist/win-unpacked/)
- [ ] LICENSE.txt exists (or will be auto-created)
- [ ] Icon file optional (commented out in installer.nsi)

**Note:** Icon is optional. If you want custom icon, create `assets/icon.ico` and uncomment line 21 in `installer.nsi`

**After building:**
- [ ] Test on clean VM
- [ ] Verify Python installs
- [ ] Verify Tesseract installs
- [ ] Verify app runs
- [ ] Test OCR offline mode

---

## 🎯 Benefits

**For Users:**
```
Before: 
1. Download app
2. Download Python → Install
3. pip install packages
4. Download Tesseract → Install
5. Run app
= 5 steps, ~15 minutes

After:
1. Download 90dayChonThanh-AllInOne-Setup.exe
2. Run installer
3. Done!
= 2 steps, ~5 minutes (mostly waiting)
```

**For Support:**
- ✅ Fewer support tickets
- ✅ Consistent environment
- ✅ Known versions (Python 3.11, Tesseract 5.3.3)
- ✅ Professional appearance

---

## 📦 Distribution

**Final package:**
```
📁 90dayChonThanh-v1.0.0/
├── 90dayChonThanh-AllInOne-Setup.exe  (~235MB)
└── README.txt                          (Quick guide)
```

**README.txt:**
```
90dayChonThanh Desktop App
All-in-One Installer

Installation:
1. Run: 90dayChonThanh-AllInOne-Setup.exe
2. Wait for installation (5-10 minutes)
3. Desktop icon → Open app
4. Done!

This installer includes:
- Python 3.11
- Tesseract OCR (Vietnamese)
- 90dayChonThanh Desktop App

No additional setup required!
```

**Upload và share:**
- Google Drive / Dropbox
- File share service (WeTransfer, etc.)
- Company network share

---

## 🎉 Result

**Single-file installer that:**
- ✅ Installs everything automatically
- ✅ No manual steps for users
- ✅ Creates desktop shortcuts
- ✅ Adds uninstaller
- ✅ Professional experience

**User experience:**
```
Download → Run → Wait → Use
```

**That's it! 🚀**
