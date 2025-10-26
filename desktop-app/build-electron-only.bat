@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Build Electron App Only
echo   (For testing before NSIS)
echo ========================================
echo.

REM Check Node.js
echo [1/4] Checking Node.js...
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js not found
    pause
    exit /b 1
)
echo [OK] Node.js found

REM Check Yarn
echo [2/4] Checking Yarn...
where yarn >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Yarn not found
    echo Installing Yarn...
    npm install -g yarn
)
echo [OK] Yarn found

REM Install dependencies if needed
if not exist "node_modules" (
    echo [3/4] Installing dependencies...
    call yarn install
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed
        pause
        exit /b 1
    )
) else (
    echo [3/4] Dependencies already installed
)

REM Build React app
echo [4/4] Building React app...
call yarn build
if errorlevel 1 (
    echo [ERROR] React build failed
    pause
    exit /b 1
)
echo [OK] React built

REM Build Electron app (unpacked for installer)
echo [5/5] Building Electron app (unpacked)...
call yarn electron-pack
if errorlevel 1 (
    echo [ERROR] Electron pack failed
    pause
    exit /b 1
)
echo [OK] Electron packed

REM Verify output
echo.
echo ========================================
echo   Verifying Output
echo ========================================
echo.

if exist "dist\win-unpacked" (
    echo [OK] dist\win-unpacked\ exists
    
    REM Check for .exe file
    dir /b "dist\win-unpacked\*.exe" >nul 2>nul
    if errorlevel 1 (
        echo [WARNING] No .exe file found in dist\win-unpacked\
    ) else (
        echo [OK] Found .exe files:
        dir /b "dist\win-unpacked\*.exe"
    )
    
    echo.
    echo Folder structure:
    tree /F "dist\win-unpacked" | more
) else (
    echo [ERROR] dist\win-unpacked\ not created
    echo.
    echo Possible issues:
    echo - electron-builder not configured correctly
    echo - package.json missing electron-builder config
    echo - Build failed silently
    pause
    exit /b 1
)

echo.
echo ========================================
echo   BUILD COMPLETE!
echo ========================================
echo.
echo Next step: Run build-allinone.bat
echo.
pause
