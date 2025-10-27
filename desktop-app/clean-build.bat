@echo off
echo.
echo ========================================
echo   Clean Build - 90dayChonThanh
echo ========================================
echo.

echo [1/5] Cleaning old builds...
if exist "build" (
    echo Removing build folder...
    rmdir /s /q build
)
if exist "dist" (
    echo Removing dist folder...
    rmdir /s /q dist
)
echo [OK] Old builds cleaned
echo.

echo [2/5] Building React app...
call yarn build
if errorlevel 1 (
    echo [ERROR] React build failed
    pause
    exit /b 1
)
echo [OK] React built
echo.

echo [3/5] Building Electron app...
call yarn electron-pack
if errorlevel 1 (
    echo [ERROR] Electron pack failed
    pause
    exit /b 1
)
echo [OK] Electron packed
echo.

echo [4/5] Verifying build...
if exist "dist\win-unpacked\90dayChonThanh.exe" (
    echo [OK] Executable found
) else (
    echo [ERROR] Executable not found
    pause
    exit /b 1
)
echo.

echo [5/5] Build complete!
echo.
echo ========================================
echo   BUILD SUCCESSFUL
echo ========================================
echo.
echo App location: dist\win-unpacked\
echo.
echo To run:
echo   cd dist\win-unpacked
echo   90dayChonThanh.exe
echo.
pause
