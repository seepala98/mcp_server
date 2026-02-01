"""Glassdoor Job Scraper - A robust scraper with anti-bot protection."""

__version__ = "1.0.0"
__author__ = "Glassdoor Scraper"

from .core import GlassdoorScraper, scrape_jobs, StealthBrowser, JobDataExtractor
from .config import ScraperConfig
from .exceptions import (
    ScraperException,
    CaptchaDetectedException,
    RateLimitException,
    AccessBlockedException,
)
from .storage import DataExporter

__all__ = [
    "GlassdoorScraper",
    "scrape_jobs",
    "StealthBrowser",
    "JobDataExtractor",
    "ScraperConfig",
    "DataExporter",
    "ScraperException",
    "CaptchaDetectedException",
    "RateLimitException",
    "AccessBlockedException",
]