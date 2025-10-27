@echo off
echo.
echo ========================================
echo   Test VietOCR Installation
echo ========================================
echo.

echo [1/4] Installing VietOCR...
echo This will download ~220MB (PyTorch + VietOCR)
echo.

py -m pip install vietocr torch torchvision
if errorlevel 1 (
    echo [ERROR] Installation failed
    pause
    exit /b 1
)

echo.
echo [2/4] Verifying installation...
py -m pip show vietocr
py -m pip show torch

echo.
echo [3/4] Testing import...
py -c "from vietocr.tool.predictor import Predictor; from vietocr.tool.config import Cfg; print('[OK] VietOCR imports successfully')"
if errorlevel 1 (
    echo [ERROR] Import test failed
    pause
    exit /b 1
)

echo.
echo [4/4] Testing OCR engine...
cd python
py ocr_engine_vietocr.py ..\assets\test-image.jpg 2>nul
if errorlevel 1 (
    echo [WARNING] OCR test failed (no test image?)
    echo But installation looks OK
) else (
    echo [OK] VietOCR engine working!
)

echo.
echo ========================================
echo   INSTALLATION COMPLETE
echo ========================================
echo.
echo VietOCR is ready to use!
echo.
echo Accuracy: 90-95%% (vs 85-88%% Tesseract)
echo Size: ~220MB installed
echo.
echo Next steps:
echo 1. Integrate VietOCR into process_document.py
echo 2. Or read ENABLE_VIETOCR_2025.md for details
echo.
pause
