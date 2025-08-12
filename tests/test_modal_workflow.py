#!/usr/bin/env python3
"""
Test Modal Command Workflow
Tests the new direct FreeCAD command triggering system
"""

import json
import socket
import time

def send_mcp_command(tool_name, args):
    """Send command to FreeCAD via MCP bridge"""
    try:
        # Connect to MCP bridge socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/freecad_mcp.sock")
        
        # Send command
        command = json.dumps({"tool": tool_name, "args": args})
        sock.send(command.encode('utf-8'))
        
        # Receive response
        response = sock.recv(8192).decode('utf-8')
        sock.close()
        
        return response
        
    except Exception as e:
        return f"Error: {e}"

def test_modal_commands():
    """Test the new modal command workflow"""
    print("🧪 Testing Modal Command Workflow")
    print("=" * 50)
    
    # Test 1: Fillet command
    print("\n1️⃣  Testing Fillet Command")
    print("Command: Add 3mm fillet to Box")
    
    response = send_mcp_command("partdesign_operations", {
        "operation": "fillet",
        "object_name": "Box", 
        "radius": 3.0
    })
    
    print("Response:")
    print(response)
    
    # Test 2: Chamfer command  
    print("\n2️⃣  Testing Chamfer Command")
    print("Command: Add 2mm chamfer to Cylinder")
    
    response = send_mcp_command("partdesign_operations", {
        "operation": "chamfer",
        "object_name": "Cylinder",
        "distance": 2.0
    })
    
    print("Response:")
    print(response)
    
    # Test 3: Hole command
    print("\n3️⃣  Testing Hole Command")
    print("Command: Create 6mm hole, 10mm deep")
    
    response = send_mcp_command("partdesign_operations", {
        "operation": "hole",
        "diameter": 6.0,
        "depth": 10.0
    })
    
    print("Response:")
    print(response)
    
    # Test 4: Pad command
    print("\n4️⃣  Testing Pad Command") 
    print("Command: Pad Sketch with 15mm length")
    
    response = send_mcp_command("partdesign_operations", {
        "operation": "pad",
        "sketch_name": "Sketch",
        "length": 15.0
    })
    
    print("Response:")
    print(response)
    
    # Test 5: Python execution command
    print("\n5️⃣  Testing Python Execution")
    print("Command: Execute Python code to create sketch")
    
    response = send_mcp_command("execute_python", {
        "code": "print('Sketcher operations have been removed - use execute_python for custom sketch creation')"
    })
    
    print("Response:")
    print(response)
    
    # Test 6: View command
    print("\n6️⃣  Testing View Command")
    print("Command: Set isometric view")
    
    response = send_mcp_command("view_control", {
        "operation": "set_view",
        "view_type": "isometric" 
    })
    
    print("Response:")
    print(response)
    
    print("\n" + "=" * 50)
    print("✅ Modal Command Workflow Tests Complete!")
    print("\n🎯 Expected Results:")
    print("- Each command should open the corresponding FreeCAD tool/dialog")
    print("- User can then complete the operation in FreeCAD's native interface")
    print("- No complex back-and-forth between Claude Code and FreeCAD")
    print("- Professional CAD workflow: Command → Modal → Execute")

def test_connection():
    """Test basic connection to FreeCAD"""
    print("🔌 Testing FreeCAD Connection")
    
    response = send_mcp_command("check_freecad_connection", {})
    print("Connection Status:")
    print(response)
    
    return "FreeCAD running" in response

if __name__ == "__main__":
    print("🚀 FreeCAD Modal Workflow Test Suite")
    print("=" * 60)
    
    # Test connection first
    if test_connection():
        print("\n✅ FreeCAD connection established")
        
        # Ask user to create a basic setup
        print("\n📋 Test Setup Required:")
        print("1. Open FreeCAD")
        print("2. Create a new document")
        print("3. Add a Box (Part → Primitives → Box)")
        print("4. Add a Cylinder next to it")
        print("5. Create a sketch on XY plane")
        print("\nPress ENTER when ready to test...")
        input()
        
        # Run modal command tests
        test_modal_commands()
        
    else:
        print("\n❌ FreeCAD not connected")
        print("Please:")
        print("1. Start FreeCAD")
        print("2. Switch to AI Copilot workbench") 
        print("3. Run this test again")