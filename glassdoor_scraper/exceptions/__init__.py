"""Exceptions module for Glassdoor Scraper."""

from .custom_exceptions import (
    ScraperException,
    CaptchaDetectedException,
    RateLimitException,
    AccessBlockedException,
    ParseException,
    ProxyException,
    TimeoutException,
    ValidationException,
)

__all__ = [
    "ScraperException",
    "CaptchaDetectedException",
    "RateLimitException",
    "AccessBlockedException",
    "ParseException",
    "ProxyException",
    "TimeoutException",
    "ValidationException",
]