# FreeCAD initialization file for AICopilot Workbench
# This runs when FreeCAD starts (before GUI)

import FreeCAD
import os
import sys

# Add our directory to path
path = os.path.dirname(__file__)
if path not in sys.path:
    sys.path.append(path)

FreeCAD.Console.PrintMessage("AICopilot Workbench loading...\n")

# Module is loaded, GUI initialization happens in InitGui.py