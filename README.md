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

# Install Claude Code
npm install -g @anthropics/claude-code             # All platforms
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

| Tool | Description | Example |
|------|-------------|---------|
| `mcp__ctxform__check_freecad_connection` | Check FreeCAD connection | Basic connectivity test |
| `mcp__ctxform__box` | Create boxes | `length=30, width=20, height=15` |
| `mcp__ctxform__cylinder` | Create cylinders | `radius=8, height=25` |
| `mcp__ctxform__sphere` | Create spheres | `radius=10` |
| `mcp__ctxform__screenshot` | Take screenshots | `width=800, height=600` |
| `mcp__ctxform__list_objects` | List all objects | Returns object names and types |
| `mcp__ctxform__python` | Execute Python in FreeCAD | `code="App.newDocument()"` |
| `mcp__ctxform__ai` | Natural language agent | `request="Create motor mount"` |
| `mcp__ctxform__new_document` | Create new document | `name="Project1"` |
| `mcp__ctxform__save_document` | Save document | Auto or with filename |

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