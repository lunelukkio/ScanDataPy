# -*- coding: utf-8 -*-
"""
Event system for decoupling View and Controller communication.
Uses PyQt6 signals for event-driven architecture.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ViewEvent:
    """Base class for all view events"""
    event_type: str
    data: Dict[str, Any]


class ViewEventBus(QObject):
    """
    Central event bus for View->Controller communication.
    Views emit events through this bus, and Controllers subscribe to them.
    """
    
    # File operations
    file_open_requested = pyqtSignal(object)  # filename_obj or None
    
    # ROI operations
    roi_size_change_requested = pyqtSignal(str)  # "large" or "small"
    roi_clicked = pyqtSignal(str, list)  # axes_name, [x, y, None, None]
    bl_roi_mode_changed = pyqtSignal(bool)  # True for baseline mode
    bl_use_roi1_changed = pyqtSignal(bool)  # True to use Roi1
    
    # Modifier operations
    modifier_value_change_requested = pyqtSignal(str, object)  # modifier_name, value
    scale_mode_changed = pyqtSignal(str)  # "Original", "DFoF", "Normalize"
    bl_comp_toggled = pyqtSignal(bool)  # True to enable
    dif_image_toggled = pyqtSignal(bool)  # True to enable
    invert_toggled = pyqtSignal(bool)  # True to enable
    
    # Channel operations
    fluo_channel_changed = pyqtSignal(str)  # "Ch0", "Ch1", "Ch2"
    elec_channel_changed = pyqtSignal(str)  # "Ch1" - "Ch8"
    
    # Time window operations
    time_window_change_requested = pyqtSignal(str, str, list)  # window_type, axes_name, values
    
    # View update requests
    view_update_requested = pyqtSignal(str)  # axes_name or None for all
    marker_update_requested = pyqtSignal(str, str)  # axes_name, roi_tag
    
    # Axes sync
    axes_sync_requested = pyqtSignal(str, object)  # source_axes, range_data


class ControllerEventBus(QObject):
    """
    Event bus for Controller->View communication.
    Controllers emit events to update views without direct references.
    """
    
    # Data updates
    data_loaded = pyqtSignal(str, object)  # filename, data_info
    axes_data_updated = pyqtSignal(str, object)  # axes_name, data
    
    # UI state updates
    roi_marker_updated = pyqtSignal(str, str, object)  # axes_name, roi_tag, position
    modifier_state_changed = pyqtSignal(str, object)  # modifier_name, state
    
    # Window management
    float_window_requested = pyqtSignal(bool, object)  # show/hide, window_data
    
    # Status updates
    status_message = pyqtSignal(str)  # message
    error_occurred = pyqtSignal(str)  # error_message