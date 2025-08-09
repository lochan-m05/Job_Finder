from beanie import Document, Indexed
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class JobSource(str, Enum):
    LINKEDIN = "linkedin"
    NAUKRI = "naukri"
    INDEED = "indeed"
    FRESHERS_LIVE = "freshers_live"
    TWITTER = "twitter"
    OTHER = "other"

class ExperienceLevel(str, Enum):
    FRESHER = "fresher"
    ENTRY_LEVEL = "entry_level"
    MID_LEVEL = "mid_level"
    SENIOR_LEVEL = "senior_level"
    EXECUTIVE = "executive"

class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"

class LocationModel(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    remote: bool = False
    hybrid: bool = False

class SalaryModel(BaseModel):
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: str = "INR"
    per: str = "year"  # year, month, hour

class SkillsModel(BaseModel):
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    extracted_skills: List[str] = []
    skill_match_score: Optional[float] = None

class JobModel(Document):
    # Basic job information
    title: Indexed(str)
    company: Indexed(str)
    description: str
    job_url: str
    
    # Source and scraping info
    source: JobSource
    hashtags: List[str] = []
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    posted_at: Optional[datetime] = None
    
    # Job details
    location: LocationModel
    job_type: JobType
    experience_level: ExperienceLevel
    salary: Optional[SalaryModel] = None
    
    # Skills and requirements
    skills: SkillsModel
    requirements: List[str] = []
    benefits: List[str] = []
    
    # Contact information (embedded or referenced)
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    recruiter_phone: Optional[str] = None
    recruiter_linkedin: Optional[str] = None
    company_email: Optional[str] = None
    
    # NLP Analysis
    job_category: Optional[str] = None
    sentiment_score: Optional[float] = None
    urgency_score: Optional[float] = None
    quality_score: Optional[float] = None
    
    # Metadata
    is_active: bool = True
    views: int = 0
    applications: int = 0
    
    class Settings:
        name = "jobs"
        indexes = [
            "title",
            "company",
            "source",
            "hashtags",
            "scraped_at",
            "posted_at",
            "location.city",
            "job_type",
            "experience_level",
            "is_active"
        ]

class JobSearchRequest(BaseModel):
    hashtags: List[str]
    sources: List[JobSource] = [JobSource.LINKEDIN, JobSource.NAUKRI, JobSource.INDEED]
    time_filter: str = "24h"  # 1h, 24h, 7d, 30d
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    skills: List[str] = []
    
class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: LocationModel
    salary: Optional[SalaryModel]
    description: str
    job_url: str
    source: JobSource
    posted_at: Optional[datetime]
    scraped_at: datetime
    skills: SkillsModel
    recruiter_contact: Optional[dict] = None
    quality_score: Optional[float] = None
