Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HealthStack System Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "Virtual environment found, using existing venv..." -ForegroundColor Green
} else {
    Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Write-Host "Make sure Python is installed and in your PATH" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Step 2: Using virtual environment Python..." -ForegroundColor Yellow
$pythonExe = ".\venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: Virtual environment Python not found at $pythonExe" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 3: Upgrading pip..." -ForegroundColor Yellow
& $pythonExe -m pip install --upgrade pip

Write-Host ""
Write-Host "Step 4: Installing requirements..." -ForegroundColor Yellow
& $pythonExe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install requirements" -ForegroundColor Red
    Write-Host "Try running: .\venv\Scripts\python.exe -m pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 5: Installing additional package..." -ForegroundColor Yellow
& $pythonExe -m pip install --upgrade djangorestframework-simplejwt

Write-Host ""
Write-Host "Step 6: Running migrations..." -ForegroundColor Yellow
& $pythonExe manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to run migrations" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the server, run:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "OR use the venv Python directly:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\python.exe manage.py runserver" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
