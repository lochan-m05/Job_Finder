from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from datetime import datetime
import logging

from .linkedin_scraper import LinkedInScraper
from .naukri_scraper import NaukriScraper
from .indeed_scraper import IndeedScraper
from .twitter_scraper import TwitterScraper
from app.models.job import JobSource

logger = logging.getLogger(__name__)

class ScraperManager:
    """Manages multiple scrapers and coordinates scraping tasks"""
    
    def __init__(self, use_proxy: bool = False, headless: bool = True):
        self.use_proxy = use_proxy
        self.headless = headless
        self.scrapers = {}
        self._initialize_scrapers()
    
    def _initialize_scrapers(self):
        """Initialize all available scrapers"""
        scraper_classes = {
            JobSource.LINKEDIN: LinkedInScraper,
            JobSource.NAUKRI: NaukriScraper,
            JobSource.INDEED: IndeedScraper,
            JobSource.TWITTER: TwitterScraper
        }
        
        for source, scraper_class in scraper_classes.items():
            try:
                self.scrapers[source] = scraper_class(
                    use_proxy=self.use_proxy,
                    headless=self.headless
                )
                logger.info(f"Initialized {source} scraper")
            except Exception as e:
                logger.error(f"Failed to initialize {source} scraper: {e}")
    
    async def scrape_jobs(
        self,
        hashtags: List[str],
        sources: List[str],
        time_filter: str = "24h",
        max_workers: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Scrape jobs from multiple sources concurrently
        
        Args:
            hashtags: List of hashtags to search for
            sources: List of job sources to scrape
            time_filter: Time filter for job posting age
            max_workers: Maximum number of concurrent scrapers
        
        Returns:
            List of job dictionaries
        """
        all_jobs = []
        
        # Filter sources to only include available scrapers
        available_sources = [source for source in sources if source in self.scrapers]
        
        if not available_sources:
            logger.warning("No available scrapers for requested sources")
            return all_jobs
        
        # Run scrapers concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit scraping tasks
            future_to_source = {}
            
            for source in available_sources:
                scraper = self.scrapers[source]
                future = executor.submit(
                    self._scrape_with_error_handling,
                    scraper,
                    hashtags,
                    time_filter,
                    source
                )
                future_to_source[future] = source
            
            # Collect results as they complete
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    jobs = future.result()
                    if jobs:
                        all_jobs.extend(jobs)
                        logger.info(f"Successfully scraped {len(jobs)} jobs from {source}")
                    else:
                        logger.warning(f"No jobs found from {source}")
                        
                except Exception as e:
                    logger.error(f"Error scraping from {source}: {e}")
        
        # Remove duplicates based on job URL
        unique_jobs = self._remove_duplicates(all_jobs)
        
        logger.info(f"Total unique jobs scraped: {len(unique_jobs)}")
        return unique_jobs
    
    def _scrape_with_error_handling(
        self,
        scraper,
        hashtags: List[str],
        time_filter: str,
        source: str
    ) -> List[Dict[str, Any]]:
        """
        Scrape jobs with error handling and session management
        """
        jobs = []
        
        try:
            # Start scraper session
            scraper.start_session()
            
            # Special handling for LinkedIn (requires login)
            if source == JobSource.LINKEDIN:
                if not scraper.login():
                    logger.warning("LinkedIn login failed, skipping LinkedIn scraping")
                    return jobs
            
            # Scrape jobs
            jobs = scraper.search_jobs(hashtags, time_filter)
            
            # Extract contact information for each job
            for job in jobs:
                try:
                    contact_info = scraper.extract_contact_info(job)
                    job.update(contact_info)
                except Exception as e:
                    logger.warning(f"Failed to extract contact info for job {job.get('title', 'Unknown')}: {e}")
            
        except Exception as e:
            logger.error(f"Error in scraper {source}: {e}")
            
        finally:
            # Always close scraper session
            try:
                scraper.close_session()
            except Exception as e:
                logger.error(f"Error closing scraper session for {source}: {e}")
        
        return jobs
    
    def _remove_duplicates(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate jobs based on URL and title similarity"""
        seen_urls = set()
        seen_titles = set()
        unique_jobs = []
        
        for job in jobs:
            job_url = job.get("job_url", "")
            job_title = job.get("title", "").lower().strip()
            company = job.get("company", "").lower().strip()
            
            # Create a unique identifier
            job_key = f"{job_title}:{company}"
            
            # Skip if we've seen this URL or very similar job
            if job_url in seen_urls or job_key in seen_titles:
                continue
            
            seen_urls.add(job_url)
            seen_titles.add(job_key)
            unique_jobs.append(job)
        
        return unique_jobs
    
    async def scrape_single_source(
        self,
        source: str,
        hashtags: List[str],
        time_filter: str = "24h"
    ) -> List[Dict[str, Any]]:
        """Scrape jobs from a single source"""
        
        if source not in self.scrapers:
            logger.error(f"Scraper for {source} not available")
            return []
        
        scraper = self.scrapers[source]
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        jobs = await loop.run_in_executor(
            None,
            self._scrape_with_error_handling,
            scraper,
            hashtags,
            time_filter,
            source
        )
        
        return jobs
    
    def get_available_sources(self) -> List[str]:
        """Get list of available scraper sources"""
        return list(self.scrapers.keys())
    
    def close_all_sessions(self):
        """Close all scraper sessions"""
        for source, scraper in self.scrapers.items():
            try:
                scraper.close_session()
            except Exception as e:
                logger.error(f"Error closing session for {source}: {e}")

# Scraper factory function
def create_scraper_manager(use_proxy: bool = False, headless: bool = True) -> ScraperManager:
    """Factory function to create scraper manager"""
    return ScraperManager(use_proxy=use_proxy, headless=headless)
