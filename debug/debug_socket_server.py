# Debug Socket Server for FreeCAD MCP - Enhanced Logging
# Minimal version with extensive logging to debug crashes

import FreeCAD
import FreeCADGui
import socket
import threading
import json
import os
import time
import traceback
import sys

class DebugFreeCADServer:
    """Minimal debug version of FreeCAD socket server with extensive logging"""
    
    def __init__(self):
        self.socket_path = "/tmp/freecad_mcp_debug.sock"
        self.server_socket = None
        self.is_running = False
        self.log_file = open("/tmp/freecad_debug.log", "w")
        
    def log(self, message):
        """Thread-safe logging"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}\n"
        print(log_msg.strip())  # Console
        self.log_file.write(log_msg)  # File
        self.log_file.flush()
        
    def start_server(self):
        """Start debug server"""
        try:
            self.log("=== DEBUG SERVER STARTING ===")
            self.log(f"Python version: {sys.version}")
            self.log(f"FreeCAD version: {FreeCAD.Version()}")
            self.log(f"Current documents: {list(FreeCAD.listDocuments().keys())}")
            
            # Remove existing socket
            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)
                
            # Create socket
            self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server_socket.bind(self.socket_path)
            self.server_socket.listen(1)
            self.is_running = True
            
            self.log(f"Debug server listening on {self.socket_path}")
            
            # Accept connections
            while self.is_running:
                try:
                    client, addr = self.server_socket.accept()
                    self.log("Client connected")
                    self.handle_client(client)
                except Exception as e:
                    self.log(f"Server loop error: {e}")
                    traceback.print_exc()
                    
        except Exception as e:
            self.log(f"Server start error: {e}")
            traceback.print_exc()
            
    def handle_client(self, client):
        """Handle client with extensive logging"""
        try:
            while True:
                data = client.recv(1024)
                if not data:
                    break
                    
                self.log(f"Received: {data.decode()}")
                
                try:
                    command = json.loads(data.decode())
                    tool = command.get('tool', '')
                    args = command.get('args', {})
                    
                    self.log(f"Processing tool: {tool}")
                    self.log(f"Args: {args}")
                    
                    # Process command safely
                    response = self.process_tool(tool, args)
                    
                    self.log(f"Response: {response}")
                    client.send(response.encode())
                    
                except json.JSONDecodeError as e:
                    self.log(f"JSON decode error: {e}")
                    client.send(b"JSON Error")
                except Exception as e:
                    self.log(f"Command processing error: {e}")
                    traceback.print_exc()
                    client.send(f"Error: {e}".encode())
                    
        except Exception as e:
            self.log(f"Client handler error: {e}")
            traceback.print_exc()
        finally:
            client.close()
            self.log("Client disconnected")
            
    def process_tool(self, tool, args):
        """Process tool with safety checks"""
        self.log(f"=== PROCESSING TOOL: {tool} ===")
        
        if tool == "test_echo":
            return f"Debug echo: {args.get('message', 'no message')}"
            
        elif tool == "execute_python":
            return self.safe_execute_python(args)
            
        elif tool == "check_state":
            return self.check_freecad_state()
            
        else:
            return f"Unknown tool: {tool}"
            
    def safe_execute_python(self, args):
        """Execute Python with extensive logging"""
        code = args.get('code', '')
        self.log(f"Executing Python code: {repr(code)}")
        
        try:
            # Pre-execution checks
            self.log("Pre-execution state check...")
            self.log(f"FreeCAD.ActiveDocument: {FreeCAD.ActiveDocument}")
            self.log(f"Document count: {len(FreeCAD.listDocuments())}")
            
            # Execute with logging
            self.log("Starting code execution...")
            
            # Capture stdout
            old_stdout = sys.stdout
            
            class LogCapture:
                def __init__(self, logger):
                    self.logger = logger
                def write(self, msg):
                    if msg.strip():
                        self.logger(f"CODE OUTPUT: {msg.strip()}")
                def flush(self):
                    pass
                    
            sys.stdout = LogCapture(self.log)
            
            try:
                exec(code, {'FreeCAD': FreeCAD, 'FreeCADGui': FreeCADGui})
                self.log("Code execution completed successfully")
                return "Code executed successfully"
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            self.log(f"Python execution error: {e}")
            self.log(f"Traceback: {traceback.format_exc()}")
            return f"Python error: {e}"
            
    def check_freecad_state(self):
        """Check FreeCAD state thoroughly"""
        try:
            state = {
                "version": str(FreeCAD.Version()),
                "documents": list(FreeCAD.listDocuments().keys()),
                "active_doc": str(FreeCAD.ActiveDocument) if FreeCAD.ActiveDocument else None,
                "gui_available": FreeCADGui is not None
            }
            
            if FreeCADGui:
                try:
                    wb = FreeCADGui.activeWorkbench()
                    state["workbench"] = wb.__class__.__name__ if wb else None
                except:
                    state["workbench"] = "Error accessing workbench"
                    
            return json.dumps(state, indent=2)
            
        except Exception as e:
            return f"State check error: {e}"

# Global server instance
debug_server = None

def start_debug_server():
    """Start the debug server"""
    global debug_server
    try:
        debug_server = DebugFreeCADServer()
        debug_server.start_server()
    except Exception as e:
        print(f"Failed to start debug server: {e}")
        traceback.print_exc()

def stop_debug_server():
    """Stop the debug server"""
    global debug_server
    if debug_server:
        debug_server.is_running = False
        if debug_server.server_socket:
            debug_server.server_socket.close()
        debug_server.log_file.close()

# Auto-start when imported
if __name__ == "__main__":
    start_debug_server()