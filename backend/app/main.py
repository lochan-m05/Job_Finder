from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Job Discovery Platform API...")
    
    yield
    
    # Shutdown
    print("Shutting down Job Discovery Platform API...")

app = FastAPI(
    title="Job Discovery Platform API",
    description="AI-powered job discovery with real-time scraping and NLP analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Job Discovery Platform API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "not_connected",
        "redis": "not_connected",
        "message": "Basic API is running. Install MongoDB and Redis for full functionality."
    }

@app.post("/api/scrape-jobs")
async def trigger_job_scraping(
    background_tasks: BackgroundTasks,
    hashtags: list[str],
    time_filter: str = "24h",
    sources: list[str] = ["linkedin", "naukri", "indeed"]
):
    """
    Trigger job scraping (placeholder endpoint)
    """
    return {
        "message": "Scraping simulation - install MongoDB and Redis for actual scraping",
        "hashtags": hashtags,
        "time_filter": time_filter,
        "sources": sources,
        "note": "This is a demo endpoint. Full functionality requires database setup."
    }

@app.get("/api/jobs")
async def get_jobs(
    q: str = "",
    limit: int = 20,
    offset: int = 0
):
    """
    Get jobs (placeholder endpoint)
    """
    # Mock job data for demonstration
    mock_jobs = [
        {
            "id": "1",
            "title": "Python Developer",
            "company": "Tech Corp",
            "location": "Mumbai, India",
            "description": "We are looking for a Python developer with FastAPI experience...",
            "skills": ["Python", "FastAPI", "MongoDB"],
            "posted_at": "2024-01-08T10:00:00Z",
            "source": "linkedin"
        },
        {
            "id": "2", 
            "title": "React Frontend Developer",
            "company": "StartupXYZ",
            "location": "Bangalore, India",
            "description": "Join our team as a React developer...",
            "skills": ["React", "TypeScript", "JavaScript"],
            "posted_at": "2024-01-08T09:00:00Z",
            "source": "naukri"
        }
    ]
    
    return {
        "jobs": mock_jobs[:limit],
        "total": len(mock_jobs),
        "limit": limit,
        "offset": offset,
        "note": "These are mock jobs. Connect database for real job data."
    }

@app.get("/api/analytics/dashboard")
async def get_dashboard_data(time_range: str = "7d"):
    """
    Get dashboard analytics data (placeholder)
    """
    mock_analytics = {
        "stats": {
            "totalJobs": 156,
            "newJobs": 23,
            "totalContacts": 89,
            "savedJobs": 12,
            "jobsChange": 15,
            "newJobsChange": 8,
            "contactsChange": 12,
            "savedJobsChange": 3
        },
        "jobTrends": [
            {"date": "2024-01-01", "jobs": 10},
            {"date": "2024-01-02", "jobs": 15},
            {"date": "2024-01-03", "jobs": 12},
            {"date": "2024-01-04", "jobs": 18},
            {"date": "2024-01-05", "jobs": 22},
            {"date": "2024-01-06", "jobs": 25},
            {"date": "2024-01-07", "jobs": 28}
        ],
        "skillTrends": [
            {"skill": "Python", "count": 45},
            {"skill": "JavaScript", "count": 38},
            {"skill": "React", "count": 32},
            {"skill": "Node.js", "count": 28},
            {"skill": "FastAPI", "count": 25}
        ],
        "locationTrends": [
            {"location": "Mumbai", "count": 35},
            {"location": "Bangalore", "count": 42},
            {"location": "Delhi", "count": 28},
            {"location": "Pune", "count": 22},
            {"location": "Hyderabad", "count": 18}
        ]
    }
    
    return mock_analytics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )