# MCP Bridge - Connects external Claude to embedded FreeCAD server
# This runs as a separate process that Claude can connect to

import asyncio
import json
import socket
import sys
from typing import Optional
import struct

class MCPBridge:
    """Bridge between Claude (external) and FreeCAD (internal) MCP server"""
    
    def __init__(self, host="localhost", port=5000):
        self.host = host
        self.port = port
        self.freecad_socket = None
        self.claude_reader = None
        self.claude_writer = None
        
    async def start(self):
        """Start the bridge server"""
        # This server listens for Claude connections
        server = await asyncio.start_server(
            self.handle_claude_connection,
            self.host, 
            self.port
        )
        
        print(f"MCP Bridge listening on {self.host}:{self.port}")
        print("Add this to Claude Desktop config:")
        print(f'''
"freecad-copilot": {{
  "command": "python",
  "args": ["{__file__}"],
  "env": {{}}
}}
        ''')
        
        async with server:
            await server.serve_forever()
            
    async def handle_claude_connection(self, reader, writer):
        """Handle connection from Claude"""
        self.claude_reader = reader
        self.claude_writer = writer
        
        # Connect to FreeCAD's internal socket
        await self.connect_to_freecad()
        
        # Bridge messages between Claude and FreeCAD
        await asyncio.gather(
            self.forward_claude_to_freecad(),
            self.forward_freecad_to_claude()
        )
        
    async def connect_to_freecad(self):
        """Connect to FreeCAD's internal MCP server"""
        # FreeCAD creates a named pipe/socket when workbench loads
        if sys.platform == "win32":
            # Windows named pipe
            pipe_name = r'\\\\.\\pipe\\freecad_mcp'
            # TODO: Implement Windows named pipe connection
        else:
            # Unix domain socket
            socket_path = "/tmp/freecad_mcp.sock"
            self.freecad_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                self.freecad_socket.connect(socket_path)
                print(f"Connected to FreeCAD at {socket_path}")
            except Exception as e:
                print(f"Failed to connect to FreeCAD: {e}")
                print("Make sure FreeCAD is running with AI Copilot workbench active")
                
    async def forward_claude_to_freecad(self):
        """Forward messages from Claude to FreeCAD"""
        while True:
            try:
                # Read from Claude (stdin or socket)
                data = await self.claude_reader.read(4096)
                if not data:
                    break
                    
                # Send to FreeCAD
                if self.freecad_socket:
                    self.freecad_socket.send(data)
                    
            except Exception as e:
                print(f"Error forwarding to FreeCAD: {e}")
                break
                
    async def forward_freecad_to_claude(self):
        """Forward messages from FreeCAD to Claude"""
        while self.freecad_socket:
            try:
                # Read from FreeCAD
                data = self.freecad_socket.recv(4096)
                if not data:
                    break
                    
                # Send to Claude
                self.claude_writer.write(data)
                await self.claude_writer.drain()
                
            except Exception as e:
                print(f"Error forwarding to Claude: {e}")
                break

# Alternative: Direct stdio mode for Claude Desktop
class MCPStdioBridge:
    """Bridge using stdio for Claude Desktop"""
    
    def __init__(self):
        self.freecad_socket = None
        
    async def start(self):
        """Start stdio bridge"""
        # Connect to FreeCAD
        await self.connect_to_freecad()
        
        # Use stdin/stdout for Claude
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout
        )
        writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, asyncio.get_event_loop())
        
        # Bridge messages
        await asyncio.gather(
            self.forward_stdin_to_freecad(reader),
            self.forward_freecad_to_stdout(writer)
        )
        
    async def connect_to_freecad(self):
        """Connect to FreeCAD's internal MCP server"""
        socket_path = "/tmp/freecad_mcp.sock" if sys.platform != "win32" else r'\\\\.\\pipe\\freecad_mcp'
        
        # Retry connection until FreeCAD is ready
        for i in range(10):
            try:
                if sys.platform == "win32":
                    # Windows implementation needed
                    pass
                else:
                    self.freecad_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    self.freecad_socket.connect(socket_path)
                    self.freecad_socket.setblocking(False)
                    
                print(f"Connected to FreeCAD", file=sys.stderr)
                return
            except Exception as e:
                await asyncio.sleep(2)
                
        raise Exception("Could not connect to FreeCAD after 10 attempts")
        
    async def forward_stdin_to_freecad(self, reader):
        """Forward stdin to FreeCAD"""
        loop = asyncio.get_event_loop()
        while True:
            data = await reader.read(4096)
            if not data:
                break
            if self.freecad_socket:
                await loop.sock_sendall(self.freecad_socket, data)
                
    async def forward_freecad_to_stdout(self, writer):
        """Forward FreeCAD to stdout"""
        loop = asyncio.get_event_loop()
        while True:
            if self.freecad_socket:
                data = await loop.sock_recv(self.freecad_socket, 4096)
                if not data:
                    break
                writer.write(data)
                await writer.drain()

if __name__ == "__main__":
    # Use stdio mode for Claude Desktop
    bridge = MCPStdioBridge()
    asyncio.run(bridge.start())