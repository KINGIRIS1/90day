@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
color 0B
title Check Files - Fixed Version

echo.
echo ========================================
echo   Check Files - Batch Scan (FIXED)
echo ========================================
echo.

echo Current directory: %CD%
echo.

set "error_count=0"

echo Checking critical files...
echo.

:: Check preload.js
if exist "electron\preload.js" (
    findstr /C:"analyzeBatchFile" "electron\preload.js" >nul
    if !errorlevel! equ 0 (
        echo ✅ electron\preload.js - analyzeBatchFile found
    ) else (
        echo ❌ electron\preload.js - analyzeBatchFile NOT found
        set /a error_count+=1
    )
) else (
    echo ❌ electron\preload.js - FILE NOT FOUND
    set /a error_count+=1
)

:: Check main.js
if exist "electron\main.js" (
    findstr /C:"analyze-batch-file" "electron\main.js" >nul
    if !errorlevel! equ 0 (
        echo ✅ electron\main.js - IPC handler found
    ) else (
        echo ❌ electron\main.js - IPC handler NOT found
        set /a error_count+=1
    )
) else (
    echo ❌ electron\main.js - FILE NOT FOUND
    set /a error_count+=1
)

:: Check batch_scanner.py
if exist "python\batch_scanner.py" (
    echo ✅ python\batch_scanner.py - exists
) else (
    echo ❌ python\batch_scanner.py - NOT FOUND
    set /a error_count+=1
)

:: Check BatchScanner.js
if exist "src\components\BatchScanner.js" (
    echo ✅ src\components\BatchScanner.js - exists
) else (
    echo ❌ src\components\BatchScanner.js - NOT FOUND
    set /a error_count+=1
)

:: Check App.js
if exist "src\App.js" (
    findstr /C:"BatchScanner" "src\App.js" >nul
    if !errorlevel! equ 0 (
        echo ✅ src\App.js - BatchScanner imported
    ) else (
        echo ❌ src\App.js - BatchScanner NOT imported
        set /a error_count+=1
    )
) else (
    echo ❌ src\App.js - FILE NOT FOUND
    set /a error_count+=1
)

echo.
echo ========================================

if !error_count! equ 0 (
    echo ✅ All files are correct!
    echo.
    echo You can now run: yarn electron-dev-win
) else (
    echo ❌ Found !error_count! error(s)
    echo.
    echo POSSIBLE REASONS:
    echo 1. You copied an OLD version of the folder
    echo 2. You are in the WRONG directory
    echo 3. Files were not copied completely
    echo.
    echo WHERE TO GET LATEST FILES:
    echo Server path: /app/desktop-app/
    echo.
    echo Make sure you copy from THIS exact path!
)

echo ========================================
echo.

pause
