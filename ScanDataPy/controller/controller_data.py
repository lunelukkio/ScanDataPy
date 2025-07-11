# -*- coding: utf-8 -*-
"""
Refactored DataController with event-driven architecture.
No direct references to views - communicates via events only.
"""

from abc import ABCMeta, abstractmethod
from PyQt6.QtCore import Qt, QObject
from pathlib import Path

from ScanDataPy.model.model import DataService
from ScanDataPy.controller.controller_axes import TraceAxesController, ImageAxesController
from ScanDataPy.controller.controller_filename import FileService
from ScanDataPy.controller.controller_key_manager import KeyManager
from ScanDataPy.common_event import ViewEventBus, ControllerEventBus


class DataController(QObject):
    """
    Main data controller that manages the application logic.
    Communicates with views only through event buses.
    """
    
    def __init__(self, gui_backend_name=None):
        super().__init__()
        self._gui_backend_name = gui_backend_name
        self.filename_obj = None
        self.current_filename = [0]
        self._model = DataService()
        self._file_service = FileService(self._gui_backend_name)
        self._key_manager = KeyManager()
        self._ax_dict = {}  # Axes controllers
        
        # Event buses for communication
        self.view_event_bus = ViewEventBus()
        self.controller_event_bus = ControllerEventBus()
        
        # Connect view events to controller methods
        self._connect_view_events()
        
        # Initialize axes controllers after window is created
        self._axes_initialized = False
    
    def _connect_view_events(self):
        """Connect view events to appropriate handler methods"""
        # File operations
        self.view_event_bus.file_open_requested.connect(self._handle_file_open)
        
        # ROI operations
        self.view_event_bus.roi_size_change_requested.connect(self._handle_roi_size_change)
        self.view_event_bus.roi_clicked.connect(self._handle_roi_click)
        self.view_event_bus.bl_roi_mode_changed.connect(self._handle_bl_roi_mode_change)
        self.view_event_bus.bl_use_roi1_changed.connect(self._handle_bl_use_roi1_change)
        
        # Modifier operations
        self.view_event_bus.modifier_value_change_requested.connect(self._handle_modifier_value_change)
        self.view_event_bus.scale_mode_changed.connect(self._handle_scale_mode_change)
        self.view_event_bus.bl_comp_toggled.connect(self._handle_bl_comp_toggle)
        self.view_event_bus.dif_image_toggled.connect(self._handle_dif_image_toggle)
        self.view_event_bus.invert_toggled.connect(self._handle_invert_toggle)
        
        # Channel operations
        self.view_event_bus.fluo_channel_changed.connect(self._handle_fluo_channel_change)
        self.view_event_bus.elec_channel_changed.connect(self._handle_elec_channel_change)
        
        # Time window operations
        self.view_event_bus.time_window_change_requested.connect(self._handle_time_window_change)
        
        # View updates
        self.view_event_bus.view_update_requested.connect(self._handle_view_update_request)
        self.view_event_bus.axes_sync_requested.connect(self._handle_axes_sync)
    
    def initialize_axes(self, axes_config):
        """
        Initialize axes controllers based on configuration from view.
        Called after the view window is created.
        
        Args:
            axes_config: Dict with axes information
                {
                    "ImageAxes": {"type": "Image", "widget": image_ax},
                    "FluoAxes": {"type": "Trace", "widget": trace_ax1},
                    "ElecAxes": {"type": "Trace", "widget": trace_ax2}
                }
        """
        for axes_name, config in axes_config.items():
            ax_type = config["type"]
            widget = config["widget"]
            
            if ax_type == "Image":
                controller = ImageAxesController(self, self._model, None, widget)
            elif ax_type == "Trace":
                controller = TraceAxesController(self, self._model, None, widget)
            else:
                raise ValueError(f"Unknown axes type: {ax_type}")
            
            self._ax_dict[axes_name] = controller
            print(f"[DataController]: Added {axes_name} axes controller")
        
        self._axes_initialized = True
    
    def get_filename(self):
        """Return the filename as a string"""
        return self.filename_obj.name if self.filename_obj else None
    
    @property
    def ax_dict(self):
        return self._ax_dict
    
    @property
    def key_manager(self):
        return self._key_manager
    
    # Event Handlers
    
    def _handle_file_open(self, filename_obj):
        """Handle file open request from view"""
        self.__reset()
        
        if filename_obj is None:
            filename_obj = self._file_service.open_file()
        
        if filename_obj is None or filename_obj.name == "":
            self.controller_event_bus.status_message.emit("File opening cancelled")
            return
        
        # Create experiments data
        try:
            success = self.create_experiments(filename_obj)
            if success:
                self.filename_obj = filename_obj
                self._key_manager.set_tag("filename_list", filename_obj.name)
                
                # Create default modifiers and settings
                self.create_default_modifier(0)
                self.default_settings(filename_obj.name)
                
                # Get similar files
                same_ext_files = self._file_service.get_files_with_same_extension(
                    filename_obj.fullname
                )
                
                # Emit success event
                self.controller_event_bus.data_loaded.emit(
                    filename_obj.name, 
                    {"same_ext_files": same_ext_files}
                )
                
                # Request view updates
                self.view_event_bus.view_update_requested.emit(None)  # Update all
                self.view_event_bus.marker_update_requested.emit("ImageAxes", "Roi1")
                
                print(f"[DataController]: Opened {filename_obj.name} successfully")
            else:
                self.controller_event_bus.error_occurred.emit("Failed to open file")
        
        except Exception as e:
            self.controller_event_bus.error_occurred.emit(f"Error opening file: {str(e)}")
    
    def _handle_roi_size_change(self, command):
        """Handle ROI size change request"""
        if command == "large":
            val = [None, None, 1, 1]
        elif command == "small":
            val = [None, None, -1, -1]
        else:
            self.controller_event_bus.error_occurred.emit(f"Invalid ROI size command: {command}")
            return
        
        if "FluoAxes" in self._ax_dict:
            roi_tag = self._ax_dict["FluoAxes"].change_roi_size(val)
            self.view_event_bus.view_update_requested.emit("FluoAxes")
            self.view_event_bus.marker_update_requested.emit("ImageAxes", roi_tag)
    
    def _handle_roi_click(self, axes_name, position):
        """Handle ROI click on image"""
        if axes_name == "ImageAxes" and "FluoAxes" in self._ax_dict:
            x, y = round(position[0]), round(position[1])
            val = [x, y, None, None]
            roi_tag = self._ax_dict["FluoAxes"].onclick_axes(val)
            self.view_event_bus.view_update_requested.emit("FluoAxes")
            self.view_event_bus.marker_update_requested.emit("ImageAxes", roi_tag)
    
    def _handle_bl_roi_mode_change(self, enabled):
        """Handle baseline ROI mode change"""
        mode = "Baseline_control" if enabled else "Normal"
        if "FluoAxes" in self._ax_dict:
            self._ax_dict["FluoAxes"].change_current_ax_mode(mode)
            self.view_event_bus.view_update_requested.emit("FluoAxes")
    
    def _handle_bl_use_roi1_change(self, use_roi1):
        """Handle baseline ROI selection change"""
        roi = "Roi1" if use_roi1 else "Roi0"
        if "FluoAxes" in self._ax_dict:
            self._ax_dict["FluoAxes"].replace_key_manager_tag("bl_roi_list", "Roi", roi)
            self._ax_dict["FluoAxes"].set_update_flag(True)
            self.view_event_bus.view_update_requested.emit("FluoAxes")
    
    def _handle_modifier_value_change(self, modifier_name, value):
        """Handle modifier value change request"""
        self._model.set_modifier_val(modifier_name, value)
        # Determine which axes need updating based on modifier
        if modifier_name in ["TimeWindow0", "BlComp0"]:
            self._ax_dict["FluoAxes"].set_update_flag(True)
            self.view_event_bus.view_update_requested.emit("FluoAxes")
        elif modifier_name in ["TimeWindow1"]:
            self._ax_dict["ImageAxes"].set_update_flag(True)
            self.view_event_bus.view_update_requested.emit("ImageAxes")
    
    def _handle_scale_mode_change(self, mode):
        """Handle scale mode change (Original, DFoF, Normalize)"""
        self._model.set_modifier_val("Scale0", mode)
        if "FluoAxes" in self._ax_dict:
            self._ax_dict["FluoAxes"].set_update_flag(True)
            self.view_event_bus.view_update_requested.emit("FluoAxes")
    
    def _handle_bl_comp_toggle(self, enabled):
        """Handle baseline compensation toggle"""
        if "FluoAxes" in self._ax_dict:
            if enabled:
                self._ax_dict["FluoAxes"].set_tag("modifier_list", "BlComp0")
                self._model.set_modifier_val("BlComp0", "Exponential")
                self.controller_event_bus.float_window_requested.emit(True, {})
            else:
                self._model.set_modifier_val("BlComp0", "Disable")
                self._ax_dict["FluoAxes"].set_tag("modifier_list", "BlComp0")
                self.controller_event_bus.float_window_requested.emit(False, {})
            
            self._ax_dict["FluoAxes"].set_update_flag(True)
            self.view_event_bus.view_update_requested.emit("FluoAxes")
    
    def _handle_dif_image_toggle(self, enabled):
        """Handle differential image toggle"""
        if "ImageAxes" in self._ax_dict:
            self._ax_dict["ImageAxes"].set_tag("modifier_list", "DifImage0")
            color = "plasma" if enabled else "grey"
            self._ax_dict["ImageAxes"].change_color(color)
            self._ax_dict["ImageAxes"].set_update_flag(True)
            self.view_event_bus.view_update_requested.emit("ImageAxes")
    
    def _handle_invert_toggle(self, enabled):
        """Handle invert toggle"""
        if "FluoAxes" in self._ax_dict:
            self._ax_dict["FluoAxes"].set_tag("modifier_list", "Invert0")
            self._ax_dict["FluoAxes"].set_update_flag(True)
            self.view_event_bus.view_update_requested.emit("FluoAxes")
    
    def _handle_fluo_channel_change(self, channel):
        """Handle fluorescence channel change"""
        for ax_name in ["FluoAxes", "ImageAxes"]:
            if ax_name in self._ax_dict:
                self._ax_dict[ax_name].set_tag("ch_list", channel)
                self._ax_dict[ax_name].set_update_flag(True)
        self.view_event_bus.view_update_requested.emit("FluoAxes")
        self.view_event_bus.view_update_requested.emit("ImageAxes")
    
    def _handle_elec_channel_change(self, channel):
        """Handle electrical channel change"""
        if "ElecAxes" in self._ax_dict:
            self._ax_dict["ElecAxes"].set_tag("ch_list", channel)
            self._ax_dict["ElecAxes"].set_update_flag(True)
            self.view_event_bus.view_update_requested.emit("ElecAxes")
    
    def _handle_time_window_change(self, window_type, axes_name, values):
        """Handle time window change request"""
        self._model.set_modifier_val(window_type, values)
        if axes_name in self._ax_dict:
            self._ax_dict[axes_name].set_update_flag(True)
            self.view_event_bus.view_update_requested.emit(axes_name)
    
    def _handle_view_update_request(self, axes_name):
        """Handle view update request"""
        if axes_name is None:
            # Update all axes
            for ax in self._ax_dict.values():
                ax.update()
                ax.set_update_flag(False)
        elif axes_name in self._ax_dict:
            self._ax_dict[axes_name].update()
            self._ax_dict[axes_name].set_update_flag(False)
        
        self.controller_event_bus.status_message.emit("View updated")
    
    def _handle_axes_sync(self, source_axes, range_data):
        """Handle axes synchronization request"""
        # This would be implemented based on specific sync requirements
        pass
    
    # Existing methods (modified to remove view dependencies)
    
    def create_experiments(self, filename_obj):
        """Create experiments from file"""
        print("[DataController]: Create_experiments() ----->")
        new_data = self._model.create_experiments(filename_obj.fullname)
        if new_data is not True:
            raise Exception("Failed to create a model.")
        print("-----> [DataController]: Create_experiments() Done")
        return True
    
    def create_default_modifier(self, filename_number):
        """Create default modifiers from settings"""
        print("[DataController]: Create_default_modifiers() ----->")
        
        filename = self._key_manager.filename_list[self.current_filename[0]]
        default = self._model.get_data(
            {"Filename": filename, "Attribute": "Default", "DataType": "Text"}
        )
        
        for modifier_name in default.data["default_settings"]["default_modifiers"]:
            self.create_modifier(modifier_name)
        
        print("-----> [DataController]: Create_default_modifier() Done")
        self._model.print_infor("Modifier")
    
    def create_modifier(self, modifier_name):
        """Create a modifier"""
        self._model.add_modifier(modifier_name)
    
    def set_observer(self, ax_name, modifier_tag):
        """Set observer for axes controller"""
        if ax_name in self._ax_dict:
            self._ax_dict[ax_name].set_observer(modifier_tag)
    
    def default_settings(self, filename_key):
        """Apply default settings from configuration"""
        print("========== Start default settings. ==========")
        
        filename = self._key_manager.filename_list[self.current_filename[0]]
        default = self._model.get_data(
            {"Filename": filename, "Attribute": "Default", "DataType": "Text"}
        )
        
        # Set observers
        default_observer = default.data["default_settings"]["default_observer"]
        for key, item_list in default_observer.items():
            for value in item_list:
                self.set_observer(key, value)
        
        # Set main controller tags
        main_default_tag_list = default.data["default_settings"]["main_default_tag"]
        for tag_list_name, tag_list in main_default_tag_list.items():
            for tag in tag_list:
                self._key_manager.set_tag(tag_list_name, tag)
        
        # Set axes controller tags
        for ax_name, ax_controller in self._ax_dict.items():
            ax_controller.key_manager.set_tag("filename_list", filename)
            
            # Get appropriate default tags based on axes type
            if ax_name == "FluoAxes":
                tag_key = "trace_ax_default_tag"
            elif ax_name == "ImageAxes":
                tag_key = "image_ax_default_tag"
            elif ax_name == "ElecAxes":
                tag_key = "elec_ax_default_tag"
            else:
                continue
            
            default_tag_list = default.data["default_settings"].get(tag_key, {})
            for tag_list_name, tag_list in default_tag_list.items():
                for tag in tag_list:
                    ax_controller.key_manager.set_tag(tag_list_name, tag)
        
        # Set modifier default values
        default_values_list = default.data["default_settings"]["modifier_default_val"]
        for modifier, value in default_values_list.items():
            self._model.set_modifier_val(modifier, value)
        
        print("========== End of default settings ==========")
    
    def __reset(self):
        """Reset all components"""
        self._model.reset()
        self._file_service.reset()
        self._key_manager.reset()
        for ax in self._ax_dict.values():
            ax.key_manager.reset()
    
    def print_infor(self):
        """Print information about current state"""
        print("========== Data Information ==========")
        self._model.print_infor()
        print("Operating controller list ---------->")
        self._key_manager.print_infor()
        print("Axes controller infor ---------->")
        for ax in self._ax_dict.values():
            ax.print_infor()
        print("========== Data Information End ==========")