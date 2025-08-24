"""Fixed MCP server with lazy loading for heavy dependencies."""

import asyncio
import json
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
        ),
        Tool(
            name="start_network_monitoring",
            description="Start monitoring network traffic using Chrome DevTools Protocol",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="stop_network_monitoring", 
            description="Stop monitoring network traffic",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_network_requests",
            description="Get captured network requests, optionally filtered by URL pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "url_filter": {"type": "string", "description": "URL pattern to filter requests"}
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_network_responses",
            description="Get captured network responses, optionally filtered by URL pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "url_filter": {"type": "string", "description": "URL pattern to filter responses"}
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_response_body",
            description="Get response body for a specific request ID",
            inputSchema={
                "type": "object", 
                "properties": {
                    "request_id": {"type": "string", "description": "Request ID to get response body for"}
                },
                "required": ["request_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_network_summary",
            description="Get summary of captured network activity",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="clear_network_data",
            description="Clear all captured network data",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
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
            from .handlers.navigation_wrapper import handle_navigate
            return await handle_navigate(arguments, manager)
        elif name == "screenshot":
            from .handlers.tool_wrappers import handle_screenshot
            return await handle_screenshot(arguments, manager)
        elif name == "click":
            from .handlers.tool_wrappers import handle_click
            return await handle_click(arguments, manager)
        elif name == "fill":
            from .handlers.tool_wrappers import handle_fill
            return await handle_fill(arguments, manager)
        elif name == "select":
            from .handlers.tool_wrappers import handle_select
            return await handle_select(arguments, manager)
        elif name == "hover":
            from .handlers.tool_wrappers import handle_hover
            return await handle_hover(arguments, manager)
        elif name == "evaluate":
            from .handlers.tool_wrappers import handle_evaluate
            return await handle_evaluate(arguments, manager)
        elif name == "start_network_monitoring":
            return await handle_start_network_monitoring(arguments, manager)
        elif name == "stop_network_monitoring":
            return await handle_stop_network_monitoring(arguments, manager)
        elif name == "get_network_requests":
            return await handle_get_network_requests(arguments, manager)
        elif name == "get_network_responses":
            return await handle_get_network_responses(arguments, manager)
        elif name == "get_response_body":
            return await handle_get_response_body(arguments, manager)
        elif name == "get_network_summary":
            return await handle_get_network_summary(arguments, manager)
        elif name == "clear_network_data":
            return await handle_clear_network_data(arguments, manager)
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


# Network monitoring handler functions
async def handle_start_network_monitoring(arguments: dict[str, Any], manager) -> list[TextContent]:
    """Handle start_network_monitoring tool call."""
    try:
        success = await manager.start_network_monitoring()
        result = {"success": success, "monitoring_active": manager.network_monitoring}
        return [TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        logger.error(f"Error starting network monitoring: {e}")
        return [TextContent(type="text", text=f"Error starting network monitoring: {str(e)}")]


async def handle_stop_network_monitoring(arguments: dict[str, Any], manager) -> list[TextContent]:
    """Handle stop_network_monitoring tool call."""
    try:
        success = await manager.stop_network_monitoring()
        result = {"success": success, "monitoring_active": manager.network_monitoring}
        return [TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        logger.error(f"Error stopping network monitoring: {e}")
        return [TextContent(type="text", text=f"Error stopping network monitoring: {str(e)}")]


async def handle_get_network_requests(arguments: dict[str, Any], manager) -> list[TextContent]:
    """Handle get_network_requests tool call."""
    try:
        url_filter = arguments.get('url_filter')
        requests = manager.get_network_requests(url_filter)
        result = {
            "total": len(requests),
            "url_filter": url_filter,
            "requests": requests
        }
        return [TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        logger.error(f"Error getting network requests: {e}")
        return [TextContent(type="text", text=f"Error getting network requests: {str(e)}")]


async def handle_get_network_responses(arguments: dict[str, Any], manager) -> list[TextContent]:
    """Handle get_network_responses tool call.""" 
    try:
        url_filter = arguments.get('url_filter')
        responses = manager.get_network_responses(url_filter)
        result = {
            "total": len(responses),
            "url_filter": url_filter,
            "responses": responses
        }
        return [TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        logger.error(f"Error getting network responses: {e}")
        return [TextContent(type="text", text=f"Error getting network responses: {str(e)}")]


async def handle_get_response_body(arguments: dict[str, Any], manager) -> list[TextContent]:
    """Handle get_response_body tool call."""
    try:
        request_id = arguments.get('request_id')
        if not request_id:
            return [TextContent(type="text", text="Error: request_id is required")]
        
        body = await manager.get_response_body(request_id)
        result = {
            "request_id": request_id,
            "body": body,
            "success": body is not None
        }
        return [TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        logger.error(f"Error getting response body: {e}")
        return [TextContent(type="text", text=f"Error getting response body: {str(e)}")]


async def handle_get_network_summary(arguments: dict[str, Any], manager) -> list[TextContent]:
    """Handle get_network_summary tool call."""
    try:
        summary = manager.get_network_summary()
        return [TextContent(type="text", text=json.dumps(summary))]
    except Exception as e:
        logger.error(f"Error getting network summary: {e}")
        return [TextContent(type="text", text=f"Error getting network summary: {str(e)}")]


async def handle_clear_network_data(arguments: dict[str, Any], manager) -> list[TextContent]:
    """Handle clear_network_data tool call."""
    try:
        manager.clear_network_data()
        result = {"success": True, "message": "Network data cleared successfully"}
        return [TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        logger.error(f"Error clearing network data: {e}")
        return [TextContent(type="text", text=f"Error clearing network data: {str(e)}")]


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