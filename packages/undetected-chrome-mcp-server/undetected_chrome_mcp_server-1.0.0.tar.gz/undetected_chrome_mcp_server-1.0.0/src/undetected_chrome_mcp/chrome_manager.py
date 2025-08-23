"""Chrome driver management with undetected-chromedriver and anti-detection capabilities."""

import asyncio
import logging
import os
import random
import time
from typing import Any, Dict, Optional

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    WebDriverException,
    NoSuchElementException,
    StaleElementReferenceException
)

logger = logging.getLogger(__name__)

class ChromeManager:
    """Manages Chrome driver instances with anti-detection capabilities."""
    
    def __init__(self):
        self.driver: Optional[uc.Chrome] = None
        self.session_timeout = int(os.getenv('CHROME_SESSION_TIMEOUT', '300'))
        self.max_sessions = int(os.getenv('CHROME_MAX_SESSIONS', '5'))
        self.last_activity = time.time()
        
        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebDriver/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ]
    
    def _get_chrome_options(self, custom_options: Optional[Dict[str, Any]] = None) -> Options:
        """Configure Chrome options with anti-detection settings."""
        options = uc.ChromeOptions()
        
        # Basic stealth arguments
        stealth_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage", 
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-default-apps",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-default-apps",
            "--disable-extensions",
            "--no-default-browser-check",
            "--no-first-run"
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        options.add_argument(f"--user-agent={user_agent}")
        
        # Random window size for fingerprint variation
        width = random.randint(1024, 1920)
        height = random.randint(768, 1080)
        options.add_argument(f"--window-size={width},{height}")
        
        # Apply custom options if provided
        if custom_options:
            if custom_options.get('headless'):
                options.add_argument("--headless=new")
            
            # Add custom arguments
            if 'args' in custom_options:
                for arg in custom_options['args']:
                    options.add_argument(arg)
        else:
            # Default to headless
            options.add_argument("--headless=new")
        
        return options
    
    async def get_driver(self, custom_options: Optional[Dict[str, Any]] = None) -> uc.Chrome:
        """Get Chrome driver with anti-detection capabilities."""
        # Check if we need to create a new driver
        if self.driver is None or self._should_refresh_session():
            await self._create_new_driver(custom_options)
        
        self.last_activity = time.time()
        return self.driver
    
    def _should_refresh_session(self) -> bool:
        """Determine if we should refresh the current session."""
        if self.driver is None:
            return True
        
        # Check if session is too old
        if time.time() - self.last_activity > self.session_timeout:
            logger.info("Session timeout reached, refreshing driver")
            return True
        
        # Check if driver is still responsive
        try:
            self.driver.current_url
            return False
        except Exception:
            logger.warning("Driver unresponsive, creating new session")
            return True
    
    async def _create_new_driver(self, custom_options: Optional[Dict[str, Any]] = None):
        """Create a new undetected Chrome driver instance."""
        # Clean up existing driver
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
        
        # Run driver creation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        self.driver = await loop.run_in_executor(None, self._create_driver_sync, custom_options)
        
        logger.info("Created new undetected Chrome driver")
    
    def _create_driver_sync(self, custom_options: Optional[Dict[str, Any]] = None) -> uc.Chrome:
        """Synchronous driver creation."""
        options = self._get_chrome_options(custom_options)
        
        # Get custom Chrome executable path if set
        chrome_executable = os.getenv('CHROME_EXECUTABLE_PATH')
        
        try:
            if chrome_executable and os.path.exists(chrome_executable):
                options.binary_location = chrome_executable
                logger.info(f"Using custom Chrome executable: {chrome_executable}")
            
            # Create undetected Chrome driver
            driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect
                use_subprocess=True,
                headless=True if "--headless" in str(options.arguments) else False
            )
            
            # Configure timeouts
            driver.implicitly_wait(10)
            driver.set_page_load_timeout(30)
            
            # Apply additional anti-detection measures
            self._apply_stealth_scripts(driver)
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            raise
    
    def _apply_stealth_scripts(self, driver: uc.Chrome):
        """Apply additional JavaScript-based stealth measures."""
        stealth_script = """
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Mock chrome object
        window.chrome = {
            runtime: {},
            loadTimes: function() {
                return {
                    connectionInfo: 'http/1.1',
                    finishDocumentLoadTime: Date.now(),
                    finishLoadTime: Date.now(),
                    firstPaintAfterLoadTime: 0,
                    firstPaintTime: Date.now(),
                    navigationType: 'Other',
                    npnNegotiatedProtocol: 'unknown',
                    requestTime: Date.now() - 1000,
                    startLoadTime: Date.now() - 1000,
                    wasAlternateProtocolAvailable: false,
                    wasFetchedViaSpdy: false,
                    wasNpnNegotiated: false
                };
            },
            csi: function() {
                return {
                    onloadT: Date.now(),
                    pageT: Date.now() - 1000,
                    startE: Date.now() - 1000,
                    tran: 15
                };
            }
        };
        
        // Mock plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """
        
        try:
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': stealth_script
            })
        except Exception as e:
            logger.warning(f"Could not apply stealth scripts: {e}")
    
    def _human_like_delay(self, min_delay: float = 0.1, max_delay: float = 0.5):
        """Add human-like delays between actions."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    async def wait_for_element(
        self, 
        selector: str, 
        timeout: int = 10, 
        condition: str = "presence"
    ) -> Any:
        """Wait for element with specified condition."""
        driver = await self.get_driver()
        wait = WebDriverWait(driver, timeout)
        
        conditions = {
            "presence": EC.presence_of_element_located((By.CSS_SELECTOR, selector)),
            "clickable": EC.element_to_be_clickable((By.CSS_SELECTOR, selector)),
            "visible": EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
        }
        
        if condition not in conditions:
            raise ValueError(f"Unknown condition: {condition}")
        
        return await asyncio.get_event_loop().run_in_executor(
            None, wait.until, conditions[condition]
        )
    
    async def find_element(self, selector: str) -> Any:
        """Find element by CSS selector."""
        driver = await self.get_driver()
        return await asyncio.get_event_loop().run_in_executor(
            None, driver.find_element, By.CSS_SELECTOR, selector
        )
    
    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript and return result."""
        driver = await self.get_driver()
        return await asyncio.get_event_loop().run_in_executor(
            None, driver.execute_script, script
        )
    
    async def cleanup(self):
        """Clean up Chrome driver resources."""
        if self.driver:
            try:
                await asyncio.get_event_loop().run_in_executor(None, self.driver.quit)
                logger.info("Chrome driver cleaned up successfully")
            except Exception as e:
                logger.error(f"Error cleaning up Chrome driver: {e}")
            finally:
                self.driver = None