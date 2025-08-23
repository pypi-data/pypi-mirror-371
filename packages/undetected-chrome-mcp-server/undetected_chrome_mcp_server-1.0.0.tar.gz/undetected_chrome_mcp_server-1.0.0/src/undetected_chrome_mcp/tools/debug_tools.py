"""Debug tools to test basic functionality."""

import logging
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Get list of debug tools."""
    return [
        Tool(
            name="debug_hello",
            description="Simple debug hello tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet",
                        "default": "Debug"
                    }
                },
                "required": []
            }
        )
    ]


async def handle_tool_call(name: str, arguments: dict, chrome_manager) -> list[TextContent]:
    """Handle debug tool calls."""
    if name == "debug_hello":
        name_arg = arguments.get("name", "Debug")
        message = f"Debug Hello from undetected-chrome-mcp: {name_arg}!"
        return [TextContent(type="text", text=message)]
    
    raise ValueError(f"Unknown debug tool: {name}")