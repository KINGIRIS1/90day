@echo off
echo ========================================
echo Fix Only GCN APIs - Windows Desktop
echo ========================================
echo.

echo Step 1: Killing all processes...
taskkill /F /IM electron.exe 2>nul
taskkill /F /IM node.exe 2>nul
echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo Step 2: Cleaning cache...
if exist node_modules\.cache (
    echo Deleting node_modules\.cache...
    rmdir /S /Q node_modules\.cache
)
if exist build (
    echo Deleting build...
    rmdir /S /Q build
)

echo.
echo Step 3: Cleaning Electron cache...
echo Deleting %APPDATA%\Electron...
del /Q /F "%APPDATA%\Electron\*" 2>nul
rmdir /S /Q "%APPDATA%\Electron" 2>nul
echo Deleting %LOCALAPPDATA%\Electron...
del /Q /F "%LOCALAPPDATA%\Electron\*" 2>nul
rmdir /S /Q "%LOCALAPPDATA%\Electron" 2>nul

echo.
echo Step 4: Reinstalling dependencies...
echo This may take a few minutes...
call yarn install

echo.
echo Step 5: Building frontend...
call yarn build

echo.
echo ========================================
echo Fix complete! Starting app...
echo ========================================
echo.
echo Press Ctrl+C to cancel, or
pause

call yarn electron-dev-win
