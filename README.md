# X11 GStreamer Viewer

**Created by Ruliano Castian - From the streets to the code!**

A Python application that creates and manages X11 windows with integrated GStreamer 4-way video viewing capabilities. This project replicates the functionality of the running GStreamer pipeline while providing a clean Python interface for X11 window management.

## Features

- **X11 Window Management**: Create and manage X11 windows with proper event handling
- **GStreamer Integration**: 4-way video compositor with multiple camera inputs
- **Interactive Controls**: Mouse and keyboard controls for view switching
- **Configurable**: JSON-based configuration system
- **Cross-platform**: Designed for Linux with X11 support

## Architecture

The application consists of several key components:

- **X11WindowManager**: Handles X11 window creation, management, and event handling
- **GStreamerManager**: Manages the GStreamer pipeline for video processing
- **MainWindow**: Coordinates between X11 and GStreamer components
- **Config**: Configuration management system
- **Utils**: Logging and utility functions

## Installation

### Prerequisites

- Python 3.8+
- GStreamer 1.0+ with Python bindings
- X11 development libraries
- Video4Linux2 devices (for camera input)

### Dependencies

```bash
# Install system dependencies (Arch Linux)
sudo pacman -S gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly
sudo pacman -S python-gobject python-xlib
sudo pacman -S v4l-utils

# Install Python dependencies
pip install -r requirements.txt
```

### Build and Install

```bash
# Clone the repository
git clone <repository-url>
cd x11-gstreamer-viewer

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

## Usage

### Basic Usage

```bash
# Run with default settings
x11-gstreamer-viewer

# Run with custom window size
x11-gstreamer-viewer --width 1920 --height 1080

# Run with debug logging
x11-gstreamer-viewer --log-level DEBUG
```

### Command Line Options

```
--width, -w          Window width in pixels (default: 3840)
--height, -h         Window height in pixels (default: 2160)
--x, -x              Window X position (default: 0)
--y, -y              Window Y position (default: 0)
--title, -t          Window title (default: 'X11 GStreamer Viewer')
--fullscreen, -f     Start in fullscreen mode

--video-width        Individual video width (default: 1920)
--video-height       Individual video height (default: 1080)
--output-width        Output video width (default: 3840)
--output-height      Output video height (default: 2160)

--log-level, -l      Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
--log-file           Log file path (default: console only)
--no-console-log     Disable console logging

--config, -c         Configuration file path
--save-config         Save current configuration and exit
--show-config         Show current configuration and exit
```

### Controls

- **Left Click**: Switch to 4-way view
- **Middle Click**: Cycle through cameras
- **Right Click**: Exit application
- **Escape/Q**: Exit application
- **1-4**: Switch to specific camera
- **0**: Switch to 4-way view

## Configuration

The application uses a JSON-based configuration system. Configuration files are stored in `~/.config/x11-gstreamer-viewer/config.json`.

### Example Configuration

```json
{
  "video": {
    "width": 1920,
    "height": 1080,
    "output_width": 3840,
    "output_height": 2160,
    "devices": ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3"]
  },
  "window": {
    "width": 3840,
    "height": 2160,
    "x": 0,
    "y": 0,
    "title": "X11 GStreamer Viewer",
    "fullscreen": false
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": null,
    "console": true
  }
}
```

## Development

### Project Structure

```
x11-gstreamer-viewer/
├── x11_gstreamer_viewer/
│   ├── core/
│   │   ├── x11_manager.py      # X11 window management
│   │   └── gstreamer_manager.py # GStreamer pipeline management
│   ├── ui/
│   │   └── main_window.py      # Main application window
│   ├── utils/
│   │   ├── config.py           # Configuration management
│   │   └── logger.py           # Logging setup
│   ├── main.py                 # Main entry point
│   └── __init__.py
├── tests/                      # Test modules
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
└── README.md                   # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_config.py

# Run with coverage
pytest --cov=x11_gstreamer_viewer
```

### Code Style

The project follows Python best practices:

- **Black** for code formatting
- **Flake8** for linting
- **Type hints** for better code documentation
- **Docstrings** for all public methods

```bash
# Format code
black x11_gstreamer_viewer/

# Lint code
flake8 x11_gstreamer_viewer/
```

## GStreamer Pipeline

The application replicates the following GStreamer pipeline:

```bash
gst-launch-1.0 \
    v4l2src device=/dev/video0 ! videoconvert ! videoscale method=2 ! \
    video/x-raw,width=1920,height=1080 ! \
    compositor name=comp \
    sink_0::xpos=0 sink_0::ypos=0 sink_0::width=1920 sink_0::height=1080 \
    sink_1::xpos=1920 sink_1::ypos=0 sink_1::width=1920 sink_1::height=1080 \
    sink_2::xpos=0 sink_2::ypos=1080 sink_2::width=1920 sink_2::height=1080 \
    sink_3::xpos=1920 sink_3::ypos=1080 sink_3::width=1920 sink_3::height=1080 ! \
    videoconvert ! autovideosink \
    v4l2src device=/dev/video1 ! videoconvert ! videoscale method=2 ! \
    video/x-raw,width=1920,height=1080 ! comp.sink_1 \
    v4l2src device=/dev/video2 ! videoconvert ! videoscale method=2 ! \
    video/x-raw,width=1920,height=1080 ! comp.sink_2 \
    v4l2src device=/dev/video3 ! videoconvert ! videoscale method=2 ! \
    video/x-raw,width=1920,height=1080 ! comp.sink_3
```

## Troubleshooting

### Common Issues

1. **No video devices found**
   - Ensure video devices exist: `ls /dev/video*`
   - Check device permissions: `ls -la /dev/video*`

2. **GStreamer initialization failed**
   - Install GStreamer development packages
   - Check GStreamer installation: `gst-inspect-1.0`

3. **X11 connection failed**
   - Ensure X11 is running
   - Check DISPLAY environment variable: `echo $DISPLAY`

4. **Permission denied**
   - Add user to video group: `sudo usermod -a -G video $USER`
   - Logout and login again

### Debug Mode

Run with debug logging to get detailed information:

```bash
x11-gstreamer-viewer --log-level DEBUG --log-file debug.log
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Author

**Ruliano Castian** - *From the streets to the code!*

- Email: ruliano@streets2code.dev
- GitHub: [@ruliano-castian](https://github.com/ruliano-castian)

---

*"From the streets to the code - every line I write is a step toward a better future."* - Ruliano Castian