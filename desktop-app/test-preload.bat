@echo off
chcp 65001 >nul
color 0E
title Test Preload.js

echo.
echo ========================================
echo   DIAGNOSTIC - Check Everything
echo ========================================
echo.

echo Current directory:
cd
echo.

echo [1] Checking if files exist...
if exist "electron\preload.js" (
    echo ✅ electron\preload.js exists
) else (
    echo ❌ electron\preload.js NOT FOUND!
    echo You are in the WRONG directory!
    pause
    exit /b 1
)

if exist "electron\main.js" (
    echo ✅ electron\main.js exists
) else (
    echo ❌ electron\main.js NOT FOUND!
    pause
    exit /b 1
)

echo.
echo [2] Checking preload.js content...
findstr /C:"analyzeBatchFile" "electron\preload.js" >nul
if %errorlevel% equ 0 (
    echo ✅ preload.js contains analyzeBatchFile
) else (
    echo ❌ preload.js does NOT contain analyzeBatchFile
    echo This is the OLD file!
    pause
    exit /b 1
)

echo.
echo [3] Checking main.js loads preload.js...
findstr /C:"preload.js" "electron\main.js" >nul
if %errorlevel% equ 0 (
    echo ✅ main.js references preload.js
) else (
    echo ❌ main.js does NOT load preload.js
    pause
    exit /b 1
)

echo.
echo [4] Checking package.json...
if exist "package.json" (
    echo ✅ package.json exists
    findstr /C:"electron-dev-win" "package.json" >nul
    if %errorlevel% equ 0 (
        echo ✅ electron-dev-win script exists
    ) else (
        echo ❌ electron-dev-win script NOT found
    )
) else (
    echo ❌ package.json NOT FOUND!
    pause
    exit /b 1
)

echo.
echo ========================================
echo All files look correct!
echo ========================================
echo.
echo BUT you said API is still undefined!
echo.
echo This means ONE of these:
echo.
echo 1. You are running a PACKAGED .exe file
echo    → Solution: Delete .exe, run yarn electron-dev-win
echo.
echo 2. Port 3001 is showing OLD React code
echo    → Solution: Kill all processes, restart
echo.
echo 3. Browser cache (extremely rare in Electron)
echo    → Solution: Clear browser data
echo.
echo Let's check what you're actually running...
echo.
pause

echo.
echo ========================================
echo   NEXT STEPS
echo ========================================
echo.
echo Please do the following:
echo.
echo 1. CLOSE the app completely
echo.
echo 2. Check if there's a .exe file:
dir /B *.exe 2>nul
if %errorlevel% equ 0 (
    echo.
    echo ⚠️  FOUND .exe FILES! You might be running these!
    echo    DELETE them and run yarn electron-dev-win instead!
    echo.
)

echo.
echo 3. Kill ALL processes:
taskkill /F /IM electron.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul

echo.
echo 4. Check port 3001:
netstat -ano | findstr :3001
if %errorlevel% equ 0 (
    echo ⚠️  Port 3001 is BUSY!
    echo.
    echo Kill the process using port 3001:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001') do (
        echo Killing PID: %%a
        taskkill /F /PID %%a 2>nul
    )
)

echo.
echo 5. Now start FRESH:
echo.
echo    yarn electron-dev-win
echo.
echo 6. After app opens, press F12 and type:
echo.
echo    window.electronAPI
echo.
echo    Should show an object with many functions!
echo.
pause
