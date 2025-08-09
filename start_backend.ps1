# Simple Backend Startup Script
Write-Host "Starting Job Discovery Backend..." -ForegroundColor Green

# Navigate to backend directory
cd backend

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Start the backend server
Write-Host "Starting FastAPI server on http://localhost:8000..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host "API Documentation will be available at: http://localhost:8000/docs" -ForegroundColor Blue

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
