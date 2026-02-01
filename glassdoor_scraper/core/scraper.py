"""Main Glassdoor scraper implementation."""

import re
import time
import random
from typing import List, Dict, Any, Optional, Callable
from urllib.parse import urlencode, quote

from .browser import StealthBrowser
from .extractor import JobDataExtractor
from ..config import ScraperConfig
from ..utils import human_like_delay, random_delay, ProxyManager
from ..utils.helpers import format_job_data, retry_with_backoff
from ..exceptions import (
    CaptchaDetectedException,
    RateLimitException,
    AccessBlockedException,
    ParseException,
)
from ..storage import DataExporter


class GlassdoorScraper:
    """Main scraper class for Glassdoor job listings."""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize the Glassdoor scraper.
        
        Args:
            config: Scraper configuration
        """
        self.config = config or ScraperConfig()
        self.browser: Optional[StealthBrowser] = None
        self.extractor = JobDataExtractor()
        self.exporter = DataExporter(self.config.output_dir)
        self.jobs: List[Dict[str, Any]] = []
        self._stop_requested = False
    
    def start(self) -> "GlassdoorScraper":
        """
        Start the scraper and initialize the browser.
        
        Returns:
            Self for method chaining
        """
        print("Starting Glassdoor scraper...")
        self.browser = StealthBrowser(self.config)
        self.browser.start()
        print("Browser started successfully")
        return self
    
    def stop(self) -> None:
        """Stop the scraper and cleanup resources."""
        self._stop_requested = True
        if self.browser:
            self.browser.close()
            self.browser = None
        print("Scraper stopped")
    
    def search(
        self,
        keyword: str,
        location: str = "",
        job_type: str = "",
        remote: bool = False,
        days_ago: int = 0,
        min_salary: int = 0,
        max_salary: int = 0,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs on Glassdoor.
        
        Args:
            keyword: Job title or keywords
            location: Job location (city, state, or "remote")
            job_type: Job type filter (fulltime, parttime, contract, internship)
            remote: Whether to filter for remote jobs only
            days_ago: Filter for jobs posted within this many days
            min_salary: Minimum salary filter
            max_salary: Maximum salary filter
            progress_callback: Callback function(current, total) for progress updates
            
        Returns:
            List of job dictionaries
        """
        if not self.browser:
            raise RuntimeError("Scraper not started. Call start() first.")
        
        self.jobs = []
        page = 1
        
        # Build search URL
        search_url = self._build_search_url(
            keyword=keyword,
            location=location,
            job_type=job_type,
            remote=remote,
            days_ago=days_ago,
        )
        
        print(f"Searching for: {keyword} in {location or 'any location'}")
        print(f"Starting at: {search_url}")
        
        # Wait a bit before starting to avoid immediate detection
        import time
        time.sleep(random.uniform(2, 4))
        
        try:
            while page <= self.config.max_pages and len(self.jobs) < self.config.max_jobs:
                if self._stop_requested:
                    break
                
                print(f"\nProcessing page {page}...")
                
                # Navigate to search page
                print(f"  Navigating to search page...")
                self.browser.navigate(search_url, wait_until="domcontentloaded", timeout=45000)
                human_like_delay("page_load")
                
                # Scroll to load all content
                self.browser.random_scroll()
                human_like_delay("read")
                
                # Extract jobs from page
                html = self.browser.get_page_content()
                page_jobs = self.extractor.extract_jobs_from_search_page(html)
                
                if not page_jobs:
                    print("No jobs found on this page")
                    break
                
                print(f"Found {len(page_jobs)} job listings on page {page}")
                
                # Process each job
                for job in page_jobs:
                    if self._stop_requested or len(self.jobs) >= self.config.max_jobs:
                        break
                    
                    # Get detailed information
                    detailed_job = self._get_job_details(job)
                    
                    if detailed_job:
                        # Apply salary filter
                        if min_salary > 0 or max_salary > 0:
                            if not self._passes_salary_filter(detailed_job, min_salary, max_salary):
                                continue
                        
                        self.jobs.append(detailed_job)
                        
                        if progress_callback:
                            progress_callback(len(self.jobs), self.config.max_jobs)
                        
                        print(f"  ✓ Scraped: {detailed_job.get('title', 'Unknown')} at {detailed_job.get('company', 'Unknown')}")
                    
                    # Delay between jobs
                    random_delay(
                        self.config.min_delay,
                        self.config.max_delay
                    )
                
                # Check for next page
                if not self.extractor.has_next_page(html):
                    print("No more pages available")
                    break
                
                # Get next page URL
                next_url = self.extractor.get_next_page_url(html)
                if not next_url:
                    # Try to construct next page URL
                    search_url = self._get_next_page_url(search_url, page + 1)
                else:
                    search_url = next_url
                
                page += 1
                
                # Delay between pages
                human_like_delay("navigate")
        
        except CaptchaDetectedException as e:
            print(f"\n⚠ CAPTCHA detected: {e}")
            print("Please solve the CAPTCHA manually or try again later.")
        
        except AccessBlockedException as e:
            print(f"\n⚠ Access blocked: {e}")
            print("Consider using proxies or waiting before trying again.")
        
        except Exception as e:
            print(f"\n✗ Error during search: {e}")
        
        print(f"\n✓ Scraping complete. Total jobs collected: {len(self.jobs)}")
        return self.jobs
    
    def _build_search_url(
        self,
        keyword: str,
        location: str = "",
        job_type: str = "",
        remote: bool = False,
        days_ago: int = 0,
    ) -> str:
        """Build the Glassdoor search URL with parameters."""
        # Use the simpler job search URL format
        base_url = "https://www.glassdoor.com/Job/jobs.htm"
        
        params = {
            "sc.keyword": keyword,
        }
        
        # For location, use the suggestType parameter which works better
        if location:
            params["sc.location"] = location
        
        if remote:
            params["remoteWorkType"] = "1"
        
        if days_ago > 0:
            # Glassdoor uses different date ranges
            if days_ago <= 1:
                params["fromAge"] = "1"
            elif days_ago <= 3:
                params["fromAge"] = "3"
            elif days_ago <= 7:
                params["fromAge"] = "7"
            elif days_ago <= 14:
                params["fromAge"] = "14"
            else:
                params["fromAge"] = "30"
        
        # Job type mapping
        job_type_map = {
            "fulltime": "F",
            "parttime": "P",
            "contract": "C",
            "internship": "I",
        }
        if job_type and job_type.lower() in job_type_map:
            params["jobType"] = job_type_map[job_type.lower()]
        
        query_string = urlencode(params, quote_via=quote)
        return f"{base_url}?{query_string}"
    
    def _get_next_page_url(self, current_url: str, next_page: int) -> str:
        """Construct URL for the next page."""
        # Glassdoor uses pagination parameters
        if "p=" in current_url:
            return re.sub(r'p=\d+', f'p={next_page}', current_url)
        else:
            separator = "&" if "?" in current_url else "?"
            return f"{current_url}{separator}p={next_page}"
    
    def _get_job_details(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get detailed information for a job."""
        job_url = job.get('job_url')
        if not job_url:
            return job
        
        retries = 0
        while retries < self.config.max_retries:
            try:
                # Navigate to job page
                self.browser.navigate(job_url)
                human_like_delay("page_load")
                
                # Extract detailed information
                html = self.browser.get_page_content()
                details = self.extractor.extract_job_details(html)
                
                # Merge with basic job info
                job.update(details)
                
                return format_job_data(job)
            
            except (CaptchaDetectedException, AccessBlockedException):
                raise
            
            except Exception as e:
                retries += 1
                if retries >= self.config.max_retries:
                    print(f"  ✗ Failed to get details after {retries} attempts: {e}")
                    return job
                
                wait_time = self.config.retry_delay * (2 ** retries)
                print(f"  ⚠ Retry {retries}/{self.config.max_retries} in {wait_time:.1f}s...")
                time.sleep(wait_time)
        
        return job
    
    def _passes_salary_filter(self, job: Dict[str, Any], min_salary: int, max_salary: int) -> bool:
        """Check if job passes salary filter."""
        salary_text = job.get('salary', '')
        if not salary_text:
            return True  # Include jobs without salary info
        
        # Extract numbers from salary text
        import re
        numbers = re.findall(r'\d+', salary_text.replace(',', ''))
        
        if not numbers:
            return True
        
        # Assume first number is min, second is max (or double the first for hourly)
        job_min = int(numbers[0])
        job_max = int(numbers[1]) if len(numbers) > 1 else job_min * 2
        
        # Check if ranges overlap
        if max_salary > 0 and job_min > max_salary:
            return False
        if min_salary > 0 and job_max < min_salary:
            return False
        
        return True
    
    def export(self, format_type: str = "both", filename: str = None) -> List[str]:
        """
        Export scraped jobs to file(s).
        
        Args:
            format_type: Export format - "csv", "json", or "both"
            filename: Base filename (optional)
            
        Returns:
            List of exported file paths
        """
        return self.exporter.export(self.jobs, format_type, filename)
    
    def get_jobs(self) -> List[Dict[str, Any]]:
        """Get the list of scraped jobs."""
        return self.jobs
    
    def clear_jobs(self) -> None:
        """Clear the jobs list."""
        self.jobs = []
    
    def __enter__(self) -> "GlassdoorScraper":
        """Context manager entry."""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()


# Convenience function for quick scraping
def scrape_jobs(
    keyword: str,
    location: str = "",
    max_jobs: int = 50,
    headless: bool = True,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Quick function to scrape jobs without managing the scraper instance.
    
    Args:
        keyword: Job title or keywords
        location: Job location
        max_jobs: Maximum number of jobs to scrape
        headless: Whether to run browser in headless mode
        **kwargs: Additional arguments for search()
        
    Returns:
        List of job dictionaries
    """
    config = ScraperConfig(headless=headless, max_jobs=max_jobs)
    
    with GlassdoorScraper(config) as scraper:
        jobs = scraper.search(keyword, location, **kwargs)
        scraper.export()
        return jobs