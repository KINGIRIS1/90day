@echo off
chcp 65001 > nul
title Quick Build - 90dayChonThanh Installer

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║       Quick Build - 90dayChonThanh Installer v1.1.0       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo This is a simplified build script for quick rebuilds.
echo Use build-installer.bat for full builds with prerequisites check.
echo.
echo Starting quick build process...
echo.

:: Clean Python vendor
echo [1/4] Cleaning Python vendor...
powershell -ExecutionPolicy Bypass -File .\python\scripts\clean-local-python.ps1 2>nul

:: Build React
echo [2/4] Building React app...
call yarn build
if %errorlevel% neq 0 (
    echo [ERROR] React build failed!
    pause
    exit /b 1
)

:: Build installer
echo [3/4] Building Windows installer...
call yarn dist:win
if %errorlevel% neq 0 (
    echo [ERROR] Installer build failed!
    pause
    exit /b 1
)

:: Verify
echo [4/4] Verifying output...
if exist "dist\90dayChonThanh-Setup-1.1.0.exe" (
    echo.
    echo ✓ Build successful!
    echo.
    echo Installer: dist\90dayChonThanh-Setup-1.1.0.exe
    echo.
    explorer "dist"
) else (
    echo.
    echo [ERROR] Installer not found!
)

pause
