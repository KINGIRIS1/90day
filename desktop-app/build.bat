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

REM Check Python (optional warning only)
echo.
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
echo ========================================
echo Select build type:
echo ========================================
echo.
echo 1. Windows installer (.exe) - RECOMMENDED
echo 2. Portable version (no install)
echo 3. Both installer and portable
echo.
set /p choice="Enter choice [1-3]: "

if "%choice%"=="1" goto BUILD_INSTALLER
if "%choice%"=="2" goto BUILD_PORTABLE
if "%choice%"=="3" goto BUILD_BOTH

echo.
echo [ERROR] Invalid choice: %choice%
echo Please enter 1, 2, or 3
pause
exit /b 1

:BUILD_INSTALLER
echo.
echo ========================================
echo Building Windows installer...
echo ========================================
call yarn electron-build --win
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)
goto DONE

:BUILD_PORTABLE
echo.
echo ========================================
echo Building portable version...
echo ========================================
call yarn electron-pack
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)
echo.
echo Creating ZIP archive...
cd dist
if exist win-unpacked (
    powershell -Command "Compress-Archive -Path win-unpacked -DestinationPath 90dayChonThanh-Portable-Win.zip -Force"
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Created: 90dayChonThanh-Portable-Win.zip
    ) else (
        echo [ERROR] Failed to create ZIP
    )
)
cd ..
goto DONE

:BUILD_BOTH
echo.
echo ========================================
echo Building installer...
echo ========================================
call yarn electron-build --win
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Installer build failed
    pause
    exit /b 1
)
echo.
echo ========================================
echo Building portable version...
echo ========================================
call yarn electron-pack
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Portable build failed
    pause
    exit /b 1
)
cd dist
if exist win-unpacked (
    echo Creating ZIP archive...
    powershell -Command "Compress-Archive -Path win-unpacked -DestinationPath 90dayChonThanh-Portable-Win.zip -Force"
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Created: 90dayChonThanh-Portable-Win.zip
    )
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
echo.
dir dist\*.exe 2>nul
dir dist\*.zip 2>nul
echo.
echo ========================================
echo Next steps:
echo ========================================
echo 1. Test installer on clean Windows machine
echo 2. Verify Tesseract OCR works
echo 3. Distribute to users
echo.
echo Press any key to exit...
pause >nul

