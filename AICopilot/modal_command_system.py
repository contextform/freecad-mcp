# Modal Command System - Direct FreeCAD Command Integration
# Triggers native FreeCAD commands and modals for proper CAD workflow

import FreeCAD
import FreeCADGui
import time
from typing import Dict, Any

class ModalCommandSystem:
    """System that triggers native FreeCAD commands directly"""
    
    def __init__(self):
        self.last_commands = {}  # Track recent commands for reporting
        
    # =====================================================================
    # PARTDESIGN COMMANDS - Trigger Native FreeCAD Modals
    # =====================================================================
    
    def trigger_fillet_command(self, args: Dict[str, Any]) -> str:
        """Trigger native FreeCAD fillet command"""
        try:
            object_name = args.get('object_name', '')
            radius = args.get('radius', 1.0)
            
            # Pre-select object if specified
            if object_name:
                doc = FreeCAD.ActiveDocument
                if doc:
                    obj = doc.getObject(object_name)
                    if obj:
                        FreeCADGui.Selection.clearSelection()
                        FreeCADGui.Selection.addSelection(obj)
            
            # Ensure Part Design workbench (safe - doesn't crash)
            FreeCADGui.activateWorkbench("PartDesignWorkbench")
            
            # Trigger native fillet command - opens FreeCAD's fillet dialog
            FreeCADGui.runCommand('PartDesign_Fillet', 0)
            
            # Store command info for potential follow-up
            self.last_commands['fillet'] = {'radius': radius, 'object': object_name}
            
            result = f"✅ FreeCAD Fillet Tool Opened"
            if object_name:
                result += f"\n📦 Pre-selected: {object_name}"
            result += f"\n⚙️  Suggested radius: {radius}mm"
            result += f"\n\n👉 Complete in FreeCAD:\n1. Select edges to fillet\n2. Set radius ({radius}mm)\n3. Click OK"
            
            return result
            
        except Exception as e:
            return f"Error opening fillet tool: {e}"
    
    def trigger_chamfer_command(self, args: Dict[str, Any]) -> str:
        """Trigger native FreeCAD chamfer command"""
        try:
            object_name = args.get('object_name', '')
            distance = args.get('distance', 1.0)
            
            # Pre-select object if specified
            if object_name:
                doc = FreeCAD.ActiveDocument
                if doc:
                    obj = doc.getObject(object_name)
                    if obj:
                        FreeCADGui.Selection.clearSelection()
                        FreeCADGui.Selection.addSelection(obj)
            
            # Ensure Part Design workbench (safe - doesn't crash)
            FreeCADGui.activateWorkbench("PartDesignWorkbench")
            
            # Trigger native chamfer command
            FreeCADGui.runCommand('PartDesign_Chamfer', 0)
            
            self.last_commands['chamfer'] = {'distance': distance, 'object': object_name}
            
            result = f"✅ FreeCAD Chamfer Tool Opened"
            if object_name:
                result += f"\n📦 Pre-selected: {object_name}"
            result += f"\n⚙️  Suggested distance: {distance}mm"
            result += f"\n\n👉 Complete in FreeCAD:\n1. Select edges to chamfer\n2. Set distance ({distance}mm)\n3. Click OK"
            
            return result
            
        except Exception as e:
            return f"Error opening chamfer tool: {e}"
    
    def trigger_hole_command(self, args: Dict[str, Any]) -> str:
        """Trigger native FreeCAD hole wizard"""
        try:
            diameter = args.get('diameter', 6.0)
            depth = args.get('depth', 10.0)
            
            # Ensure Part Design workbench (safe - doesn't crash)
            FreeCADGui.activateWorkbench("PartDesignWorkbench")
            
            # Trigger native hole command
            FreeCADGui.runCommand('PartDesign_Hole', 0)
            
            self.last_commands['hole'] = {'diameter': diameter, 'depth': depth}
            
            result = f"✅ FreeCAD Hole Wizard Opened"
            result += f"\n⚙️  Suggested diameter: {diameter}mm"
            result += f"\n⚙️  Suggested depth: {depth}mm"
            result += f"\n\n👉 Complete in FreeCAD:\n1. Select face for hole\n2. Position hole\n3. Set parameters (⌀{diameter}mm, depth {depth}mm)\n4. Click OK"
            
            return result
            
        except Exception as e:
            return f"Error opening hole wizard: {e}"
    
    def trigger_pad_command(self, args: Dict[str, Any]) -> str:
        """Trigger native FreeCAD pad command"""
        try:
            sketch_name = args.get('sketch_name', '')
            length = args.get('length', 10.0)
            
            # Pre-select sketch if specified
            if sketch_name:
                doc = FreeCAD.ActiveDocument
                if doc:
                    sketch = doc.getObject(sketch_name)
                    if sketch:
                        FreeCADGui.Selection.clearSelection()
                        FreeCADGui.Selection.addSelection(sketch)
            
            # Ensure Part Design workbench (safe - doesn't crash)
            FreeCADGui.activateWorkbench("PartDesignWorkbench")
            
            # Trigger native pad command
            FreeCADGui.runCommand('PartDesign_Pad', 0)
            
            self.last_commands['pad'] = {'length': length, 'sketch': sketch_name}
            
            result = f"✅ FreeCAD Pad Tool Opened"
            if sketch_name:
                result += f"\n📐 Pre-selected: {sketch_name}"
            result += f"\n⚙️  Suggested length: {length}mm"
            result += f"\n\n👉 Complete in FreeCAD:\n1. Confirm sketch selection\n2. Set pad length ({length}mm)\n3. Choose direction\n4. Click OK"
            
            return result
            
        except Exception as e:
            return f"Error opening pad tool: {e}"
    
    def trigger_pocket_command(self, args: Dict[str, Any]) -> str:
        """Trigger native FreeCAD pocket command"""
        try:
            sketch_name = args.get('sketch_name', '')
            length = args.get('length', 10.0)
            
            # Pre-select sketch if specified
            if sketch_name:
                doc = FreeCAD.ActiveDocument
                if doc:
                    sketch = doc.getObject(sketch_name)
                    if sketch:
                        FreeCADGui.Selection.clearSelection()
                        FreeCADGui.Selection.addSelection(sketch)
            
            # Ensure Part Design workbench (safe - doesn't crash)
            FreeCADGui.activateWorkbench("PartDesignWorkbench")
            
            # Trigger native pocket command
            FreeCADGui.runCommand('PartDesign_Pocket', 0)
            
            self.last_commands['pocket'] = {'length': length, 'sketch': sketch_name}
            
            result = f"✅ FreeCAD Pocket Tool Opened"
            if sketch_name:
                result += f"\n📐 Pre-selected: {sketch_name}"
            result += f"\n⚙️  Suggested depth: {length}mm"
            result += f"\n\n👉 Complete in FreeCAD:\n1. Confirm sketch selection\n2. Set pocket depth ({length}mm)\n3. Choose direction\n4. Click OK"
            
            return result
            
        except Exception as e:
            return f"Error opening pocket tool: {e}"
    
    def trigger_pattern_command(self, args: Dict[str, Any]) -> str:
        """Trigger native FreeCAD pattern commands"""
        try:
            pattern_type = args.get('type', 'linear')  # linear, polar
            feature_name = args.get('feature_name', '')
            count = args.get('count', 3)
            spacing = args.get('spacing', 10.0)
            
            # Pre-select feature if specified
            if feature_name:
                doc = FreeCAD.ActiveDocument
                if doc:
                    feature = doc.getObject(feature_name)
                    if feature:
                        FreeCADGui.Selection.clearSelection()
                        FreeCADGui.Selection.addSelection(feature)
            
            # Ensure Part Design workbench (safe - doesn't crash)
            FreeCADGui.activateWorkbench("PartDesignWorkbench")
            
            # Trigger appropriate pattern command
            if pattern_type.lower() == 'polar':
                FreeCADGui.runCommand('PartDesign_PolarPattern', 0)
                command_name = "Polar Pattern"
            else:
                FreeCADGui.runCommand('PartDesign_LinearPattern', 0)
                command_name = "Linear Pattern"
            
            self.last_commands['pattern'] = {'type': pattern_type, 'count': count, 'spacing': spacing}
            
            result = f"✅ FreeCAD {command_name} Tool Opened"
            if feature_name:
                result += f"\n🔧 Pre-selected: {feature_name}"
            result += f"\n⚙️  Suggested count: {count}"
            result += f"\n⚙️  Suggested spacing: {spacing}mm"
            result += f"\n\n👉 Complete in FreeCAD:\n1. Select feature to pattern\n2. Set direction/axis\n3. Set count ({count}) and spacing ({spacing}mm)\n4. Click OK"
            
            return result
            
        except Exception as e:
            return f"Error opening pattern tool: {e}"
    
    
    
    # =====================================================================
    # WORKBENCH & VIEW COMMANDS
    # =====================================================================
    
    def trigger_workbench_command(self, workbench_name: str) -> str:
        """Switch to specified workbench"""
        try:
            # Map common names to actual workbench classes
            workbench_map = {
                'partdesign': 'PartDesignWorkbench',
                'part': 'PartWorkbench', 
                'draft': 'DraftWorkbench',
                'arch': 'ArchWorkbench',
                'mesh': 'MeshWorkbench'
            }
            
            wb_name = workbench_map.get(workbench_name.lower(), workbench_name)
            
            FreeCADGui.activateWorkbench(wb_name)
            
            return f"✅ Switched to {workbench_name.title()} workbench"
            
        except Exception as e:
            return f"Error switching workbench: {e}"
    
    def trigger_view_command(self, view_type: str) -> str:
        """Set standard view orientations"""
        try:
            view_commands = {
                'top': 'Std_ViewTop',
                'bottom': 'Std_ViewBottom', 
                'front': 'Std_ViewFront',
                'back': 'Std_ViewRear',
                'rear': 'Std_ViewRear',  # Alias for back
                'left': 'Std_ViewLeft',
                'right': 'Std_ViewRight',
                'iso': 'Std_ViewIsometric',
                'isometric': 'Std_ViewIsometric',  # Full name support
                'axo': 'Std_ViewAxometric',
                'axonometric': 'Std_ViewAxometric',  # Full name support
                'fit': 'Std_ViewFitAll',
                'fitall': 'Std_ViewFitAll'  # Alternative name
            }
            
            if view_type.lower() not in view_commands:
                return f"❌ Unknown view type: {view_type}"
            
            command = view_commands[view_type.lower()]
            FreeCADGui.runCommand(command, 0)
            
            return f"✅ View set to {view_type.title()}"
            
        except Exception as e:
            return f"Error setting view: {e}"
    
    # =====================================================================
    # DOCUMENT COMMANDS
    # =====================================================================
    
    
    def trigger_save_command(self, filepath: str = "") -> str:
        """Save document"""
        try:
            if filepath:
                # Save as specific file
                if FreeCAD.ActiveDocument:
                    FreeCAD.ActiveDocument.saveAs(filepath)
                return f"✅ Document saved as: {filepath}"
            else:
                # Regular save
                FreeCADGui.runCommand('Std_Save', 0)
                return f"✅ Document saved"
            
        except Exception as e:
            return f"Error saving document: {e}"
    
    # =====================================================================
    # UTILITY COMMANDS
    # =====================================================================
    
    def get_last_command_info(self, command_type: str = "") -> str:
        """Get info about last executed command"""
        try:
            if command_type and command_type in self.last_commands:
                info = self.last_commands[command_type]
                return f"Last {command_type} command: {info}"
            elif self.last_commands:
                result = "Recent commands:\n"
                for cmd_type, info in self.last_commands.items():
                    result += f"- {cmd_type}: {info}\n"
                return result
            else:
                return "No recent commands tracked"
                
        except Exception as e:
            return f"Error getting command info: {e}"

# Global instance
_modal_system = None

def get_modal_system():
    """Get global modal command system"""
    global _modal_system
    if _modal_system is None:
        _modal_system = ModalCommandSystem()
    return _modal_system