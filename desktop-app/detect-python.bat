@echo off
echo.
echo ========================================
echo   Detect Python Used by App
echo ========================================
echo.

echo Testing different Python commands...
echo.

echo [1] py command:
py --version
py -c "import sys; print('Executable:', sys.executable)"
py -c "import sys; print('Site-packages:', sys.path)"
echo.

echo [2] python command:
python --version
python -c "import sys; print('Executable:', sys.executable)"
echo.

echo [3] python3 command (if exists):
python3 --version 2>nul || echo python3 not found
echo.

echo [4] Which Python executables:
where py
where python
where python3 2>nul
echo.

echo [5] Testing pytesseract import:
echo.
echo Via py:
py -c "import pytesseract; print('OK: pytesseract found via py')" 2>nul || echo "FAIL: pytesseract not found via py"
echo.
echo Via python:
python -c "import pytesseract; print('OK: pytesseract found via python')" 2>nul || echo "FAIL: pytesseract not found via python"
echo.

echo [6] All Python versions:
py -0 2>nul || echo py launcher not available
echo.

echo ========================================
echo   Copy the output above and send to me
echo ========================================
pause
