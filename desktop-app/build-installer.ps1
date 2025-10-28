# PowerShell build script for v1.1.0
# Run as Administrator

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "BUILD WINDOWS INSTALLER v1.1.0 (PowerShell)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Node.js
Write-Host "[STEP 1/6] Checking Node.js..." -ForegroundColor Yellow

try {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    Write-Host "Make sure to check 'Add to PATH' during installation" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Check npm
Write-Host ""
Write-Host "[STEP 2/6] Checking npm..." -ForegroundColor Yellow

try {
    $npmVersion = npm --version
    Write-Host "[OK] npm found: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] npm not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 3: Install dependencies
Write-Host ""
Write-Host "[STEP 3/6] Installing Node.js dependencies..." -ForegroundColor Yellow
Write-Host "This may take 2-5 minutes..." -ForegroundColor Gray

npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# Step 4: Install Python packages (optional)
Write-Host ""
Write-Host "[STEP 4/6] Installing Python dependencies..." -ForegroundColor Yellow

cd python
try {
    python -m pip install -r requirements.txt
    Write-Host "[OK] Python packages installed" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Python packages install failed (OK for app-only build)" -ForegroundColor Yellow
}
cd ..

# Step 5: Build React frontend
Write-Host ""
Write-Host "[STEP 5/6] Building React frontend..." -ForegroundColor Yellow
Write-Host "This may take 2-3 minutes..." -ForegroundColor Gray

npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to build React frontend" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] React frontend built" -ForegroundColor Green

# Step 6: Build Electron app
Write-Host ""
Write-Host "[STEP 6/6] Building Electron app + installer..." -ForegroundColor Yellow
Write-Host "This may take 3-5 minutes..." -ForegroundColor Gray

npm run electron-build
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to build Electron app" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Success
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "BUILD COMPLETE!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""

# Check output
if (Test-Path "dist\90dayChonThanh Setup*.exe") {
    Write-Host "[SUCCESS] Installer created:" -ForegroundColor Green
    Get-ChildItem "dist\90dayChonThanh*.exe" | Select-Object Name, Length
    Write-Host ""
    Write-Host "Location: $PWD\dist\" -ForegroundColor Cyan
} elseif (Test-Path "dist\win-unpacked") {
    Write-Host "[SUCCESS] Portable app created in: dist\win-unpacked\" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Build output not found in expected location" -ForegroundColor Yellow
    Write-Host "Check dist\ folder manually" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Test installer on this machine" -ForegroundColor White
Write-Host "2. Test on clean Windows machine (recommended)" -ForegroundColor White
Write-Host "3. Upload to Google Drive" -ForegroundColor White
Write-Host "4. Share with users" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
