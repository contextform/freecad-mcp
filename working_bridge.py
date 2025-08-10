#!/opt/homebrew/bin/python3.11
"""
Working MCP Bridge for FreeCAD
Uses the correct MCP API for testing with Claude Desktop
"""

import asyncio
import json
import os
import sys
import socket
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
        # MCP import failed - exit silently to avoid STDIO corruption
        sys.exit(1)

    # Create server (name must match config!)
    server = Server("ctxform")
    
    # Check if FreeCAD is available
    socket_path = "/tmp/freecad_mcp.sock"
    freecad_available = os.path.exists(socket_path)
    
    async def send_to_freecad(tool_name: str, args: dict) -> str:
        """Send command to FreeCAD via Unix socket"""
        try:
            if not os.path.exists(socket_path):
                return json.dumps({"error": "FreeCAD socket not available. Please start FreeCAD and switch to AI Copilot workbench"})
            
            # Create socket connection
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(socket_path)
            
            # Send command
            command = json.dumps({"tool": tool_name, "args": args})
            sock.send(command.encode('utf-8'))
            
            # Receive response
            response = sock.recv(4096).decode('utf-8')
            sock.close()
            
            return response
            
        except Exception as e:
            return json.dumps({"error": f"Socket communication error: {e}"})
    
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        base_tools = [
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
            )
        ]
        
        # Add FreeCAD tools if socket is available
        if os.path.exists(socket_path):
            freecad_tools = [
                types.Tool(
                    name="create_box",
                    description="Create a box in FreeCAD with specified dimensions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "length": {"type": "number", "description": "Box length in mm", "default": 10},
                            "width": {"type": "number", "description": "Box width in mm", "default": 10},
                            "height": {"type": "number", "description": "Box height in mm", "default": 10},
                            "x": {"type": "number", "description": "X position", "default": 0},
                            "y": {"type": "number", "description": "Y position", "default": 0},
                            "z": {"type": "number", "description": "Z position", "default": 0}
                        }
                    }
                ),
                types.Tool(
                    name="create_cylinder",
                    description="Create a cylinder in FreeCAD",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "radius": {"type": "number", "description": "Cylinder radius in mm", "default": 5},
                            "height": {"type": "number", "description": "Cylinder height in mm", "default": 10},
                            "x": {"type": "number", "description": "X position", "default": 0},
                            "y": {"type": "number", "description": "Y position", "default": 0},
                            "z": {"type": "number", "description": "Z position", "default": 0}
                        }
                    }
                ),
                types.Tool(
                    name="create_sphere",
                    description="Create a sphere in FreeCAD",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "radius": {"type": "number", "description": "Sphere radius in mm", "default": 5},
                            "x": {"type": "number", "description": "X position", "default": 0},
                            "y": {"type": "number", "description": "Y position", "default": 0},
                            "z": {"type": "number", "description": "Z position", "default": 0}
                        }
                    }
                ),
                types.Tool(
                    name="get_screenshot",
                    description="Take a screenshot of the current FreeCAD view",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "width": {"type": "integer", "description": "Screenshot width", "default": 800},
                            "height": {"type": "integer", "description": "Screenshot height", "default": 600}
                        }
                    }
                ),
                types.Tool(
                    name="list_all_objects",
                    description="List all objects in the active FreeCAD document",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="activate_workbench",
                    description="Activate a specific FreeCAD workbench",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workbench_name": {"type": "string", "description": "Name of workbench to activate"}
                        },
                        "required": ["workbench_name"]
                    }
                ),
                types.Tool(
                    name="execute_python",
                    description="Execute Python code in FreeCAD context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Python code to execute"}
                        },
                        "required": ["code"]
                    }
                ),
                # GUI Control Tools
                types.Tool(
                    name="run_command",
                    description="Execute a FreeCAD GUI command",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "FreeCAD command name (e.g. 'Std_New', 'Part_Box')"}
                        },
                        "required": ["command"]
                    }
                ),
                types.Tool(
                    name="new_document",
                    description="Create a new FreeCAD document",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Document name", "default": "Unnamed"}
                        }
                    }
                ),
                types.Tool(
                    name="save_document",
                    description="Save the current document",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "File path to save (optional)"}
                        }
                    }
                ),
                types.Tool(
                    name="set_view",
                    description="Set the 3D view orientation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "view_type": {"type": "string", "description": "View type: top, front, left, right, isometric, axonometric", "default": "isometric"}
                        }
                    }
                ),
                types.Tool(
                    name="fit_all",
                    description="Fit all objects in the 3D view",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="select_object",
                    description="Select a specific object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to select"}
                        },
                        "required": ["object_name"]
                    }
                ),
                types.Tool(
                    name="clear_selection",
                    description="Clear all selected objects",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_selection",
                    description="Get currently selected objects",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="hide_object",
                    description="Hide an object from view",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to hide"}
                        },
                        "required": ["object_name"]
                    }
                ),
                types.Tool(
                    name="show_object",
                    description="Show a hidden object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to show"}
                        },
                        "required": ["object_name"]
                    }
                ),
                types.Tool(
                    name="delete_object",
                    description="Delete an object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to delete"}
                        },
                        "required": ["object_name"]
                    }
                ),
                types.Tool(
                    name="undo",
                    description="Undo the last operation",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="redo",
                    description="Redo the last undone operation",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="ai_agent",
                    description="Process requests through the FreeCAD ReAct Agent (Claude Code-like intelligent assistant)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "request": {
                                "type": "string", 
                                "description": "Natural language request for FreeCAD operations (e.g. 'Make all holes 2mm bigger', 'Create a motor mount', 'List all objects')"
                            }
                        },
                        "required": ["request"]
                    }
                )
            ]
            return base_tools + freecad_tools
        
        return base_tools

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
            
        # Route FreeCAD tools to socket
        elif name in ["create_box", "create_cylinder", "create_sphere", "get_screenshot", 
                      "list_all_objects", "activate_workbench", "execute_python",
                      "run_command", "new_document", "save_document", "set_view", "fit_all",
                      "select_object", "clear_selection", "get_selection", "hide_object", 
                      "show_object", "delete_object", "undo", "redo", "ai_agent"]:
            args = arguments or {}
            response = await send_to_freecad(name, args)
            
            return [types.TextContent(
                type="text",
                text=response
            )]
            
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    # Run the server
    import mcp.server.stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ctxform",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())