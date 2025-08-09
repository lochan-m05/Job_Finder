# Local Development Setup (Without Docker)

Since Docker is not installed, here's how to run the Job Discovery Platform locally:

## Prerequisites

### 1. Install Python 3.11+
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

### 2. Install Node.js 18+
- Download from: https://nodejs.org/
- Choose LTS version

### 3. Install MongoDB Community Edition
- Download from: https://www.mongodb.com/try/download/community
- Or use MongoDB Atlas (cloud): https://www.mongodb.com/atlas

### 4. Install Redis
- For Windows: https://github.com/microsoftarchive/redis/releases
- Or use Redis Cloud: https://redis.com/try-free/

## Backend Setup

1. **Navigate to backend directory:**
   ```powershell
   cd backend
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Install Chrome for scraping:**
   - Download and install Google Chrome
   - Download ChromeDriver: https://chromedriver.chromium.org/

5. **Set environment variables:**
   ```powershell
   # Create .env file in backend directory
   $env:MONGODB_URL="mongodb://localhost:27017/job_discovery"
   $env:REDIS_URL="redis://localhost:6379/0"
   $env:SECRET_KEY="your-secret-key-here"
   ```

6. **Start backend server:**
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start Celery worker (new terminal):**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   celery -A app.services.celery_app worker --loglevel=info
   ```

## Frontend Setup

1. **Navigate to frontend directory:**
   ```powershell
   cd frontend
   ```

2. **Install dependencies:**
   ```powershell
   npm install
   ```

3. **Start development server:**
   ```powershell
   npm start
   ```

## Quick Start Script

I'll create a PowerShell script to automate the setup:

```powershell
# Run this script: .\local_start.ps1
```

## Access URLs

After starting both backend and frontend:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Troubleshooting

### Python Issues
- Ensure Python is in PATH: `python --version`
- Use `py` instead of `python` if needed

### Node.js Issues
- Ensure Node.js is installed: `node --version`
- Clear npm cache: `npm cache clean --force`

### Database Issues
- Start MongoDB service: `net start MongoDB`
- Start Redis service: `redis-server`

### Port Conflicts
- Change ports in configuration if 3000 or 8000 are in use
- Check running processes: `netstat -ano | findstr :8000`
