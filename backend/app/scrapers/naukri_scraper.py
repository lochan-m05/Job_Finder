from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import re
from .base_scraper import BaseScraper
from app.models.job import JobSource, JobType, ExperienceLevel

class NaukriScraper(BaseScraper):
    """Naukri.com job scraper"""
    
    def __init__(self, use_proxy: bool = False, headless: bool = True):
        super().__init__(use_proxy, headless)
        self.base_url = "https://www.naukri.com"
    
    def search_jobs(self, hashtags: List[str], time_filter: str) -> List[Dict[str, Any]]:
        """Search for jobs on Naukri"""
        jobs = []
        
        try:
            # Convert hashtags to search query
            search_query = " ".join([tag.replace("#", "") for tag in hashtags])
            
            # Navigate to jobs search page
            search_url = f"{self.base_url}/jobs-in-india"
            self.driver.get(search_url)
            self.random_delay(2, 4)
            
            # Enter search query
            search_box = self.safe_find_element(By.ID, "qsb-keyword-sugg")
            if search_box:
                search_box.clear()
                search_box.send_keys(search_query)
                search_box.send_keys(Keys.RETURN)
                self.random_delay(3, 5)
            
            # Apply time filter
            self._apply_time_filter(time_filter)
            
            # Extract job listings
            job_cards = self.safe_find_elements(By.CSS_SELECTOR, ".jobTuple")
            
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
                    print(f"Error extracting Naukri job card: {e}")
                    continue
            
        except Exception as e:
            print(f"Error searching Naukri jobs: {e}")
        
        return jobs
    
    def _apply_time_filter(self, time_filter: str):
        """Apply time filter to search results"""
        try:
            # Click on filter dropdown
            filter_button = self.safe_find_element(By.CSS_SELECTOR, ".filter-dropdown")
            if filter_button:
                filter_button.click()
                self.random_delay(1, 2)
            
            # Select appropriate time filter
            time_filter_map = {
                "1h": "1",      # Last 1 day (closest to 1h)
                "24h": "1",     # Last 1 day
                "7d": "7",      # Last 7 days
                "30d": "30"     # Last 30 days
            }
            
            if time_filter in time_filter_map:
                filter_option = self.safe_find_element(
                    By.XPATH, 
                    f"//span[contains(text(), '{time_filter_map[time_filter]} day')]"
                )
                if filter_option:
                    filter_option.click()
                    self.random_delay(2, 3)
        
        except Exception as e:
            print(f"Error applying time filter: {e}")
    
    def _extract_job_card_data(self, card) -> Dict[str, Any]:
        """Extract data from job card element"""
        try:
            # Job title and URL
            title_element = card.find_element(By.CSS_SELECTOR, ".jobTupleHeader .title a")
            title = self.extract_text_safe(title_element)
            job_url = self.extract_attribute_safe(title_element, "href")
            
            if not job_url.startswith("http"):
                job_url = self.base_url + job_url
            
            # Company
            company_element = card.find_element(By.CSS_SELECTOR, ".companyInfo .subTitle a")
            company = self.extract_text_safe(company_element)
            
            # Experience
            experience_element = card.find_element(By.CSS_SELECTOR, ".jobTupleFooter .experience")
            experience = self.extract_text_safe(experience_element)
            
            # Salary
            salary_element = card.find_element(By.CSS_SELECTOR, ".jobTupleFooter .salary")
            salary = self.extract_text_safe(salary_element)
            
            # Location
            location_element = card.find_element(By.CSS_SELECTOR, ".jobTupleFooter .location")
            location = self.extract_text_safe(location_element)
            
            # Posted time
            posted_element = card.find_element(By.CSS_SELECTOR, ".jobTupleFooter .postedDate")
            posted_time = self.extract_text_safe(posted_element)
            
            # Skills (if available)
            skills_elements = card.find_elements(By.CSS_SELECTOR, ".jobTupleFooter .skill")
            skills = [self.extract_text_safe(skill) for skill in skills_elements]
            
            return {
                "title": title,
                "company": company,
                "experience": experience,
                "salary": salary,
                "location": location,
                "job_url": job_url,
                "posted_time": posted_time,
                "skills": skills,
                "source": JobSource.NAUKRI
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
                ".jobDescriptionSection, .jdSection"
            )
            if description_element:
                job_details["description"] = self.extract_text_safe(description_element)
            
            # Company details
            company_element = self.safe_find_element(By.CSS_SELECTOR, ".companyName a")
            if company_element:
                job_details["company_url"] = self.extract_attribute_safe(company_element, "href")
            
            # Job details section
            details_section = self.safe_find_element(By.CSS_SELECTOR, ".jobDetails")
            if details_section:
                # Extract salary information
                salary_element = details_section.find_element(By.CSS_SELECTOR, ".salary")
                if salary_element:
                    salary_text = self.extract_text_safe(salary_element)
                    job_details["salary"] = self._parse_salary(salary_text)
                
                # Extract experience level
                exp_element = details_section.find_element(By.CSS_SELECTOR, ".experience")
                if exp_element:
                    exp_text = self.extract_text_safe(exp_element)
                    job_details["experience_level"] = self._map_experience_level(exp_text)
            
            # Extract skills from description and tags
            if "description" in job_details:
                job_details["extracted_skills"] = self._extract_skills_from_description(job_details["description"])
            
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
            # Extract emails and phones from description
            description = job_data.get("description", "")
            if description:
                emails = self.extract_emails_from_text(description)
                phones = self.extract_phones_from_text(description)
                
                if emails:
                    contact_info["recruiter_email"] = emails[0]
                if phones:
                    contact_info["recruiter_phone"] = phones[0]
            
            # Try to find HR contact information in job posting
            hr_section = self.safe_find_element(By.CSS_SELECTOR, ".hrContact, .recruiterContact")
            if hr_section:
                hr_text = self.extract_text_safe(hr_section)
                
                # Extract name from HR section
                name_match = re.search(r"Contact:?\s*([A-Za-z\s]+)", hr_text)
                if name_match:
                    contact_info["recruiter_name"] = name_match.group(1).strip()
                
                # Extract additional emails and phones
                hr_emails = self.extract_emails_from_text(hr_text)
                hr_phones = self.extract_phones_from_text(hr_text)
                
                if hr_emails and not contact_info["recruiter_email"]:
                    contact_info["recruiter_email"] = hr_emails[0]
                if hr_phones and not contact_info["recruiter_phone"]:
                    contact_info["recruiter_phone"] = hr_phones[0]
        
        except Exception as e:
            print(f"Error extracting contact info: {e}")
        
        return contact_info
    
    def _parse_salary(self, salary_text: str) -> Dict[str, Any]:
        """Parse salary information from text"""
        salary_info = {
            "min_salary": None,
            "max_salary": None,
            "currency": "INR",
            "per": "year"
        }
        
        try:
            # Extract salary numbers (in lakhs/thousands)
            salary_pattern = r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(lakh|thousand|LPA|lakhs|thousands)'
            match = re.search(salary_pattern, salary_text.lower())
            
            if match:
                min_sal = float(match.group(1))
                max_sal = float(match.group(2))
                unit = match.group(3).lower()
                
                # Convert to actual numbers
                if "lakh" in unit:
                    salary_info["min_salary"] = min_sal * 100000
                    salary_info["max_salary"] = max_sal * 100000
                elif "thousand" in unit:
                    salary_info["min_salary"] = min_sal * 1000
                    salary_info["max_salary"] = max_sal * 1000
        
        except Exception as e:
            print(f"Error parsing salary: {e}")
        
        return salary_info
    
    def _map_experience_level(self, experience_text: str) -> str:
        """Map experience text to our enum"""
        exp_lower = experience_text.lower()
        
        if "0" in exp_lower or "fresher" in exp_lower:
            return ExperienceLevel.FRESHER
        elif any(x in exp_lower for x in ["1", "2", "entry"]):
            return ExperienceLevel.ENTRY_LEVEL
        elif any(x in exp_lower for x in ["3", "4", "5", "6", "mid"]):
            return ExperienceLevel.MID_LEVEL
        elif any(x in exp_lower for x in ["7", "8", "9", "10", "senior"]):
            return ExperienceLevel.SENIOR_LEVEL
        else:
            return ExperienceLevel.ENTRY_LEVEL
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills from job description"""
        # Common technical skills for Indian job market
        tech_skills = [
            "java", "python", "javascript", "react", "angular", "node.js", "php",
            "sql", "mysql", "oracle", "mongodb", "postgresql", "html", "css",
            "spring", "hibernate", "rest api", "microservices", "aws", "azure",
            "git", "jenkins", "docker", "kubernetes", "agile", "scrum",
            "c++", "c#", ".net", "asp.net", "mvc", "web api", "json", "xml",
            "machine learning", "data science", "python", "r", "tableau",
            "power bi", "excel", "salesforce", "sap", "testing", "selenium",
            "manual testing", "automation testing", "jira", "confluence"
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in tech_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills
