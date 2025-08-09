# Simple Frontend Startup Script
Write-Host "Starting Job Discovery Frontend..." -ForegroundColor Green

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the frontend development server
Write-Host "Starting React development server on http://localhost:3000..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan

npm start
