#!/opt/homebrew/bin/python3.11
"""
Working MCP Bridge for FreeCAD
Uses the correct MCP API for testing with Claude Desktop
"""

import asyncio
import json
import os
import sys
from typing import Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Run MCP server for FreeCAD integration"""
    try:
        # Import MCP components with correct API
        import mcp.types as types
        from mcp.server import NotificationOptions, Server
        from mcp.server.models import InitializationOptions
    except ImportError as e:
        # Fallback error message
        error_msg = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": f"MCP import failed: {e}"
            }
        }
        print(json.dumps(error_msg), file=sys.stderr)
        sys.exit(1)

    # Create server
    server = Server("freecad-ai-copilot")
    
    # Check if FreeCAD is available
    socket_path = "/tmp/freecad_mcp.sock"
    freecad_available = os.path.exists(socket_path)
    
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="check_freecad_connection",
                description="Check if FreeCAD is running with AI Copilot workbench",
                inputSchema={
                    "type": "object",
                    "properties": {},
                }
            ),
            types.Tool(
                name="test_echo",
                description="Test tool that echoes back a message",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to echo back"
                        }
                    },
                    "required": ["message"]
                }
            ),
            types.Tool(
                name="list_expected_tools",
                description="List tools that would be available when FreeCAD is connected",
                inputSchema={
                    "type": "object",
                    "properties": {},
                }
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent]:
        """Handle tool calls"""
        
        if name == "check_freecad_connection":
            status = {
                "freecad_socket_exists": os.path.exists(socket_path),
                "socket_path": socket_path,
                "status": "FreeCAD running with AI Copilot workbench" if os.path.exists(socket_path) 
                         else "FreeCAD not running. Please start FreeCAD and switch to AI Copilot workbench"
            }
            return [types.TextContent(
                type="text",
                text=json.dumps(status, indent=2)
            )]
            
        elif name == "test_echo":
            message = arguments.get("message", "No message provided") if arguments else "No arguments"
            return [types.TextContent(
                type="text", 
                text=f"Bridge received: {message}"
            )]
            
        elif name == "list_expected_tools":
            tools = {
                "document_operations": [
                    "create_document", "save_document", "list_documents"
                ],
                "object_creation": [
                    "create_box", "create_cylinder", "create_sphere", "create_cone"
                ],
                "sketch_operations": [
                    "create_sketch", "add_line_to_sketch", "add_circle_to_sketch"
                ],
                "boolean_operations": [
                    "boolean_cut", "boolean_union", "boolean_intersection"
                ],
                "gui_control": [
                    "click_at", "drag_mouse", "send_keys", "click_menu", "activate_workbench"
                ],
                "visualization": [
                    "get_screenshot", "fit_all", "set_view", "take_screenshot"
                ],
                "parts_library": [
                    "save_as_part", "insert_part_from_library", "list_parts_library"
                ],
                "advanced": [
                    "execute_python", "serialize_object", "get_gui_state"
                ]
            }
            
            total_tools = sum(len(category) for category in tools.values())
            
            result = {
                "status": "Bridge running - waiting for FreeCAD connection",
                "total_expected_tools": total_tools,
                "tool_categories": tools,
                "note": "These tools will be available when FreeCAD is running with AI Copilot workbench"
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="freecad-ai-copilot",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())