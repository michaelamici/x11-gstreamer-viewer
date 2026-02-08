# x11-gstreamer-viewer - Architecture Documentation

**Date:** 2026-02-08
**Project Type:** Desktop Application
**Architecture Pattern:** Component-Based Architecture with Manager Pattern

## Executive Summary

X11 GStreamer Viewer is a Python desktop application that integrates X11 window management with GStreamer video pipelines to provide a 4-way video display interface. The application is designed for capture card PCIe device integration, enabling users to view multiple video sources simultaneously on a single monitor.

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.8+ | Application language |
| **Window System** | X11 | - | Native Linux window management |
| **Multimedia Framework** | GStreamer | 1.0+ | Video pipeline and compositing |
| **X11 Bindings** | python-xlib | >=0.33 | X11 API access |
| **GStreamer Bindings** | PyGObject | >=3.44.0 | GStreamer Python integration |
| **Video Input** | Video4Linux2 | - | Camera/capture card support |

### Development Tools

- **Testing:** pytest >=7.0.0
- **Code Formatting:** black >=22.0.0
- **Linting:** flake8 >=4.0.0

## Architecture Pattern

### Component-Based Architecture

The application follows a component-based architecture with clear separation of concerns:

1. **Core Components**: Low-level system integration (X11, GStreamer)
2. **UI Components**: High-level coordination and user interface
3. **Utility Components**: Shared services (configuration, logging)

### Manager Pattern

Each major subsystem is managed by a dedicated manager class:
- `X11WindowManager`: Manages X11 windows and events
- `GStreamerManager`: Manages GStreamer pipelines and video sources
- `MainWindow`: Coordinates between managers

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Main Application                     │
│                  (main.py)                              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌─────────▼──────────┐
│  MainWindow    │      │      Config        │
│  (Coordinator) │      │   (Configuration) │
└───────┬────────┘      └───────────────────┘
        │
   ┌────┴────┐
   │         │
┌──▼───┐  ┌─▼──────────┐
│ X11  │  │ GStreamer  │
│ Mgr  │  │    Mgr     │
└──────┘  └────────────┘
```

### Component Responsibilities

#### MainWindow (`ui/main_window.py`)
- Coordinates X11 and GStreamer components
- Handles application lifecycle (start, stop, run)
- Manages event routing between components
- Provides unified application interface

#### X11WindowManager (`core/x11_manager.py`)
- Creates and manages X11 windows
- Handles X11 events (keyboard, mouse, window events)
- Provides window ID for GStreamer embedding
- Manages window properties and state

#### GStreamerManager (`core/gstreamer_manager.py`)
- Creates and manages GStreamer pipelines
- Handles video source creation and linking
- Manages video compositing (2x2 grid layout)
- Provides FPS and latency monitoring
- Handles view switching (tiled vs single camera)

#### Config (`utils/config.py`)
- Loads configuration from JSON files
- Merges command-line arguments with file config
- Validates configuration values
- Provides default values

#### Logger (`utils/logger.py`)
- Sets up logging configuration
- Configures log levels and handlers
- Provides module-specific loggers

## Data Architecture

### Video Pipeline Architecture

```
┌─────────────┐
│ Video Source│
│  (v4l2src)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│videoconvert │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ videoscale  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ caps filter │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│textoverlay  │─────▶│  compositor  │
│ (FPS/Lat)   │      │  (2x2 grid)   │
└─────────────┘      └──────┬───────┘
                            │
                            ▼
                    ┌──────────────┐
                    │videoconvert  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ xvimagesink  │
                    │ (X11 window) │
                    └──────────────┘
