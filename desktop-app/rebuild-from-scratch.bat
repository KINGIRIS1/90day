@echo off
echo ============================================
echo REBUILD FROM SCRATCH - 90dayChonThanh
echo ============================================
echo.

REM Step 1: Kill processes
echo [1/8] Stopping all processes...
taskkill /f /im 90dayChonThanh.exe 2>nul
taskkill /f /im electron.exe 2>nul
timeout /t 2 /nobreak >nul
echo Done.
echo.

REM Step 2: Clean everything
echo [2/8] Cleaning all build artifacts...
if exist dist (
    echo Removing dist...
    attrib -r -s -h dist\*.* /s /d 2>nul
    rd /s /q dist 2>nul
)
if exist build (
    echo Removing build...
    rd /s /q build 2>nul
)
if exist node_modules (
    echo Removing node_modules...
    rd /s /q node_modules 2>nul
)
echo Done.
echo.

REM Step 3: Backup and replace package.json
echo [3/8] Updating package.json...
if exist package.json (
    copy /y package.json package.json.backup >nul
    echo Backed up to package.json.backup
)
if exist package.json.FINAL (
    copy /y package.json.FINAL package.json >nul
    echo Updated package.json from package.json.FINAL
) else (
    echo WARNING: package.json.FINAL not found!
    echo Using existing package.json
)
echo Done.
echo.

REM Step 4: Clean cache
echo [4/8] Cleaning yarn cache...
call yarn cache clean
echo Done.
echo.

REM Step 5: Install dependencies
echo [5/8] Installing dependencies...
echo This may take 3-5 minutes...
call yarn install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 6: Build React
echo [6/8] Building React app...
call yarn build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: React build failed!
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 7: Verify Python folder
echo [7/8] Verifying Python folder...
if not exist python (
    echo ERROR: python folder not found!
    echo Make sure python folder exists in project root
    pause
    exit /b 1
)
dir python\*.py | find /c ".py" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No Python files found in python folder!
    pause
    exit /b 1
)
echo Python folder verified.
echo Done.
echo.

REM Step 8: Build Windows installer
echo [8/8] Building Windows installer...
echo This may take 3-5 minutes...
echo.
call npx electron-builder --win --x64
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Electron builder failed!
    pause
    exit /b 1
)
echo Done.
echo.

REM Verification
echo ============================================
echo VERIFICATION
echo ============================================
echo.

if not exist "dist\90dayChonThanh Setup 1.1.0.exe" (
    echo ERROR: Installer not found!
    pause
    exit /b 1
)

for %%I in ("dist\90dayChonThanh Setup 1.1.0.exe") do set SIZE=%%~zI
set /a SIZE_MB=%SIZE% / 1024 / 1024

echo Installer: dist\90dayChonThanh Setup 1.1.0.exe
echo Size: %SIZE_MB% MB
echo.

REM Check Python in build
if exist "dist\win-unpacked\resources\app\python" (
    echo [OK] Python folder found in build
    dir "dist\win-unpacked\resources\app\python\*.py" | find /c ".py"
) else (
    echo [WARNING] Python folder NOT found in build!
    echo This will cause OCR to fail!
)
echo.

REM Check node_modules
if exist "dist\win-unpacked\resources\app\node_modules" (
    echo [OK] node_modules found in build
) else (
    echo [WARNING] node_modules NOT found in build!
)
echo.

echo ============================================
echo BUILD COMPLETE!
echo ============================================
echo.
echo Next steps:
echo 1. Test portable: dist\win-unpacked\90dayChonThanh.exe
echo 2. Install: dist\90dayChonThanh Setup 1.1.0.exe
echo 3. Test OCR with Gemini Flash API key
echo.
pause
