# Embedded MCP Server for FreeCAD AI Copilot
# Runs INSIDE FreeCAD process for direct access

import FreeCAD
import FreeCADGui
import asyncio
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import threading
import queue
from datetime import datetime

# MCP protocol implementation
from mcp import Server, Tool
from mcp.types import TextContent, ImageContent

@dataclass
class DesignContext:
    """Rich context about current design state"""
    selection: List[str]
    active_document: str
    viewport_state: Dict
    recent_operations: List[Dict]
    cursor_position: tuple
    timestamp: datetime

class EmbeddedMCPServer:
    """MCP Server embedded directly in FreeCAD process"""
    
    def __init__(self):
        self.server = Server("freecad-ai-copilot")
        self.memory_system = None
        self.context_queue = queue.Queue()
        self.is_running = False
        self.socket_path = "/tmp/freecad_mcp.sock" if sys.platform != "win32" else r'\\.\pipe\freecad_mcp'
        
        # Initialize memory system
        from memory_system import CADMemorySystem
        self.memory_system = CADMemorySystem()
        
        # Register tools
        self._register_tools()
        
        # Create Unix socket for bridge connection
        self._create_socket()
        
        # Start async event loop in separate thread
        self.loop_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.loop_thread.start()
        
    def _register_tools(self):
        """Register all MCP tools with direct FreeCAD access"""
        
        @self.server.tool()
        async def get_full_context() -> str:
            """Get complete design context including selection, viewport, and history"""
            context = self._capture_context()
            return json.dumps({
                "selection": context.selection,
                "document": context.active_document,
                "viewport": context.viewport_state,
                "recent_ops": context.recent_operations[-10:],
                "cursor": context.cursor_position
            })
            
        @self.server.tool()
        async def create_parametric_object(
            object_type: str,
            parameters: Dict[str, Any],
            name: Optional[str] = None
        ) -> str:
            """Create object with full parametric control"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            # Direct access to FreeCAD internals
            if object_type == "Box":
                obj = doc.addObject("Part::Box", name or "Box")
                for key, value in parameters.items():
                    setattr(obj, key, value)
            elif object_type == "Sketch":
                obj = doc.addObject("Sketcher::SketchObject", name or "Sketch")
                # Add constraints directly
                if "constraints" in parameters:
                    for constraint in parameters["constraints"]:
                        obj.addConstraint(constraint)
                        
            doc.recompute()
            
            # Store in memory system
            if self.memory_system:
                self.memory_system.store_operation(object_type, parameters, obj.Name)
                
            return f"Created {object_type}: {obj.Name}"
            
        @self.server.tool()
        async def get_selection_details() -> str:
            """Get detailed info about selected entities"""
            sel = FreeCADGui.Selection.getSelectionEx()
            if not sel:
                return "Nothing selected"
                
            details = []
            for s in sel:
                obj_info = {
                    "name": s.ObjectName,
                    "type": s.Object.TypeId,
                    "sub_elements": s.SubElementNames,
                    "properties": {
                        p: str(getattr(s.Object, p))
                        for p in s.Object.PropertiesList
                    }
                }
                details.append(obj_info)
                
            return json.dumps(details, indent=2)
            
        @self.server.tool()
        async def recall_design(query: str) -> str:
            """Use AI memory to recall previous designs"""
            if not self.memory_system:
                return "Memory system not initialized"
                
            results = self.memory_system.semantic_search(query)
            if results:
                # Recreate the design
                for operation in results[0]["operations"]:
                    await create_parametric_object(
                        operation["type"],
                        operation["parameters"]
                    )
                return f"Recalled design: {results[0]['description']}"
            return "No matching designs found"
            
        @self.server.tool()
        async def analyze_design_intent() -> str:
            """Analyze what user is trying to build"""
            context = self._capture_context()
            
            # Analyze patterns in recent operations
            patterns = self._detect_patterns(context.recent_operations)
            
            # Predict next likely operation
            prediction = self._predict_next_operation(patterns)
            
            return json.dumps({
                "detected_patterns": patterns,
                "likely_intent": self._infer_intent(patterns),
                "suggested_next": prediction
            })
            
        @self.server.tool() 
        async def get_failed_operations() -> str:
            """Get operations that failed or were undone"""
            # Direct access to FreeCAD's undo stack
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            failed_ops = []
            # Access internal undo/redo stack
            for i in range(doc.UndoCount):
                op_name = doc.UndoNames[i] if i < len(doc.UndoNames) else "Unknown"
                failed_ops.append({
                    "operation": op_name,
                    "index": i
                })
                
            return json.dumps(failed_ops)
            
    def _capture_context(self) -> DesignContext:
        """Capture rich context from FreeCAD"""
        sel = FreeCADGui.Selection.getSelectionEx()
        doc = FreeCAD.ActiveDocument
        
        # Get viewport state
        view = FreeCADGui.ActiveDocument.ActiveView if FreeCADGui.ActiveDocument else None
        viewport = {}
        if view:
            viewport = {
                "camera_position": str(view.getCameraNode().position.getValue()),
                "camera_orientation": str(view.getCameraNode().orientation.getValue()),
                "zoom": view.getCamera().focalDistance.getValue()
            }
            
        return DesignContext(
            selection=[s.ObjectName for s in sel],
            active_document=doc.Name if doc else None,
            viewport_state=viewport,
            recent_operations=self._get_recent_operations(),
            cursor_position=FreeCADGui.getMainWindow().cursor().pos().toTuple() if FreeCADGui.getMainWindow() else (0, 0),
            timestamp=datetime.now()
        )
        
    def _get_recent_operations(self) -> List[Dict]:
        """Get recent operations from event observer"""
        if hasattr(FreeCAD, '__ai_observer'):
            return FreeCAD.__ai_observer.get_recent_operations()
        return []
        
    def _detect_patterns(self, operations: List[Dict]) -> List[str]:
        """Detect patterns in user operations"""
        patterns = []
        
        # Check for repetitive operations
        if len(operations) >= 3:
            last_three = [op["type"] for op in operations[-3:]]
            if len(set(last_three)) == 1:
                patterns.append(f"Repeating {last_three[0]}")
                
        # Check for sketch-extrude pattern
        if len(operations) >= 2:
            if operations[-2].get("type") == "Sketch" and operations[-1].get("type") == "Pad":
                patterns.append("Sketch-Extrude workflow")
                
        return patterns
        
    def _predict_next_operation(self, patterns: List[str]) -> Dict:
        """Predict likely next operation based on patterns"""
        if "Sketch-Extrude workflow" in patterns:
            return {"likely": "Add features to extruded part", "confidence": 0.8}
        return {"likely": "Unknown", "confidence": 0.0}
        
    def _infer_intent(self, patterns: List[str]) -> str:
        """Infer user's design intent from patterns"""
        if "Sketch-Extrude workflow" in patterns:
            return "Creating 3D part from 2D profile"
        return "Exploring design"
        
    def _run_async_loop(self):
        """Run async event loop in separate thread"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.server.run())
        
    def ensure_running(self):
        """Ensure MCP server is running"""
        if not self.is_running:
            self.is_running = True
            FreeCAD.Console.PrintMessage("MCP Server started on embedded connection\\n")
            
    def stop(self):
        """Stop the MCP server"""
        self.is_running = False