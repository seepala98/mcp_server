"""Configuration settings for Glassdoor Scraper."""

import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ScraperConfig:
    """Configuration for the Glassdoor scraper."""
    
    # Browser settings
    headless: bool = True
    browser_type: str = "chromium"  # chromium, firefox, webkit
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # Rate limiting (seconds)
    min_delay: float = 3.0
    max_delay: float = 8.0
    page_load_timeout: int = 30
    navigation_timeout: int = 30
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 5.0
    
    # Job search settings
    max_jobs: int = 100
    max_pages: int = 10
    jobs_per_page: int = 30
    
    # Proxy settings
    use_proxies: bool = False
    proxy_list: List[str] = field(default_factory=list)
    proxy_timeout: int = 10
    
    # Anti-detection
    rotate_user_agents: bool = True
    randomize_viewport: bool = True
    
    # Output settings
    output_format: str = "csv"  # csv, json, both
    output_dir: str = "output"
    
    # Glassdoor specific
    base_url: str = "https://www.glassdoor.com"
    search_url: str = "https://www.glassdoor.com/Job/jobs.htm"
    
    @classmethod
    def from_env(cls) -> "ScraperConfig":
        """Create config from environment variables."""
        return cls(
            headless=os.getenv("SCRAPER_HEADLESS", "true").lower() == "true",
            browser_type=os.getenv("SCRAPER_BROWSER", "chromium"),
            use_proxies=os.getenv("USE_PROXIES", "false").lower() == "true",
            max_jobs=int(os.getenv("MAX_JOBS", "100")),
            max_pages=int(os.getenv("MAX_PAGES", "10")),
            min_delay=float(os.getenv("MIN_DELAY", "3.0")),
            max_delay=float(os.getenv("MAX_DELAY", "8.0")),
            output_dir=os.getenv("OUTPUT_DIR", "output"),
        )


# Default user agents for rotation
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.2; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# Viewport sizes for randomization
VIEWPORT_SIZES: List[Tuple[int, int]] = [
    (1920, 1080),
    (1366, 768),
    (1440, 900),
    (1536, 864),
    (1280, 720),
    (1600, 900),
    (2560, 1440),
    (1680, 1050),
]

# Selectors for Glassdoor job listings (may need updating)
JOB_LISTING_SELECTORS = {
    "job_card": "[data-test='jobListing']",
    "job_title": "a.jobLink",
    "company_name": ".employerName",
    "location": ".location",
    "salary": ".salary-estimate",
    "rating": ".rating",
    "job_link": "a.jobLink",
    "next_button": "[data-test='pagination-next']",
    "job_description": ".jobDescriptionContent",
    "job_description_alt": "[data-test='job-description']",
    "company_size": ".companySize",
    "company_industry": ".industry",
}

# CAPTCHA/Block detection patterns
BLOCK_PATTERNS = [
    "captcha",
    "challenge",
    "verify you are human",
    "access denied",
    "blocked",
    "security check",
    "please verify",
]

# Error messages
ERROR_MESSAGES = {
    "captcha_detected": "CAPTCHA detected. Please solve manually or try again later.",
    "rate_limited": "Rate limited by Glassdoor. Please wait before trying again.",
    "blocked": "Access blocked by Glassdoor. Consider using proxies.",
    "timeout": "Request timed out. The page may be slow or blocked.",
    "parse_error": "Failed to parse job data. The page structure may have changed.",
}