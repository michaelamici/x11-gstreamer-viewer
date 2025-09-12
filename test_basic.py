#!/usr/bin/env python3
"""
Basic Test Script for X11 GStreamer Viewer
Created by Ruliano Castian - From the streets to the code!

This script tests the basic functionality of the X11 GStreamer Viewer
without requiring all dependencies to be installed.
"""

import sys
import os

# Add the package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'x11_gstreamer_viewer'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from x11_gstreamer_viewer.core.x11_manager import X11WindowManager
        print("✓ X11WindowManager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import X11WindowManager: {e}")
        return False
    
    try:
        from x11_gstreamer_viewer.core.gstreamer_manager import GStreamerManager
        print("✓ GStreamerManager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import GStreamerManager: {e}")
        return False
    
    try:
        from x11_gstreamer_viewer.ui.main_window import MainWindow
        print("✓ MainWindow imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import MainWindow: {e}")
        return False
    
    try:
        from x11_gstreamer_viewer.utils.config import Config
        print("✓ Config imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Config: {e}")
        return False
    
    return True

def test_x11_manager():
    """Test X11 manager initialization."""
    print("\nTesting X11 Manager...")
    
    try:
        from x11_gstreamer_viewer.core.x11_manager import X11WindowManager
        
        # Test initialization
        x11_manager = X11WindowManager()
        print("✓ X11WindowManager initialized successfully")
        
        # Test window creation
        if x11_manager.create_window(width=800, height=600, title="Test Window"):
            print("✓ Test window created successfully")
            
            # Get window ID
            window_id = x11_manager.get_window_id()
            if window_id:
                print(f"✓ Window ID: {window_id}")
            else:
                print("✗ Could not get window ID")
            
            # Clean up
            x11_manager.destroy_window()
            print("✓ Test window destroyed")
        else:
            print("✗ Failed to create test window")
            return False
        
        # Clean up
        x11_manager.close()
        print("✓ X11WindowManager closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ X11 Manager test failed: {e}")
        return False

def test_gstreamer_manager():
    """Test GStreamer manager initialization."""
    print("\nTesting GStreamer Manager...")
    
    try:
        from x11_gstreamer_viewer.core.gstreamer_manager import GStreamerManager
        
        # Test initialization
        gst_manager = GStreamerManager()
        print("✓ GStreamerManager initialized successfully")
        
        # Test pipeline creation (without window ID for now)
        if gst_manager.create_pipeline():
            print("✓ GStreamer pipeline created successfully")
            
            # Clean up
            gst_manager.destroy_pipeline()
            print("✓ GStreamer pipeline destroyed")
        else:
            print("✗ Failed to create GStreamer pipeline")
            return False
        
        # Clean up
        gst_manager.close()
        print("✓ GStreamerManager closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ GStreamer Manager test failed: {e}")
        return False

def test_config():
    """Test configuration system."""
    print("\nTesting Configuration...")
    
    try:
        from x11_gstreamer_viewer.utils.config import Config
        
        # Test initialization
        config = Config()
        print("✓ Config initialized successfully")
        
        # Test validation
        if config.validate():
            print("✓ Configuration validation passed")
        else:
            print("✗ Configuration validation failed")
            return False
        
        # Test video devices
        devices = config.get_video_devices()
        print(f"✓ Available video devices: {devices}")
        
        # Test argument updating
        args = {
            "video_width": 1280,
            "video_height": 720,
            "window_width": 1920,
            "window_height": 1080,
            "title": "Test Title"
        }
        config.update_from_args(args)
        
        if (config.video.width == 1280 and 
            config.video.height == 720 and 
            config.window.width == 1920 and 
            config.window.height == 1080 and 
            config.window.title == "Test Title"):
            print("✓ Configuration argument updating works")
        else:
            print("✗ Configuration argument updating failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_main_window():
    """Test main window initialization."""
    print("\nTesting Main Window...")
    
    try:
        from x11_gstreamer_viewer.ui.main_window import MainWindow
        
        # Test initialization
        main_window = MainWindow(width=800, height=600)
        print("✓ MainWindow initialized successfully")
        
        # Test window creation
        if main_window.create_window("Test Main Window"):
            print("✓ Main window created successfully")
            
            # Test status
            status = main_window.get_status()
            if status:
                print(f"✓ Status retrieved: {status}")
            else:
                print("✗ Could not get status")
            
            # Clean up
            main_window.close()
            print("✓ Main window closed")
        else:
            print("✗ Failed to create main window")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Main Window test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("X11 GStreamer Viewer - Basic Tests")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_x11_manager,
        test_gstreamer_manager,
        test_config,
        test_main_window,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The X11 GStreamer Viewer is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())