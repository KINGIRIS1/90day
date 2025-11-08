@echo off
chcp 65001 >nul
color 0C
title Force Clean & Restart - Kill All Cache

echo.
echo ========================================
echo   FORCE CLEAN ^& RESTART
echo ========================================
echo.
echo This will:
echo  1. Kill ALL Electron/Node processes
echo  2. Delete ALL cache (project + system)
echo  3. Rebuild from scratch
echo  4. Start fresh app
echo.
pause

echo.
echo [1/6] Killing ALL Electron processes...
taskkill /F /IM electron.exe /T 2>nul
if %errorlevel% equ 0 (
    echo ✅ Killed Electron
) else (
    echo ℹ️  No Electron running
)

timeout /t 2 /nobreak >nul

echo.
echo [2/6] Killing ALL Node processes...
taskkill /F /IM node.exe /T 2>nul
if %errorlevel% equ 0 (
    echo ✅ Killed Node
) else (
    echo ℹ️  No Node running
)

timeout /t 2 /nobreak >nul

echo.
echo [3/6] Deleting project cache...
if exist "node_modules\.cache" (
    rmdir /S /Q "node_modules\.cache"
    echo ✅ Deleted node_modules\.cache
)
if exist "build" (
    rmdir /S /Q "build"
    echo ✅ Deleted build folder
)
if exist ".cache" (
    rmdir /S /Q ".cache"
    echo ✅ Deleted .cache
)

echo.
echo [4/6] Deleting Electron system cache...
echo Cleaning AppData...
if exist "%APPDATA%\Electron" (
    rmdir /S /Q "%APPDATA%\Electron" 2>nul
    echo ✅ Cleaned AppData\Electron
)
if exist "%LOCALAPPDATA%\Electron" (
    rmdir /S /Q "%LOCALAPPDATA%\Electron" 2>nul
    echo ✅ Cleaned LocalAppData\Electron
)
if exist "%TEMP%\electron*" (
    del /F /Q "%TEMP%\electron*" 2>nul
    echo ✅ Cleaned Temp\electron
)

echo.
echo [5/6] Rebuilding node_modules...
echo This will take 2-3 minutes...
echo.
rmdir /S /Q node_modules 2>nul
call yarn install
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: yarn install failed!
    echo Check your internet connection.
    pause
    exit /b 1
)

echo.
echo [6/6] Starting app with CLEAN state...
echo.
echo ========================================
echo   App should start in 10-20 seconds
echo ========================================
echo.

call yarn electron-dev-win

pause
