# Build Windows Installer for 90dayChonThanh
# PowerShell Script

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Build Windows Installer - 90dayChonThanh" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
$nodeVersion = node --version
Write-Host "✓ Node.js installed: $nodeVersion" -ForegroundColor Green

# Check Yarn
Write-Host "`nChecking Yarn..." -ForegroundColor Yellow
if (!(Get-Command yarn -ErrorAction SilentlyContinue)) {
    Write-Host "Yarn not found. Installing..." -ForegroundColor Yellow
    npm install -g yarn
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install Yarn!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}
$yarnVersion = yarn --version
Write-Host "✓ Yarn installed: $yarnVersion" -ForegroundColor Green

# Install dependencies
Write-Host "`n[1/3] Installing dependencies..." -ForegroundColor Cyan
yarn install
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Build React app
Write-Host "`n[2/3] Building React app..." -ForegroundColor Cyan
yarn build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build React app!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ React app built" -ForegroundColor Green

# Build Windows installer
Write-Host "`n[3/3] Building Windows installer (NSIS)..." -ForegroundColor Cyan
npx electron-builder --win --x64
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build Windows installer!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Windows installer built" -ForegroundColor Green

# Success
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "`nYour installer is located at:" -ForegroundColor Cyan
Write-Host "dist\90dayChonThanh Setup 1.1.0.exe" -ForegroundColor Yellow
Write-Host ""

# Get file size
$installerPath = "dist\90dayChonThanh Setup 1.1.0.exe"
if (Test-Path $installerPath) {
    $fileSize = (Get-Item $installerPath).Length / 1MB
    Write-Host "Installer size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
}

Write-Host "`nYou can now distribute this installer to users!" -ForegroundColor Green
Read-Host "`nPress Enter to exit"
