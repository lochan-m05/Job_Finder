from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import re
from .base_scraper import BaseScraper
from app.models.job import JobSource

class TwitterScraper(BaseScraper):
    """Twitter job scraper for hashtag-based job postings"""
    
    def __init__(self, use_proxy: bool = False, headless: bool = True):
        super().__init__(use_proxy, headless)
        self.base_url = "https://twitter.com"
    
    def search_jobs(self, hashtags: List[str], time_filter: str) -> List[Dict[str, Any]]:
        """Search for job postings on Twitter using hashtags"""
        jobs = []
        
        try:
            # Create search query with hashtags
            search_query = " OR ".join(hashtags)
            search_query += " (job OR hiring OR opportunity OR career OR recruitment)"
            
            # Navigate to Twitter search
            search_url = f"{self.base_url}/search"
            self.driver.get(search_url)
            self.random_delay(3, 5)
            
            # Enter search query
            search_box = self.safe_find_element(By.CSS_SELECTOR, "[data-testid='SearchBox_Search_Input']")
            if search_box:
                search_box.clear()
                search_box.send_keys(search_query)
                search_box.send_keys(Keys.RETURN)
                self.random_delay(3, 5)
            
            # Switch to Latest tab for recent posts
            latest_tab = self.safe_find_element(By.XPATH, "//span[text()='Latest']/parent::*")
            if latest_tab:
                latest_tab.click()
                self.random_delay(2, 3)
            
            # Scroll to load more tweets
            self._scroll_to_load_tweets()
            
            # Extract tweets that look like job postings
            tweets = self.safe_find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
            
            for tweet in tweets[:50]:  # Limit to first 50 tweets
                try:
                    job_data = self._extract_job_from_tweet(tweet)
                    if job_data and self._is_job_related(job_data["content"]):
                        jobs.append(job_data)
                        
                except Exception as e:
                    print(f"Error extracting tweet: {e}")
                    continue
            
        except Exception as e:
            print(f"Error searching Twitter jobs: {e}")
        
        return jobs
    
    def _scroll_to_load_tweets(self):
        """Scroll down to load more tweets"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for _ in range(5):  # Scroll 5 times
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.random_delay(2, 3)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def _extract_job_from_tweet(self, tweet) -> Dict[str, Any]:
        """Extract job information from tweet element"""
        try:
            # Tweet content
            content_element = tweet.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']")
            content = self.extract_text_safe(content_element)
            
            # User information
            user_element = tweet.find_element(By.CSS_SELECTOR, "[data-testid='User-Name'] span")
            user_name = self.extract_text_safe(user_element)
            
            # User handle
            handle_element = tweet.find_element(By.CSS_SELECTOR, "[data-testid='User-Name'] a")
            user_handle = self.extract_text_safe(handle_element)
            
            # Tweet time
            time_element = tweet.find_element(By.CSS_SELECTOR, "time")
            posted_time = self.extract_attribute_safe(time_element, "datetime")
            
            # Tweet URL
            tweet_link = tweet.find_element(By.CSS_SELECTOR, "time").find_element(By.XPATH, "..")
            tweet_url = self.extract_attribute_safe(tweet_link, "href")
            if tweet_url and not tweet_url.startswith("http"):
                tweet_url = self.base_url + tweet_url
            
            # Extract structured job information from content
            job_info = self._parse_job_content(content)
            
            return {
                "title": job_info.get("title", "Job Opportunity"),
                "company": job_info.get("company", user_name),
                "description": content,
                "content": content,
                "user_name": user_name,
                "user_handle": user_handle,
                "job_url": tweet_url,
                "posted_time": posted_time,
                "source": JobSource.TWITTER,
                "location": job_info.get("location"),
                "salary": job_info.get("salary"),
                "experience": job_info.get("experience"),
                "skills": job_info.get("skills", [])
            }
            
        except NoSuchElementException:
            return None
    
    def _is_job_related(self, content: str) -> bool:
        """Check if tweet content is actually job-related"""
        job_keywords = [
            "hiring", "job", "opportunity", "career", "position", "role",
            "looking for", "seeking", "recruitment", "vacancy", "opening",
            "apply", "resume", "cv", "candidate", "interview", "salary",
            "experience", "skills", "requirements", "qualifications"
        ]
        
        content_lower = content.lower()
        
        # Must contain at least 2 job-related keywords
        keyword_count = sum(1 for keyword in job_keywords if keyword in content_lower)
        
        # Also check for email/contact information
        has_contact = bool(self.extract_emails_from_text(content) or 
                          self.extract_phones_from_text(content) or
                          "dm" in content_lower or "contact" in content_lower)
        
        return keyword_count >= 2 or (keyword_count >= 1 and has_contact)
    
    def _parse_job_content(self, content: str) -> Dict[str, Any]:
        """Parse job information from tweet content"""
        job_info = {}
        
        # Extract job title
        title_patterns = [
            r"(?:hiring|looking for|seeking)\s+(?:a\s+)?([A-Za-z\s]+?)(?:\s+at|\s+for|\s+-|$)",
            r"job\s+(?:opening|position)\s*:?\s*([A-Za-z\s]+?)(?:\s+at|\s+for|\s+-|$)",
            r"(\w+\s+(?:developer|engineer|manager|analyst|designer|intern))",
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                job_info["title"] = match.group(1).strip()
                break
        
        # Extract company name
        company_patterns = [
            r"at\s+([A-Za-z\s]+?)(?:\s+is|\s+are|\s+for|\s+-|$)",
            r"@(\w+)",  # Twitter handle might be company
            r"([A-Z][a-zA-Z\s]+)\s+is\s+hiring"
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, content)
            if match:
                job_info["company"] = match.group(1).strip()
                break
        
        # Extract location
        location_patterns = [
            r"(?:in|at|location)\s*:?\s*([A-Za-z\s,]+?)(?:\s+for|\s+-|$)",
            r"([A-Za-z\s]+,\s*India)",
            r"(Mumbai|Delhi|Bangalore|Hyderabad|Chennai|Pune|Kolkata|Ahmedabad|Gurgaon|Noida)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                job_info["location"] = match.group(1).strip()
                break
        
        # Extract salary information
        salary_patterns = [
            r"salary\s*:?\s*₹?\s*(\d+(?:,\d+)*(?:\s*-\s*₹?\s*\d+(?:,\d+)*)?)",
            r"₹\s*(\d+(?:,\d+)*(?:\s*-\s*₹?\s*\d+(?:,\d+)*)?)",
            r"(\d+\s*LPA|\d+\s*lakhs?)"
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                job_info["salary"] = match.group(1).strip()
                break
        
        # Extract experience requirements
        exp_patterns = [
            r"(\d+\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp))",
            r"(?:experience|exp)\s*:?\s*(\d+\+?\s*(?:years?|yrs?))",
            r"(fresher|entry.level|senior|mid.level)"
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                job_info["experience"] = match.group(1).strip()
                break
        
        # Extract skills
        skills = []
        skill_patterns = [
            r"(?:skills?|technologies?|tech\s+stack)\s*:?\s*([A-Za-z,\s/]+?)(?:\s+for|\s+-|$)",
            r"#(\w+)"  # Hashtags might be skills
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    skills.extend([s.strip() for s in match.split(",")])
        
        job_info["skills"] = [skill for skill in skills if len(skill) > 2]
        
        return job_info
    
    def extract_job_details(self, job_url: str) -> Dict[str, Any]:
        """Extract additional details from tweet URL"""
        try:
            self.driver.get(job_url)
            self.random_delay(2, 3)
            
            # Get tweet thread or replies for more details
            details = {}
            
            # Look for replies that might contain more job details
            replies = self.safe_find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
            
            for reply in replies[1:3]:  # Check first 2 replies
                try:
                    reply_content = reply.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']")
                    reply_text = self.extract_text_safe(reply_content)
                    
                    # Check if reply contains additional job information
                    if any(keyword in reply_text.lower() for keyword in ["apply", "email", "contact", "cv", "resume"]):
                        reply_info = self._parse_job_content(reply_text)
                        details.update(reply_info)
                        
                        # Extract contact information
                        emails = self.extract_emails_from_text(reply_text)
                        phones = self.extract_phones_from_text(reply_text)
                        
                        if emails:
                            details["contact_email"] = emails[0]
                        if phones:
                            details["contact_phone"] = phones[0]
                
                except Exception:
                    continue
            
            return details
            
        except Exception as e:
            print(f"Error extracting tweet details: {e}")
            return {}
    
    def extract_contact_info(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contact information from tweet"""
        contact_info = {
            "recruiter_name": None,
            "recruiter_email": None,
            "recruiter_phone": None,
            "recruiter_linkedin": None,
            "company_email": None
        }
        
        # Use the tweet author as potential recruiter
        contact_info["recruiter_name"] = job_data.get("user_name")
        
        # Extract contact from tweet content
        content = job_data.get("content", "")
        
        emails = self.extract_emails_from_text(content)
        phones = self.extract_phones_from_text(content)
        
        if emails:
            contact_info["recruiter_email"] = emails[0]
        if phones:
            contact_info["recruiter_phone"] = phones[0]
        
        # Twitter handle as LinkedIn alternative
        user_handle = job_data.get("user_handle", "")
        if user_handle:
            contact_info["recruiter_linkedin"] = f"https://twitter.com/{user_handle.replace('@', '')}"
        
        return contact_info
