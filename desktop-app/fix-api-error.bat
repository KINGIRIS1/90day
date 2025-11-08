@echo off
chcp 65001 >nul
color 0A
title Fix API Error - Windows Desktop

echo.
echo ========================================
echo   Fix API Error - Windows Desktop
echo ========================================
echo.

echo [1/5] Killing Electron and Node processes...
taskkill /F /IM electron.exe 2>nul
if %errorlevel% equ 0 (
    echo ✅ Killed Electron processes
) else (
    echo ℹ️  No Electron processes running
)

taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo ✅ Killed Node processes
) else (
    echo ℹ️  No Node processes running
)

timeout /t 2 /nobreak >nul
echo.

echo [2/5] Cleaning project cache...
if exist node_modules\.cache (
    rmdir /S /Q node_modules\.cache
    echo ✅ Cleaned node_modules cache
) else (
    echo ℹ️  No node_modules cache found
)

if exist build (
    rmdir /S /Q build
    echo ✅ Cleaned build folder
) else (
    echo ℹ️  No build folder found
)
echo.

echo [3/5] Cleaning Electron cache...
del /Q /F "%APPDATA%\Electron\*" 2>nul
del /Q /F "%LOCALAPPDATA%\Electron\*" 2>nul
echo ✅ Cleaned Electron cache
echo.

echo [4/5] Checking critical files...
if not exist "electron\preload.js" (
    echo ❌ ERROR: electron\preload.js not found!
    echo Please copy the complete desktop-app folder
    pause
    exit /b 1
)

if not exist "electron\main.js" (
    echo ❌ ERROR: electron\main.js not found!
    echo Please copy the complete desktop-app folder
    pause
    exit /b 1
)

if not exist "python\batch_scanner.py" (
    echo ❌ ERROR: python\batch_scanner.py not found!
    echo Please copy the complete desktop-app folder
    pause
    exit /b 1
)

if not exist "src\components\BatchScanner.js" (
    echo ❌ ERROR: src\components\BatchScanner.js not found!
    echo Please copy the complete desktop-app folder
    pause
    exit /b 1
)

echo ✅ All critical files present
echo.

echo [5/5] Reinstalling dependencies...
echo This may take 2-3 minutes...
call yarn install
if %errorlevel% neq 0 (
    echo ❌ ERROR: yarn install failed!
    echo Please check your internet connection
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

echo ========================================
echo   Fix completed successfully!
echo ========================================
echo.
echo Starting app...
echo Press Ctrl+C to stop
echo.

call yarn electron-dev-win

pause
