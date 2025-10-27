@echo off
echo ============================================================
echo DEBUG CLASSIFICATION - HOP DONG CHUYEN NHUONG
echo ============================================================
echo.

set IMAGE_PATH=%1

if "%IMAGE_PATH%"=="" (
    echo Error: Please provide image path
    echo Usage: debug-classification.bat "D:\test\image.jpg"
    exit /b 1
)

echo Testing image: %IMAGE_PATH%
echo.
echo This will show detailed classification process...
echo.

python process_document.py "%IMAGE_PATH%" easyocr

echo.
echo ============================================================
pause
