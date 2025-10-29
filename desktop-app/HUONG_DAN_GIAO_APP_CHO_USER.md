# 📦 HƯỚNG DẪN GIAO APP CHO USER - ĐƠN GIẢN NHẤT

## 🎯 Tóm tắt: User cần gì?

### **3 BƯỚC DUY NHẤT:**

```
1. Cài Python 3.8+ (Tick "Add to PATH")
2. Cài Tesseract OCR (Tick "Vietnamese")  
3. Chạy file 90dayChonThanh-Setup.exe
```

**Thời gian:** ~10-15 phút  
**Yêu cầu:** Windows 10+, ~500MB ổ cứng

---

## 📁 Files Cần Giao Cho User

### **PACKAGE CƠ BẢN** (Khuyến nghị)

```
📦 90dayChonThanh-v1.1.0/
│
├── 📄 90dayChonThanh-Setup-1.1.0.exe     (Installer - ~150MB)
├── 📄 HUONG_DAN_CAI_DAT.txt              (Hướng dẫn ngắn gọn)
└── 📄 LINKS.txt                          (Link download Python & Tesseract)
```

### **PACKAGE ĐẦY ĐỦ** (Nếu user không có internet)

```
📦 90dayChonThanh-Complete-v1.1.0/
│
├── 📄 90dayChonThanh-Setup-1.1.0.exe     (Installer - ~150MB)
├── 📄 90dayChonThanh-Portable.zip        (Portable version - ~220MB)
├── 📄 HUONG_DAN_CAI_DAT.txt              
├── 📄 REQUIREMENTS.txt                    
│
├── 📁 Prerequisites/                      (Software cần cài)
│   ├── python-3.11.7-amd64.exe           (~25MB - offline installer)
│   └── tesseract-ocr-w64-setup-5.3.3.exe (~40MB - offline installer)
│
└── 📁 Docs/
    ├── HUONG_DAN_DAY_DU.pdf
    └── VIDEO_HUONG_DAN.mp4               (Optional)
```

---

## 📝 Nội Dung File HUONG_DAN_CAI_DAT.txt

