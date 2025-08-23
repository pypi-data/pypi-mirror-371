"""Interaction handler for chrome_click, chrome_fill, chrome_select, chrome_hover tools."""

import asyncio
import logging
from typing import Any, Dict, Optional

from selenium.common.exceptions import (
    NoSuchElementException, 
    ElementNotInteractableException,
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

logger = logging.getLogger(__name__)

class InteractionHandler:
    """Handles interaction operations with page elements."""
    
    def __init__(self, chrome_manager):
        self.chrome_manager = chrome_manager
    
    async def click(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Click an element on the page.
        
        Args:
            arguments: Tool arguments containing selector and timeout
            
        Returns:
            Click result with success status and element info
        """
        selector = arguments.get('selector')
        timeout = arguments.get('timeout', 10000) / 1000  # Convert to seconds
        
        if not selector:
            raise ValueError("Selector is required for click operation")
        
        logger.info(f"Clicking element: {selector}")
        
        try:
            # Wait for element to be clickable
            element = await self.chrome_manager.wait_for_element(
                selector, timeout=int(timeout), condition="clickable"
            )
            
            # Add human-like delay
            self.chrome_manager._human_like_delay(0.1, 0.3)
            
            # Perform click
            await asyncio.get_event_loop().run_in_executor(
                None, element.click
            )
            
            # Get element info
            element_info = await self._get_element_info(element)
            
            result = {
                "success": True,
                "element": element_info
            }
            
            logger.info(f"Click successful: {selector}")
            return result
            
        except TimeoutException:
            error_msg = f"Element not clickable within {timeout}s: {selector}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
            
        except (NoSuchElementException, ElementNotInteractableException) as e:
            error_msg = f"Element interaction failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
            
        except Exception as e:
            error_msg = f"Unexpected error during click: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def fill(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Fill an input field with text.
        
        Args:
            arguments: Tool arguments containing selector, value, and clear option
            
        Returns:
            Fill result with success status and final value
        """
        selector = arguments.get('selector')
        value = arguments.get('value')
        clear = arguments.get('clear', True)
        
        if not selector or value is None:
            raise ValueError("Selector and value are required for fill operation")
        
        logger.info(f"Filling input: {selector} with value: {value}")
        
        try:
            # Wait for element to be present
            element = await self.chrome_manager.wait_for_element(
                selector, timeout=10, condition="presence"
            )
            
            # Clear field if requested
            if clear:
                await asyncio.get_event_loop().run_in_executor(
                    None, element.clear
                )
            
            # Add human-like delay
            self.chrome_manager._human_like_delay(0.1, 0.3)
            
            # Send keys with human-like typing
            await self._type_text(element, str(value))
            
            # Get final value
            final_value = await asyncio.get_event_loop().run_in_executor(
                None, lambda: element.get_attribute('value')
            )
            
            result = {
                "success": True,
                "value": final_value
            }
            
            logger.info(f"Fill successful: {selector}")
            return result
            
        except (NoSuchElementException, ElementNotInteractableException) as e:
            error_msg = f"Element fill failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
            
        except Exception as e:
            error_msg = f"Unexpected error during fill: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def select(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Select an option from a dropdown.
        
        Args:
            arguments: Tool arguments containing selector and value
            
        Returns:
            Selection result with success status and selected value
        """
        selector = arguments.get('selector')
        value = arguments.get('value')
        
        if not selector or value is None:
            raise ValueError("Selector and value are required for select operation")
        
        logger.info(f"Selecting option: {value} from {selector}")
        
        try:
            # Wait for select element
            element = await self.chrome_manager.wait_for_element(
                selector, timeout=10, condition="presence"
            )
            
            # Create Select object and select by value
            select_obj = Select(element)
            await asyncio.get_event_loop().run_in_executor(
                None, select_obj.select_by_value, str(value)
            )
            
            # Add human-like delay
            self.chrome_manager._human_like_delay(0.1, 0.3)
            
            # Get selected value
            selected_value = await asyncio.get_event_loop().run_in_executor(
                None, lambda: select_obj.first_selected_option.get_attribute('value')
            )
            
            result = {
                "success": True,
                "selectedValue": selected_value
            }
            
            logger.info(f"Selection successful: {selector}")
            return result
            
        except (NoSuchElementException, ElementNotInteractableException) as e:
            error_msg = f"Element selection failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
            
        except Exception as e:
            error_msg = f"Unexpected error during selection: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def hover(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Hover over an element.
        
        Args:
            arguments: Tool arguments containing selector
            
        Returns:
            Hover result with success status and element info
        """
        selector = arguments.get('selector')
        
        if not selector:
            raise ValueError("Selector is required for hover operation")
        
        logger.info(f"Hovering over element: {selector}")
        
        try:
            driver = await self.chrome_manager.get_driver()
            
            # Wait for element
            element = await self.chrome_manager.wait_for_element(
                selector, timeout=10, condition="presence"
            )
            
            # Perform hover
            actions = ActionChains(driver)
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: actions.move_to_element(element).perform()
            )
            
            # Add human-like delay
            self.chrome_manager._human_like_delay(0.1, 0.3)
            
            # Get element info
            element_info = await self._get_element_info(element)
            
            result = {
                "success": True,
                "element": element_info
            }
            
            logger.info(f"Hover successful: {selector}")
            return result
            
        except (NoSuchElementException, ElementNotInteractableException) as e:
            error_msg = f"Element hover failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
            
        except Exception as e:
            error_msg = f"Unexpected error during hover: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _type_text(self, element, text: str):
        """Type text with human-like delays."""
        for char in text:
            await asyncio.get_event_loop().run_in_executor(
                None, element.send_keys, char
            )
            # Small delay between keystrokes
            import time
            time.sleep(0.02 + (0.01 * (0.5 - 1.0)) * 2)  # 20-30ms delay
    
    async def _get_element_info(self, element) -> Dict[str, Any]:
        """Get information about an element."""
        try:
            tag_name = await asyncio.get_event_loop().run_in_executor(
                None, lambda: element.tag_name
            )
            
            text = await asyncio.get_event_loop().run_in_executor(
                None, lambda: element.text
            )
            
            size = await asyncio.get_event_loop().run_in_executor(
                None, lambda: element.size
            )
            
            location = await asyncio.get_event_loop().run_in_executor(
                None, lambda: element.location
            )
            
            return {
                "tagName": tag_name,
                "text": text,
                "size": size,
                "location": location
            }
        except Exception:
            return {"tagName": "unknown", "text": "", "size": {}, "location": {}}