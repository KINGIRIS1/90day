@echo off
echo ============================================
echo FINAL BUILD - All Fixes Applied
echo ============================================
echo.

REM Step 1: Kill processes
echo [1/7] Stopping processes...
taskkill /f /im 90dayChonThanh.exe 2>nul
taskkill /f /im electron.exe 2>nul
timeout /t 2 /nobreak >nul
echo Done.
echo.

REM Step 2: Clean
echo [2/7] Cleaning...
if exist dist rd /s /q dist
if exist build rd /s /q build
echo Done.
echo.

REM Step 3: Verify Python file is correct
echo [3/7] Verifying Python files...
findstr /c:"gemini-1.5-flash" python\ocr_engine_gemini_flash.py >nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Python file uses correct model: gemini-1.5-flash
) else (
    echo WARNING: Python file may use wrong model!
    echo Check python\ocr_engine_gemini_flash.py
)
echo Done.
echo.

REM Step 4: Copy electron.js
echo [4/7] Updating electron.js...
copy /y electron\main.js public\electron.js >nul
echo Done.
echo.

REM Step 5: Build React
echo [5/7] Building React...
call yarn build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: React build failed!
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 6: Build Windows
echo [6/7] Building Windows installer...
call npx electron-builder --win --x64
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Electron build failed!
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 7: Verify
echo [7/7] Verifying build...
if not exist "dist\90dayChonThanh Setup 1.1.0.exe" (
    echo ERROR: Installer not found!
    pause
    exit /b 1
)

for %%I in ("dist\90dayChonThanh Setup 1.1.0.exe") do set SIZE=%%~zI
set /a SIZE_MB=%SIZE% / 1024 / 1024

echo.
echo ============================================
echo BUILD COMPLETE!
echo ============================================
echo.
echo Installer: dist\90dayChonThanh Setup 1.1.0.exe
echo Size: %SIZE_MB% MB
echo.

REM Check Python in build
if exist "dist\win-unpacked\resources\app\python\ocr_engine_gemini_flash.py" (
    echo [OK] Python files found in build
    findstr /c:"gemini-1.5-flash" "dist\win-unpacked\resources\app\python\ocr_engine_gemini_flash.py" >nul
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Using correct Gemini model: gemini-1.5-flash
    ) else (
        echo [WARNING] May use wrong Gemini model!
    )
) else (
    echo [ERROR] Python files NOT found in build!
)

echo.
echo ============================================
echo INSTALLATION INSTRUCTIONS:
echo ============================================
echo.
echo 1. Uninstall old version:
echo    Settings ^> Apps ^> 90dayChonThanh ^> Uninstall
echo.
echo 2. Install new version:
echo    dist\90dayChonThanh Setup 1.1.0.exe
echo.
echo 3. Install Python dependencies:
echo    py -m pip install requests google-generativeai Pillow
echo.
echo 4. Test app with Gemini Flash + your API key
echo.
pause
