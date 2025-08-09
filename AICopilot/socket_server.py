# FreeCAD Socket Server for MCP Communication
# Runs inside FreeCAD to receive commands from external MCP bridge

import FreeCAD
import FreeCADGui
import socket
import threading
import json
import os
import time
import asyncio
from typing import Dict, Any

# Import the ReAct agent
try:
    from freecad_agent import FreeCADReActAgent
except ImportError as e:
    FreeCAD.Console.PrintWarning(f"Could not import FreeCADReActAgent: {e}\n")
    FreeCADReActAgent = None

class FreeCADSocketServer:
    """Socket server that runs inside FreeCAD to receive MCP commands"""
    
    def __init__(self):
        self.socket_path = "/tmp/freecad_mcp.sock"
        self.server_socket = None
        self.is_running = False
        self.client_connections = []
        
        # Initialize the ReAct agent
        if FreeCADReActAgent:
            self.agent = FreeCADReActAgent(self)
            FreeCAD.Console.PrintMessage("Socket server initialized with ReAct Agent\n")
        else:
            self.agent = None
            FreeCAD.Console.PrintMessage("Socket server initialized without agent (import failed)\n")
            
    def start_server(self):
        """Start the Unix socket server"""
        try:
            # Remove existing socket file
            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)
                
            # Create Unix domain socket
            self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server_socket.bind(self.socket_path)
            self.server_socket.listen(5)
            
            self.is_running = True
            
            # Start server thread
            server_thread = threading.Thread(target=self._server_loop, daemon=True)
            server_thread.start()
            
            FreeCAD.Console.PrintMessage(f"Socket server started on {self.socket_path}\n")
            return True
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"Failed to start socket server: {e}\n")
            return False
            
    def _server_loop(self):
        """Main server loop to accept connections"""
        while self.is_running and self.server_socket:
            try:
                client_socket, _ = self.server_socket.accept()
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()
                self.client_connections.append(client_socket)
                
            except Exception as e:
                if self.is_running:
                    FreeCAD.Console.PrintError(f"Server loop error: {e}\n")
                break
                
    def _handle_client(self, client_socket):
        """Handle individual client connections"""
        try:
            while self.is_running:
                # Receive data
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                # Process the command
                response = self._process_command(data.decode('utf-8'))
                
                # Send response
                if response:
                    client_socket.send(response.encode('utf-8'))
                    
        except Exception as e:
            FreeCAD.Console.PrintError(f"Client handler error: {e}\n")
        finally:
            client_socket.close()
            if client_socket in self.client_connections:
                self.client_connections.remove(client_socket)
                
    def _process_command(self, command_str: str) -> str:
        """Process incoming command and return response"""
        try:
            # Parse JSON command
            command = json.loads(command_str)
            
            # Extract tool name and arguments
            tool_name = command.get('tool')
            args = command.get('args', {})
            
            # Route to appropriate handler
            result = self._execute_tool(tool_name, args)
            
            return json.dumps({
                "success": True,
                "result": result
            })
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })
            
    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute the requested tool"""
        
        # Map tool names to implementations
        if tool_name == "create_box":
            return self._create_box(args)
        elif tool_name == "create_cylinder":
            return self._create_cylinder(args)
        elif tool_name == "create_sphere":
            return self._create_sphere(args)
        elif tool_name == "get_screenshot":
            return self._get_screenshot(args)
        elif tool_name == "list_all_objects":
            return self._list_all_objects(args)
        elif tool_name == "activate_workbench":
            return self._activate_workbench(args)
        elif tool_name == "execute_python":
            return self._execute_python(args)
        # GUI Control Tools
        elif tool_name == "run_command":
            return self._run_command(args)
        elif tool_name == "new_document":
            return self._new_document(args)
        elif tool_name == "save_document":
            return self._save_document(args)
        elif tool_name == "open_document":
            return self._open_document(args)
        elif tool_name == "set_view":
            return self._set_view(args)
        elif tool_name == "fit_all":
            return self._fit_all(args)
        elif tool_name == "select_object":
            return self._select_object(args)
        elif tool_name == "clear_selection":
            return self._clear_selection(args)
        elif tool_name == "get_selection":
            return self._get_selection(args)
        elif tool_name == "hide_object":
            return self._hide_object(args)
        elif tool_name == "show_object":
            return self._show_object(args)
        elif tool_name == "delete_object":
            return self._delete_object(args)
        elif tool_name == "undo":
            return self._undo(args)
        elif tool_name == "redo":
            return self._redo(args)
        elif tool_name == "ai_agent":
            return self._ai_agent(args)
        else:
            return f"Unknown tool: {tool_name}"
            
    def _create_box(self, args: Dict[str, Any]) -> str:
        """Create a box with specified dimensions"""
        try:
            length = args.get('length', 10)
            width = args.get('width', 10)  
            height = args.get('height', 10)
            x = args.get('x', 0)
            y = args.get('y', 0)
            z = args.get('z', 0)
            
            # Create document if needed
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            
            # Create box
            box = doc.addObject("Part::Box", "Box")
            box.Length = length
            box.Width = width
            box.Height = height
            box.Placement.Base = FreeCAD.Vector(x, y, z)
            
            # Recompute and fit view
            doc.recompute()
            if FreeCADGui.ActiveDocument:
                FreeCADGui.SendMsgToActiveView("ViewFit")
            
            return f"Created box: {box.Name} ({length}x{width}x{height}mm) at ({x},{y},{z})"
            
        except Exception as e:
            return f"Error creating box: {e}"
            
    def _create_cylinder(self, args: Dict[str, Any]) -> str:
        """Create a cylinder with specified dimensions"""
        try:
            radius = args.get('radius', 5)
            height = args.get('height', 10)
            x = args.get('x', 0)
            y = args.get('y', 0)
            z = args.get('z', 0)
            
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            
            cylinder = doc.addObject("Part::Cylinder", "Cylinder")
            cylinder.Radius = radius
            cylinder.Height = height
            cylinder.Placement.Base = FreeCAD.Vector(x, y, z)
            
            doc.recompute()
            if FreeCADGui.ActiveDocument:
                FreeCADGui.SendMsgToActiveView("ViewFit")
            
            return f"Created cylinder: {cylinder.Name} (R{radius}, H{height}) at ({x},{y},{z})"
            
        except Exception as e:
            return f"Error creating cylinder: {e}"
            
    def _create_sphere(self, args: Dict[str, Any]) -> str:
        """Create a sphere with specified radius"""
        try:
            radius = args.get('radius', 5)
            x = args.get('x', 0)
            y = args.get('y', 0)
            z = args.get('z', 0)
            
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            
            sphere = doc.addObject("Part::Sphere", "Sphere")
            sphere.Radius = radius
            sphere.Placement.Base = FreeCAD.Vector(x, y, z)
            
            doc.recompute()
            if FreeCADGui.ActiveDocument:
                FreeCADGui.SendMsgToActiveView("ViewFit")
            
            return f"Created sphere: {sphere.Name} (R{radius}) at ({x},{y},{z})"
            
        except Exception as e:
            return f"Error creating sphere: {e}"
            
    def _get_screenshot(self, args: Dict[str, Any]) -> str:
        """Take screenshot of current view"""
        try:
            if not FreeCADGui.ActiveDocument:
                return "No active document for screenshot"
                
            import tempfile
            import base64
            
            width = args.get('width', 800)
            height = args.get('height', 600)
            
            view = FreeCADGui.ActiveDocument.ActiveView
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                
            # Save image
            view.saveImage(tmp_path, width, height, "White")
            
            # Convert to base64
            with open(tmp_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Cleanup
            os.unlink(tmp_path)
            
            return json.dumps({
                "image": f"data:image/png;base64,{image_data}",
                "width": width,
                "height": height
            })
            
        except Exception as e:
            return f"Error taking screenshot: {e}"
            
    def _list_all_objects(self, args: Dict[str, Any]) -> str:
        """List all objects in active document"""
        try:
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            objects = []
            for obj in doc.Objects:
                objects.append({
                    "name": obj.Name,
                    "type": obj.TypeId,
                    "label": obj.Label
                })
                
            return json.dumps(objects)
            
        except Exception as e:
            return f"Error listing objects: {e}"
            
    def _activate_workbench(self, args: Dict[str, Any]) -> str:
        """Activate specified workbench"""
        try:
            workbench_name = args.get('workbench_name', '')
            FreeCADGui.activateWorkbench(workbench_name)
            return f"Activated workbench: {workbench_name}"
        except Exception as e:
            return f"Error activating workbench: {e}"
            
    def _execute_python(self, args: Dict[str, Any]) -> str:
        """Execute Python code in FreeCAD context"""
        try:
            code = args.get('code', '')
            
            # Create execution context
            exec_context = {
                'FreeCAD': FreeCAD,
                'FreeCADGui': FreeCADGui,
                'doc': FreeCAD.ActiveDocument
            }
            
            # Execute code
            exec(code, exec_context)
            
            # Return result if available
            if 'result' in exec_context:
                return str(exec_context['result'])
            else:
                return "Code executed successfully"
                
        except Exception as e:
            return f"Python execution error: {e}"
            
    # GUI Control Tools
    def _run_command(self, args: Dict[str, Any]) -> str:
        """Run a FreeCAD GUI command"""
        try:
            command = args.get('command', '')
            FreeCADGui.runCommand(command)
            return f"Executed command: {command}"
        except Exception as e:
            return f"Error running command: {e}"
            
    def _new_document(self, args: Dict[str, Any]) -> str:
        """Create a new document"""
        try:
            name = args.get('name', 'Unnamed')
            doc = FreeCAD.newDocument(name)
            return f"Created new document: {doc.Name}"
        except Exception as e:
            return f"Error creating document: {e}"
            
    def _save_document(self, args: Dict[str, Any]) -> str:
        """Save the current document"""
        try:
            filename = args.get('filename', '')
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document to save"
                
            if filename:
                doc.saveAs(filename)
                return f"Document saved as: {filename}"
            else:
                doc.save()
                return f"Document saved: {doc.Name}"
        except Exception as e:
            return f"Error saving document: {e}"
            
    def _open_document(self, args: Dict[str, Any]) -> str:
        """Open a document"""
        try:
            filename = args.get('filename', '')
            doc = FreeCAD.openDocument(filename)
            return f"Opened document: {doc.Name}"
        except Exception as e:
            return f"Error opening document: {e}"
            
    def _set_view(self, args: Dict[str, Any]) -> str:
        """Set the 3D view to a specific orientation"""
        try:
            view_type = args.get('view_type', 'isometric').lower()
            
            if not FreeCADGui.ActiveDocument:
                return "No active document for view change"
                
            view = FreeCADGui.ActiveDocument.ActiveView
            
            if view_type == 'top':
                view.viewTop()
            elif view_type == 'bottom':
                view.viewBottom()
            elif view_type == 'front':
                view.viewFront()
            elif view_type == 'rear':
                view.viewRear()
            elif view_type == 'left':
                view.viewLeft()
            elif view_type == 'right':
                view.viewRight()
            elif view_type == 'isometric' or view_type == 'iso':
                view.viewIsometric()
            elif view_type == 'axonometric':
                view.viewAxonometric()
            else:
                return f"Unknown view type: {view_type}"
                
            return f"View set to: {view_type}"
        except Exception as e:
            return f"Error setting view: {e}"
            
    def _fit_all(self, args: Dict[str, Any]) -> str:
        """Fit all objects in the view"""
        try:
            if FreeCADGui.ActiveDocument:
                FreeCADGui.SendMsgToActiveView("ViewFit")
                return "View fitted to all objects"
            else:
                return "No active document"
        except Exception as e:
            return f"Error fitting view: {e}"
            
    def _select_object(self, args: Dict[str, Any]) -> str:
        """Select an object"""
        try:
            object_name = args.get('object_name', '')
            doc_name = args.get('doc_name', '')
            
            if not doc_name:
                doc = FreeCAD.ActiveDocument
                doc_name = doc.Name if doc else ""
                
            if not doc_name:
                return "No document specified or active"
                
            FreeCADGui.Selection.addSelection(doc_name, object_name)
            return f"Selected object: {object_name}"
        except Exception as e:
            return f"Error selecting object: {e}"
            
    def _clear_selection(self, args: Dict[str, Any]) -> str:
        """Clear all selections"""
        try:
            FreeCADGui.Selection.clearSelection()
            return "Selection cleared"
        except Exception as e:
            return f"Error clearing selection: {e}"
            
    def _get_selection(self, args: Dict[str, Any]) -> str:
        """Get current selection"""
        try:
            selected = FreeCADGui.Selection.getSelectionEx()
            selection_info = []
            
            for sel in selected:
                selection_info.append({
                    "document": sel.DocumentName,
                    "object": sel.ObjectName,
                    "sub_elements": sel.SubElementNames
                })
                
            return json.dumps(selection_info)
        except Exception as e:
            return f"Error getting selection: {e}"
            
    def _hide_object(self, args: Dict[str, Any]) -> str:
        """Hide an object"""
        try:
            object_name = args.get('object_name', '')
            doc = FreeCAD.ActiveDocument
            
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object not found: {object_name}"
                
            obj.ViewObject.Visibility = False
            return f"Hidden object: {object_name}"
        except Exception as e:
            return f"Error hiding object: {e}"
            
    def _show_object(self, args: Dict[str, Any]) -> str:
        """Show an object"""
        try:
            object_name = args.get('object_name', '')
            doc = FreeCAD.ActiveDocument
            
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object not found: {object_name}"
                
            obj.ViewObject.Visibility = True
            return f"Shown object: {object_name}"
        except Exception as e:
            return f"Error showing object: {e}"
            
    def _delete_object(self, args: Dict[str, Any]) -> str:
        """Delete an object"""
        try:
            object_name = args.get('object_name', '')
            doc = FreeCAD.ActiveDocument
            
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object not found: {object_name}"
                
            doc.removeObject(object_name)
            doc.recompute()
            return f"Deleted object: {object_name}"
        except Exception as e:
            return f"Error deleting object: {e}"
            
    def _undo(self, args: Dict[str, Any]) -> str:
        """Undo last operation"""
        try:
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            FreeCADGui.runCommand("Std_Undo")
            return "Undo completed"
        except Exception as e:
            return f"Error undoing: {e}"
            
    def _redo(self, args: Dict[str, Any]) -> str:
        """Redo last undone operation"""
        try:
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            FreeCADGui.runCommand("Std_Redo")
            return "Redo completed"
        except Exception as e:
            return f"Error redoing: {e}"
            
    def _ai_agent(self, args: Dict[str, Any]) -> str:
        """Handle requests through the ReAct Agent"""
        try:
            if not self.agent:
                return "AI Agent not available (import failed)"
                
            request = args.get('request', '')
            if not request:
                return "No request provided for AI agent"
                
            # Process through the ReAct agent
            result = self.agent.process_request(request)
            return result
            
        except Exception as e:
            return f"AI Agent error: {e}"
            
    def stop_server(self):
        """Stop the socket server"""
        self.is_running = False
        
        # Close all client connections
        for client in self.client_connections[:]:
            client.close()
        self.client_connections.clear()
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
            
        # Remove socket file
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            
        FreeCAD.Console.PrintMessage("Socket server stopped\n")