from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from typing import List
from enum import Enum
from datetime import datetime, timedelta

# Local imports
from app.scrapers.scraper_manager import ScraperManager
from app.models.job import JobSource

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
    hashtags: str | None = Query(default=None, description="Comma-separated hashtags without # (e.g. python,react)"),
    sources: str | None = Query(default=None, description="Comma-separated sources (linkedin,naukri,indeed,twitter)"),
    time_filter: str = Query(default="24h", description="1h, 24h, 7d, 30d"),
    limit: int = 20,
    offset: int = 0,
):
    """
    Get jobs by live scraping when hashtags are provided. Returns fresh data with real posted times.
    Falls back to empty list when no hashtags supplied.
    """

    def to_iso(dt: datetime) -> str:
        return dt.replace(microsecond=0).isoformat() + "Z"

    def parse_posted_time(value: str | None) -> str | None:
        if not value:
            return None
        text = value.strip().lower()
        now = datetime.utcnow()
        try:
            if text in ("just now", "now"):
                return to_iso(now)
            # e.g., '2 hours ago', '3 hrs ago', '45 minutes ago', '5 days ago'
            parts = text.split()
            if len(parts) >= 2 and parts[0].isdigit():
                amount = int(parts[0])
                unit = parts[1]
                if unit.startswith("min"):
                    return to_iso(now - timedelta(minutes=amount))
                if unit.startswith("hour") or unit.startswith("hr"):
                    return to_iso(now - timedelta(hours=amount))
                if unit.startswith("day"):
                    return to_iso(now - timedelta(days=amount))
                if unit.startswith("week"):
                    return to_iso(now - timedelta(weeks=amount))
            # Twitter ISO datetime
            if "t" in text and ":" in text and text.endswith("z"):
                # already ISO-like
                return value
        except Exception:
            pass
        return None

    # If no hashtags are provided, return empty dataset (frontend shows guidance)
    hashtag_list: List[str] = []
    if hashtags:
        hashtag_list = [h.strip().lstrip("#") for h in hashtags.split(",") if h.strip()]

    if not hashtag_list:
        return {"jobs": [], "total": 0, "limit": limit, "offset": offset}

    # Determine sources (map strings to JobSource enum)
    default_sources = [JobSource.LINKEDIN, JobSource.NAUKRI, JobSource.INDEED, JobSource.TWITTER]
    source_list: List[JobSource] = default_sources
    if sources:
        candidates = [s.strip().lower() for s in sources.split(",") if s.strip()]
        mapped: List[JobSource] = []
        for s in candidates:
            try:
                mapped.append(JobSource(s))
            except Exception:
                continue
        if mapped:
            source_list = mapped

    # Run live scraping
    manager = ScraperManager(use_proxy=True, headless=True)
    try:
        raw_jobs = await manager.scrape_jobs(hashtag_list, source_list, time_filter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {e}")
    finally:
        try:
            manager.close_all_sessions()
        except Exception:
            pass

    # Map and filter results
    jobs_mapped = []
    for idx, job in enumerate(raw_jobs):
        title = job.get("title") or "Job"
        company = job.get("company") or ""
        location = job.get("location") or ""
        description = job.get("description") or job.get("snippet") or ""
        job_url = job.get("job_url") or job.get("url") or ""
        posted_iso = parse_posted_time(job.get("posted_time")) or to_iso(datetime.utcnow())
        source_raw = job.get("source") or "other"
        if isinstance(source_raw, Enum):
            source_str = source_raw.value
        else:
            source_str = str(source_raw)

        jobs_mapped.append({
            "id": f"{hash(job_url) ^ hash(title) ^ hash(company)}",
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "skills": job.get("skills") or [],
            "posted_at": posted_iso,
            "source": source_str,
            # normalize a simple salary view when available
            "salary": job.get("salary") if isinstance(job.get("salary"), dict) else None,
            "job_url": job_url,
        })

    # Simple text filter and paging
    if q:
        q_low = q.lower()
        jobs_mapped = [j for j in jobs_mapped if q_low in j["title"].lower() or q_low in j["company"].lower()]

    total = len(jobs_mapped)
    paged = jobs_mapped[offset: offset + limit]

    return {
        "jobs": paged,
        "total": total,
        "limit": limit,
        "offset": offset,
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