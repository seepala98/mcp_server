"""Custom exceptions for Glassdoor Scraper."""


class ScraperException(Exception):
    """Base exception for scraper errors."""
    pass


class CaptchaDetectedException(ScraperException):
    """Raised when CAPTCHA is detected."""
    pass


class RateLimitException(ScraperException):
    """Raised when rate limited by Glassdoor."""
    pass


class AccessBlockedException(ScraperException):
    """Raised when access is blocked."""
    pass


class ParseException(ScraperException):
    """Raised when parsing fails."""
    pass


class ProxyException(ScraperException):
    """Raised when proxy-related errors occur."""
    pass


class TimeoutException(ScraperException):
    """Raised when operations timeout."""
    pass


class ValidationException(ScraperException):
    """Raised when input validation fails."""
    pass