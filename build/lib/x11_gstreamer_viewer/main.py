#!/usr/bin/env python3
"""
X11 GStreamer Viewer - Main Entry Point
Created by Ruliano Castian - From the streets to the code!

Main application entry point that coordinates X11 window management
and GStreamer video pipeline.
"""

import sys
import argparse
import signal
import logging
from typing import Dict, Any

from .ui.main_window import MainWindow
from .utils.config import Config
from .utils.logger import setup_logging, get_logger

logger = get_logger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="X11 GStreamer Viewer - 4-Way Video Display",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run with default settings
  %(prog)s --width 1920 --height 1080  # Custom window size
  %(prog)s --log-level DEBUG         # Enable debug logging
  %(prog)s --config ~/my_config.json # Use custom config file

Controls:
  Escape/Q       Exit application
        """
    )
    
    # Window options
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=3840,
        help="Window width in pixels (default: 3840)"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=2160,
        help="Window height in pixels (default: 2160)"
    )
    parser.add_argument(
        "--x", "-x",
        type=int,
        default=0,
        help="Window X position (default: 0)"
    )
    parser.add_argument(
        "--y", "-y",
        type=int,
        default=0,
        help="Window Y position (default: 0)"
    )
    parser.add_argument(
        "--title", "-t",
        type=str,
        default="X11 GStreamer Viewer",
        help="Window title (default: 'X11 GStreamer Viewer')"
    )
    parser.add_argument(
        "--fullscreen", "-f",
        action="store_true",
        help="Start in fullscreen mode"
    )
    
    # Video options
    parser.add_argument(
        "--video-width",
        type=int,
        default=1920,
        help="Individual video width (default: 1920)"
    )
    parser.add_argument(
        "--video-height",
        type=int,
        default=1080,
        help="Individual video height (default: 1080)"
    )
    parser.add_argument(
        "--output-width",
        type=int,
        default=3840,
        help="Output video width (default: 3840)"
    )
    parser.add_argument(
        "--output-height",
        type=int,
        default=2160,
        help="Output video height (default: 2160)"
    )
    
    # Logging options
    parser.add_argument(
        "--log-level", "-l",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path (default: console only)"
    )
    parser.add_argument(
        "--no-console-log",
        action="store_true",
        help="Disable console logging"
    )
    
    # Configuration options
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Configuration file path"
    )
    parser.add_argument(
        "--save-config",
        action="store_true",
        help="Save current configuration and exit"
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show current configuration and exit"
    )
    
    # Other options
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="X11 GStreamer Viewer 1.0.0"
    )
    
    return parser.parse_args()


def setup_signal_handlers(main_window: MainWindow) -> None:
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        main_window.close()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main() -> int:
    """Main application entry point."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Load configuration
        config = Config(args.config)
        
        # Update configuration from arguments
        config.update_from_args(vars(args))
        
        # Validate configuration
        if not config.validate():
            print("Error: Invalid configuration")
            return 1
        
        # Handle special commands
        if args.save_config:
            config.save()
            print("Configuration saved")
            return 0
        
        if args.show_config:
            config.print_config()
            return 0
        
        # Set up logging
        setup_logging(
            level=config.logging.level,
            log_file=config.logging.file,
            console=config.logging.console
        )
        
        logger.info("Starting X11 GStreamer Viewer")
        logger.info(f"Version: 1.0.0")
        logger.info(f"Author: Ruliano Castian")
        
        # Print configuration
        logger.info("Configuration:")
        logger.info(f"  Window: {config.window.width}x{config.window.height} at ({config.window.x}, {config.window.y})")
        logger.info(f"  Video: {config.video.width}x{config.video.height}")
        logger.info(f"  Output: {config.video.output_width}x{config.video.output_height}")
        logger.info(f"  Devices: {config.get_video_devices()}")
        
        # Create main window
        main_window = MainWindow(
            width=config.window.width,
            height=config.window.height
        )
        
        # Set up signal handlers
        setup_signal_handlers(main_window)
        
        # Create window
        if not main_window.create_window(config.window.title):
            logger.error("Failed to create main window")
            return 1
        
        # Run main window
        main_window.run()
        
        logger.info("Application finished")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())