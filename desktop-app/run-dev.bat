@echo off
echo ========================================
echo  90dayChonThanh Desktop App
echo  Development Mode
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo [Step 1/2] Installing dependencies...
    call yarn install
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo Please make sure Node.js and Yarn are installed.
        pause
        exit /b 1
    )
) else (
    echo [Step 1/2] Dependencies already installed, skipping...
)

echo.
echo [Step 2/2] Starting app in development mode...
echo.
echo ========================================
echo  Development server starting...
echo  - React Dev Server: http://localhost:3001
echo  - Electron will open automatically
echo  - Hot reload enabled
echo  Close this window to stop
echo ========================================
echo.

call yarn electron-dev-win

echo.
echo Development server stopped.
pause
