# ContextForm FreeCAD AI Copilot for Claude Code

An intelligent AI copilot for FreeCAD that integrates seamlessly with Claude Code, providing deep CAD automation through natural language via the Model Context Protocol (MCP).

## Features

- 🤖 **Natural Language CAD Control** - Create 3D objects with conversational commands
- 🔧 **Real-time Socket Communication** - Direct FreeCAD control through Unix sockets
- 📊 **Event Observation** - Learns from user interactions to improve assistance
- 💾 **Memory System** - Remembers patterns and preferences across sessions
- 🎯 **Deep FreeCAD Integration** - Runs embedded for complete API access
- ⚡ **Claude Code MCP Integration** - Professional-grade AI assistant with full FreeCAD control
- 🏢 **ContextForm Branded** - Enterprise-ready with professional tool naming

## Architecture

```
Claude Code (AI Interface)
      ↕️ MCP Protocol
ContextForm Bridge Server (Python 3.11)
      ↕️ Unix Socket
FreeCAD Socket Server (Embedded)
      ↕️ Direct API
FreeCAD Core
```

### Why This Architecture?

- **Embedded Design**: Runs INSIDE FreeCAD for direct API access
- **Bridge Pattern**: Handles Python version differences (FreeCAD 3.9 vs MCP 3.11)
- **Socket Communication**: Fast, reliable IPC with minimal overhead
- **MCP Standard**: Uses official Model Context Protocol for Claude Code
- **Modular**: Each component can be updated independently

## Prerequisites

