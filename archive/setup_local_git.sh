#!/bin/bash
# Setup local git backup in FreeCAD development directory

echo "🛡️  Setting up local git backup for rollback protection..."

# Navigate to FreeCAD AICopilot directory
FREECAD_DIR="$HOME/Library/Application Support/FreeCAD/Mod/AICopilot"

if [ ! -d "$FREECAD_DIR" ]; then
    echo "❌ FreeCAD AICopilot directory not found at: $FREECAD_DIR"
    echo "   Please check if the path is correct"
    exit 1
fi

echo "📁 Found FreeCAD directory: $FREECAD_DIR"
cd "$FREECAD_DIR"

# Check if git already initialized
if [ -d ".git" ]; then
    echo "✅ Git already initialized in this directory"
    echo "   Adding current state as backup commit..."
    git add -A
    git commit -m "Backup commit - $(date)"
else
    echo "🔧 Initializing local git repository..."
    git init
    
    echo "📝 Adding all current files..."
    git add -A
    
    echo "💾 Creating baseline commit..."
    git commit -m "Baseline working version - $(date)"
fi

echo ""
echo "✅ Local git backup setup complete!"
echo ""
echo "📅 Daily safety habit (run when you finish coding):"
echo "   cd '$FREECAD_DIR'"
echo "   git add -A && git commit -m \"\$(date +%Y-%m-%d) - working version\""
echo ""
echo "🔄 To rollback if needed:"
echo "   git log --oneline                  # See recent commits"
echo "   git checkout HEAD~1                # Go back 1 commit"
echo "   git checkout [commit-hash]         # Go to specific commit"
echo ""
echo "🎯 You now have rollback protection while keeping clean GitHub releases!"