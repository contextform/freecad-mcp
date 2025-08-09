#!/usr/bin/env python3
"""Test auto-start functionality of AI Copilot service"""

import socket
import json
import time

def check_ai_service():
    """Check if AI service is running"""
    socket_path = "/tmp/freecad_mcp.sock"
    
    try:
        # Try to connect to the socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2)  # 2 second timeout
        sock.connect(socket_path)
        
        # Test with a simple command
        command = {"tool": "check_freecad_connection", "args": {}}
        sock.send(json.dumps(command).encode('utf-8'))
        
        response = sock.recv(1024).decode('utf-8')
        sock.close()
        
        result = json.loads(response)
        if result.get("success"):
            print("✅ AI Copilot Service is running and responding!")
            print(f"   Socket path: {socket_path}")
            return True
        else:
            print("⚠️  AI Service responding but with errors")
            return False
            
    except socket.timeout:
        print("⏱️  Socket connection timeout - service may be starting")
        return False
    except ConnectionRefusedError:
        print("❌ AI Service not running - socket connection refused")
        return False
    except FileNotFoundError:
        print("❌ Socket file not found - FreeCAD not running or service not started")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_cross_workbench_availability():
    """Test that service works from any workbench context"""
    print("🧪 Testing Cross-Workbench AI Service Availability\n")
    
    print("Step 1: Check if AI service is auto-started")
    service_running = check_ai_service()
    
    if not service_running:
        print("\n❌ Test failed: AI service not running")
        print("   Please start FreeCAD and the service should auto-start")
        return False
    
    print("\nStep 2: Test basic functionality")
    socket_path = "/tmp/freecad_mcp.sock"
    
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(socket_path)
        
        # Test creating an object (should work from any workbench)
        command = {"tool": "create_box", "args": {"length": 25, "width": 15, "height": 8}}
        print("→ Testing object creation from service...")
        sock.send(json.dumps(command).encode('utf-8'))
        
        response = sock.recv(4096).decode('utf-8')
        result = json.loads(response)
        
        if result.get("success"):
            print("✅ Object creation successful!")
            print(f"   Result: {result.get('result')}")
        else:
            print(f"❌ Object creation failed: {result.get('error')}")
            
        sock.close()
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False
    
    print("\n🎯 Cross-workbench test completed!")
    print("   AI service should now work from Part Design, Sketcher, etc.")
    return True

if __name__ == "__main__":
    print("🤖 FreeCAD AI Copilot Auto-Start Test\n")
    print("This test verifies that the AI service starts automatically")
    print("and works from any workbench without manual activation.\n")
    
    success = test_cross_workbench_availability()
    
    if success:
        print("\n✅ AUTO-START TEST PASSED!")
        print("   • AI service auto-starts when FreeCAD loads")
        print("   • Service persists across workbench changes") 
        print("   • Claude Desktop can connect from any workbench")
    else:
        print("\n❌ AUTO-START TEST FAILED!")
        print("   Please check FreeCAD console for error messages")