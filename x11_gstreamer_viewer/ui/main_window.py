#!/usr/bin/env python3
"""
Main Window UI
Created by Ruliano Castian - From the streets to the code!

Main application window that integrates X11 window management
with GStreamer video pipeline.
"""

import logging
import threading
import time
from typing import Optional, Callable, Dict, Any
from enum import Enum

from ..core.x11_manager import X11WindowManager
from ..core.gstreamer_manager import GStreamerManager, ViewMode

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Main application window that manages both X11 and GStreamer components.
    
    This class serves as the main interface between the X11 window system
    and the GStreamer video pipeline, handling user interactions and
    coordinating between the two systems.
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
        self.current_view_mode = ViewMode.FOUR_WAY
        
        # Event handlers
        self.event_handlers: Dict[str, Callable] = {}
        
        # Threading
        self.event_thread: Optional[threading.Thread] = None
        self.gstreamer_thread: Optional[threading.Thread] = None
        
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
        
        # Button press handler
        self.x11_manager.set_event_handler(X.ButtonPress, self._handle_button_press)
        
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
            
            # Start event handling thread
            self._start_event_thread()
            
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
            
            # Stop event thread
            self._stop_event_thread()
            
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
            logger.info("  Left Click: Switch to 4-way view")
            logger.info("  Middle Click: Cycle through cameras")
            logger.info("  Right Click: Exit")
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
    
    def _start_event_thread(self) -> None:
        """Start the event handling thread."""
        try:
            self.event_thread = threading.Thread(
                target=self._event_loop,
                daemon=True,
                name="EventThread"
            )
            self.event_thread.start()
            logger.info("Event thread started")
        except Exception as e:
            logger.error(f"Failed to start event thread: {e}")
    
    def _stop_event_thread(self) -> None:
        """Stop the event handling thread."""
        try:
            if self.event_thread is not None and self.event_thread.is_alive():
                # The thread will stop when self.running becomes False
                self.event_thread.join(timeout=1.0)
                logger.info("Event thread stopped")
        except Exception as e:
            logger.error(f"Error stopping event thread: {e}")
    
    def _event_loop(self) -> None:
        """Event handling loop."""
        try:
            while self.running:
                # Handle GStreamer events if needed
                if self.gstreamer_manager is not None:
                    # Check pipeline state
                    state = self.gstreamer_manager.get_pipeline_state()
                    if state != "GST_STATE_PLAYING" and self.running:
                        logger.warning(f"Pipeline state: {state}")
                
                time.sleep(0.1)  # Small delay
                
        except Exception as e:
            logger.error(f"Error in event loop: {e}")
    
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
            elif keysym == XK.XK_1:
                self._switch_to_camera(1)
            elif keysym == XK.XK_2:
                self._switch_to_camera(2)
            elif keysym == XK.XK_3:
                self._switch_to_camera(3)
            elif keysym == XK.XK_4:
                self._switch_to_camera(4)
            elif keysym == XK.XK_0:
                self._switch_to_four_way()
                
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
    
    def _handle_button_press(self, event) -> None:
        """Handle mouse button press events."""
        try:
            button = event.detail
            x, y = event.event_x, event.event_y
            
            logger.debug(f"Mouse button {button} pressed at ({x}, {y})")
            
            if button == 1:  # Left click
                self._handle_left_click(x, y)
            elif button == 2:  # Middle click
                self._handle_middle_click(x, y)
            elif button == 3:  # Right click
                self._handle_right_click(x, y)
                
        except Exception as e:
            logger.error(f"Error handling button press: {e}")
    
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
    
    def _handle_left_click(self, x: int, y: int) -> None:
        """Handle left mouse click - switch to 4-way view."""
        logger.info(f"Left click at ({x}, {y}) - switching to 4-way view")
        self._switch_to_four_way()
    
    def _handle_middle_click(self, x: int, y: int) -> None:
        """Handle middle mouse click - cycle through cameras."""
        logger.info(f"Middle click at ({x}, {y}) - cycling cameras")
        self._cycle_cameras()
    
    def _handle_right_click(self, x: int, y: int) -> None:
        """Handle right mouse click - exit application."""
        logger.info(f"Right click at ({x}, {y}) - exiting")
        self.running = False
        if self.x11_manager is not None:
            self.x11_manager.running = False
    
    def _switch_to_four_way(self) -> None:
        """Switch to 4-way view mode."""
        try:
            if self.gstreamer_manager is not None:
                if self.gstreamer_manager.switch_view_mode(ViewMode.FOUR_WAY):
                    self.current_view_mode = ViewMode.FOUR_WAY
                    logger.info("Switched to 4-way view")
                else:
                    logger.error("Failed to switch to 4-way view")
        except Exception as e:
            logger.error(f"Error switching to 4-way view: {e}")
    
    def _switch_to_camera(self, camera_num: int) -> None:
        """Switch to specific camera view."""
        try:
            if self.gstreamer_manager is not None:
                mode_map = {
                    1: ViewMode.CAMERA_1,
                    2: ViewMode.CAMERA_2,
                    3: ViewMode.CAMERA_3,
                    4: ViewMode.CAMERA_4,
                }
                
                mode = mode_map.get(camera_num)
                if mode is not None:
                    if self.gstreamer_manager.switch_view_mode(mode):
                        self.current_view_mode = mode
                        logger.info(f"Switched to camera {camera_num}")
                    else:
                        logger.error(f"Failed to switch to camera {camera_num}")
                else:
                    logger.warning(f"Invalid camera number: {camera_num}")
        except Exception as e:
            logger.error(f"Error switching to camera {camera_num}: {e}")
    
    def _cycle_cameras(self) -> None:
        """Cycle through camera views."""
        try:
            camera_modes = [ViewMode.CAMERA_1, ViewMode.CAMERA_2, ViewMode.CAMERA_3, ViewMode.CAMERA_4]
            
            if self.current_view_mode in camera_modes:
                # Find next camera
                current_index = camera_modes.index(self.current_view_mode)
                next_index = (current_index + 1) % len(camera_modes)
                next_mode = camera_modes[next_index]
            else:
                # Start with camera 1
                next_mode = ViewMode.CAMERA_1
            
            if self.gstreamer_manager is not None:
                if self.gstreamer_manager.switch_view_mode(next_mode):
                    self.current_view_mode = next_mode
                    logger.info(f"Cycled to {next_mode.value}")
                else:
                    logger.error(f"Failed to cycle to {next_mode.value}")
        except Exception as e:
            logger.error(f"Error cycling cameras: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current application status.
        
        Returns:
            Dictionary with status information
        """
        status = {
            "running": self.running,
            "current_view_mode": self.current_view_mode.value,
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