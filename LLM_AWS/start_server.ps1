# PowerShell script to start AI Chat API Server

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🚀 Starting AI Chat API Server on Port 7000" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if in correct directory (should be in Bookies_Website root)
if (-not (Test-Path "LLM_AWS\main.py")) {
    Write-Host "❌ Error: Please run this script from Bookies_Website root directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Expected: D:\Bookies_Website (or your project root)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  cd D:\Bookies_Website" -ForegroundColor White
    Write-Host "  .\LLM_AWS\start_server.ps1" -ForegroundColor White
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow

# Check if FastAPI is installed
$fastapi = pip show fastapi 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Dependencies not installed" -ForegroundColor Yellow
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r LLM_AWS\requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "✅ Dependencies OK" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Starting server..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 Server will be available at:" -ForegroundColor Cyan
Write-Host "   - http://localhost:7000" -ForegroundColor White
Write-Host "   - Swagger UI: http://localhost:7000/docs" -ForegroundColor White
Write-Host "   - ReDoc: http://localhost:7000/redoc" -ForegroundColor White
Write-Host ""
Write-Host "💡 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
python LLM_AWS\run_server.py
