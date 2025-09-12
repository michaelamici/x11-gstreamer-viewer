#!/usr/bin/env python3
"""
Window Fix Test Script
Created by Ruliano Castian - From the streets to the code!

Test script to verify the window creation fix for i3 compatibility.
"""

import sys
import os
import time
import subprocess

# Add the package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'x11_gstreamer_viewer'))

from x11_gstreamer_viewer.core.x11_manager import X11WindowManager
from x11_gstreamer_viewer.utils.logger import setup_logging

def count_windows():
    """Count the number of windows."""
    try:
        result = subprocess.run(['xwininfo', '-tree', '-root'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # Count non-root windows
            lines = result.stdout.split('\n')
            window_count = 0
            for line in lines:
                if 'x11-gstreamer-viewer' in line.lower() or 'test' in line.lower():
                    window_count += 1
            return window_count
        return 0
    except Exception:
        return 0

def test_window_creation():
    """Test window creation and count."""
    print("Testing Window Creation Fix")
    print("=" * 40)
    
    # Set up logging
    setup_logging(level="INFO")
    
    print("1. Counting windows before test...")
    windows_before = count_windows()
    print(f"   Windows before: {windows_before}")
    
    print("2. Creating test window...")
    try:
        x11_manager = X11WindowManager()
        
        if x11_manager.create_window(
            width=800, height=600, 
            x=100, y=100,
            title="Window Fix Test"
        ):
            print("   ✓ Window created successfully")
            
            window_id = x11_manager.get_window_id()
            geometry = x11_manager.get_window_geometry()
            print(f"   Window ID: {window_id}")
            print(f"   Geometry: {geometry}")
            
            print("3. Counting windows after creation...")
            windows_after = count_windows()
            print(f"   Windows after: {windows_after}")
            
            if windows_after == windows_before + 1:
                print("   ✓ Correct number of windows created")
            else:
                print(f"   ✗ Expected {windows_before + 1} windows, got {windows_after}")
            
            print("4. Waiting 2 seconds to observe window behavior...")
            time.sleep(2)
            
            print("5. Destroying window...")
            x11_manager.destroy_window()
            x11_manager.close()
            
            print("6. Counting windows after destruction...")
            windows_final = count_windows()
            print(f"   Windows after destruction: {windows_final}")
            
            if windows_final == windows_before:
                print("   ✓ Window properly destroyed")
            else:
                print(f"   ✗ Expected {windows_before} windows, got {windows_final}")
            
            return windows_after == windows_before + 1 and windows_final == windows_before
            
        else:
            print("   ✗ Failed to create window")
            return False
            
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        return False

def test_multiple_windows():
    """Test creating multiple windows."""
    print("\nTesting Multiple Window Creation")
    print("=" * 40)
    
    try:
        windows_before = count_windows()
        print(f"Windows before: {windows_before}")
        
        managers = []
        
        # Create 3 windows
        for i in range(3):
            print(f"Creating window {i+1}...")
            x11_manager = X11WindowManager()
            
            if x11_manager.create_window(
                width=400, height=300,
                x=200 + i*50, y=200 + i*50,
                title=f"Test Window {i+1}"
            ):
                managers.append(x11_manager)
                print(f"   ✓ Window {i+1} created")
            else:
                print(f"   ✗ Failed to create window {i+1}")
        
        windows_after = count_windows()
        print(f"Windows after creating {len(managers)} windows: {windows_after}")
        
        expected = windows_before + len(managers)
        if windows_after == expected:
            print(f"   ✓ Correct number of windows ({expected})")
        else:
            print(f"   ✗ Expected {expected} windows, got {windows_after}")
        
        # Clean up
        print("Cleaning up...")
        for i, manager in enumerate(managers):
            manager.destroy_window()
            manager.close()
            print(f"   Destroyed window {i+1}")
        
        windows_final = count_windows()
        print(f"Windows after cleanup: {windows_final}")
        
        if windows_final == windows_before:
            print("   ✓ All windows properly cleaned up")
        else:
            print(f"   ✗ Expected {windows_before} windows, got {windows_final}")
        
        return windows_after == expected and windows_final == windows_before
        
    except Exception as e:
        print(f"Exception during multiple window test: {e}")
        return False

def main():
    """Main test function."""
    print("Window Fix Test Suite")
    print("Created by Ruliano Castian - From the streets to the code!")
    print()
    
    test1_passed = test_window_creation()
    test2_passed = test_multiple_windows()
    
    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"Single window test: {'PASS' if test1_passed else 'FAIL'}")
    print(f"Multiple window test: {'PASS' if test2_passed else 'FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Window fix is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Window issues still exist.")
        return 1

if __name__ == "__main__":
    sys.exit(main())