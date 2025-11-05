@echo off
chcp 65001 > nul
title Test Installer - 90dayChonThanh

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         Test Installer - 90dayChonThanh v1.1.0            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Check if installer exists
if not exist "dist\90dayChonThanh-Setup-1.1.0.exe" (
    echo [ERROR] Installer not found!
    echo.
    echo Expected location: dist\90dayChonThanh-Setup-1.1.0.exe
    echo.
    echo Please build the installer first:
    echo   build-installer.bat
    echo.
    pause
    exit /b 1
)

:: Get installer info
echo [1/3] Checking installer file...
echo.

for %%A in ("dist\90dayChonThanh-Setup-1.1.0.exe") do (
    set SIZE=%%~zA
    set /a SIZE_MB=!SIZE! / 1048576
)

echo   ✓ File exists: dist\90dayChonThanh-Setup-1.1.0.exe
echo   ✓ File size: %SIZE_MB% MB
echo.

:: Check if app is already installed
echo [2/3] Checking installation status...
echo.

set INSTALL_PATH=%LOCALAPPDATA%\Programs\90dayChonThanh\90dayChonThanh.exe

if exist "%INSTALL_PATH%" (
    echo   ⚠ App is already installed at:
    echo     %INSTALL_PATH%
    echo.
    echo   You can:
    echo     1. Uninstall it first via Windows Settings
    echo     2. Or run the installer (it will upgrade)
    echo.
) else (
    echo   ✓ App is not installed (fresh install)
    echo.
)

:: Offer to run installer
echo [3/3] Ready to test installer
echo.
echo Do you want to run the installer now?
echo   1. Yes - Run installer
echo   2. No  - Just open dist folder
echo   3. Exit
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting installer...
    echo.
    start "" "dist\90dayChonThanh-Setup-1.1.0.exe"
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║  Installer is running!                                     ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo After installation completes:
    echo   1. Launch the app from Desktop or Start Menu
    echo   2. Test all features (scan, classify, export)
    echo   3. Check Settings are saved
    echo   4. Try with real Vietnamese land documents
    echo.
    echo Installation location:
    echo   %LOCALAPPDATA%\Programs\90dayChonThanh\
    echo.
) else if "%choice%"=="2" (
    echo.
    echo Opening dist folder...
    explorer "dist"
) else (
    echo.
    echo Exiting...
)

pause
