#!/usr/bin/env python3
"""
GStreamer Manager
Created by Ruliano Castian - From the streets to the code!

Manages GStreamer pipeline for 4-way video viewing.
"""

import logging
import gi
from typing import Optional, List, Dict, Any
from enum import Enum

# GStreamer imports
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GstVideo, GLib

logger = logging.getLogger(__name__)


class ViewMode(Enum):
    """View modes for the video display."""
    FOUR_WAY = "4way"
    CAMERA_1 = "camera1"
    CAMERA_2 = "camera2"
    CAMERA_3 = "camera3"
    CAMERA_4 = "camera4"


class GStreamerManager:
    """
    Manages GStreamer pipeline for 4-way video viewing.
    
    This class creates and manages the GStreamer pipeline that replicates
    the functionality of the running gst-launch command.
    """
    
    def __init__(self):
        """Initialize the GStreamer Manager."""
        self.pipeline: Optional[Gst.Pipeline] = None
        self.current_mode = ViewMode.FOUR_WAY
        self.running = False
        
        # Video configuration
        self.video_width = 1920
        self.video_height = 1080
        self.output_width = 3840
        self.output_height = 2160
        
        # Video devices
        self.video_devices = ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3"]
        
        # Pipeline elements
        self.video_sources: List[Gst.Element] = []
        self.compositor: Optional[Gst.Element] = None
        self.video_sink: Optional[Gst.Element] = None
        
        # Initialize GStreamer
        self._init_gstreamer()
        
    def _init_gstreamer(self) -> None:
        """Initialize GStreamer."""
        try:
            Gst.init(None)
            logger.info("GStreamer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GStreamer: {e}")
            raise
    
    def create_pipeline(self, window_id: Optional[int] = None) -> bool:
        """
        Create the GStreamer pipeline.
        
        Args:
            window_id: X11 window ID for video sink
            
        Returns:
            True if pipeline created successfully, False otherwise
        """
        try:
            if self.pipeline is not None:
                logger.warning("Pipeline already exists, destroying it first")
                self.destroy_pipeline()
            
            # Create pipeline
            self.pipeline = Gst.Pipeline.new("video-viewer-pipeline")
            
            # Create video sources
            self._create_video_sources()
            
            # Create compositor
            self._create_compositor()
            
            # Create video sink
            self._create_video_sink(window_id)
            
            # Link elements
            self._link_elements()
            
            logger.info("GStreamer pipeline created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create pipeline: {e}")
            return False
    
    def _create_video_sources(self) -> None:
        """Create video source elements."""
        self.video_sources = []
        
        for i, device in enumerate(self.video_devices):
            try:
                # Create v4l2src element
                src = Gst.ElementFactory.make("v4l2src", f"video_src_{i}")
                if src is None:
                    logger.warning(f"Could not create v4l2src for device {device}")
                    continue
                
                # Set device property
                src.set_property("device", device)
                
                # Create videoconvert element
                convert = Gst.ElementFactory.make("videoconvert", f"video_convert_{i}")
                if convert is None:
                    logger.error(f"Could not create videoconvert for source {i}")
                    continue
                
                # Create videoscale element
                scale = Gst.ElementFactory.make("videoscale", f"video_scale_{i}")
                if scale is None:
                    logger.error(f"Could not create videoscale for source {i}")
                    continue
                
                # Create caps filter
                caps = Gst.ElementFactory.make("capsfilter", f"video_caps_{i}")
                if caps is None:
                    logger.error(f"Could not create capsfilter for source {i}")
                    continue
                
                # Set caps properties
                caps_str = f"video/x-raw,width={self.video_width},height={self.video_height}"
                caps.set_property("caps", Gst.caps_from_string(caps_str))
                
                # Add elements to pipeline
                self.pipeline.add(src)
                self.pipeline.add(convert)
                self.pipeline.add(scale)
                self.pipeline.add(caps)
                
                # Link source elements
                src.link(convert)
                convert.link(scale)
                scale.link(caps)
                
                # Store the caps element as the output of this source
                self.video_sources.append(caps)
                
                logger.info(f"Created video source {i} for device {device}")
                
            except Exception as e:
                logger.error(f"Failed to create video source {i}: {e}")
    
    def _create_compositor(self) -> None:
        """Create the compositor element."""
        try:
            self.compositor = Gst.ElementFactory.make("compositor", "video_compositor")
            if self.compositor is None:
                raise Exception("Could not create compositor element")
            
            # Set compositor properties using caps
            # Note: Compositor properties are set via caps or pad properties
            # We'll set them when linking the elements
            
            # Add to pipeline
            self.pipeline.add(self.compositor)
            
            logger.info("Created compositor element")
            
        except Exception as e:
            logger.error(f"Failed to create compositor: {e}")
            raise
    
    def _create_video_sink(self, window_id: Optional[int] = None) -> None:
        """Create the video sink element."""
        try:
            # Create videoconvert for final output
            convert = Gst.ElementFactory.make("videoconvert", "final_convert")
            if convert is None:
                raise Exception("Could not create final videoconvert")
            
            # Create video sink
            if window_id is not None:
                # Use xvimagesink for X11 window
                self.video_sink = Gst.ElementFactory.make("xvimagesink", "video_sink")
                if self.video_sink is None:
                    logger.warning("Could not create xvimagesink, falling back to autovideosink")
                    self.video_sink = Gst.ElementFactory.make("autovideosink", "video_sink")
            else:
                # Use autovideosink
                self.video_sink = Gst.ElementFactory.make("autovideosink", "video_sink")
            
            if self.video_sink is None:
                raise Exception("Could not create video sink")
            
            # Set sink properties
            if hasattr(self.video_sink, 'set_property'):
                if window_id is not None:
                    try:
                        self.video_sink.set_property("window-id", window_id)
                    except Exception as e:
                        logger.debug(f"Could not set window-id property: {e}")
                        # Try alternative property names
                        try:
                            self.video_sink.set_property("window", window_id)
                        except Exception as e2:
                            logger.debug(f"Could not set window property: {e2}")
            
            # Add to pipeline
            self.pipeline.add(convert)
            self.pipeline.add(self.video_sink)
            
            # Link final elements
            convert.link(self.video_sink)
            
            logger.info(f"Created video sink (window_id: {window_id})")
            
        except Exception as e:
            logger.error(f"Failed to create video sink: {e}")
            raise
    
    def _link_elements(self) -> None:
        """Link all pipeline elements."""
        try:
            # Set pipeline to READY state to access pads
            self.pipeline.set_state(Gst.State.READY)
            
            # Link video sources to compositor
            for i, source in enumerate(self.video_sources):
                if i < 4:  # Only link first 4 sources
                    # Request sink pad from compositor
                    sink_pad = self.compositor.get_request_pad(f"sink_{i}")
                    if sink_pad is not None:
                        # Set compositor sink properties
                        try:
                            if i == 0:
                                sink_pad.set_property("xpos", 0)
                                sink_pad.set_property("ypos", 0)
                                sink_pad.set_property("width", self.video_width)
                                sink_pad.set_property("height", self.video_height)
                            elif i == 1:
                                sink_pad.set_property("xpos", self.video_width)
                                sink_pad.set_property("ypos", 0)
                                sink_pad.set_property("width", self.video_width)
                                sink_pad.set_property("height", self.video_height)
                            elif i == 2:
                                sink_pad.set_property("xpos", 0)
                                sink_pad.set_property("ypos", self.video_height)
                                sink_pad.set_property("width", self.video_width)
                                sink_pad.set_property("height", self.video_height)
                            elif i == 3:
                                sink_pad.set_property("xpos", self.video_width)
                                sink_pad.set_property("ypos", self.video_height)
                                sink_pad.set_property("width", self.video_width)
                                sink_pad.set_property("height", self.video_height)
                        except Exception as e:
                            logger.debug(f"Could not set compositor sink {i} properties: {e}")
                        
                        source_pad = source.get_static_pad("src")
                        if source_pad is not None:
                            source_pad.link(sink_pad)
                            logger.info(f"Linked video source {i} to compositor")
                        else:
                            logger.warning(f"No src pad found on source {i}")
                    else:
                        logger.warning(f"Could not request sink pad {i} from compositor")
            
            # Link compositor to final convert
            compositor_pad = self.compositor.get_static_pad("src")
            convert_pad = self.pipeline.get_by_name("final_convert").get_static_pad("sink")
            if compositor_pad is not None and convert_pad is not None:
                compositor_pad.link(convert_pad)
                logger.info("Linked compositor to final convert")
            else:
                logger.warning("Could not link compositor to final convert")
            
            # Set pipeline back to NULL state
            self.pipeline.set_state(Gst.State.NULL)
            
            logger.info("Pipeline elements linked successfully")
            
        except Exception as e:
            logger.error(f"Failed to link elements: {e}")
            raise
    
    def start_pipeline(self) -> bool:
        """
        Start the GStreamer pipeline.
        
        Returns:
            True if pipeline started successfully, False otherwise
        """
        try:
            if self.pipeline is None:
                logger.error("No pipeline created")
                return False
            
            # Set pipeline state to playing
            ret = self.pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                logger.error("Failed to start pipeline")
                return False
            
            self.running = True
            logger.info("GStreamer pipeline started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start pipeline: {e}")
            return False
    
    def stop_pipeline(self) -> None:
        """Stop the GStreamer pipeline."""
        try:
            if self.pipeline is not None:
                self.pipeline.set_state(Gst.State.NULL)
                self.running = False
                logger.info("GStreamer pipeline stopped")
        except Exception as e:
            logger.error(f"Failed to stop pipeline: {e}")
    
    def destroy_pipeline(self) -> None:
        """Destroy the GStreamer pipeline."""
        try:
            if self.pipeline is not None:
                self.stop_pipeline()
                self.pipeline = None
                self.video_sources = []
                self.compositor = None
                self.video_sink = None
                logger.info("GStreamer pipeline destroyed")
        except Exception as e:
            logger.error(f"Failed to destroy pipeline: {e}")
    
    def switch_view_mode(self, mode: ViewMode) -> bool:
        """
        Switch the view mode.
        
        Args:
            mode: New view mode
            
        Returns:
            True if mode switched successfully, False otherwise
        """
        try:
            if self.current_mode == mode:
                logger.info(f"Already in {mode.value} mode")
                return True
            
            logger.info(f"Switching from {self.current_mode.value} to {mode.value}")
            
            # For now, we'll recreate the pipeline with different configuration
            # In a more advanced implementation, we could dynamically reconfigure
            self.current_mode = mode
            
            # Stop current pipeline
            self.stop_pipeline()
            
            # Recreate pipeline with new mode
            window_id = self._get_current_window_id()
            if self.create_pipeline(window_id):
                return self.start_pipeline()
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to switch view mode: {e}")
            return False
    
    def _get_current_window_id(self) -> Optional[int]:
        """Get the current window ID from the video sink."""
        try:
            if self.video_sink is not None and hasattr(self.video_sink, 'get_property'):
                return self.video_sink.get_property("window-id")
        except Exception as e:
            logger.debug(f"Could not get window ID: {e}")
        return None
    
    def set_window_id(self, window_id: int) -> bool:
        """
        Set the window ID for the video sink.
        
        Args:
            window_id: X11 window ID
            
        Returns:
            True if window ID set successfully, False otherwise
        """
        try:
            if self.video_sink is not None and hasattr(self.video_sink, 'set_property'):
                self.video_sink.set_property("window-id", window_id)
                logger.info(f"Set window ID to {window_id}")
                return True
            else:
                logger.warning("Video sink does not support window-id property")
                return False
        except Exception as e:
            logger.error(f"Failed to set window ID: {e}")
            return False
    
    def get_pipeline_state(self) -> Optional[str]:
        """
        Get the current pipeline state.
        
        Returns:
            Pipeline state as string, or None if no pipeline
        """
        try:
            if self.pipeline is not None:
                state = self.pipeline.get_state(0)[1]
                return Gst.Element.state_get_name(state)
        except Exception as e:
            logger.error(f"Failed to get pipeline state: {e}")
        return None
    
    def is_running(self) -> bool:
        """
        Check if the pipeline is running.
        
        Returns:
            True if pipeline is running, False otherwise
        """
        return self.running and self.pipeline is not None
    
    def close(self) -> None:
        """Close the GStreamer manager and cleanup resources."""
        try:
            self.destroy_pipeline()
            logger.info("GStreamer manager closed")
        except Exception as e:
            logger.error(f"Error closing GStreamer manager: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()