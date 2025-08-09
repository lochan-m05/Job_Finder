from celery import current_task
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.services.celery_app import celery_app
from app.nlp.job_analyzer import JobAnalyzer
from app.nlp.contact_extractor import ContactExtractor
from app.models.job import JobModel
from app.models.contact import ContactModel

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.analyze_job_description")
def analyze_job_description_task(self, job_id: str, description: str):
    """
    Analyze job description using NLP and update job record
    """
    task_id = self.request.id
    
    try:
        logger.info(f"Starting NLP analysis for job {job_id}")
        
        # Initialize NLP analyzer
        job_analyzer = JobAnalyzer()
        
        # Analyze job description
        analysis = job_analyzer.analyze_job_description(description)
        
        # Update job record with analysis results
        # This would typically update the database
        # For now, we'll return the analysis
        
        result = {
            "job_id": job_id,
            "analysis": analysis,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed NLP analysis for job {job_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in NLP analysis task: {e}")
        raise e

@celery_app.task(bind=True, name="app.tasks.extract_contact_information")
def extract_contact_information_task(self, job_id: str, text: str, source_url: str = None):
    """
    Extract contact information from job posting text
    """
    task_id = self.request.id
    
    try:
        logger.info(f"Starting contact extraction for job {job_id}")
        
        # Initialize contact extractor
        contact_extractor = ContactExtractor()
        
        # Extract contacts
        contacts = contact_extractor.extract_all_contacts(text, source_url)
        
        # Process and validate contacts
        processed_contacts = []
        
        # Process emails
        for email_data in contacts.get('emails', []):
            if email_data.get('overall_score', 0) > 0.5:  # Only high-confidence emails
                processed_contacts.append({
                    'type': 'email',
                    'value': email_data['email'],
                    'confidence': email_data['overall_score'],
                    'is_business': email_data.get('is_business', False)
                })
        
        # Process phones
        for phone_data in contacts.get('phones', []):
            if phone_data.get('overall_score', 0) > 0.5:  # Only high-confidence phones
                processed_contacts.append({
                    'type': 'phone',
                    'value': phone_data['number'],
                    'confidence': phone_data['overall_score'],
                    'is_whatsapp': phone_data.get('is_whatsapp_likely', False)
                })
        
        # Process social profiles
        for platform, profile_url in contacts.get('social_profiles', {}).items():
            processed_contacts.append({
                'type': 'social',
                'platform': platform,
                'value': profile_url,
                'confidence': 0.8
            })
        
        result = {
            "job_id": job_id,
            "contacts": processed_contacts,
            "raw_contacts": contacts,
            "extracted_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed contact extraction for job {job_id}, found {len(processed_contacts)} contacts")
        return result
        
    except Exception as e:
        logger.error(f"Error in contact extraction task: {e}")
        raise e

@celery_app.task(bind=True, name="app.tasks.calculate_job_match_scores")
def calculate_job_match_scores_task(self, user_profile: Dict[str, Any], job_ids: List[str]):
    """
    Calculate job match scores for a user profile against multiple jobs
    """
    task_id = self.request.id
    
    try:
        logger.info(f"Calculating match scores for {len(job_ids)} jobs")
        
        job_analyzer = JobAnalyzer()
        match_scores = []
        
        # Update progress
        total_jobs = len(job_ids)
        
        for i, job_id in enumerate(job_ids):
            try:
                # In a real implementation, you'd fetch the job from database
                # For now, we'll use mock data
                job_description = f"Mock job description for {job_id}"
                
                # Calculate match score
                match_score = job_analyzer.calculate_job_match_score(job_description, user_profile)
                
                match_scores.append({
                    'job_id': job_id,
                    'match_score': match_score,
                    'calculated_at': datetime.utcnow().isoformat()
                })
                
                # Update progress every 10 jobs
                if (i + 1) % 10 == 0:
                    current_task.update_state(
                        state='PROGRESS',
                        meta={
                            'current': i + 1,
                            'total': total_jobs,
                            'status': f'Processed {i + 1}/{total_jobs} jobs'
                        }
                    )
                
            except Exception as e:
                logger.error(f"Error calculating match score for job {job_id}: {e}")
                continue
        
        result = {
            "user_profile": user_profile,
            "match_scores": match_scores,
            "total_processed": len(match_scores),
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed match score calculation for {len(match_scores)} jobs")
        return result
        
    except Exception as e:
        logger.error(f"Error in match score calculation task: {e}")
        raise e

@celery_app.task(name="app.tasks.batch_update_job_scores")
def batch_update_job_scores_task():
    """
    Periodic task to update job quality and urgency scores
    """
    try:
        logger.info("Starting batch job score update")
        
        job_analyzer = JobAnalyzer()
        
        # In real implementation, fetch jobs from database
        # This is a mock implementation
        updated_jobs = []
        
        # Mock: Update 100 recent jobs
        for i in range(100):
            job_id = f"job_{i}"
            
            # Mock job description
            description = "Sample job description"
            
            # Analyze job
            analysis = job_analyzer.analyze_job_description(description)
            
            # Update job scores in database
            # This would be actual database update
            updated_jobs.append({
                'job_id': job_id,
                'quality_score': analysis.get('quality_score'),
                'urgency_score': analysis.get('urgency_score'),
                'sentiment_score': analysis.get('sentiment_score')
            })
        
        result = {
            "updated_jobs": len(updated_jobs),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed batch job score update for {len(updated_jobs)} jobs")
        return result
        
    except Exception as e:
        logger.error(f"Error in batch job score update: {e}")
        raise e

@celery_app.task(bind=True, name="app.tasks.analyze_resume_job_match")
def analyze_resume_job_match_task(self, resume_text: str, job_description: str):
    """
    Analyze match between resume and job description
    """
    task_id = self.request.id
    
    try:
        logger.info("Starting resume-job match analysis")
        
        job_analyzer = JobAnalyzer()
        
        # Analyze job description
        job_analysis = job_analyzer.analyze_job_description(job_description)
        
        # Extract skills from resume (simplified)
        resume_skills = job_analyzer.extract_skills(resume_text)
        
        # Create user profile from resume
        user_profile = {
            'skills': resume_skills,
            'experience_level': 'mid_level',  # Could be extracted from resume
        }
        
        # Calculate match score
        match_score = job_analyzer.calculate_job_match_score(job_description, user_profile)
        
        # Identify matching and missing skills
        job_skills = set(skill.lower() for skill in job_analysis.get('skills', []))
        user_skills = set(skill.lower() for skill in resume_skills)
        
        matching_skills = list(job_skills.intersection(user_skills))
        missing_skills = list(job_skills - user_skills)
        
        result = {
            "match_score": match_score,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "job_skills": list(job_skills),
            "user_skills": list(user_skills),
            "job_analysis": job_analysis,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Completed resume-job match analysis, score: {match_score}")
        return result
        
    except Exception as e:
        logger.error(f"Error in resume-job match analysis: {e}")
        raise e

@celery_app.task(bind=True, name="app.tasks.generate_job_insights")
def generate_job_insights_task(self, job_ids: List[str]):
    """
    Generate insights and trends from job data
    """
    task_id = self.request.id
    
    try:
        logger.info(f"Generating insights for {len(job_ids)} jobs")
        
        job_analyzer = JobAnalyzer()
        
        # Mock data - in real implementation, fetch from database
        insights = {
            "skill_trends": {},
            "salary_trends": {},
            "company_trends": {},
            "location_trends": {},
            "urgency_trends": {}
        }
        
        # Analyze each job (mock implementation)
        for job_id in job_ids:
            # In real implementation, fetch job from database
            job_description = f"Mock description for {job_id}"
            
            analysis = job_analyzer.analyze_job_description(job_description)
            
            # Update skill trends
            for skill in analysis.get('skills', []):
                skill_lower = skill.lower()
                insights["skill_trends"][skill_lower] = insights["skill_trends"].get(skill_lower, 0) + 1
        
        # Calculate percentages and top trends
        total_jobs = len(job_ids)
        
        # Top skills
        top_skills = sorted(
            insights["skill_trends"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        insights["top_skills"] = [
            {"skill": skill, "count": count, "percentage": round((count / total_jobs) * 100, 1)}
            for skill, count in top_skills
        ]
        
        # Mock other insights
        insights["average_quality_score"] = 0.75
        insights["average_urgency_score"] = 0.45
        insights["remote_job_percentage"] = 35.2
        insights["salary_mentioned_percentage"] = 68.5
        
        result = {
            "insights": insights,
            "total_jobs_analyzed": total_jobs,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info("Completed job insights generation")
        return result
        
    except Exception as e:
        logger.error(f"Error generating job insights: {e}")
        raise e
