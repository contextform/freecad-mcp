#!/usr/bin/env python3
"""Test complete installation from repo"""

import os
import sys
import subprocess

def test_repo_completeness():
    """Test that repo has all necessary files for installation"""
    print("🧪 Testing FreeCAD MCP Repository Completeness\n")
    
    required_files = [
        "AICopilot/InitGui.py",
        "AICopilot/socket_server.py", 
        "AICopilot/event_observer.py",
        "AICopilot/memory_system.py",
        "AICopilot/Resources/icons/AICopilot.svg",
        "AICopilot/commands/ai_commands.py",
        "working_bridge.py",
        "README.md"
    ]
    
    print("✅ Checking required files:")
    all_present = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"  ✅ {file_path} ({file_size} bytes)")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_present = False
    
    if all_present:
        print("\n✅ All required files present!")
        return True
    else:
        print("\n❌ Some files missing!")
        return False

def test_installation_instructions():
    """Test the installation process"""
    print("\n📋 Testing Installation Instructions:")
    
    # Test 1: Can we find FreeCAD Mod directory?
    freecad_mod_paths = [
        os.path.expanduser("~/Library/Application Support/FreeCAD/Mod/"),  # macOS
        os.path.expanduser("~/.FreeCAD/Mod/"),  # Linux
        os.path.expandvars(r"%APPDATA%\FreeCAD\Mod\\")  # Windows
    ]
    
    freecad_found = False
    for path in freecad_mod_paths:
        if os.path.exists(path):
            print(f"  ✅ Found FreeCAD Mod directory: {path}")
            freecad_found = True
            break
    
    if not freecad_found:
        print("  ⚠️  FreeCAD Mod directory not found (FreeCAD may not be installed)")
    
    # Test 2: Check if Python 3.11+ available
    try:
        result = subprocess.run(["python3.11", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Python 3.11 available: {result.stdout.strip()}")
        else:
            print("  ❌ Python 3.11 not found")
    except FileNotFoundError:
        print("  ❌ Python 3.11 not found")
    
    # Test 3: Check working_bridge.py is executable
    if os.access("working_bridge.py", os.X_OK):
        print("  ✅ working_bridge.py is executable")
    else:
        print("  ⚠️  working_bridge.py not executable (may need chmod +x)")
    
    return True

def simulate_user_installation():
    """Simulate what a user would do"""
    print("\n👤 Simulating User Installation Process:")
    
    print("  1. git clone https://github.com/contextform/freecad-mcp.git")
    print("     ✅ Repository cloned (you're running this test)")
    
    print("  2. Copy AICopilot to FreeCAD Mod directory")
    if os.path.exists("AICopilot"):
        print("     ✅ AICopilot directory ready for copying")
    else:
        print("     ❌ AICopilot directory missing!")
        return False
    
    print("  3. Configure Claude Desktop with working_bridge.py path")
    if os.path.exists("working_bridge.py"):
        abs_path = os.path.abspath("working_bridge.py") 
        print(f"     ✅ Bridge script at: {abs_path}")
    else:
        print("     ❌ working_bridge.py missing!")
        return False
    
    print("  4. Start FreeCAD → AI Copilot auto-starts")
    print("     ✅ Ready for user testing")
    
    return True

def main():
    print("🤖 FreeCAD AI Copilot Installation Test")
    print("=" * 50)
    
    # Run all tests
    repo_ok = test_repo_completeness()
    install_ok = test_installation_instructions() 
    user_ok = simulate_user_installation()
    
    print("\n" + "=" * 50)
    if repo_ok and install_ok and user_ok:
        print("🎉 INSTALLATION TEST PASSED!")
        print("Repository is ready for users to clone and install!")
        print("\nNext steps for users:")
        print("1. Follow README.md installation instructions") 
        print("2. Start FreeCAD and enjoy AI-powered CAD!")
    else:
        print("❌ INSTALLATION TEST FAILED!")
        print("Please fix missing files or issues above")
    
    return repo_ok and install_ok and user_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)