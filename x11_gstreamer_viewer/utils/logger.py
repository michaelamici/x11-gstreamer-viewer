#!/usr/bin/env python3
"""
Logging Configuration
Created by Ruliano Castian - From the streets to the code!

Sets up logging configuration for the application.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", 
                  format_str: Optional[str] = None,
                  log_file: Optional[str] = None,
                  console: bool = True) -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: Log format string
        log_file: Path to log file (optional)
        console: Enable console logging
    """
    # Default format
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Convert level string to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(format_str)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file handler: {e}")
    
    # Set up specific loggers
    _setup_module_loggers()
    
    logging.info(f"Logging configured - Level: {level}, File: {log_file or 'None'}")


def _setup_module_loggers() -> None:
    """Set up specific module loggers with appropriate levels."""
    # GStreamer logging
    gst_logger = logging.getLogger('gi.repository.Gst')
    gst_logger.setLevel(logging.WARNING)  # Reduce GStreamer noise
    
    # X11 logging
    x11_logger = logging.getLogger('Xlib')
    x11_logger.setLevel(logging.WARNING)  # Reduce X11 noise
    
    # Application logging
    app_logger = logging.getLogger('x11_gstreamer_viewer')
    app_logger.setLevel(logging.DEBUG)  # Full debug for our app


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)