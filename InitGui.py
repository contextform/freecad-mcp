# FreeCAD 1.0 AI Copilot - Global Service
# Copyright (c) 2024
# SPDX-License-Identifier: LGPL-2.1-or-later

import FreeCAD
import FreeCADGui
import os
import sys

# Add our directory to Python path
import inspect
try:
    current_file = inspect.getfile(inspect.currentframe())
    path = os.path.dirname(current_file)
except:
    # Fallback for FreeCAD
    path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "AICopilot")

if path not in sys.path:
    sys.path.append(path)

# ============================================================================
# GLOBAL AI SERVICE - AUTO-START
# Runs immediately when FreeCAD GUI loads, available from any workbench
# ============================================================================

class GlobalAIService:
    """Global AI service that runs across all workbenches"""
    
    def __init__(self):
        self.socket_server = None
        self.event_observer = None
        self.is_running = False
        
    def start(self):
        """Start the global AI service"""
        if self.is_running:
            FreeCAD.Console.PrintMessage("AI Service already running\n")
            return
            
        FreeCAD.Console.PrintMessage("🤖 Starting FreeCAD AI Copilot Service...\n")
        
        # Start socket server for Claude Desktop communication
        try:
            from socket_server import FreeCADSocketServer
            self.socket_server = FreeCADSocketServer()
            if self.socket_server.start_server():
                FreeCAD.__ai_socket_server = self.socket_server
                FreeCAD.Console.PrintMessage("✅ AI Socket Server started - Claude Desktop ready\n")
            else:
                FreeCAD.Console.PrintError("❌ Failed to start AI socket server\n")
                return False
        except Exception as e:
            FreeCAD.Console.PrintError(f"❌ Socket server error: {e}\n")
            return False
            
        # Start event observer for learning
        try:
            from event_observer import FreeCADEventObserver
            self.event_observer = FreeCADEventObserver()
            self.event_observer.start()
            FreeCAD.__ai_observer = self.event_observer
            FreeCAD.Console.PrintMessage("✅ AI Event Observer started - Learning enabled\n")
        except Exception as e:
            FreeCAD.Console.PrintError(f"❌ Event observer error: {e}\n")
            
        self.is_running = True
        FreeCAD.__ai_global_service = self
        FreeCAD.Console.PrintMessage("🎯 AI Copilot Service running - Available from ALL workbenches!\n")
        return True
        
    def stop(self):
        """Stop the global AI service"""
        if not self.is_running:
            return
            
        FreeCAD.Console.PrintMessage("🔄 Stopping AI Copilot Service...\n")
        
        if self.socket_server:
            self.socket_server.stop_server()
            self.socket_server = None
            
        if self.event_observer:
            self.event_observer = None
            
        self.is_running = False
        
        # Clean up global references
        if hasattr(FreeCAD, '__ai_socket_server'):
            delattr(FreeCAD, '__ai_socket_server')
        if hasattr(FreeCAD, '__ai_observer'):
            delattr(FreeCAD, '__ai_observer')
        if hasattr(FreeCAD, '__ai_global_service'):
            delattr(FreeCAD, '__ai_global_service')
            
        FreeCAD.Console.PrintMessage("✅ AI Copilot Service stopped\n")

# ============================================================================
# AUTO-START: Initialize AI service when FreeCAD GUI loads
# ============================================================================
try:
    # Initialize immediately after class definition
    if not hasattr(FreeCAD, '__ai_global_service'):
        service = GlobalAIService()
        if service.start():
            FreeCAD.Console.PrintMessage("🚀 FreeCAD AI Copilot ready! Works from any workbench.\n")
        else:
            FreeCAD.Console.PrintError("⚠️  AI Copilot failed to start\n")
except Exception as e:
    FreeCAD.Console.PrintError(f"AI Copilot auto-start failed: {e}\n")

# ============================================================================
# AI COPILOT WORKBENCH - Optional UI Panel
# Service runs globally, but this workbench provides management tools
# ============================================================================

