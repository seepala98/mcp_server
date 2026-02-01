"""Stealth browser management for Glassdoor scraping."""

import random
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from ..config import ScraperConfig, VIEWPORT_SIZES
from ..utils import UserAgentRotator, ProxyManager, get_random_viewport
from ..exceptions import CaptchaDetectedException, AccessBlockedException


class StealthBrowser:
    """Manages a stealth browser instance with anti-detection features."""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize the stealth browser.
        
        Args:
            config: Scraper configuration
        """
        self.config = config or ScraperConfig()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.ua_rotator = UserAgentRotator()
        self.proxy_manager: Optional[ProxyManager] = None
        
        if self.config.use_proxies and self.config.proxy_list:
            self.proxy_manager = ProxyManager(self.config.proxy_list)
    
    def start(self) -> "StealthBrowser":
        """
        Start the browser with stealth settings.
        
        Returns:
            Self for method chaining
        """
        self.playwright = sync_playwright().start()
        
        # Browser launch options with additional stealth
        launch_options = {
            "headless": self.config.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-accelerated-2d-canvas",
                "--disable-gpu",
                "--window-size=1920,1080",
                "--start-maximized",
                "--hide-scrollbars",
                "--disable-notifications",
                "--disable-extensions",
                "--force-color-profile=srgb",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-breakpad",
                "--disable-component-extensions-with-background-pages",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--disable-renderer-backgrounding",
                "--enable-features=NetworkService,NetworkServiceInProcess",
                "--force-webrtc-ip-handling-policy=default_public_interface_only",
                "--metrics-recording-only",
                "--mute-audio",
            ]
        }
        
        # Add proxy if configured
        if self.proxy_manager:
            proxy = self.proxy_manager.get_random_proxy()
            if proxy:
                launch_options["proxy"] = {
                    "server": proxy.url,
                }
        
        # Launch browser
        browser_type = getattr(self.playwright, self.config.browser_type)
        self.browser = browser_type.launch(**launch_options)
        
        # Create context with stealth settings
        context_options = self._get_context_options()
        self.context = self.browser.new_context(**context_options)
        
        # Apply stealth scripts
        self._apply_stealth_scripts()
        
        # Add additional evasion scripts
        self._apply_advanced_stealth()
        
        # Create page
        self.page = self.context.new_page()
        
        # Set timeouts
        self.page.set_default_timeout(self.config.page_load_timeout * 1000)
        self.page.set_default_navigation_timeout(self.config.navigation_timeout * 1000)
        
        return self
    
    def _get_context_options(self) -> Dict[str, Any]:
        """Get browser context options with stealth settings."""
        # Random viewport
        if self.config.randomize_viewport:
            viewport_width, viewport_height = get_random_viewport()
        else:
            viewport_width, viewport_height = self.config.viewport_width, self.config.viewport_height
        
        # Random user agent
        user_agent = self.ua_rotator.get_random_ua() if self.config.rotate_user_agents else None
        
        context_options = {
            "viewport": {"width": viewport_width, "height": viewport_height},
            "screen": {"width": viewport_width, "height": viewport_height},
            "device_scale_factor": random.choice([1, 1.25, 1.5, 2]),
            "locale": random.choice(["en-US", "en-GB", "en-CA"]),
            "timezone_id": random.choice([
                "America/New_York", "America/Chicago", "America/Denver", 
                "America/Los_Angeles", "Europe/London"
            ]),
            "geolocation": None,
            "permissions": [],
            "color_scheme": random.choice(["light", "dark"]),
        }
        
        if user_agent:
            context_options["user_agent"] = user_agent
        
        return context_options
    
    def _apply_stealth_scripts(self) -> None:
        """Apply stealth scripts to avoid detection."""
        # Override navigator.webdriver
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Override plugins
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    }
                ]
            });
        """)
        
        # Override languages
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        # Override permissions
        self.context.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        # Override webdriver property more thoroughly
        self.context.add_init_script("""
            delete Object.getPrototypeOf(navigator).webdriver;
        """)
        
        # Add Chrome runtime
        self.context.add_init_script("""
            window.chrome = {
                runtime: {
                    OnInstalledReason: {CHROME_UPDATE: "chrome_update"},
                    OnRestartRequiredReason: {APP_UPDATE: "app_update"},
                    PlatformArch: {ARM: "arm"},
                    PlatformNaclArch: {ARM: "arm"},
                    PlatformOs: {ANDROID: "android"},
                    RequestUpdateCheckStatus: {NO_UPDATE: "no_update"},
                }
            };
        """)
    
    def _apply_advanced_stealth(self) -> None:
        """Apply advanced stealth techniques."""
        # Override iframe sandbox
        self.context.add_init_script("""
            // Override toString to hide automation
            const originalToString = Function.prototype.toString;
            Function.prototype.toString = function() {
                if (this === window.navigator.permissions.query) {
                    return 'function query() { [native code] }';
                }
                if (this === window.navigator.webdriver) {
                    return 'undefined';
                }
                return originalToString.call(this);
            };
        """)
        
        # Add notification permission
        self.context.add_init_script("""
            if (!window.Notification) {
                window.Notification = {
                    permission: 'default',
                    requestPermission: function() {
                        return Promise.resolve('default');
                    }
                };
            }
        """)
        
        # Override console
        self.context.add_init_script("""
            window.console.debug = window.console.log;
        """)
        
        # Add missing permissions
        self.context.add_init_script("""
            if (!navigator.permissions) {
                navigator.permissions = {};
            }
            if (!navigator.permissions.query) {
                navigator.permissions.query = function() {
                    return Promise.resolve({state: 'prompt'});
                };
            }
        """)
        
        # Override device memory
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
        """)
        
        # Override hardware concurrency
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 4
            });
        """)
    
    def navigate(self, url: str, wait_until: str = "domcontentloaded", timeout: Optional[int] = None) -> None:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete
            timeout: Navigation timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        try:
            self.page.goto(
                url, 
                wait_until=wait_until,
                timeout=timeout or self.config.navigation_timeout * 1000
            )
        except Exception as e:
            # If domcontentloaded fails, try with load event
            if "timeout" in str(e).lower():
                print(f"  ⚠ Navigation timeout, retrying with shorter wait...")
                self.page.goto(url, wait_until="load", timeout=20000)
        
        # Check for CAPTCHA/block
        self._check_for_blocks()
    
    def _check_for_blocks(self) -> None:
        """Check if the page is blocked or requires CAPTCHA."""
        if not self.page:
            return
        
        content = self.page.content().lower()
        
        # Check for block patterns
        from ..config import BLOCK_PATTERNS
        for pattern in BLOCK_PATTERNS:
            if pattern in content:
                if "captcha" in pattern or "challenge" in pattern:
                    raise CaptchaDetectedException(f"CAPTCHA detected: {pattern}")
                else:
                    raise AccessBlockedException(f"Access blocked: {pattern}")
    
    def scroll_page(self, amount: Optional[int] = None, smooth: bool = True) -> None:
        """
        Scroll the page.
        
        Args:
            amount: Amount to scroll (random if None)
            smooth: Whether to scroll smoothly
        """
        if not self.page:
            return
        
        if amount is None:
            amount = random.randint(300, 800)
        
        behavior = "smooth" if smooth else "auto"
        
        self.page.evaluate(f"""
            window.scrollBy({{
                top: {amount},
                behavior: '{behavior}'
            }});
        """)
    
    def random_scroll(self) -> None:
        """Perform random scrolling behavior."""
        from ..utils import random_scroll_behavior
        
        behavior = random_scroll_behavior()
        
        for _ in range(behavior["steps"]):
            self.scroll_page(behavior["amount"])
            random_delay(behavior["delay"] * 0.5, behavior["delay"] * 1.5)
    
    def click(self, selector: str, delay: Optional[float] = None) -> None:
        """
        Click an element with human-like delay.
        
        Args:
            selector: CSS selector for the element
            delay: Delay before clicking (random if None)
        """
        if not self.page:
            return
        
        if delay is None:
            delay = random.uniform(0.1, 0.5)
        
        import time
        time.sleep(delay)
        
        self.page.click(selector)
    
    def type_text(self, selector: str, text: str, delay: Optional[float] = None) -> None:
        """
        Type text into an element with human-like delay.
        
        Args:
            selector: CSS selector for the element
            text: Text to type
            delay: Delay between keystrokes (random if None)
        """
        if not self.page:
            return
        
        if delay is None:
            delay = random.uniform(0.05, 0.15)
        
        self.page.fill(selector, "")
        
        for char in text:
            self.page.type(selector, char, delay=delay)
    
    def get_page_content(self) -> str:
        """Get the current page HTML content."""
        if not self.page:
            return ""
        return self.page.content()
    
    def get_page_text(self) -> str:
        """Get the current page text content."""
        if not self.page:
            return ""
        return self.page.inner_text("body")
    
    def screenshot(self, path: str) -> None:
        """
        Take a screenshot of the current page.
        
        Args:
            path: Path to save the screenshot
        """
        if self.page:
            self.page.screenshot(path=path, full_page=True)
    
    def close(self) -> None:
        """Close the browser and cleanup."""
        if self.context:
            self.context.close()
            self.context = None
        
        if self.browser:
            self.browser.close()
            self.browser = None
        
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
    
    def __enter__(self) -> "StealthBrowser":
        """Context manager entry."""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


def random_delay(min_seconds: float, max_seconds: float) -> None:
    """Sleep for a random amount of time."""
    import time
    time.sleep(random.uniform(min_seconds, max_seconds))