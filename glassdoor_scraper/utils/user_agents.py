"""User agent rotation utilities."""

import random
from typing import Optional
from fake_useragent import UserAgent as FakeUserAgent

from ..config import DEFAULT_USER_AGENTS


class UserAgentRotator:
    """Handles rotation of User-Agent strings."""
    
    def __init__(self, use_fake_useragent: bool = True):
        """
        Initialize the User-Agent rotator.
        
        Args:
            use_fake_useragent: Whether to use fake-useragent library for dynamic UAs
        """
        self.use_fake = use_fake_useragent
        self.fake_ua: Optional[FakeUserAgent] = None
        self.default_uas = DEFAULT_USER_AGENTS.copy()
        
        if use_fake_useragent:
            try:
                self.fake_ua = FakeUserAgent()
            except Exception:
                # Fallback to default list if fake-useragent fails
                self.fake_ua = None
    
    def get_random_ua(self) -> str:
        """
        Get a random User-Agent string.
        
        Returns:
            A random User-Agent string
        """
        if self.fake_ua:
            try:
                return self.fake_ua.random
            except Exception:
                pass
        
        return random.choice(self.default_uas)
    
    def get_chrome_ua(self) -> str:
        """Get a Chrome User-Agent."""
        chrome_uas = [ua for ua in self.default_uas if "Chrome" in ua and "Edg" not in ua]
        if chrome_uas:
            return random.choice(chrome_uas)
        return self.get_random_ua()
    
    def get_firefox_ua(self) -> str:
        """Get a Firefox User-Agent."""
        firefox_uas = [ua for ua in self.default_uas if "Firefox" in ua]
        if firefox_uas:
            return random.choice(firefox_uas)
        return self.get_random_ua()
    
    def get_safari_ua(self) -> str:
        """Get a Safari User-Agent."""
        safari_uas = [ua for ua in self.default_uas if "Safari" in ua and "Chrome" not in ua]
        if safari_uas:
            return random.choice(safari_uas)
        return self.get_random_ua()


# Global instance for convenience
_ua_rotator: Optional[UserAgentRotator] = None


def get_ua_rotator() -> UserAgentRotator:
    """Get the global User-Agent rotator instance."""
    global _ua_rotator
    if _ua_rotator is None:
        _ua_rotator = UserAgentRotator()
    return _ua_rotator