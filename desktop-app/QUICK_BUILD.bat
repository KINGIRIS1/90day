@echo off
echo ========================================
echo   90dayChonThanh - Quick Build Script
echo ========================================
echo.

echo [1/3] Installing dependencies...
call yarn install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Building React app...
call yarn build
if %errorlevel% neq 0 (
    echo ERROR: Failed to build React app
    pause
    exit /b 1
)

echo.
echo [3/3] Creating Windows installer...
call electron-builder --win nsis
if %errorlevel% neq 0 (
    echo ERROR: Failed to create installer
    pause
    exit /b 1
)

echo.
echo ========================================
echo   BUILD COMPLETE!
echo ========================================
echo.
echo Installer location: dist\90dayChonThanh-Setup-1.1.0.exe
echo.
echo You can now distribute this file to users.
echo.
pause
