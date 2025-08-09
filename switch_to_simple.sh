#!/bin/bash
# Switch to simple standard development workflow

echo "🔄 Switching to simple standard workflow..."

FREECAD_MOD="$HOME/Library/Application Support/FreeCAD/Mod"
CURRENT_WORKBENCH="$FREECAD_MOD/AICopilot"
REPO_WORKBENCH="$HOME/Documents/freecad-mcp/AICopilot"

# Step 1: Backup current FreeCAD workbench
if [ -d "$CURRENT_WORKBENCH" ]; then
    echo "📦 Backing up current FreeCAD workbench..."
    mv "$CURRENT_WORKBENCH" "${CURRENT_WORKBENCH}_backup_$(date +%Y%m%d)"
    echo "   Backed up to: ${CURRENT_WORKBENCH}_backup_$(date +%Y%m%d)"
fi

# Step 2: Create symlink from FreeCAD to repo
echo "🔗 Creating symlink from FreeCAD to GitHub repo..."
ln -s "$REPO_WORKBENCH" "$CURRENT_WORKBENCH"

if [ -L "$CURRENT_WORKBENCH" ]; then
    echo "✅ Symlink created successfully!"
    echo "   FreeCAD will now use: $REPO_WORKBENCH"
else
    echo "❌ Failed to create symlink"
    exit 1
fi

# Step 3: Test the symlink
if [ -f "$CURRENT_WORKBENCH/InitGui.py" ]; then
    echo "✅ Symlink working - FreeCAD can find the workbench"
else
    echo "❌ Symlink not working properly"
    exit 1
fi

echo ""
echo "🎉 Simple workflow setup complete!"
echo ""
echo "📝 Your new workflow:"
echo "   1. Edit files in: $REPO_WORKBENCH"
echo "   2. Test immediately in FreeCAD (via symlink)"
echo "   3. Commit regularly: git add -A && git commit -m 'message'"
echo "   4. Push when ready: git push origin main"
echo ""
echo "✅ Standard, simple, normal development workflow!"
echo ""
echo "🧹 To clean up:"
echo "   You can delete the local git repo we created earlier:"
echo "   rm -rf '${CURRENT_WORKBENCH}_backup_$(date +%Y%m%d)/.git'"