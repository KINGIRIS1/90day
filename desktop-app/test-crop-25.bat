@echo off
echo ============================================================
echo EASYOCR CROP OPTIMIZATION TEST
echo Testing different crop percentages
echo ============================================================
echo.

set IMAGE_PATH=%1

if "%IMAGE_PATH%"=="" (
    echo Error: Please provide image path
    echo Usage: test-crop-optimization.bat "D:\test\image.jpg"
    exit /b 1
)

echo Testing image: %IMAGE_PATH%
echo.
echo This will test EasyOCR with 25%% crop (optimized for speed)
echo.

echo ============================================================
echo Running EasyOCR with 25%% crop
echo Expected: ~7-8 seconds (fastest optimized version!)
echo ============================================================
echo.

python ocr_engine_easyocr.py "%IMAGE_PATH%"

echo.
echo ============================================================
echo TEST COMPLETE!
echo ============================================================
echo.
echo Check the results:
echo - OCR Time should be around 7-8 seconds
echo - Text regions detected should be ~30-35
echo - Should still capture title/header information
echo.
echo If text is missing important info, we can increase back to 30-35%%
echo ============================================================
