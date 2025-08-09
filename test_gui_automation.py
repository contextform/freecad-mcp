#!/usr/bin/env python3
"""Test GUI automation functionality"""

import socket
import json
import time

def test_gui_tool(tool_name, args={}):
    """Test a specific GUI tool"""
    socket_path = "/tmp/freecad_mcp.sock"
    
    try:
        # Connect to socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(socket_path)
        
        # Send command
        command = {"tool": tool_name, "args": args}
        print(f"→ Testing {tool_name}: {args}")
        sock.send(json.dumps(command).encode('utf-8'))
        
        # Receive response
        response = sock.recv(4096).decode('utf-8')
        result = json.loads(response)
        
        if result.get("success"):
            print(f"✅ {result.get('result')}")
        else:
            print(f"❌ Error: {result.get('error')}")
            
        sock.close()
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ Socket error: {e}")
        return False

def run_gui_tests():
    """Run comprehensive GUI automation tests"""
    print("🧪 Testing FreeCAD GUI Automation\n")
    
    # Test 1: View Control
    print("📷 Testing View Control:")
    test_gui_tool("set_view", {"view_type": "front"})
    time.sleep(1)
    test_gui_tool("set_view", {"view_type": "isometric"})
    test_gui_tool("fit_all")
    
    print("\n📋 Testing Object Selection:")
    # Create some objects first
    test_gui_tool("create_box", {"length": 30, "width": 20, "height": 10})
    test_gui_tool("create_cylinder", {"radius": 8, "height": 25, "x": 40})
    
    # Test selection
    test_gui_tool("select_object", {"object_name": "Box"})
    test_gui_tool("get_selection")
    test_gui_tool("clear_selection")
    test_gui_tool("get_selection")
    
    print("\n👁️ Testing Object Visibility:")
    test_gui_tool("hide_object", {"object_name": "Box"})
    test_gui_tool("show_object", {"object_name": "Box"})
    
    print("\n🔄 Testing Undo/Redo:")
    test_gui_tool("undo")
    test_gui_tool("redo")
    
    print("\n📁 Testing Document Operations:")
    test_gui_tool("new_document", {"name": "TestDoc"})
    test_gui_tool("save_document", {"filename": "/tmp/test_freecad.fcstd"})
    
    print("\n⚡ Testing FreeCAD Commands:")
    test_gui_tool("run_command", {"command": "Std_ViewFitAll"})
    test_gui_tool("run_command", {"command": "Std_ViewIsometric"})
    
    print("\n🗑️ Testing Object Deletion:")
    test_gui_tool("delete_object", {"object_name": "Cylinder"})
    
    print("\n✅ GUI Automation tests completed!")

if __name__ == "__main__":
    run_gui_tests()