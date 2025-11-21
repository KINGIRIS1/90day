@echo off
echo ========================================
echo  90dayChonThanh Desktop App
echo  Starting Application...
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo [Step 1/3] Installing dependencies...
    call yarn install
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo Please make sure Node.js and Yarn are installed.
        pause
        exit /b 1
    )
) else (
    echo [Step 1/3] Dependencies already installed, skipping...
)

echo.
echo [Step 2/3] Building React app...
call yarn build
if errorlevel 1 (
    echo.
    echo ERROR: Failed to build React app!
    pause
    exit /b 1
)

echo.
echo [Step 3/3] Starting Electron app...
echo.
echo ========================================
echo  Application is starting...
echo  Close this window to stop the app
echo ========================================
echo.

call yarn electron

echo.
echo Application closed.
pause
