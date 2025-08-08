#!/usr/bin/env python3
"""Test script to verify FreeCAD socket communication"""

import socket
import json
import sys

def test_freecad_socket():
    socket_path = "/tmp/freecad_mcp.sock"
    
    try:
        # Connect to socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(socket_path)
        print(f"✓ Connected to FreeCAD socket at {socket_path}")
        
        # Test create_box command
        command = {
            "tool": "create_box",
            "args": {
                "length": 50,
                "width": 30,
                "height": 20
            }
        }
        
        print(f"→ Sending command: {json.dumps(command)}")
        sock.send(json.dumps(command).encode('utf-8'))
        
        # Receive response
        response = sock.recv(4096).decode('utf-8')
        print(f"← Received response: {response}")
        
        # Parse response
        result = json.loads(response)
        if result.get("success"):
            print("✓ Box created successfully!")
            print(f"  Result: {result.get('result')}")
        else:
            print(f"✗ Error: {result.get('error')}")
        
        sock.close()
        
    except FileNotFoundError:
        print(f"✗ Socket not found at {socket_path}")
        print("  Make sure FreeCAD is running with AI Copilot workbench")
    except ConnectionRefusedError:
        print(f"✗ Connection refused to {socket_path}")
        print("  Socket exists but not accepting connections")
    except Exception as e:
        print(f"✗ Error: {e}")
        
if __name__ == "__main__":
    test_freecad_socket()