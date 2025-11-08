@echo off
chcp 65001 >nul
color 0D
title Auto Patch - Batch Scan APIs

echo.
echo ========================================
echo   Auto Patch - Batch Scan APIs
echo ========================================
echo.
echo This script will automatically:
echo  1. Replace electron\preload.js
echo  2. Patch electron\main.js
echo  3. Patch src\App.js
echo.
echo Make sure FILE_1_preload.js.txt exists!
echo.
pause

if not exist "FILE_1_preload.js.txt" (
    echo.
    echo ❌ ERROR: FILE_1_preload.js.txt not found!
    echo.
    echo Please make sure you have this file in the same directory.
    echo This file should be provided by the developer.
    echo.
    pause
    exit /b 1
)

echo.
echo [Step 1] Backing up original files...
copy electron\preload.js electron\preload.js.backup >nul 2>&1
copy electron\main.js electron\main.js.backup >nul 2>&1
copy src\App.js src\App.js.backup >nul 2>&1
echo ✅ Backup completed

echo.
echo [Step 2] Replacing preload.js...
copy /Y FILE_1_preload.js.txt electron\preload.js >nul
if %errorlevel% equ 0 (
    echo ✅ preload.js replaced
) else (
    echo ❌ Failed to replace preload.js
    pause
    exit /b 1
)

echo.
echo [Step 3] Checking results...
findstr "analyzeBatchFile" electron\preload.js >nul
if %errorlevel% equ 0 (
    echo ✅ preload.js - analyzeBatchFile found
) else (
    echo ❌ preload.js - analyzeBatchFile NOT found
    echo Something went wrong!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Patch completed!
echo ========================================
echo.
echo IMPORTANT: You still need to manually patch:
echo  - electron\main.js (add IPC handlers)
echo  - src\App.js (add import and components)
echo.
echo See PASTE_FILES_GUIDE.md for instructions.
echo.
echo After manual patching, run:
echo    check-files.bat
echo.
pause
