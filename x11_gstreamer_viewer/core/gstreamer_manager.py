#!/usr/bin/env python3
"""
GStreamer Manager
Created by Ruliano Castian - From the streets to the code!

Manages GStreamer pipeline for 4-way video viewing.
"""

import logging
import gi
from typing import Optional, List

# GStreamer imports
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GstVideo

logger = logging.getLogger(__name__)


class GStreamerManager:
    """
    Manages GStreamer pipeline for 4-way video viewing.
    
    Simple and clean implementation following KISS principle.
    """
    
    def __init__(self):
        """Initialize the GStreamer Manager."""
        self.pipeline: Optional[Gst.Pipeline] = None
        self.running = False
        
        # Video configuration
        self.video_width = 1920
        self.video_height = 1080
        
        # Video devices
        self.video_devices = ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3"]
        
        # View state tracking (-1 = tiled, 0-3 = single camera)
        self.current_view = -1
        self.compositor_sink_pads: List[Gst.Pad] = []
        
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
            
            # Reset view state
            self.current_view = -1
            self.compositor_sink_pads = []
            
            # Create pipeline
            self.pipeline = Gst.Pipeline.new("video-viewer-pipeline")
            
            # Create compositor
            compositor = Gst.ElementFactory.make("compositor", "comp")
            if compositor is None:
                raise Exception("Could not create compositor")
            
            # Create video sink
            sink = self._create_video_sink(window_id)
            
            # Add elements to pipeline
            self.pipeline.add(compositor)
            self.pipeline.add(sink)
            
            # Create video sources and link them
            self._create_and_link_sources(compositor)
            
            # Add explicit caps after compositor for better format negotiation
            output_caps = Gst.ElementFactory.make("capsfilter", "output_caps")
            if output_caps is not None:
                # Compositor output is 2x2 grid: width*2 x height*2
                output_width = self.video_width * 2
                output_height = self.video_height * 2
                caps_str = f"video/x-raw,width={output_width},height={output_height},framerate=30/1"
                output_caps.set_property("caps", Gst.caps_from_string(caps_str))
                self.pipeline.add(output_caps)
                # Link: compositor -> output_caps -> convert -> sink
                compositor.link(output_caps)
                output_caps.link(sink)
                logger.debug(f"Added explicit output caps: {output_width}x{output_height}")
            else:
                # Fallback: link compositor directly to sink
                compositor.link(sink)
                logger.debug("Could not create output caps filter, linking compositor directly")
            
            
            logger.info("GStreamer pipeline created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create pipeline: {e}")
            return False
    
    def _create_and_link_sources(self, compositor: Gst.Element) -> None:
        """Create video sources and link them to compositor."""
        for i, device in enumerate(self.video_devices):
            try:
                # Create source elements
                src = Gst.ElementFactory.make("v4l2src", f"src_{i}")
                convert = Gst.ElementFactory.make("videoconvert", f"convert_{i}")
                scale = Gst.ElementFactory.make("videoscale", f"scale_{i}")
                caps = Gst.ElementFactory.make("capsfilter", f"caps_{i}")
                
                if not all([src, convert, scale, caps]):
                    logger.warning(f"Could not create elements for device {device}")
                    continue
                
                # Set properties
                src.set_property("device", device)
                # Configure v4l2src for low latency
                try:
                    src.set_property("do-timestamp", True)  # Use timestamps from device
                    logger.debug(f"Configured v4l2src {i} for low latency")
                except Exception as e:
                    logger.debug(f"Could not set do-timestamp on v4l2src {i}: {e}")
                
                # Add framerate to caps for better format negotiation
                caps_str = f"video/x-raw,width={self.video_width},height={self.video_height},framerate=30/1"
                caps.set_property("caps", Gst.caps_from_string(caps_str))
                
                # Add to pipeline
                for element in [src, convert, scale, caps]:
                    self.pipeline.add(element)
                
                # Link elements
                src.link(convert)
                convert.link(scale)
                scale.link(caps)
                
                # Link to compositor sink
                sink_pad = compositor.get_request_pad(f"sink_{i}")
                if sink_pad:
                    caps_pad = caps.get_static_pad("src")
                    if caps_pad:
                        caps_pad.link(sink_pad)
                        # Set compositor sink properties
                        self._set_compositor_sink_properties(sink_pad, i)
                        # Store sink pad for view switching
                        self.compositor_sink_pads.append(sink_pad)
                        logger.info(f"Created and linked video source {i} for device {device}")
                
            except Exception as e:
                logger.error(f"Failed to create video source {i}: {e}")
    
    def _set_compositor_sink_properties(self, sink_pad: Gst.Pad, index: int) -> None:
        """Set compositor sink properties for positioning."""
        try:
            if index == 0:
                sink_pad.set_property("xpos", 0)
                sink_pad.set_property("ypos", 0)
            elif index == 1:
                sink_pad.set_property("xpos", self.video_width)
                sink_pad.set_property("ypos", 0)
            elif index == 2:
                sink_pad.set_property("xpos", 0)
                sink_pad.set_property("ypos", self.video_height)
            elif index == 3:
                sink_pad.set_property("xpos", self.video_width)
                sink_pad.set_property("ypos", self.video_height)
            
            sink_pad.set_property("width", self.video_width)
            sink_pad.set_property("height", self.video_height)
            sink_pad.set_property("alpha", 1.0)
        except Exception as e:
            logger.debug(f"Could not set compositor sink {index} properties: {e}")
    
    def cycle_view(self) -> None:
        """Cycle through views: Tiled ? Camera 0 ? Camera 1 ? Camera 2 ? Camera 3 ? Tiled."""
        try:
            if not self.compositor_sink_pads:
                logger.warning("No compositor sink pads available for view switching")
                return
            
            output_width = self.video_width * 2
            output_height = self.video_height * 2
            
            self.current_view += 1
            if self.current_view > 3:
                self.current_view = -1
            
            if self.current_view == -1:
                self._set_tiled_view(output_width, output_height)
                logger.info("Switched to tiled view (4-way split)")
            else:
                self._set_single_camera_view(self.current_view, output_width, output_height)
                logger.info(f"Switched to single camera view: Camera {self.current_view}")
        except Exception as e:
            logger.error(f"Failed to cycle view: {e}")

    def _set_tiled_view(self, output_width: int, output_height: int) -> None:
        """Set compositor to show all cameras in tiled (2x2) view."""
        try:
            for i, sink_pad in enumerate(self.compositor_sink_pads):
                if i == 0:
                    sink_pad.set_property("xpos", 0)
                    sink_pad.set_property("ypos", 0)
                elif i == 1:
                    sink_pad.set_property("xpos", self.video_width)
                    sink_pad.set_property("ypos", 0)
                elif i == 2:
                    sink_pad.set_property("xpos", 0)
                    sink_pad.set_property("ypos", self.video_height)
                elif i == 3:
                    sink_pad.set_property("xpos", self.video_width)
                    sink_pad.set_property("ypos", self.video_height)
                
                sink_pad.set_property("width", self.video_width)
                sink_pad.set_property("height", self.video_height)
                sink_pad.set_property("alpha", 1.0)
        except Exception as e:
            logger.error(f"Failed to set tiled view: {e}")

    def _set_single_camera_view(self, camera_index: int, output_width: int, output_height: int) -> None:
        """Set compositor to show single camera fullscreen."""
        try:
            for i, sink_pad in enumerate(self.compositor_sink_pads):
                if i == camera_index:
                    sink_pad.set_property("xpos", 0)
                    sink_pad.set_property("ypos", 0)
                    sink_pad.set_property("width", output_width)
                    sink_pad.set_property("height", output_height)
                    sink_pad.set_property("alpha", 1.0)
                else:
                    sink_pad.set_property("alpha", 0.0)
        except Exception as e:
            logger.error(f"Failed to set single camera view: {e}")
    
    def _create_video_sink(self, window_id: Optional[int] = None) -> Gst.Element:
        """Create the video sink element."""
        try:
            # Create videoconvert for final output
            convert = Gst.ElementFactory.make("videoconvert", "final_convert")
            if convert is None:
                raise Exception("Could not create videoconvert")
            
            # Create X11 video sink (xvimagesink for best performance)
            sink = Gst.ElementFactory.make("xvimagesink", "video_sink")
            if sink is None:
                # Fallback to ximagesink
                sink = Gst.ElementFactory.make("ximagesink", "video_sink")
                if sink is None:
                    raise Exception("Could not create any X11 video sink")
                logger.info("Created ximagesink for window embedding")
            else:
                logger.info("Created xvimagesink for window embedding")
            
            # Configure sink for low latency
            try:
                # Disable sync to clock for real-time display (reduces buffering)
                sink.set_property("sync", False)
                # Drop late frames instead of queuing them
                sink.set_property("max-lateness", -1)
                sink.set_property("drop-on-lateness", True)
                logger.debug("Configured sink for low latency")
            except Exception as e:
                logger.debug(f"Could not set all latency properties: {e}")
            
            # Store window ID for later setting
            self.window_id = window_id
            
            # Add to pipeline and link
            self.pipeline.add(convert)
            self.pipeline.add(sink)
            convert.link(sink)
            
            logger.info(f"Created video sink (window_id: {window_id})")
            return convert
            
        except Exception as e:
            logger.error(f"Failed to create video sink: {e}")
            raise
    
    
    def start_pipeline(self) -> bool:
        """Start the GStreamer pipeline."""
        try:
            if self.pipeline is None:
                logger.error("No pipeline created")
                return False
            
            ret = self.pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                logger.error("Failed to start pipeline")
                return False
            
            # Set window ID after pipeline starts playing (correct way for X11 embedding)
            if hasattr(self, 'window_id') and self.window_id is not None:
                self._set_window_id_after_start()
            
            self.running = True
            logger.info("GStreamer pipeline started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start pipeline: {e}")
            return False
    
    def _set_window_id_after_start(self) -> None:
        """Set window ID after pipeline starts playing."""
        try:
            sink_element = self.pipeline.get_by_name("video_sink")
            if sink_element is None:
                logger.warning("Could not find video sink element")
                return
            
            # Use VideoOverlay interface (standard way for X11 embedding)
            try:
                # Try to use VideoOverlay interface (xvimagesink implements this)
                overlay = GstVideo.VideoOverlay.cast(sink_element)
                overlay.set_window_handle(self.window_id)
                logger.info(f"Set window handle to {self.window_id} using VideoOverlay interface")
                return
            except (AttributeError, TypeError, Exception) as e:
                logger.debug(f"Could not use VideoOverlay interface: {e}")
            
            # Fallback: Try direct method call (some sinks implement this directly)
            try:
                if hasattr(sink_element, 'set_window_handle'):
                    sink_element.set_window_handle(self.window_id)
                    logger.info(f"Set window handle to {self.window_id} using direct method")
                    return
            except Exception as e:
                logger.debug(f"Could not set window handle directly: {e}")
            
            # Fallback: Property setting
            window_properties = ["window-id", "xid", "xwindow-id", "window"]
            for prop_name in window_properties:
                try:
                    sink_element.set_property(prop_name, self.window_id)
                    logger.info(f"Set {prop_name} to {self.window_id}")
                    return
                except Exception as e:
                    logger.debug(f"Could not set {prop_name}: {e}")
                    continue
            
            logger.warning("Could not set window ID for embedding")
                
        except Exception as e:
            logger.error(f"Failed to set window ID: {e}")
    
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
                logger.info("GStreamer pipeline destroyed")
        except Exception as e:
            logger.error(f"Failed to destroy pipeline: {e}")
    
    def get_pipeline_state(self) -> Optional[str]:
        """Get the current pipeline state."""
        try:
            if self.pipeline is not None:
                state = self.pipeline.get_state(0)[1]
                return Gst.Element.state_get_name(state)
        except Exception as e:
            logger.error(f"Failed to get pipeline state: {e}")
        return None
    
    def is_running(self) -> bool:
        """Check if the pipeline is running."""
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