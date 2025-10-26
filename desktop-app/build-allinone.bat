@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   All-in-One Installer Builder
echo   90dayChonThanh Desktop App
echo ========================================
echo.

REM Check NSIS
echo [1/5] Checking NSIS...
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    echo [OK] NSIS found
) else (
    echo [ERROR] NSIS not found
    echo Please install from: https://nsis.sourceforge.io/Download
    pause
    exit /b 1
)

REM Check Python installer
echo [2/5] Checking Python installer...
if exist "installers\python-3.11.8-amd64.exe" (
    echo [OK] Python installer found
) else (
    echo [ERROR] Python installer not found
    echo.
    echo Please download:
    echo URL: https://www.python.org/downloads/windows/
    echo File: python-3.11.8-amd64.exe
    echo Save to: installers\python-3.11.8-amd64.exe
    echo.
    pause
    exit /b 1
)

REM Check Tesseract installer
echo [3/5] Checking Tesseract installer...
if exist "installers\tesseract-ocr-w64-setup-5.3.3.exe" (
    echo [OK] Tesseract installer found
) else (
    echo [ERROR] Tesseract installer not found
    echo.
    echo Please download:
    echo URL: https://github.com/UB-Mannheim/tesseract/wiki
    echo File: tesseract-ocr-w64-setup-5.3.3.exe
    echo Save to: installers\tesseract-ocr-w64-setup-5.3.3.exe
    echo.
    pause
    exit /b 1
)

REM Build Electron app
echo [4/5] Building Electron app...
if not exist "dist\win-unpacked" (
    echo Building React + Electron...
    call yarn build >nul 2>nul
    call yarn electron-pack >nul 2>nul
    echo [OK] Electron app built
) else (
    echo [OK] Using existing build
)

REM Create LICENSE if not exists
if not exist "LICENSE.txt" (
    echo MIT License > LICENSE.txt
)

REM Build NSIS installer
echo [5/5] Building NSIS installer...
echo This may take 2-3 minutes...
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi

if errorlevel 1 (
    echo.
    echo [ERROR] NSIS build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   BUILD COMPLETE!
echo ========================================
echo.
echo Output file: 90dayChonThanh-AllInOne-Setup.exe
echo.

REM Show file info
if exist "90dayChonThanh-AllInOne-Setup.exe" (
    for %%A in ("90dayChonThanh-AllInOne-Setup.exe") do (
        set size=%%~zA
        set /a sizeMB=!size!/1048576
        echo File size: !sizeMB! MB
    )
    echo.
    echo This installer includes:
    echo - Python 3.11
    echo - Tesseract OCR Vietnamese
    echo - 90dayChonThanh Desktop App
    echo.
    echo Ready to distribute!
) else (
    echo [ERROR] Output file not found
)

echo.
echo ========================================
echo   NEXT STEPS
echo ========================================
echo.
echo 1. Test installer on clean VM/PC
echo 2. Verify all components install
echo 3. Test app functionality
echo 4. Distribute to users
echo.
pause
