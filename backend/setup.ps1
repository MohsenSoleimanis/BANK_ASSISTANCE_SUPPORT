# Backend Setup Script
# Run this to set up the backend environment

Write-Host "Setting up Bank Support AI Backend..." -ForegroundColor Green

# Check Python version
Write-Host "`nChecking Python version..." -ForegroundColor Yellow
python --version

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Cyan
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
Write-Host "Run: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan

# Install dependencies
Write-Host "`nTo install dependencies, run after activating venv:" -ForegroundColor Yellow
Write-Host "pip install -r requirements.txt" -ForegroundColor Cyan

# Setup .env file
Write-Host "`nSetting up environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host ".env file already exists" -ForegroundColor Cyan
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file from .env.example" -ForegroundColor Green
    Write-Host "⚠️  Please edit .env and add your API keys!" -ForegroundColor Red
}

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Install deps: pip install -r requirements.txt" -ForegroundColor White
Write-Host "3. Edit .env file with your API keys" -ForegroundColor White
Write-Host "4. Start services: docker-compose up -d postgres redis qdrant" -ForegroundColor White
Write-Host "5. Ingest documents: python scripts/ingest_documents.py --path ../data/documents/policies" -ForegroundColor White
Write-Host "6. Run server: uvicorn app.main:app --reload" -ForegroundColor White
