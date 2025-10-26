@echo off
setlocal enabledelayedexpansion

REM Build script for 90dayChonThanh Desktop App (Windows)
echo.
echo ========================================
echo   90dayChonThanh Desktop App Builder
echo ========================================
echo.

REM Check Node.js
echo [1/4] Checking Node.js...
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 16+
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
echo [OK] Node.js: %NODE_VER%

REM Check Yarn
echo [2/4] Checking Yarn...
where yarn >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Yarn not found. Installing...
    call npm install -g yarn
)
for /f "tokens=*" %%i in ('yarn --version') do set YARN_VER=%%i
echo [OK] Yarn: %YARN_VER%

REM Check Python (optional)
echo [3/4] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
    echo [WARNING] Python not found. App will need Python installed.
) else (
    for /f "tokens=*" %%i in ('python --version') do set PY_VER=%%i
    echo [OK] Python: !PY_VER!
)

REM Install dependencies
echo [4/4] Installing dependencies...
echo This may take a few minutes...
call yarn install >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo.
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Build React
echo.
echo Building React app...
call yarn build >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Failed to build React app
    echo.
    pause
    exit /b 1
)
echo [OK] React app built

REM Show menu
echo.
echo ========================================
echo   SELECT BUILD TYPE
echo ========================================
echo.
echo   1. Windows installer (.exe) - RECOMMENDED
echo.
echo   2. Portable version (ZIP, no install)
echo.
echo   3. Both installer and portable
echo.
echo ========================================
echo.
set /p "choice=Enter your choice (1, 2, or 3): "

REM Validate choice
if "%choice%"=="" goto INVALID_CHOICE
if "%choice%"=="1" goto BUILD_INSTALLER
if "%choice%"=="2" goto BUILD_PORTABLE
if "%choice%"=="3" goto BUILD_BOTH
goto INVALID_CHOICE

:INVALID_CHOICE
echo.
echo [ERROR] Invalid choice: "%choice%"
echo Please run the script again and enter 1, 2, or 3
echo.
pause
exit /b 1

:BUILD_INSTALLER
echo.
echo ========================================
echo   Building Windows Installer...
echo ========================================
echo.
call yarn electron-build --win
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)
goto SUCCESS

:BUILD_PORTABLE
echo.
echo ========================================
echo   Building Portable Version...
echo ========================================
echo.
call yarn electron-pack
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)
echo.
echo Creating ZIP archive...
cd dist
if exist win-unpacked (
    powershell -Command "Compress-Archive -Path win-unpacked -DestinationPath 90dayChonThanh-Portable-Win.zip -Force"
    if errorlevel 0 (
        echo [OK] Created: 90dayChonThanh-Portable-Win.zip
    )
)
cd ..
goto SUCCESS

:BUILD_BOTH
echo.
echo ========================================
echo   Building Installer and Portable...
echo ========================================
echo.
echo [1/2] Building installer...
call yarn electron-build --win
if errorlevel 1 (
    echo [ERROR] Installer build failed
    pause
    exit /b 1
)
echo [OK] Installer complete
echo.
echo [2/2] Building portable...
call yarn electron-pack
if errorlevel 1 (
    echo [ERROR] Portable build failed
    pause
    exit /b 1
)
cd dist
if exist win-unpacked (
    echo Creating ZIP...
    powershell -Command "Compress-Archive -Path win-unpacked -DestinationPath 90dayChonThanh-Portable-Win.zip -Force"
    if errorlevel 0 (
        echo [OK] Portable version complete
    )
)
cd ..
goto SUCCESS

:SUCCESS
echo.
echo ========================================
echo   BUILD COMPLETE!
echo ========================================
echo.
echo Output files in: .\dist\
echo.
if exist dist\*.exe (
    echo Installer files:
    dir /b dist\*.exe
)
if exist dist\*.zip (
    echo Portable files:
    dir /b dist\*.zip
)
echo.
echo ========================================
echo   NEXT STEPS
echo ========================================
echo.
echo 1. Test the installer on a clean machine
echo 2. Verify Tesseract OCR integration works
echo 3. Distribute to users
echo.
echo ========================================
echo.
pause
exit /b 0


