#!/opt/homebrew/bin/python3.11
"""
FreeCAD MCP Bridge - Phase 1 Smart Dispatcher Architecture
Smart dispatchers aligned with FreeCAD workbench structure for optimal Claude Code integration
"""

import asyncio
import json
import os
import sys
import socket
import platform
from typing import Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize debugging infrastructure (optional - works without it)
try:
    from freecad_debug import get_debugger, debug_decorator
    from freecad_health import get_monitor
    import logging
    
    debugger = get_debugger()
    monitor = get_monitor()
    debugger.logger.info("="*80)
    debugger.logger.info("FreeCAD MCP Bridge Starting with Debug Infrastructure")
    debugger.logger.info("="*80)
    DEBUG_ENABLED = True
except ImportError:
    # Debugging modules not available - continue without them
    debugger = None
    monitor = None
    DEBUG_ENABLED = False
    
    # Create no-op decorator if debug not available
    def debug_decorator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

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

    # Create server with freecad naming
    server = Server("freecad")
    
    # Check if FreeCAD is available (cross-platform)
    if platform.system() == "Windows":
        socket_path = "localhost:23456"
        freecad_available = True  # We'll check connection when needed
    else:
        socket_path = "/tmp/freecad_mcp.sock"
        freecad_available = os.path.exists(socket_path)
    
    @debug_decorator(track_state=False, track_performance=True)
    async def send_to_freecad(tool_name: str, args: dict) -> str:
        """Send command to FreeCAD via socket (cross-platform)"""
        try:
            # Create socket connection based on platform
            if platform.system() == "Windows":
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('localhost', 23456))
            else:
                if not os.path.exists(socket_path):
                    return json.dumps({"error": "FreeCAD socket not available. Please start FreeCAD and switch to AI Copilot workbench"})
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(socket_path)
            
            # Send command
            command = json.dumps({"tool": tool_name, "args": args})
            sock.send(command.encode('utf-8'))
            
            # Receive response
            response = sock.recv(8192).decode('utf-8')
            sock.close()
            
            # Check if this is a selection workflow response
            try:
                result = json.loads(response)
                if isinstance(result, dict) and result.get("status") == "awaiting_selection":
                    # Handle interactive selection workflow
                    return await handle_selection_workflow(tool_name, args, result)
            except json.JSONDecodeError:
                pass  # Not JSON, return as-is
            
            return response
            
        except Exception as e:
            # Log the exception if debugger is available
            if DEBUG_ENABLED and debugger:
                debugger.log_operation(
                    operation="send_to_freecad",
                    parameters={"tool_name": tool_name, "args": args},
                    error=e
                )
                # Check FreeCAD health after socket error
                if monitor:
                    status = monitor.perform_health_check()
                    if not status['is_healthy']:
                        monitor.log_crash(status, {
                            "triggered_by": "socket_error",
                            "tool_name": tool_name,
                            "args": args
                        })
            return json.dumps({"error": f"Socket communication error: {e}"})
    
    async def handle_selection_workflow(tool_name: str, original_args: dict, selection_request: dict) -> str:
        """Handle the interactive selection workflow - Claude Code style"""
        try:
            # Format the interactive message for Claude Code
            message = selection_request.get("message", "Please make selection in FreeCAD")
            selection_type = selection_request.get("selection_type", "elements")
            object_name = selection_request.get("object_name", "")
            operation_id = selection_request.get("operation_id", "")
            
            # Create Claude Code compatible interactive response
            interactive_response = {
                "interactive": True,
                "message": f"🎯 Interactive Selection Required\n\n{message}",
                "operation_id": operation_id,
                "selection_type": selection_type,
                "object_name": object_name,
                "tool_name": tool_name,
                "original_args": original_args,
                "instructions": f"1. Go to FreeCAD and select {selection_type} on {object_name}\n2. Return here and choose an option:"
            }
            
            return json.dumps(interactive_response)
            
        except Exception as e:
            return json.dumps({"error": f"Selection workflow error: {e}"})
    
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available Phase 1 smart dispatcher tools"""
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
        
        # Add Phase 1 Smart Dispatchers if socket is available
        if freecad_available:
            smart_dispatchers = [
                types.Tool(
                    name="partdesign_operations", 
                    description="⚠️ MODIFIES FreeCAD document: Smart dispatcher for parametric features. Operations like fillet/chamfer require edge selection and will permanently modify the 3D model.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "PartDesign operation to perform",
                                "enum": [
                                    # Additive features (5)
                                    "pad", "revolution", "loft", "sweep", "additive_pipe",
                                    # Subtractive features (2)
                                    "groove", "subtractive_sweep",
                                    # Dress-up features (2)
                                    "fillet", "chamfer",
                                    # Pattern features (1)
                                    "mirror",
                                    # Hole features (3)
                                    "hole", "counterbore", "countersink"
                                ]
                            },
                            "sketch_name": {"type": "string", "description": "Sketch name for operations"},
                            "object_name": {"type": "string", "description": "Object name for dress-up operations"},
                            "feature_name": {"type": "string", "description": "Feature name for pattern operations"},
                            # Common parameters
                            "length": {"type": "number", "description": "Length/depth for pad", "default": 10},
                            "radius": {"type": "number", "description": "Radius for fillet/holes", "default": 1},
                            "distance": {"type": "number", "description": "Distance for chamfer", "default": 1},
                            "angle": {"type": "number", "description": "Angle for revolution/draft", "default": 360},
                            "thickness": {"type": "number", "description": "Thickness value", "default": 2},
                            # Pattern parameters
                            "count": {"type": "integer", "description": "Pattern count", "default": 3},
                            "spacing": {"type": "number", "description": "Pattern spacing", "default": 10},
                            "axis": {"type": "string", "description": "Axis for patterns", "enum": ["x", "y", "z"], "default": "x"},
                            "plane": {"type": "string", "description": "Mirror plane", "enum": ["XY", "XZ", "YZ"], "default": "YZ"},
                            # Hole parameters
                            "diameter": {"type": "number", "description": "Hole diameter", "default": 6},
                            "depth": {"type": "number", "description": "Hole depth", "default": 10},
                            "x": {"type": "number", "description": "X position", "default": 0},
                            "y": {"type": "number", "description": "Y position", "default": 0},
                            # Advanced parameters
                            "name": {"type": "string", "description": "Name for result feature"}
                        },
                        "required": ["operation"]
                    }
                ),
                types.Tool(
                    name="part_operations",
                    description="Smart dispatcher for all basic solid and boolean operations (18+ operations)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "Part operation to perform", 
                                "enum": [
                                    # Primitive creation (6)
                                    "box", "cylinder", "sphere", "cone", "torus", "wedge",
                                    # Boolean operations (4)
                                    "fuse", "cut", "common", "section",
                                    # Transform operations (4)
                                    "move", "rotate", "scale", "mirror",
                                    # Advanced creation (4)
                                    "loft", "sweep", "extrude", "revolve"
                                ]
                            },
                            # Primitive parameters
                            "length": {"type": "number", "description": "Box length", "default": 10},
                            "width": {"type": "number", "description": "Box width", "default": 10},
                            "height": {"type": "number", "description": "Box/cylinder height", "default": 10},
                            "radius": {"type": "number", "description": "Sphere/cylinder radius", "default": 5},
                            "radius1": {"type": "number", "description": "Major radius for torus/cone", "default": 10},
                            "radius2": {"type": "number", "description": "Minor radius for torus/cone", "default": 3},
                            # Position parameters
                            "x": {"type": "number", "description": "X position", "default": 0},
                            "y": {"type": "number", "description": "Y position", "default": 0},
                            "z": {"type": "number", "description": "Z position", "default": 0},
                            # Boolean operation parameters
                            "objects": {"type": "array", "items": {"type": "string"}, "description": "Object names for boolean ops"},
                            "base": {"type": "string", "description": "Base object for cut operation"},
                            "tools": {"type": "array", "items": {"type": "string"}, "description": "Tool objects for cut"},
                            # Transform parameters
                            "object_name": {"type": "string", "description": "Object to transform"},
                            "axis": {"type": "string", "description": "Rotation axis", "enum": ["x", "y", "z"], "default": "z"},
                            "angle": {"type": "number", "description": "Rotation angle", "default": 90},
                            "scale_factor": {"type": "number", "description": "Scale factor", "default": 1.5},
                            # Advanced creation parameters
                            "sketches": {"type": "array", "items": {"type": "string"}, "description": "Sketches for loft"},
                            "profile_sketch": {"type": "string", "description": "Profile sketch for sweep"},
                            "path_sketch": {"type": "string", "description": "Path sketch for sweep"},
                            # Naming
                            "name": {"type": "string", "description": "Name for result object"}
                        },
                        "required": ["operation"]
                    }
                ),
                types.Tool(
                    name="view_control",
                    description="Smart dispatcher for all view, screenshot, and document operations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "View control operation",
                                "enum": [
                                    # View operations
                                    "screenshot", "set_view", "fit_all", "zoom_in", "zoom_out",
                                    # Document operations  
                                    "create_document", "save_document", "list_objects",
                                    # Selection operations
                                    "select_object", "clear_selection", "get_selection",
                                    # Object visibility
                                    "hide_object", "show_object", "delete_object",
                                    # History operations
                                    "undo", "redo",
                                    # Workbench control
                                    "activate_workbench"
                                ]
                            },
                            # Screenshot parameters
                            "width": {"type": "integer", "description": "Screenshot width", "default": 800},
                            "height": {"type": "integer", "description": "Screenshot height", "default": 600},
                            # View parameters
                            "view_type": {"type": "string", "description": "View orientation", 
                                         "enum": ["top", "front", "left", "right", "isometric", "axonometric"], 
                                         "default": "isometric"},
                            # Document parameters
                            "document_name": {"type": "string", "description": "Document name", "default": "Unnamed"},
                            "filename": {"type": "string", "description": "File path to save"},
                            # Object parameters
                            "object_name": {"type": "string", "description": "Object name for operations"},
                            # Workbench parameters
                            "workbench_name": {"type": "string", "description": "Workbench name to activate"}
                        },
                        "required": ["operation"]
                    }
                ),
                types.Tool(
                    name="execute_python",
                    description="Execute arbitrary Python code in FreeCAD context for power users and advanced operations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Python code to execute in FreeCAD context"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                types.Tool(
                    name="continue_selection",
                    description="Continue an interactive selection operation after selecting elements in FreeCAD",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation_id": {
                                "type": "string",
                                "description": "The operation ID from the awaiting_selection response"
                            }
                        },
                        "required": ["operation_id"]
                    }
                )
            ]
            return base_tools + smart_dispatchers
        
        return base_tools

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent]:
        """Handle tool calls with smart dispatcher routing"""
        
        if name == "check_freecad_connection":
            status = {
                "freecad_socket_exists": freecad_available,
                "socket_path": socket_path,
                "status": "FreeCAD running with AI Copilot workbench" if freecad_available 
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
            
        # Handle continue_selection tool
        elif name == "continue_selection":
            operation_id = arguments.get("operation_id") if arguments else None
            if not operation_id:
                return [types.TextContent(
                    type="text",
                    text="Error: operation_id is required to continue selection"
                )]
            
            # Send continuation command to FreeCAD
            response = await send_to_freecad("continue_selection", {
                "operation_id": operation_id
            })
            
            return [types.TextContent(
                type="text",
                text=response
            )]
            
        # Route smart dispatcher tools to socket with enhanced routing
        elif name in ["partdesign_operations", "part_operations", 
                      "view_control", "execute_python"]:
            args = arguments or {}
            
            # Check if this is a continuation from interactive selection
            if args.get("_continue_from_interactive"):
                # Extract the original operation details
                operation_id = args.get("operation_id")
                tool_name = args.get("tool_name") 
                original_args = args.get("original_args", {})
                
                # Add continuation flag
                continue_args = {
                    **original_args,
                    "_continue_selection": True,
                    "_operation_id": operation_id
                }
                
                response = await send_to_freecad(tool_name, continue_args)
            else:
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

    # Optional: Start health monitoring if debugging enabled
    async def health_check_loop():
        """Periodic health check for FreeCAD"""
        if not DEBUG_ENABLED or not monitor:
            return
            
        while True:
            try:
                status = monitor.perform_health_check()
                if not status['is_healthy']:
                    debugger.logger.error("FreeCAD health check FAILED!")
                    monitor.log_crash(status)
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                if debugger:
                    debugger.logger.error(f"Health check error: {e}")
                await asyncio.sleep(30)
    
    # Start health monitoring in background if enabled
    if DEBUG_ENABLED and monitor:
        health_task = asyncio.create_task(health_check_loop())
    
    # Run the server
    import mcp.server.stdio
    
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="freecad",
                    server_version="2.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    finally:
        # Export debug info on shutdown if debugging enabled
        if DEBUG_ENABLED and debugger:
            debugger.logger.info("="*80)
            debugger.logger.info("MCP Bridge shutting down - exporting debug info")
            debugger.logger.info("="*80)
            
            try:
                # Performance report
                perf_report = debugger.get_performance_report()
                debugger.logger.info(f"\n{perf_report}")
                
                # Export debug package
                debug_pkg = debugger.export_debug_package()
                debugger.logger.info(f"Debug package: {debug_pkg}")
                
                # Export crash report if there were crashes
                if monitor and monitor.crash_history:
                    crash_report = monitor.export_crash_report()
                    debugger.logger.info(f"Crash report: {crash_report}")
                    stats = monitor.get_crash_statistics()
                    debugger.logger.info(f"Crash statistics: {stats}")
            except Exception as e:
                if debugger:
                    debugger.logger.error(f"Error during shutdown export: {e}")

if __name__ == "__main__":
    asyncio.run(main())
