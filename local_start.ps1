# Job Discovery Platform - Local Development Startup Script
# Run this script: .\local_start.ps1

Write-Host "Starting Job Discovery Platform (Local Development)" -ForegroundColor Blue
Write-Host "================================================================" -ForegroundColor Blue

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.11+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found. Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Check if backend directory exists
if (-not (Test-Path "backend")) {
    Write-Host "[ERROR] Backend directory not found. Creating project structure..." -ForegroundColor Red
    New-Item -ItemType Directory -Path "backend", "frontend" -Force
}

# Setup backend
Write-Host "Setting up backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Install requirements if they exist
if (Test-Path "requirements.txt") {
    Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
} else {
    Write-Host "Installing basic dependencies..." -ForegroundColor Cyan
    pip install fastapi uvicorn python-multipart python-jose motor beanie celery redis requests beautifulsoup4 selenium spacy transformers nltk scikit-learn email-validator phonenumbers python-dotenv loguru
    
    # Download spaCy model
    python -m spacy download en_core_web_sm
}

# Create basic app structure if it doesn't exist
if (-not (Test-Path "app")) {
    Write-Host "Creating basic app structure..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path "app" -Force
    
    # Create a simple main.py
    @"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Job Discovery Platform API",
    description="AI-powered job discovery with real-time scraping and NLP analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Job Discovery Platform API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"@ | Out-File -FilePath "app\main.py" -Encoding utf8
}

# Go back to root
Set-Location ..

# Setup frontend
Write-Host "Setting up frontend..." -ForegroundColor Yellow
Set-Location frontend

# Initialize React app if package.json doesn't exist
if (-not (Test-Path "package.json")) {
    Write-Host "Creating React application..." -ForegroundColor Cyan
    npx create-react-app . --template typescript --yes
}

# Install additional dependencies
if (Test-Path "package.json") {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
    npm install axios react-router-dom @types/react-router-dom tailwindcss @headlessui/react @heroicons/react recharts react-query
}

# Go back to root
Set-Location ..

# Create environment file
if (-not (Test-Path ".env")) {
    Write-Host "Creating environment configuration..." -ForegroundColor Cyan
    @"
# Database Configuration
MONGODB_URL=mongodb://localhost:27017/job_discovery
DATABASE_NAME=job_discovery

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Development settings
DEBUG=true
"@ | Out-File -FilePath ".env" -Encoding utf8
}

# Start services
Write-Host "Starting services..." -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Blue

# Start backend in new window
Write-Host "Starting backend server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# Wait a moment
Start-Sleep 3

# Start frontend in new window
Write-Host "Starting frontend server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm start"

# Show completion message
Write-Host ""
Write-Host "Job Discovery Platform is starting!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Blue
Write-Host "Frontend:      http://localhost:3000" -ForegroundColor Yellow
Write-Host "Backend API:   http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Docs:      http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Note: For full functionality, you will also need:" -ForegroundColor Yellow
Write-Host "   - MongoDB running on localhost:27017" -ForegroundColor Yellow
Write-Host "   - Redis running on localhost:6379" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop services, close the PowerShell windows" -ForegroundColor Cyan
Write-Host "For Docker setup, install Docker Desktop and run: docker-compose up" -ForegroundColor Cyan

# Keep this window open
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
