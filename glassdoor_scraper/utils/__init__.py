"""Utilities module for Glassdoor Scraper."""

from .user_agents import UserAgentRotator, get_ua_rotator
from .proxy_manager import ProxyManager, Proxy
from .helpers import (
    random_delay,
    get_random_viewport,
    human_like_delay,
    random_scroll_behavior,
    is_captcha_page,
    clean_text,
    extract_salary_range,
    parse_posting_date,
    sanitize_filename,
    format_job_data,
    chunk_list,
    retry_with_backoff,
)

__all__ = [
    "UserAgentRotator",
    "get_ua_rotator",
    "ProxyManager",
    "Proxy",
    "random_delay",
    "get_random_viewport",
    "human_like_delay",
    "random_scroll_behavior",
    "is_captcha_page",
    "clean_text",
    "extract_salary_range",
    "parse_posting_date",
    "sanitize_filename",
    "format_job_data",
    "chunk_list",
    "retry_with_backoff",
]