```txt
╔══════════════════════════════════════════════════════════════╗
║      HƯỚNG DẪN CÀI ĐẶT - 90dayChonThanh Desktop v1.1.0     ║
╚══════════════════════════════════════════════════════════════╝

⏱️  THỜI GIAN: 10-15 phút
💻 YÊU CẦU: Windows 10 trở lên, 500MB ổ cứng

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 BƯỚC 1: CÀI PYTHON (BẮT BUỘC)

1. Mở file: python-3.11.7-amd64.exe
   (Hoặc download từ: https://www.python.org/downloads/)

2. Khi cửa sổ cài đặt hiện ra:
   ✅ QUAN TRỌNG: Tick vào ô "Add Python to PATH"
   └─ Ô này ở dưới cùng, phải tick!

3. Click "Install Now"

4. Đợi cài xong → Close

5. KỂM TRA: Mở Command Prompt (gõ "cmd" trong Start Menu)
   Gõ: python --version
   Phải hiện: Python 3.11.7 (hoặc tương tự)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 BƯỚC 2: CÀI THƯ VIỆN PYTHON

1. Mở Command Prompt (gõ "cmd" trong Start Menu)

2. Copy lệnh này và paste vào CMD:
   
   pip install pytesseract Pillow

3. Enter → Đợi cài xong (30 giây - 1 phút)

4. Thấy "Successfully installed..." là OK

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 BƯỚC 3: CÀI TESSERACT OCR (BẮT BUỘC)

1. Mở file: tesseract-ocr-w64-setup-5.3.3.exe
   (Hoặc download từ: https://github.com/UB-Mannheim/tesseract/wiki)

2. Khi cài đặt:
   ✅ Chọn "Additional language data (download)"
   ✅ Tick "Vietnamese" trong danh sách ngôn ngữ
   ✅ Tick "Add to PATH"

3. Next → Next → Install

4. Close

5. KIỂM TRA: Mở Command Prompt mới (CMD)
   Gõ: tesseract --version
   Phải hiện: tesseract 5.3.3 (hoặc tương tự)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 BƯỚC 4: CÀI APP

1. Double click file: 90dayChonThanh-Setup-1.1.0.exe

2. Nếu Windows cảnh báo:
   → Click "More info"
   → Click "Run anyway"

3. Follow wizard:
   Next → Next → Install → Finish

4. Xong! App đã cài vào:
   - Desktop: Icon "90dayChonThanh"
   - Start Menu: 90dayChonThanh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 BƯỚC 5: CHẠY VÀ TEST APP

1. Double click icon "90dayChonThanh" trên Desktop

2. Lần đầu mở có thể mất vài giây

3. Khi app mở:
   - Tab "File Scan" → Click "Chọn Files"
   - Chọn 1 ảnh tài liệu bất kỳ
   - Click "Quét Offline"
   - Xem kết quả

4. Nếu thấy kết quả → CÀI ĐẶT THÀNH CÔNG! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ TROUBLESHOOTING (Nếu Gặp Lỗi)

┌─────────────────────────────────────────────────────────────┐
│ LỖI: "Python is not recognized"                             │
├─────────────────────────────────────────────────────────────┤
│ NGUYÊN NHÂN: Chưa cài Python hoặc chưa tick "Add to PATH"   │
│ GIẢI PHÁP:                                                   │
│  1. Uninstall Python cũ                                     │
│  2. Cài lại Python                                          │
│  3. ✅ Nhớ tick "Add Python to PATH"                        │
│  4. Restart máy                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ LỖI: "Tesseract is not recognized"                          │
├─────────────────────────────────────────────────────────────┤
│ NGUYÊN NHÂN: Chưa cài Tesseract hoặc chưa tick "Add PATH"   │
│ GIẢI PHÁP:                                                   │
│  1. Cài lại Tesseract                                       │
│  2. ✅ Tick "Add to PATH" khi cài                           │
│  3. Restart máy                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ LỖI: "No module named 'pytesseract'"                        │
├─────────────────────────────────────────────────────────────┤
│ NGUYÊN NHÂN: Chưa cài thư viện Python                        │
│ GIẢI PHÁP:                                                   │
│  Mở CMD, gõ: pip install pytesseract Pillow                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ LỖI: App không mở                                           │
├─────────────────────────────────────────────────────────────┤
│ GIẢI PHÁP:                                                   │
│  1. Restart máy                                              │
│  2. Right click app icon → "Run as administrator"           │
│  3. Check antivirus có block không                          │
└─────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 HỖ TRỢ

Nếu vẫn gặp vấn đề:
  📧 Email: support@90daychonthanh.com
  📱 Hotline: [Số điện thoại]
  
Đính kèm:
  - Screenshot lỗi
  - Log file (nếu có) tại: C:\Users\<tên bạn>\AppData\Roaming\90dayChonThanh\logs\

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CHECKLIST HOÀN THÀNH

Sau khi cài đặt, check các mục sau:

□ Python installed? (cmd: python --version)
□ Tesseract installed? (cmd: tesseract --version)
□ App icon trên Desktop?
□ App mở được?
□ Quét được 1 file test?

Nếu tất cả ✅ → CÀI ĐẶT THÀNH CÔNG!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Version: 1.1.0
Updated: 2025-01-27
```

---

## 📝 Nội Dung File LINKS.txt

```txt
═══════════════════════════════════════════════════════════════
  DOWNLOAD LINKS - 90dayChonThanh Prerequisites
═══════════════════════════════════════════════════════════════

📥 PYTHON (Required)

Official Website:
  https://www.python.org/downloads/

Direct Download (Windows 64-bit):
  https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe

⚠️  QUAN TRỌNG: Khi cài, tick "Add Python to PATH"

───────────────────────────────────────────────────────────────

📥 TESSERACT OCR (Required)

Official GitHub:
  https://github.com/UB-Mannheim/tesseract/wiki

Direct Download (Windows 64-bit):
  https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe

⚠️  QUAN TRỌNG: 
    - Tick "Vietnamese language pack"
    - Tick "Add to PATH"

───────────────────────────────────────────────────────────────

📥 PYTHON LIBRARIES (Required)

Sau khi cài Python, mở Command Prompt (CMD) và chạy:

  pip install pytesseract Pillow

───────────────────────────────────────────────────────────────

✅ VERIFICATION

Sau khi cài xong tất cả, verify bằng CMD:

  python --version
  tesseract --version
  pip list | findstr pytesseract

Nếu cả 3 đều OK → Sẵn sàng cài app!

═══════════════════════════════════════════════════════════════
```

