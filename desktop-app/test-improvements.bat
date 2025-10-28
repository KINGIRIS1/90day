@echo off
chcp 65001 >nul
echo ================================================================================
echo 🧪 TEST v1.1.0 IMPROVEMENTS
echo ================================================================================
echo.

REM Check if image path provided
if "%~1"=="" (
    echo ❌ Error: No image file specified
    echo.
    echo Usage: test-improvements.bat "path\to\image.jpg"
    echo.
    echo Example:
    echo   test-improvements.bat "C:\Users\nguye\Desktop\test.jpg"
    echo.
    pause
    exit /b 1
)

REM Check if file exists
if not exist "%~1" (
    echo ❌ Error: File not found: %~1
    echo.
    pause
    exit /b 1
)

echo 📁 Testing with image: %~1
echo.

REM Detect Python
set PYTHON_CMD=
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=py
    ) else (
        echo ❌ Error: Python not found
        echo Please install Python 3.8+ from https://www.python.org/
        pause
        exit /b 1
    )
)

echo ✅ Found Python: %PYTHON_CMD%
echo.

REM Run test script
echo 🚀 Starting test...
echo.

%PYTHON_CMD% test-improvements.py "%~1"

echo.
echo ================================================================================
echo 📝 Test complete! Review results above.
echo ================================================================================
echo.
pause