```

### Pipeline Details

**Video Sources:**
- 4x `v4l2src` elements (one per video device: /dev/video0-3)
- Each source configured for low latency (`do-timestamp=True`)

**Processing Chain:**
- `videoconvert`: Format conversion
- `videoscale`: Scaling to target resolution (1920x1080 per source)
- `capsfilter`: Format negotiation and framerate control (30fps)
- `textoverlay`: FPS and latency display overlay

**Compositing:**
- `compositor`: 2x2 grid layout
  - Top-left (sink_0): Camera 0 at (0, 0)
  - Top-right (sink_1): Camera 1 at (1920, 0)
  - Bottom-left (sink_2): Camera 2 at (0, 1080)
  - Bottom-right (sink_3): Camera 3 at (1920, 1080)

**Output:**
- Final `videoconvert`: Final format conversion
- `xvimagesink`: Hardware-accelerated X11 video sink
  - Embedded directly in X11 window
  - Configured for low latency (sync=False, drop-on-lateness=True)

## Component Design

### X11WindowManager

**Responsibilities:**
- X11 display connection management
- Window creation and destruction
- Event handling (keyboard, mouse, window events)
- Window property management
- Graphics context management

**Key Methods:**
- `create_window()`: Creates X11 window with specified properties
- `get_window_id()`: Returns window ID for GStreamer embedding
- `handle_events()`: Processes X11 events
- `run_event_loop()`: Main event loop

**State Management:**
- Window state (created/destroyed)
- Event handlers registry
- Running state for event loop

### GStreamerManager

**Responsibilities:**
- GStreamer pipeline creation and management
- Video source creation and linking
- Compositor configuration
- View switching (tiled vs single camera)
- FPS and latency monitoring
- Window embedding

**Key Methods:**
- `create_pipeline()`: Creates GStreamer pipeline
- `start_pipeline()`: Starts pipeline playback
- `cycle_view()`: Switches between tiled and single camera views
- `_set_window_id_after_start()`: Embeds video in X11 window

**State Management:**
- Pipeline state (created/running/stopped)
- Current view mode (-1 = tiled, 0-3 = single camera)
- FPS and latency tracking per camera
- FPS overlay visibility state

### MainWindow

**Responsibilities:**
- Coordinates X11 and GStreamer managers
- Handles application lifecycle
- Routes events between components
- Validates window size matches compositor output

**Key Methods:**
- `create_window()`: Creates X11 window and GStreamer pipeline
- `start()`: Starts video pipeline
- `run()`: Main application loop
- `close()`: Cleanup and resource management

**State Management:**
- Running state
- Component initialization state
- Event handler registry

## Integration Points

### X11 ↔ GStreamer Integration

**Window Embedding:**
1. X11WindowManager creates X11 window
2. Window ID retrieved via `get_window_id()`
3. Window ID passed to GStreamerManager
4. GStreamerManager sets window ID on video sink after pipeline starts
5. Video renders directly into X11 window

**Event Flow:**
- X11 events → MainWindow → GStreamerManager (for view switching)
- Mouse activity → GStreamerManager (for FPS overlay visibility)

### Configuration Integration

**Config Flow:**
1. Config loads from JSON file or uses defaults
2. Command-line arguments override file config
3. Config values passed to MainWindow
4. MainWindow passes values to X11WindowManager and GStreamerManager

## Source Tree

### Critical Folders

**`x11_gstreamer_viewer/core/`**
- Core functionality modules
- Low-level system integration
- No UI dependencies

**`x11_gstreamer_viewer/ui/`**
- User interface coordination
- Depends on core modules

**`x11_gstreamer_viewer/utils/`**
- Shared utilities
- Used by all modules

## Development Workflow

### Prerequisites
- Python 3.8+
- GStreamer 1.0+ with Python bindings
- X11 development libraries
- Video4Linux2 support

### Setup
```bash
# Install system dependencies
sudo pacman -S gstreamer gst-plugins-base gst-plugins-good \
               gst-plugins-bad gst-plugins-ugly python-gobject \
               python-xlib v4l-utils

# Install Python dependencies
pip install -r requirements.txt

# Install application
pip install -e .
```

### Running
```bash
# Run with defaults
x11-gstreamer-viewer

# Run with custom settings
x11-gstreamer-viewer --width 1920 --height 1080 --log-level DEBUG
```

### Testing
```bash
# Run all tests
pytest

# Run basic tests
python test_basic.py
```

## Deployment Architecture

### Local Deployment
- Application runs as standalone Python application
- Requires X11 display server
- Requires GStreamer runtime
- Requires video device access (/dev/video*)

### Configuration
- User configuration: `~/.config/x11-gstreamer-viewer/config.json`
- Command-line arguments override file config
- Default values provided for all options

## Testing Strategy

### Test Structure
- `test_basic.py`: Basic functionality tests
- `tests/test_config.py`: Configuration tests
- Module-level tests for core components

### Test Coverage
- Import tests
- X11 Manager tests
- GStreamer Manager tests
- Configuration tests
- Main Window tests

**Current Status:** 5/5 tests passing (100% pass rate)

## Performance Considerations

### Low Latency Configuration
- GStreamer sink configured with `sync=False` (VSYNC disabled)
- Frame dropping enabled (`drop-on-lateness=True`)
- Video sources use device timestamps (`do-timestamp=True`)

### Hardware Acceleration
- Uses `xvimagesink` for GPU-accelerated video rendering
- Avoids `glimagesink` (OpenGL-based, can cause stuttering)

### Window Embedding
- Window ID set after pipeline starts (correct timing)
- Direct X11 window embedding (no separate video window)

## Error Handling

### Error Handling Strategy
- Comprehensive logging throughout application
- Graceful degradation (fallback video sinks)
- Proper resource cleanup on errors
- Signal handlers for graceful shutdown

### Common Error Scenarios
- X11 connection failure → Log error and exit
- GStreamer initialization failure → Log error and exit
- Video device not found → Log warning, continue with available devices
- Window creation failure → Log error and exit

## Security Considerations

### Video Device Access
- Requires access to `/dev/video*` devices
- User should be in `video` group
- No network exposure (local application only)

### Configuration
- Configuration files stored in user home directory
- No sensitive data stored (only video device paths and window settings)

## Future Enhancements

### Potential Improvements
1. **Recording**: Add video recording capabilities
2. **Network Streaming**: Add network streaming support
3. **GUI Controls**: Add on-screen controls and status display
4. **Advanced Compositing**: Add more video effects
5. **Configuration UI**: Add graphical configuration interface

---

_Generated using BMAD Method `document-project` workflow_
