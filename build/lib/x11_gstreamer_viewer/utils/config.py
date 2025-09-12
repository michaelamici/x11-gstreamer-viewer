#!/usr/bin/env python3
"""
Configuration Management
Created by Ruliano Castian - From the streets to the code!

Handles application configuration and settings.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class VideoConfig:
    """Video configuration settings."""
    width: int = 1920
    height: int = 1080
    output_width: int = 3840
    output_height: int = 2160
    devices: list = None
    
    def __post_init__(self):
        if self.devices is None:
            self.devices = ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3"]


@dataclass
class WindowConfig:
    """Window configuration settings."""
    width: int = 3840
    height: int = 2160
    x: int = 0
    y: int = 0
    title: str = "X11 GStreamer Viewer"
    fullscreen: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    console: bool = True


class Config:
    """
    Application configuration manager.
    
    Handles loading, saving, and managing application configuration
    from various sources (file, environment, defaults).
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or os.path.expanduser("~/.config/x11-gstreamer-viewer/config.json")
        
        # Default configuration
        self.video = VideoConfig()
        self.window = WindowConfig()
        self.logging = LoggingConfig()
        
        # Load configuration
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                # Update configurations
                if 'video' in data:
                    self.video = VideoConfig(**data['video'])
                
                if 'window' in data:
                    self.window = WindowConfig(**data['window'])
                
                if 'logging' in data:
                    self.logging = LoggingConfig(**data['logging'])
                
                print(f"Configuration loaded from {self.config_file}")
            else:
                print(f"Configuration file not found, using defaults")
                
        except Exception as e:
            print(f"Error loading configuration: {e}")
            print("Using default configuration")
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Prepare data
            data = {
                'video': asdict(self.video),
                'window': asdict(self.window),
                'logging': asdict(self.logging),
            }
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def get_video_devices(self) -> list:
        """
        Get available video devices.
        
        Returns:
            List of available video device paths
        """
        available_devices = []
        
        for device in self.video.devices:
            if os.path.exists(device):
                available_devices.append(device)
        
        return available_devices
    
    def update_from_args(self, args: Dict[str, Any]) -> None:
        """
        Update configuration from command line arguments.
        
        Args:
            args: Dictionary of command line arguments
        """
        # Update video config
        if 'video_width' in args:
            self.video.width = args['video_width']
        if 'video_height' in args:
            self.video.height = args['video_height']
        if 'output_width' in args:
            self.video.output_width = args['output_width']
        if 'output_height' in args:
            self.video.output_height = args['output_height']
        
        # Update window config
        if 'window_width' in args:
            self.window.width = args['window_width']
        if 'window_height' in args:
            self.window.height = args['window_height']
        if 'window_x' in args:
            self.window.x = args['window_x']
        if 'window_y' in args:
            self.window.y = args['window_y']
        if 'title' in args:
            self.window.title = args['title']
        if 'fullscreen' in args:
            self.window.fullscreen = args['fullscreen']
        
        # Update logging config
        if 'log_level' in args:
            self.logging.level = args['log_level']
        if 'log_file' in args:
            self.logging.file = args['log_file']
        if 'no_console_log' in args:
            self.logging.console = not args['no_console_log']
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate video configuration
            if self.video.width <= 0 or self.video.height <= 0:
                print("Error: Invalid video dimensions")
                return False
            
            if self.video.output_width <= 0 or self.video.output_height <= 0:
                print("Error: Invalid output dimensions")
                return False
            
            # Validate window configuration
            if self.window.width <= 0 or self.window.height <= 0:
                print("Error: Invalid window dimensions")
                return False
            
            # Validate logging configuration
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.logging.level.upper() not in valid_levels:
                print(f"Error: Invalid log level '{self.logging.level}'")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validating configuration: {e}")
            return False
    
    def print_config(self) -> None:
        """Print current configuration."""
        print("Current Configuration:")
        print("====================")
        print(f"Video: {asdict(self.video)}")
        print(f"Window: {asdict(self.window)}")
        print(f"Logging: {asdict(self.logging)}")
        print(f"Available devices: {self.get_video_devices()}")