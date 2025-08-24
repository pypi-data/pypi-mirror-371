"""JavaScript handler for chrome_evaluate tool."""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    JavascriptException
)

logger = logging.getLogger(__name__)

class JavaScriptHandler:
    """Handles JavaScript execution operations."""
    
    def __init__(self, chrome_manager):
        self.chrome_manager = chrome_manager
    
    async def evaluate(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute JavaScript code in the browser context.
        
        Args:
            arguments: Tool arguments containing script and timeout
            
        Returns:
            Execution result with success status, result data, and error info
        """
        script = arguments.get('script')
        timeout = arguments.get('timeout', 30000) / 1000  # Convert to seconds
        
        if not script:
            raise ValueError("Script is required for JavaScript evaluation")
        
        logger.info(f"Executing JavaScript: {script[:100]}...")
        
        try:
            driver = await self.chrome_manager.get_driver()
            
            # Set script timeout
            await asyncio.get_event_loop().run_in_executor(
                None, driver.set_script_timeout, timeout
            )
            
            # Execute the script
            result = await asyncio.get_event_loop().run_in_executor(
                None, driver.execute_script, script
            )
            
            # Process the result
            processed_result = self._process_result(result)
            
            response = {
                "success": True,
                "result": processed_result
            }
            
            logger.info("JavaScript execution successful")
            return response
            
        except JavascriptException as e:
            error_msg = f"JavaScript execution error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "result": None
            }
            
        except TimeoutException:
            error_msg = f"JavaScript execution timeout after {timeout}s"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "result": None
            }
            
        except WebDriverException as e:
            error_msg = f"WebDriver error during JavaScript execution: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "result": None
            }
            
        except Exception as e:
            error_msg = f"Unexpected error during JavaScript execution: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "result": None
            }
    
    def _process_result(self, result: Any) -> Any:
        """Process JavaScript execution result for JSON serialization."""
        if result is None:
            return None
        
        # Handle basic types
        if isinstance(result, (bool, int, float, str)):
            return result
        
        # Handle lists/arrays
        if isinstance(result, list):
            return [self._process_result(item) for item in result]
        
        # Handle dictionaries/objects
        if isinstance(result, dict):
            return {key: self._process_result(value) for key, value in result.items()}
        
        # Handle WebElements (convert to basic info)
        if hasattr(result, 'tag_name'):
            try:
                return {
                    "type": "WebElement",
                    "tagName": result.tag_name,
                    "text": result.text[:100] if result.text else "",  # Limit text length
                    "id": result.get_attribute("id") or "",
                    "className": result.get_attribute("class") or ""
                }
            except Exception:
                return {"type": "WebElement", "error": "Could not serialize element"}
        
        # For other objects, try to convert to string
        try:
            # Try JSON serialization first
            json.dumps(result)
            return result
        except (TypeError, ValueError):
            # Fall back to string representation
            return str(result)
    
    async def evaluate_async(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute asynchronous JavaScript code.
        
        Args:
            arguments: Tool arguments containing script and timeout
            
        Returns:
            Execution result with success status, result data, and error info
        """
        script = arguments.get('script')
        timeout = arguments.get('timeout', 30000) / 1000
        
        if not script:
            raise ValueError("Script is required for async JavaScript evaluation")
        
        logger.info(f"Executing async JavaScript: {script[:100]}...")
        
        try:
            driver = await self.chrome_manager.get_driver()
            
            # Wrap script in async execution context
            async_script = f"""
            var callback = arguments[arguments.length - 1];
            try {{
                var result = (function() {{
                    {script}
                }})();
                if (result && typeof result.then === 'function') {{
                    result.then(callback).catch(callback);
                }} else {{
                    callback(result);
                }}
            }} catch (error) {{
                callback({{error: error.message, stack: error.stack}});
            }}
            """
            
            # Execute async script
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: driver.execute_async_script(async_script)
            )
            
            # Check for JavaScript errors
            if isinstance(result, dict) and 'error' in result:
                return {
                    "success": False,
                    "error": f"JavaScript error: {result['error']}",
                    "result": None
                }
            
            processed_result = self._process_result(result)
            
            return {
                "success": True,
                "result": processed_result
            }
            
        except Exception as e:
            error_msg = f"Async JavaScript execution error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "result": None
            }