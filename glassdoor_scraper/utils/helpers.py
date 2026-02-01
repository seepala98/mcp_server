"""Helper utilities for the Glassdoor scraper."""

import random
import time
import re
from typing import Tuple, Optional
from datetime import datetime

from ..config import VIEWPORT_SIZES


def random_delay(min_seconds: float, max_seconds: float) -> None:
    """
    Sleep for a random amount of time between min and max seconds.
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def get_random_viewport() -> Tuple[int, int]:
    """
    Get a random viewport size.
    
    Returns:
        Tuple of (width, height)
    """
    return random.choice(VIEWPORT_SIZES)


def human_like_delay(action_type: str = "default") -> None:
    """
    Apply human-like delays based on action type.
    
    Args:
        action_type: Type of action (page_load, click, scroll, read, default)
    """
    delays = {
        "page_load": (2.0, 4.0),
        "click": (0.5, 1.5),
        "scroll": (0.3, 1.0),
        "read": (3.0, 6.0),
        "search": (2.0, 5.0),
        "navigate": (3.0, 7.0),
        "default": (1.0, 3.0),
    }
    
    min_delay, max_delay = delays.get(action_type, delays["default"])
    random_delay(min_delay, max_delay)


def random_scroll_behavior() -> dict:
    """
    Generate random scroll behavior parameters.
    
    Returns:
        Dictionary with scroll parameters
    """
    return {
        "steps": random.randint(3, 8),
        "delay": random.uniform(0.1, 0.3),
        "amount": random.randint(300, 800),
    }


def is_captcha_page(page_content: str) -> bool:
    """
    Check if the page content indicates a CAPTCHA or block.
    
    Args:
        page_content: HTML content of the page
        
    Returns:
        True if CAPTCHA detected, False otherwise
    """
    from ..config import BLOCK_PATTERNS
    
    content_lower = page_content.lower()
    return any(pattern in content_lower for pattern in BLOCK_PATTERNS)


def clean_text(text: Optional[str]) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
    
    return text.strip()


def extract_salary_range(text: str) -> Optional[str]:
    """
    Extract salary range from text.
    
    Args:
        text: Text containing salary information
        
    Returns:
        Extracted salary range or None
    """
    # Common salary patterns
    patterns = [
        r'\$[\d,]+\s*-\s*\$[\d,]+',  # $50,000 - $70,000
        r'\$[\d,]+K?\s*-\s*\$[\d,]+K?',  # $50K - $70K
        r'[\d,]+\s*-\s*[\d,]+\s*(?:USD|CAD|GBP|EUR)?',  # 50000 - 70000 USD
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None


def parse_posting_date(date_text: str) -> Optional[str]:
    """
    Parse job posting date text into ISO format.
    
    Args:
        date_text: Date text like "2 days ago", "Just posted", etc.
        
    Returns:
        ISO format date string or None
    """
    if not date_text:
        return None
    
    date_text = date_text.lower().strip()
    
    # Handle relative dates
    if "just" in date_text or "today" in date_text:
        return datetime.now().strftime("%Y-%m-%d")
    
    # Extract number and unit
    match = re.search(r'(\d+)\s+(day|week|month|hour)', date_text)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        
        from datetime import timedelta
        now = datetime.now()
        
        if unit == "day":
            date = now - timedelta(days=amount)
        elif unit == "week":
            date = now - timedelta(weeks=amount)
        elif unit == "month":
            date = now - timedelta(days=amount * 30)
        elif unit == "hour":
            date = now - timedelta(hours=amount)
        else:
            return None
        
        return date.strftime("%Y-%m-%d")
    
    return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be used as a filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename.strip()


def format_job_data(job: dict) -> dict:
    """
    Format and clean job data for export.
    
    Args:
        job: Raw job data dictionary
        
    Returns:
        Formatted job data
    """
    formatted = {}
    
    # Clean text fields
    text_fields = ["title", "company", "location", "description", "requirements"]
    for field in text_fields:
        if field in job:
            formatted[field] = clean_text(job[field])
    
    # Copy other fields
    for key, value in job.items():
        if key not in formatted:
            formatted[key] = value
    
    # Add scrape timestamp
    formatted["scraped_at"] = datetime.now().isoformat()
    
    return formatted


def chunk_list(lst: list, chunk_size: int):
    """
    Split a list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Yields:
        Chunks of the list
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries
        base_delay: Base delay between retries
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
            
            return None
        
        return wrapper
    return decorator