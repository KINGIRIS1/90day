@echo off
echo ==========================================
echo Verify Build Package
echo ==========================================
echo.

REM Check if dist folder exists
if not exist "dist" (
    echo ERROR: dist folder not found!
    echo Please run build-windows.bat first
    pause
    exit /b 1
)

REM Check for installer
if not exist "dist\90dayChonThanh Setup 1.1.0.exe" (
    echo ERROR: Installer not found!
    pause
    exit /b 1
)

REM Check installer size
for %%I in ("dist\90dayChonThanh Setup 1.1.0.exe") do set SIZE=%%~zI
set /a SIZE_MB=%SIZE% / 1024 / 1024
echo Installer size: %SIZE_MB% MB

if %SIZE_MB% LSS 100 (
    echo.
    echo WARNING: Installer size is too small!
    echo Expected: ~150-200 MB
    echo Actual: %SIZE_MB% MB
    echo.
    echo This may indicate missing dependencies or resources.
    echo Please check the build configuration.
    pause
    exit /b 1
)

echo.
echo Checking unpacked files...

REM Check win-unpacked
if not exist "dist\win-unpacked" (
    echo ERROR: win-unpacked folder not found!
    pause
    exit /b 1
)

REM Check resources
if not exist "dist\win-unpacked\resources" (
    echo ERROR: resources folder not found!
    pause
    exit /b 1
)

REM Check app.asar
if not exist "dist\win-unpacked\resources\app.asar" (
    echo ERROR: app.asar not found!
    pause
    exit /b 1
)

REM Check python folder
if not exist "dist\win-unpacked\resources\python" (
    echo ERROR: python folder not found in resources!
    echo This will cause OCR to fail.
    pause
    exit /b 1
)

echo.
echo Checking app.asar contents...
npx asar list "dist\win-unpacked\resources\app.asar" | findstr /i "electron.js" > nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: electron.js not found in app.asar!
    pause
    exit /b 1
)

npx asar list "dist\win-unpacked\resources\app.asar" | findstr /i "node_modules" > nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: node_modules may be missing in app.asar!
    echo This could cause runtime errors.
)

echo.
echo ==========================================
echo ✓ Build verification passed!
echo ==========================================
echo.
echo Installer: dist\90dayChonThanh Setup 1.1.0.exe
echo Size: %SIZE_MB% MB
echo.
echo The package is ready for distribution!
echo.
pause
