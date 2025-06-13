"""
ScanDataPy - Scientific data analysis application for neurophysiology

This package provides tools for analyzing neurophysiology data including:
- Data file loading and processing
- Image and trace visualization
- ROI (Region of Interest) analysis
- Electrophysiology trace analysis
"""

__version__ = "1.5.5"
__author__ = "lunelukkio@gmail.com"

from .common_class import FileService, WholeFilename, KeyManager, Tools
from .model.model import DataService
from .view.view import QtDataWindow

__all__ = [
    "FileService",
    "WholeFilename",
    "KeyManager",
    "Tools",
    "DataService",
    "QtDataWindow",
]
