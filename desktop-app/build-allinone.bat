@echo off
REM ===================================================================
REM Build All-in-One Installer - Automatic Python & Tesseract
REM ===================================================================

echo.
echo ====================================================================
echo  BUILD ALL-IN-ONE INSTALLER
echo ====================================================================
echo.
echo Installer nay se tu dong cai:
echo   - Python 3.11
echo   - Tesseract OCR (Vietnamese)
echo   - Desktop App
echo.
echo User chi can double-click 1 file .exe!
echo.
echo ====================================================================
echo.

REM Step 1: Check NSIS
echo [1/5] Checking NSIS...
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    echo   [OK] NSIS found
) else (
    echo   [ERROR] NSIS not found!
    echo   Please download and install from: https://nsis.sourceforge.io/Download
    pause
    exit /b 1
)

REM Step 2: Build Electron App
echo.
echo [2/5] Building Electron app...
call yarn build
if %errorlevel% neq 0 (
    echo   [ERROR] Yarn build failed
    pause
    exit /b 1
)
echo   [OK] React build complete

echo.
echo [2.5/5] Building Electron package...
call yarn electron-build
if %errorlevel% neq 0 (
    echo   [ERROR] Electron build failed
    pause
    exit /b 1
)
echo   [OK] Electron package complete

REM Step 3: Check installers folder
echo.
echo [3/5] Checking dependencies...

if not exist "installers" (
    echo   [INFO] Creating installers folder...
    mkdir installers
)

if not exist "installers\python-3.11.8-amd64.exe" (
    echo.
    echo   [WARNING] Python installer not found!
    echo   Please download from: https://www.python.org/downloads/windows/
    echo   File: python-3.11.8-amd64.exe
    echo   Save to: desktop-app\installers\
    echo.
    pause
    exit /b 1
)
echo   [OK] Python installer found

if not exist "installers\tesseract-ocr-w64-setup-5.3.3.exe" (
    echo.
    echo   [WARNING] Tesseract installer not found!
    echo   Please download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo   File: tesseract-ocr-w64-setup-5.3.3.exe  
    echo   Save to: desktop-app\installers\
    echo.
    pause
    exit /b 1
)
echo   [OK] Tesseract installer found

REM Step 4: Check LICENSE.txt
echo.
echo [4/5] Checking LICENSE.txt...
if not exist "LICENSE.txt" (
    echo   [INFO] Creating default LICENSE.txt...
    echo MIT License > LICENSE.txt
    echo. >> LICENSE.txt
    echo Copyright (c) 2025 90dayChonThanh >> LICENSE.txt
)
echo   [OK] LICENSE.txt exists

REM Step 5: Build with NSIS
echo.
echo [5/5] Building All-in-One installer with NSIS...
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi

if %errorlevel% equ 0 (
    echo.
    echo ====================================================================
    echo  BUILD COMPLETE!
    echo ====================================================================
    echo.
    echo  Output: 90dayChonThanh-AllInOne-Setup.exe
    echo.
    echo  Installer includes:
    echo    - Python 3.11 (auto-install)
    echo    - Tesseract OCR (auto-install)
    echo    - Desktop App
    echo.
    echo  User can now double-click this ONE file to install everything!
    echo.
    echo ====================================================================
    pause
) else (
    echo.
    echo [ERROR] NSIS build failed!
    echo Check the output above for errors.
    pause
    exit /b 1
)
