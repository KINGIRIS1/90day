@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   All-in-One Installer Prerequisites
echo   Verification Script
echo ========================================
echo.

set ERRORS=0
set WARNINGS=0

REM Check NSIS
echo [1/8] Checking NSIS installation...
if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    echo [OK] NSIS found
    for /f "tokens=*" %%i in ('"C:\Program Files (x86)\NSIS\makensis.exe" /VERSION 2^>nul') do set NSIS_VER=%%i
    echo      Version: !NSIS_VER!
) else (
    echo [ERROR] NSIS not found
    echo        Download from: https://nsis.sourceforge.io/Download
    set /a ERRORS+=1
)
echo.

REM Check Node.js
echo [2/8] Checking Node.js...
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js not found
    echo        Download from: https://nodejs.org/
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
    echo [OK] Node.js found: !NODE_VER!
)
echo.

REM Check Yarn
echo [3/8] Checking Yarn...
where yarn >nul 2>nul
if errorlevel 1 (
    echo [WARNING] Yarn not found
    echo          Will install during build
    set /a WARNINGS+=1
) else (
    for /f "tokens=*" %%i in ('yarn --version') do set YARN_VER=%%i
    echo [OK] Yarn found: !YARN_VER!
)
echo.

REM Check Python
echo [4/8] Checking Python (for testing)...
where python >nul 2>nul
if errorlevel 1 (
    echo [WARNING] Python not found
    echo          Not required for build, but needed for testing
    set /a WARNINGS+=1
) else (
    for /f "tokens=*" %%i in ('python --version') do set PY_VER=%%i
    echo [OK] Python found: !PY_VER!
)
echo.

REM Check Tesseract
echo [5/8] Checking Tesseract (for testing)...
where tesseract >nul 2>nul
if errorlevel 1 (
    echo [WARNING] Tesseract not found
    echo          Not required for build, but needed for testing
    set /a WARNINGS+=1
) else (
    for /f "tokens=*" %%i in ('tesseract --version 2^>^&1 ^| findstr /C:"tesseract"') do set TESS_VER=%%i
    echo [OK] Tesseract found: !TESS_VER!
)
echo.

REM Check Python installer
echo [6/8] Checking Python installer...
if exist "installers\python-3.11.8-amd64.exe" (
    echo [OK] Python installer found
    for %%A in ("installers\python-3.11.8-amd64.exe") do (
        set size=%%~zA
        set /a sizeMB=!size!/1048576
        echo      Size: !sizeMB! MB
    )
) else (
    echo [ERROR] Python installer not found
    echo        Download from: https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    echo        Save to: installers\python-3.11.8-amd64.exe
    set /a ERRORS+=1
)
echo.

REM Check Tesseract installer
echo [7/8] Checking Tesseract installer...
if exist "installers\tesseract-ocr-w64-setup-5.3.3.exe" (
    echo [OK] Tesseract installer found
    for %%A in ("installers\tesseract-ocr-w64-setup-5.3.3.exe") do (
        set size=%%~zA
        set /a sizeMB=!size!/1048576
        echo      Size: !sizeMB! MB
    )
) else (
    echo [ERROR] Tesseract installer not found
    echo        Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo        Save to: installers\tesseract-ocr-w64-setup-5.3.3.exe
    set /a ERRORS+=1
)
echo.

REM Check disk space
echo [8/8] Checking disk space...
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do set FREESPACE=%%a
set FREESPACE=%FREESPACE:,=%
set /a FREEMB=%FREESPACE%/1048576
if %FREEMB% LSS 1000 (
    echo [WARNING] Low disk space: !FREEMB! MB free
    echo          Recommended: 1000+ MB free
    set /a WARNINGS+=1
) else (
    echo [OK] Disk space: !FREEMB! MB free
)
echo.

REM Summary
echo ========================================
echo   VERIFICATION SUMMARY
echo ========================================
echo.
echo Errors:   !ERRORS!
echo Warnings: !WARNINGS!
echo.

if !ERRORS! GTR 0 (
    echo [FAIL] Cannot proceed with build
    echo        Please fix errors above
    echo.
    goto END_FAIL
)

if !WARNINGS! GTR 0 (
    echo [PARTIAL] Can proceed, but with warnings
    echo           Some features may not work
    echo.
) else (
    echo [SUCCESS] All prerequisites satisfied!
    echo           Ready to build all-in-one installer
    echo.
)

REM Additional checks
echo ========================================
echo   ADDITIONAL INFO
echo ========================================
echo.

REM Check if already built
if exist "dist\win-unpacked" (
    echo [INFO] Found existing build in dist\win-unpacked\
    echo        Will use this if building installer
    echo.
)

REM Check if previous installer exists
if exist "90dayChonThanh-AllInOne-Setup.exe" (
    echo [INFO] Found previous installer
    for %%A in ("90dayChonThanh-AllInOne-Setup.exe") do (
        set size=%%~zA
        set /a sizeMB=!size!/1048576
        echo        Size: !sizeMB! MB
        echo        Created: %%~tA
    )
    echo.
)

REM Show next steps
echo ========================================
echo   NEXT STEPS
echo ========================================
echo.

if !ERRORS! EQU 0 (
    echo To build the all-in-one installer:
    echo.
    echo   1. Run: build-allinone.bat
    echo   2. Wait 5-10 minutes
    echo   3. Test: 90dayChonThanh-AllInOne-Setup.exe
    echo.
    echo To build just the app:
    echo.
    echo   1. Run: build.bat
    echo   2. Choose option 1, 2, or 3
    echo.
    
    set /p "PROCEED=Do you want to build now? (y/n): "
    if /i "!PROCEED!"=="y" (
        echo.
        echo Starting build...
        call build-allinone.bat
    ) else (
        echo.
        echo Build cancelled. Run build-allinone.bat when ready.
    )
) else (
    echo Please fix the errors above before building.
    echo.
    echo Required downloads:
    if not exist "installers\python-3.11.8-amd64.exe" (
        echo   - Python: https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    )
    if not exist "installers\tesseract-ocr-w64-setup-5.3.3.exe" (
        echo   - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
    )
    if not exist "C:\Program Files (x86)\NSIS\makensis.exe" (
        echo   - NSIS: https://nsis.sourceforge.io/Download
    )
)

echo.
goto END_SUCCESS

:END_FAIL
pause
exit /b 1

:END_SUCCESS
pause
exit /b 0
