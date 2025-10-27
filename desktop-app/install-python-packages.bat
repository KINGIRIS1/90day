@echo off
echo.
echo ========================================
echo   Auto-Install Python Packages
echo   90dayChonThanh Desktop App
echo ========================================
echo.

echo [1/3] Installing pytesseract and Pillow...
echo.

REM Try multiple installation methods
echo Trying method 1: py -m pip install...
py -m pip install pytesseract Pillow --upgrade
echo.

echo Trying method 2: python -m pip install...
python -m pip install pytesseract Pillow --upgrade
echo.

echo Trying method 3: pip install...
pip install pytesseract Pillow --upgrade
echo.

echo [2/3] Verifying installation...
echo.

py -m pip show pytesseract
if errorlevel 1 (
    echo [!] pytesseract not found via py
) else (
    echo [OK] pytesseract installed via py
)

echo.
py -m pip show Pillow
if errorlevel 1 (
    echo [!] Pillow not found via py
) else (
    echo [OK] Pillow installed via py
)

echo.
echo [3/3] Testing import...
echo.

py -c "import pytesseract; import PIL; print('SUCCESS: All packages imported correctly')" 2>nul
if errorlevel 1 (
    echo [!] Import test failed
    echo.
    echo Please check:
    echo 1. Python is installed correctly
    echo 2. pip is working
    echo 3. No conflicting Python versions
) else (
    echo [OK] Packages working correctly!
)

echo.
echo ========================================
echo   Installation Complete
echo ========================================
echo.
echo Next steps:
echo 1. Restart the desktop app
echo 2. Try scanning a document
echo.
pause
