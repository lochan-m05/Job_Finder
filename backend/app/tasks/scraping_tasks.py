from celery import current_task
from typing import List, Dict, Any
import asyncio
from datetime import datetime
import logging

from app.services.celery_app import celery_app
from app.scrapers.scraper_manager import ScraperManager
from app.nlp.job_analyzer import JobAnalyzer
from app.nlp.contact_extractor import ContactExtractor
from app.models.job import JobModel, JobSource, ExperienceLevel, JobType, LocationModel, SalaryModel, SkillsModel
from app.models.contact import ContactModel, ContactType, ContactSource, EmailModel, PhoneModel, SocialProfileModel
from app.models.scraping_task import ScrapingTaskModel, TaskStatus, TaskType
from app.database import get_database

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.scrape_jobs")
def scrape_jobs_task(self, hashtags: List[str], time_filter: str = "24h", sources: List[str] = None):
    """
    Asynchronous task to scrape jobs from multiple sources
    """
    task_id = self.request.id
    
    try:
        # Update task status
        update_task_status(task_id, TaskStatus.RUNNING, {"current_operation": "Starting scraping process"})
        
        # Initialize components
        scraper_manager = ScraperManager(use_proxy=True, headless=True)
        job_analyzer = JobAnalyzer()
        contact_extractor = ContactExtractor()
        
        if not sources:
            sources = [JobSource.LINKEDIN, JobSource.NAUKRI, JobSource.INDEED, JobSource.TWITTER]
        
        # Run scraping
        logger.info(f"Starting job scraping for hashtags: {hashtags}, sources: {sources}")
        
        # Use asyncio to run the async scraping function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            raw_jobs = loop.run_until_complete(
                scraper_manager.scrape_jobs(hashtags, sources, time_filter)
            )
        finally:
            loop.close()
        
        logger.info(f"Scraped {len(raw_jobs)} raw jobs")
        
        # Update progress
        update_task_status(
            task_id, 
            TaskStatus.RUNNING, 
            {
                "current_operation": "Processing scraped jobs",
                "items_processed": 0,
                "total_items": len(raw_jobs)
            }
        )
        
        # Process and save jobs
        saved_job_ids = []
        processed_count = 0
        
        for job_data in raw_jobs:
            try:
                # Process job with NLP
                job_model = process_job_data(job_data, job_analyzer, contact_extractor)
                
                if job_model:
                    # Save to database
                    job_id = save_job_to_database(job_model)
                    if job_id:
                        saved_job_ids.append(job_id)
                
                processed_count += 1
                
                # Update progress
                if processed_count % 5 == 0:  # Update every 5 jobs
                    update_task_status(
                        task_id,
                        TaskStatus.RUNNING,
                        {
                            "current_operation": "Processing jobs",
                            "items_processed": processed_count,
                            "items_succeeded": len(saved_job_ids),
                            "total_items": len(raw_jobs)
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error processing job: {e}")
                continue
        
        # Complete task
        result = {
            "total_scraped": len(raw_jobs),
            "total_saved": len(saved_job_ids),
            "job_ids": saved_job_ids,
            "hashtags": hashtags,
            "sources": sources,
            "time_filter": time_filter,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            {
                "items_processed": processed_count,
                "items_succeeded": len(saved_job_ids),
                "result_summary": result
            }
        )
        
        logger.info(f"Job scraping completed. Saved {len(saved_job_ids)} jobs")
        return result
        
    except Exception as e:
        logger.error(f"Error in scraping task: {e}")
        
        # Mark task as failed
        update_task_status(
            task_id,
            TaskStatus.FAILED,
            {
                "error_message": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise e

def process_job_data(job_data: Dict[str, Any], job_analyzer: JobAnalyzer, contact_extractor: ContactExtractor) -> JobModel:
    """Process raw job data into structured JobModel"""
    
    try:
        # Analyze job description with NLP
        description = job_data.get("description", "")
        nlp_analysis = job_analyzer.analyze_job_description(description) if description else {}
        
        # Extract contact information
        contact_info = contact_extractor.extract_all_contacts(description)
        
        # Create location model
        location_str = job_data.get("location", "")
        location = parse_location(location_str)
        
        # Create salary model
        salary_str = job_data.get("salary", "")
        salary = parse_salary(salary_str)
        
        # Create skills model
        skills = SkillsModel(
            required_skills=job_data.get("skills", []),
            extracted_skills=nlp_analysis.get("skills", []),
            skill_match_score=None
        )
        
        # Extract recruiter contact information
        emails = contact_info.get("emails", [])
        phones = contact_info.get("phones", [])
        social_profiles = contact_info.get("social_profiles", {})
        names = contact_info.get("names", [])
        
        recruiter_email = emails[0]["email"] if emails else None
        recruiter_phone = phones[0]["number"] if phones else None
        recruiter_linkedin = social_profiles.get("linkedin")
        recruiter_name = names[0]["name"] if names else None
        
        # Create job model
        job_model = JobModel(
            title=job_data.get("title", ""),
            company=job_data.get("company", ""),
            description=description,
            job_url=job_data.get("job_url", ""),
            source=JobSource(job_data.get("source", JobSource.OTHER)),
            hashtags=job_data.get("hashtags", []),
            posted_at=parse_datetime(job_data.get("posted_time")),
            location=location,
            job_type=parse_job_type(job_data.get("job_type")),
            experience_level=parse_experience_level(job_data.get("experience_level") or nlp_analysis.get("experience_level")),
            salary=salary,
            skills=skills,
            requirements=nlp_analysis.get("requirements", []),
            benefits=nlp_analysis.get("benefits", []),
            recruiter_name=recruiter_name,
            recruiter_email=recruiter_email,
            recruiter_phone=recruiter_phone,
            recruiter_linkedin=recruiter_linkedin,
            job_category=nlp_analysis.get("job_category"),
            sentiment_score=nlp_analysis.get("sentiment_score"),
            urgency_score=nlp_analysis.get("urgency_score"),
            quality_score=nlp_analysis.get("quality_score")
        )
        
        return job_model
        
    except Exception as e:
        logger.error(f"Error processing job data: {e}")
        return None

def parse_location(location_str: str) -> LocationModel:
    """Parse location string into LocationModel"""
    location = LocationModel()
    
    if not location_str:
        return location
    
    location_lower = location_str.lower()
    
    # Check for remote indicators
    if any(term in location_lower for term in ["remote", "work from home", "wfh"]):
        location.remote = True
    
    # Check for hybrid indicators
    if "hybrid" in location_lower:
        location.hybrid = True
    
    # Extract city and state (basic parsing)
    parts = location_str.split(",")
    if parts:
        location.city = parts[0].strip()
        if len(parts) > 1:
            location.state = parts[1].strip()
        location.country = "India"  # Default for Indian job boards
    
    return location

def parse_salary(salary_str: str) -> SalaryModel:
    """Parse salary string into SalaryModel"""
    if not salary_str:
        return None
    
    salary = SalaryModel()
    
    # Extract salary numbers (various formats)
    import re
    
    # Pattern for lakhs
    lakh_pattern = r'(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*(?:lakh|lpa|lakhs?)'
    match = re.search(lakh_pattern, salary_str.lower())
    
    if match:
        min_sal = float(match.group(1)) * 100000
        max_sal = float(match.group(2) or match.group(1)) * 100000
        
        salary.min_salary = min_sal
        salary.max_salary = max_sal
        salary.currency = "INR"
        salary.per = "year"
    
    return salary

def parse_job_type(job_type_str: str) -> JobType:
    """Parse job type string"""
    if not job_type_str:
        return JobType.FULL_TIME
    
    job_type_lower = job_type_str.lower()
    
    if "part-time" in job_type_lower or "part time" in job_type_lower:
        return JobType.PART_TIME
    elif "contract" in job_type_lower:
        return JobType.CONTRACT
    elif "internship" in job_type_lower:
        return JobType.INTERNSHIP
    elif "freelance" in job_type_lower:
        return JobType.FREELANCE
    else:
        return JobType.FULL_TIME

def parse_experience_level(exp_str: str) -> ExperienceLevel:
    """Parse experience level string"""
    if not exp_str:
        return ExperienceLevel.ENTRY_LEVEL
    
    exp_lower = exp_str.lower()
    
    if any(term in exp_lower for term in ["fresher", "0 year", "entry", "no experience"]):
        return ExperienceLevel.FRESHER
    elif any(term in exp_lower for term in ["1-3", "2-4", "junior", "associate"]):
        return ExperienceLevel.ENTRY_LEVEL
    elif any(term in exp_lower for term in ["3-5", "4-6", "mid", "intermediate"]):
        return ExperienceLevel.MID_LEVEL
    elif any(term in exp_lower for term in ["5+", "6+", "senior", "lead"]):
        return ExperienceLevel.SENIOR_LEVEL
    elif any(term in exp_lower for term in ["manager", "director", "head", "executive"]):
        return ExperienceLevel.EXECUTIVE
    else:
        return ExperienceLevel.ENTRY_LEVEL

def parse_datetime(date_str: str) -> datetime:
    """Parse various date string formats"""
    if not date_str:
        return None
    
    try:
        # Try different date formats
        from dateutil import parser
        return parser.parse(date_str)
    except:
        return None

def save_job_to_database(job_model: JobModel) -> str:
    """Save job model to database"""
    try:
        # This would be implemented with actual database connection
        # For now, return a mock ID
        return f"job_{datetime.utcnow().timestamp()}"
    except Exception as e:
        logger.error(f"Error saving job to database: {e}")
        return None

def update_task_status(task_id: str, status: TaskStatus, update_data: Dict[str, Any]):
    """Update task status in database"""
    try:
        # This would update the ScrapingTaskModel in database
        logger.info(f"Task {task_id} status: {status.value}, data: {update_data}")
        
        # Update the current task metadata
        if hasattr(current_task, 'update_state'):
            current_task.update_state(
                state=status.value.upper(),
                meta=update_data
            )
    except Exception as e:
        logger.error(f"Error updating task status: {e}")

@celery_app.task(name="app.tasks.scrape_single_source")
def scrape_single_source_task(source: str, hashtags: List[str], time_filter: str = "24h"):
    """Scrape jobs from a single source"""
    
    try:
        scraper_manager = ScraperManager(use_proxy=True, headless=True)
        job_analyzer = JobAnalyzer()
        contact_extractor = ContactExtractor()
        
        # Run scraping for single source
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            raw_jobs = loop.run_until_complete(
                scraper_manager.scrape_single_source(source, hashtags, time_filter)
            )
        finally:
            loop.close()
        
        # Process jobs
        processed_jobs = []
        for job_data in raw_jobs:
            job_model = process_job_data(job_data, job_analyzer, contact_extractor)
            if job_model:
                job_id = save_job_to_database(job_model)
                if job_id:
                    processed_jobs.append(job_id)
        
        return {
            "source": source,
            "total_scraped": len(raw_jobs),
            "total_saved": len(processed_jobs),
            "job_ids": processed_jobs
        }
        
    except Exception as e:
        logger.error(f"Error in single source scraping: {e}")
        raise e
