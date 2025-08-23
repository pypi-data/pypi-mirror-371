"""Main MCP server implementation for undetected ChromeDriver."""

import asyncio
import logging
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

from .chrome_manager import ChromeManager
from .tools import (
    navigation_tools,
    interaction_tools,
    screenshot_tools,
    javascript_tools,
    debug_tools,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("undetected-chrome-mcp")

# Global chrome manager instance
chrome_manager: ChromeManager | None = None


def initialize_chrome_manager():
    """Initialize Chrome manager."""
    global chrome_manager
    if chrome_manager is None:
        chrome_manager = ChromeManager()


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available tools."""
    tools = []
    
    # Add tools from each module - matches reddit-mcp pattern exactly
    tools.extend(debug_tools.get_tools())
    tools.extend(navigation_tools.get_tools())
    tools.extend(interaction_tools.get_tools())
    tools.extend(screenshot_tools.get_tools())
    tools.extend(javascript_tools.get_tools())
    
    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    # Initialize chrome manager if not already done
    if chrome_manager is None:
        initialize_chrome_manager()
    
    # Route to appropriate tool handler - matches reddit-mcp pattern exactly  
    if name in [tool.name for tool in debug_tools.get_tools()]:
        return await debug_tools.handle_tool_call(name, arguments, chrome_manager)
    elif name in [tool.name for tool in navigation_tools.get_tools()]:
        return await navigation_tools.handle_tool_call(name, arguments, chrome_manager)
    elif name in [tool.name for tool in interaction_tools.get_tools()]:
        return await interaction_tools.handle_tool_call(name, arguments, chrome_manager)
    elif name in [tool.name for tool in screenshot_tools.get_tools()]:
        return await screenshot_tools.handle_tool_call(name, arguments, chrome_manager)
    elif name in [tool.name for tool in javascript_tools.get_tools()]:
        return await javascript_tools.handle_tool_call(name, arguments, chrome_manager)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def cleanup():
    """Clean up resources."""
    if chrome_manager:
        await chrome_manager.cleanup()


async def main():
    """Main entry point for the server."""
    logger.info("Starting Undetected ChromeDriver MCP Server...")
    
    # Check for required environment variables (optional)
    chrome_path = os.getenv('CHROME_EXECUTABLE_PATH')
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