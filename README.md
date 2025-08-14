# FreeCAD MCP

**FreeCAD MCP** is an open-source Model Context Protocol (MCP) server that enables AI assistants to interact with FreeCAD for automated CAD workflows.

## What is FreeCAD MCP?

FreeCAD MCP provides a standardized interface for AI models like Claude, ChatGPT, and other LLMs to directly control and automate FreeCAD operations. By implementing the Model Context Protocol, FreeCAD MCP bridges the gap between natural language AI assistants and professional CAD automation.

## Key Features

- **Full FreeCAD API Access** - Complete programmatic control over FreeCAD's Python API
- **Sketch Creation** - Automated 2D sketch generation with geometric constraints
- **3D Operations** - Support for extrude, revolve, loft, sweep, and other 3D operations
- **Parametric Design** - Modify parameters and see real-time updates in your models
- **File Management** - Open, save, and export in multiple CAD formats (STEP, IGES, STL, etc.)
- **Assembly Tools** - Create and manage complex assemblies with constraints

## Quick Start

```bash
# Clone the FreeCAD MCP repository
git clone https://github.com/contextform/freecad-mcp.git

# Navigate to the project directory
cd freecad-mcp

# Install dependencies
npm install

# Start the MCP server
npm start
```

## Prerequisites

- FreeCAD 0.21 or higher installed
- Node.js 18+ and npm
- Python 3.8+ (for FreeCAD Python API)

## Installation

### Option 1: NPM (Recommended)

```bash
npm install -g freecad-mcp
freecad-mcp start
```

### Option 2: From Source

```bash
git clone https://github.com/contextform/freecad-mcp.git
cd freecad-mcp
npm install
npm run build
npm start
```

## Configuration

Create a `config.json` file in your project root:

```json
{
  "freecad": {
    "path": "/usr/bin/freecad",
    "pythonPath": "/usr/bin/python3"
  },
  "server": {
    "port": 3000,
    "host": "localhost"
  }
}
```

## Usage Examples

### Creating a Simple Box

Send this to your AI assistant connected via FreeCAD MCP:

```
Create a box with dimensions 100x50x25mm
```

### Parametric Design

```
Create a parametric cylinder with:
- Radius parameter: 20mm
- Height parameter: 50mm
- Make both parameters editable
```

### Complex Operations

```
1. Create a sketch on the XY plane
2. Draw a circle with radius 30mm
3. Extrude the sketch 40mm
4. Add a fillet of 5mm to the top edge
```

## API Documentation

FreeCAD MCP exposes the following MCP tools:

### Core Tools

- `create_document` - Create a new FreeCAD document
- `open_document` - Open an existing FreeCAD file
- `save_document` - Save the current document
- `export_document` - Export to various CAD formats

### Sketch Tools

- `create_sketch` - Create a new sketch on a plane
- `add_line` - Add a line to the active sketch
- `add_circle` - Add a circle to the active sketch
- `add_constraint` - Add geometric constraints

### 3D Operations

- `extrude` - Extrude a sketch or face
- `revolve` - Revolve a sketch around an axis
- `loft` - Create a loft between profiles
- `fillet` - Add fillets to edges
- `chamfer` - Add chamfers to edges

### Parameter Management

- `add_parameter` - Create a named parameter
- `update_parameter` - Modify parameter value
- `list_parameters` - Get all parameters

## Use Cases

### 1. AI-Assisted Design
Let AI help you create complex geometries by describing what you need in natural language.

### 2. Batch Processing
Automate repetitive CAD tasks across multiple files.

### 3. Design Optimization
Use AI to explore and optimize design parameters.

### 4. Documentation Generation
Automatically generate technical drawings and documentation.

### 5. Quality Assurance
Implement automated design validation and testing.

## Integration with AI Assistants

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "freecad-mcp": {
      "command": "npx",
      "args": ["freecad-mcp", "start"]
    }
  }
}
```

### Custom Integration

```javascript
import { MCPClient } from '@anthropic/mcp';
import { FreeCADMCP } from 'freecad-mcp';

const client = new MCPClient();
const freecadServer = new FreeCADMCP();

await client.connect(freecadServer);
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repo
git clone https://github.com/contextform/freecad-mcp.git
cd freecad-mcp

# Install dependencies
npm install

# Run tests
npm test

# Start development server
npm run dev
```

## License

FreeCAD MCP is released under the MIT License. See [LICENSE](LICENSE) for details.

## Support

- **Documentation**: [https://contextform.dev/freecad-mcp/](https://contextform.dev/freecad-mcp/)
- **Issues**: [GitHub Issues](https://github.com/contextform/freecad-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/contextform/freecad-mcp/discussions)

## Acknowledgments

FreeCAD MCP is built on top of the excellent [FreeCAD](https://www.freecadweb.org/) open-source CAD platform and implements the [Model Context Protocol](https://github.com/anthropics/mcp) specification.

## About ContextForm

FreeCAD MCP is developed by [ContextForm](https://contextform.dev), specializing in AI-powered CAD automation tools.

---

**Keywords**: FreeCAD MCP, FreeCAD automation, Model Context Protocol, CAD automation, FreeCAD API, FreeCAD tools, AI CAD, parametric design, 3D modeling automation