- FreeCAD 1.0 or later
- Python 3.11+ (for MCP bridge)
- **Claude Code** (Anthropic's official CLI)

## Quick Installation

### Step 1: Install Dependencies

```bash
# Install Python 3.11 (required for MCP)
brew install python@3.11                           # macOS
# or
sudo apt install python3.11 python3.11-venv       # Linux  
# or download from python.org                      # Windows

# Install MCP
/opt/homebrew/bin/python3.11 -m pip install mcp    # macOS
# or  
python3.11 -m pip install mcp                      # Linux/Windows

# Install Claude Code (choose one method)
npm install -g claude-code                          # NPM (recommended)
# or
brew install claude-code                            # Homebrew (macOS)
# or download from: https://github.com/anthropics/claude-code/releases

# Verify installation
claude --version
```

### Step 2: Install FreeCAD Workbench

```bash
# Clone this repository
git clone https://github.com/contextform/freecad-mcp.git
cd freecad-mcp

# Copy workbench to FreeCAD Mod directory
cp -r AICopilot ~/Library/Application\ Support/FreeCAD/Mod/        # macOS
# or
cp -r AICopilot ~/.FreeCAD/Mod/                                     # Linux  
# or
cp -r AICopilot %APPDATA%\FreeCAD\Mod\                             # Windows
```

### Step 3: Configure Claude Code MCP Server

Navigate to your project directory and add the MCP server:

```bash
cd freecad-mcp

# Add ContextForm FreeCAD MCP server to Claude Code
claude mcp add ctxform /opt/homebrew/bin/python3.11 /full/path/to/freecad-mcp/working_bridge.py

# Verify it's connected
claude mcp list
```

### Step 4: Start Using!

1. **Start FreeCAD** - AI Copilot service auto-starts  
2. **Go to any workbench** (Part Design, Sketcher, etc.)
3. **Open Claude Code** in your project directory:
   ```bash
   claude
   ```
4. **Verify MCP tools are loaded**:
   ```
   List available tools
   ```
   You should see tools like `mcp__ctxform__box`, `mcp__ctxform__cylinder`, etc.

5. **Start creating**: 
   ```
   Use the mcp__ctxform__box tool with length=50, width=30, height=20
   ```

🎉 **That's it!** The AI Copilot works from any FreeCAD workbench through Claude Code!

## Usage

### Basic Commands

In Claude Code, you can use these ContextForm FreeCAD tools:

```bash
# Check connection
Use the mcp__ctxform__check_freecad_connection tool

# Create 3D objects
Use the mcp__ctxform__box tool with length=50, width=30, height=20
Use the mcp__ctxform__cylinder tool with radius=15, height=40
Use the mcp__ctxform__sphere tool with radius=10

# Document management
Use the mcp__ctxform__list_objects tool
Use the mcp__ctxform__new_document tool with name="MyProject"
Use the mcp__ctxform__save_document tool

# Advanced features
Use the mcp__ctxform__screenshot tool with width=800, height=600
Use the mcp__ctxform__python tool with code="print('Hello FreeCAD!')"

# AI Agent for natural language
Use the mcp__ctxform__ai tool with request="Create a bracket with mounting holes"
```

### Example Workflow

```bash
# Start Claude Code in your project
cd freecad-mcp
claude

# Create objects
Use the mcp__ctxform__box tool with length=100, width=50, height=25
Use the mcp__ctxform__cylinder tool with radius=8, height=30, x=50

# Take a screenshot
Use the mcp__ctxform__screenshot tool

# Use AI for complex requests
Use the mcp__ctxform__ai tool with request="Position the cylinder on top of the box and make them blue"
```

## Available Tools

### **Connection & Status**
mcp__ctxform__check_freecad_connection: Check if FreeCAD is running with AI Copilot workbench.
mcp__ctxform__test_echo: Test tool that echoes back a message for connectivity verification.

### **Basic Shape Creation**
mcp__ctxform__create_box: Create a box in FreeCAD with specified dimensions (length, width, height).
mcp__ctxform__create_cylinder: Create a cylinder in FreeCAD with radius and height parameters.
mcp__ctxform__create_sphere: Create a sphere in FreeCAD with specified radius.
mcp__ctxform__create_cone: Create a cone with configurable top/bottom radius and height.
mcp__ctxform__create_torus: Create a torus (donut shape) with major and minor radius.
mcp__ctxform__create_wedge: Create a wedge (triangular prism) with full dimensional control.

### **Boolean Operations**
mcp__ctxform__fuse_objects: Fuse (union) two or more objects together into a single solid.
mcp__ctxform__cut_objects: Cut (subtract) objects from a base object for complex shapes.
mcp__ctxform__common_objects: Find common (intersection) of two or more objects.

### **Object Transformations**
mcp__ctxform__move_object: Move (translate) an object to a new position in 3D space.
mcp__ctxform__rotate_object: Rotate an object around X, Y, or Z axis by specified degrees.
mcp__ctxform__copy_object: Create a copy of an object with optional position offset.
mcp__ctxform__array_object: Create a linear array of an object with configurable spacing.

### **Part Design**
mcp__ctxform__create_sketch: Create a new sketch on XY, XZ, or YZ plane for advanced modeling.
mcp__ctxform__pad_sketch: Extrude a sketch to create a solid (pad operation) with specified length.
mcp__ctxform__pocket_sketch: Cut a sketch from a solid (pocket operation) with specified depth.
mcp__ctxform__fillet_edges: Add fillets (rounded edges) to an object with configurable radius.

### **Analysis Tools**
mcp__ctxform__measure_distance: Measure distance between two objects or their centers of mass.
mcp__ctxform__get_volume: Calculate the volume of an object in cubic millimeters.
mcp__ctxform__get_bounding_box: Get the bounding box dimensions and envelope of an object.
mcp__ctxform__get_mass_properties: Get comprehensive mass properties (volume, area, center of mass).

### **Document Management**
mcp__ctxform__new_document: Create a new FreeCAD document with optional custom name.
mcp__ctxform__save_document: Save the current document to file with optional filename.
mcp__ctxform__list_all_objects: List all objects in the active FreeCAD document.

### **View & Visualization**
mcp__ctxform__get_screenshot: Take a screenshot of the current FreeCAD view as base64 image.
mcp__ctxform__set_view: Set the 3D view orientation (top, front, left, right, isometric).
mcp__ctxform__fit_all: Fit all objects in the 3D view for optimal viewing.

### **Selection & Visibility**
mcp__ctxform__select_object: Select a specific object by name for operations.
mcp__ctxform__clear_selection: Clear all selected objects in the document.
mcp__ctxform__get_selection: Get currently selected objects and their details.
mcp__ctxform__hide_object: Hide an object from view while keeping it in document.
mcp__ctxform__show_object: Show a previously hidden object in the view.
mcp__ctxform__delete_object: Delete an object permanently from the document.

### **History & Workflow**
mcp__ctxform__undo: Undo the last operation performed in FreeCAD.
mcp__ctxform__redo: Redo the last undone operation in FreeCAD.

### **Advanced Features**
mcp__ctxform__execute_python: Execute arbitrary Python code in FreeCAD context for custom operations.
mcp__ctxform__run_command: Execute a FreeCAD GUI command by name for advanced control.
mcp__ctxform__activate_workbench: Activate a specific FreeCAD workbench (Part Design, Sketcher, etc.).

### **AI Assistant**
mcp__ctxform__ai_agent: Process requests through the FreeCAD ReAct Agent for natural language CAD operations.

## Project Structure

```
freecad-mcp/
├── AICopilot/                  # Complete FreeCAD workbench
│   ├── InitGui.py              # Auto-start global AI service
│   ├── socket_server.py        # 22+ tools + GUI automation
│   ├── event_observer.py       # User interaction learning
│   ├── memory_system.py        # Pattern recognition & memory
│   ├── freecad_agent.py        # ReAct agent for complex tasks
│   ├── commands/               # Management commands
│   └── Resources/icons/        # Workbench icons
├── working_bridge.py           # ContextForm MCP bridge server
├── .claude.json               # Claude Code MCP configuration
├── test_*.py                   # Testing utilities
└── README.md                   # This file
```

## Troubleshooting

### MCP Server Not Loading
```bash
# Check if server is registered
claude mcp list

# If not showing, re-add it
claude mcp remove ctxform
claude mcp add ctxform /opt/homebrew/bin/python3.11 /path/to/working_bridge.py

# Restart Claude Code
exit  # or Ctrl+C
claude
```

### FreeCAD Not Responding
1. Check that FreeCAD is running
2. Verify the AI Copilot workbench is installed
3. Look for startup messages in FreeCAD console:
   ```
   🤖 Starting FreeCAD AI Copilot Service...
   ✅ AI Socket Server started
   ```

### Tools Not Showing
```bash
# In Claude Code, check available tools
List available tools

# Should show tools like mcp__ctxform__box
# If not, check MCP server health
claude mcp list
```

## License

LGPL-2.1-or-later (compatible with FreeCAD)

---

**Built by ContextForm with ❤️ for the FreeCAD community**  
*Powered by Claude Code & Model Context Protocol*