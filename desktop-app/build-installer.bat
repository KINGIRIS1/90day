@echo off
echo ================================================================================
echo BUILD WINDOWS INSTALLER v1.1.0
echo ================================================================================
echo.

echo [STEP 1/6] Checking prerequisites...
echo.

REM Check Node.js - Try multiple methods
set NODE_CMD=

REM Method 1: Check if 'node' command works
node --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set NODE_CMD=node
    goto :node_found
)

REM Method 2: Check common installation paths
if exist "C:\Program Files\nodejs\node.exe" (
    set NODE_CMD="C:\Program Files\nodejs\node.exe"
    set PATH=%PATH%;C:\Program Files\nodejs
    goto :node_found
)

if exist "C:\Program Files (x86)\nodejs\node.exe" (
    set NODE_CMD="C:\Program Files (x86)\nodejs\node.exe"
    set PATH=%PATH%;C:\Program Files (x86)\nodejs
    goto :node_found
)

REM Not found
echo [ERROR] Node.js not found!
echo.
echo Please install Node.js from https://nodejs.org/
echo Make sure to check "Add to PATH" during installation
echo.
echo After installing, CLOSE this window and open a NEW Command Prompt
echo.
pause
exit /b 1

:node_found
%NODE_CMD% --version
echo [OK] Node.js found

REM Check Yarn - Try multiple methods
set YARN_CMD=

REM Method 1: Check if 'yarn' command works
yarn --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set YARN_CMD=yarn
    goto :yarn_found
)

REM Method 2: Try npm path
if exist "C:\Users\%USERNAME%\AppData\Roaming\npm\yarn.cmd" (
    set YARN_CMD="C:\Users\%USERNAME%\AppData\Roaming\npm\yarn.cmd"
    goto :yarn_found
)

REM Not found - install it
echo [WARNING] Yarn not found!
echo Installing Yarn...
%NODE_CMD% -e "console.log('Installing Yarn globally...')"
call npm install -g yarn
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Yarn
    pause
    exit /b 1
)
set YARN_CMD=yarn

:yarn_found
%YARN_CMD% --version
echo [OK] Yarn found

REM Check Python
set PYTHON_CMD=
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
) else (
    py --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=py
    ) else (
        echo [ERROR] Python not found!
        echo Please install Python 3.8+ from https://www.python.org/
        pause
        exit /b 1
    )
)
%PYTHON_CMD% --version
echo [OK] Python found

echo.
echo ================================================================================
echo [STEP 2/6] Installing Node.js dependencies...
echo ================================================================================
echo.

call %YARN_CMD% install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo [STEP 3/6] Installing Python dependencies...
echo ================================================================================
echo.

cd python
%PYTHON_CMD% -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some Python packages may have failed to install
    echo This is OK if building App-only (Python will be bundled separately)
)
cd ..

echo.
echo ================================================================================
echo [STEP 4/6] Building React frontend...
echo ================================================================================
echo.

call %YARN_CMD% build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build React frontend
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo [STEP 5/6] Building Electron App...
echo ================================================================================
echo.

call %YARN_CMD% electron-build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build Electron app
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo [STEP 6/6] Creating NSIS Installer (if available)...
echo ================================================================================
echo.

REM Check if NSIS is installed
where makensis >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] NSIS found, creating installer...
    REM Build NSIS installer if needed
    echo [INFO] Installer will be created by electron-builder
) else (
    echo [WARNING] NSIS not found - Only portable app will be created
    echo To create .exe installer, install NSIS from https://nsis.sourceforge.io/
)

echo.
echo ================================================================================
echo BUILD COMPLETE!
echo ================================================================================
echo.

REM Find the output
if exist "dist\90dayChonThanh Setup*.exe" (
    echo [SUCCESS] Installer created:
    dir /b dist\90dayChonThanh*.exe
    echo.
    echo Location: %CD%\dist\
) else if exist "dist\win-unpacked" (
    echo [SUCCESS] Portable app created in: dist\win-unpacked\
    echo You can run: dist\win-unpacked\90dayChonThanh.exe
) else (
    echo [WARNING] Build output not found in expected location
    echo Please check the dist\ folder
)

echo.
echo ================================================================================
echo NEXT STEPS:
echo ================================================================================
echo 1. Test the installer by running it on a clean Windows machine
echo 2. Verify all features work (OCR, classification, PDF export)
echo 3. Upload to Google Drive or file sharing service
echo 4. Share with users
echo.
echo ================================================================================

pause
