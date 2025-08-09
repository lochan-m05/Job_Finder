from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import re
from .base_scraper import BaseScraper
from app.models.job import JobSource, JobType, ExperienceLevel

class IndeedScraper(BaseScraper):
    """Indeed.com job scraper"""
    
    def __init__(self, use_proxy: bool = False, headless: bool = True):
        super().__init__(use_proxy, headless)
        self.base_url = "https://in.indeed.com"
    
    def search_jobs(self, hashtags: List[str], time_filter: str) -> List[Dict[str, Any]]:
        """Search for jobs on Indeed"""
        jobs = []
        
        try:
            # Convert hashtags to search query
            search_query = " ".join([tag.replace("#", "") for tag in hashtags])
            
            # Navigate to Indeed search
            self.driver.get(self.base_url)
            self.random_delay(2, 4)
            
            # Enter search query
            search_box = self.safe_find_element(By.ID, "text-input-what")
            if search_box:
                search_box.clear()
                search_box.send_keys(search_query)
            
            # Set location to India (if location field exists)
            location_box = self.safe_find_element(By.ID, "text-input-where")
            if location_box:
                location_box.clear()
                location_box.send_keys("India")
            
            # Submit search
            search_button = self.safe_find_element(By.CSS_SELECTOR, "button[type='submit']")
            if search_button:
                search_button.click()
                self.random_delay(3, 5)
            
            # Apply time filter
            self._apply_time_filter(time_filter)
            
            # Extract job listings
            job_cards = self.safe_find_elements(By.CSS_SELECTOR, "[data-jk]")
            
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
                    print(f"Error extracting Indeed job card: {e}")
                    continue
            
        except Exception as e:
            print(f"Error searching Indeed jobs: {e}")
        
        return jobs
    
    def _apply_time_filter(self, time_filter: str):
        """Apply time filter to search results"""
        try:
            # Look for date posted filter
            date_filter = self.safe_find_element(By.CSS_SELECTOR, "button[aria-controls='filter-dateposted-menu']")
            if date_filter:
                date_filter.click()
                self.random_delay(1, 2)
                
                # Map time filters to Indeed options
                time_filter_map = {
                    "1h": "1",      # Last 24 hours
                    "24h": "1",     # Last 24 hours
                    "7d": "7",      # Last 7 days
                    "30d": "14"     # Last 14 days (closest to 30d)
                }
                
                if time_filter in time_filter_map:
                    days = time_filter_map[time_filter]
                    filter_option = self.safe_find_element(
                        By.XPATH, 
                        f"//a[contains(@href, 'fromage={days}')]"
                    )
                    if filter_option:
                        filter_option.click()
                        self.random_delay(2, 3)
        
        except Exception as e:
            print(f"Error applying time filter: {e}")
    
    def _extract_job_card_data(self, card) -> Dict[str, Any]:
        """Extract data from job card element"""
        try:
            # Get job ID
            job_id = self.extract_attribute_safe(card, "data-jk")
            
            # Job title and URL
            title_element = card.find_element(By.CSS_SELECTOR, "h2 a span[title]")
            title = self.extract_attribute_safe(title_element, "title")
            
            # Construct job URL
            job_url = f"{self.base_url}/viewjob?jk={job_id}"
            
            # Company
            company_element = card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']")
            company = self.extract_text_safe(company_element)
            
            # Location
            location_element = card.find_element(By.CSS_SELECTOR, "[data-testid='job-location']")
            location = self.extract_text_safe(location_element)
            
            # Salary (if available)
            salary_element = card.find_element(By.CSS_SELECTOR, "[data-testid='attribute_snippet_testid']")
            salary = self.extract_text_safe(salary_element) if salary_element else None
            
            # Job snippet/summary
            snippet_element = card.find_element(By.CSS_SELECTOR, "[data-testid='job-snippet']")
            snippet = self.extract_text_safe(snippet_element)
            
            # Posted date
            posted_element = card.find_element(By.CSS_SELECTOR, "[data-testid='myJobsStateDate']")
            posted_time = self.extract_text_safe(posted_element)
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "snippet": snippet,
                "job_url": job_url,
                "posted_time": posted_time,
                "source": JobSource.INDEED
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
                "#jobDescriptionText, [data-testid='jobsearch-jobDescriptionText']"
            )
            if description_element:
                job_details["description"] = self.extract_text_safe(description_element)
            
            # Job details from the page
            details_section = self.safe_find_element(By.CSS_SELECTOR, ".jobsearch-jobDescriptionText")
            
            # Extract salary if available
            salary_elements = self.safe_find_elements(By.CSS_SELECTOR, "[data-testid='job-salary']")
            if salary_elements:
                salary_text = self.extract_text_safe(salary_elements[0])
                job_details["salary"] = self._parse_salary(salary_text)
            
            # Extract job type
            job_type_elements = self.safe_find_elements(By.CSS_SELECTOR, "[data-testid='job-type-text']")
            if job_type_elements:
                job_type_text = self.extract_text_safe(job_type_elements[0])
                job_details["job_type"] = self._map_job_type(job_type_text)
            
            # Extract skills from description
            if "description" in job_details:
                job_details["extracted_skills"] = self._extract_skills_from_description(job_details["description"])
            
            # Extract company information
            company_section = self.safe_find_element(By.CSS_SELECTOR, "[data-testid='inlineHeader-companyName']")
            if company_section:
                company_link = company_section.find_element(By.TAG_NAME, "a")
                if company_link:
                    job_details["company_url"] = self.extract_attribute_safe(company_link, "href")
            
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
            
            # Look for hiring manager or recruiter information
            hiring_info = self.safe_find_element(By.CSS_SELECTOR, ".jobsearch-HiringInsights")
            if hiring_info:
                hiring_text = self.extract_text_safe(hiring_info)
                
                # Extract recruiter name
                name_patterns = [
                    r"Posted by:?\s*([A-Za-z\s]+)",
                    r"Recruiter:?\s*([A-Za-z\s]+)",
                    r"Hiring Manager:?\s*([A-Za-z\s]+)"
                ]
                
                for pattern in name_patterns:
                    name_match = re.search(pattern, hiring_text)
                    if name_match:
                        contact_info["recruiter_name"] = name_match.group(1).strip()
                        break
            
            # Try to extract contact from company page
            company_url = job_data.get("company_url")
            if company_url and company_url.startswith("/"):
                company_url = self.base_url + company_url
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
            
            # Look for company information
            company_info = self.safe_find_element(By.CSS_SELECTOR, ".cmp-company-overview")
            if company_info:
                info_text = self.extract_text_safe(company_info)
                
                # Extract emails and phones
                emails = self.extract_emails_from_text(info_text)
                phones = self.extract_phones_from_text(info_text)
                
                if emails:
                    contacts["company_email"] = emails[0]
                if phones:
                    contacts["recruiter_phone"] = phones[0]
        
        except Exception as e:
            print(f"Error extracting company contacts: {e}")
        
        return contacts
    
    def _parse_salary(self, salary_text: str) -> Dict[str, Any]:
        """Parse salary information from text"""
        salary_info = {
            "min_salary": None,
            "max_salary": None,
            "currency": "INR",
            "per": "year"
        }
        
        try:
            # Extract salary numbers
            salary_patterns = [
                r'₹\s*(\d+(?:,\d+)*)\s*-\s*₹\s*(\d+(?:,\d+)*)',  # ₹50,000 - ₹70,000
                r'(\d+(?:,\d+)*)\s*-\s*(\d+(?:,\d+)*)\s*per\s+month',  # 50,000 - 70,000 per month
                r'(\d+(?:,\d+)*)\s*-\s*(\d+(?:,\d+)*)\s*monthly'   # 50,000 - 70,000 monthly
            ]
            
            for pattern in salary_patterns:
                match = re.search(pattern, salary_text)
                if match:
                    min_sal = float(match.group(1).replace(",", ""))
                    max_sal = float(match.group(2).replace(",", ""))
                    
                    salary_info["min_salary"] = min_sal
                    salary_info["max_salary"] = max_sal
                    
                    # Determine if it's monthly or yearly
                    if "month" in salary_text.lower():
                        salary_info["per"] = "month"
                    
                    break
        
        except Exception as e:
            print(f"Error parsing salary: {e}")
        
        return salary_info
    
    def _map_job_type(self, job_type_text: str) -> str:
        """Map job type text to our enum"""
        job_type_lower = job_type_text.lower()
        
        if "full-time" in job_type_lower or "full time" in job_type_lower:
            return JobType.FULL_TIME
        elif "part-time" in job_type_lower or "part time" in job_type_lower:
            return JobType.PART_TIME
        elif "contract" in job_type_lower:
            return JobType.CONTRACT
        elif "internship" in job_type_lower:
            return JobType.INTERNSHIP
        elif "freelance" in job_type_lower:
            return JobType.FREELANCE
        else:
            return JobType.FULL_TIME
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills from job description"""
        # Common skills for Indeed job postings
        tech_skills = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js",
            "sql", "mongodb", "postgresql", "mysql", "html", "css", "php",
            "c++", "c#", ".net", "spring", "django", "flask", "laravel",
            "aws", "azure", "gcp", "docker", "kubernetes", "git", "jenkins",
            "machine learning", "data science", "ai", "pandas", "numpy",
            "tableau", "power bi", "excel", "salesforce", "sap", "crm",
            "testing", "selenium", "cypress", "junit", "agile", "scrum",
            "rest api", "graphql", "microservices", "devops", "ci/cd"
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in tech_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills
