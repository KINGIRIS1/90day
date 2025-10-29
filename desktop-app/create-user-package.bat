@echo off
chcp 65001 >nul
echo ╔══════════════════════════════════════════════════════════════╗
echo ║     TẠO PACKAGE GIAO CHO USER - 90dayChonThanh v1.1.0      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM ============================================================
REM CONFIGURATION
REM ============================================================
set APP_VERSION=1.1.0
set PACKAGE_NAME=90dayChonThanh-v%APP_VERSION%-UserPackage
set PACKAGE_DIR=%PACKAGE_NAME%

REM ============================================================
REM STEP 1: CREATE DIRECTORY STRUCTURE
REM ============================================================
echo [1/7] Tạo thư mục package...
if exist "%PACKAGE_DIR%" (
    echo    Xóa package cũ...
    rmdir /s /q "%PACKAGE_DIR%"
)
mkdir "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%\Prerequisites"
mkdir "%PACKAGE_DIR%\Docs"

REM ============================================================
REM STEP 2: COPY INSTALLER
REM ============================================================
echo [2/7] Copy installer...
if exist "installers\90dayChonThanh-Setup-%APP_VERSION%.exe" (
    copy "installers\90dayChonThanh-Setup-%APP_VERSION%.exe" "%PACKAGE_DIR%\" >nul
    echo    ✓ Installer copied
) else (
    echo    ⚠ WARNING: Installer not found in installers\
    echo    Tìm kiếm trong thư mục hiện tại...
    if exist "90dayChonThanh-Setup-%APP_VERSION%.exe" (
        copy "90dayChonThanh-Setup-%APP_VERSION%.exe" "%PACKAGE_DIR%\" >nul
        echo    ✓ Installer found and copied
    ) else (
        echo    ✗ ERROR: Installer not found!
        echo.
        echo    Vui lòng build installer trước:
        echo    npm run build
        pause
        exit /b 1
    )
)

REM ============================================================
REM STEP 3: COPY PORTABLE VERSION (OPTIONAL)
REM ============================================================
echo [3/7] Copy portable version...
if exist "90dayChonThanh-Portable-Win.zip" (
    copy "90dayChonThanh-Portable-Win.zip" "%PACKAGE_DIR%\" >nul
    echo    ✓ Portable version copied
) else (
    echo    ⚠ Portable version not found, skipping...
)

REM ============================================================
REM STEP 4: CREATE QUICK START GUIDE (TXT)
REM ============================================================
echo [4/7] Tạo hướng dẫn nhanh...
(
echo ╔══════════════════════════════════════════════════════════════╗
echo ║      HƯỚNG DẪN CÀI ĐẶT - 90dayChonThanh Desktop v%APP_VERSION%     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ⏱️  THỜI GIAN: 10-15 phút
echo 💻 YÊU CẦU: Windows 10+, 500MB ổ cứng
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📥 BƯỚC 1: CÀI PYTHON (BẮT BUỘC^)
echo.
echo 1. Download Python từ: https://www.python.org/downloads/
echo    Hoặc dùng file trong thư mục Prerequisites\
echo.
echo 2. Khi cài đặt:
echo    ✅ QUAN TRỌNG: Tick "Add Python to PATH"
echo    └─ Ô này ở dưới cùng, PHẢI TICK!
echo.
echo 3. Click "Install Now" → Đợi cài xong
echo.
echo 4. KIỂM TRA: Mở Command Prompt (gõ "cmd" trong Start Menu^)
echo    Gõ: python --version
echo    Phải hiện: Python 3.x.x
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📥 BƯỚC 2: CÀI THƯ VIỆN PYTHON
echo.
echo 1. Mở Command Prompt (gõ "cmd" trong Start Menu^)
echo.
echo 2. Copy và paste lệnh này:
echo    pip install pytesseract Pillow
echo.
echo 3. Enter → Đợi cài xong (30 giây - 1 phút^)
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📥 BƯỚC 3: CÀI TESSERACT OCR (BẮT BUỘC^)
echo.
echo 1. Download từ: https://github.com/UB-Mannheim/tesseract/wiki
echo    Hoặc dùng file trong Prerequisites\
echo.
echo 2. Khi cài đặt:
echo    ✅ Chọn "Additional language data (download^)"
echo    ✅ Tick "Vietnamese"
echo    ✅ Tick "Add to PATH"
echo.
echo 3. Next → Install → Close
echo.
echo 4. KIỂM TRA: Mở Command Prompt MỚI
echo    Gõ: tesseract --version
echo    Phải hiện: tesseract 5.x.x
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📥 BƯỚC 4: CÀI APP
echo.
echo 1. Double click: 90dayChonThanh-Setup-%APP_VERSION%.exe
echo.
echo 2. Nếu Windows cảnh báo:
echo    → Click "More info"
echo    → Click "Run anyway"
echo.
echo 3. Next → Install → Finish
echo.
echo 4. Xong! App đã cài trên Desktop
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🚀 BƯỚC 5: CHẠY APP
echo.
echo 1. Double click icon "90dayChonThanh" trên Desktop
echo.
echo 2. Tab "File Scan" → Chọn 1 ảnh → Quét Offline → Xem kết quả
echo.
echo 3. Thành công! 🎉
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ❌ NẾU GẶP LỖI:
echo.
echo "Python is not recognized"
echo   → Cài lại Python, nhớ tick "Add to PATH"
echo   → Restart máy
echo.
echo "Tesseract is not recognized"
echo   → Cài lại Tesseract, nhớ tick "Add to PATH"
echo   → Restart máy
echo.
echo "No module named 'pytesseract'"
echo   → Mở CMD: pip install pytesseract Pillow
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ CHECKLIST HOÀN THÀNH:
echo.
echo □ Python installed? (cmd: python --version^)
echo □ Tesseract installed? (cmd: tesseract --version^)
echo □ App icon trên Desktop?
echo □ App mở được?
echo □ Quét được file test?
echo.
echo Nếu tất cả ✅ → CÀI ĐẶT THÀNH CÔNG!
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Version: %APP_VERSION%
echo Docs: Xem thêm trong thư mục Docs\
) > "%PACKAGE_DIR%\BAT_DAU_O_DAY.txt"
echo    ✓ Quick start guide created