---

## 📝 Nội Dung File REQUIREMENTS.txt

```txt
═══════════════════════════════════════════════════════════════
  SYSTEM REQUIREMENTS - 90dayChonThanh Desktop v1.1.0
═══════════════════════════════════════════════════════════════

🖥️  OPERATING SYSTEM

Supported:
  ✅ Windows 10 (64-bit)
  ✅ Windows 11 (64-bit)

Not Supported:
  ❌ Windows 7/8/8.1
  ❌ Windows 32-bit
  ❌ macOS
  ❌ Linux

───────────────────────────────────────────────────────────────

💾 DISK SPACE

Required:
  • App installation: ~200 MB
  • Python + Libraries: ~100 MB
  • Tesseract OCR: ~200 MB
  • Working space: ~100 MB
  
  Total: ~600 MB (Minimum)
  Recommended: 1 GB free space

───────────────────────────────────────────────────────────────

🧠 MEMORY (RAM)

Minimum: 4 GB
Recommended: 8 GB or more

Note: 
  - Offline OCR: 1-2 GB RAM usage
  - Cloud Boost: Minimal RAM usage

───────────────────────────────────────────────────────────────

🐍 PYTHON

Required: Python 3.8 or higher
Recommended: Python 3.11+

Download: https://www.python.org/downloads/

⚠️  CRITICAL: Must add Python to PATH during installation

───────────────────────────────────────────────────────────────

📦 PYTHON LIBRARIES

Required packages:
  • pytesseract
  • Pillow

Installation:
  pip install pytesseract Pillow

───────────────────────────────────────────────────────────────

🔤 TESSERACT OCR

Required: Tesseract 5.0 or higher
Recommended: Tesseract 5.3.3+

Download: https://github.com/UB-Mannheim/tesseract/wiki

⚠️  CRITICAL: 
    - Must install Vietnamese language pack
    - Must add to PATH during installation

───────────────────────────────────────────────────────────────

🌐 INTERNET CONNECTION

Required for:
  • Cloud Boost feature (optional)
  • First-time pip install (if not using offline package)

Not required for:
  • Offline OCR (works completely offline)
  • Basic app functionality

───────────────────────────────────────────────────────────────

🔧 OPTIONAL (Advanced Features)

For EasyOCR engine (if enabled):
  pip install easyocr

For VietOCR engine (if enabled):
  pip install vietocr

Note: These are OPTIONAL. Default Tesseract engine works fine.

───────────────────────────────────────────────────────────────

✅ QUICK CHECK

Before installing app, verify:

□ Windows 10/11 (64-bit)
□ 1 GB free disk space
□ 4 GB+ RAM
□ Python 3.8+ installed (with PATH)
□ pip install pytesseract Pillow (completed)
□ Tesseract OCR installed (with Vietnamese + PATH)

If all checked → Ready to install!

═══════════════════════════════════════════════════════════════
```

---

## 🎬 Script Để Tạo Package Tự Động

### `create-user-package.bat`

