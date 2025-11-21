@echo off
echo ========================================
echo  Installing Dependencies
echo ========================================
echo.

echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js version:
node --version
echo.

echo Checking Yarn installation...
yarn --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Yarn is not installed!
    echo Installing Yarn globally...
    npm install -g yarn
    if errorlevel 1 (
        echo Failed to install Yarn!
        pause
        exit /b 1
    )
)

echo Yarn version:
yarn --version
echo.

echo Installing project dependencies...
echo This may take a few minutes...
echo.

call yarn install

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo  Installation Complete!
    echo ========================================
    echo.
    echo Next steps:
    echo   - Run 'run-app.bat' to start the application
    echo   - Run 'run-dev.bat' for development mode
    echo.
)

pause
