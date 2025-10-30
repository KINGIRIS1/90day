@echo off
echo ==========================================
echo Build Windows Installer
echo ==========================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Yarn is installed
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing Yarn...
    npm install -g yarn
)

echo Step 1: Installing dependencies...
call yarn install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Step 2: Building React app...
call yarn build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to build React app!
    pause
    exit /b 1
)

echo.
echo Step 3: Building Windows installer (NSIS)...
call npx electron-builder --win --x64
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to build Windows installer!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Build completed successfully!
echo ==========================================
echo.
echo Your installer is located at:
echo dist\90dayChonThanh Setup 1.1.0.exe
echo.
pause
