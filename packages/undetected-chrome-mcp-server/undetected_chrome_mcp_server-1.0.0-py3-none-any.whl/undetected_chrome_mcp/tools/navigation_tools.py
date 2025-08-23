"""Navigation tools for undetected Chrome MCP server."""

import logging

from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Get list of navigation tools."""
    return [
        Tool(
            name="navigate",
            description="Navigate to a URL with undetected Chrome",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to"
                    },
                    "allowDangerous": {
                        "type": "boolean",
                        "description": "Allow dangerous LaunchOptions (default: false)",
                        "default": False
                    },
                    "launchOptions": {
                        "type": "object",
                        "description": "Chrome launch options",
                        "default": None
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Navigation timeout in milliseconds",
                        "default": 30000
                    }
                },
                "required": ["url"]
            }
        )
    ]


async def handle_tool_call(name: str, arguments: dict, chrome_manager) -> list[TextContent]:
    """Handle navigation tool calls."""
    if name == "navigate":
        # Import handler locally to avoid circular imports
        from ..handlers.navigation_handler import NavigationHandler
        
        handler = NavigationHandler(chrome_manager)
        result = await handler.navigate(arguments)
        return [TextContent(type="text", text=str(result))]
    
    raise ValueError(f"Unknown navigation tool: {name}")