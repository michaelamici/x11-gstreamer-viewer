#!/usr/bin/env python3
"""
X11 GStreamer Viewer Demo
Created by Ruliano Castian - From the streets to the code!

A simple demo script that shows the X11 GStreamer Viewer in action.
"""

import sys
import os
import time
import logging

# Add the package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'x11_gstreamer_viewer'))

from x11_gstreamer_viewer.ui.main_window import MainWindow
from x11_gstreamer_viewer.utils.logger import setup_logging

def main():
    """Run the demo."""
    print("X11 GStreamer Viewer Demo")
    print("=" * 30)
    print("Created by Ruliano Castian - From the streets to the code!")
    print()
    
    # Set up logging
    setup_logging(level="INFO")
    logger = logging.getLogger(__name__)
    
    try:
        # Create main window
        logger.info("Creating main window...")
        main_window = MainWindow(width=1920, height=1080)
        
        # Create the window
        if not main_window.create_window("X11 GStreamer Viewer Demo"):
            logger.error("Failed to create main window")
            return 1
        
        logger.info("Main window created successfully!")
        
        # Get window information
        window_id = main_window.x11_manager.get_window_id()
        geometry = main_window.x11_manager.get_window_geometry()
        
        print(f"Window ID: {window_id}")
        print(f"Window Geometry: {geometry}")
        print()
        print("Controls:")
        print("  Left Click: Switch to 4-way view")
        print("  Middle Click: Cycle through cameras")
        print("  Right Click: Exit")
        print("  Escape/Q: Exit")
        print("  1-4: Switch to specific camera")
        print("  0: Switch to 4-way view")
        print()
        print("Starting video pipeline...")
        
        # Start the application
        if main_window.start():
            logger.info("Application started successfully!")
            print("Application is running. Use mouse/keyboard controls to interact.")
            print("Press Ctrl+C to exit.")
            
            # Run the main loop
            main_window.run()
        else:
            logger.error("Failed to start application")
            return 1
        
        logger.info("Demo completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Demo error: {e}")
        return 1
    finally:
        try:
            main_window.close()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())