# FreeCAD Commands for AI Copilot Workbench

import FreeCAD
import FreeCADGui
from PySide2 import QtCore, QtGui, QtWidgets

class AI_Connect:
    """Command to connect to Claude"""
    
    def GetResources(self):
        return {
            'Pixmap': 'connect.svg',
            'MenuText': 'Connect to AI',
            'ToolTip': 'Start AI assistant connection'
        }
        
    def Activated(self):
        """Called when command is activated"""
        if hasattr(FreeCAD, '__ai_mcp_server'):
            FreeCAD.__ai_mcp_server.ensure_running()
            
            # Show connection dialog
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("AI Copilot Connected")
            msg.setInformativeText("Add to Claude Desktop config:\n\nfreecad-copilot:\n  command: python\n  args: [mcp_bridge.py]")
            msg.setWindowTitle("AI Connection")
            msg.exec_()
        else:
            FreeCAD.Console.PrintError("MCP server not initialized\n")
            
    def IsActive(self):
        """Return whether command is active"""
        return True

class AI_Disconnect:
    """Command to disconnect from Claude"""
    
    def GetResources(self):
        return {
            'Pixmap': 'disconnect.svg',
            'MenuText': 'Disconnect AI',
            'ToolTip': 'Stop AI assistant'
        }
        
    def Activated(self):
        """Called when command is activated"""
        if hasattr(FreeCAD, '__ai_mcp_server'):
            FreeCAD.__ai_mcp_server.stop()
            FreeCAD.Console.PrintMessage("AI Copilot disconnected\n")
            
    def IsActive(self):
        """Return whether command is active"""
        return hasattr(FreeCAD, '__ai_mcp_server') and FreeCAD.__ai_mcp_server.is_running

class AI_ShowMemory:
    """Command to show AI memory/learning"""
    
    def GetResources(self):
        return {
            'Pixmap': 'memory.svg',
            'MenuText': 'Show AI Memory',
            'ToolTip': 'View learned patterns and preferences'
        }
        
    def Activated(self):
        """Show memory dialog"""
        if not hasattr(FreeCAD, '__ai_mcp_server'):
            FreeCAD.Console.PrintError("AI not initialized\n")
            return
            
        memory = FreeCAD.__ai_mcp_server.memory_system
        if not memory:
            FreeCAD.Console.PrintError("Memory system not available\n")
            return
            
        # Create dialog
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("AI Memory & Learning")
        dialog.resize(600, 400)
        
        layout = QtWidgets.QVBoxLayout()
        
        # Tabs for different memory aspects
        tabs = QtWidgets.QTabWidget()
        
        # Patterns tab
        patterns_widget = QtWidgets.QTextEdit()
        patterns_widget.setReadOnly(True)
        patterns = memory.get_common_patterns()
        patterns_text = "Learned Patterns:\n\n"
        for p in patterns:
            patterns_text += f"• {p['name']}\n"
            patterns_text += f"  Frequency: {p['frequency']}, Success: {p['success_rate']:.1%}\n\n"
        patterns_widget.setText(patterns_text)
        tabs.addTab(patterns_widget, "Patterns")
        
        # Preferences tab
        prefs_widget = QtWidgets.QTextEdit()
        prefs_widget.setReadOnly(True)
        prefs = memory.get_preferences()
        prefs_text = "Learned Preferences:\n\n"
        for key, value in prefs.items():
            prefs_text += f"• {key}: {value}\n"
        prefs_widget.setText(prefs_text)
        tabs.addTab(prefs_widget, "Preferences")
        
        # Recent designs tab
        recent_widget = QtWidgets.QListWidget()
        designs = memory.recall_similar_designs("", limit=10)
        for d in designs:
            item = f"{d['description']} ({d['created']})"
            recent_widget.addItem(item)
        tabs.addTab(recent_widget, "Recent Designs")
        
        layout.addWidget(tabs)
        
        # Buttons
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def IsActive(self):
        """Return whether command is active"""
        return hasattr(FreeCAD, '__ai_mcp_server')

# Register commands
FreeCADGui.addCommand('AI_Connect', AI_Connect())
FreeCADGui.addCommand('AI_Disconnect', AI_Disconnect())
FreeCADGui.addCommand('AI_ShowMemory', AI_ShowMemory())