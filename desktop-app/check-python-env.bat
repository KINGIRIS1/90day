@echo off
echo.
echo ========================================
echo   Python Environment Check
echo ========================================
echo.

REM Check Python versions
echo [1/6] Checking Python versions...
echo.
echo Python (py launcher):
py --version 2>nul || echo [NOT FOUND]
echo.
echo Python (python command):
python --version 2>nul || echo [NOT FOUND]
echo.

REM Check Python locations
echo [2/6] Checking Python locations...
echo.
where py 2>nul || echo py: [NOT FOUND]
where python 2>nul || echo python: [NOT FOUND]
echo.

REM Check pip version
echo [3/6] Checking pip...
echo.
py -m pip --version 2>nul || echo [pip NOT FOUND via py]
echo.

REM Check installed packages
echo [4/6] Checking required packages...
echo.
echo Checking pytesseract:
py -m pip show pytesseract 2>nul || echo [NOT INSTALLED]
echo.
echo Checking Pillow:
py -m pip show Pillow 2>nul || echo [NOT INSTALLED]
echo.

REM Check Tesseract
echo [5/6] Checking Tesseract OCR...
echo.
tesseract --version 2>nul || echo [Tesseract NOT FOUND]
echo.

REM List all Python versions
echo [6/6] Available Python versions:
echo.
py -0 2>nul || echo [Python launcher not available]
echo.

REM Summary
echo ========================================
echo   SUMMARY
echo ========================================
echo.

REM Check if packages are missing
py -m pip show pytesseract >nul 2>nul
if errorlevel 1 (
    echo [!] pytesseract NOT INSTALLED
    echo.
    echo To fix, run:
    echo   py -m pip install pytesseract Pillow
    echo.
) else (
    echo [OK] pytesseract installed
)

py -m pip show Pillow >nul 2>nul
if errorlevel 1 (
    echo [!] Pillow NOT INSTALLED
    echo.
    echo To fix, run:
    echo   py -m pip install pytesseract Pillow
    echo.
) else (
    echo [OK] Pillow installed
)

tesseract --version >nul 2>nul
if errorlevel 1 (
    echo [!] Tesseract NOT INSTALLED
    echo.
    echo Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
) else (
    echo [OK] Tesseract installed
)

echo.
echo ========================================
pause
