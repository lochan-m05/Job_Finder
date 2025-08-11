from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
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

# In-memory state for last scrape to power dashboard/notifications without DB
RECENT_STATE: Dict[str, Any] = {
    "jobs": [],
    "hashtags": [],
    "sources": [],
    "time_filter": "24h",
    "updated_at": None,
}

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
            # contact fields if available
            "recruiter_name": job.get("recruiter_name"),
            "recruiter_email": job.get("recruiter_email"),
            "recruiter_phone": job.get("recruiter_phone"),
            "recruiter_linkedin": job.get("recruiter_linkedin"),
        })

    # Simple text filter and paging
    if q:
        q_low = q.lower()
        jobs_mapped = [j for j in jobs_mapped if q_low in j["title"].lower() or q_low in j["company"].lower()]

    total = len(jobs_mapped)
    paged = jobs_mapped[offset: offset + limit]

    # Update in-memory cache for dashboard/notifications
    try:
        RECENT_STATE.update({
            "jobs": jobs_mapped,
            "hashtags": hashtag_list,
            "sources": [s.value if isinstance(s, Enum) else str(s) for s in source_list],
            "time_filter": time_filter,
            "updated_at": to_iso(datetime.utcnow()),
        })
    except Exception:
        pass

    return {
        "jobs": paged,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

@app.get("/api/jobs/recent")
async def get_recent_jobs(limit: int = 10):
    jobs = RECENT_STATE.get("jobs", [])
    return {"jobs": jobs[: max(0, min(limit, len(jobs)))]}

@app.get("/api/analytics/dashboard")
async def get_dashboard_data(time_range: str = "7d"):
    """Compute analytics from the most recent live scrape (in-memory)."""
    from collections import Counter

    jobs = RECENT_STATE.get("jobs", [])
    if not jobs:
        return {
            "stats": {
                "totalJobs": 0,
                "newJobs": 0,
                "totalContacts": 0,
                "savedJobs": 0,
                "jobsChange": 0,
                "newJobsChange": 0,
                "contactsChange": 0,
                "savedJobsChange": 0,
            },
            "jobTrends": [],
            "skillTrends": [],
            "locationTrends": [],
        }

    # Trends by day (limit by time_range days)
    days_map = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
    days = days_map.get(time_range, 7)
    now = datetime.utcnow()

    def date_only(dt_iso: str) -> str:
        try:
            d = datetime.fromisoformat(dt_iso.replace("Z", "+00:00"))
            return d.date().isoformat()
        except Exception:
            return now.date().isoformat()

    counts_by_date: Dict[str, int] = {}
    for i in range(days):
        day = (now - timedelta(days=(days - 1 - i))).date().isoformat()
        counts_by_date[day] = 0

    for j in jobs:
        d = date_only(j.get("posted_at") or RECENT_STATE.get("updated_at") or now.isoformat())
        if d in counts_by_date:
            counts_by_date[d] += 1

    job_trends = [{"date": d, "jobs": counts_by_date[d]} for d in sorted(counts_by_date.keys())]

    # Skills
    skill_counter = Counter()
    for j in jobs:
        for s in j.get("skills", []) or []:
            skill_counter[s] += 1
    skill_trends = [{"skill": k, "count": v} for k, v in skill_counter.most_common(10)]

    # Locations
    loc_counter = Counter()
    for j in jobs:
        loc = (j.get("location") or "").strip() or "Unknown"
        loc_counter[loc] += 1
    locationTrends = [{"location": k, "count": v} for k, v in loc_counter.most_common(5)]

    # Contacts found
    total_contacts = 0
    for j in jobs:
        if j.get("recruiter_email") or j.get("recruiter_phone"):
            total_contacts += 1

    # New jobs today
    cutoff = now - timedelta(days=1)
    def is_recent(dt_iso: str) -> bool:
        try:
            d = datetime.fromisoformat((dt_iso or "").replace("Z", "+00:00"))
            return d >= cutoff
        except Exception:
            return False

    new_jobs = sum(1 for j in jobs if is_recent(j.get("posted_at")))

    stats = {
        "totalJobs": len(jobs),
        "newJobs": new_jobs,
        "totalContacts": total_contacts,
        "savedJobs": 0,
        # No previous baseline in-memory; return zeros for changes
        "jobsChange": 0,
        "newJobsChange": 0,
        "contactsChange": 0,
        "savedJobsChange": 0,
    }

    return {
        "stats": stats,
        "jobTrends": job_trends,
        "skillTrends": skill_trends,
        "locationTrends": locationTrends,
    }

@app.get("/api/notifications")
async def get_notifications():
    jobs = RECENT_STATE.get("jobs", [])
    hashtags = RECENT_STATE.get("hashtags", [])
    updated_at = RECENT_STATE.get("updated_at")

    if not jobs:
        return {"notifications": []}

    # Compose simple notifications from last scrape
    contact_count = sum(1 for j in jobs if j.get("recruiter_email") or j.get("recruiter_phone"))
    job_count = len(jobs)

    tags_text = " ".join(f"#{t}" for t in hashtags[:5])
    notifications = []
    notifications.append({
        "id": "n1",
        "title": "New Jobs Found",
        "message": f"{job_count} jobs found for {tags_text}",
        "time": updated_at or "just now",
        "type": "info",
    })
    if contact_count:
        notifications.append({
            "id": "n2",
            "title": "Contacts Extracted",
            "message": f"{contact_count} postings with contact details",
            "time": updated_at or "just now",
            "type": "success",
        })
    return {"notifications": notifications}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )