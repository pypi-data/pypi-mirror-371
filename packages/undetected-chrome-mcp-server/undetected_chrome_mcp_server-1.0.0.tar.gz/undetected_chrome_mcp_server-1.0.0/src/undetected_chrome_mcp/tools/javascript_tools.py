"""JavaScript tools for undetected Chrome MCP server."""

import logging

from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)


def get_tools() -> list[Tool]:
    """Get list of JavaScript tools."""
    return [
        Tool(
            name="evaluate", 
            description="Execute JavaScript in the browser console",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "JavaScript code to execute"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Execution timeout in milliseconds",
                        "default": 30000
                    }
                },
                "required": ["script"]
            }
        )
    ]


async def handle_tool_call(name: str, arguments: dict, chrome_manager) -> list[TextContent]:
    """Handle JavaScript tool calls."""
    if name == "evaluate":
        # Import handler locally to avoid circular imports
        from ..handlers.javascript_handler import JavaScriptHandler
        
        handler = JavaScriptHandler(chrome_manager)
        result = await handler.evaluate(arguments)
        return [TextContent(type="text", text=str(result))]
    
    raise ValueError(f"Unknown JavaScript tool: {name}")