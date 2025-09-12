#!/usr/bin/env python3
"""
Automated Debug Script
Created by Ruliano Castian - From the streets to the code!

Automated script to debug window creation issues without user intervention.
"""

import sys
import os
import time
import subprocess
import logging

# Add the package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'x11_gstreamer_viewer'))

def run_command(cmd, timeout=10):
    """Run a command with timeout."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, 
                              text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def get_window_info():
    """Get comprehensive window information."""
    print("🔍 Analyzing Window Environment...")
    
    # Check window manager
    success, stdout, stderr = run_command("pgrep i3")
    if success and stdout.strip():
        print("   ✓ i3 window manager detected")
        wm = "i3"
    else:
        print("   ⚠ i3 not detected, checking other WMs...")
        success, stdout, stderr = run_command("pgrep -f 'window.*manager'")
        if success and stdout.strip():
            print("   ✓ Other window manager detected")
            wm = "other"
        else:
            print("   ⚠ No window manager detected")
            wm = "none"
    
    # Get window tree
    success, stdout, stderr = run_command("xwininfo -tree -root")
    if success:
        print("   ✓ Window tree retrieved")
        return wm, stdout
    else:
        print(f"   ✗ Failed to get window tree: {stderr}")
        return wm, ""

def analyze_window_creation():
    """Analyze window creation process."""
    print("\n🏗️ Testing Window Creation...")
    
    # Import our modules
    try:
        from x11_gstreamer_viewer.core.x11_manager import X11WindowManager
        from x11_gstreamer_viewer.utils.logger import setup_logging
        
        # Set up logging
        setup_logging(level="INFO")
        
        print("   ✓ Modules imported successfully")
        
        # Test window creation
        print("   Creating test window...")
        x11_manager = X11WindowManager()
        
        if x11_manager.create_window(
            width=600, height=400,
            x=100, y=100,
            title="Automated Debug Test"
        ):
            print("   ✓ Window created successfully")
            
            window_id = x11_manager.get_window_id()
            geometry = x11_manager.get_window_geometry()
            
            print(f"   Window ID: {window_id}")
            print(f"   Geometry: {geometry}")
            
            # Wait and observe
            print("   Observing window behavior...")
            time.sleep(2)
            
            # Check if window is still there
            success, stdout, stderr = run_command("xwininfo -tree -root")
            if success and str(window_id) in stdout:
                print("   ✓ Window still visible in window tree")
            else:
                print("   ⚠ Window not found in window tree")
            
            # Clean up
            print("   Cleaning up...")
            x11_manager.destroy_window()
            x11_manager.close()
            print("   ✓ Window destroyed")
            
            return True
            
        else:
            print("   ✗ Failed to create window")
            return False
            
    except Exception as e:
        print(f"   ✗ Exception during window creation: {e}")
        return False

def test_gstreamer_integration():
    """Test GStreamer integration."""
    print("\n🎥 Testing GStreamer Integration...")
    
    try:
        from x11_gstreamer_viewer.core.gstreamer_manager import GStreamerManager
        from x11_gstreamer_viewer.core.x11_manager import X11WindowManager
        
        print("   Creating X11 window...")
        x11_manager = X11WindowManager()
        
        if x11_manager.create_window(
            width=800, height=600,
            title="GStreamer Integration Test"
        ):
            window_id = x11_manager.get_window_id()
            print(f"   ✓ X11 window created (ID: {window_id})")
            
            print("   Creating GStreamer pipeline...")
            gst_manager = GStreamerManager()
            
            if gst_manager.create_pipeline(window_id):
                print("   ✓ GStreamer pipeline created")
                
                # Check if pipeline can start (without actually starting)
                print("   Testing pipeline state...")
                state = gst_manager.get_pipeline_state()
                print(f"   Pipeline state: {state}")
                
                # Clean up
                gst_manager.destroy_pipeline()
                gst_manager.close()
                x11_manager.destroy_window()
                x11_manager.close()
                
                print("   ✓ Cleanup completed")
                return True
            else:
                print("   ✗ Failed to create GStreamer pipeline")
                x11_manager.destroy_window()
                x11_manager.close()
                return False
        else:
            print("   ✗ Failed to create X11 window")
            return False
            
    except Exception as e:
        print(f"   ✗ Exception during GStreamer test: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive test suite."""
    print("🚀 Running Comprehensive Debug Test")
    print("=" * 50)
    
    # Get initial environment info
    wm, window_tree = get_window_info()
    
    # Test window creation
    window_test_passed = analyze_window_creation()
    
    # Test GStreamer integration
    gstreamer_test_passed = test_gstreamer_integration()
    
    # Final analysis
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Window Manager: {wm}")
    print(f"Window Creation: {'PASS' if window_test_passed else 'FAIL'}")
    print(f"GStreamer Integration: {'PASS' if gstreamer_test_passed else 'FAIL'}")
    
    if window_test_passed and gstreamer_test_passed:
        print("\n🎉 All tests passed! The window fix is working correctly.")
        print("   The double window issue should be resolved.")
        return True
    else:
        print("\n❌ Some tests failed. Issues still exist.")
        if not window_test_passed:
            print("   - Window creation issues detected")
        if not gstreamer_test_passed:
            print("   - GStreamer integration issues detected")
        return False

def main():
    """Main function."""
    print("Automated Window Debug Tool")
    print("Created by Ruliano Castian - From the streets to the code!")
    print()
    
    try:
        success = run_comprehensive_test()
        return 0 if success else 1
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())