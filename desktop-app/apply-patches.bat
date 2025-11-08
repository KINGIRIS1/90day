@echo off
chcp 65001 >nul
color 0E
title Apply Patches - Batch Scan Feature

echo.
echo ========================================
echo   Apply Patches - Batch Scan Feature
echo ========================================
echo.
echo This will copy updated files from server
echo to fix the API errors.
echo.
echo Files to be updated:
echo   - electron\preload.js
echo   - electron\main.js
echo   - src\App.js
echo.
pause

echo.
echo [Step 1] Backing up old files...

if exist electron\preload.js (
    copy electron\preload.js electron\preload.js.backup >nul
    echo ✅ Backed up electron\preload.js
)

if exist electron\main.js (
    copy electron\main.js electron\main.js.backup >nul
    echo ✅ Backed up electron\main.js
)

if exist src\App.js (
    copy src\App.js src\App.js.backup >nul
    echo ✅ Backed up src\App.js
)

echo.
echo [Step 2] You need to manually copy these files from server:
echo.
echo FROM SERVER:                          TO LOCAL:
echo ├─ /app/desktop-app/electron/preload.js  →  electron\preload.js
echo ├─ /app/desktop-app/electron/main.js     →  electron\main.js
echo └─ /app/desktop-app/src/App.js           →  src\App.js
echo.
echo MANUAL STEPS:
echo 1. Open FileZilla / WinSCP / Your FTP client
echo 2. Connect to server
echo 3. Navigate to /app/desktop-app/
echo 4. Download these 3 files
echo 5. Overwrite the files in your local folder
echo.

pause

echo.
echo [Step 3] After copying files, run this:
echo.
echo    check-files.bat
echo.
echo To verify all files are correct.
echo.
echo Then run:
echo.
echo    fix-api-error.bat
echo.
echo To clean cache and restart app.
echo.

pause
