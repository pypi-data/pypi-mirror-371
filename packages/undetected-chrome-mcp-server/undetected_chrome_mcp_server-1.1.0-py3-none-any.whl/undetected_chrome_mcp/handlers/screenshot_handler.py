"""Screenshot handler for chrome_screenshot tool."""

import asyncio
import base64
import logging
import os
import tempfile
from typing import Any, Dict, Optional

from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from PIL import Image
import io

logger = logging.getLogger(__name__)

class ScreenshotHandler:
    """Handles screenshot operations with chrome_screenshot tool."""
    
    def __init__(self, chrome_manager):
        self.chrome_manager = chrome_manager
    
    async def screenshot(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Capture a screenshot of the page or specific element.
        
        Args:
            arguments: Tool arguments containing name, selector, encoded, width, height, fullPage
            
        Returns:
            Screenshot result with success status, path/data, and dimensions
        """
        name = arguments.get('name')
        selector = arguments.get('selector')
        encoded = arguments.get('encoded', False)
        width = arguments.get('width')
        height = arguments.get('height')
        full_page = arguments.get('fullPage', False)
        
        if not name:
            raise ValueError("Screenshot name is required")
        
        logger.info(f"Taking screenshot: {name}")
        
        try:
            driver = await self.chrome_manager.get_driver()
            
            # Set viewport size if specified
            if width and height:
                await asyncio.get_event_loop().run_in_executor(
                    None, driver.set_window_size, width, height
                )
            
            screenshot_data = None
            dimensions = {}
            
            if selector:
                # Element-specific screenshot
                try:
                    element = await self.chrome_manager.wait_for_element(selector, timeout=10)
                    screenshot_data = await asyncio.get_event_loop().run_in_executor(
                        None, element.screenshot_as_png
                    )
                    
                    # Get element dimensions
                    size = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: element.size
                    )
                    dimensions = {"width": size['width'], "height": size['height']}
                    
                except NoSuchElementException:
                    return {
                        "success": False,
                        "error": f"Element not found: {selector}"
                    }
                    
            else:
                # Full page or viewport screenshot
                if full_page:
                    # Get full page dimensions
                    script = """
                    return {
                        width: Math.max(document.body.scrollWidth, document.documentElement.scrollWidth),
                        height: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
                    };
                    """
                    page_size = await self.chrome_manager.execute_script(script)
                    
                    # Set window size to full page
                    await asyncio.get_event_loop().run_in_executor(
                        None, driver.set_window_size, page_size['width'], page_size['height']
                    )
                    
                    dimensions = page_size
                else:
                    # Get current viewport dimensions
                    viewport_size = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: driver.get_window_size()
                    )
                    dimensions = {"width": viewport_size['width'], "height": viewport_size['height']}
                
                # Take screenshot
                screenshot_data = await asyncio.get_event_loop().run_in_executor(
                    None, driver.get_screenshot_as_png
                )
            
            # Process screenshot data
            if encoded:
                # Return base64 encoded data
                encoded_data = base64.b64encode(screenshot_data).decode('utf-8')
                result = {
                    "success": True,
                    "data": f"data:image/png;base64,{encoded_data}",
                    "dimensions": dimensions
                }
            else:
                # Save to file
                filename = f"{name}.png" if not name.endswith('.png') else name
                temp_dir = tempfile.gettempdir()
                file_path = os.path.join(temp_dir, filename)
                
                await asyncio.get_event_loop().run_in_executor(
                    None, self._save_screenshot, screenshot_data, file_path
                )
                
                result = {
                    "success": True,
                    "path": file_path,
                    "dimensions": dimensions
                }
            
            logger.info(f"Screenshot captured successfully: {name}")
            return result
            
        except WebDriverException as e:
            error_msg = f"WebDriver error during screenshot: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
            
        except Exception as e:
            error_msg = f"Unexpected error during screenshot: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def _save_screenshot(self, screenshot_data: bytes, file_path: str):
        """Save screenshot data to file."""
        with open(file_path, 'wb') as f:
            f.write(screenshot_data)