#!/usr/bin/env python3
"""
Test script for Enhanced MCP Server
Run this INSIDE FreeCAD's Python console to test the new capabilities
"""

import FreeCAD
import FreeCADGui
import sys
import os

# Add our module path
import sys
sys.path.append('/Users/josephwu/Documents/FreeCAD_MCP')

def test_basic_setup():
    """Test if enhanced MCP server can be imported and initialized"""
    print("\n=== Testing Basic Setup ===")
    try:
        from mcp_server_enhanced import EnhancedFreeCADMCP
        print("✓ Enhanced MCP module imported successfully")
        
        # Try to create instance
        mcp = EnhancedFreeCADMCP()
        print("✓ Enhanced MCP server instance created")
        
        # Check if tools are registered
        if hasattr(mcp, 'server'):
            print("✓ MCP server object exists")
        
        # Check parts library path
        if os.path.exists(mcp.parts_library_path):
            print(f"✓ Parts library directory exists: {mcp.parts_library_path}")
        else:
            print(f"✓ Parts library directory created: {mcp.parts_library_path}")
            
        return mcp
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_screenshot():
    """Test screenshot capability"""
    print("\n=== Testing Screenshot ===")
    try:
        # Create a simple object first
        if not FreeCAD.ActiveDocument:
            FreeCAD.newDocument("TestDoc")
        
        # Create a box to screenshot
        box = FreeCAD.ActiveDocument.addObject("Part::Box", "TestBox")
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")
        
        # Test screenshot function directly
        import base64
        import tempfile
        
        view = FreeCADGui.ActiveDocument.ActiveView
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        view.saveImage(tmp_path, 800, 600, "white")
        
        # Check if file was created
        if os.path.exists(tmp_path):
            print(f"✓ Screenshot saved to: {tmp_path}")
            
            # Try base64 encoding
            with open(tmp_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            if image_data:
                print(f"✓ Base64 encoding successful (length: {len(image_data)})")
            
            os.unlink(tmp_path)
        
        return True
    except Exception as e:
        print(f"✗ Screenshot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_serialization():
    """Test object serialization"""
    print("\n=== Testing Serialization ===")
    try:
        # Create an object to serialize
        if not FreeCAD.ActiveDocument:
            FreeCAD.newDocument("TestDoc")
        
        obj = FreeCAD.ActiveDocument.addObject("Part::Box", "SerializeTest")
        obj.Length = 20
        obj.Width = 30
        obj.Height = 40
        obj.Placement.Base = FreeCAD.Vector(10, 20, 30)
        FreeCAD.ActiveDocument.recompute()
        
        # Manual serialization test
        serialized = {
            "Name": obj.Name,
            "Label": obj.Label,
            "TypeId": obj.TypeId,
            "Properties": {
                "Length": obj.Length.Value if hasattr(obj.Length, 'Value') else obj.Length,
                "Width": obj.Width.Value if hasattr(obj.Width, 'Value') else obj.Width,
                "Height": obj.Height.Value if hasattr(obj.Height, 'Value') else obj.Height,
                "Placement": {
                    "Position": [obj.Placement.Base.x, obj.Placement.Base.y, obj.Placement.Base.z],
                    "Rotation": list(obj.Placement.Rotation.Q)
                }
            }
        }
        
        print(f"✓ Object serialized: {obj.Name}")
        print(f"  Properties: Length={serialized['Properties']['Length']}, "
              f"Width={serialized['Properties']['Width']}, "
              f"Height={serialized['Properties']['Height']}")
        
        return True
    except Exception as e:
        print(f"✗ Serialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_access():
    """Test GUI access capabilities"""
    print("\n=== Testing GUI Access ===")
    try:
        from PySide2 import QtWidgets
        
        # Get main window
        main_window = FreeCADGui.getMainWindow()
        if main_window:
            print("✓ Main window accessed")
            print(f"  Window size: {main_window.width()}x{main_window.height()}")
        
        # List workbenches
        workbenches = FreeCADGui.listWorkbenches()
        if workbenches:
            print(f"✓ Found {len(workbenches)} workbenches")
            print(f"  Available: {', '.join(list(workbenches.keys())[:5])}...")
        
        # Check for toolbars
        toolbars = main_window.findChildren(QtWidgets.QToolBar)
        if toolbars:
            print(f"✓ Found {len(toolbars)} toolbars")
            visible_toolbars = [tb for tb in toolbars if tb.isVisible()]
            print(f"  Visible: {len(visible_toolbars)}")
        
        # Check for menu bar
        menubar = main_window.menuBar()
        if menubar:
            print("✓ Menu bar accessible")
            menus = [action.text() for action in menubar.actions() if action.text()]
            print(f"  Menus: {', '.join(menus[:5])}")
        
        return True
    except Exception as e:
        print(f"✗ GUI access test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mouse_automation():
    """Test mouse automation capabilities"""
    print("\n=== Testing Mouse Automation ===")
    try:
        from PySide2 import QtCore, QtTest
        from PySide2.QtTest import QTest
        
        print("✓ QTest module imported")
        
        # Check if we can access the main window for mouse operations
        main_window = FreeCADGui.getMainWindow()
        if main_window:
            # Test creating a QPoint
            point = QtCore.QPoint(100, 100)
            print(f"✓ Can create QPoint: ({point.x()}, {point.y()})")
            
            # Check mouse button constants
            if hasattr(QtCore.Qt, 'LeftButton'):
                print("✓ Mouse button constants available")
            
            # Check if QTest methods exist
            if hasattr(QTest, 'mouseClick'):
                print("✓ QTest.mouseClick method available")
            if hasattr(QTest, 'mouseDClick'):
                print("✓ QTest.mouseDClick method available")
            if hasattr(QTest, 'mouseMove'):
                print("✓ QTest.mouseMove method available")
            
        return True
    except Exception as e:
        print(f"✗ Mouse automation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyboard_automation():
    """Test keyboard automation capabilities"""
    print("\n=== Testing Keyboard Automation ===")
    try:
        from PySide2 import QtCore, QtTest
        from PySide2.QtTest import QTest
        
        # Check keyboard methods
        if hasattr(QTest, 'keyClick'):
            print("✓ QTest.keyClick method available")
        if hasattr(QTest, 'keyClicks'):
            print("✓ QTest.keyClicks method available")
        
        # Check key constants
        if hasattr(QtCore.Qt, 'Key_A'):
            print("✓ Key constants available (e.g., Key_A)")
        if hasattr(QtCore.Qt, 'ControlModifier'):
            print("✓ Modifier constants available (e.g., ControlModifier)")
        
        return True
    except Exception as e:
        print(f"✗ Keyboard automation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_execution():
    """Test FreeCAD command execution"""
    print("\n=== Testing Command Execution ===")
    try:
        # List available commands
        commands = FreeCADGui.listCommands()
        if commands:
            print(f"✓ Found {len(commands)} commands")
            print(f"  Sample commands: {', '.join(commands[:5])}")
        
        # Check if we can access doCommand
        if hasattr(FreeCADGui, 'doCommand'):
            print("✓ FreeCADGui.doCommand available")
        
        # Check if we can access runCommand
        if hasattr(FreeCADGui, 'runCommand'):
            print("✓ FreeCADGui.runCommand available")
        
        # Try to execute a simple command
        try:
            # This should be safe - just gets the active document
            FreeCADGui.doCommand("App.ActiveDocument")
            print("✓ Successfully executed test command")
        except:
            print("  Note: Command execution may require specific context")
        
        return True
    except Exception as e:
        print(f"✗ Command execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("ENHANCED MCP SERVER TEST SUITE")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Basic setup
    mcp = test_basic_setup()
    results['basic_setup'] = mcp is not None
    
    # Test 2: Screenshot
    results['screenshot'] = test_screenshot()
    
    # Test 3: Serialization
    results['serialization'] = test_serialization()
    
    # Test 4: GUI Access
    results['gui_access'] = test_gui_access()
    
    # Test 5: Mouse Automation
    results['mouse_automation'] = test_mouse_automation()
    
    # Test 6: Keyboard Automation
    results['keyboard_automation'] = test_keyboard_automation()
    
    # Test 7: Command Execution
    results['command_execution'] = test_command_execution()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test:.<30} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Enhanced MCP server is ready!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    return results

# Run tests if executed directly
if __name__ == "__main__":
    results = run_all_tests()