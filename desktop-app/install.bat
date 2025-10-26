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
echo === Installing PaddleOCR (Vietnamese specialized, 90-95%% accuracy) ===
echo This may take 5-10 minutes for first-time installation
echo Models (~100MB) will be downloaded on first run
echo.
cd python

REM Try to install PaddleOCR first (best accuracy)
echo [1/3] Installing PaddlePaddle...
python -m pip install paddlepaddle>=3.0.0 --quiet
if %ERRORLEVEL% EQU 0 (
    echo [OK] PaddlePaddle installed successfully
    echo.
    echo [2/3] Installing PaddleOCR...
    python -m pip install paddleocr>=3.0.0 --quiet
    if %ERRORLEVEL% EQU 0 (
        echo [OK] PaddleOCR installed successfully
        echo [SUCCESS] Using PaddleOCR engine - 90-95%% accuracy for Vietnamese!
    ) else (
        echo [WARN] PaddleOCR installation failed. Will use Tesseract fallback.
    )
) else (
    echo [WARN] PaddlePaddle installation failed. Will use Tesseract fallback.
)

echo.
echo [3/3] Installing other dependencies...
python -m pip install -r requirements-windows.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Python dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] All Python dependencies installed
echo.
echo === OCR Engine Info ===
echo - Primary: PaddleOCR (90-95%% accuracy)
echo - Fallback: Tesseract (85-88%% accuracy)
echo - For setup help: See PADDLEOCR_SETUP.md
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
