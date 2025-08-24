"""Fixed MCP server with lazy loading for heavy dependencies."""

import asyncio
import logging
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("undetected-chrome-mcp")

# Global chrome manager instance (lazy loaded)
chrome_manager = None


def get_chrome_manager():
    """Lazy load ChromeManager only when needed."""
    global chrome_manager
    if chrome_manager is None:
        try:
            from .chrome_manager import ChromeManager
            chrome_manager = ChromeManager()
            logger.info("ChromeManager initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import ChromeManager: {e}")
            # Return a mock manager for tool listing
            chrome_manager = "mock"
    return chrome_manager


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available tools without importing heavy dependencies."""
    tools = []
    
    # Define tools directly without importing handlers
    tools.extend([
        Tool(
            name="navigate",
            description="Navigate to a URL with anti-detection measures",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to"},
                    "wait_until": {
                        "type": "string",
                        "description": "Wait condition",
                        "enum": ["load", "domcontentloaded", "networkidle0", "networkidle2"],
                        "default": "load"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="screenshot",
            description="Take a screenshot of the current page or specific element",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name for the screenshot"},
                    "selector": {"type": "string", "description": "CSS selector for element screenshot"},
                    "full_page": {"type": "boolean", "description": "Capture full page", "default": False}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="click",
            description="Click on an element",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector for element to click"}
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="fill",
            description="Fill a form field",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector for form field"},
                    "value": {"type": "string", "description": "Value to fill"}
                },
                "required": ["selector", "value"]
            }
        ),
        Tool(
            name="select",
            description="Select an option from a dropdown",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector for select element"},
                    "value": {"type": "string", "description": "Option value to select"}
                },
                "required": ["selector", "value"]
            }
        ),
        Tool(
            name="hover",
            description="Hover over an element",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector for element to hover"}
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="evaluate",
            description="Execute JavaScript in the browser context",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {"type": "string", "description": "JavaScript code to execute"}
                },
                "required": ["script"]
            }
        )
    ])
    
    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls with lazy loading of dependencies."""
    
    # Lazy load handlers only when actually needed
    manager = get_chrome_manager()
    
    if manager == "mock":
        return [TextContent(
            type="text", 
            text=f"Error: Chrome dependencies not available. Please ensure undetected-chromedriver and selenium are installed."
        )]
    
    try:
        # Import handlers only when needed
        if name == "navigate":
            from .handlers.navigation_handler import handle_navigate
            return await handle_navigate(arguments, manager)
        elif name == "screenshot":
            from .handlers.screenshot_handler import handle_screenshot
            return await handle_screenshot(arguments, manager)
        elif name == "click":
            from .handlers.interaction_handler import handle_click
            return await handle_click(arguments, manager)
        elif name == "fill":
            from .handlers.interaction_handler import handle_fill
            return await handle_fill(arguments, manager)
        elif name == "select":
            from .handlers.interaction_handler import handle_select
            return await handle_select(arguments, manager)
        elif name == "hover":
            from .handlers.interaction_handler import handle_hover
            return await handle_hover(arguments, manager)
        elif name == "evaluate":
            from .handlers.javascript_handler import handle_evaluate
            return await handle_evaluate(arguments, manager)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except ImportError as e:
        logger.error(f"Failed to import handler for {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error: Failed to load handler for {name}. Dependencies may be missing: {e}"
        )]
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def cleanup():
    """Cleanup Chrome manager if initialized."""
    global chrome_manager
    if chrome_manager and chrome_manager != "mock":
        try:
            await chrome_manager.cleanup()
            logger.info("Chrome manager cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def main():
    """Main entry point for the server."""
    logger.info("Starting Undetected ChromeDriver MCP Server...")
    
    # Get custom Chrome path if provided
    chrome_path = os.getenv("CHROME_EXECUTABLE_PATH")
    if chrome_path:
        logger.info(f"Using custom Chrome executable: {chrome_path}")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream, 
                write_stream,
                server.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        await cleanup()
        logger.info("Server shutdown complete")


def cli_main():
    """CLI entry point."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()