class AICopilotWorkbench(FreeCADGui.Workbench):
    """AI Copilot management workbench - optional UI for service control"""
    
    def __init__(self):
        # Get icon path
        try:
            current_file = inspect.getfile(inspect.currentframe())
            icon_path = os.path.join(os.path.dirname(current_file), "Resources", "icons", "AICopilot.svg")
        except:
            icon_path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "AICopilot", "Resources", "icons", "AICopilot.svg")
        
        self.__class__.Icon = icon_path
        self.__class__.MenuText = "AI Copilot"
        self.__class__.ToolTip = "AI Copilot service management (service runs globally)"
        
    def Initialize(self):
        """Initialize workbench - service is already running globally"""
        FreeCAD.Console.PrintMessage("AI Copilot Workbench initialized\n")
        
        # Simple management commands
        self.ai_commands = ["AI_ServiceStatus", "AI_RestartService"]
        
        try:
            # Create basic management toolbar
            self.appendToolbar("AI Service", self.ai_commands)
            self.appendMenu("AI Service", self.ai_commands)
            
            # Register simple commands
            self._register_management_commands()
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"Failed to setup AI management: {e}\n")
            
        # Service status check
        if hasattr(FreeCAD, '__ai_global_service'):
            service = FreeCAD.__ai_global_service
            if service.is_running:
                FreeCAD.Console.PrintMessage("✅ Global AI Service is running\n")
            else:
                FreeCAD.Console.PrintWarning("⚠️  Global AI Service not running\n")
        else:
            FreeCAD.Console.PrintWarning("⚠️  Global AI Service not found\n")
            
    def Activated(self):
        """Called when user switches to this workbench"""
        FreeCAD.Console.PrintMessage("AI Copilot management workbench activated\n")
        
        # Show service status
        if hasattr(FreeCAD, '__ai_global_service'):
            service = FreeCAD.__ai_global_service
            FreeCAD.Console.PrintMessage(f"AI Service Status: {'Running' if service.is_running else 'Stopped'}\n")
            
    def Deactivated(self):
        """Called when user switches away from this workbench"""
        FreeCAD.Console.PrintMessage("AI Copilot management workbench deactivated\n")
        # NOTE: Global service continues running!
        
    def ContextMenu(self, recipient):
        """Add context menu items"""
        if hasattr(self, 'ai_commands'):
            self.appendContextMenu("AI Copilot", self.ai_commands)
        
    def GetClassName(self):
        """Return the workbench classname"""
        return "Gui::PythonWorkbench"
        
    def _register_management_commands(self):
        """Register simple management commands"""
        
        # Service Status Command
        class AI_ServiceStatus:
            def Activated(self):
                if hasattr(FreeCAD, '__ai_global_service'):
                    service = FreeCAD.__ai_global_service
                    status = "🟢 RUNNING" if service.is_running else "🔴 STOPPED"
                    FreeCAD.Console.PrintMessage(f"\n=== AI Copilot Service Status ===\n")
                    FreeCAD.Console.PrintMessage(f"Status: {status}\n")
                    FreeCAD.Console.PrintMessage(f"Socket Server: {'Active' if service.socket_server else 'Inactive'}\n")
                    FreeCAD.Console.PrintMessage(f"Event Observer: {'Active' if service.event_observer else 'Inactive'}\n")
                    FreeCAD.Console.PrintMessage(f"Claude Desktop: {'Connected' if os.path.exists('/tmp/freecad_mcp.sock') else 'Disconnected'}\n")
                    FreeCAD.Console.PrintMessage("==================================\n")
                else:
                    FreeCAD.Console.PrintError("❌ AI Service not found\n")
                    
            def GetResources(self):
                return {'Pixmap': 'AICopilot.svg', 'MenuText': 'Service Status', 'ToolTip': 'Show AI service status'}
        
        # Restart Service Command  
        class AI_RestartService:
            def Activated(self):
                try:
                    FreeCAD.Console.PrintMessage("🔄 Restarting AI Copilot Service...\n")
                    
                    # Stop existing service
                    if hasattr(FreeCAD, '__ai_global_service'):
                        service = FreeCAD.__ai_global_service
                        service.stop()
                    
                    # Start new service
                    new_service = GlobalAIService()
                    if new_service.start():
                        FreeCAD.Console.PrintMessage("✅ AI Service restarted successfully\n")
                    else:
                        FreeCAD.Console.PrintError("❌ Failed to restart AI Service\n")
                        
                except Exception as e:
                    FreeCAD.Console.PrintError(f"❌ Restart failed: {e}\n")
                    
            def GetResources(self):
                return {'Pixmap': 'AICopilot.svg', 'MenuText': 'Restart Service', 'ToolTip': 'Restart AI service'}
        
        # Register commands
        FreeCADGui.addCommand('AI_ServiceStatus', AI_ServiceStatus())
        FreeCADGui.addCommand('AI_RestartService', AI_RestartService())

# Register the workbench
FreeCADGui.addWorkbench(AICopilotWorkbench())