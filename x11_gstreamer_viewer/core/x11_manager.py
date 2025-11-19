#!/usr/bin/env python3
"""
X11 Window Manager
Created by Ruliano Castian - From the streets to the code!

Handles X11 window creation, management, and event handling.
"""

import logging
from typing import Optional, Tuple, Callable, Dict, Any
from Xlib import X, XK, display
from Xlib.protocol import request
from Xlib.xobject import drawable
from Xlib.error import BadWindow, BadDrawable

logger = logging.getLogger(__name__)


class X11WindowManager:
    """
    Manages X11 windows and handles window events.
    
    This class provides a clean interface for creating and managing
    X11 windows with proper event handling and cleanup.
    """
    
    def __init__(self, display_name: Optional[str] = None):
        """
        Initialize the X11 Window Manager.
        
        Args:
            display_name: X11 display name (e.g., ":0.0")
        """
        self.display_name = display_name
        self.dpy: Optional[display.Display] = None
        self.screen: Optional[Any] = None
        self.root: Optional[drawable.Window] = None
        self.window: Optional[drawable.Window] = None
        self.gc: Optional[Any] = None
        self.running = False
        
        # Window properties
        self.window_width = 3840
        self.window_height = 2160
        self.window_x = 0
        self.window_y = 0
        
        # Event handlers
        self.event_handlers: Dict[int, Callable] = {}
        
        # Initialize display
        self._init_display()
        
    def _init_display(self) -> None:
        """Initialize X11 display connection."""
        try:
            self.dpy = display.Display(self.display_name)
            self.screen = self.dpy.screen()
            self.root = self.screen.root
            
            logger.info(f"Connected to X11 display: {self.dpy.get_display_name()}")
            logger.info(f"Screen dimensions: {self.screen.width_in_pixels}x{self.screen.height_in_pixels}")
            
        except Exception as e:
            logger.error(f"Failed to connect to X11 display: {e}")
            raise
    
    def create_window(self, 
                     width: int = 3840, 
                     height: int = 2160,
                     x: int = 0, 
                     y: int = 0,
                     title: str = "X11 GStreamer Viewer") -> bool:
        """
        Create a new X11 window.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            x: Window X position
            y: Window Y position
            title: Window title
            
        Returns:
            True if window created successfully, False otherwise
        """
        try:
            if self.window is not None:
                logger.warning("Window already exists, destroying it first")
                self.destroy_window()
            
            # Store window properties
            self.window_width = width
            self.window_height = height
            self.window_x = x
            self.window_y = y
            
            # Create window
            self.window = self.root.create_window(
                x, y, width, height, 0,
                self.screen.root_depth,
                X.CopyFromParent,
                X.CopyFromParent,
                background_pixel=self.screen.black_pixel,  # Black background for video
                event_mask=(X.ExposureMask | X.KeyPressMask | X.KeyReleaseMask | 
                           X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask |
                           X.StructureNotifyMask | X.FocusChangeMask)
            )
            
            # Set window properties
            self.window.set_wm_name(title)
            self.window.set_wm_class("x11-gstreamer-viewer", "X11GStreamerViewer")
            
            # Set window type for better window manager integration
            try:
                # Set window type to normal window (not override-redirect)
                self.window.change_attributes(override_redirect=False)
                
                # Set window state hints for tiling window managers
                from Xlib.protocol.request import ConfigureWindow
                self.window.configure(
                    x=x, y=y, width=width, height=height,
                    border_width=0,
                    stack_mode=X.Above
                )
            except Exception as e:
                logger.debug(f"Could not set window attributes: {e}")
            
            # Set window hints (simplified approach)
            try:
                hints = {
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height,
                    'min_width': width,
                    'min_height': height,
                    'max_width': width,
                    'max_height': height,
                }
                self.window.set_wm_normal_hints(**hints)
            except Exception as e:
                logger.debug(f"Could not set window hints: {e}")
            
            # Set up window manager protocol
            try:
                # Set WM_DELETE_WINDOW protocol for proper window closing
                wm_delete_window = self.dpy.intern_atom("WM_DELETE_WINDOW")
                self.window.set_wm_protocols([wm_delete_window])
                
                # Set window state
                wm_state = self.dpy.intern_atom("WM_STATE")
                from Xlib import Xatom
                self.window.change_property(
                    wm_state, Xatom.WM_STATE, 32, [1, 0]  # Normal state
                )
            except Exception as e:
                logger.debug(f"Could not set window manager protocol: {e}")
            
            # Create graphics context
            self.gc = self.window.create_gc(
                foreground=self.screen.white_pixel,
                background=self.screen.black_pixel  # Match window background
            )
            
            # Map window
            self.window.map()
            
            # Flush display
            self.dpy.flush()
            
            # Wait for MapNotify event to ensure window is ready for embedding
            self._wait_for_map_notify()
            
            logger.info(f"Created window: {width}x{height} at ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create window: {e}")
            return False
    
    def _wait_for_map_notify(self, timeout: float = 5.0) -> bool:
        """
        Wait for MapNotify event to ensure window is ready for embedding.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if MapNotify received, False if timeout
        """
        if self.window is None or self.dpy is None:
            return False
        
        import time
        start_time = time.time()
        
        try:
            # Process events until we get MapNotify for our window
            while time.time() - start_time < timeout:
                if self.dpy.pending_events():
                    event = self.dpy.next_event()
                    # Check if this is a MapNotify event for our window
                    if event.type == X.MapNotify:
                        # MapNotify event has 'window' attribute pointing to the mapped window
                        if hasattr(event, 'window') and event.window == self.window:
                            logger.debug("Received MapNotify event, window is ready")
                            return True
                        # Also check event.event (some X11 implementations use this)
                        elif hasattr(event, 'event') and event.event == self.window:
                            logger.debug("Received MapNotify event, window is ready")
                            return True
                else:
                    # Small sleep to avoid busy waiting
                    time.sleep(0.01)
            
            logger.warning(f"Timeout waiting for MapNotify event after {timeout}s")
            return False
            
        except Exception as e:
            logger.debug(f"Error waiting for MapNotify: {e}")
            # Don't fail completely, window might still work
            return False
    
    def destroy_window(self) -> None:
        """Destroy the current window."""
        try:
            if self.window is not None:
                self.window.destroy()
                self.window = None
                self.gc = None
                self.dpy.flush()
                logger.info("Window destroyed")
        except Exception as e:
            logger.error(f"Failed to destroy window: {e}")
    
    def set_event_handler(self, event_type: int, handler: Callable) -> None:
        """
        Set an event handler for a specific event type.
        
        Args:
            event_type: X11 event type (e.g., X.KeyPress)
            handler: Function to handle the event
        """
        self.event_handlers[event_type] = handler
        logger.debug(f"Set event handler for event type: {event_type}")
    
    def get_window_id(self) -> Optional[int]:
        """
        Get the window ID for GStreamer integration.
        
        Returns:
            Window ID as integer, or None if no window exists
        """
        if self.window is not None:
            return self.window.id
        return None
    
    def get_window_geometry(self) -> Tuple[int, int, int, int]:
        """
        Get current window geometry.
        
        Returns:
            Tuple of (x, y, width, height)
        """
        if self.window is not None:
            try:
                geometry = self.window.get_geometry()
                return (geometry.x, geometry.y, geometry.width, geometry.height)
            except (BadWindow, BadDrawable):
                pass
        
        return (self.window_x, self.window_y, self.window_width, self.window_height)
    
    def draw_text(self, text: str, x: int, y: int, color: Optional[int] = None) -> None:
        """
        Draw text on the window.
        
        Args:
            text: Text to draw
            x: X position
            y: Y position
            color: Text color (optional)
        """
        if self.window is None or self.gc is None:
            return
        
        try:
            if color is not None:
                self.gc.change(foreground=color)
            
            self.window.draw_text(self.gc, x, y, text)
            self.dpy.flush()
            
        except Exception as e:
            logger.error(f"Failed to draw text: {e}")
    
    def clear_window(self, color: Optional[int] = None) -> None:
        """
        Clear the window with specified color.
        
        Args:
            color: Background color (optional)
        """
        if self.window is None or self.gc is None:
            return
        
        try:
            if color is not None:
                self.gc.change(background=color)
            
            self.window.fill_rectangle(self.gc, 0, 0, self.window_width, self.window_height)
            self.dpy.flush()
            
        except Exception as e:
            logger.error(f"Failed to clear window: {e}")
    
    def handle_events(self) -> None:
        """Handle X11 events."""
        if self.dpy is None:
            return
        
        try:
            while self.dpy.pending_events():
                event = self.dpy.next_event()
                
                # Call registered event handler
                if event.type in self.event_handlers:
                    self.event_handlers[event.type](event)
                
                # Handle common events
                if event.type == X.Expose:
                    self._handle_expose(event)
                elif event.type == X.KeyPress:
                    self._handle_key_press(event)
                elif event.type == X.ButtonPress:
                    self._handle_button_press(event)
                elif event.type == X.ClientMessage:
                    self._handle_client_message(event)
                    
        except Exception as e:
            logger.error(f"Error handling events: {e}")
    
    def _handle_expose(self, event) -> None:
        """Handle window expose events."""
        logger.debug("Window exposed")
        # Redraw window content if needed
    
    def _handle_key_press(self, event) -> None:
        """Handle key press events."""
        keysym = self.dpy.keycode_to_keysym(event.detail, 0)
        key_name = XK.keysym_to_string(keysym)
        
        logger.debug(f"Key pressed: {key_name}")
        
        # Handle special keys
        if keysym == XK.XK_Escape:
            logger.info("Escape key pressed, exiting...")
            self.running = False
        elif keysym == XK.XK_q:
            logger.info("Q key pressed, exiting...")
            self.running = False
    
    def _handle_button_press(self, event) -> None:
        """Handle mouse button press events."""
        button = event.detail
        x, y = event.event_x, event.event_y
        
        logger.debug(f"Mouse button {button} pressed at ({x}, {y})")
        
        # Handle different mouse buttons
        if button == 1:  # Left click
            self._handle_left_click(x, y)
        elif button == 2:  # Middle click
            self._handle_middle_click(x, y)
        elif button == 3:  # Right click
            self._handle_right_click(x, y)
    
    def _handle_left_click(self, x: int, y: int) -> None:
        """Handle left mouse click."""
        logger.info(f"Left click at ({x}, {y})")
        # Implement view switching logic here
    
    def _handle_middle_click(self, x: int, y: int) -> None:
        """Handle middle mouse click."""
        logger.info(f"Middle click at ({x}, {y})")
        # Implement camera cycling logic here
    
    def _handle_right_click(self, x: int, y: int) -> None:
        """Handle right mouse click."""
        logger.info(f"Right click at ({x}, {y})")
        # Implement exit logic here
    
    def _handle_client_message(self, event) -> None:
        """Handle client message events (e.g., window close)."""
        logger.debug("Client message received")
        if event.data[0] == self.dpy.intern_atom("WM_DELETE_WINDOW").atom:
            logger.info("Window close requested")
            self.running = False
    
    def run_event_loop(self) -> None:
        """Run the main event loop."""
        if self.window is None:
            logger.error("No window created, cannot run event loop")
            return
        
        self.running = True
        logger.info("Starting X11 event loop...")
        
        try:
            while self.running:
                self.handle_events()
                self.dpy.flush()
                
                # Small delay to prevent excessive CPU usage
                self.dpy.sync()
                
        except KeyboardInterrupt:
            logger.info("Event loop interrupted by user")
        except Exception as e:
            logger.error(f"Error in event loop: {e}")
        finally:
            self.running = False
            logger.info("Event loop ended")
    
    def close(self) -> None:
        """Close the X11 connection and cleanup resources."""
        try:
            self.running = False
            self.destroy_window()
            
            if self.dpy is not None:
                self.dpy.close()
                self.dpy = None
            
            logger.info("X11 connection closed")
            
        except Exception as e:
            logger.error(f"Error closing X11 connection: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()