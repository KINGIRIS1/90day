@echo off
echo ========================================
echo  Building Windows Installer
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo ERROR: Dependencies not installed!
    echo Please run 'install-dependencies.bat' first.
    pause
    exit /b 1
)

echo [Step 1/2] Building React app...
call yarn build
if errorlevel 1 (
    echo.
    echo ERROR: Failed to build React app!
    pause
    exit /b 1
)

echo.
echo [Step 2/2] Creating Windows installer...
echo This may take several minutes...
echo.

call yarn dist:win

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create installer!
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo  Build Complete!
    echo ========================================
    echo.
    echo Installer location: dist\90dayChonThanh Setup.exe
    echo.
)

pause