```batch
@echo off
echo ========================================
echo  TAO PACKAGE GIAO CHO USER
echo ========================================
echo.

REM Variables
set APP_VERSION=1.1.0
set PACKAGE_NAME=90dayChonThanh-v%APP_VERSION%
set PACKAGE_DIR=%PACKAGE_NAME%

REM Create package directory
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"

echo [1/5] Copying installer...
copy "installers\90dayChonThanh-Setup-%APP_VERSION%.exe" "%PACKAGE_DIR%\" >nul
if errorlevel 1 (
    echo ERROR: Installer not found!
    pause
    exit /b 1
)

echo [2/5] Copying portable version...
if exist "90dayChonThanh-Portable-Win.zip" (
    copy "90dayChonThanh-Portable-Win.zip" "%PACKAGE_DIR%\" >nul
) else (
    echo Warning: Portable version not found, skipping...
)

echo [3/5] Creating documentation...
REM HUONG_DAN_CAI_DAT.txt
echo Creating HUONG_DAN_CAI_DAT.txt...
(
echo HUONG DAN CAI DAT - 90dayChonThanh Desktop v%APP_VERSION%
echo.
echo BUOC 1: Cai Python 3.8+ ^(Tick "Add to PATH"^)
echo BUOC 2: Cai Tesseract OCR ^(Tick "Vietnamese"^)
echo BUOC 3: pip install pytesseract Pillow
echo BUOC 4: Chay 90dayChonThanh-Setup-%APP_VERSION%.exe
echo.
echo Chi tiet day du xem file HUONG_DAN_DAY_DU.md
) > "%PACKAGE_DIR%\HUONG_DAN_CAI_DAT.txt"

REM LINKS.txt
echo Creating LINKS.txt...
(
echo DOWNLOAD LINKS
echo.
echo Python: https://www.python.org/downloads/
echo Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
) > "%PACKAGE_DIR%\LINKS.txt"

REM REQUIREMENTS.txt
echo Creating REQUIREMENTS.txt...
(
echo SYSTEM REQUIREMENTS
echo.
echo - Windows 10/11 ^(64-bit^)
echo - Python 3.8+
echo - Tesseract OCR 5.0+
echo - 1 GB disk space
echo - 4 GB RAM
) > "%PACKAGE_DIR%\REQUIREMENTS.txt"

echo [4/5] Copying full documentation...
copy "HUONG_DAN_CAI_DAT_USER.md" "%PACKAGE_DIR%\HUONG_DAN_DAY_DU.md" >nul

echo [5/5] Creating ZIP archive...
powershell -command "Compress-Archive -Path '%PACKAGE_DIR%' -DestinationPath '%PACKAGE_NAME%.zip' -Force"

echo.
echo ========================================
echo  HOAN THANH!
echo ========================================
echo.
echo Package created: %PACKAGE_NAME%.zip
echo.
echo Noi dung:
dir /b "%PACKAGE_DIR%"
echo.
echo Ban co the gui file ZIP nay cho user!
echo.
pause
```

---

## ✅ CHECKLIST CHO DEVELOPER (Người Build)

### Trước Khi Giao App:

- [ ] Build app thành công (installer .exe + portable .zip)
- [ ] Test installer trên máy Windows clean
- [ ] Test portable version trên máy Windows clean
- [ ] Verify Python + Tesseract requirements
- [ ] Tạo package với script `create-user-package.bat`
- [ ] Kiểm tra tất cả files trong package
- [ ] Test hướng dẫn với 1 user thật
- [ ] Chuẩn bị support email/phone

### Files Phải Có Trong Package:

- [ ] `90dayChonThanh-Setup-X.X.X.exe`
- [ ] `HUONG_DAN_CAI_DAT.txt` (ngắn gọn)
- [ ] `LINKS.txt` (download links)
- [ ] `REQUIREMENTS.txt` (system requirements)
- [ ] `HUONG_DAN_DAY_DU.md` (chi tiết)

### Optional (Nếu User Không Có Internet):

- [ ] `python-3.11.7-amd64.exe` (~25MB)
- [ ] `tesseract-ocr-w64-setup-5.3.3.exe` (~40MB)
- [ ] `90dayChonThanh-Portable-Win.zip` (~220MB)

---

## 📊 User Experience Flow

```
User nhận ZIP
    ↓
Giải nén
    ↓
Đọc HUONG_DAN_CAI_DAT.txt
    ↓
Cài Python (5 phút)
    ↓
Cài Tesseract (3 phút)
    ↓
pip install libraries (2 phút)
    ↓
Chạy installer (2 phút)
    ↓
Mở app → Test → Success! 🎉
    ↓
Total: ~12-15 phút
```

---

## 🎯 Summary

**3 FILES QUAN TRỌNG NHẤT GỬI CHO USER:**

1. **90dayChonThanh-Setup-X.X.X.exe** - Installer
2. **HUONG_DAN_CAI_DAT.txt** - Hướng dẫn ngắn gọn
3. **LINKS.txt** - Download links cho Python & Tesseract

**User chỉ cần:**
1. Cài Python (tick PATH)
2. Cài Tesseract (tick Vietnamese)
3. Chạy installer
4. Done!

**Tổng thời gian:** 10-15 phút  
**Độ khó:** ⭐⭐☆☆☆ (Dễ, có hướng dẫn chi tiết)
