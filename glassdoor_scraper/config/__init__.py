"""Configuration module for Glassdoor Scraper."""

from .settings import (
    ScraperConfig,
    DEFAULT_USER_AGENTS,
    VIEWPORT_SIZES,
    JOB_LISTING_SELECTORS,
    BLOCK_PATTERNS,
    ERROR_MESSAGES,
)

__all__ = [
    "ScraperConfig",
    "DEFAULT_USER_AGENTS",
    "VIEWPORT_SIZES",
    "JOB_LISTING_SELECTORS",
    "BLOCK_PATTERNS",
    "ERROR_MESSAGES",
]