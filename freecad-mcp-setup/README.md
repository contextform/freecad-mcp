# FreeCAD MCP Setup

Easy installer for [FreeCAD MCP](https://github.com/contextform/freecad-mcp) - Control FreeCAD with Claude AI through natural language.

## Quick Install

```bash
npm install -g freecad-mcp-setup
freecad-mcp setup
```

## Features

- ✅ **Cross-platform** - macOS, Linux, Windows support
- ✅ **Smart detection** - Finds FreeCAD installation automatically  
- ✅ **Update checking** - Prompts when new versions are available
- ✅ **Zero configuration** - Registers MCP server automatically
- ✅ **Error handling** - Clear error messages and recovery steps

## Commands

```bash
freecad-mcp setup          # Install or check for updates
freecad-mcp setup --update # Force update to latest version
freecad-mcp --help         # Show help information
```

## What It Does

1. **Checks** if FreeCAD 1.0+ is installed
2. **Downloads** latest FreeCAD MCP release from GitHub
3. **Installs** AI Copilot workbench to correct location
4. **Registers** MCP server with Claude Code
5. **Tests** the connection and provides next steps

## Requirements  

- **FreeCAD 1.0+** - [Download here](https://freecad.org/downloads.php)
- **Node.js 14+** - For running the installer
- **Claude Code** - `npm install -g claude-code`

## Manual Installation

If you prefer manual installation, see the [main repository](https://github.com/contextform/freecad-mcp).

## Troubleshooting

**FreeCAD not found:**
- Install FreeCAD 1.0+ from https://freecad.org/downloads.php

**Claude Code not found:** 
- Install with: `npm install -g claude-code`

**Permission errors:**
- Run with appropriate permissions for your OS
- On macOS/Linux: Check file permissions with `ls -la`

## License

LGPL-2.1-or-later (same as FreeCAD)