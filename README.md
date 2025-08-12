# FreeCAD MCP - AI-Powered CAD

**Control FreeCAD with Claude AI through natural language!**

Create 3D models, add features, and automate CAD workflows using conversational AI.

> **🎉 New!** Easy 2-command installation with automatic updates!

## 📋 Requirements

**Before installation, make sure you have:**

- **FreeCAD 1.0+** - [Download here](https://freecad.org/downloads.php)
- **Node.js & npm** - [Download here](https://nodejs.org/)
- **Claude Code** - `npm install -g claude-code` (recommended)

*Python 3.9+ is included with FreeCAD automatically*

## ⚡ Super Easy Install

### 🚀 Two-Command Install
```bash
npm install -g freecad-mcp-setup
freecad-mcp setup
```

**Windows users:** If you get "command not recognized", try:
- Restart your command prompt, OR
- Use: `npx freecad-mcp-setup setup`

**That's it!** The installer automatically:
- ✅ **Cross-platform**: Works on macOS, Linux, and Windows
- ✅ Detects your OS and FreeCAD installation
- ✅ Downloads latest FreeCAD MCP from GitHub
- ✅ Installs the AI Copilot workbench to correct location
- ✅ Downloads and registers MCP bridge server  
- ✅ Provides clear next steps for testing

**To update later:** Just run `freecad-mcp setup` again!

### 📋 What You'll See:
```
🚀 FreeCAD MCP Setup

1️⃣ Checking FreeCAD installation...
✅ FreeCAD found

🔍 Checking for updates...
2️⃣ Installing FreeCAD MCP...
⬇️ Downloading FreeCAD MCP...
✅ FreeCAD workbench installed

3️⃣ Setting up Claude integration...
✅ MCP server registered with Claude Code

🎉 Installation complete!
```

### 🖥️ Using Claude Desktop?

The installer works with Claude Code by default. For Claude Desktop users, after running the installer, you'll need to manually configure:

**Add to your Claude Desktop config:**

*macOS/Linux:*
```json
{
  "mcpServers": {
    "freecad": {
      "command": "python3",
      "args": ["/Users/yourusername/.freecad-mcp/working_bridge.py"]
    }
  }
}
```

*Windows:*
```json
{
  "mcpServers": {
    "freecad": {
      "command": "python3",
      "args": ["C:\\Users\\yourusername\\.freecad-mcp\\working_bridge.py"]
    }
  }
}
```

*Config file locations:*
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

### 🔧 Manual Installation (Developers)

**For developers who prefer full control:**

```bash
# Clone the repository
git clone https://github.com/contextform/freecad-mcp.git
cd freecad-mcp

# Install dependencies
python3 -m pip install mcp

# Install FreeCAD workbench (choose your OS):
# macOS:
cp -r AICopilot ~/Library/Application\ Support/FreeCAD/Mod/

# Linux:
# cp -r AICopilot ~/.local/share/FreeCAD/Mod/

# Windows:
# cp -r AICopilot %APPDATA%\FreeCAD\Mod\

# Register MCP server with full path
claude mcp add freecad python3 "$(pwd)/working_bridge.py"
```

**Benefits of manual installation:**
- Full source code access for modification
- Easy development and testing
- Custom installation paths
- Direct git workflow for contributions

## 🚀 What You Can Do

**Create 3D Objects:**
```
Create a 50x30x20mm box with 5mm fillets
Make a cylinder with 25mm radius and 60mm height
```

**Parametric Features:**
```
Add a 3mm fillet to Pad001
Create a 6mm counterbore hole at position (20,10)
Make a linear pattern of 5 copies spaced 30mm apart
```

**Advanced Operations:**
```
Create a PartDesign pad from Sketch001 with 15mm length
Add a mirror of Feature001 across the XZ plane
Take an isometric screenshot at 1200x800
```

## 🛠️ Available Operations

- **PartDesign (13 ops)**: Pad, Revolution, Fillet, Chamfer, Holes, Patterns
- **Part (18 ops)**: Primitives, Booleans, Transforms, Advanced shapes
- **View Control (14 ops)**: Screenshots, Zoom, Selection, Document management
- **Python Execution**: Custom FreeCAD scripts for complex operations


## 🐛 Troubleshooting

**Installation Problems:**
```bash
# Re-run the installer (fixes most issues)
freecad-mcp setup

# Force update to latest version  
freecad-mcp setup --update

# Get help
freecad-mcp --help
```

**Common Issues:**

| Problem | Solution |
|---------|----------|
| **"FreeCAD not found"** | Install FreeCAD 1.0+ from [freecad.org](https://freecad.org/downloads.php) |
| **"Claude Code not found"** | Run `npm install -g claude-code` |
| **"npm command not found"** | Install Node.js from [nodejs.org](https://nodejs.org/) |
| **MCP registration failed** | Manual setup: `claude mcp add freecad python3 ~/.freecad-mcp/working_bridge.py` |

**Testing Connection:**
1. Launch FreeCAD first (AI service auto-starts)
2. Run `claude` in terminal
3. Ask Claude: **"List available tools"**  
4. Should see `mcp__freecad__*` tools listed ✅

## 📞 Support

- [Issues](https://github.com/contextform/freecad-mcp/issues)
- [Discussions](https://github.com/contextform/freecad-mcp/discussions)

---

**Ready to design with AI? Install and start creating!** 🚀