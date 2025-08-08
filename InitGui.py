# FreeCAD 1.0 AI Copilot Workbench
# Copyright (c) 2024
# SPDX-License-Identifier: LGPL-2.1-or-later

import FreeCAD
import FreeCADGui
import os
import sys

# Add our directory to Python path
path = os.path.dirname(__file__)
if path not in sys.path:
    sys.path.append(path)

class AICopilotWorkbench(FreeCADGui.Workbench):
    """AI-powered CAD assistant with embedded MCP server and memory system"""
    
    def __init__(self):
        self.__class__.Icon = os.path.join(os.path.dirname(__file__), "Resources", "icons", "AICopilot.svg")
        self.__class__.MenuText = "AI Copilot"
        self.__class__.ToolTip = "AI-powered CAD assistant with memory"
        
    def Initialize(self):
        """Initialize the workbench when FreeCAD starts"""
        FreeCAD.Console.PrintMessage("Initializing AI Copilot Workbench...\n")
        
        # Import and register commands
        try:
            from commands import ai_commands
            self.ai_commands = ["AI_Connect", "AI_Disconnect", "AI_ShowMemory"]
            
            # Create toolbar
            self.appendToolbar("AI Copilot", self.ai_commands)
            
            # Create menu
            self.appendMenu("AI Copilot", self.ai_commands)
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"Failed to load AI commands: {e}\n")
            
        # Start the enhanced embedded MCP server
        try:
            # Try enhanced version first
            from mcp_server_enhanced import EnhancedFreeCADMCP
            self.mcp_server = EnhancedFreeCADMCP()
            FreeCAD.__ai_mcp_server = self.mcp_server
            FreeCAD.Console.PrintMessage("Enhanced MCP Server embedded and ready\n")
        except ImportError:
            # Fall back to original if enhanced not available
            try:
                from mcp_server import EmbeddedMCPServer
                self.mcp_server = EmbeddedMCPServer()
                FreeCAD.__ai_mcp_server = self.mcp_server
                FreeCAD.Console.PrintMessage("MCP Server embedded and ready\n")
            except Exception as e:
                FreeCAD.Console.PrintError(f"Failed to start MCP server: {e}\n")
        except Exception as e:
            FreeCAD.Console.PrintError(f"Failed to start enhanced MCP server: {e}\n")
            
        # Initialize event observer for capturing user interactions
        try:
            from event_observer import FreeCADEventObserver
            self.observer = FreeCADEventObserver()
            self.observer.start()
            FreeCAD.__ai_observer = self.observer
            FreeCAD.Console.PrintMessage("Event observer started\n")
        except Exception as e:
            FreeCAD.Console.PrintError(f"Failed to start event observer: {e}\n")
            
    def Activated(self):
        """Called when user switches to this workbench"""
        FreeCAD.Console.PrintMessage("AI Copilot Workbench activated\n")
        
        # Start MCP server if not already running
        if hasattr(self, 'mcp_server'):
            self.mcp_server.ensure_running()
            
    def Deactivated(self):
        """Called when user switches away from this workbench"""
        FreeCAD.Console.PrintMessage("AI Copilot Workbench deactivated\n")
        
    def ContextMenu(self, recipient):
        """Add context menu items"""
        self.appendContextMenu("AI Copilot", self.ai_commands)
        
    def GetClassName(self):
        """Return the workbench classname"""
        return "Gui::PythonWorkbench"

# Register the workbench
FreeCADGui.addWorkbench(AICopilotWorkbench())