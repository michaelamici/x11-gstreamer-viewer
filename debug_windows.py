#!/usr/bin/env python3
"""
Window Debug Script
Created by Ruliano Castian - From the streets to the code!

Debug script to analyze window creation issues in i3 window manager.
"""

import sys
import os
import time
import subprocess
import logging

# Add the package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'x11_gstreamer_viewer'))

from Xlib import display, X
from x11_gstreamer_viewer.core.x11_manager import X11WindowManager
from x11_gstreamer_viewer.utils.logger import setup_logging

def get_window_info():
    """Get information about all windows."""
    try:
        # Get window tree
        result = subprocess.run(['xwininfo', '-tree', '-root'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error getting window tree: {result.stderr}"
    except Exception as e:
        return f"Exception getting window info: {e}"

def get_window_manager_info():
    """Get window manager information."""
    try:
        # Check if i3 is running
        result = subprocess.run(['pgrep', 'i3'], capture_output=True, text=True)
        if result.returncode == 0:
            return "i3 window manager detected"
        else:
            return "i3 not detected"
    except Exception as e:
        return f"Exception checking window manager: {e}"

def analyze_window_creation():
    """Analyze window creation process."""
    print("Window Debug Analysis")
    print("=" * 50)
    
    # Set up logging
    setup_logging(level="DEBUG")
    logger = logging.getLogger(__name__)
    
    print("1. Window Manager Info:")
    print(f"   {get_window_manager_info()}")
    print()
    
    print("2. Current Windows (before test):")
    window_info_before = get_window_info()
    print("   " + window_info_before.replace('\n', '\n   '))
    print()
    
    print("3. Creating test window...")
    try:
        # Create X11 manager
        x11_manager = X11WindowManager()
        
        # Create a small test window
        if x11_manager.create_window(width=400, height=300, title="Debug Test Window"):
            print("   ✓ Test window created successfully")
            
            window_id = x11_manager.get_window_id()
            geometry = x11_manager.get_window_geometry()
            print(f"   Window ID: {window_id}")
            print(f"   Geometry: {geometry}")
            
            print("4. Current Windows (after creation):")
            window_info_after = get_window_info()
            print("   " + window_info_after.replace('\n', '\n   '))
            print()
            
            print("5. Window Properties Analysis:")
            try:
                # Get detailed window info
                dpy = display.Display()
                window = dpy.create_resource_object('window', window_id)
                
                # Get window attributes
                attrs = window.get_attributes()
                print(f"   Window attributes: {attrs}")
                
                # Get window properties
                wm_name = window.get_wm_name()
                wm_class = window.get_wm_class()
                print(f"   WM Name: {wm_name}")
                print(f"   WM Class: {wm_class}")
                
                # Check if window is mapped
                print(f"   Mapped: {attrs.map_state == X.IsViewable}")
                
            except Exception as e:
                print(f"   Error analyzing window properties: {e}")
            
            print()
            print("6. Waiting 3 seconds to observe window behavior...")
            time.sleep(3)
            
            print("7. Destroying test window...")
            x11_manager.destroy_window()
            x11_manager.close()
            
            print("8. Current Windows (after destruction):")
            window_info_final = get_window_info()
            print("   " + window_info_final.replace('\n', '\n   '))
            
        else:
            print("   ✗ Failed to create test window")
            
    except Exception as e:
        print(f"   ✗ Exception during window creation: {e}")
        logger.exception("Window creation failed")

def test_multiple_windows():
    """Test creating multiple windows to see if duplicates occur."""
    print("\nMultiple Window Test")
    print("=" * 30)
    
    try:
        windows = []
        
        for i in range(3):
            print(f"Creating window {i+1}...")
            x11_manager = X11WindowManager()
            
            if x11_manager.create_window(
                width=300, height=200, 
                x=100 + i*50, y=100 + i*50,
                title=f"Test Window {i+1}"
            ):
                window_id = x11_manager.get_window_id()
                windows.append((x11_manager, window_id))
                print(f"   ✓ Window {i+1} created (ID: {window_id})")
            else:
                print(f"   ✗ Failed to create window {i+1}")
        
        print(f"\nCreated {len(windows)} windows")
        
        # Show current window state
        print("\nCurrent Windows:")
        window_info = get_window_info()
        print("   " + window_info.replace('\n', '\n   '))
        
        # Clean up
        print("\nCleaning up...")
        for x11_manager, window_id in windows:
            x11_manager.destroy_window()
            x11_manager.close()
            print(f"   Destroyed window {window_id}")
            
    except Exception as e:
        print(f"Exception during multiple window test: {e}")

def main():
    """Main debug function."""
    print("X11 Window Debug Tool")
    print("Created by Ruliano Castian - From the streets to the code!")
    print()
    
    analyze_window_creation()
    test_multiple_windows()
    
    print("\nDebug analysis complete!")

if __name__ == "__main__":
    main()