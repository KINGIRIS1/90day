@echo off
echo ============================================
echo FIXING ocr_engine_gemini_flash.py
echo ============================================
echo.

REM Step 1: Backup broken file
echo [1/3] Backing up broken file...
copy /y "C:\Users\nguye\AppData\Local\Programs\90daychonhanh-desktop\resources\app\python\ocr_engine_gemini_flash.py" "C:\Users\nguye\AppData\Local\Programs\90daychonhanh-desktop\resources\app\python\ocr_engine_gemini_flash.py.broken"
echo Done.
echo.

REM Step 2: Copy working file from source
echo [2/3] Copying working file from source...
copy /y "C:\desktop-app\python\ocr_engine_gemini_flash.py" "C:\Users\nguye\AppData\Local\Programs\90daychonhanh-desktop\resources\app\python\ocr_engine_gemini_flash.py"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to copy file!
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 3: Test
echo [3/3] Testing...
cd C:\Users\nguye\AppData\Local\Programs\90daychonhanh-desktop\resources\app\python
py -c "from ocr_engine_gemini_flash import classify_document_gemini_flash; print('Import OK')"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Import failed!
    pause
    exit /b 1
)
echo.

echo ============================================
echo FILE FIXED!
echo ============================================
echo.
echo Now test app or run:
echo py process_document.py "your_image.jpg" gemini-flash YOUR_API_KEY
echo.
pause
