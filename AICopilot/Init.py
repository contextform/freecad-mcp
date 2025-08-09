# FreeCAD initialization file for AICopilot Workbench
# This runs when FreeCAD starts (before GUI)

import FreeCAD
import os
import sys

# Add our directory to path
import inspect
try:
    current_file = inspect.getfile(inspect.currentframe())
    path = os.path.dirname(current_file)
except:
    # Fallback for FreeCAD
    path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "AICopilot")

if path not in sys.path:
    sys.path.append(path)

FreeCAD.Console.PrintMessage("AICopilot Workbench loading...\n")

# Module is loaded, GUI initialization happens in InitGui.py