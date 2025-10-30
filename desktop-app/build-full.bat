@echo off
echo ==========================================
echo FULL BUILD - Include All Dependencies
echo ==========================================
echo.

REM Step 1: Clean everything
echo [1/5] Cleaning old builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo Done.
echo.

REM Step 2: Build React
echo [2/5] Building React app...
call yarn build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: React build failed!
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 3: Check build folder
echo [3/5] Verifying React build...
if not exist "build" (
    echo ERROR: build folder not found!
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 4: Build with explicit config
echo [4/5] Building Windows installer with full dependencies...
echo This may take 5-10 minutes...
echo.

call npx electron-builder --win --x64 ^
  --config.extends=null ^
  --config.files="build/**/*" ^
  --config.files="public/electron.js" ^
  --config.files="public/preload.js" ^
  --config.files="python/**/*" ^
  --config.files="node_modules/**/*" ^
  --config.files="package.json" ^
  --config.asarUnpack="python/**/*" ^
  --config.asarUnpack="node_modules/electron-store/**/*"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Electron builder failed!
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 5: Verify
echo [5/5] Verifying build...
if not exist "dist\90dayChonThanh Setup 1.1.0.exe" (
    echo ERROR: Installer not created!
    pause
    exit /b 1
)

for %%I in ("dist\90dayChonThanh Setup 1.1.0.exe") do set SIZE=%%~zI
set /a SIZE_MB=%SIZE% / 1024 / 1024

echo.
echo ==========================================
echo BUILD COMPLETE!
echo ==========================================
echo.
echo Installer: dist\90dayChonThanh Setup 1.1.0.exe
echo Size: %SIZE_MB% MB
echo.

if %SIZE_MB% LSS 100 (
    echo WARNING: Size is still too small (%SIZE_MB% MB)
    echo Expected: 150-200 MB
    echo.
    echo Checking app.asar contents...
    echo.
    npx asar list "dist\win-unpacked\resources\app.asar" | findstr /i "node_modules" > nul
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: node_modules NOT found in app.asar!
        echo The build configuration is not working correctly.
        echo.
        echo Please try manual steps in FIX_BUILD_MANUAL.md
    ) else (
        echo node_modules found in app.asar, but size is still small.
        echo This might be a compression issue.
    )
) else (
    echo ✓ Build size looks correct!
    echo Ready for distribution.
)

echo.
pause
