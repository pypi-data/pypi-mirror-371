"""Navigation handler wrapper functions for MCP server."""

from mcp.types import TextContent
from typing import Any, Dict, List

async def handle_navigate(arguments: dict[str, Any], chrome_manager) -> list[TextContent]:
    """Navigate to a URL with anti-detection.
    
    This is a wrapper function that the MCP server expects.
    """
    try:
        # Get or create a driver instance
        driver = await chrome_manager.get_driver()
        
        url = arguments.get("url", "")
        if not url:
            return [TextContent(
                type="text",
                text="Error: URL is required for navigation"
            )]
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for page to stabilize
        import time
        time.sleep(2)
        
        # Get page info
        current_url = driver.current_url
        title = driver.title
        
        # Check if we bypassed detection
        detection_status = driver.execute_script("return navigator.webdriver")
        
        result = f"Successfully navigated to {current_url}\n"
        result += f"Title: {title}\n"
        result += f"Bot detection: {'Detected' if detection_status else 'Not detected (Success!)'}"
        
        return [TextContent(
            type="text",
            text=result
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Navigation error: {str(e)}"
        )]