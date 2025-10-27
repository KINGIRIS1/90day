@echo off
echo ============================================================
echo EASYOCR OPTIMIZATION TEST - Before vs After
echo ============================================================
echo.

set IMAGE_PATH=%1

if "%IMAGE_PATH%"=="" (
    echo Error: Please provide image path
    echo Usage: test-easyocr-optimized.bat "D:\test\image.jpg"
    exit /b 1
)

echo Testing image: %IMAGE_PATH%
echo.

echo ============================================================
echo TEST 1: ORIGINAL (Full image, default parameters)
echo Expected: ~30-40 seconds
echo ============================================================
echo.
python test_easyocr.py "%IMAGE_PATH%"

echo.
echo.
echo ============================================================
echo TEST 2: OPTIMIZED (Top 40%, resized, tuned parameters)
echo Expected: ~5-10 seconds (3-5x faster!)
echo ============================================================
echo.
python ocr_engine_easyocr.py "%IMAGE_PATH%"

echo.
echo ============================================================
echo COMPARISON COMPLETE!
echo ============================================================
echo.
echo Check the results above:
echo - Original: Full scan, many regions detected
echo - Optimized: Top 40% only, faster processing
echo.
echo The optimized version should be 3-5x faster while maintaining
echo good accuracy for document title/type detection.
echo ============================================================
