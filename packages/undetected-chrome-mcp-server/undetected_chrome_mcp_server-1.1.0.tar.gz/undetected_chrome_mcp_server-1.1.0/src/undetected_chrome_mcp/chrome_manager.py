"""Chrome driver management with undetected-chromedriver and anti-detection capabilities."""

import asyncio
import json
import logging
import os
import random
import threading
import time
from typing import Any, Dict, List, Optional, Callable

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
        
        # Network monitoring state
        self.network_monitoring = False
        self.network_requests: List[Dict[str, Any]] = []
        self.network_responses: List[Dict[str, Any]] = []
        self.network_lock = threading.Lock()
        self.max_network_entries = int(os.getenv('CHROME_MAX_NETWORK_ENTRIES', '1000'))
        
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
            
            # Create undetected Chrome driver with CDP events enabled for network monitoring
            driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect
                use_subprocess=True,
                headless=True if "--headless" in str(options.arguments) else False,
                enable_cdp_events=True  # Enable CDP for network monitoring
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
    
    # Network monitoring methods
    def _network_request_handler(self, message):
        """Handle Network.requestWillBeSent events."""
        try:
            # Debug: Log the actual message structure
            logger.info(f"CDP Network Request Event: {message}")
            
            with self.network_lock:
                if len(self.network_requests) >= self.max_network_entries:
                    self.network_requests.pop(0)  # Remove oldest
                
                # Handle different message structures
                if isinstance(message, dict) and 'params' in message:
                    # Standard CDP format
                    params = message['params']
                    request_data = {
                        'requestId': params.get('requestId'),
                        'url': params.get('request', {}).get('url'),
                        'method': params.get('request', {}).get('method'),
                        'headers': params.get('request', {}).get('headers', {}),
                        'timestamp': params.get('timestamp'),
                        'type': params.get('type'),
                        'postData': params.get('request', {}).get('postData')
                    }
                else:
                    # Direct format (undetected-chromedriver specific)
                    request_data = {
                        'requestId': message.get('requestId'),
                        'url': message.get('request', {}).get('url') if message.get('request') else message.get('url'),
                        'method': message.get('request', {}).get('method') if message.get('request') else message.get('method'),
                        'headers': message.get('request', {}).get('headers', {}) if message.get('request') else message.get('headers', {}),
                        'timestamp': message.get('timestamp'),
                        'type': message.get('type'),
                        'postData': message.get('request', {}).get('postData') if message.get('request') else message.get('postData')
                    }
                
                self.network_requests.append(request_data)
                logger.debug(f"Network request captured: {request_data['method']} {request_data['url']}")
        except Exception as e:
            logger.warning(f"Error handling network request: {e}")
    
    def _network_response_handler(self, message):
        """Handle Network.responseReceived events."""
        try:
            # Debug: Log the actual message structure
            logger.info(f"CDP Network Response Event: {message}")
            
            with self.network_lock:
                if len(self.network_responses) >= self.max_network_entries:
                    self.network_responses.pop(0)  # Remove oldest
                
                # Handle different message structures
                if isinstance(message, dict) and 'params' in message:
                    # Standard CDP format
                    params = message['params']
                    response_data = {
                        'requestId': params.get('requestId'),
                        'url': params.get('response', {}).get('url'),
                        'status': params.get('response', {}).get('status'),
                        'statusText': params.get('response', {}).get('statusText'),
                        'headers': params.get('response', {}).get('headers', {}),
                        'mimeType': params.get('response', {}).get('mimeType'),
                        'timestamp': params.get('timestamp'),
                        'type': params.get('type')
                    }
                else:
                    # Direct format (undetected-chromedriver specific)
                    response_data = {
                        'requestId': message.get('requestId'),
                        'url': message.get('response', {}).get('url') if message.get('response') else message.get('url'),
                        'status': message.get('response', {}).get('status') if message.get('response') else message.get('status'),
                        'statusText': message.get('response', {}).get('statusText') if message.get('response') else message.get('statusText'),
                        'headers': message.get('response', {}).get('headers', {}) if message.get('response') else message.get('headers', {}),
                        'mimeType': message.get('response', {}).get('mimeType') if message.get('response') else message.get('mimeType'),
                        'timestamp': message.get('timestamp'),
                        'type': message.get('type')
                    }
                
                self.network_responses.append(response_data)
                logger.debug(f"Network response captured: {response_data['status']} {response_data['url']}")
        except Exception as e:
            logger.warning(f"Error handling network response: {e}")
    
    async def start_network_monitoring(self) -> bool:
        """Start monitoring network traffic using Chrome DevTools Protocol."""
        if self.network_monitoring:
            return True
        
        try:
            driver = await self.get_driver()
            
            # Enable Network domain
            await asyncio.get_event_loop().run_in_executor(
                None, driver.execute_cdp_cmd, 'Network.enable', {}
            )
            
            # Add event listeners
            await asyncio.get_event_loop().run_in_executor(
                None, driver.add_cdp_listener, 'Network.requestWillBeSent', self._network_request_handler
            )
            await asyncio.get_event_loop().run_in_executor(
                None, driver.add_cdp_listener, 'Network.responseReceived', self._network_response_handler
            )
            
            self.network_monitoring = True
            logger.info("Network monitoring started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start network monitoring: {e}")
            return False
    
    async def stop_network_monitoring(self) -> bool:
        """Stop monitoring network traffic."""
        if not self.network_monitoring:
            return True
        
        try:
            driver = await self.get_driver()
            
            # Disable Network domain
            await asyncio.get_event_loop().run_in_executor(
                None, driver.execute_cdp_cmd, 'Network.disable', {}
            )
            
            self.network_monitoring = False
            logger.info("Network monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop network monitoring: {e}")
            return False
    
    def clear_network_data(self):
        """Clear all captured network data."""
        with self.network_lock:
            self.network_requests.clear()
            self.network_responses.clear()
        logger.info("Network data cleared")
    
    def get_network_requests(self, url_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get captured network requests, optionally filtered by URL pattern."""
        with self.network_lock:
            if url_filter:
                return [req for req in self.network_requests if url_filter.lower() in req.get('url', '').lower()]
            return self.network_requests.copy()
    
    def get_network_responses(self, url_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get captured network responses, optionally filtered by URL pattern."""
        with self.network_lock:
            if url_filter:
                return [resp for resp in self.network_responses if url_filter.lower() in resp.get('url', '').lower()]
            return self.network_responses.copy()
    
    async def get_response_body(self, request_id: str) -> Optional[str]:
        """Get response body for a specific request ID."""
        if not self.network_monitoring:
            logger.warning("Network monitoring is not enabled")
            return None
        
        try:
            driver = await self.get_driver()
            result = await asyncio.get_event_loop().run_in_executor(
                None, driver.execute_cdp_cmd, 'Network.getResponseBody', {'requestId': request_id}
            )
            return result.get('body')
        except Exception as e:
            logger.warning(f"Failed to get response body for request {request_id}: {e}")
            return None
    
    def get_network_summary(self) -> Dict[str, Any]:
        """Get summary of captured network activity."""
        with self.network_lock:
            requests_by_type = {}
            responses_by_status = {}
            
            for req in self.network_requests:
                req_type = req.get('type', 'unknown')
                requests_by_type[req_type] = requests_by_type.get(req_type, 0) + 1
            
            for resp in self.network_responses:
                status = resp.get('status', 0)
                status_group = f"{status // 100}xx"
                responses_by_status[status_group] = responses_by_status.get(status_group, 0) + 1
            
            return {
                'monitoring_active': self.network_monitoring,
                'total_requests': len(self.network_requests),
                'total_responses': len(self.network_responses),
                'requests_by_type': requests_by_type,
                'responses_by_status': responses_by_status,
                'max_entries': self.max_network_entries
            }