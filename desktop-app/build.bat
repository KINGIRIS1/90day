@echo off
REM Build script for 90dayChonThanh Desktop App (Windows)
REM Tự động build installer

echo ========================================
echo   90dayChonThanh Desktop App Builder
echo ========================================
echo.

REM Check Node.js
echo Checking requirements...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found. Please install Node.js 16+
    pause
    exit /b 1
)
echo [OK] Node.js: 
node --version

REM Check Yarn
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Yarn not found. Installing...
    npm install -g yarn
)
echo [OK] Yarn:
yarn --version

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Python not found. Users will need to install Python.
) else (
    echo [OK] Python:
    python --version
)

echo.
echo Installing dependencies...
call yarn install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building React app...
call yarn build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build React app
    pause
    exit /b 1
)

echo.
echo Select build type:
echo 1. Windows installer (.exe) - RECOMMENDED
echo 2. Portable version (no install)
echo 3. Both
echo.
set /p choice="Enter choice [1-3]: "

if "%choice%"=="1" goto BUILD_INSTALLER
if "%choice%"=="2" goto BUILD_PORTABLE
if "%choice%"=="3" goto BUILD_BOTH
echo Invalid choice
pause
exit /b 1

:BUILD_INSTALLER
echo.
echo Building Windows installer...
call yarn electron-build --win
goto DONE

:BUILD_PORTABLE
echo.
echo Building portable version...
call yarn electron-pack
echo.
echo Creating ZIP archive...
cd dist
if exist win-unpacked (
    powershell Compress-Archive -Path win-unpacked -DestinationPath 90dayChonThanh-Portable-Win.zip -Force
    echo [OK] Created: 90dayChonThanh-Portable-Win.zip
)
cd ..
goto DONE

:BUILD_BOTH
echo.
echo Building installer...
call yarn electron-build --win
echo.
echo Building portable...
call yarn electron-pack
cd dist
if exist win-unpacked (
    powershell Compress-Archive -Path win-unpacked -DestinationPath 90dayChonThanh-Portable-Win.zip -Force
    echo [OK] Created: 90dayChonThanh-Portable-Win.zip
)
cd ..
goto DONE

:DONE
echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo Output files in: .\dist\
dir dist\*.exe dist\*.zip 2>nul
echo.
echo Next steps:
echo 1. Test installer on clean Windows machine
echo 2. Verify Tesseract OCR works
echo 3. Distribute to users
echo.
pause
