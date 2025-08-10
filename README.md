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

| Tool | Description | Example Parameters |
|------|-------------|-------------------|
| `mcp__ctxform__check_freecad_connection` | Check FreeCAD connection | Basic connectivity test |
| `mcp__ctxform__test_echo` | Test echo message | `message="hello"` |
| **Shape Creation** | | |
| `mcp__ctxform__create_box` | Create boxes | `length=30, width=20, height=15` |
| `mcp__ctxform__create_cylinder` | Create cylinders | `radius=8, height=25` |
| `mcp__ctxform__create_sphere` | Create spheres | `radius=10` |
| `mcp__ctxform__create_cone` | Create cones | `radius1=5, radius2=0, height=10` |
| `mcp__ctxform__create_torus` | Create torus (donut) | `radius1=10, radius2=3` |
| `mcp__ctxform__create_wedge` | Create wedges | `xmax=10, ymax=10, zmax=10` |
| **Boolean Operations** | | |
| `mcp__ctxform__fuse_objects` | Union objects | `objects=["Box", "Cylinder"]` |
| `mcp__ctxform__cut_objects` | Subtract objects | `base="Box", tools=["Cylinder"]` |
| `mcp__ctxform__common_objects` | Intersect objects | `objects=["Box", "Sphere"]` |
| **Transformations** | | |
| `mcp__ctxform__move_object` | Move objects | `object_name="Box", x=10, y=5` |
| `mcp__ctxform__rotate_object` | Rotate objects | `object_name="Box", axis="z", angle=90` |
| `mcp__ctxform__copy_object` | Copy objects | `object_name="Box", x=20` |
| `mcp__ctxform__array_object` | Create arrays | `object_name="Box", count=5, spacing_x=15` |
| **Part Design** | | |
| `mcp__ctxform__create_sketch` | Create sketches | `plane="XY", name="Sketch001"` |
| `mcp__ctxform__pad_sketch` | Extrude sketches | `sketch_name="Sketch", length=10` |
| `mcp__ctxform__pocket_sketch` | Cut from sketches | `sketch_name="Sketch", length=5` |
| `mcp__ctxform__fillet_edges` | Round edges | `object_name="Box", radius=2` |
| **Analysis** | | |
| `mcp__ctxform__measure_distance` | Measure distance | `object1="Box", object2="Cylinder"` |
| `mcp__ctxform__get_volume` | Calculate volume | `object_name="Box"` |
| `mcp__ctxform__get_bounding_box` | Get dimensions | `object_name="Box"` |
| `mcp__ctxform__get_mass_properties` | Mass properties | `object_name="Box"` |
| **Document** | | |
| `mcp__ctxform__new_document` | Create document | `name="Project1"` |
| `mcp__ctxform__save_document` | Save document | Auto or with filename |
| `mcp__ctxform__list_all_objects` | List all objects | Returns object names and types |
| **View** | | |
| `mcp__ctxform__get_screenshot` | Take screenshots | `width=800, height=600` |
| `mcp__ctxform__set_view` | Set view angle | `view_type="isometric"` |
| `mcp__ctxform__fit_all` | Fit view | Auto-fit all objects |
| **Selection** | | |
| `mcp__ctxform__select_object` | Select objects | `object_name="Box"` |
| `mcp__ctxform__clear_selection` | Clear selection | No parameters |
| `mcp__ctxform__get_selection` | Get selected | Returns selected objects |
| `mcp__ctxform__hide_object` | Hide objects | `object_name="Box"` |
| `mcp__ctxform__show_object` | Show objects | `object_name="Box"` |
| `mcp__ctxform__delete_object` | Delete objects | `object_name="Box"` |
| **History** | | |
| `mcp__ctxform__undo` | Undo operation | No parameters |
| `mcp__ctxform__redo` | Redo operation | No parameters |
| **Advanced** | | |
| `mcp__ctxform__execute_python` | Run Python code | `code="print('Hello')"` |
| `mcp__ctxform__run_command` | GUI commands | `command="Std_ViewFitAll"` |
| `mcp__ctxform__activate_workbench` | Switch workbench | `workbench_name="PartDesignWorkbench"` |
| **AI** | | |
| `mcp__ctxform__ai_agent` | Natural language | `request="Create motor mount"` |

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