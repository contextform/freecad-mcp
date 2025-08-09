# Event Observer - Captures ALL FreeCAD interactions
# This is the KEY to intelligent memory

import FreeCAD
import FreeCADGui
from PySide2 import QtCore
from datetime import datetime
from collections import deque
import json

class FreeCADEventObserver(QtCore.QObject):
    """Captures rich context from user interactions"""
    
    def __init__(self):
        super().__init__()
        self.operations_history = deque(maxlen=1000)  # Keep last 1000 ops
        self.selection_history = deque(maxlen=100)
        self.failed_attempts = deque(maxlen=50)
        self.time_tracking = {}
        self.current_operation_start = None
        
    def start(self):
        """Start observing FreeCAD events"""
        FreeCAD.Console.PrintMessage("Starting event observation...\\n")
        
        # Connect to selection observer
        FreeCADGui.Selection.addObserver(self)
        
        # Hook into document observer
        FreeCAD.addDocumentObserver(self)
        
        # Install event filter for mouse/keyboard
        if FreeCADGui.getMainWindow():
            FreeCADGui.getMainWindow().installEventFilter(self)
            
    def onSelectionChanged(self, doc, obj, sub, pos):
        """Called when selection changes"""
        self.selection_history.append({
            "timestamp": datetime.now().isoformat(),
            "document": doc,
            "object": obj,
            "sub_element": sub,
            "position": pos,
            "duration_since_last": self._get_duration()
        })
        
    def eventFilter(self, obj, event):
        """Capture mouse and keyboard events"""
        event_type = event.type()
        
        # Track mouse hover time
        if event_type == QtCore.QEvent.HoverEnter:
            self.current_operation_start = datetime.now()
            
        # Track failed clicks (nothing selected)
        elif event_type == QtCore.QEvent.MouseButtonPress:
            if not FreeCADGui.Selection.getSelection():
                self.failed_attempts.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "empty_click",
                    "position": (event.x(), event.y())
                })
                
        return False  # Don't block event
        
    def slotCreatedDocument(self, doc):
        """Document created"""
        self._record_operation("create_document", {"name": doc.Name})
        
    def slotDeletedDocument(self, doc):
        """Document deleted"""
        self._record_operation("delete_document", {"name": doc.Name})
        
    def slotCreatedObject(self, obj):
        """Object created"""
        self._record_operation("create_object", {
            "name": obj.Name,
            "type": obj.TypeId,
            "properties": self._extract_properties(obj)
        })
        
    def slotDeletedObject(self, obj):
        """Object deleted"""
        self._record_operation("delete_object", {
            "name": obj.Name,
            "type": obj.TypeId
        })
        
    def slotChangedObject(self, obj, prop):
        """Object property changed"""
        self._record_operation("modify_object", {
            "name": obj.Name,
            "property": prop,
            "new_value": str(getattr(obj, prop, None))
        })
        
    def slotUndo(self):
        """Undo operation - indicates mistake or exploration"""
        self._record_operation("undo", {
            "reason": "user_initiated",
            "timestamp": datetime.now().isoformat()
        })
        
        # Mark last operation as "undone" - learning opportunity
        if len(self.operations_history) > 1:
            self.operations_history[-2]["was_undone"] = True
            
    def slotRedo(self):
        """Redo operation"""
        self._record_operation("redo", {
            "timestamp": datetime.now().isoformat()
        })
        
    def _record_operation(self, op_type, data):
        """Record an operation with rich context"""
        operation = {
            "type": op_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "selection_context": self._get_selection_context(),
            "viewport_context": self._get_viewport_context(),
            "duration": self._get_duration()
        }
        
        self.operations_history.append(operation)
        self.current_operation_start = datetime.now()
        
    def _get_selection_context(self):
        """Get current selection state"""
        sel = FreeCADGui.Selection.getSelectionEx()
        return [
            {
                "object": s.ObjectName,
                "sub_elements": s.SubElementNames
            }
            for s in sel
        ]
        
    def _get_viewport_context(self):
        """Get viewport/camera state"""
        try:
            if FreeCADGui.ActiveDocument and hasattr(FreeCADGui.ActiveDocument, 'ActiveView'):
                view = FreeCADGui.ActiveDocument.ActiveView
                if view and hasattr(view, 'getCameraNode'):
                    cam = view.getCameraNode()
                    return {
                        "position": str(cam.position.getValue()),
                        "orientation": str(cam.orientation.getValue()),
                        "focal_distance": cam.focalDistance.getValue()
                    }
        except:
            # Silently ignore - camera not available in all contexts
            pass
        return {}
        
    def _get_duration(self):
        """Get time since last operation"""
        if self.current_operation_start:
            return (datetime.now() - self.current_operation_start).total_seconds()
        return 0
        
    def _extract_properties(self, obj):
        """Extract key properties from object"""
        props = {}
        for prop in ["Length", "Width", "Height", "Radius", "Angle"]:
            if hasattr(obj, prop):
                props[prop] = float(getattr(obj, prop))
        return props
        
    def get_recent_operations(self, count=10):
        """Get recent operations for analysis"""
        return list(self.operations_history)[-count:]
        
    def get_failed_attempts(self):
        """Get failed user attempts - learning opportunities"""
        return list(self.failed_attempts)
        
    def get_interaction_patterns(self):
        """Analyze interaction patterns"""
        patterns = {
            "avg_time_between_ops": self._calculate_avg_time(),
            "most_modified_objects": self._get_most_modified(),
            "undo_rate": self._calculate_undo_rate(),
            "selection_patterns": self._analyze_selections()
        }
        return patterns
        
    def _calculate_avg_time(self):
        """Calculate average time between operations"""
        if len(self.operations_history) < 2:
            return 0
            
        times = [op.get("duration", 0) for op in self.operations_history]
        return sum(times) / len(times) if times else 0
        
    def _get_most_modified(self):
        """Find most frequently modified objects"""
        modifications = {}
        for op in self.operations_history:
            if op["type"] == "modify_object":
                obj_name = op["data"].get("name")
                modifications[obj_name] = modifications.get(obj_name, 0) + 1
        return modifications
        
    def _calculate_undo_rate(self):
        """Calculate how often user undoes - indicates difficulty"""
        undo_count = sum(1 for op in self.operations_history if op["type"] == "undo")
        total = len(self.operations_history)
        return undo_count / total if total > 0 else 0
        
    def _analyze_selections(self):
        """Analyze selection patterns"""
        return {
            "total_selections": len(self.selection_history),
            "empty_clicks": len(self.failed_attempts),
            "avg_selection_time": self._calculate_avg_time()
        }