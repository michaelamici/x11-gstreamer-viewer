#!/usr/bin/env python3
"""
Main Window UI
Created by Ruliano Castian - From the streets to the code!

Main application window that integrates X11 window management
with GStreamer video pipeline.
"""

import logging
from typing import Optional, Callable, Dict, Any

from ..core.x11_manager import X11WindowManager
from ..core.gstreamer_manager import GStreamerManager

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Main application window that manages both X11 and GStreamer components.
    
    Simple and clean implementation following KISS principle.
    """
    
    def __init__(self, width: int = 3840, height: int = 2160):
        """
        Initialize the main window.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        self.width = width
        self.height = height
        
        # Initialize managers
        self.x11_manager: Optional[X11WindowManager] = None
        self.gstreamer_manager: Optional[GStreamerManager] = None
        
        # Application state
        self.running = False
        
        # Event handlers
        self.event_handlers: Dict[str, Callable] = {}
        
        
        # Initialize components
        self._init_components()
        
    def _init_components(self) -> None:
        """Initialize X11 and GStreamer components."""
        try:
            # Initialize X11 manager
            self.x11_manager = X11WindowManager()
            
            # Initialize GStreamer manager
            self.gstreamer_manager = GStreamerManager()
            
            # Set up event handlers
            self._setup_event_handlers()
            
            logger.info("Main window components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _setup_event_handlers(self) -> None:
        """Set up event handlers for user interactions."""
        if self.x11_manager is None:
            return
        
        # Set up X11 event handlers
        from Xlib import X
        
        # Key press handler
        self.x11_manager.set_event_handler(X.KeyPress, self._handle_key_press)
        
        # Client message handler (window close)
        self.x11_manager.set_event_handler(X.ClientMessage, self._handle_client_message)
        
        logger.info("Event handlers set up")
    
    def create_window(self, title: str = "X11 GStreamer Viewer") -> bool:
        """
        Create the main window.
        
        Args:
            title: Window title
            
        Returns:
            True if window created successfully, False otherwise
        """
        try:
            if self.x11_manager is None:
                logger.error("X11 manager not initialized")
                return False
            
            # Create X11 window
            if not self.x11_manager.create_window(
                width=self.width,
                height=self.height,
                title=title
            ):
                logger.error("Failed to create X11 window")
                return False
            
            # Get window ID for GStreamer
            window_id = self.x11_manager.get_window_id()
            if window_id is None:
                logger.error("Could not get window ID")
                return False
            
            # Create GStreamer pipeline
            if not self.gstreamer_manager.create_pipeline(window_id):
                logger.error("Failed to create GStreamer pipeline")
                return False
            
            logger.info(f"Main window created successfully (ID: {window_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create main window: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start the main window and video pipeline.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            if self.gstreamer_manager is None:
                logger.error("GStreamer manager not initialized")
                return False
            
            # Start GStreamer pipeline
            if not self.gstreamer_manager.start_pipeline():
                logger.error("Failed to start GStreamer pipeline")
                return False
            
            
            self.running = True
            logger.info("Main window started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start main window: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the main window and cleanup resources."""
        try:
            self.running = False
            
            # Stop GStreamer pipeline
            if self.gstreamer_manager is not None:
                self.gstreamer_manager.stop_pipeline()
            
            
            logger.info("Main window stopped")
            
        except Exception as e:
            logger.error(f"Error stopping main window: {e}")
    
    def run(self) -> None:
        """Run the main event loop."""
        try:
            if not self.start():
                logger.error("Failed to start main window")
                return
            
            logger.info("Main window running...")
            logger.info("Controls:")
            logger.info("  Escape/Q: Exit")
            
            # Run X11 event loop
            if self.x11_manager is not None:
                self.x11_manager.run_event_loop()
            
        except KeyboardInterrupt:
            logger.info("Main window interrupted by user")
        except Exception as e:
            logger.error(f"Error in main window: {e}")
        finally:
            self.stop()
    
    
    def _handle_key_press(self, event) -> None:
        """Handle key press events."""
        try:
            keysym = self.x11_manager.dpy.keycode_to_keysym(event.detail, 0)
            from Xlib import XK
            
            if keysym == XK.XK_Escape or keysym == XK.XK_q:
                logger.info("Exit key pressed")
                self.running = False
                if self.x11_manager is not None:
                    self.x11_manager.running = False
                
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
    
    def _handle_client_message(self, event) -> None:
        """Handle client message events (window close)."""
        try:
            if (self.x11_manager is not None and 
                event.data[0] == self.x11_manager.dpy.intern_atom("WM_DELETE_WINDOW").atom):
                logger.info("Window close requested")
                self.running = False
                if self.x11_manager is not None:
                    self.x11_manager.running = False
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current application status."""
        status = {
            "running": self.running,
            "window_geometry": None,
            "pipeline_state": None,
        }
        
        try:
            if self.x11_manager is not None:
                status["window_geometry"] = self.x11_manager.get_window_geometry()
            
            if self.gstreamer_manager is not None:
                status["pipeline_state"] = self.gstreamer_manager.get_pipeline_state()
                
        except Exception as e:
            logger.error(f"Error getting status: {e}")
        
        return status
    
    def close(self) -> None:
        """Close the main window and cleanup all resources."""
        try:
            self.stop()
            
            if self.gstreamer_manager is not None:
                self.gstreamer_manager.close()
                self.gstreamer_manager = None
            
            if self.x11_manager is not None:
                self.x11_manager.close()
                self.x11_manager = None
            
            logger.info("Main window closed")
            
        except Exception as e:
            logger.error(f"Error closing main window: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()