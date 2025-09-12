#!/bin/bash
# X11 GStreamer Viewer Build Script
# Created by Ruliano Castian - From the streets to the code!

set -e

echo "X11 GStreamer Viewer - Build Script"
echo "===================================="
echo "Created by Ruliano Castian - From the streets to the code!"
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/
echo "✓ Cleaned"

# Run tests
echo ""
echo "Running tests..."
python test_basic.py
echo "✓ Tests passed"

# Build package
echo ""
echo "Building package..."
python setup.py build
echo "✓ Build completed"

# Create distribution
echo ""
echo "Creating distribution..."
python setup.py sdist
echo "✓ Distribution created"

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "To install:"
echo "  pip install dist/x11-gstreamer-viewer-1.0.0.tar.gz"
echo ""
echo "To run:"
echo "  python -m x11_gstreamer_viewer.main"
echo "  python demo.py"
echo ""
echo "From the streets to the code - we build it right! 🔥"