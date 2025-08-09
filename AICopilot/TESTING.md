# Testing the Enhanced FreeCAD MCP Server

## Prerequisites

1. **FreeCAD** installed and running
2. **Python dependencies**:
   ```bash
   pip install mcp numpy
   ```

## Testing Steps

### Step 1: Quick Dependency Check
Run this from terminal to check basic dependencies:
```bash
cd /Users/josephwu/Documents/FreeCAD_MCP
python3 quick_test.py
```

### Step 2: Install in FreeCAD
1. Copy the entire folder to FreeCAD's Mod directory:
   ```bash
   cp -r /Users/josephwu/Documents/FreeCAD_MCP ~/Library/Application\ Support/FreeCAD/Mod/AICopilot
   ```

2. Start FreeCAD

3. Switch to "AI Copilot" workbench from the dropdown

### Step 3: Test Inside FreeCAD
Run this in FreeCAD's Python console:
```python
# Basic test
exec(open('/Users/josephwu/Documents/FreeCAD_MCP/test_enhanced_mcp.py').read())
```

### Step 4: Test Individual Features

#### Test Screenshot with Base64:
```python
import FreeCAD, FreeCADGui
import sys
sys.path.append('/Users/josephwu/Documents/FreeCAD_MCP')
from mcp_server_enhanced import EnhancedFreeCADMCP

# Create MCP instance
mcp = EnhancedFreeCADMCP()

# Create a test object
doc = FreeCAD.newDocument()
box = doc.addObject("Part::Box", "TestBox")
doc.recompute()
FreeCADGui.SendMsgToActiveView("ViewFit")

# Test screenshot (would be async in real MCP)
# For testing, we'll call the function directly
import asyncio
result = asyncio.run(mcp.server.get_screenshot())
print("Screenshot result length:", len(result))
```

#### Test GUI Control:
```python
# Test finding widgets
from PySide2 import QtWidgets
main_window = FreeCADGui.getMainWindow()

# List toolbars
toolbars = main_window.findChildren(QtWidgets.QToolBar)
print(f"Found {len(toolbars)} toolbars")

# Test menu access
menubar = main_window.menuBar()
menus = [action.text() for action in menubar.actions()]
print("Available menus:", menus)
```

#### Test Mouse/Keyboard:
```python
from PySide2.QtTest import QTest
from PySide2 import QtCore

# Check if QTest is available
print("QTest available:", hasattr(QTest, 'mouseClick'))
print("Can simulate clicks:", hasattr(QTest, 'keyClick'))
```

## Expected Results

### ✅ All Tests Pass:
- Basic setup: Module imports work
- Screenshot: Creates base64 encoded images
- Serialization: Objects can be serialized/deserialized
- GUI Access: Can access menus, toolbars, widgets
- Mouse Automation: QTest methods available
- Keyboard Automation: Key simulation ready
- Command Execution: Can run FreeCAD commands

### ⚠️ Common Issues:

1. **ImportError for 'mcp'**:
   ```bash
   pip install mcp
   ```

2. **ImportError for 'numpy'**:
   ```bash
   pip install numpy
   ```

3. **"No module named PySide2"** outside FreeCAD:
   - This is normal - PySide2 comes with FreeCAD

4. **Permission errors**:
   - Make sure FreeCAD has permission to access the file system
   - Check that the Mod directory is writable

## Testing with Claude Desktop

Once all tests pass in FreeCAD:

1. Configure Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "freecad-copilot": {
      "command": "python3",
      "args": ["/Users/josephwu/Documents/FreeCAD_MCP/simple_bridge.py"]
    }
  }
}
```

2. Start FreeCAD with AI Copilot workbench

3. Start Claude Desktop

4. Test commands in Claude:
   - "Show me the current FreeCAD state"
   - "Create a box at position 10,10,10"
   - "Take a screenshot of the current view"
   - "List all available workbenches"

## Success Indicators

- ✅ FreeCAD console shows "Enhanced MCP Server embedded and ready"
- ✅ Test suite shows all tests passing
- ✅ Claude can connect and execute commands
- ✅ Screenshots appear as base64 images in Claude
- ✅ GUI automation works (clicking, typing)

## Troubleshooting

### MCP Server doesn't start:
Check FreeCAD console for error messages. Common issues:
- Missing dependencies (mcp, numpy)
- Path issues (update sys.path in InitGui.py)
- Import errors (check module names)

### Bridge can't connect:
- Ensure FreeCAD is running with AI Copilot workbench active
- Check socket path exists: `/tmp/freecad_mcp.sock`
- Verify bridge script path in Claude config

### GUI automation fails:
- Some operations require FreeCAD to be in focus
- Certain dialogs may block automation
- Try running FreeCAD in foreground