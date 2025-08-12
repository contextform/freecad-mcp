# Enhanced Embedded MCP Server - Complete FreeCAD Control
# Combines best of neka-nat with full GUI automation

import FreeCAD
import FreeCADGui
import Part
import Sketcher
import Draft
import asyncio
import json
import base64
import io
import os
from typing import Any, Dict, List, Optional
from mcp import Server, Tool
from mcp.types import TextContent, ImageContent
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtTest import QTest

class EnhancedFreeCADMCP:
    """Enhanced MCP Server with complete FreeCAD control"""
    
    def __init__(self):
        self.server = Server("freecad-enhanced")
        self.parts_library_path = os.path.join(FreeCAD.getUserAppDataDir(), "Parts")
        self._ensure_parts_library()
        self._register_all_tools()
        
    def _ensure_parts_library(self):
        """Create parts library directory if needed"""
        if not os.path.exists(self.parts_library_path):
            os.makedirs(self.parts_library_path)
            
    def _register_all_tools(self):
        """Register all enhanced tools"""
        
        # ===== SCREENSHOT WITH BASE64 (from neka-nat) =====
        @self.server.tool()
        async def get_screenshot(
            width: int = 1920,
            height: int = 1080,
            background: str = "white",
            as_base64: bool = True
        ) -> str:
            """Get screenshot of current view with base64 encoding"""
            if not FreeCADGui.ActiveDocument:
                return json.dumps({"error": "No active document"})
                
            view = FreeCADGui.ActiveDocument.ActiveView
            
            # Save to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                
            # Capture image
            view.saveImage(tmp_path, width, height, background)
            
            if as_base64:
                # Read and encode as base64
                with open(tmp_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                os.unlink(tmp_path)
                return json.dumps({
                    "image": f"data:image/png;base64,{image_data}",
                    "width": width,
                    "height": height
                })
            else:
                return json.dumps({"path": tmp_path})
                
        # ===== PARTS LIBRARY (from neka-nat) =====
        @self.server.tool()
        async def save_as_part(
            object_name: str,
            part_name: str,
            category: str = "General"
        ) -> str:
            """Save object as reusable part in library"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(object_name)
            if not obj:
                return f"Object {object_name} not found"
                
            # Create category directory
            category_path = os.path.join(self.parts_library_path, category)
            os.makedirs(category_path, exist_ok=True)
            
            # Save part
            part_file = os.path.join(category_path, f"{part_name}.FCStd")
            
            # Create temporary document with just this object
            temp_doc = FreeCAD.newDocument("TempPart")
            copy = temp_doc.addObject(obj.TypeId, obj.Name)
            copy.Shape = obj.Shape.copy()
            temp_doc.saveAs(part_file)
            FreeCAD.closeDocument(temp_doc.Name)
            
            return f"Saved {object_name} as {part_name} in {category}"
            
        @self.server.tool()
        async def insert_part_from_library(
            part_name: str,
            category: str = "General",
            x: float = 0,
            y: float = 0,
            z: float = 0
        ) -> str:
            """Insert part from library at position"""
            part_file = os.path.join(self.parts_library_path, category, f"{part_name}.FCStd")
            
            if not os.path.exists(part_file):
                return f"Part {part_name} not found in {category}"
                
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            
            # Merge the part document
            FreeCAD.openDocument(part_file)
            part_doc = FreeCAD.getDocument(os.path.basename(part_file)[:-6])
            
            # Copy objects to active document
            for obj in part_doc.Objects:
                if hasattr(obj, 'Shape'):
                    new_obj = doc.addObject(obj.TypeId, f"{part_name}_{obj.Name}")
                    new_obj.Shape = obj.Shape.copy()
                    new_obj.Placement.Base = FreeCAD.Vector(x, y, z)
                    
            FreeCAD.closeDocument(part_doc.Name)
            doc.recompute()
            
            return f"Inserted {part_name} at ({x}, {y}, {z})"
            
        @self.server.tool()
        async def list_parts_library() -> str:
            """List all available parts in library"""
            parts = {}
            for category in os.listdir(self.parts_library_path):
                category_path = os.path.join(self.parts_library_path, category)
                if os.path.isdir(category_path):
                    parts[category] = [
                        f[:-6] for f in os.listdir(category_path)
                        if f.endswith('.FCStd')
                    ]
            return json.dumps(parts, indent=2)
            
        # ===== OBJECT SERIALIZATION (Enhanced) =====
        @self.server.tool()
        async def serialize_object(obj_name: str) -> str:
            """Serialize object with all properties for storage/transfer"""
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
                
            obj = doc.getObject(obj_name)
            if not obj:
                return f"Object {obj_name} not found"
                
            serialized = {
                "Name": obj.Name,
                "Label": obj.Label,
                "TypeId": obj.TypeId,
                "Properties": {}
            }
            
            # Serialize all properties
            for prop in obj.PropertiesList:
                try:
                    value = getattr(obj, prop)
                    prop_type = obj.getTypeIdOfProperty(prop)
                    
                    # Handle different property types
                    if hasattr(value, 'Value'):  # Quantity
                        serialized["Properties"][prop] = {
                            "Value": value.Value,
                            "Unit": str(value.Unit)
                        }
                    elif hasattr(value, 'Base'):  # Placement
                        serialized["Properties"][prop] = {
                            "Position": [value.Base.x, value.Base.y, value.Base.z],
                            "Rotation": [value.Rotation.Q[0], value.Rotation.Q[1], 
                                       value.Rotation.Q[2], value.Rotation.Q[3]]
                        }
                    elif hasattr(value, 'x'):  # Vector
                        serialized["Properties"][prop] = [value.x, value.y, value.z]
                    else:
                        serialized["Properties"][prop] = str(value)
                except:
                    serialized["Properties"][prop] = None
                    
            # Add shape data if available
            if hasattr(obj, 'Shape'):
                serialized["ShapeInfo"] = {
                    "Volume": obj.Shape.Volume,
                    "Area": obj.Shape.Area,
                    "BoundBox": {
                        "Min": [obj.Shape.BoundBox.XMin, obj.Shape.BoundBox.YMin, obj.Shape.BoundBox.ZMin],
                        "Max": [obj.Shape.BoundBox.XMax, obj.Shape.BoundBox.YMax, obj.Shape.BoundBox.ZMax]
                    }
                }
                
            return json.dumps(serialized, indent=2)
            
        @self.server.tool()
        async def deserialize_object(serialized_json: str) -> str:
            """Create object from serialized data"""
            data = json.loads(serialized_json)
            doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
            
            # Create object
            obj = doc.addObject(data["TypeId"], data["Name"])
            obj.Label = data["Label"]
            
            # Restore properties
            for prop, value in data["Properties"].items():
                try:
                    if isinstance(value, dict):
                        if "Position" in value:  # Placement
                            pos = FreeCAD.Vector(*value["Position"])
                            rot = FreeCAD.Rotation(*value["Rotation"])
                            setattr(obj, prop, FreeCAD.Placement(pos, rot))
                        elif "Value" in value:  # Quantity
                            setattr(obj, prop, value["Value"])
                    elif isinstance(value, list) and len(value) == 3:  # Vector
                        setattr(obj, prop, FreeCAD.Vector(*value))
                    else:
                        setattr(obj, prop, value)
                except:
                    pass
                    
            doc.recompute()
            return f"Created {obj.Name} from serialized data"
            
        # ===== FREECAD COMMAND EXECUTION =====
        @self.server.tool()
        async def execute_command(command_name: str, args: Dict = None) -> str:
            """Execute any FreeCAD command"""
            try:
                if args:
                    # Execute with arguments
                    cmd_str = f"FreeCADGui.runCommand('{command_name}', {args})"
                else:
                    cmd_str = f"FreeCADGui.runCommand('{command_name}')"
                    
                exec(cmd_str)
                return f"Executed command: {command_name}"
            except Exception as e:
                # Try alternate method
                try:
                    FreeCADGui.doCommand(f"Gui.runCommand('{command_name}')")
                    return f"Executed command: {command_name}"
                except Exception as e2:
                    return f"Error: {e2}"
                    
        @self.server.tool()
        async def activate_workbench(workbench_name: str) -> str:
            """Switch to specific workbench"""
            try:
                FreeCADGui.activateWorkbench(workbench_name)
                return f"Switched to {workbench_name} workbench"
            except Exception as e:
                return f"Error: {e}"
                
        @self.server.tool()
        async def list_commands() -> str:
            """List all available FreeCAD commands"""
            commands = FreeCADGui.listCommands()
            return json.dumps(commands)
            
        @self.server.tool()
        async def list_workbenches() -> str:
            """List all available workbenches"""
            workbenches = FreeCADGui.listWorkbenches()
            return json.dumps(workbenches)
            
        # ===== MOUSE AUTOMATION =====
        @self.server.tool()
        async def click_at(
            x: int,
            y: int,
            button: str = "left",
            double_click: bool = False
        ) -> str:
            """Click at specific coordinates"""
            main_window = FreeCADGui.getMainWindow()
            point = QtCore.QPoint(x, y)
            
            if button == "left":
                qt_button = QtCore.Qt.LeftButton
            elif button == "right":
                qt_button = QtCore.Qt.RightButton
            elif button == "middle":
                qt_button = QtCore.Qt.MiddleButton
            else:
                return f"Unknown button: {button}"
                
            if double_click:
                QTest.mouseDClick(main_window, qt_button, QtCore.Qt.NoModifier, point)
                action = "Double-clicked"
            else:
                QTest.mouseClick(main_window, qt_button, QtCore.Qt.NoModifier, point)
                action = "Clicked"
                
            return f"{action} {button} button at ({x}, {y})"
            
        @self.server.tool()
        async def drag_mouse(
            start_x: int,
            start_y: int,
            end_x: int,
            end_y: int,
            button: str = "left"
        ) -> str:
            """Drag mouse from start to end position"""
            main_window = FreeCADGui.getMainWindow()
            
            if button == "left":
                qt_button = QtCore.Qt.LeftButton
            elif button == "right":
                qt_button = QtCore.Qt.RightButton
            else:
                qt_button = QtCore.Qt.MiddleButton
                
            # Simulate drag
            start = QtCore.QPoint(start_x, start_y)
            end = QtCore.QPoint(end_x, end_y)
            
            QTest.mousePress(main_window, qt_button, QtCore.Qt.NoModifier, start)
            QTest.mouseMove(main_window, end)
            QTest.mouseRelease(main_window, qt_button, QtCore.Qt.NoModifier, end)
            
            return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"
            
        @self.server.tool()
        async def mouse_wheel(delta: int, x: int = None, y: int = None) -> str:
            """Scroll mouse wheel for zoom/pan"""
            main_window = FreeCADGui.getMainWindow()
            
            if x is not None and y is not None:
                point = QtCore.QPoint(x, y)
            else:
                # Use center of window
                rect = main_window.rect()
                point = rect.center()
                
            # Create wheel event
            event = QtGui.QWheelEvent(
                point,
                delta,
                QtCore.Qt.NoButton,
                QtCore.Qt.NoModifier,
                QtCore.Qt.Vertical
            )
            
            QtCore.QCoreApplication.postEvent(main_window, event)
            return f"Scrolled wheel by {delta} at ({point.x()}, {point.y()})"
            
        # ===== KEYBOARD AUTOMATION =====
        @self.server.tool()
        async def send_keys(keys: str) -> str:
            """Send keyboard input"""
            main_window = FreeCADGui.getMainWindow()
            QTest.keyClicks(main_window, keys)
            return f"Sent keys: {keys}"
            
        @self.server.tool()
        async def send_shortcut(
            key: str,
            ctrl: bool = False,
            shift: bool = False,
            alt: bool = False
        ) -> str:
            """Send keyboard shortcut"""
            main_window = FreeCADGui.getMainWindow()
            
            modifiers = QtCore.Qt.NoModifier
            if ctrl:
                modifiers |= QtCore.Qt.ControlModifier
            if shift:
                modifiers |= QtCore.Qt.ShiftModifier
            if alt:
                modifiers |= QtCore.Qt.AltModifier
                
            # Convert key string to Qt key
            qt_key = getattr(QtCore.Qt, f"Key_{key.upper()}", None)
            if not qt_key:
                return f"Unknown key: {key}"
                
            QTest.keyClick(main_window, qt_key, modifiers)
            
            shortcut_str = []
            if ctrl: shortcut_str.append("Ctrl")
            if shift: shortcut_str.append("Shift")
            if alt: shortcut_str.append("Alt")
            shortcut_str.append(key.upper())
            
            return f"Sent shortcut: {'+'.join(shortcut_str)}"
            
        # ===== GUI NAVIGATION =====
        @self.server.tool()
        async def find_widget(
            widget_name: str = None,
            widget_type: str = None,
            text: str = None
        ) -> str:
            """Find GUI widget by name, type, or text"""
            main_window = FreeCADGui.getMainWindow()
            
            # Determine widget class
            if widget_type:
                widget_class = getattr(QtWidgets, widget_type, QtWidgets.QWidget)
            else:
                widget_class = QtWidgets.QWidget
                
            if widget_name:
                widget = main_window.findChild(widget_class, widget_name)
                if widget:
                    return json.dumps({
                        "found": True,
                        "name": widget.objectName(),
                        "type": widget.__class__.__name__,
                        "visible": widget.isVisible(),
                        "enabled": widget.isEnabled(),
                        "geometry": {
                            "x": widget.x(),
                            "y": widget.y(),
                            "width": widget.width(),
                            "height": widget.height()
                        }
                    })
                    
            # Search by text if provided
            if text:
                widgets = main_window.findChildren(widget_class)
                for w in widgets:
                    if hasattr(w, 'text') and text in w.text():
                        return json.dumps({
                            "found": True,
                            "name": w.objectName(),
                            "type": w.__class__.__name__,
                            "text": w.text(),
                            "geometry": {
                                "x": w.x(),
                                "y": w.y(),
                                "width": w.width(),
                                "height": w.height()
                            }
                        })
                        
            return json.dumps({"found": False})
            
        @self.server.tool()
        async def click_widget(widget_name: str) -> str:
            """Click on specific widget by name"""
            main_window = FreeCADGui.getMainWindow()
            widget = main_window.findChild(QtWidgets.QWidget, widget_name)
            
            if not widget:
                return f"Widget {widget_name} not found"
                
            if not widget.isVisible() or not widget.isEnabled():
                return f"Widget {widget_name} is not clickable"
                
            # Click center of widget
            QTest.mouseClick(widget, QtCore.Qt.LeftButton)
            return f"Clicked widget: {widget_name}"
            
        @self.server.tool()
        async def click_menu(menu_path: str) -> str:
            """Navigate and click menu item (e.g., 'File/New')"""
            parts = menu_path.split('/')
            main_window = FreeCADGui.getMainWindow()
            menubar = main_window.menuBar()
            
            # Find top-level menu
            current_menu = None
            for action in menubar.actions():
                if parts[0] in action.text():
                    current_menu = action.menu()
                    break
                    
            if not current_menu:
                return f"Menu {parts[0]} not found"
                
            # Navigate sub-menus
            for part in parts[1:]:
                found = False
                for action in current_menu.actions():
                    if part in action.text():
                        if action.menu():
                            current_menu = action.menu()
                        else:
                            # Click the action
                            action.trigger()
                            return f"Clicked menu item: {menu_path}"
                        found = True
                        break
                        
                if not found:
                    return f"Menu item {part} not found"
                    
            return f"Menu navigation completed"
            
        @self.server.tool()
        async def fill_dialog(
            field_name: str,
            value: str,
            dialog_title: str = None
        ) -> str:
            """Fill field in dialog box"""
            main_window = FreeCADGui.getMainWindow()
            
            # Find dialog
            if dialog_title:
                dialogs = main_window.findChildren(QtWidgets.QDialog)
                dialog = None
                for d in dialogs:
                    if dialog_title in d.windowTitle():
                        dialog = d
                        break
            else:
                # Find topmost dialog
                dialogs = main_window.findChildren(QtWidgets.QDialog)
                dialog = dialogs[-1] if dialogs else None
                
            if not dialog:
                return "No dialog found"
                
            # Find field
            field = dialog.findChild(QtWidgets.QLineEdit, field_name)
            if not field:
                # Try finding by label
                labels = dialog.findChildren(QtWidgets.QLabel)
                for label in labels:
                    if field_name in label.text():
                        # Find associated input
                        buddy = label.buddy()
                        if buddy and isinstance(buddy, QtWidgets.QLineEdit):
                            field = buddy
                            break
                            
            if field:
                field.setText(str(value))
                return f"Set {field_name} to {value}"
            else:
                return f"Field {field_name} not found"
                
        @self.server.tool()
        async def click_dialog_button(button_text: str) -> str:
            """Click button in active dialog"""
            main_window = FreeCADGui.getMainWindow()
            dialogs = main_window.findChildren(QtWidgets.QDialog)
            
            if not dialogs:
                return "No dialog found"
                
            dialog = dialogs[-1]  # Most recent dialog
            
            # Find button
            buttons = dialog.findChildren(QtWidgets.QPushButton)
            for button in buttons:
                if button_text in button.text():
                    button.click()
                    return f"Clicked button: {button_text}"
                    
            return f"Button {button_text} not found"
            
        # ===== TOOLBAR ACCESS =====
        @self.server.tool()
        async def list_toolbars() -> str:
            """List all available toolbars"""
            main_window = FreeCADGui.getMainWindow()
            toolbars = main_window.findChildren(QtWidgets.QToolBar)
            
            toolbar_info = []
            for tb in toolbars:
                actions = []
                for action in tb.actions():
                    if action.text():
                        actions.append({
                            "text": action.text(),
                            "enabled": action.isEnabled(),
                            "icon": bool(action.icon())
                        })
                        
                toolbar_info.append({
                    "name": tb.objectName(),
                    "title": tb.windowTitle(),
                    "visible": tb.isVisible(),
                    "actions": actions
                })
                
            return json.dumps(toolbar_info, indent=2)
            
        @self.server.tool()
        async def click_toolbar_action(toolbar_name: str, action_text: str) -> str:
            """Click toolbar button"""
            main_window = FreeCADGui.getMainWindow()
            toolbar = main_window.findChild(QtWidgets.QToolBar, toolbar_name)
            
            if not toolbar:
                return f"Toolbar {toolbar_name} not found"
                
            for action in toolbar.actions():
                if action_text in action.text():
                    action.trigger()
                    return f"Clicked toolbar action: {action_text}"
                    
            return f"Action {action_text} not found in {toolbar_name}"
            
        # ===== 3D VIEW INTERACTION =====
        @self.server.tool()
        async def click_in_3d_view(x: int, y: int, select: bool = True) -> str:
            """Click in 3D view for selection or interaction"""
            if not FreeCADGui.ActiveDocument:
                return "No active document"
                
            view = FreeCADGui.ActiveDocument.ActiveView
            
            # Get object info at position
            info = view.getObjectInfo((x, y))
            
            if info and select:
                obj = FreeCAD.ActiveDocument.getObject(info['Object'])
                if obj:
                    FreeCADGui.Selection.clearSelection()
                    FreeCADGui.Selection.addSelection(obj)
                    return f"Selected {obj.Name} at ({x}, {y})"
                    
            # Just click if no object or not selecting
            widget = view.getViewer().getWidget()
            QTest.mouseClick(widget, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier, QtCore.QPoint(x, y))
            
            return f"Clicked in 3D view at ({x}, {y})"
            
        @self.server.tool()
        async def sketch_in_view(points: List[Dict[str, float]]) -> str:
            """Draw sketch by clicking points in view"""
            if not FreeCADGui.ActiveDocument:
                return "No active document"
                
            view = FreeCADGui.ActiveDocument.ActiveView
            widget = view.getViewer().getWidget()
            
            # Start sketching
            for i, point in enumerate(points):
                x, y = int(point['x']), int(point['y'])
                qt_point = QtCore.QPoint(x, y)
                
                if i == 0:
                    # First click
                    QTest.mouseClick(widget, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier, qt_point)
                else:
                    # Subsequent clicks
                    QTest.mouseMove(widget, qt_point)
                    QTest.mouseClick(widget, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier, qt_point)
                    
            # End sketching (ESC key)
            QTest.keyClick(widget, QtCore.Qt.Key_Escape)
            
            return f"Drew sketch with {len(points)} points"
            
        # ===== COMBO BOX AND DROPDOWN CONTROL =====
        @self.server.tool()
        async def select_dropdown_item(
            widget_name: str,
            item_text: str
        ) -> str:
            """Select item from dropdown/combobox"""
            main_window = FreeCADGui.getMainWindow()
            combo = main_window.findChild(QtWidgets.QComboBox, widget_name)
            
            if not combo:
                return f"Dropdown {widget_name} not found"
                
            # Find and select item
            index = combo.findText(item_text)
            if index >= 0:
                combo.setCurrentIndex(index)
                return f"Selected '{item_text}' in {widget_name}"
            else:
                return f"Item '{item_text}' not found in {widget_name}"
                
        # ===== ADVANCED GUI STATE =====
        @self.server.tool()
        async def get_gui_state() -> str:
            """Get comprehensive GUI state information"""
            main_window = FreeCADGui.getMainWindow()
            
            state = {
                "active_workbench": FreeCADGui.activeWorkbench().__class__.__name__,
                "active_document": FreeCAD.ActiveDocument.Name if FreeCAD.ActiveDocument else None,
                "main_window": {
                    "width": main_window.width(),
                    "height": main_window.height(),
                    "title": main_window.windowTitle()
                },
                "visible_toolbars": [],
                "open_dialogs": [],
                "focused_widget": None
            }
            
            # Get visible toolbars
            for toolbar in main_window.findChildren(QtWidgets.QToolBar):
                if toolbar.isVisible():
                    state["visible_toolbars"].append(toolbar.objectName())
                    
            # Get open dialogs
            for dialog in main_window.findChildren(QtWidgets.QDialog):
                if dialog.isVisible():
                    state["open_dialogs"].append({
                        "title": dialog.windowTitle(),
                        "name": dialog.objectName()
                    })
                    
            # Get focused widget
            focused = QtWidgets.QApplication.focusWidget()
            if focused:
                state["focused_widget"] = {
                    "name": focused.objectName(),
                    "type": focused.__class__.__name__
                }
                
            return json.dumps(state, indent=2)