REM ============================================================
REM STEP 5: CREATE DOWNLOAD LINKS FILE
REM ============================================================
echo [5/7] Tạo file download links...
(
echo ═══════════════════════════════════════════════════════════════
echo   DOWNLOAD LINKS - Prerequisites
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📥 PYTHON (Required^)
echo.
echo Official Website:
echo   https://www.python.org/downloads/
echo.
echo Direct Download (Windows 64-bit^):
echo   https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe
echo.
echo ⚠️  Khi cài: Tick "Add Python to PATH"
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo 📥 TESSERACT OCR (Required^)
echo.
echo Official GitHub:
echo   https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo Direct Download (Windows 64-bit^):
echo   https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
echo.
echo ⚠️  Khi cài: 
echo     - Tick "Vietnamese language pack"
echo     - Tick "Add to PATH"
echo.
echo ───────────────────────────────────────────────────────────────
echo.
echo 📥 PYTHON LIBRARIES (Required^)
echo.
echo Sau khi cài Python, mở Command Prompt (CMD^) và chạy:
echo.
echo   pip install pytesseract Pillow
echo.
echo ═══════════════════════════════════════════════════════════════
) > "%PACKAGE_DIR%\DOWNLOAD_LINKS.txt"
echo    ✓ Download links created

REM ============================================================
REM STEP 6: CREATE REQUIREMENTS FILE
REM ============================================================
echo [6/7] Tạo file requirements...
(
echo ═══════════════════════════════════════════════════════════════
echo   SYSTEM REQUIREMENTS
echo ═══════════════════════════════════════════════════════════════
echo.
echo 🖥️  OPERATING SYSTEM:
echo   ✅ Windows 10 (64-bit^)
echo   ✅ Windows 11 (64-bit^)
echo.
echo 💾 DISK SPACE:
echo   Minimum: 600 MB
echo   Recommended: 1 GB
echo.
echo 🧠 MEMORY (RAM^):
echo   Minimum: 4 GB
echo   Recommended: 8 GB
echo.
echo 🐍 PYTHON:
echo   Required: Python 3.8+
echo   Recommended: Python 3.11+
echo   Download: https://www.python.org/downloads/
echo.
echo 📦 PYTHON LIBRARIES:
echo   • pytesseract
echo   • Pillow
echo   Install: pip install pytesseract Pillow
echo.
echo 🔤 TESSERACT OCR:
echo   Required: Tesseract 5.0+
echo   Recommended: Tesseract 5.3.3+
echo   Download: https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo 🌐 INTERNET:
echo   Required for: Cloud Boost (optional^)
echo   Not required for: Offline OCR
echo.
echo ═══════════════════════════════════════════════════════════════
) > "%PACKAGE_DIR%\REQUIREMENTS.txt"
echo    ✓ Requirements created

REM ============================================================
REM STEP 7: COPY FULL DOCUMENTATION
REM ============================================================
echo [7/7] Copy tài liệu đầy đủ...
if exist "HUONG_DAN_CAI_DAT_USER.md" (
    copy "HUONG_DAN_CAI_DAT_USER.md" "%PACKAGE_DIR%\Docs\HUONG_DAN_DAY_DU.md" >nul
    echo    ✓ Full guide copied
)
if exist "HUONG_DAN_GIAO_APP_CHO_USER.md" (
    copy "HUONG_DAN_GIAO_APP_CHO_USER.md" "%PACKAGE_DIR%\Docs\DEVELOPER_GUIDE.md" >nul
    echo    ✓ Developer guide copied
)
if exist "README.md" (
    copy "README.md" "%PACKAGE_DIR%\Docs\README.md" >nul
    echo    ✓ README copied
)

REM ============================================================
REM STEP 8: CREATE ZIP ARCHIVE
REM ============================================================
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Đang tạo file ZIP...
powershell -command "Compress-Archive -Path '%PACKAGE_DIR%' -DestinationPath '%PACKAGE_NAME%.zip' -Force"

if errorlevel 1 (
    echo ✗ Lỗi tạo ZIP file!
    pause
    exit /b 1
)

REM ============================================================
REM SUMMARY
REM ============================================================
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    HOÀN THÀNH!                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 📦 Package created: %PACKAGE_NAME%.zip
echo 📁 Folder: %PACKAGE_DIR%\
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📋 NỘI DUNG PACKAGE:
echo.
dir /b "%PACKAGE_DIR%"
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ CHUẨN BỊ GIAO CHO USER:
echo.
echo 1. Gửi file ZIP: %PACKAGE_NAME%.zip
echo 2. User giải nén
echo 3. User đọc: BAT_DAU_O_DAY.txt
echo 4. User follow hướng dẫn
echo 5. Done!
echo.
echo 💡 TIP: Có thể copy offline installers vào Prerequisites\ để user
echo          không cần download (nếu user không có internet^)
echo.
pause
