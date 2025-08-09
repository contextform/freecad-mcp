# FreeCAD AI Copilot - Embedded MCP Server

An intelligent CAD assistant that runs INSIDE FreeCAD with deep memory and learning capabilities.

## Architecture Difference

### Our Approach (Embedded)
```
[Claude] <-MCP-> [Server INSIDE FreeCAD] -> Direct Access to Everything
```

### Others' Approach (External)
```
[Claude] <-MCP-> [External Server] <-RPC-> [Limited FreeCAD Access]
```

## Key Advantages

1. **Complete Context Capture**
   - Every mouse movement
   - Failed selection attempts
   - Hover duration
   - Undo/redo patterns
   
2. **Direct Internal Access**
   - No RPC limitations
   - Access to undo stack
   - Real-time viewport state
   - Internal event stream
   
3. **Intelligent Memory**
   - Learns from failures
   - Detects patterns
   - Suggests next operations
   - Recalls similar designs

## Installation

1. Find your FreeCAD Mod directory:
   - Windows: `C:\\Users\\[username]\\AppData\\Roaming\\FreeCAD\\Mod\\`
   - macOS: `~/Library/Application Support/FreeCAD/Mod/`
   - Linux: `~/.FreeCAD/Mod/`

2. Copy this folder to Mod directory as `AICopilot`

3. Install Python dependencies:
```bash
pip install mcp sqlite3 numpy
```

4. Restart FreeCAD

5. Switch to "AI Copilot" workbench from the dropdown

## Usage

The MCP server starts automatically when you activate the workbench. It provides:

### Tools Available to Claude

- `get_full_context` - Complete design state including selection, viewport, history
- `create_parametric_object` - Create objects with full parametric control  
- `get_selection_details` - Detailed info about selected entities
- `recall_design` - Use memory to recreate previous designs
- `analyze_design_intent` - AI analysis of what you're building
- `get_failed_operations` - Learn from mistakes

### Memory Features

- Automatically learns your patterns
- Remembers successful workflows
- Tracks time spent on operations
- Suggests next steps based on history

## Testing with Claude

1. Start FreeCAD with AI Copilot workbench
2. In Claude Desktop, the MCP server should auto-connect
3. Try: "Show me what I'm currently working on"
4. Try: "Recreate the bracket I made yesterday"

## Development

To extend the system:

1. Add new tools in `mcp_server.py`
2. Capture more events in `event_observer.py`
3. Enhance memory in `memory_system.py`

## Why This Architecture?

External MCP servers (like neka-nat/freecad-mcp) can only see what FreeCAD exposes through RPC. They miss:

- User interaction patterns
- Failed attempts (learning opportunities)
- Timing information
- Context switches
- The "why" behind operations

Our embedded approach captures EVERYTHING, enabling true AI assistance.

## License

LGPL-2.1-or-later (compatible with FreeCAD)