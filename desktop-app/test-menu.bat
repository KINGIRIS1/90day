@echo off
REM Simple test script to debug menu issue

echo Testing menu display...
echo.
echo ========================================
echo   TEST MENU
echo ========================================
echo.
echo   1. Option One
echo.
echo   2. Option Two
echo.
echo   3. Option Three
echo.
echo ========================================
echo.

set /p "choice=Enter your choice (1, 2, or 3): "

echo.
echo You entered: "%choice%"
echo.

if "%choice%"=="1" (
    echo You selected Option 1
) else if "%choice%"=="2" (
    echo You selected Option 2
) else if "%choice%"=="3" (
    echo You selected Option 3
) else (
    echo Invalid choice: "%choice%"
)

echo.
pause
