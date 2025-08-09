# Testing FreeCAD MCP with Claude Desktop

## Complete Setup & Testing Guide

### Step 1: Install Dependencies
```bash
# Install MCP library
pip install mcp

# Install other dependencies
pip install numpy
```

### Step 2: Install in FreeCAD
```bash
# Copy to FreeCAD Mod directory
cp -r /Users/josephwu/Documents/FreeCAD_MCP ~/Library/Application\ Support/FreeCAD/Mod/AICopilot

# Or create a symlink (easier for development)
ln -s /Users/josephwu/Documents/FreeCAD_MCP ~/Library/Application\ Support/FreeCAD/Mod/AICopilot
```

### Step 3: Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "freecad-ai": {
      "command": "python3",
      "args": ["/Users/josephwu/Documents/FreeCAD_MCP/simple_bridge.py"],
      "env": {}
    }
  }
}
```

### Step 4: Start Everything

1. **Start FreeCAD**:
   - Open FreeCAD
   - Switch to "AI Copilot" workbench from dropdown
   - You should see in console: "Enhanced MCP Server embedded and ready"

2. **Start Claude Desktop**:
   - Open Claude Desktop
   - It will automatically connect to the MCP server

### Step 5: Test Commands in Claude

## 🧪 Test Sequence for Claude Desktop

Copy and paste these commands one by one into Claude:

### Basic Connection Test:
```
Can you check if you're connected to FreeCAD? List all available tools you have for FreeCAD control.
```

### Test 1: Document Operations
```
Please create a new FreeCAD document called "TestProject" and tell me what you see.
```

### Test 2: Create Objects
```
Create a box with dimensions 20x30x40 mm at position (10, 10, 0). Then take a screenshot and show it to me.
```

### Test 3: GUI Control
```
List all available workbenches in FreeCAD. Then switch to the Part Design workbench.
```

### Test 4: Selection and Query
```
List all objects in the current document. Select the box we created and tell me its properties.
```

### Test 5: Screenshot with Base64
```
Take a screenshot of the current 3D view and display it. Fit all objects in view first.
```

### Test 6: Complex Operation
```
Create a cylinder with radius 15mm and height 50mm at position (50, 10, 0). Then create a boolean cut where the cylinder cuts through the box.
```

### Test 7: Save as Part
```
Save the current selection as a reusable part called "TestPart" in category "General". Then list all parts in the library.
```

### Test 8: Mouse/Keyboard Test
```
Click at coordinates (400, 300) in the 3D view. Then send the keyboard shortcut Ctrl+A to select all.
```

### Test 9: Command Execution
```
Execute the FreeCAD command to fit all objects in view. List available commands that contain "View".
```

### Test 10: Full Workflow
```
Please do the following:
1. Create a new document
2. Create a sketch on XY plane
3. Add a circle with radius 25mm
4. Exit sketch
5. Pad the sketch by 30mm
6. Take a screenshot and show me the result
```

## 🔍 What to Look For

### In FreeCAD Console:
- ✅ "Enhanced MCP Server embedded and ready"
- ✅ "Event observer started"
- ✅ "MCP Server started on embedded connection"

### In Claude Desktop:
- ✅ Claude should respond with actual FreeCAD data
- ✅ Screenshots should appear as embedded images
- ✅ Object properties should be accurate
- ✅ Commands should execute in FreeCAD

### In FreeCAD UI:
- ✅ Objects appear as Claude creates them
- ✅ Workbench switches when commanded
- ✅ Selection changes as Claude selects objects
- ✅ View updates (zoom, rotation) work

## 🐛 Troubleshooting

### "MCP server not connected":
1. Check if FreeCAD is running with AI Copilot workbench
2. Verify socket exists: `ls -la /tmp/freecad_mcp.sock`
3. Restart both FreeCAD and Claude Desktop

### "No tools available":
1. Check Claude Desktop config path is correct
2. Verify simple_bridge.py path is absolute
3. Check Python path in config

### "Commands don't execute":
1. Make sure FreeCAD window is not blocked by dialogs
2. Check FreeCAD console for error messages
3. Try simpler commands first

### "Screenshots don't work":
1. Create an object first (empty view can't screenshot)
2. Check if view is active: `FreeCADGui.ActiveDocument`
3. Try "ViewFit" command first

## 📝 Expected Responses from Claude

When properly connected, Claude should respond like:

```
"I can see I have access to FreeCAD through the MCP connection. I have tools for:
- Creating and managing documents
- Creating 3D objects (boxes, cylinders, spheres)
- Boolean operations
- Taking screenshots
- GUI automation
- Command execution
[... lists all available tools ...]"
```

And when executing commands:

```
"I've created a box with dimensions 20x30x40mm at position (10, 10, 0). 
Here's a screenshot of the current view: [base64 image displayed]
The box has been successfully added to the document."
```

## 🚀 Advanced Testing

Once basic tests work, try:

1. **Complex Geometry**:
   ```
   Create a parametric bracket with mounting holes
   ```

2. **Assembly Operations**:
   ```
   Create multiple parts and position them in an assembly
   ```

3. **Sketch-based Workflow**:
   ```
   Create a complex 2D sketch and revolve it around an axis
   ```

4. **File Operations**:
   ```
   Save the current document as "TestProject.FCStd" and create a parts library
   ```

## ✅ Success Indicators

- Claude can see and describe FreeCAD's state
- Objects appear in FreeCAD as Claude creates them
- Screenshots show up in Claude's responses
- GUI operations (menu clicks, shortcuts) work
- Complex workflows complete successfully

## 📊 Performance Check

Ask Claude:
```
Can you create 10 boxes in a grid pattern (5x2) with 30mm spacing, 
then take a screenshot and tell me how long it took?
```

This tests:
- Batch operations
- Precise positioning
- Performance measurement
- Visual feedback