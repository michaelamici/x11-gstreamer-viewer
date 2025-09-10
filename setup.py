#!/usr/bin/env python3
"""
X11 GStreamer Viewer Setup
Created by Ruliano Castian - From the streets to the code!
"""

from setuptools import setup, find_packages

setup(
    name="x11-gstreamer-viewer",
    version="1.0.0",
    description="X11 Window Manager with GStreamer 4-Way Video Viewer",
    author="Ruliano Castian",
    author_email="ruliano@streets2code.dev",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "python-xlib>=0.33",
        "PyGObject>=3.44.0",
        "gi>=1.2.0",
        "gst-python>=1.20.0",
        "numpy>=1.21.0",
        "opencv-python>=4.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "x11-gstreamer-viewer=x11_gstreamer_viewer.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)