# 🚀 Quick Start Guide

## Choose Your Setup Method:

### 🐳 **Option 1: Docker Setup (Recommended)**

**Prerequisites:**
- Install Docker Desktop: https://www.docker.com/products/docker-desktop/

**Steps:**
```powershell
# 1. Start services
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### 💻 **Option 2: Local Development (Without Docker)**

**Prerequisites:**
- Python 3.11+ (https://python.org)
- Node.js 18+ (https://nodejs.org)
- MongoDB (https://mongodb.com/try/download/community)
- Redis (https://github.com/microsoftarchive/redis/releases)

**Quick Start:**
```powershell
# Run the automated setup script
.\local_start.ps1
```

**Manual Setup:**
```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn motor celery redis selenium beautifulsoup4 spacy
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npx create-react-app . --template typescript
npm install axios react-router-dom tailwindcss
npm start
```

---

## 🔧 **Troubleshooting**

### Docker Issues:
- **Docker not found**: Install Docker Desktop
- **Port conflicts**: Stop services using ports 3000, 8000, 27017, 6379
- **Permission denied**: Run PowerShell as Administrator

### Local Development Issues:
- **Python not found**: Add Python to PATH during installation
- **Node.js not found**: Install from nodejs.org
- **Module not found**: Activate virtual environment first

### Database Issues:
- **MongoDB connection**: Start MongoDB service or use MongoDB Atlas
- **Redis connection**: Start Redis server or use Redis Cloud

---

## 📖 **Next Steps**

1. **Configure Environment**: Edit `.env` file with your settings
2. **Add API Keys**: LinkedIn credentials, CAPTCHA service, proxies
3. **Start Scraping**: Search with hashtags like `#python #developer #remote`
4. **Explore Features**: Dashboard, analytics, contact management

---

## 🆘 **Getting Help**

If you encounter any issues:

1. **Check Prerequisites**: Ensure all required software is installed
2. **Review Logs**: Check console output for error messages
3. **Restart Services**: Stop and start again
4. **Clean Install**: Remove node_modules/venv and reinstall

**Common Commands:**
```powershell
# Check what's running on ports
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill process by PID
taskkill /PID <PID_NUMBER> /F

# Restart MongoDB (if installed as service)
net stop MongoDB
net start MongoDB
```

Happy coding! 🎯
