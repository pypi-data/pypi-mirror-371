"""Navigation handler for chrome_navigate tool."""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

class NavigationHandler:
    """Handles navigation operations with chrome_navigate tool."""
    
    def __init__(self, chrome_manager):
        self.chrome_manager = chrome_manager
    
    async def navigate(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to a URL with anti-detection capabilities.
        
        Args:
            arguments: Tool arguments containing url, timeout, allowDangerous, launchOptions
            
        Returns:
            Navigation result with success status, url, title, and load time
        """
        url = arguments.get('url')
        timeout = arguments.get('timeout', 30000) / 1000  # Convert to seconds
        allow_dangerous = arguments.get('allowDangerous', False)
        launch_options = arguments.get('launchOptions')
        
        if not url:
            raise ValueError("URL is required for navigation")
        
        logger.info(f"Navigating to: {url}")
        start_time = time.time()
        
        try:
            # Get driver with custom options if provided
            driver = await self.chrome_manager.get_driver(launch_options)
            
            # Set page load timeout
            await asyncio.get_event_loop().run_in_executor(
                None, driver.set_page_load_timeout, timeout
            )
            
            # Navigate to URL
            await asyncio.get_event_loop().run_in_executor(
                None, driver.get, url
            )
            
            # Add human-like delay
            self.chrome_manager._human_like_delay(0.5, 1.5)
            
            # Get final URL and title
            final_url = await asyncio.get_event_loop().run_in_executor(
                None, lambda: driver.current_url
            )
            
            title = await asyncio.get_event_loop().run_in_executor(
                None, lambda: driver.title
            )
            
            load_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            result = {
                "success": True,
                "url": final_url,
                "title": title,
                "loadTime": load_time
            }
            
            logger.info(f"Navigation successful: {final_url} (loaded in {load_time}ms)")
            return result
            
        except TimeoutException:
            error_msg = f"Navigation timeout after {timeout}s for URL: {url}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "url": url,
                "loadTime": int((time.time() - start_time) * 1000)
            }
            
        except WebDriverException as e:
            error_msg = f"WebDriver error during navigation: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "url": url,
                "loadTime": int((time.time() - start_time) * 1000)
            }
            
        except Exception as e:
            error_msg = f"Unexpected error during navigation: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "url": url,
                "loadTime": int((time.time() - start_time) * 1000)
            }