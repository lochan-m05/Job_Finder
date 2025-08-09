import os
import time
import re
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
from .base_scraper import BaseScraper
from app.models.job import JobSource, JobType, ExperienceLevel

class LinkedInScraper(BaseScraper):
    """LinkedIn job scraper with login capability"""
    
    def __init__(self, use_proxy: bool = False, headless: bool = True):
        super().__init__(use_proxy, headless)
        self.is_logged_in = False
        self.base_url = "https://www.linkedin.com"
        
    def login(self) -> bool:
        """Login to LinkedIn"""
        try:
            email = os.getenv("LINKEDIN_EMAIL")
            password = os.getenv("LINKEDIN_PASSWORD")
            
            if not email or not password:
                print("LinkedIn credentials not found in environment variables")
                return False
            
            self.driver.get(f"{self.base_url}/login")
            self.random_delay(2, 4)
            
            # Enter email
            email_field = self.safe_find_element(By.ID, "username")
            if email_field:
                email_field.clear()
                email_field.send_keys(email)
            
            # Enter password
            password_field = self.safe_find_element(By.ID, "password")
            if password_field:
                password_field.clear()
                password_field.send_keys(password)
            
            # Click login button
            login_button = self.safe_find_element(By.XPATH, "//button[@type='submit']")
            if login_button:
                login_button.click()
                self.random_delay(3, 5)
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "in/" in self.driver.current_url:
                self.is_logged_in = True
                print("Successfully logged in to LinkedIn")
                return True
            else:
                print("LinkedIn login failed")
                return False
                
        except Exception as e:
            print(f"Error during LinkedIn login: {e}")
            return False
    
    def search_jobs(self, hashtags: List[str], time_filter: str) -> List[Dict[str, Any]]:
        """Search for jobs on LinkedIn"""
        jobs = []
        
        try:
            # Convert hashtags to search query
            search_query = " ".join([tag.replace("#", "") for tag in hashtags])
            
            # Navigate to jobs page
            jobs_url = f"{self.base_url}/jobs/search/?keywords={search_query}"
            
            # Add time filter
            time_filter_map = {
                "1h": "r86400",     # Past 24 hours (LinkedIn doesn't have 1h)
                "24h": "r86400",    # Past 24 hours
                "7d": "r604800",    # Past week
                "30d": "r2592000"   # Past month
            }
            
            if time_filter in time_filter_map:
                jobs_url += f"&f_TPR={time_filter_map[time_filter]}"
            
            self.driver.get(jobs_url)
            self.random_delay(3, 5)
            
            # Scroll to load more jobs
            self._scroll_to_load_jobs()
            
            # Extract job listings
            job_cards = self.safe_find_elements(By.CSS_SELECTOR, ".job-search-card")
            
            for card in job_cards[:50]:  # Limit to first 50 jobs
                try:
                    job_data = self._extract_job_card_data(card)
                    if job_data:
                        # Get detailed job information
                        detailed_job = self.extract_job_details(job_data["job_url"])
                        if detailed_job:
                            job_data.update(detailed_job)
                        
                        jobs.append(job_data)
                        self.random_delay(1, 2)
                        
                except Exception as e:
                    print(f"Error extracting job card: {e}")
                    continue
            
        except Exception as e:
            print(f"Error searching LinkedIn jobs: {e}")
        
        return jobs
    
    def _scroll_to_load_jobs(self):
        """Scroll down to load more job listings"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for _ in range(3):  # Scroll 3 times
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.random_delay(2, 3)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def _extract_job_card_data(self, card) -> Dict[str, Any]:
        """Extract data from job card element"""
        try:
            # Job title and URL
            title_element = card.find_element(By.CSS_SELECTOR, ".job-search-card__title a")
            title = self.extract_text_safe(title_element)
            job_url = self.extract_attribute_safe(title_element, "href")
            
            # Company
            company_element = card.find_element(By.CSS_SELECTOR, ".job-search-card__subtitle a")
            company = self.extract_text_safe(company_element)
            
            # Location
            location_element = card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
            location = self.extract_text_safe(location_element)
            
            # Posted time
            time_element = card.find_element(By.CSS_SELECTOR, ".job-search-card__listdate")
            posted_time = self.extract_text_safe(time_element)
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "job_url": job_url,
                "posted_time": posted_time,
                "source": JobSource.LINKEDIN
            }
            
        except NoSuchElementException:
            return None
    
    def extract_job_details(self, job_url: str) -> Dict[str, Any]:
        """Extract detailed job information from job page"""
        try:
            self.driver.get(job_url)
            self.random_delay(2, 4)
            
            job_details = {}
            
            # Job description
            description_element = self.safe_find_element(
                By.CSS_SELECTOR, 
                ".jobs-box__html-content, .jobs-description-content__text"
            )
            if description_element:
                job_details["description"] = self.extract_text_safe(description_element)
            
            # Company details
            company_link = self.safe_find_element(By.CSS_SELECTOR, ".jobs-details-top-card__company-url")
            if company_link:
                job_details["company_url"] = self.extract_attribute_safe(company_link, "href")
            
            # Job criteria (experience level, job type, etc.)
            criteria_items = self.safe_find_elements(By.CSS_SELECTOR, ".jobs-details-top-card__job-criteria-item")
            
            for item in criteria_items:
                label_element = item.find_element(By.CSS_SELECTOR, ".jobs-details-top-card__job-criteria-text")
                value_element = item.find_element(By.CSS_SELECTOR, ".jobs-details-top-card__job-criteria-text:last-child")
                
                label = self.extract_text_safe(label_element).lower()
                value = self.extract_text_safe(value_element)
                
                if "experience level" in label:
                    job_details["experience_level"] = self._map_experience_level(value)
                elif "employment type" in label:
                    job_details["job_type"] = self._map_job_type(value)
            
            # Extract skills from description
            if "description" in job_details:
                job_details["skills"] = self._extract_skills_from_description(job_details["description"])
            
            return job_details
            
        except Exception as e:
            print(f"Error extracting job details from {job_url}: {e}")
            return {}
    
    def extract_contact_info(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contact information from job posting"""
        contact_info = {
            "recruiter_name": None,
            "recruiter_email": None,
            "recruiter_phone": None,
            "recruiter_linkedin": None,
            "company_email": None
        }
        
        try:
            # Try to find recruiter information in the job posting
            recruiter_element = self.safe_find_element(
                By.CSS_SELECTOR, 
                ".jobs-poster__name, .jobs-details-top-card__company-url"
            )
            
            if recruiter_element:
                contact_info["recruiter_name"] = self.extract_text_safe(recruiter_element)
            
            # Extract emails and phones from description
            description = job_data.get("description", "")
            if description:
                emails = self.extract_emails_from_text(description)
                phones = self.extract_phones_from_text(description)
                
                if emails:
                    contact_info["recruiter_email"] = emails[0]
                if phones:
                    contact_info["recruiter_phone"] = phones[0]
            
            # Try to visit company page for more contact info
            company_url = job_data.get("company_url")
            if company_url:
                additional_contacts = self._extract_company_contacts(company_url)
                contact_info.update(additional_contacts)
            
        except Exception as e:
            print(f"Error extracting contact info: {e}")
        
        return contact_info
    
    def _extract_company_contacts(self, company_url: str) -> Dict[str, Any]:
        """Extract contact information from company page"""
        contacts = {}
        
        try:
            self.driver.get(company_url)
            self.random_delay(2, 3)
            
            # Look for contact information in company about section
            about_text = ""
            about_elements = self.safe_find_elements(By.CSS_SELECTOR, ".org-about-us-organization-description__text")
            
            for element in about_elements:
                about_text += self.extract_text_safe(element) + " "
            
            # Extract emails and phones from about text
            if about_text:
                emails = self.extract_emails_from_text(about_text)
                phones = self.extract_phones_from_text(about_text)
                
                if emails:
                    contacts["company_email"] = emails[0]
                if phones and "recruiter_phone" not in contacts:
                    contacts["recruiter_phone"] = phones[0]
            
        except Exception as e:
            print(f"Error extracting company contacts: {e}")
        
        return contacts
    
    def _map_experience_level(self, value: str) -> str:
        """Map LinkedIn experience level to our enum"""
        value_lower = value.lower()
        
        if "entry" in value_lower or "fresher" in value_lower:
            return ExperienceLevel.FRESHER
        elif "associate" in value_lower or "junior" in value_lower:
            return ExperienceLevel.ENTRY_LEVEL
        elif "mid" in value_lower or "senior" in value_lower:
            return ExperienceLevel.MID_LEVEL
        elif "executive" in value_lower or "director" in value_lower:
            return ExperienceLevel.EXECUTIVE
        else:
            return ExperienceLevel.ENTRY_LEVEL
    
    def _map_job_type(self, value: str) -> str:
        """Map LinkedIn job type to our enum"""
        value_lower = value.lower()
        
        if "full-time" in value_lower:
            return JobType.FULL_TIME
        elif "part-time" in value_lower:
            return JobType.PART_TIME
        elif "contract" in value_lower:
            return JobType.CONTRACT
        elif "internship" in value_lower:
            return JobType.INTERNSHIP
        else:
            return JobType.FULL_TIME
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills from job description using keyword matching"""
        # Common technical skills
        tech_skills = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js",
            "sql", "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
            "git", "github", "gitlab", "agile", "scrum", "rest api",
            "html", "css", "bootstrap", "tailwind", "scss", "sass",
            "machine learning", "ai", "data science", "pandas", "numpy",
            "tensorflow", "pytorch", "scikit-learn", "fastapi", "django",
            "flask", "spring boot", "express", "laravel", "php"
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in tech_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills
