@echo off
echo ============================================
echo FIX: Add PYTHONPATH to production build
echo ============================================
echo.

echo [1/5] Syncing electron.js...
copy /y electron\main.js public\electron.js
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to sync electron.js
    pause
    exit /b 1
)
echo Done.
echo.

echo [2/5] Cleaning old builds...
if exist dist rd /s /q dist
if exist build rd /s /q build
echo Done.
echo.

echo [3/5] Building React...
call yarn build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: React build failed!
    pause
    exit /b 1
)
echo Done.
echo.

echo [4/5] Building Windows installer...
call npx electron-builder --win --x64
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo Done.
echo.

echo [5/5] Verifying...
if not exist "dist\90dayChonThanh Setup 1.1.0.exe" (
    echo ERROR: Installer not found!
    pause
    exit /b 1
)

for %%I in ("dist\90dayChonThanh Setup 1.1.0.exe") do set SIZE=%%~zI
set /a SIZE_MB=%SIZE% / 1024 / 1024

echo.
echo ============================================
echo BUILD COMPLETE WITH PYTHONPATH FIX!
echo ============================================
echo.
echo Installer: dist\90dayChonThanh Setup 1.1.0.exe
echo Size: %SIZE_MB% MB
echo.
echo CHANGES:
echo - Added PYTHONPATH to Python spawn environment
echo - Set working directory to Python script location
echo - Python will now find system site-packages!
echo.
echo NEXT STEPS:
echo 1. Uninstall old app: Settings -^> Apps -^> Uninstall
echo 2. Install new app: dist\90dayChonThanh Setup 1.1.0.exe
echo 3. Test OCR with Gemini Flash
echo.
pause
