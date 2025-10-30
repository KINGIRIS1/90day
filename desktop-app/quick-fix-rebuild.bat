@echo off
echo ============================================
echo QUICK FIX - Update electron.js and rebuild
echo ============================================
echo.

REM Step 1: Kill processes
echo [1/5] Stopping processes...
taskkill /f /im 90dayChonThanh.exe 2>nul
taskkill /f /im electron.exe 2>nul
timeout /t 2 /nobreak >nul
echo Done.
echo.

REM Step 2: Clean dist
echo [2/5] Cleaning dist folder...
if exist dist (
    attrib -r -s -h dist\*.* /s /d 2>nul
    rd /s /q dist 2>nul
)
echo Done.
echo.

REM Step 3: Copy electron.js from electron folder to public
echo [3/5] Updating electron.js...
if exist electron\main.js (
    copy /y electron\main.js public\electron.js >nul
    echo electron.js updated from electron\main.js
) else (
    echo WARNING: electron\main.js not found!
)
echo Done.
echo.

REM Step 4: Build React (if needed)
if not exist build (
    echo [4/5] Building React app...
    call yarn build
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: React build failed!
        pause
        exit /b 1
    )
) else (
    echo [4/5] Skipping React build (already exists)
)
echo Done.
echo.

REM Step 5: Build Windows installer
echo [5/5] Building Windows installer...
echo This may take 3-5 minutes...
call npx electron-builder --win --x64
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo Done.
echo.

echo ============================================
echo BUILD COMPLETE!
echo ============================================
echo.

if exist "dist\90dayChonThanh Setup 1.1.0.exe" (
    for %%I in ("dist\90dayChonThanh Setup 1.1.0.exe") do set SIZE=%%~zI
    set /a SIZE_MB=!SIZE! / 1024 / 1024
    echo Installer: dist\90dayChonThanh Setup 1.1.0.exe
    echo Size: !SIZE_MB! MB
) else (
    echo ERROR: Installer not created!
    pause
    exit /b 1
)

echo.
echo Next: Install and test OCR!
pause
