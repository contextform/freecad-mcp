# Claude Code Setup for FreeCAD AI Copilot

## Quick Setup

1. **Make sure you have Claude Code installed** and can run `claude` command
2. **Navigate to this project directory:**
   ```bash
   cd /Users/josephwu/Documents/FreeCAD_MCP
   ```
3. **Start Claude Code from this directory:**
   ```bash
   claude
   ```

That's it! Claude Code will automatically detect the `.claude/mcp.json` config and load the FreeCAD MCP server.

## Testing the Connection

1. **Start FreeCAD** and make sure the AI Copilot workbench loads
2. **In Claude Code**, try these commands:
   ```
   Use the check_freecad_connection tool
   
   Use the test_echo tool with message "hello freecad"
   
   Create a box that's 20x20x20mm using the create_box tool
   ```

## Available Tools

Once connected, you'll have access to 19+ FreeCAD tools:

**Object Creation:**
- `create_box` - Create boxes with dimensions
- `create_cylinder` - Create cylinders  
- `create_sphere` - Create spheres

**Document Management:**
- `new_document` - Create new FreeCAD document
- `save_document` - Save current document
- `list_all_objects` - List all objects in document

**View Control:**
- `get_screenshot` - Take screenshot of FreeCAD view
- `set_view` - Change 3D view orientation
- `fit_all` - Fit all objects in view

**AI Agent:**
- `ai_agent` - Use natural language requests like "Make all holes 2mm bigger"

## Dual Setup

You can use **both** Claude Desktop and Claude Code with the same FreeCAD installation:

- **Claude Desktop:** Uses `claude_desktop_config.json` 
- **Claude Code:** Uses `.claude/mcp.json`
- **Same FreeCAD connection** for both!

## Troubleshooting

**"FreeCAD not available" error:**
1. Make sure FreeCAD is running
2. Load the AI Copilot workbench (or any workbench - the service runs globally)
3. Check that `/tmp/freecad_mcp.sock` exists

**MCP server errors:**
1. Check Python 3.11 is installed: `/opt/homebrew/bin/python3.11 --version`
2. Install MCP if needed: `pip install mcp`