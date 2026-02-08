# x11-gstreamer-viewer Documentation Index

**Type:** Monolith Desktop Application
**Primary Language:** Python 3.8+
**Architecture:** Component-Based Architecture with Manager Pattern
**Last Updated:** 2026-02-08

## Project Overview

X11 GStreamer Viewer is a Python desktop application designed for capture card PCIe device integration, enabling 4-way video display from multiple video sources. The application creates X11 windows with embedded GStreamer video pipelines, providing a clean interface for viewing video feeds from capture cards, cameras, and other Video4Linux2 devices.

**Primary Use Cases:**
- **Capture Card Integration**: Display video from PCIe capture cards (e.g., for Deskflow with other computers)
- **Picture-in-Picture (PIP)**: Display multiple video sources simultaneously on a single monitor
- **Multi-Source Monitoring**: Monitor Apple TV, computer outputs, and other video sources in a unified interface
- **Hardware-Accelerated Video Display**: Smooth video rendering using X11 and GStreamer integration

## Quick Reference

- **Tech Stack:** Python 3.8+, X11, GStreamer 1.0+, python-xlib, PyGObject
- **Entry Point:** `x11_gstreamer_viewer/main.py` (also available as `x11-gstreamer-viewer` command)
- **Architecture Pattern:** Component-Based Architecture with Manager Pattern
- **Database:** N/A (no database)
- **Deployment:** Local desktop application

## Generated Documentation

### Core Documentation

- [Project Overview](./project-overview.md) - Executive summary and high-level architecture
- [Source Tree Analysis](./source-tree-analysis.md) - Annotated directory structure
- [Architecture](./architecture.md) - Detailed technical architecture
- [Development Guide](./development-guide.md) - Local setup and development workflow

### Component Documentation

**Core Components:**
- `x11_gstreamer_viewer/core/x11_manager.py` - X11 window management (428 lines)
- `x11_gstreamer_viewer/core/gstreamer_manager.py` - GStreamer pipeline management (654 lines)

**UI Components:**
- `x11_gstreamer_viewer/ui/main_window.py` - Main window coordinator (294 lines)

**Utility Components:**
- `x11_gstreamer_viewer/utils/config.py` - Configuration management (216 lines)
- `x11_gstreamer_viewer/utils/logger.py` - Logging setup (92 lines)

## Existing Documentation

- [README.md](../README.md) - User-facing documentation with installation and usage instructions
- [WORK_LOG.md](../WORK_LOG.md) - Development log and project history

## Getting Started

### Prerequisites

- **Python**: 3.8 or higher
- **GStreamer**: 1.0+ with Python bindings
- **X11**: X11 development libraries
- **Video4Linux2**: Camera/capture card support

### Setup

```bash
# Install system dependencies (Arch Linux)
sudo pacman -S gstreamer gst-plugins-base gst-plugins-good \
               gst-plugins-bad gst-plugins-ugly \
               python-gobject python-xlib v4l-utils

# Install Python dependencies
pip install -r requirements.txt

# Install application
pip install -e .
```

### Run Locally

```bash
# Run with default settings
x11-gstreamer-viewer

# Run with custom settings
x11-gstreamer-viewer --width 1920 --height 1080 --log-level DEBUG

# Or using Python module
python -m x11_gstreamer_viewer.main
```

### Run Tests

```bash
# Run all tests
pytest

# Run basic functionality tests
python test_basic.py

# Run with coverage
pytest --cov=x11_gstreamer_viewer
```

## For AI-Assisted Development

This documentation was generated specifically to enable AI agents to understand and extend this codebase.

### When Planning New Features:

**UI-only features:**
→ Reference: `architecture.md`, `source-tree-analysis.md` (UI components section)

**Core functionality features:**
→ Reference: `architecture.md`, `source-tree-analysis.md` (Core components section)

**Configuration features:**
→ Reference: `development-guide.md` (Configuration section), `architecture.md` (Config component)

**Video pipeline features:**
→ Reference: `architecture.md` (Video Pipeline Architecture section), `source-tree-analysis.md` (GStreamerManager)

**Window management features:**
→ Reference: `architecture.md` (X11WindowManager section), `source-tree-analysis.md` (X11Manager)

### Key Architecture Points:

1. **Component Structure**: Clean separation between core (X11/GStreamer), UI (MainWindow), and utilities (Config/Logger)
2. **Manager Pattern**: Each major subsystem managed by dedicated manager class
3. **Window Embedding**: Video embedded directly in X11 windows using window ID
4. **Video Pipeline**: 4-way compositor with FPS/latency monitoring
5. **Configuration**: JSON-based with command-line override support

### Common Development Patterns:

- **Adding video sources**: Modify `GStreamerManager.video_devices` and compositor configuration
- **Window modifications**: Edit `X11WindowManager` methods and event handlers
- **Configuration changes**: Update `Config` class and command-line arguments
- **New features**: Follow component structure (core → UI → main)

### Testing Strategy:

- Module-level tests for each component
- Integration tests for component interaction
- Basic functionality tests in `test_basic.py`
- Configuration tests in `tests/test_config.py`

### Performance Considerations:

- Uses `xvimagesink` for hardware acceleration (not `glimagesink`)
- Low latency configuration (VSYNC disabled, frame dropping enabled)
- Window ID set after pipeline starts (correct timing for embedding)

---

_Documentation generated by BMAD Method `document-project` workflow_
