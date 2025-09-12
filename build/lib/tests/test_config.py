#!/usr/bin/env python3
"""
Configuration Tests
Created by Ruliano Castian - From the streets to the code!
"""

import pytest
import tempfile
import os
from x11_gstreamer_viewer.utils.config import Config, VideoConfig, WindowConfig, LoggingConfig


class TestVideoConfig:
    """Test VideoConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = VideoConfig()
        assert config.width == 1920
        assert config.height == 1080
        assert config.output_width == 3840
        assert config.output_height == 2160
        assert config.devices == ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3"]
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = VideoConfig(
            width=1280,
            height=720,
            output_width=2560,
            output_height=1440,
            devices=["/dev/video0", "/dev/video1"]
        )
        assert config.width == 1280
        assert config.height == 720
        assert config.output_width == 2560
        assert config.output_height == 1440
        assert config.devices == ["/dev/video0", "/dev/video1"]


class TestWindowConfig:
    """Test WindowConfig class."""
    
    def test_default_values(self):
        """Test default window configuration values."""
        config = WindowConfig()
        assert config.width == 3840
        assert config.height == 2160
        assert config.x == 0
        assert config.y == 0
        assert config.title == "X11 GStreamer Viewer"
        assert config.fullscreen is False
    
    def test_custom_values(self):
        """Test custom window configuration values."""
        config = WindowConfig(
            width=1920,
            height=1080,
            x=100,
            y=100,
            title="Custom Title",
            fullscreen=True
        )
        assert config.width == 1920
        assert config.height == 1080
        assert config.x == 100
        assert config.y == 100
        assert config.title == "Custom Title"
        assert config.fullscreen is True


class TestLoggingConfig:
    """Test LoggingConfig class."""
    
    def test_default_values(self):
        """Test default logging configuration values."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert config.file is None
        assert config.console is True
    
    def test_custom_values(self):
        """Test custom logging configuration values."""
        config = LoggingConfig(
            level="DEBUG",
            format="%(levelname)s: %(message)s",
            file="/tmp/test.log",
            console=False
        )
        assert config.level == "DEBUG"
        assert config.format == "%(levelname)s: %(message)s"
        assert config.file == "/tmp/test.log"
        assert config.console is False


class TestConfig:
    """Test Config class."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = Config()
        assert isinstance(config.video, VideoConfig)
        assert isinstance(config.window, WindowConfig)
        assert isinstance(config.logging, LoggingConfig)
    
    def test_config_file_loading(self):
        """Test loading configuration from file."""
        # Create temporary config file
        config_data = {
            "video": {
                "width": 1280,
                "height": 720,
                "output_width": 2560,
                "output_height": 1440,
                "devices": ["/dev/video0", "/dev/video1"]
            },
            "window": {
                "width": 1920,
                "height": 1080,
                "x": 100,
                "y": 100,
                "title": "Test Window",
                "fullscreen": False
            },
            "logging": {
                "level": "DEBUG",
                "format": "%(levelname)s: %(message)s",
                "file": "/tmp/test.log",
                "console": True
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            config = Config(config_file)
            assert config.video.width == 1280
            assert config.video.height == 720
            assert config.window.width == 1920
            assert config.window.height == 1080
            assert config.logging.level == "DEBUG"
        finally:
            os.unlink(config_file)
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        
        # Valid configuration should pass
        assert config.validate() is True
        
        # Invalid video dimensions should fail
        config.video.width = -1
        assert config.validate() is False
        
        # Reset and test invalid window dimensions
        config.video.width = 1920
        config.window.height = -1
        assert config.validate() is False
    
    def test_get_video_devices(self):
        """Test getting available video devices."""
        config = Config()
        devices = config.get_video_devices()
        
        # Should return a list
        assert isinstance(devices, list)
        
        # Should not contain non-existent devices
        for device in devices:
            assert device.startswith("/dev/video")
    
    def test_update_from_args(self):
        """Test updating configuration from arguments."""
        config = Config()
        
        args = {
            "video_width": 1280,
            "video_height": 720,
            "window_width": 1920,
            "window_height": 1080,
            "title": "Custom Title",
            "log_level": "DEBUG"
        }
        
        config.update_from_args(args)
        
        assert config.video.width == 1280
        assert config.video.height == 720
        assert config.window.width == 1920
        assert config.window.height == 1080
        assert config.window.title == "Custom Title"
        assert config.logging.level == "DEBUG"