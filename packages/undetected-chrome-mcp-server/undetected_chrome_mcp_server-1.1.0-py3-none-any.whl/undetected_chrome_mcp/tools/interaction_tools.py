"""Interaction tools for undetected Chrome MCP server."""

import logging

from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Get list of interaction tools."""
    return [
        Tool(
            name="click",
            description="Click an element on the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for element to click"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Wait timeout in milliseconds",
                        "default": 10000
                    }
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="fill",
            description="Fill out an input field",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for input field"
                    },
                    "value": {
                        "type": "string",
                        "description": "Value to fill"
                    },
                    "clear": {
                        "type": "boolean",
                        "description": "Clear field before filling (default: true)",
                        "default": True
                    }
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
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for select element"
                    },
                    "value": {
                        "type": "string",
                        "description": "Value to select"
                    }
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
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for element to hover"
                    }
                },
                "required": ["selector"]
            }
        )
    ]


async def handle_tool_call(name: str, arguments: dict, chrome_manager) -> list[TextContent]:
    """Handle interaction tool calls."""
    # Import handler locally to avoid circular imports
    from ..handlers.interaction_handler import InteractionHandler
    
    handler = InteractionHandler(chrome_manager)
    
    if name == "click":
        result = await handler.click(arguments)
    elif name == "fill":
        result = await handler.fill(arguments)
    elif name == "select":
        result = await handler.select(arguments)
    elif name == "hover":
        result = await handler.hover(arguments)
    else:
        raise ValueError(f"Unknown interaction tool: {name}")
    
    return [TextContent(type="text", text=str(result))]