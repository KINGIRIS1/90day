@echo off
chcp 65001 >nul
color 0C
title EMERGENCY FIX - Check & Verify

echo.
echo ========================================
echo   EMERGENCY FIX - Diagnostic
echo ========================================
echo.

echo Please do the following IN THE APP:
echo.
echo 1. Press F12 to open DevTools
echo 2. Go to Console tab
echo 3. Type this command and press Enter:
echo.
echo    console.log(typeof window.electronAPI.analyzeBatchFile);
echo.
echo 4. Tell me the result:
echo    - If it says "function" → API is loaded ✅
echo    - If it says "undefined" → API NOT loaded ❌
echo.
echo ========================================
echo.
pause

echo.
echo If result was "undefined", do this:
echo.
echo 1. Type this in Console:
echo    Object.keys(window.electronAPI)
echo.
echo 2. Check if "analyzeBatchFile" is in the list
echo.
echo If NOT in the list → preload.js is still OLD!
echo.
pause

echo.
echo ========================================
echo   NUCLEAR OPTION - Complete Rebuild
echo ========================================
echo.
echo If API is still undefined, we need to:
echo 1. Completely delete this folder
echo 2. Copy FRESH from server
echo 3. Rebuild from scratch
echo.
echo Press Ctrl+C to cancel
echo Press any key to continue with nuclear option...
pause

echo.
echo [NUCLEAR] Deleting current installation...
cd ..
rmdir /S /Q desktop-app 2>nul

echo.
echo ❌ Folder deleted!
echo.
echo NOW YOU MUST:
echo 1. Copy FRESH desktop-app folder from server
echo 2. cd desktop-app
echo 3. yarn install
echo 4. yarn electron-dev-win
echo.
pause
