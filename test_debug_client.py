#!/usr/bin/env python3
# Debug client to test FreeCAD crash issues

import socket
import json
import time

def send_debug_command(tool, args=None):
    """Send command to debug server"""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/freecad_mcp_debug.sock")
        
        command = {"tool": tool, "args": args or {}}
        sock.send(json.dumps(command).encode())
        
        response = sock.recv(4096).decode()
        sock.close()
        
        return response
        
    except Exception as e:
        return f"Client error: {e}"

def main():
    """Run debug tests"""
    print("=== FreeCAD Debug Test Client ===")
    
    # Test 1: Basic connectivity
    print("\n1. Testing basic connectivity...")
    response = send_debug_command("test_echo", {"message": "hello debug"})
    print(f"Response: {response}")
    
    # Test 2: Check FreeCAD state
    print("\n2. Checking FreeCAD state...")
    response = send_debug_command("check_state")
    print(f"State: {response}")
    
    # Test 3: Simple Python execution
    print("\n3. Testing simple Python...")
    response = send_debug_command("execute_python", {
        "code": "print('Simple test')"
    })
    print(f"Response: {response}")
    
    # Test 4: FreeCAD version access
    print("\n4. Testing FreeCAD version access...")
    response = send_debug_command("execute_python", {
        "code": "import FreeCAD; print(f'Version: {FreeCAD.Version()}')"
    })
    print(f"Response: {response}")
    
    # Test 5: Document listing
    print("\n5. Testing document listing...")
    response = send_debug_command("execute_python", {
        "code": "import FreeCAD; print(f'Docs: {list(FreeCAD.listDocuments().keys())}')"
    })
    print(f"Response: {response}")
    
    # Test 6: The problematic document creation
    print("\n6. Testing document creation (THIS MIGHT CRASH)...")
    print("   Sending command...")
    response = send_debug_command("execute_python", {
        "code": "import FreeCAD; print('Creating doc...'); doc = FreeCAD.newDocument('DebugTest'); print(f'Created: {doc.Name}')"
    })
    print(f"Response: {response}")

if __name__ == "__main__":
    main()