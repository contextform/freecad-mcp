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
        elif tool_name == "create_cone":
            return self._create_cone(args)
        elif tool_name == "create_torus":
            return self._create_torus(args)
        elif tool_name == "create_wedge":
            return self._create_wedge(args)
        # Boolean Operations
        elif tool_name == "fuse_objects":
            return self._fuse_objects(args)
        elif tool_name == "cut_objects":
            return self._cut_objects(args)
        elif tool_name == "common_objects":
            return self._common_objects(args)
        # Transformations
        elif tool_name == "move_object":
            return self._move_object(args)
        elif tool_name == "rotate_object":
            return self._rotate_object(args)
        elif tool_name == "copy_object":
            return self._copy_object(args)
        elif tool_name == "array_object":
            return self._array_object(args)
        # Part Design
        elif tool_name == "create_sketch":
            return self._create_sketch(args)
        elif tool_name == "pad_sketch":
            return self._pad_sketch(args)
        elif tool_name == "pocket_sketch":
            return self._pocket_sketch(args)
        elif tool_name == "fillet_edges":
            return self._fillet_edges(args)
        # Analysis
        elif tool_name == "measure_distance":
            return self._measure_distance(args)
        elif tool_name == "get_volume":
            return self._get_volume(args)
        elif tool_name == "get_bounding_box":
            return self._get_bounding_box(args)
        elif tool_name == "get_mass_properties":
            return self._get_mass_properties(args)
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
            
    def _create_cone(self, args: Dict[str, Any]) -> str:
        """Create a cone with specified radii and height"""
        try:
            radius1 = args.get('radius1', 5)  # Bottom radius
            radius2 = args.get('radius2', 0)  # Top radius
            height = args.get('height', 10)
            x = args.get('x', 0)
            y = args.get('y', 0)
            z = args.get('z', 0)
            
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            
            cone = doc.addObject("Part::Cone", "Cone")
            cone.Radius1 = radius1
            cone.Radius2 = radius2
            cone.Height = height
            cone.Placement.Base = FreeCAD.Vector(x, y, z)
            
            doc.recompute()
            if FreeCADGui.ActiveDocument:
                FreeCADGui.SendMsgToActiveView("ViewFit")
            
            return f"Created cone: {cone.Name} (R1{radius1}, R2{radius2}, H{height}) at ({x},{y},{z})"
            
        except Exception as e:
            return f"Error creating cone: {e}"
            
    def _create_torus(self, args: Dict[str, Any]) -> str:
        """Create a torus (donut shape) with specified radii"""
        try:
            radius1 = args.get('radius1', 10)  # Major radius
            radius2 = args.get('radius2', 3)   # Minor radius
            x = args.get('x', 0)
            y = args.get('y', 0)
            z = args.get('z', 0)
            
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            
            torus = doc.addObject("Part::Torus", "Torus")
            torus.Radius1 = radius1
            torus.Radius2 = radius2
            torus.Placement.Base = FreeCAD.Vector(x, y, z)
            
            doc.recompute()
            if FreeCADGui.ActiveDocument:
                FreeCADGui.SendMsgToActiveView("ViewFit")
            
            return f"Created torus: {torus.Name} (R1{radius1}, R2{radius2}) at ({x},{y},{z})"
            
        except Exception as e:
            return f"Error creating torus: {e}"
            
    def _create_wedge(self, args: Dict[str, Any]) -> str:
        """Create a wedge (triangular prism) with specified dimensions"""
        try:
            xmin = args.get('xmin', 0)
            ymin = args.get('ymin', 0)
            zmin = args.get('zmin', 0)
            x2min = args.get('x2min', 2)
            x2max = args.get('x2max', 8)
            xmax = args.get('xmax', 10)
            ymax = args.get('ymax', 10)
            zmax = args.get('zmax', 10)
            
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            
            wedge = doc.addObject("Part::Wedge", "Wedge")
            wedge.Xmin = xmin
            wedge.Ymin = ymin
            wedge.Zmin = zmin
            wedge.X2min = x2min
            wedge.X2max = x2max
            wedge.Xmax = xmax
            wedge.Ymax = ymax
            wedge.Zmax = zmax
            
            doc.recompute()
            if FreeCADGui.ActiveDocument:
                FreeCADGui.SendMsgToActiveView("ViewFit")
            
            return f"Created wedge: {wedge.Name} ({xmax}x{ymax}x{zmax}) at origin"
            
        except Exception as e:
            return f"Error creating wedge: {e}"
            
    # === Boolean Operations ===
    def _fuse_objects(self, args: Dict[str, Any]) -> str:
        """Fuse (union) multiple objects together"""
        try:
            objects = args.get('objects', [])
            name = args.get('name', 'Fusion')
            
            if len(objects) < 2:
                return "Need at least 2 objects to fuse"
                
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            # Get object references
            objs = []
            for obj_name in objects:
                obj = doc.getObject(obj_name)
                if obj:
                    objs.append(obj)
                else:
                    return f"Object not found: {obj_name}"
                    
            # Create fusion
            fusion = doc.addObject("Part::MultiFuse", name)
            fusion.Shapes = objs
            doc.recompute()
            
            return f"Created fusion: {fusion.Name} from {len(objects)} objects"
            
        except Exception as e:
            return f"Error fusing objects: {e}"
            
    def _cut_objects(self, args: Dict[str, Any]) -> str:
        """Cut (subtract) tools from base object"""
        try:
            base = args.get('base', '')
            tools = args.get('tools', [])
            name = args.get('name', 'Cut')
            
            if not base or not tools:
                return "Need base object and tool objects"
                
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            # Get object references
            base_obj = doc.getObject(base)
            if not base_obj:
                return f"Base object not found: {base}"
                
            tool_objs = []
            for tool_name in tools:
                tool_obj = doc.getObject(tool_name)
                if tool_obj:
                    tool_objs.append(tool_obj)
                else:
                    return f"Tool object not found: {tool_name}"
                    
            # Create cut
            cut = doc.addObject("Part::Cut", name)
            cut.Base = base_obj
            cut.Tool = tool_objs[0] if len(tool_objs) == 1 else tool_objs
            doc.recompute()
            
            return f"Created cut: {cut.Name} from {base} minus {len(tools)} tools"
            
        except Exception as e:
            return f"Error cutting objects: {e}"
            
    def _common_objects(self, args: Dict[str, Any]) -> str:
        """Find intersection of multiple objects"""
        try:
            objects = args.get('objects', [])
            name = args.get('name', 'Common')
            
            if len(objects) < 2:
                return "Need at least 2 objects for intersection"
                
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            # Get object references
            objs = []
            for obj_name in objects:
                obj = doc.getObject(obj_name)
                if obj:
                    objs.append(obj)
                else:
                    return f"Object not found: {obj_name}"
                    
            # Create common
            common = doc.addObject("Part::MultiCommon", name)
            common.Shapes = objs
            doc.recompute()
            
            return f"Created intersection: {common.Name} from {len(objects)} objects"
            
        except Exception as e:
            return f"Error finding intersection: {e}"
    
    # === Transformation Tools ===
    def _move_object(self, args: Dict[str, Any]) -> str:
        """Move an object to new position"""
        try:
            object_name = args.get('object_name', '')
            x = args.get('x', 0)
            y = args.get('y', 0)
            z = args.get('z', 0)
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object not found: {object_name}"
                
            # Move object
            obj.Placement.Base = FreeCAD.Vector(
                obj.Placement.Base.x + x,
                obj.Placement.Base.y + y,
                obj.Placement.Base.z + z
            )
            doc.recompute()
            
            return f"Moved {object_name} by ({x}, {y}, {z})"
            
        except Exception as e:
            return f"Error moving object: {e}"
            
    def _rotate_object(self, args: Dict[str, Any]) -> str:
        """Rotate an object around axis"""
        try:
            object_name = args.get('object_name', '')
            axis = args.get('axis', 'z')
            angle = args.get('angle', 90)
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object not found: {object_name}"
                
            # Set rotation axis
            axis_vector = FreeCAD.Vector(0, 0, 1)  # default Z
            if axis.lower() == 'x':
                axis_vector = FreeCAD.Vector(1, 0, 0)
            elif axis.lower() == 'y':
                axis_vector = FreeCAD.Vector(0, 1, 0)
                
            # Rotate object
            rotation = FreeCAD.Rotation(axis_vector, angle)
            obj.Placement.Rotation = obj.Placement.Rotation.multiply(rotation)
            doc.recompute()
            
            return f"Rotated {object_name} by {angle}° around {axis.upper()}-axis"
            
        except Exception as e:
            return f"Error rotating object: {e}"
            
    def _copy_object(self, args: Dict[str, Any]) -> str:
        """Create a copy of an object"""
        try:
            object_name = args.get('object_name', '')
            name = args.get('name', 'Copy')
            x = args.get('x', 0)
            y = args.get('y', 0)
            z = args.get('z', 0)
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object not found: {object_name}"
                
            # Create copy
            copy = doc.copyObject(obj)
            copy.Label = name
            copy.Placement.Base = FreeCAD.Vector(
                obj.Placement.Base.x + x,
                obj.Placement.Base.y + y,
                obj.Placement.Base.z + z
            )
            doc.recompute()
            
            return f"Created copy: {copy.Name} at offset ({x}, {y}, {z})"
            
        except Exception as e:
            return f"Error copying object: {e}"
            
    def _array_object(self, args: Dict[str, Any]) -> str:
        """Create linear array of object"""
        try:
            object_name = args.get('object_name', '')
            count = args.get('count', 3)
            spacing_x = args.get('spacing_x', 10)
            spacing_y = args.get('spacing_y', 0)
            spacing_z = args.get('spacing_z', 0)
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object not found: {object_name}"
                
            # Create array copies
            copies = []
            for i in range(1, count):  # Start from 1 (original is 0)
                copy = doc.copyObject(obj)
                copy.Label = f"{obj.Label}_Array{i}"
                copy.Placement.Base = FreeCAD.Vector(
                    obj.Placement.Base.x + (spacing_x * i),
                    obj.Placement.Base.y + (spacing_y * i),
                    obj.Placement.Base.z + (spacing_z * i)
                )
                copies.append(copy.Name)
                
            doc.recompute()
            
            return f"Created array: {count} copies of {object_name} with spacing ({spacing_x}, {spacing_y}, {spacing_z})"
            
        except Exception as e:
            return f"Error creating array: {e}"
    
    # === Part Design Tools ===
    def _create_sketch(self, args: Dict[str, Any]) -> str:
        """Create a new sketch on specified plane"""
        try:
            plane = args.get('plane', 'XY')
            name = args.get('name', 'Sketch')
            
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            
            # Create sketch
            sketch = doc.addObject('Sketcher::SketchObject', name)
            
            # Set plane
            if plane.upper() == 'XY':
                sketch.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0), FreeCAD.Rotation(0,0,0,1))
            elif plane.upper() == 'XZ':
                sketch.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0), FreeCAD.Rotation(1,0,0,1))
            elif plane.upper() == 'YZ':
                sketch.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0), FreeCAD.Rotation(0,1,0,1))
                
            doc.recompute()
            
            return f"Created sketch: {sketch.Name} on {plane} plane"
            
        except Exception as e:
            return f"Error creating sketch: {e}"
            
    def _pad_sketch(self, args: Dict[str, Any]) -> str:
        """Extrude a sketch to create solid (pad)"""
        try:
            sketch_name = args.get('sketch_name', '')
            length = args.get('length', 10)
            name = args.get('name', 'Pad')
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            sketch = doc.getObject(sketch_name)
            if not sketch:
                return f"Sketch not found: {sketch_name}"
                
            # Create pad
            pad = doc.addObject("PartDesign::Pad", name)
            pad.Profile = sketch
            pad.Length = length
            doc.recompute()
            
            return f"Created pad: {pad.Name} from {sketch_name} with length {length}mm"
            
        except Exception as e:
            return f"Error creating pad: {e}"
            
    def _pocket_sketch(self, args: Dict[str, Any]) -> str:
        """Cut a sketch from solid (pocket)"""
        try:
            sketch_name = args.get('sketch_name', '')
            length = args.get('length', 5)
            name = args.get('name', 'Pocket')
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            sketch = doc.getObject(sketch_name)
            if not sketch:
                return f"Sketch not found: {sketch_name}"
                
            # Create pocket
            pocket = doc.addObject("PartDesign::Pocket", name)
            pocket.Profile = sketch
            pocket.Length = length
            doc.recompute()
            
            return f"Created pocket: {pocket.Name} from {sketch_name} with depth {length}mm"
            
        except Exception as e:
            return f"Error creating pocket: {e}"
            
    def _fillet_edges(self, args: Dict[str, Any]) -> str:
        """Add fillets to object edges"""
        try:
            object_name = args.get('object_name', '')
            radius = args.get('radius', 1)
            name = args.get('name', 'Fillet')
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object not found: {object_name}"
                
            # Create fillet (simplified - fillets all edges)
            fillet = doc.addObject("Part::Fillet", name)
            fillet.Base = obj
            
            # Add all edges with same radius (simplified approach)
            if hasattr(obj, 'Shape') and obj.Shape.Edges:
                edge_list = []
                for i, edge in enumerate(obj.Shape.Edges):
                    edge_list.append((i+1, radius, radius))
                fillet.Edges = edge_list
                
            doc.recompute()
            
            return f"Created fillet: {fillet.Name} on {object_name} with radius {radius}mm"
            
        except Exception as e:
            return f"Error creating fillet: {e}"
    
    # === Analysis Tools ===
    def _measure_distance(self, args: Dict[str, Any]) -> str:
        """Measure distance between two objects"""
        try:
            object1 = args.get('object1', '')
            object2 = args.get('object2', '')
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj1 = doc.getObject(object1)
            obj2 = doc.getObject(object2)
            
            if not obj1:
                return f"Object not found: {object1}"
            if not obj2:
                return f"Object not found: {object2}"
                
            # Calculate distance between centers of mass
            if hasattr(obj1, 'Shape') and hasattr(obj2, 'Shape'):
                center1 = obj1.Shape.CenterOfMass
                center2 = obj2.Shape.CenterOfMass
                distance = center1.distanceToPoint(center2)
                
                return f"Distance between {object1} and {object2}: {distance:.2f} mm"
            else:
                return "Objects must have Shape property for distance measurement"
                
        except Exception as e:
            return f"Error measuring distance: {e}"
            
    def _get_volume(self, args: Dict[str, Any]) -> str:
        """Calculate volume of an object"""
        try:
            object_name = args.get('object_name', '')
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object not found: {object_name}"
                
            if hasattr(obj, 'Shape'):
                volume = obj.Shape.Volume
                return f"Volume of {object_name}: {volume:.2f} mm³"
            else:
                return "Object must have Shape property for volume calculation"
                
        except Exception as e:
            return f"Error calculating volume: {e}"
            
    def _get_bounding_box(self, args: Dict[str, Any]) -> str:
        """Get bounding box dimensions of an object"""
        try:
            object_name = args.get('object_name', '')
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object not found: {object_name}"
                
            if hasattr(obj, 'Shape'):
                bb = obj.Shape.BoundBox
                return f"Bounding box of {object_name}:\n" + \
                       f"  X: {bb.XMin:.2f} to {bb.XMax:.2f} mm (length: {bb.XLength:.2f})\n" + \
                       f"  Y: {bb.YMin:.2f} to {bb.YMax:.2f} mm (width: {bb.YLength:.2f})\n" + \
                       f"  Z: {bb.ZMin:.2f} to {bb.ZMax:.2f} mm (height: {bb.ZLength:.2f})"
            else:
                return "Object must have Shape property for bounding box calculation"
                
        except Exception as e:
            return f"Error calculating bounding box: {e}"
            
    def _get_mass_properties(self, args: Dict[str, Any]) -> str:
        """Get mass properties of an object"""
        try:
            object_name = args.get('object_name', '')
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object not found: {object_name}"
                
            if hasattr(obj, 'Shape'):
                shape = obj.Shape
                volume = shape.Volume
                center_of_mass = shape.CenterOfMass
                
                # Calculate surface area
                area = 0
                for face in shape.Faces:
                    area += face.Area
                
                return f"Mass properties of {object_name}:\n" + \
                       f"  Volume: {volume:.2f} mm³\n" + \
                       f"  Surface Area: {area:.2f} mm²\n" + \
                       f"  Center of Mass: ({center_of_mass.x:.2f}, {center_of_mass.y:.2f}, {center_of_mass.z:.2f})"
            else:
                return "Object must have Shape property for mass properties calculation"
                
        except Exception as e:
            return f"Error calculating mass properties: {e}"
    
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
        """Create a new document - safely creates without closing existing"""
        try:
            name = args.get('name', 'Unnamed')
            
            # Try the safer GUI command approach first
            try:
                import FreeCADGui
                if FreeCADGui:
                    # Use GUI command which handles threading better
                    FreeCADGui.runCommand('Std_New', 0)
                    
                    # Wait a moment for document creation
                    import time
                    time.sleep(0.1)
                    
                    # Set the document label if requested
                    if FreeCAD.ActiveDocument and name != 'Unnamed':
                        FreeCAD.ActiveDocument.Label = name
                        
                    return f"Created new document: {name}"
            except:
                pass
            
            # Fallback: Try direct API with error handling
            try:
                doc = FreeCAD.newDocument(name)
                return f"Created new document: {doc.Name}"
            except:
                # If both methods fail, just report error
                return "Unable to create new document - try using File menu directly"
                
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