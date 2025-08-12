#!/opt/homebrew/bin/python3.11
"""
Debug version of FreeCAD MCP Bridge to test startup
"""

import sys
import os

print("Debug bridge starting...", file=sys.stderr)

try:
    import mcp.types as types
    from mcp.server import Server
    print("MCP imports successful", file=sys.stderr)
except ImportError as e:
    print(f"MCP import failed: {e}", file=sys.stderr)
    sys.exit(1)

try:
    # Create server
    server = Server("freecad")
    print("Server created", file=sys.stderr)
    
    # Check socket
    socket_path = "/tmp/freecad_mcp.sock"
    socket_exists = os.path.exists(socket_path)
    print(f"Socket exists: {socket_exists}", file=sys.stderr)
    
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List tools including continue_selection"""
        return [
            types.Tool(
                name="test_tool",
                description="Test tool",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="continue_selection", 
                description="Continue selection workflow",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation_id": {"type": "string", "description": "Operation ID"}
                    },
                    "required": ["operation_id"]
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle tool calls"""
        return [types.TextContent(type="text", text=f"Tool {name} called")]
    
    print("Handlers registered", file=sys.stderr)
    
    # Try to run
    import asyncio
    import mcp.server.stdio
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions
    
    async def main():
        print("Starting stdio server...", file=sys.stderr)
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="freecad-debug",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    
    if __name__ == "__main__":
        print("Running main...", file=sys.stderr)
        asyncio.run(main())
        
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)