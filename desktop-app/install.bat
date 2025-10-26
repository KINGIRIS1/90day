@echo off
REM Desktop App Installation Script for Windows
REM Automates the setup process for the Land Document Scanner Desktop App

echo ======================================
echo   Desktop App Installation Script
echo ======================================
echo.

REM Check Node.js
echo Checking Node.js...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION%

REM Check Yarn
echo Checking Yarn...
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Yarn not found. Installing...
    npm install -g yarn
)
for /f "tokens=*" %%i in ('yarn --version') do set YARN_VERSION=%%i
echo [OK] Yarn %YARN_VERSION%

REM Check Python
echo Checking Python...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION%

REM Check pip
echo Checking pip...
python -m pip --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip not found
    echo Please install pip for Python
    pause
    exit /b 1
)
echo [OK] pip found

echo.
echo ======================================
echo   Installing Dependencies
echo ======================================
echo.

REM Install JavaScript dependencies
echo [INSTALL] Installing JavaScript dependencies...
call yarn install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install JavaScript dependencies
    pause
    exit /b 1
)
echo [OK] JavaScript dependencies installed
echo.

REM Install Python dependencies
echo [INSTALL] Installing Python dependencies...
echo.
echo === Installing VietOCR (Vietnamese Transformer-based, 90-95%% accuracy) ===
echo This may take 5-10 minutes for first-time installation
echo Models will be downloaded on first run (~100MB)
echo.
cd python

REM Install VietOCR (Vietnamese specialized)
echo [1/2] Installing VietOCR with Transformer model...
python -m pip install vietocr torch torchvision --quiet
if %ERRORLEVEL% EQU 0 (
    echo [OK] VietOCR installed successfully
    echo [SUCCESS] Using VietOCR engine - 90-95%% accuracy for Vietnamese!
) else (
    echo [WARN] VietOCR installation failed. Will use Tesseract fallback.
    echo [INFO] This is OK - Tesseract provides 85-88%% accuracy.
)

echo.
echo [2/2] Installing other dependencies...
python -m pip install Pillow opencv-python-headless pytesseract --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install basic dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] All Python dependencies installed
echo.
echo === OCR Engine Info ===
python -c "try: from vietocr.tool.predictor import Predictor; print('✓ Primary: VietOCR (90-95%% accuracy - Vietnamese Transformer)')" 2>nul || echo "○ Primary: VietOCR (not available)"
python -c "try: import pytesseract; print('✓ Fallback: Tesseract (85-88%% accuracy)')" 2>nul || echo "○ Fallback: Tesseract (not available)"
echo.
echo [INFO] For VietOCR setup help: See VIETOCR_SETUP.md
echo.

echo ======================================
echo   Installation Complete!
echo ======================================
echo.
echo [RUN] To run the app in development mode:
echo    yarn electron-dev
echo.
echo [BUILD] To build for production:
echo    yarn build
echo    yarn electron-build
echo.
echo [DOCS] For more info, see:
echo    - README.md
echo    - QUICK_START_VI.md
echo.
pause
