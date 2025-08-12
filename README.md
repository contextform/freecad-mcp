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

In Claude Code, you can use these FreeCAD smart dispatcher tools:

```bash
# Check connection
Use the mcp__freecad__check_freecad_connection tool

# Create 3D objects using Part operations
Use the mcp__freecad__part_operations tool with operation="box", length=50, width=30, height=20
Use the mcp__freecad__part_operations tool with operation="cylinder", radius=15, height=40
Use the mcp__freecad__part_operations tool with operation="sphere", radius=10

# Document management using View control
Use the mcp__freecad__view_control tool with operation="list_objects"
Use the mcp__freecad__view_control tool with operation="new_document", document_name="MyProject"
Use the mcp__freecad__view_control tool with operation="save_document"

# Advanced features
Use the mcp__freecad__view_control tool with operation="screenshot", width=800, height=600
Use the mcp__freecad__execute_python tool with code="print('Hello FreeCAD!')"

# Create parametric features using PartDesign operations
Use the mcp__freecad__partdesign_operations tool with operation="pad", sketch_name="Sketch", length=10
Use the mcp__freecad__partdesign_operations tool with operation="fillet", object_name="Box", radius=2
```

### Example Workflow

```bash
# Start Claude Code in your project
cd freecad-mcp
claude

# Create base objects
Use the mcp__freecad__part_operations tool with operation="box", length=100, width=50, height=25
Use the mcp__freecad__part_operations tool with operation="cylinder", radius=8, height=30, x=50

# Add parametric features  
Use the mcp__freecad__partdesign_operations tool with operation="fillet", object_name="Box", radius=3

# Take a screenshot
Use the mcp__freecad__view_control tool with operation="screenshot", width=800, height=600

# Create 2D sketch for advanced features
Use the mcp__freecad__execute_python tool to create sketches programmatically
Use the mcp__freecad__partdesign_operations tool with operation="pad", sketch_name="Sketch", length=15
```

## Available Tools - Phase 1 Smart Dispatchers

**🚀 New Architecture:** 5 intelligent dispatchers replace 60+ individual tools, aligned with FreeCAD workbenches for optimal Claude Code integration.

| Smart Dispatcher | Handles | Operations Count | Example Usage |
|------------------|---------|------------------|---------------|
| **`mcp__freecad__partdesign_operations`** | All parametric features | 20+ operations | `operation="pad", sketch_name="Sketch", length=10` |
| **`mcp__freecad__part_operations`** | All basic solids & booleans | 18+ operations | `operation="box", length=50, width=30, height=20` |
| **`mcp__freecad__view_control`** | View, document & selection | 15+ operations | `operation="screenshot", width=800, height=600` |
| **`mcp__freecad__execute_python`** | Power user Python execution | Direct code | `code="print('Hello FreeCAD!')"` |

### Core Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `mcp__freecad__check_freecad_connection` | Check FreeCAD connection status | None |
| `mcp__freecad__test_echo` | Test MCP bridge communication | `message="hello"` |


### PartDesign Operations (20+ operations)

All parametric feature operations through `mcp__freecad__partdesign_operations`:

| Operation | Description | Key Parameters |
|-----------|-------------|----------------|
| `pad` | Extrude sketch | `sketch_name="Sketch", length=10` |
| `pocket` | Cut from solid | `sketch_name="Sketch", length=5` |
| `revolution` | Revolve sketch | `sketch_name="Sketch", angle=360, axis="z"` |
| `loft` | Loft between profiles | `sketches=["Sketch1", "Sketch2"]` |
| `sweep` | Sweep along path | `profile_sketch="Profile", path_sketch="Path"` |
| `fillet` | Round edges | `object_name="Box", radius=2` (interactive) |
| `chamfer` | Chamfer edges | `object_name="Box", distance=1` (interactive) |
| `draft` | Add draft angle | `object_name="Box", angle=5` |
| `linear_pattern` | Linear pattern | `feature_name="Pad", count=3, spacing=10` |
| `polar_pattern` | Circular pattern | `feature_name="Pad", count=6, angle=360` |
| `mirror` | Mirror feature | `feature_name="Pad", plane="YZ"` |
| `hole` | Simple hole | `diameter=6, depth=10, x=0, y=0` |
| `counterbore` | Counterbore hole | `diameter=6, cb_diameter=12, cb_depth=3` |
| `countersink` | Countersink hole | `diameter=6, angle=90, depth=10` |

### Part Operations (18+ operations)

All basic solid and boolean operations through `mcp__freecad__part_operations`:

| Operation | Description | Key Parameters |
|-----------|-------------|----------------|
| `box` | Create box | `length=10, width=10, height=10, x=0, y=0, z=0` |
| `cylinder` | Create cylinder | `radius=5, height=10, x=0, y=0, z=0` |
| `sphere` | Create sphere | `radius=5, x=0, y=0, z=0` |
| `cone` | Create cone | `radius1=5, radius2=0, height=10` |
| `torus` | Create torus | `radius1=10, radius2=3` |
| `wedge` | Create wedge | Various dimensions |
| `fuse` | Union objects | `objects=["Box", "Cylinder"]` |
| `cut` | Subtract objects | `base="Box", tools=["Cylinder"]` |
| `common` | Intersect objects | `objects=["Box", "Sphere"]` |
| `move` | Move object | `object_name="Box", x=10, y=5, z=0` |
| `rotate` | Rotate object | `object_name="Box", axis="z", angle=90` |
| `scale` | Scale object | `object_name="Box", scale_factor=1.5` |
| `mirror` | Mirror object | `object_name="Box", plane="YZ"` |

### View Control Operations (15+ operations)

All view, document and selection operations through `mcp__freecad__view_control`:

| Operation | Description | Key Parameters |
|-----------|-------------|----------------|
| `screenshot` | Take screenshot | `width=800, height=600` |
| `set_view` | Set view angle | `view_type="isometric"` |
| `fit_all` | Fit all objects | None |
| `new_document` | Create document | `document_name="Project1"` |
| `save_document` | Save document | `filename="path/to/file.fcstd"` |
| `list_objects` | List all objects | None |
| `select_object` | Select object | `object_name="Box"` |
| `clear_selection` | Clear selection | None |
| `hide_object` | Hide object | `object_name="Box"` |
| `show_object` | Show object | `object_name="Box"` |
| `delete_object` | Delete object | `object_name="Box"` |
| `undo` | Undo operation | None |
| `redo` | Redo operation | None |
| `activate_workbench` | Switch workbench | `workbench_name="PartDesignWorkbench"` |

### Power User Tool

| Tool | Description | Parameters |
|------|-------------|------------|
| **`mcp__freecad__execute_python`** | Execute Python in FreeCAD | `code="App.ActiveDocument.addObject('Part::Box')"` |

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