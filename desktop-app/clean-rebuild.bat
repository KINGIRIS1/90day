@echo off
echo ========================================
echo  Clean Rebuild
echo ========================================
echo.
echo This will:
echo   1. Delete node_modules
echo   2. Delete build folder
echo   3. Reinstall dependencies
echo   4. Rebuild the app
echo.
set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo [Step 1/4] Cleaning node_modules...
if exist "node_modules" (
    rmdir /s /q node_modules
    echo Deleted node_modules
) else (
    echo node_modules not found, skipping...
)

echo.
echo [Step 2/4] Cleaning build folder...
if exist "build" (
    rmdir /s /q build
    echo Deleted build folder
) else (
    echo build folder not found, skipping...
)

echo.
echo [Step 3/4] Installing dependencies...
call yarn install
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo [Step 4/4] Building app...
call yarn build
if errorlevel 1 (
    echo.
    echo ERROR: Failed to build app!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Clean Rebuild Complete!
echo ========================================
echo.
echo You can now run the app with 'run-app.bat'
echo.

pause
