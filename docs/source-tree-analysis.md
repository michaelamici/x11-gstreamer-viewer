# x11-gstreamer-viewer - Source Tree Analysis

**Date:** 2026-02-08

## Overview

This project follows a clean Python package structure with clear separation between core functionality, UI components, and utilities. The codebase is organized into logical modules that handle X11 window management, GStreamer video processing, configuration, and logging.

## Complete Directory Structure

```
x11-gstreamer-viewer/
├── .cursorrules                    # Cursor IDE rules and project guidelines
├── .gitignore                     # Git ignore patterns
├── build.sh                        # Build script
├── demo.py                         # Demo script for testing
├── README.md                       # User-facing documentation
├── WORK_LOG.md                     # Development log and history
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup and installation
├── test_basic.py                   # Basic functionality tests
├── test_window_fix.py              # Window-related tests
├── x11_gstreamer_viewer/          # Main package directory
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # Application entry point
│   ├── core/                       # Core functionality modules
│   │   ├── __init__.py
│   │   ├── x11_manager.py          # X11 window management (428 lines)
│   │   └── gstreamer_manager.py   # GStreamer pipeline (654 lines)
│   ├── ui/                         # User interface components
│   │   ├── __init__.py
│   │   └── main_window.py         # Main window coordinator (294 lines)
│   └── utils/                      # Utility modules
│       ├── __init__.py
│       ├── config.py               # Configuration management (216 lines)
│       └── logger.py                # Logging setup (92 lines)
├── tests/                          # Test modules
│   ├── __init__.py
│   └── test_config.py              # Configuration tests
└── docs/                           # Project documentation (generated)
    ├── project-overview.md
    ├── source-tree-analysis.md
    └── project-scan-report.json
```

## Critical Directories

### `x11_gstreamer_viewer/core/`

**Purpose:** Core functionality modules that handle low-level system integration

**Contains:**
- `x11_manager.py`: X11 window creation, event handling, and window lifecycle management
- `gstreamer_manager.py`: GStreamer pipeline creation, video source management, and compositing

**Entry Points:** None (imported by `main_window.py`)

**Integration:** These modules are used by `MainWindow` to coordinate window and video functionality

### `x11_gstreamer_viewer/ui/`

**Purpose:** User interface coordination layer

**Contains:**
- `main_window.py`: Main application window that coordinates X11 and GStreamer components

**Entry Points:** Called from `main.py`

**Integration:** Integrates `X11WindowManager` and `GStreamerManager` to create the unified application interface

### `x11_gstreamer_viewer/utils/`

**Purpose:** Utility modules for configuration and logging

**Contains:**
- `config.py`: JSON-based configuration management with command-line argument support
- `logger.py`: Logging setup and configuration

**Entry Points:** Used throughout the application

**Integration:** Provides shared configuration and logging services to all modules

### `x11_gstreamer_viewer/`

**Purpose:** Main package root and application entry point

**Contains:**
- `main.py`: Application entry point with argument parsing and main execution flow
- `__init__.py`: Package initialization

**Entry Points:** `main.py` is the primary entry point (also accessible via `console_scripts` entry point)

**Integration:** Orchestrates the entire application lifecycle

## Entry Points

- **Main Entry:** `x11_gstreamer_viewer/main.py`
- **Additional:**
  - `x11-gstreamer-viewer` (console script): Entry point installed via setuptools
  - `demo.py`: Demo script for testing functionality

## File Organization Patterns

### Module Structure
- Each major component is in its own module file
- Clear separation between core functionality, UI, and utilities
- Consistent naming: `*_manager.py` for manager classes, `*_config.py` for configuration

### Import Patterns
- Core modules (`core/`) are imported by UI modules (`ui/`)
- Utils modules (`utils/`) are imported by all other modules
- Main entry point (`main.py`) imports from all other modules

### Configuration Pattern
- Configuration stored in `~/.config/x11-gstreamer-viewer/config.json`
- Command-line arguments override file configuration
- Default values provided for all configuration options

## Key File Types

### Python Source Files
- **Pattern:** `*.py`
- **Purpose:** Application source code
- **Examples:** `main.py`, `x11_manager.py`, `gstreamer_manager.py`

### Configuration Files
- **Pattern:** `*.json`, `*.yaml`, `setup.py`, `requirements.txt`
- **Purpose:** Package configuration, dependencies, and build settings
- **Examples:** `setup.py`, `requirements.txt`, `config.json` (user config)

### Documentation Files
- **Pattern:** `*.md`
- **Purpose:** Project documentation and guides
- **Examples:** `README.md`, `WORK_LOG.md`, `docs/*.md`

### Test Files
- **Pattern:** `test_*.py`, `*_test.py`
- **Purpose:** Unit and integration tests
- **Examples:** `test_basic.py`, `test_window_fix.py`, `tests/test_config.py`

## Configuration Files

- **`setup.py`**: Package setup, dependencies, and entry points
- **`requirements.txt`**: Python package dependencies
- **`~/.config/x11-gstreamer-viewer/config.json`**: User configuration (created at runtime)
- **`.cursorrules`**: Cursor IDE rules and project guidelines
- **`.gitignore`**: Git ignore patterns

## Notes for Development

### Adding New Features
1. **Core Functionality**: Add to `core/` directory
2. **UI Components**: Add to `ui/` directory
3. **Utilities**: Add to `utils/` directory
4. **Tests**: Add to `tests/` directory or create `test_*.py` files

### Module Dependencies
- `main.py` → imports from `ui/`, `utils/`
- `ui/main_window.py` → imports from `core/`, `utils/`
- `core/*` → imports from `utils/` (for logging)
- `utils/*` → no internal dependencies

### Testing Strategy
- Basic functionality tests in `test_basic.py`
- Module-specific tests in `tests/` directory
- Run all tests with `pytest` or `python test_basic.py`

### Build and Installation
- Install in development mode: `pip install -e .`
- Build package: `python setup.py build`
- Run build script: `./build.sh`

---

_Generated using BMAD Method `document-project` workflow_
