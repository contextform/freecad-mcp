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

## Installation

### Step 1: Install Python 3.11

```bash
# macOS
brew install python@3.11

# Ubuntu/Debian  
sudo apt install python3.11 python3.11-venv

# Windows
# Download from python.org
```

### Step 2: Install MCP Dependencies

```bash
cd FreeCAD_MCP
/opt/homebrew/bin/python3.11 -m pip install mcp
```

### Step 3: Install FreeCAD Workbench

```bash
# Copy workbench to FreeCAD Mod directory
cp -r AICopilot ~/Library/Application\ Support/FreeCAD/Mod/  # macOS
# or
cp -r AICopilot ~/.FreeCAD/Mod/  # Linux
# or  
cp -r AICopilot %APPDATA%\FreeCAD\Mod\  # Windows
```

### Step 4: Configure Claude Desktop

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "freecad-ai-copilot": {
      "command": "/opt/homebrew/bin/python3.11",
      "args": ["/path/to/FreeCAD_MCP/working_bridge.py"],
      "env": {}
    }
  }
}
```

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
FreeCAD_MCP/
├── working_bridge.py           # MCP bridge server (Python 3.11)
├── mcp_server_enhanced.py      # Enhanced MCP implementation
├── test_socket.py              # Testing utility
└── AICopilot/                  # FreeCAD workbench
    ├── InitGui.py              # Workbench initialization
    ├── socket_server.py        # Embedded socket server
    ├── event_observer.py       # User interaction tracking
    ├── memory_system.py        # Learning and memory
    └── commands/               # FreeCAD commands
```

## Key Components

### Socket Server (`socket_server.py`)
Runs inside FreeCAD, receives commands via Unix socket, executes FreeCAD operations directly.

### MCP Bridge (`working_bridge.py`)  
Translates between MCP protocol and socket commands, handles tool registration with Claude.

### Event Observer (`event_observer.py`)
Tracks user interactions, failed attempts, and patterns for intelligent assistance.

### Memory System (`memory_system.py`)
Stores patterns, preferences, and successful operations for continuous learning.

## Testing

```bash
# Test socket connection
python3 test_socket.py

# Test screenshot
python3 test_screenshot.py
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