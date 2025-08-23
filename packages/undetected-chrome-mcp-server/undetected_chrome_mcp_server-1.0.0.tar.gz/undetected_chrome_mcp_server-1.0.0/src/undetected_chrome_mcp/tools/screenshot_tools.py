"""Screenshot tools for undetected Chrome MCP server."""

import logging

from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Get list of screenshot tools."""
    return [
        Tool(
            name="screenshot",
            description="Take a screenshot of the current page or element",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name for the screenshot"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for element to screenshot"
                    },
                    "encoded": {
                        "type": "boolean",
                        "description": "Return base64 encoded image (default: false)",
                        "default": False
                    },
                    "width": {
                        "type": "number",
                        "description": "Width in pixels"
                    },
                    "height": {
                        "type": "number", 
                        "description": "Height in pixels"
                    },
                    "fullPage": {
                        "type": "boolean",
                        "description": "Capture full page (default: false)",
                        "default": False
                    }
                },
                "required": ["name"]
            }
        )
    ]


async def handle_tool_call(name: str, arguments: dict, chrome_manager) -> list[TextContent]:
    """Handle screenshot tool calls."""
    if name == "screenshot":
        # Import handler locally to avoid circular imports
        from ..handlers.screenshot_handler import ScreenshotHandler
        
        handler = ScreenshotHandler(chrome_manager)
        result = await handler.screenshot(arguments)
        return [TextContent(type="text", text=str(result))]
    
    raise ValueError(f"Unknown screenshot tool: {name}")