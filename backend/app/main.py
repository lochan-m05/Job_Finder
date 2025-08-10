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
    Generate recent, realistic analytics so the UI shows current data.
    """
    from datetime import datetime, timedelta
    import random

    now = datetime.utcnow()
    days = {
        "1d": 1,
        "7d": 7,
        "30d": 30,
        "90d": 90,
    }.get(time_range, 7)

    # Generate job trend data for the last N days
    job_trends = []
    base = random.randint(8, 20)
    for i in range(days):
        day = now - timedelta(days=(days - 1 - i))
        jobs = base + random.randint(-3, 8)
        jobs = max(0, jobs)
        job_trends.append({
            "date": day.strftime("%Y-%m-%d"),
            "jobs": jobs,
        })

    # Top skills mock
    skills = [
        "Python", "JavaScript", "React", "Node.js", "TypeScript",
        "FastAPI", "MongoDB", "Docker", "Kubernetes", "AWS"
    ]
    skill_trends = [{"skill": s, "count": random.randint(15, 60)} for s in skills]
    skill_trends.sort(key=lambda x: x["count"], reverse=True)
    skill_trends = skill_trends[:10]

    # Top locations mock
    locations = ["Mumbai", "Bangalore", "Delhi", "Pune", "Hyderabad"]
    location_trends = [{"location": loc, "count": random.randint(10, 50)} for loc in locations]

    stats = {
        "totalJobs": sum(d["jobs"] for d in job_trends),
        "newJobs": job_trends[-1]["jobs"] if job_trends else 0,
        "totalContacts": random.randint(60, 200),
        "savedJobs": random.randint(5, 25),
        "jobsChange": random.randint(-10, 20),
        "newJobsChange": random.randint(-5, 15),
        "contactsChange": random.randint(-5, 15),
        "savedJobsChange": random.randint(-3, 8),
    }

    return {
        "stats": stats,
        "jobTrends": job_trends,
        "skillTrends": skill_trends,
        "locationTrends": location_trends,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )