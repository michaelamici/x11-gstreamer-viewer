# x11-gstreamer-viewer - Development Guide

**Date:** 2026-02-08

## Prerequisites

### System Requirements

- **Operating System**: Linux with X11 support
- **Python**: 3.8 or higher
- **GStreamer**: 1.0+ with Python bindings
- **X11**: X11 development libraries
- **Video4Linux2**: Camera/capture card support

### System Dependencies (Arch Linux)

```bash
sudo pacman -S gstreamer gst-plugins-base gst-plugins-good \
               gst-plugins-bad gst-plugins-ugly \
               python-gobject python-xlib v4l-utils
```

### Python Dependencies

Install from `requirements.txt`:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install python-xlib>=0.33 PyGObject>=3.44.0
```

## Environment Setup

### Development Installation

Install the package in development mode:
```bash
pip install -e .
```

This allows you to edit the code and see changes immediately without reinstalling.

### Verify Installation

Check that the command-line tool is available:
```bash
which x11-gstreamer-viewer
x11-gstreamer-viewer --version
```

### Video Device Access

Ensure your user has access to video devices:
```bash
# Check available video devices
ls -la /dev/video*

# Add user to video group (if needed)
sudo usermod -a -G video $USER
# Logout and login again for changes to take effect
```

## Local Development

### Running the Application

**Basic usage:**
```bash
x11-gstreamer-viewer
```

**With custom settings:**
```bash
x11-gstreamer-viewer --width 1920 --height 1080 --log-level DEBUG
```

**Using Python module:**
```bash
python -m x11_gstreamer_viewer.main
```

**Using demo script:**
```bash
python demo.py
```

### Command Line Options

```
Window Options:
  --width, -w          Window width (default: 3840)
  --height, -h         Window height (default: 2160)
  --x, -x              Window X position (default: 0)
  --y, -y              Window Y position (default: 0)
  --title, -t          Window title
  --fullscreen, -f     Start in fullscreen mode

Video Options:
  --video-width        Individual video width (default: 1920)
  --video-height       Individual video height (default: 1080)
  --output-width       Output video width (default: 3840)
  --output-height      Output video height (default: 2160)

Logging Options:
  --log-level, -l      Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  --log-file           Log file path
  --no-console-log     Disable console logging

Configuration Options:
  --config, -c         Configuration file path
  --save-config         Save current configuration and exit
  --show-config         Show current configuration and exit
```

### Configuration

**Configuration File Location:**
`~/.config/x11-gstreamer-viewer/config.json`

**Example Configuration:**
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

**Save Configuration:**
```bash
x11-gstreamer-viewer --save-config
```

**Show Configuration:**
```bash
x11-gstreamer-viewer --show-config
```

## Build Process

### Building the Package

```bash
python setup.py build
```

### Installing the Package

**Development mode (editable):**
```bash
pip install -e .
```

**Production mode:**
```bash
pip install .
```

### Using Build Script

```bash
./build.sh
```

## Testing

### Running Tests

**Run all tests:**
```bash
pytest
```

**Run basic functionality tests:**
```bash
python test_basic.py
```

**Run specific test file:**
```bash
pytest tests/test_config.py
```

**Run with coverage:**
```bash
pytest --cov=x11_gstreamer_viewer
```

### Test Structure

- `test_basic.py`: Basic functionality tests
- `tests/test_config.py`: Configuration tests
- Module-level tests for core components

### Current Test Status

**Test Score:** 5/5 (100% pass rate)

- ✅ Import tests
- ✅ X11 Manager tests
- ✅ GStreamer Manager tests
- ✅ Configuration tests
- ✅ Main Window tests

## Code Style

### Formatting

The project uses **Black** for code formatting:
```bash
black x11_gstreamer_viewer/
```

### Linting

The project uses **Flake8** for linting:
```bash
flake8 x11_gstreamer_viewer/
```

### Type Hints

All functions and methods should include type hints:
```python
def create_window(self, width: int = 3840, height: int = 2160) -> bool:
    """Create a new X11 window."""
    ...
```

### Docstrings

All public methods should include docstrings:
```python
def create_window(self, width: int = 3840, height: int = 2160) -> bool:
    """
    Create a new X11 window.
    
    Args:
        width: Window width in pixels
        height: Window height in pixels
        
    Returns:
        True if window created successfully, False otherwise
    """
    ...
```

## Development Workflow

### Adding New Features

1. **Create feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes:**
   - Follow code style guidelines
   - Add type hints and docstrings
   - Write tests for new functionality

3. **Run tests:**
   ```bash
   pytest
   python test_basic.py
   ```

4. **Format and lint:**
   ```bash
   black x11_gstreamer_viewer/
   flake8 x11_gstreamer_viewer/
   ```

5. **Commit changes:**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

### Common Development Tasks

**Adding a new video source:**
1. Modify `GStreamerManager.video_devices` list
2. Update compositor sink configuration
3. Test with actual video device

**Modifying window behavior:**
1. Edit `X11WindowManager` methods
2. Update event handlers in `MainWindow`
3. Test window creation and events

**Changing configuration:**
1. Update `Config` class in `utils/config.py`
2. Add command-line argument support in `main.py`
3. Update configuration file schema

## Debugging

### Debug Logging

Enable debug logging:
```bash
x11-gstreamer-viewer --log-level DEBUG
```

### Log File

Save logs to file:
```bash
x11-gstreamer-viewer --log-level DEBUG --log-file debug.log
```

### Common Issues

**No video devices found:**
- Check device permissions: `ls -la /dev/video*`
- Ensure user is in `video` group
- Verify devices exist: `ls /dev/video*`

**GStreamer initialization failed:**
- Check GStreamer installation: `gst-inspect-1.0`
- Verify Python bindings: `python -c "import gi; gi.require_version('Gst', '1.0')"`

**X11 connection failed:**
- Check DISPLAY environment: `echo $DISPLAY`
- Ensure X11 is running
- Verify X11 libraries installed

**Window embedding not working:**
- Check window ID is set after pipeline starts
- Verify xvimagesink is available: `gst-inspect-1.0 xvimagesink`
- Check window manager compatibility

## Performance Optimization

### Low Latency Configuration

The application is configured for low latency:
- GStreamer sink: `sync=False` (VSYNC disabled)
- Frame dropping: `drop-on-lateness=True`
- Video sources: `do-timestamp=True`

### Hardware Acceleration

Uses `xvimagesink` for GPU-accelerated rendering:
- Preferred over `glimagesink` (can cause stuttering)
- Provides smooth video display

### Performance Monitoring

FPS and latency monitoring available:
- Hover mouse over window to show overlay
- Displays FPS and latency per camera
- Auto-hides after 3 seconds of inactivity

## Troubleshooting

### Video Not Displaying

1. Check video devices are accessible
2. Verify GStreamer pipeline is running
3. Check window ID is set correctly
4. Review debug logs for errors

### Stuttering or Lag

1. Verify using `xvimagesink` (not `glimagesink`)
2. Check system resources (CPU, GPU)
3. Reduce video resolution if needed
4. Check for other applications using video devices

### Window Not Appearing

1. Check X11 connection
2. Verify window creation succeeded
3. Check window manager compatibility
4. Review X11 event logs

## Contributing

### Code Contributions

1. Fork the repository
2. Create feature branch
3. Make changes following code style
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit pull request

### Documentation Contributions

- Update README.md for user-facing changes
- Update WORK_LOG.md for development history
- Update docstrings for code changes
- Update this guide for workflow changes

---

_Generated using BMAD Method `document-project` workflow_
