"""
X11 GStreamer Viewer Package
Created by Ruliano Castian - From the streets to the code!

A Python application that creates and manages X11 windows
with integrated GStreamer 4-way video viewing capabilities.
"""

__version__ = "1.0.0"
__author__ = "Ruliano Castian"
__email__ = "ruliano@streets2code.dev"

from .core.x11_manager import X11WindowManager
from .core.gstreamer_manager import GStreamerManager
from .ui.main_window import MainWindow

__all__ = [
    "X11WindowManager",
    "GStreamerManager", 
    "MainWindow",
]