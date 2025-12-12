# PowerShell Script to Fix Docker Compose
# Run this to create a working docker-compose that skips frontend for now

$rootDir = "bank-support-ai"

if (-not (Test-Path $rootDir)) {
    Write-Host "Error: $rootDir directory not found!" -ForegroundColor Red
    exit 1
}

Set-Location $rootDir

Write-Host "Fixing docker-compose.yml..." -ForegroundColor Yellow

# Create updated docker-compose WITHOUT frontend for now
$docker_compose = @'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: bankdb
      POSTGRES_USER: bankuser
      POSTGRES_PASSWORD: bankpass123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bankuser"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  qdrant_data:
'@

Set-Content -Path "docker-compose.yml" -Value $docker_compose -Encoding UTF8

Write-Host "✅ Fixed docker-compose.yml (removed frontend for now)" -ForegroundColor Green
Write-Host "`nNow run:" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor Cyan
Write-Host "  docker-compose up -d" -ForegroundColor Cyan