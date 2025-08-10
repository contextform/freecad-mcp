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
                    name="create_cone",
                    description="Create a cone in FreeCAD",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "radius1": {"type": "number", "description": "Bottom radius in mm", "default": 5},
                            "radius2": {"type": "number", "description": "Top radius in mm", "default": 0},
                            "height": {"type": "number", "description": "Cone height in mm", "default": 10},
                            "x": {"type": "number", "description": "X position", "default": 0},
                            "y": {"type": "number", "description": "Y position", "default": 0},
                            "z": {"type": "number", "description": "Z position", "default": 0}
                        }
                    }
                ),
                types.Tool(
                    name="create_torus",
                    description="Create a torus (donut shape) in FreeCAD",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "radius1": {"type": "number", "description": "Major radius (from center to tube center) in mm", "default": 10},
                            "radius2": {"type": "number", "description": "Minor radius (tube thickness) in mm", "default": 3},
                            "x": {"type": "number", "description": "X position", "default": 0},
                            "y": {"type": "number", "description": "Y position", "default": 0},
                            "z": {"type": "number", "description": "Z position", "default": 0}
                        }
                    }
                ),
                types.Tool(
                    name="create_wedge",
                    description="Create a wedge (triangular prism) in FreeCAD",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "xmin": {"type": "number", "description": "Minimum X dimension in mm", "default": 0},
                            "ymin": {"type": "number", "description": "Minimum Y dimension in mm", "default": 0},
                            "zmin": {"type": "number", "description": "Minimum Z dimension in mm", "default": 0},
                            "x2min": {"type": "number", "description": "Minimum X2 dimension in mm", "default": 2},
                            "x2max": {"type": "number", "description": "Maximum X2 dimension in mm", "default": 8},
                            "xmax": {"type": "number", "description": "Maximum X dimension in mm", "default": 10},
                            "ymax": {"type": "number", "description": "Maximum Y dimension in mm", "default": 10},
                            "zmax": {"type": "number", "description": "Maximum Z dimension in mm", "default": 10}
                        }
                    }
                ),
                # === Boolean Operations ===
                types.Tool(
                    name="fuse_objects",
                    description="Fuse (union) two or more objects together",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "objects": {"type": "array", "items": {"type": "string"}, "description": "List of object names to fuse"},
                            "name": {"type": "string", "description": "Name for the result object", "default": "Fusion"}
                        },
                        "required": ["objects"]
                    }
                ),
                types.Tool(
                    name="cut_objects",
                    description="Cut (subtract) objects from a base object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "base": {"type": "string", "description": "Base object name"},
                            "tools": {"type": "array", "items": {"type": "string"}, "description": "Objects to subtract"},
                            "name": {"type": "string", "description": "Name for the result object", "default": "Cut"}
                        },
                        "required": ["base", "tools"]
                    }
                ),
                types.Tool(
                    name="common_objects",
                    description="Find common (intersection) of two or more objects",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "objects": {"type": "array", "items": {"type": "string"}, "description": "List of object names to intersect"},
                            "name": {"type": "string", "description": "Name for the result object", "default": "Common"}
                        },
                        "required": ["objects"]
                    }
                ),
                # === Transformation Tools ===
                types.Tool(
                    name="move_object",
                    description="Move (translate) an object to a new position",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to move"},
                            "x": {"type": "number", "description": "X displacement in mm", "default": 0},
                            "y": {"type": "number", "description": "Y displacement in mm", "default": 0},
                            "z": {"type": "number", "description": "Z displacement in mm", "default": 0}
                        },
                        "required": ["object_name"]
                    }
                ),
                types.Tool(
                    name="rotate_object",
                    description="Rotate an object around an axis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to rotate"},
                            "axis": {"type": "string", "description": "Rotation axis", "enum": ["x", "y", "z"], "default": "z"},
                            "angle": {"type": "number", "description": "Rotation angle in degrees", "default": 90}
                        },
                        "required": ["object_name"]
                    }
                ),
                types.Tool(
                    name="copy_object",
                    description="Create a copy of an object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to copy"},
                            "name": {"type": "string", "description": "Name for the copy", "default": "Copy"},
                            "x": {"type": "number", "description": "X offset for copy", "default": 0},
                            "y": {"type": "number", "description": "Y offset for copy", "default": 0},
                            "z": {"type": "number", "description": "Z offset for copy", "default": 0}
                        },
                        "required": ["object_name"]
                    }
                ),
                types.Tool(
                    name="array_object",
                    description="Create a linear array of an object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to array"},
                            "count": {"type": "integer", "description": "Number of copies", "default": 3},
                            "spacing_x": {"type": "number", "description": "X spacing between copies", "default": 10},
                            "spacing_y": {"type": "number", "description": "Y spacing between copies", "default": 0},
                            "spacing_z": {"type": "number", "description": "Z spacing between copies", "default": 0}
                        },
                        "required": ["object_name"]
                    }
                ),
                # === Part Design Tools ===
                types.Tool(
                    name="create_sketch",
                    description="Create a new sketch on a plane",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plane": {"type": "string", "description": "Sketch plane", "enum": ["XY", "XZ", "YZ"], "default": "XY"},
                            "name": {"type": "string", "description": "Sketch name", "default": "Sketch"}
                        }
                    }
                ),
                types.Tool(
                    name="pad_sketch",
                    description="Extrude a sketch to create a solid (pad operation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sketch_name": {"type": "string", "description": "Name of sketch to extrude"},
                            "length": {"type": "number", "description": "Extrusion length in mm", "default": 10},
                            "name": {"type": "string", "description": "Name for the pad", "default": "Pad"}
                        },
                        "required": ["sketch_name"]
                    }
                ),
                types.Tool(
                    name="pocket_sketch",
                    description="Cut a sketch from a solid (pocket operation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sketch_name": {"type": "string", "description": "Name of sketch to cut"},
                            "length": {"type": "number", "description": "Cut depth in mm", "default": 5},
                            "name": {"type": "string", "description": "Name for the pocket", "default": "Pocket"}
                        },
                        "required": ["sketch_name"]
                    }
                ),
                types.Tool(
                    name="fillet_edges",
                    description="Add fillets (rounded edges) to an object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to fillet"},
                            "radius": {"type": "number", "description": "Fillet radius in mm", "default": 1},
                            "name": {"type": "string", "description": "Name for the filleted object", "default": "Fillet"}
                        },
                        "required": ["object_name"]
                    }
                ),
                # === Analysis Tools ===
                types.Tool(
                    name="measure_distance",
                    description="Measure distance between two objects or points",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object1": {"type": "string", "description": "First object name"},
                            "object2": {"type": "string", "description": "Second object name"}
                        },
                        "required": ["object1", "object2"]
                    }
                ),
                types.Tool(
                    name="get_volume",
                    description="Calculate the volume of an object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to analyze"}
                        },
                        "required": ["object_name"]
                    }
                ),
                types.Tool(
                    name="get_bounding_box",
                    description="Get the bounding box dimensions of an object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to analyze"}
                        },
                        "required": ["object_name"]
                    }
                ),
                types.Tool(
                    name="get_mass_properties",
                    description="Get mass properties (volume, center of mass, etc.) of an object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_name": {"type": "string", "description": "Name of object to analyze"}
                        },
                        "required": ["object_name"]
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
        elif name in ["create_box", "create_cylinder", "create_sphere", "create_cone", 
                      "create_torus", "create_wedge", "get_screenshot", 
                      "fuse_objects", "cut_objects", "common_objects",
                      "move_object", "rotate_object", "copy_object", "array_object",
                      "create_sketch", "pad_sketch", "pocket_sketch", "fillet_edges",
                      "measure_distance", "get_volume", "get_bounding_box", "get_mass_properties",
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