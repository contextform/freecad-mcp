#!/usr/bin/env python3
"""
Quick test to verify MCP server components are importable
Run this from command line: python quick_test.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("FreeCAD MCP Quick Import Test")
print("=" * 50)

# Test 1: Check basic imports
print("\n1. Testing basic Python imports...")
try:
    import json
    import base64
    import asyncio
    print("✓ Standard libraries OK")
except ImportError as e:
    print(f"✗ Missing standard library: {e}")

# Test 2: Check MCP library
print("\n2. Testing MCP library...")
try:
    from mcp import Server, Tool
    from mcp.types import TextContent
    print("✓ MCP library OK")
except ImportError as e:
    print(f"✗ MCP library not installed: {e}")
    print("  Install with: pip install mcp")

# Test 3: Check our modules
print("\n3. Testing our MCP modules...")

modules_to_test = [
    ("event_observer", "FreeCADEventObserver"),
    ("memory_system", "CADMemorySystem"),
    ("mcp_server", "EmbeddedMCPServer"),
    ("mcp_server_enhanced", "EnhancedFreeCADMCP"),
    ("mcp_bridge", "MCPBridge"),
    ("simple_bridge", None),
]

for module_name, class_name in modules_to_test:
    try:
        module = __import__(module_name)
        if class_name and hasattr(module, class_name):
            print(f"✓ {module_name}.{class_name} OK")
        else:
            print(f"✓ {module_name} OK")
    except ImportError as e:
        print(f"✗ {module_name}: {e}")
    except Exception as e:
        print(f"⚠ {module_name}: {e}")

# Test 4: Check FreeCAD-specific imports (will fail outside FreeCAD)
print("\n4. Testing FreeCAD imports (expected to fail outside FreeCAD)...")
try:
    import FreeCAD
    import FreeCADGui
    print("✓ FreeCAD modules available (running inside FreeCAD)")
except ImportError:
    print("ℹ FreeCAD modules not available (this is normal outside FreeCAD)")

# Test 5: Check PySide2 (Qt)
print("\n5. Testing Qt/PySide2...")
try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtTest import QTest
    print("✓ PySide2 and QtTest available")
except ImportError as e:
    print(f"⚠ PySide2 not available: {e}")
    print("  Note: PySide2 is usually provided by FreeCAD")

# Test 6: Check optional dependencies
print("\n6. Testing optional dependencies...")
try:
    import numpy
    print(f"✓ numpy {numpy.__version__}")
except ImportError:
    print("⚠ numpy not installed (optional for memory system)")

try:
    import sqlite3
    print(f"✓ sqlite3 available")
except ImportError:
    print("⚠ sqlite3 not available")

print("\n" + "=" * 50)
print("Test Summary:")
print("=" * 50)
print("""
If running OUTSIDE FreeCAD:
- MCP library and our modules should import OK
- FreeCAD/PySide2 imports will fail (this is normal)

If running INSIDE FreeCAD:
- All imports should work
- Use test_enhanced_mcp.py for full testing

To use with Claude Desktop:
1. Start FreeCAD
2. Switch to AI Copilot workbench
3. Configure Claude Desktop with the bridge script
""")

# Check if we're in FreeCAD
try:
    import FreeCAD
    print("\n✓ You're running inside FreeCAD!")
    print("  Run this in FreeCAD's Python console for full test:")
    print("  exec(open('/Users/josephwu/Documents/FreeCAD_MCP/test_enhanced_mcp.py').read())")
except:
    print("\nℹ You're running outside FreeCAD")
    print("  This is fine for checking dependencies")
    print("  For full testing, run test_enhanced_mcp.py inside FreeCAD")