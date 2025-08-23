"""Simple wrapper functions for MCP tools."""

from mcp.types import TextContent
from typing import Any, Dict, List
import os
import time

async def handle_screenshot(arguments: dict[str, Any], chrome_manager) -> list[TextContent]:
    """Take a screenshot of the current page."""
    try:
        driver = await chrome_manager.get_driver()
        
        name = arguments.get("name", "screenshot")
        screenshot_dir = "/workspace/reddit/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        
        filepath = os.path.join(screenshot_dir, f"{name}.png")
        driver.save_screenshot(filepath)
        
        return [TextContent(
            type="text",
            text=f"Screenshot saved to: {filepath}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Screenshot error: {str(e)}"
        )]

async def handle_click(arguments: dict[str, Any], chrome_manager) -> list[TextContent]:
    """Click on an element."""
    try:
        driver = await chrome_manager.get_driver()
        selector = arguments.get("selector", "")
        
        if not selector:
            return [TextContent(type="text", text="Error: selector is required")]
        
        element = driver.find_element("css selector", selector)
        element.click()
        
        return [TextContent(
            type="text",
            text=f"Clicked element: {selector}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Click error: {str(e)}"
        )]

async def handle_fill(arguments: dict[str, Any], chrome_manager) -> list[TextContent]:
    """Fill a form field."""
    try:
        driver = await chrome_manager.get_driver()
        selector = arguments.get("selector", "")
        value = arguments.get("value", "")
        
        if not selector:
            return [TextContent(type="text", text="Error: selector is required")]
        
        element = driver.find_element("css selector", selector)
        element.clear()
        element.send_keys(value)
        
        return [TextContent(
            type="text",
            text=f"Filled {selector} with: {value}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Fill error: {str(e)}"
        )]

async def handle_select(arguments: dict[str, Any], chrome_manager) -> list[TextContent]:
    """Select an option from a dropdown."""
    try:
        driver = await chrome_manager.get_driver()
        selector = arguments.get("selector", "")
        value = arguments.get("value", "")
        
        if not selector:
            return [TextContent(type="text", text="Error: selector is required")]
        
        from selenium.webdriver.support.ui import Select
        element = driver.find_element("css selector", selector)
        select = Select(element)
        select.select_by_value(value)
        
        return [TextContent(
            type="text",
            text=f"Selected {value} in {selector}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Select error: {str(e)}"
        )]

async def handle_hover(arguments: dict[str, Any], chrome_manager) -> list[TextContent]:
    """Hover over an element."""
    try:
        driver = await chrome_manager.get_driver()
        selector = arguments.get("selector", "")
        
        if not selector:
            return [TextContent(type="text", text="Error: selector is required")]
        
        from selenium.webdriver.common.action_chains import ActionChains
        element = driver.find_element("css selector", selector)
        ActionChains(driver).move_to_element(element).perform()
        
        return [TextContent(
            type="text",
            text=f"Hovered over: {selector}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Hover error: {str(e)}"
        )]

async def handle_evaluate(arguments: dict[str, Any], chrome_manager) -> list[TextContent]:
    """Execute JavaScript in the browser."""
    try:
        driver = await chrome_manager.get_driver()
        script = arguments.get("script", "")
        
        if not script:
            return [TextContent(type="text", text="Error: script is required")]
        
        result = driver.execute_script(script)
        
        return [TextContent(
            type="text",
            text=f"Script result: {result}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Evaluate error: {str(e)}"
        )]