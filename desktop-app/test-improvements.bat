@echo off
echo ================================================================================
echo TEST v1.1.0 IMPROVEMENTS
echo ================================================================================
echo.

REM Check if image path provided
if "%~1"=="" (
    echo Error: No image file specified
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
    echo Error: File not found: %~1
    echo.
    pause
    exit /b 1
)

echo Testing with image: %~1
echo.

REM Detect Python - Try multiple methods
set PYTHON_CMD=

REM Method 1: Try 'python' command
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :found_python
)

REM Method 2: Try 'py' launcher
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
    goto :found_python
)

REM Method 3: Try common installation paths
if exist "C:\Python311\python.exe" (
    set PYTHON_CMD=C:\Python311\python.exe
    goto :found_python
)

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe
    goto :found_python
)

REM Not found
echo Error: Python not found
echo.
echo Please try running directly:
echo   python test-improvements.py "%~1"
echo.
echo Or:
echo   py test-improvements.py "%~1"
echo.
pause
exit /b 1

:found_python
echo Found Python: %PYTHON_CMD%
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
