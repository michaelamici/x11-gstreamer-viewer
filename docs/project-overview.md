# x11-gstreamer-viewer - Project Overview

**Date:** 2026-02-08
**Type:** Desktop Application
**Architecture:** Component-Based Desktop Application

## Executive Summary

X11 GStreamer Viewer is a Python desktop application designed for capture card PCIe device integration, enabling 4-way video display from multiple video sources. The application creates X11 windows with embedded GStreamer video pipelines, providing a clean interface for viewing video feeds from capture cards, cameras, and other Video4Linux2 devices.

**Primary Use Cases:**
- **Capture Card Integration**: Display video from PCIe capture cards (e.g., for Deskflow with other computers)
- **Picture-in-Picture (PIP)**: Display multiple video sources simultaneously on a single monitor
- **Multi-Source Monitoring**: Monitor Apple TV, computer outputs, and other video sources in a unified interface
- **Hardware-Accelerated Video Display**: Smooth video rendering using X11 and GStreamer integration

## Project Classification

- **Repository Type:** Monolith
- **Project Type(s):** Desktop Application
- **Primary Language(s):** Python 3.8+
- **Architecture Pattern:** Component-Based Architecture with Manager Pattern

## Technology Stack Summary

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| **Language** | Python | 3.8+ | Core application language |
| **Window System** | X11 | - | Native Linux window management |
| **Multimedia** | GStreamer | 1.0+ | Video pipeline and compositing |
| **X11 Bindings** | python-xlib | >=0.33 | X11 window creation and event handling |
| **GStreamer Bindings** | PyGObject | >=3.44.0 | GStreamer Python integration |
| **Video Input** | Video4Linux2 | - | Camera and capture card support |
| **Configuration** | JSON | - | Configuration file format |
| **Testing** | pytest | >=7.0.0 | Unit and integration testing |
| **Code Quality** | black, flake8 | - | Code formatting and linting |

## Key Features

### Core Functionality
- **4-Way Video Display**: Simultaneous display of 4 video sources in a 2x2 grid layout
- **X11 Window Management**: Native X11 window creation with proper event handling
- **GStreamer Pipeline**: Hardware-accelerated video compositing and rendering
- **Video Source Switching**: Cycle through individual camera views or display all simultaneously
- **FPS and Latency Monitoring**: Real-time performance metrics overlay (on mouse hover)
- **Low-Latency Configuration**: Optimized for real-time video display

### Hardware Integration
- **Capture Card Support**: PCIe capture card integration via Video4Linux2
- **Multi-Device Support**: Configurable video device paths (/dev/video0-3)
- **Hardware Acceleration**: Uses xvimagesink for GPU-accelerated video rendering
- **Window Embedding**: Direct video rendering into X11 windows (no separate video window)

### User Interface
- **Keyboard Controls**: Escape/Q to exit application
- **Mouse Interaction**: Click to cycle through views, mouse hover shows FPS overlay
- **Window Manager Integration**: Proper X11 window manager protocol support
- **Configurable Window Size**: Supports custom window dimensions and positioning

## Architecture Highlights

### Component Architecture
The application follows a clean component-based architecture:

1. **X11WindowManager**: Handles X11 window creation, event processing, and window lifecycle
2. **GStreamerManager**: Manages GStreamer pipeline creation, video sources, and compositing
3. **MainWindow**: Coordinates between X11 and GStreamer components
4. **Config**: JSON-based configuration management
5. **Logger**: Comprehensive logging system

### Video Pipeline Architecture
```
4x Video Sources (v4l2src) 
  → videoconvert 
  → videoscale 
  → caps filter 
  → textoverlay (FPS display)
  → compositor (2x2 grid)
  → videoconvert
  → xvimagesink (embedded in X11 window)
```

### Key Technical Achievements
- **Window Embedding**: Successfully embeds GStreamer video directly into X11 windows
- **Performance Optimization**: Uses xvimagesink instead of glimagesink for smooth performance
- **Low Latency**: Configured for real-time video display with minimal buffering
- **FPS Monitoring**: Real-time frame rate and latency measurement per camera

## Development Overview

### Prerequisites

- **Python**: 3.8 or higher
- **GStreamer**: 1.0+ with Python bindings
- **X11**: X11 development libraries
- **Video4Linux2**: Camera/capture card support
- **System Packages** (Arch Linux):
  - `gstreamer`, `gst-plugins-base`, `gst-plugins-good`, `gst-plugins-bad`, `gst-plugins-ugly`
  - `python-gobject`, `python-xlib`
  - `v4l-utils`

### Getting Started

1. **Install System Dependencies**:
   ```bash
   sudo pacman -S gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly
   sudo pacman -S python-gobject python-xlib v4l-utils
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Application**:
   ```bash
   pip install -e .
   ```

4. **Run Application**:
   ```bash
   x11-gstreamer-viewer
   # Or with custom settings:
   x11-gstreamer-viewer --width 1920 --height 1080
   ```

### Key Commands

- **Install:** `pip install -e .`
- **Dev:** `python -m x11_gstreamer_viewer.main`
- **Build:** `python setup.py build`
- **Test:** `pytest` or `python test_basic.py`

## Repository Structure

```
x11-gstreamer-viewer/
├── x11_gstreamer_viewer/          # Main package
│   ├── core/                      # Core functionality
│   │   ├── x11_manager.py         # X11 window management
│   │   └── gstreamer_manager.py   # GStreamer pipeline
│   ├── ui/                        # User interface
│   │   └── main_window.py         # Main application window
│   ├── utils/                     # Utilities
│   │   ├── config.py             # Configuration management
│   │   └── logger.py             # Logging setup
│   ├── main.py                    # Application entry point
│   └── __init__.py
├── tests/                         # Test modules
│   ├── test_config.py            # Configuration tests
│   └── __init__.py
├── docs/                          # Project documentation
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
├── test_basic.py                  # Basic functionality tests
├── demo.py                        # Demo script
├── README.md                      # User documentation
└── WORK_LOG.md                    # Development log
```

## Documentation Map

For detailed information, see:

- [index.md](./index.md) - Master documentation index
- [architecture.md](./architecture.md) - Detailed architecture
- [source-tree-analysis.md](./source-tree-analysis.md) - Directory structure
- [development-guide.md](./development-guide.md) - Development workflow

---

_Generated using BMAD Method `document-project` workflow_
