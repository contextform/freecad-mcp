# FreeCAD AI Copilot with MCP Integration

An intelligent AI copilot for FreeCAD that runs embedded within FreeCAD, providing deep CAD automation through natural language via Claude Desktop.

## Features

- 🤖 **Natural Language CAD Control** - Create 3D objects with conversational commands
- 🔧 **Real-time Socket Communication** - Direct FreeCAD control through Unix sockets
- 📊 **Event Observation** - Learns from user interactions to improve assistance
- 💾 **Memory System** - Remembers patterns and preferences across sessions
- 🎯 **Deep FreeCAD Integration** - Runs embedded for complete API access

## Architecture

```
Claude Desktop (AI Interface)
      ↕️ MCP Protocol
Bridge Server (Python 3.11)
      ↕️ Unix Socket
FreeCAD Socket Server (Embedded)
      ↕️ Direct API
FreeCAD Core
```

### Why This Architecture?

- **Embedded Design**: Runs INSIDE FreeCAD for direct API access
- **Bridge Pattern**: Handles Python version differences (FreeCAD 3.9 vs MCP 3.11)
- **Socket Communication**: Fast, reliable IPC with minimal overhead
- **Modular**: Each component can be updated independently

## Prerequisites

- FreeCAD 1.0 or later
- Python 3.11+ (for MCP bridge)
- Claude Desktop app

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

### Step 3: Configure Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "freecad-ai-copilot": {
      "command": "/opt/homebrew/bin/python3.11",
      "args": ["/full/path/to/freecad-mcp/working_bridge.py"],
      "env": {}
    }
  }
}
```

### Step 4: Start Using!

1. **Start FreeCAD** - AI Copilot service auto-starts  
2. **Go to any workbench** (Part Design, Sketcher, etc.)
3. **Open Claude Desktop** - Should show "freecad-ai-copilot: running"
4. **Start creating**: *"Create a box that's 50x30x20mm"*

🎉 **That's it!** The AI Copilot works from any FreeCAD workbench!

## Usage

1. **Start FreeCAD**
2. **Switch to AI Copilot Workbench** (dropdown menu)
3. **Open Claude Desktop**
4. **Start creating!**

Example commands:
- "Create a box that's 50x30x20mm"
- "Create a cylinder with radius 15mm and height 40mm"
- "Take a screenshot of the current view"
- "List all objects in the document"
- "Create a sphere at position (10, 20, 0)"

## Project Structure

```
freecad-mcp/
├── AICopilot/                  # Complete FreeCAD workbench
│   ├── InitGui.py              # Auto-start global AI service
│   ├── socket_server.py        # 19 tools + GUI automation
│   ├── event_observer.py       # User interaction learning
│   ├── memory_system.py        # Pattern recognition & memory
│   ├── commands/               # Management commands
│   └── Resources/icons/        # Workbench icons
├── working_bridge.py           # MCP bridge (connects Claude Desktop)
├── test_*.py                   # Testing utilities
└── README.md                   # This file
```

## Key Components

### Auto-Start Service (`InitGui.py`)
Global AI service that starts with FreeCAD and works from any workbench.

### Socket Server (`socket_server.py`)
19 tools for 3D modeling, GUI control, screenshots, and Python execution.

### MCP Bridge (`working_bridge.py`)  
Connects Claude Desktop to FreeCAD via MCP protocol.

### Learning System (`event_observer.py` + `memory_system.py`)
Observes user interactions and learns patterns for intelligent assistance.

## Testing

```bash
# Test complete installation
python3 test_installation.py

# Test socket communication
python3 test_socket.py

# Test auto-start functionality
python3 test_auto_start.py

# Test GUI automation
python3 test_gui_automation.py
```

## Advantages Over Other Approaches

| Feature | This Project | External Scripts |
|---------|-------------|------------------|
| Runs inside FreeCAD | ✅ | ❌ |
| Direct API access | ✅ | ❌ |
| Event observation | ✅ | ❌ |
| No restarts needed | ✅ | ❌ |
| GUI automation | ✅ | Limited |
| Memory system | ✅ | ❌ |

## Contributing

Contributions welcome! Please submit pull requests or open issues.

## License

LGPL-2.1-or-later (compatible with FreeCAD)

## Acknowledgments

- FreeCAD community for the excellent CAD platform
- Anthropic for Claude and MCP protocol
- Inspired by neka-nat/freecad-mcp for serialization approaches

---

Built with ❤️ for the FreeCAD community