# Clean locally bundled Python packages incorrectly copied into the source tree
# Usage: Right-click > Run with PowerShell (or run: powershell -ExecutionPolicy Bypass -File .\\scripts\\clean-local-python.ps1)

$ErrorActionPreference = 'Continue'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktopApp = Split-Path -Parent $projectRoot
$pythonDir = Join-Path $desktopApp 'python'

if (-not (Test-Path $pythonDir)) {
  Write-Host "Python directory not found: $pythonDir" -ForegroundColor Yellow
  exit 0
}

$targets = @(
  'PIL','Pillow','requests','urllib3','certifi','charset_normalizer','idna',
  'google','google_ai','googleai','google_api_python_client','grpc','grpcio','proto*',
  '*dist-info','*egg-info','httpx','httpcore','h2','h11','anyio','sniffio','rsa','cachetools',
  'pip','setuptools','wheel','pkg_resources'
)

Write-Host "Cleaning vendor-like packages under: $pythonDir" -ForegroundColor Cyan

foreach ($pattern in $targets) {
  Get-ChildItem -LiteralPath $pythonDir -Filter $pattern -Force -ErrorAction SilentlyContinue | ForEach-Object {
    try {
      if ($_.PSIsContainer) {
        Write-Host "Removing folder: $($_.FullName)" -ForegroundColor Red
        Remove-Item -Recurse -Force -LiteralPath $_.FullName
      } else {
        Write-Host "Removing file: $($_.FullName)" -ForegroundColor Red
        Remove-Item -Force -LiteralPath $_.FullName
      }
    } catch {
      Write-Warning "Failed to remove: $($_.FullName) -> $($_.Exception.Message)"
    }
  }
}

Write-Host "Done. Only project .py files should remain in $pythonDir." -ForegroundColor Green
