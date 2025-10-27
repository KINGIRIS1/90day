@echo off
echo.
echo ========================================
echo   Starting 90dayChonThanh Desktop
echo   Port: 3001
echo ========================================
echo.

REM Set environment variables
set PORT=3001
set BROWSER=none

REM Start React + Electron
echo Starting React dev server on port 3001...
echo.
yarn electron-dev-win

pause
