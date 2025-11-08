@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
color 0E

echo.
echo ========================================
echo   Verify Source - Where did you copy from?
echo ========================================
echo.

echo This script will help identify the source of your files.
echo.

echo [Checking file dates...]
echo.

if exist "electron\preload.js" (
    echo electron\preload.js:
    dir "electron\preload.js" | findstr "preload.js"
    echo.
)

if exist "electron\main.js" (
    echo electron\main.js:
    dir "electron\main.js" | findstr "main.js"
    echo.
)

if exist "src\App.js" (
    echo src\App.js:
    dir "src\App.js" | findstr "App.js"
    echo.
)

if exist "python\batch_scanner.py" (
    echo python\batch_scanner.py:
    dir "python\batch_scanner.py" | findstr "batch_scanner.py"
    echo.
) else (
    echo ❌ python\batch_scanner.py - NOT FOUND
    echo This file is NEW and should exist!
    echo If missing, you copied an OLD version!
    echo.
)

if exist "src\components\BatchScanner.js" (
    echo src\components\BatchScanner.js:
    dir "src\components\BatchScanner.js" | findstr "BatchScanner.js"
    echo.
) else (
    echo ❌ src\components\BatchScanner.js - NOT FOUND
    echo This file is NEW and should exist!
    echo If missing, you copied an OLD version!
    echo.
)

echo ========================================
echo.
echo LATEST CODE ON SERVER:
echo   Date: Today (after our conversation)
echo   Path: /app/desktop-app/
echo.
echo IF YOUR FILES ARE OLDER:
echo   → You copied before the updates!
echo   → Copy again from /app/desktop-app/
echo.
echo IF FILES ARE MISSING (batch_scanner.py, BatchScanner.js):
echo   → Definitely copied OLD version!
echo   → MUST copy again!
echo.
pause
