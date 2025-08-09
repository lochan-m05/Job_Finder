from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import random
import time
import requests
from fake_useragent import UserAgent
from datetime import datetime, timedelta
import re
import os
from dotenv import load_dotenv

load_dotenv()

class BaseScraper(ABC):
    """Base class for all web scrapers"""
    
    def __init__(self, use_proxy: bool = False, headless: bool = True):
        self.use_proxy = use_proxy
        self.headless = headless
        self.driver = None
        self.wait = None
        self.proxies = self._load_proxies()
        self.user_agent = UserAgent()
        self.session = requests.Session()
        
    def _load_proxies(self) -> List[Dict[str, str]]:
        """Load proxy list from environment"""
        proxy_list = os.getenv("PROXY_LIST", "")
        proxies = []
        
        if proxy_list:
            for proxy_str in proxy_list.split(","):
                parts = proxy_str.strip().split(":")
                if len(parts) >= 2:
                    proxy = {
                        "host": parts[0],
                        "port": parts[1],
                        "username": parts[2] if len(parts) > 2 else None,
                        "password": parts[3] if len(parts) > 3 else None
                    }
                    proxies.append(proxy)
        
        return proxies
    
    def _get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random proxy from the list"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with anti-detection measures"""
        options = Options()
        
        if self.headless:
            options.add_argument("--headless")
        
        # Anti-detection options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set random user agent
        user_agent = self.user_agent.random
        options.add_argument(f"--user-agent={user_agent}")
        
        # Proxy setup
        if self.use_proxy:
            proxy = self._get_random_proxy()
            if proxy:
                proxy_str = f"{proxy['host']}:{proxy['port']}"
                options.add_argument(f"--proxy-server=http://{proxy_str}")
        
        # Use undetected chromedriver
        driver = uc.Chrome(options=options)
        
        # Execute script to avoid detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def start_session(self):
        """Initialize scraping session"""
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 10)
        print(f"Started scraping session for {self.__class__.__name__}")
    
    def close_session(self):
        """Close scraping session"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
        print(f"Closed scraping session for {self.__class__.__name__}")
    
    def random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """Add random delay between requests"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def safe_find_element(self, by: By, value: str, timeout: int = 5) -> Optional[Any]:
        """Safely find element with timeout"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None
    
    def safe_find_elements(self, by: By, value: str) -> List[Any]:
        """Safely find multiple elements"""
        try:
            return self.driver.find_elements(by, value)
        except NoSuchElementException:
            return []
    
    def extract_text_safe(self, element) -> str:
        """Safely extract text from element"""
        try:
            return element.text.strip() if element else ""
        except:
            return ""
    
    def extract_attribute_safe(self, element, attribute: str) -> str:
        """Safely extract attribute from element"""
        try:
            return element.get_attribute(attribute) if element else ""
        except:
            return ""
    
    def parse_time_filter(self, time_filter: str) -> datetime:
        """Parse time filter string to datetime"""
        now = datetime.utcnow()
        
        if time_filter == "1h":
            return now - timedelta(hours=1)
        elif time_filter == "24h":
            return now - timedelta(hours=24)
        elif time_filter == "7d":
            return now - timedelta(days=7)
        elif time_filter == "30d":
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=24)  # Default to 24h
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return list(set(re.findall(email_pattern, text)))
    
    def extract_phones_from_text(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        # Indian phone number patterns
        phone_patterns = [
            r'\+91[\s-]?[6-9]\d{9}',  # +91 format
            r'91[\s-]?[6-9]\d{9}',    # 91 format
            r'[6-9]\d{9}',            # 10 digit format
            r'\d{3}[\s-]\d{3}[\s-]\d{4}',  # XXX-XXX-XXXX format
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        # Clean up phone numbers
        cleaned_phones = []
        for phone in phones:
            # Remove spaces and hyphens
            clean_phone = re.sub(r'[\s-]', '', phone)
            if len(clean_phone) >= 10:
                cleaned_phones.append(clean_phone)
        
        return list(set(cleaned_phones))
    
    @abstractmethod
    def search_jobs(self, hashtags: List[str], time_filter: str) -> List[Dict[str, Any]]:
        """Search for jobs based on hashtags and time filter"""
        pass
    
    @abstractmethod
    def extract_job_details(self, job_url: str) -> Dict[str, Any]:
        """Extract detailed job information from job URL"""
        pass
    
    @abstractmethod
    def extract_contact_info(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contact information from job data"""
        pass
