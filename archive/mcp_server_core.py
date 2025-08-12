# Core Embedded MCP Server - Direct FreeCAD Access
# Runs INSIDE FreeCAD with full access to everything

import FreeCAD
import FreeCADGui
import Part
import Sketcher
import Draft
import asyncio
import json
import socket
import os
import sys
import threading
from typing import Any, Dict, List, Optional
from mcp import Server, Tool
from mcp.types import TextContent

class EmbeddedFreeCADMCP:
    """MCP Server with COMPLETE FreeCAD access"""
    
    def __init__(self):
        self.server = Server("freecad-embedded")
        self.socket_server = None
        self.socket_path = "/tmp/freecad_mcp.sock"
        
        # Register ALL FreeCAD operations as tools
        self._register_all_tools()
        
        # Start socket server for bridge
        self._start_socket_server()
        
    def _register_all_tools(self):
        """Expose EVERYTHING FreeCAD can do"""
        
        # ===== DOCUMENT OPERATIONS =====
        @self.server.tool()
        async def new_document(name: str = "Unnamed") -> str:
            """Create new FreeCAD document"""
            doc = FreeCAD.newDocument(name)
            return f"Created document: {doc.Name}"
            
        @self.server.tool()
        async def open_document(filepath: str) -> str:
            """Open existing FreeCAD file"""
            doc = FreeCAD.open(filepath)
            return f"Opened: {doc.Name}"
            
        @self.server.tool()
        async def save_document(filepath: Optional[str] = None) -> str:
            """Save current document"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
            if filepath:
                doc.saveAs(filepath)
            else:
                doc.save()
            return f"Saved: {doc.Name}"
            
        @self.server.tool()
        async def list_documents() -> str:
            """List all open documents"""
            docs = [d.Name for d in FreeCAD.listDocuments().values()]
            return json.dumps(docs)
            
        # ===== PART CREATION =====
        @self.server.tool()
        async def create_box(
            length: float = 10,
            width: float = 10,
            height: float = 10,
            x: float = 0,
            y: float = 0,
            z: float = 0
        ) -> str:
            """Create a box/cube"""
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            box = doc.addObject("Part::Box", "Box")
            box.Length = length
            box.Width = width
            box.Height = height
            box.Placement.Base = FreeCAD.Vector(x, y, z)
            doc.recompute()
            return f"Created box: {box.Name}"
            
        @self.server.tool()
        async def create_cylinder(
            radius: float = 5,
            height: float = 10,
            x: float = 0,
            y: float = 0,
            z: float = 0
        ) -> str:
            """Create a cylinder"""
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            cyl = doc.addObject("Part::Cylinder", "Cylinder")
            cyl.Radius = radius
            cyl.Height = height
            cyl.Placement.Base = FreeCAD.Vector(x, y, z)
            doc.recompute()
            return f"Created cylinder: {cyl.Name}"
            
        @self.server.tool()
        async def create_sphere(
            radius: float = 5,
            x: float = 0,
            y: float = 0,
            z: float = 0
        ) -> str:
            """Create a sphere"""
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            sphere = doc.addObject("Part::Sphere", "Sphere")
            sphere.Radius = radius
            sphere.Placement.Base = FreeCAD.Vector(x, y, z)
            doc.recompute()
            return f"Created sphere: {sphere.Name}"
            
        @self.server.tool()
        async def create_cone(
            radius1: float = 10,
            radius2: float = 0,
            height: float = 10
        ) -> str:
            """Create a cone"""
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            cone = doc.addObject("Part::Cone", "Cone")
            cone.Radius1 = radius1
            cone.Radius2 = radius2
            cone.Height = height
            doc.recompute()
            return f"Created cone: {cone.Name}"
            
        # ===== SKETCH OPERATIONS =====
        @self.server.tool()
        async def create_sketch(plane: str = "XY") -> str:
            """Create a new sketch on specified plane"""
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            sketch = doc.addObject("Sketcher::SketchObject", "Sketch")
            
            # Set plane
            if plane == "XY":
                sketch.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0), FreeCAD.Rotation(0,0,0,1))
            elif plane == "XZ":
                sketch.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0), FreeCAD.Rotation(-0.707107,0,0,0.707107))
            elif plane == "YZ":
                sketch.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0), FreeCAD.Rotation(0.5,0.5,0.5,0.5))
                
            # Enter edit mode if GUI available
            if FreeCADGui.ActiveDocument:
                FreeCADGui.ActiveDocument.setEdit(sketch.Name)
                
            return f"Created sketch: {sketch.Name} on {plane} plane"
            
        @self.server.tool()
        async def add_line_to_sketch(
            x1: float, y1: float,
            x2: float, y2: float
        ) -> str:
            """Add line to active sketch"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            # Find active sketch
            sketch = None
            for obj in doc.Objects:
                if obj.TypeId == "Sketcher::SketchObject":
                    sketch = obj
                    break
                    
            if not sketch:
                return "No sketch found"
                
            sketch.addGeometry(Part.LineSegment(
                FreeCAD.Vector(x1, y1, 0),
                FreeCAD.Vector(x2, y2, 0)
            ))
            doc.recompute()
            return f"Added line to {sketch.Name}"
            
        @self.server.tool()
        async def add_circle_to_sketch(
            center_x: float,
            center_y: float,
            radius: float
        ) -> str:
            """Add circle to active sketch"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            sketch = None
            for obj in doc.Objects:
                if obj.TypeId == "Sketcher::SketchObject":
                    sketch = obj
                    break
                    
            if not sketch:
                return "No sketch found"
                
            sketch.addGeometry(Part.Circle(
                FreeCAD.Vector(center_x, center_y, 0),
                FreeCAD.Vector(0, 0, 1),
                radius
            ))
            doc.recompute()
            return f"Added circle to {sketch.Name}"
            
        # ===== BOOLEAN OPERATIONS =====
        @self.server.tool()
        async def boolean_cut(
            tool_name: str,
            base_name: str
        ) -> str:
            """Cut one shape from another"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            base = doc.getObject(base_name)
            tool = doc.getObject(tool_name)
            
            if not base or not tool:
                return "Objects not found"
                
            cut = doc.addObject("Part::Cut", "Cut")
            cut.Base = base
            cut.Tool = tool
            doc.recompute()
            return f"Created boolean cut: {cut.Name}"
            
        @self.server.tool()
        async def boolean_union(
            obj1_name: str,
            obj2_name: str
        ) -> str:
            """Union/fuse two shapes"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj1 = doc.getObject(obj1_name)
            obj2 = doc.getObject(obj2_name)
            
            if not obj1 or not obj2:
                return "Objects not found"
                
            fusion = doc.addObject("Part::Fuse", "Fusion")
            fusion.Base = obj1
            fusion.Tool = obj2
            doc.recompute()
            return f"Created union: {fusion.Name}"
            
        @self.server.tool()
        async def boolean_intersection(
            obj1_name: str,
            obj2_name: str
        ) -> str:
            """Intersection of two shapes"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj1 = doc.getObject(obj1_name)
            obj2 = doc.getObject(obj2_name)
            
            if not obj1 or not obj2:
                return "Objects not found"
                
            common = doc.addObject("Part::Common", "Common")
            common.Base = obj1
            common.Tool = obj2
            doc.recompute()
            return f"Created intersection: {common.Name}"
            
        # ===== TRANSFORMATION OPERATIONS =====
        @self.server.tool()
        async def move_object(
            obj_name: str,
            x: float,
            y: float,
            z: float
        ) -> str:
            """Move object to position"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(obj_name)
            if not obj:
                return f"Object {obj_name} not found"
                
            obj.Placement.Base = FreeCAD.Vector(x, y, z)
            doc.recompute()
            return f"Moved {obj_name} to ({x}, {y}, {z})"
            
        @self.server.tool()
        async def rotate_object(
            obj_name: str,
            angle_x: float,
            angle_y: float,
            angle_z: float
        ) -> str:
            """Rotate object (degrees)"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(obj_name)
            if not obj:
                return f"Object {obj_name} not found"
                
            obj.Placement.Rotation = FreeCAD.Rotation(angle_x, angle_y, angle_z)
            doc.recompute()
            return f"Rotated {obj_name}"
            
        @self.server.tool()
        async def scale_object(
            obj_name: str,
            scale_x: float,
            scale_y: float,
            scale_z: float
        ) -> str:
            """Scale object"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(obj_name)
            if not obj:
                return f"Object {obj_name} not found"
                
            # Create scaled copy
            scaled = Draft.scale(obj, FreeCAD.Vector(scale_x, scale_y, scale_z))
            doc.recompute()
            return f"Scaled {obj_name}"
            
        # ===== SELECTION & QUERY =====
        @self.server.tool()
        async def get_selected_objects() -> str:
            """Get currently selected objects"""
            sel = FreeCADGui.Selection.getSelectionEx()
            selected = []
            for s in sel:
                selected.append({
                    "name": s.ObjectName,
                    "type": s.Object.TypeId,
                    "sub_elements": s.SubElementNames
                })
            return json.dumps(selected)
            
        @self.server.tool()
        async def select_object(obj_name: str) -> str:
            """Select an object by name"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(obj_name)
            if not obj:
                return f"Object {obj_name} not found"
                
            FreeCADGui.Selection.clearSelection()
            FreeCADGui.Selection.addSelection(obj)
            return f"Selected {obj_name}"
            
        @self.server.tool()
        async def list_all_objects() -> str:
            """List all objects in document"""
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
            
        @self.server.tool()
        async def get_object_properties(obj_name: str) -> str:
            """Get all properties of an object"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(obj_name)
            if not obj:
                return f"Object {obj_name} not found"
                
            props = {}
            for prop in obj.PropertiesList:
                try:
                    value = getattr(obj, prop)
                    # Convert FreeCAD types to serializable
                    if hasattr(value, 'x'):  # Vector
                        value = {"x": value.x, "y": value.y, "z": value.z}
                    elif hasattr(value, 'Base'):  # Placement
                        value = {
                            "position": {"x": value.Base.x, "y": value.Base.y, "z": value.Base.z},
                            "rotation": str(value.Rotation)
                        }
                    else:
                        value = str(value)
                    props[prop] = value
                except:
                    props[prop] = "N/A"
                    
            return json.dumps(props, indent=2)
            
        @self.server.tool()
        async def set_object_property(
            obj_name: str,
            property_name: str,
            value: Any
        ) -> str:
            """Set a property on an object"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(obj_name)
            if not obj:
                return f"Object {obj_name} not found"
                
            setattr(obj, property_name, value)
            doc.recompute()
            return f"Set {obj_name}.{property_name} = {value}"
            
        # ===== MEASUREMENT TOOLS =====
        @self.server.tool()
        async def measure_distance(
            obj1_name: str,
            obj2_name: str
        ) -> str:
            """Measure distance between two objects"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj1 = doc.getObject(obj1_name)
            obj2 = doc.getObject(obj2_name)
            
            if not obj1 or not obj2:
                return "Objects not found"
                
            pos1 = obj1.Placement.Base
            pos2 = obj2.Placement.Base
            distance = (pos2 - pos1).Length
            
            return json.dumps({
                "distance": distance,
                "delta_x": pos2.x - pos1.x,
                "delta_y": pos2.y - pos1.y,
                "delta_z": pos2.z - pos1.z
            })
            
        @self.server.tool()
        async def get_bounding_box(obj_name: str) -> str:
            """Get bounding box of object"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(obj_name)
            if not obj:
                return f"Object {obj_name} not found"
                
            if hasattr(obj, 'Shape'):
                bb = obj.Shape.BoundBox
                return json.dumps({
                    "min": {"x": bb.XMin, "y": bb.YMin, "z": bb.ZMin},
                    "max": {"x": bb.XMax, "y": bb.YMax, "z": bb.ZMax},
                    "length": bb.XLength,
                    "width": bb.YLength,
                    "height": bb.ZLength,
                    "volume": obj.Shape.Volume if hasattr(obj.Shape, 'Volume') else None,
                    "area": obj.Shape.Area if hasattr(obj.Shape, 'Area') else None
                })
            return "Object has no shape"
            
        # ===== VIEW OPERATIONS =====
        @self.server.tool()
        async def fit_all() -> str:
            """Fit all objects in view"""
            if FreeCADGui.ActiveDocument:
                FreeCADGui.SendMsgToActiveView("ViewFit")
                return "View fitted to all objects"
            return "No active view"
            
        @self.server.tool()
        async def set_view(view_type: str) -> str:
            """Set view (top, front, right, iso, etc)"""
            if not FreeCADGui.ActiveDocument:
                return "No active view"
                
            views = {
                "top": "ViewTop",
                "bottom": "ViewBottom",
                "front": "ViewFront",
                "back": "ViewRear",
                "right": "ViewRight",
                "left": "ViewLeft",
                "iso": "ViewAxometric"
            }
            
            if view_type.lower() in views:
                FreeCADGui.SendMsgToActiveView(views[view_type.lower()])
                return f"Set view to {view_type}"
            return f"Unknown view: {view_type}"
            
        @self.server.tool()
        async def take_screenshot(filepath: str) -> str:
            """Take screenshot of current view"""
            if FreeCADGui.ActiveDocument:
                view = FreeCADGui.ActiveDocument.ActiveView
                view.saveImage(filepath, 1920, 1080, "Current")
                return f"Screenshot saved to {filepath}"
            return "No active view"
            
        # ===== ADVANCED OPERATIONS =====
        @self.server.tool()
        async def execute_python(code: str) -> str:
            """Execute arbitrary Python code in FreeCAD context"""
            try:
                # Create execution context with FreeCAD modules
                exec_context = {
                    'FreeCAD': FreeCAD,
                    'FreeCADGui': FreeCADGui,
                    'Part': Part,
                    'Sketcher': Sketcher,
                    'Draft': Draft,
                    'doc': FreeCAD.ActiveDocument
                }
                
                # Execute code
                exec(code, exec_context)
                
                # Try to return result if assigned to 'result'
                if 'result' in exec_context:
                    return str(exec_context['result'])
                return "Code executed successfully"
                
            except Exception as e:
                return f"Error: {str(e)}"
                
        @self.server.tool()
        async def undo() -> str:
            """Undo last operation"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
            if doc.UndoCount > 0:
                doc.undo()
                return "Undone last operation"
            return "Nothing to undo"
            
        @self.server.tool()
        async def redo() -> str:
            """Redo operation"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
            if doc.RedoCount > 0:
                doc.redo()
                return "Redone operation"
            return "Nothing to redo"
            
        @self.server.tool()
        async def get_freecad_info() -> str:
            """Get FreeCAD version and system info"""
            return json.dumps({
                "version": FreeCAD.Version(),
                "config_dir": FreeCAD.getUserAppDataDir(),
                "macro_dir": FreeCAD.getUserMacroDir(True),
                "active_document": FreeCAD.ActiveDocument.Name if FreeCAD.ActiveDocument else None,
                "open_documents": list(FreeCAD.listDocuments().keys())
            }, indent=2)
            
    def _start_socket_server(self):
        """Start Unix socket server for bridge connection"""
        # Remove old socket if exists
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            
        # Create socket server in separate thread
        def socket_server():
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.bind(self.socket_path)
            sock.listen(1)
            
            FreeCAD.Console.PrintMessage(f"MCP socket server listening on {self.socket_path}\n")
            
            while True:
                conn, addr = sock.accept()
                # Handle MCP protocol over socket
                threading.Thread(target=self._handle_connection, args=(conn,)).start()
                
        threading.Thread(target=socket_server, daemon=True).start()
        
    def _handle_connection(self, conn):
        """Handle MCP protocol over socket connection"""
        # This is where MCP protocol messages are bridged
        # The bridge.py script connects here
        pass