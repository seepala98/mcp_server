"""Proxy management and rotation utilities."""

import random
import requests
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from urllib.parse import urlparse

from ..exceptions import ProxyException


@dataclass
class Proxy:
    """Represents a proxy server."""
    host: str
    port: int
    protocol: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    is_working: bool = True
    last_checked: Optional[float] = None
    response_time: Optional[float] = None
    
    @property
    def url(self) -> str:
        """Get the proxy URL."""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def dict_format(self) -> Dict[str, str]:
        """Get proxy in requests dictionary format."""
        return {
            "http": self.url,
            "https": self.url,
        }
    
    @classmethod
    def from_string(cls, proxy_string: str) -> "Proxy":
        """Create a Proxy from a string like 'http://user:pass@host:port' or 'host:port'."""
        try:
            if "://" in proxy_string:
                parsed = urlparse(proxy_string)
                protocol = parsed.scheme or "http"
                host = parsed.hostname
                port = parsed.port or 8080
                username = parsed.username
                password = parsed.password
            else:
                parts = proxy_string.split(":")
                host = parts[0]
                port = int(parts[1]) if len(parts) > 1 else 8080
                protocol = "http"
                username = None
                password = None
            
            return cls(
                host=host,
                port=port,
                protocol=protocol,
                username=username,
                password=password,
            )
        except Exception as e:
            raise ProxyException(f"Invalid proxy string: {proxy_string}") from e


class ProxyManager:
    """Manages a pool of proxies with rotation and health checking."""
    
    def __init__(self, proxies: Optional[List[str]] = None, check_proxies: bool = False):
        """
        Initialize the proxy manager.
        
        Args:
            proxies: List of proxy strings (optional)
            check_proxies: Whether to check proxy health on initialization
        """
        self.proxies: List[Proxy] = []
        self.current_index = 0
        
        if proxies:
            for proxy_str in proxies:
                try:
                    self.proxies.append(Proxy.from_string(proxy_str))
                except ProxyException:
                    continue
        
        if check_proxies and self.proxies:
            self.check_all_proxies()
    
    @classmethod
    def from_free_proxy_list(cls, limit: int = 10) -> "ProxyManager":
        """
        Fetch free proxies from free-proxy-list.net.
        
        Args:
            limit: Maximum number of proxies to fetch
            
        Returns:
            ProxyManager instance with free proxies
        """
        proxies = []
        try:
            url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                proxy_list = response.text.strip().split("\n")[:limit]
                proxies = [p.strip() for p in proxy_list if p.strip()]
        except Exception:
            pass
        
        return cls(proxies=proxies if proxies else None)
    
    def get_next_proxy(self) -> Optional[Proxy]:
        """Get the next proxy in rotation."""
        if not self.proxies:
            return None
        
        # Find next working proxy
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            if proxy.is_working:
                return proxy
            
            attempts += 1
        
        # If no working proxies, return None
        return None
    
    def get_random_proxy(self) -> Optional[Proxy]:
        """Get a random working proxy."""
        working_proxies = [p for p in self.proxies if p.is_working]
        if working_proxies:
            return random.choice(working_proxies)
        return None
    
    def check_proxy(self, proxy: Proxy, timeout: int = 10) -> bool:
        """
        Check if a proxy is working.
        
        Args:
            proxy: Proxy to check
            timeout: Request timeout in seconds
            
        Returns:
            True if proxy is working, False otherwise
        """
        try:
            start_time = time.time()
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxy.dict_format,
                timeout=timeout,
            )
            proxy.response_time = time.time() - start_time
            proxy.last_checked = time.time()
            proxy.is_working = response.status_code == 200
            return proxy.is_working
        except Exception:
            proxy.is_working = False
            proxy.last_checked = time.time()
            return False
    
    def check_all_proxies(self, timeout: int = 10) -> None:
        """Check health of all proxies."""
        print(f"Checking {len(self.proxies)} proxies...")
        working_count = 0
        
        for proxy in self.proxies:
            if self.check_proxy(proxy, timeout):
                working_count += 1
        
        print(f"Found {working_count} working proxies out of {len(self.proxies)}")
    
    def mark_proxy_failed(self, proxy: Proxy) -> None:
        """Mark a proxy as failed."""
        proxy.is_working = False
    
    def add_proxy(self, proxy_string: str) -> None:
        """Add a proxy to the pool."""
        try:
            proxy = Proxy.from_string(proxy_string)
            self.proxies.append(proxy)
        except ProxyException:
            pass
    
    def remove_proxy(self, proxy: Proxy) -> None:
        """Remove a proxy from the pool."""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
    
    @property
    def working_proxies_count(self) -> int:
        """Get the number of working proxies."""
        return len([p for p in self.proxies if p.is_working])
    
    @property
    def has_working_proxies(self) -> bool:
        """Check if there are any working proxies."""
        return any(p.is_working for p in self.proxies)