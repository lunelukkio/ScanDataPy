# -*- coding: utf-8 -*-
"""
Refactored QtDataWindow using event-driven architecture.
No direct calls to DataController - only emits events.
"""

import sys
import json
from abc import ABCMeta, abstractmethod

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt
import pyqtgraph as pg

from ScanDataPy.common_event import ViewEventBus, ControllerEventBus


class AbstractDataWindowFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_data_window(self, parent, view_event_bus, controller_event_bus):
        raise NotImplementedError()


class QtDataWindowFactory(AbstractDataWindowFactory):
    """Factory class for creating Qt data windows"""
    
    @staticmethod
    def create_data_window(parent, view_event_bus, controller_event_bus):
        return QtDataWindow(parent, view_event_bus, controller_event_bus)


class QtDataWindow(QtWidgets.QMainWindow):
    """
    Main data visualization window.
    Communicates with controller only through event buses.
    """
    
    def __init__(self, parent=None, view_event_bus=None, controller_event_bus=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # Event buses for communication
        self.view_event_bus = view_event_bus
        self.controller_event_bus = controller_event_bus
        
        # Connect controller events
        self._connect_controller_events()
        
        # Load settings
        self._load_settings()
        
        # Setup UI
        self._setup_ui()
        
        # Store axes widgets for controller initialization
        self.axes_widgets = {
            "ImageAxes": {"type": "Image", "widget": self.image_ax},
            "FluoAxes": {"type": "Trace", "widget": self.trace_ax1},
            "ElecAxes": {"type": "Trace", "widget": self.trace_ax2}
        }
        
        # Track UI state
        self.current_scale_mode = "Original"
        self.float_window = None
    
    def _connect_controller_events(self):
        """Connect to controller events"""
        self.controller_event_bus.data_loaded.connect(self._on_data_loaded)
        self.controller_event_bus.axes_data_updated.connect(self._on_axes_updated)
        self.controller_event_bus.roi_marker_updated.connect(self._on_roi_marker_updated)
        self.controller_event_bus.float_window_requested.connect(self._on_float_window_requested)
        self.controller_event_bus.status_message.connect(self._on_status_message)
        self.controller_event_bus.error_occurred.connect(self._on_error)
    
    def _load_settings(self):
        """Load window settings from JSON file"""
        setting = None
        search_paths = [
            "./setting/data_window_setting.json",
            "../setting/data_window_setting.json",
            "./ScanDataPy/setting/data_window_setting.json",
        ]
        
        for path in search_paths:
            try:
                with open(path, "r") as json_file:
                    setting = json.load(json_file)
                print(f"[QtDataWindow]: Successfully loaded settings from: {path}")
                break
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"[QtDataWindow]: Error loading {path}: {str(e)}")
                continue
        
        if setting is None:
            raise FileNotFoundError("[QtDataWindow]: No valid settings file found")
        
        self.settings = setting
    
    def _setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("datascan")
        
        # Apply window settings
        self.setStyleSheet("background-color: " + self.settings["main_window"]["color"] + ";")
        self.setGeometry(
            self.settings["main_window"]["window_posX"],
            self.settings["main_window"]["window_posY"],
            self.settings["main_window"]["geometryX"],
            self.settings["main_window"]["geometryY"],
        )
        
        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Create image view
        self.image_ax = CustomImageView()
        self.image_ax.ui.histogram.hide()
        self.image_ax.ui.menuBtn.hide()
        self.image_ax.ui.roiBtn.hide()
        view = self.image_ax.getView()
        view.setBackgroundColor(self.settings["main_window"]["color"])
        
        # Create splitters
        self.horizontal_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.vertical_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        
        # Create trace plots
        self.trace_ax1 = pg.PlotWidget()
        self.trace_ax2 = pg.PlotWidget()
        self.vertical_splitter.addWidget(self.trace_ax1)
        self.vertical_splitter.addWidget(self.trace_ax2)
        
        # Style trace plots
        for ax in [self.trace_ax1, self.trace_ax2]:
            ax.setBackground("white")
            ax.getAxis("bottom").setPen(pg.mkPen(color=(0, 0, 0), width=2))
            ax.getAxis("left").setPen(pg.mkPen(color=(0, 0, 0), width=2))
        self.trace_ax2.setLabel("bottom", "Time (ms)", color="black", size=20, width=2)
        
        # Add to splitters
        self.horizontal_splitter.addWidget(self.image_ax)
        self.horizontal_splitter.addWidget(self.vertical_splitter)
        main_layout.addWidget(self.horizontal_splitter)
        
        self.horizontal_splitter.setSizes([600, 1000])
        self.vertical_splitter.setSizes([450, 150])
        
        # Connect axes synchronization
        self.trace_ax1.sigXRangeChanged.connect(self._sync_x_axes)
        self.trace_ax2.sigXRangeChanged.connect(self._sync_x_axes)
        
        # Add controls
        self._setup_controls(main_layout)
        
        # Connect mouse click event on image
        self.image_ax.getView().scene().sigMouseClicked.connect(self._on_image_clicked)
    
    def _setup_controls(self, main_layout):
        """Setup control buttons and checkboxes"""
        # Differential image checkbox
        self.dif_image_button = QtWidgets.QCheckBox("Differential Image")
        self.dif_image_button.setChecked(False)
        self.dif_image_button.stateChanged.connect(
            lambda: self.view_event_bus.dif_image_toggled.emit(self.dif_image_button.isChecked())
        )
        main_layout.addWidget(self.dif_image_button)
        
        # Baseline compensation checkbox
        self.bl_comp_checkbox = QtWidgets.QCheckBox("Baseline Comp")
        self.bl_comp_checkbox.setChecked(False)
        self.bl_comp_checkbox.stateChanged.connect(
            lambda: self.view_event_bus.bl_comp_toggled.emit(self.bl_comp_checkbox.isChecked())
        )
        main_layout.addWidget(self.bl_comp_checkbox)
        
        # Scale mode radio buttons
        self.origin_trace = QtWidgets.QRadioButton("Original")
        self.dFoverF_trace = QtWidgets.QRadioButton("dF/F")
        self.normalized_trace = QtWidgets.QRadioButton("Normalize")
        
        self.trace_type = QtWidgets.QButtonGroup()
        self.trace_type.addButton(self.origin_trace)
        self.trace_type.addButton(self.dFoverF_trace)
        self.trace_type.addButton(self.normalized_trace)
        
        self.origin_trace.setChecked(True)
        self.trace_type.buttonClicked.connect(self._on_scale_changed)
        
        for btn in [self.origin_trace, self.dFoverF_trace, self.normalized_trace]:
            main_layout.addWidget(btn)
        
        # Bottom button layout
        bottom_btn_layout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, 
                                       QtWidgets.QSizePolicy.Policy.Minimum)
        
        # File operations
        load_btn = QtWidgets.QPushButton("Load")
        load_btn.setFixedSize(40, 30)
        load_btn.clicked.connect(lambda: self.view_event_bus.file_open_requested.emit(None))
        bottom_btn_layout.addWidget(load_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        # ROI size buttons
        large_btn = QtWidgets.QPushButton("Large")
        large_btn.setFixedSize(60, 30)
        large_btn.clicked.connect(lambda: self.view_event_bus.roi_size_change_requested.emit("large"))
        bottom_btn_layout.addWidget(large_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        small_btn = QtWidgets.QPushButton("Small")
        small_btn.setFixedSize(60, 30)
        small_btn.clicked.connect(lambda: self.view_event_bus.roi_size_change_requested.emit("small"))
        bottom_btn_layout.addWidget(small_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        # Baseline ROI checkbox
        self.bl_roi_change_btn = QtWidgets.QCheckBox("BL")
        self.bl_roi_change_btn.setChecked(False)
        self.bl_roi_change_btn.setFixedSize(40, 30)
        self.bl_roi_change_btn.clicked.connect(
            lambda: self.view_event_bus.bl_roi_mode_changed.emit(self.bl_roi_change_btn.isChecked())
        )
        bottom_btn_layout.addWidget(self.bl_roi_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        # Baseline use ROI1 checkbox
        self.bl_use_roi1 = QtWidgets.QCheckBox("BL=Roi1")
        self.bl_use_roi1.setChecked(False)
        self.bl_use_roi1.setFixedSize(60, 30)
        self.bl_use_roi1.clicked.connect(
            lambda: self.view_event_bus.bl_use_roi1_changed.emit(self.bl_use_roi1.isChecked())
        )
        bottom_btn_layout.addWidget(self.bl_use_roi1, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        # Time window buttons
        self.bl_time_button = QtWidgets.QPushButton("BL cut")
        self.bl_time_button.clicked.connect(lambda: self._show_time_dialog("BlComp0", "FluoAxes"))
        bottom_btn_layout.addWidget(self.bl_time_button, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        self.image_time_button = QtWidgets.QPushButton("Img time window")
        self.image_time_button.clicked.connect(lambda: self._show_time_dialog("TimeWindow0", "ImageAxes"))
        bottom_btn_layout.addWidget(self.image_time_button, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        self.dif_button = QtWidgets.QPushButton("dif image")
        self.dif_button.clicked.connect(lambda: self._show_time_dialog("TimeWindow1", "ImageAxes"))
        bottom_btn_layout.addWidget(self.dif_button, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        # Fluorescence channel checkboxes
        self.ch0_change_btn = QtWidgets.QCheckBox("Ch0")
        self.ch0_change_btn.setChecked(False)
        self.ch0_change_btn.setFixedSize(50, 30)
        self.ch0_change_btn.clicked.connect(lambda: self.view_event_bus.fluo_channel_changed.emit("Ch0"))
        bottom_btn_layout.addWidget(self.ch0_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        self.ch1_change_btn = QtWidgets.QCheckBox("Ch1")
        self.ch1_change_btn.setChecked(True)
        self.ch1_change_btn.setFixedSize(50, 30)
        self.ch1_change_btn.clicked.connect(lambda: self.view_event_bus.fluo_channel_changed.emit("Ch1"))
        bottom_btn_layout.addWidget(self.ch1_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        self.ch2_change_btn = QtWidgets.QCheckBox("Ch2")
        self.ch2_change_btn.setChecked(False)
        self.ch2_change_btn.setFixedSize(50, 30)
        self.ch2_change_btn.clicked.connect(lambda: self.view_event_bus.fluo_channel_changed.emit("Ch2"))
        bottom_btn_layout.addWidget(self.ch2_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        # Invert checkbox
        self.invert_switch = QtWidgets.QCheckBox("Invert")
        self.invert_switch.setChecked(False)
        self.invert_switch.setFixedSize(60, 30)
        self.invert_switch.clicked.connect(
            lambda: self.view_event_bus.invert_toggled.emit(self.invert_switch.isChecked())
        )
        bottom_btn_layout.addWidget(self.invert_switch, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        
        bottom_btn_layout.addSpacerItem(spacer)
        
        # Electrical channel checkboxes
        for i in range(1, 9):
            ch_btn = QtWidgets.QCheckBox(f"Ch{i}")
            ch_btn.setChecked(i == 1)
            ch_btn.setFixedSize(50, 30)
            ch_btn.clicked.connect(lambda checked, ch=f"Ch{i}": self.view_event_bus.elec_channel_changed.emit(ch))
            bottom_btn_layout.addWidget(ch_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
            setattr(self, f"elec_ch{i}_change_btn", ch_btn)
        
        main_layout.addLayout(bottom_btn_layout)
    
    def _on_scale_changed(self, button):
        """Handle scale mode change"""
        text = button.text()
        scale_map = {"Original": "Original", "dF/F": "DFoF", "Normalize": "Normalize"}
        mode = scale_map.get(text, "Original")
        self.current_scale_mode = mode
        self.view_event_bus.scale_mode_changed.emit(mode)
    
    def _show_time_dialog(self, window_type, axes_name):
        """Show time window input dialog"""
        dialog = InputDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            values = dialog.get_numbers()
            if values is not None:
                self.view_event_bus.time_window_change_requested.emit(window_type, axes_name, values)
            else:
                print("Only numerical values are available")
    
    def _sync_x_axes(self, view):
        """Synchronize x-axes between trace plots"""
        x_range1 = self.trace_ax1.viewRange()[0]
        x_range2 = self.trace_ax2.viewRange()[0]
        
        # Synchronize both axes
        self.trace_ax1.setXRange(x_range1[0], x_range1[1], padding=0)
        self.trace_ax2.setXRange(x_range1[0], x_range1[1], padding=0)
    
    def _on_image_clicked(self, event):
        """Handle mouse click on image"""
        if event.button() == Qt.MouseButton.LeftButton:
            image_pos = self.image_ax.getView().mapSceneToView(event.scenePos())
            position = [image_pos.x(), image_pos.y(), None, None]
            self.view_event_bus.roi_clicked.emit("ImageAxes", position)
    
    def get_axes_config(self):
        """Get axes configuration for controller initialization"""
        return self.axes_widgets
    
    # Event handlers for controller events
    
    def _on_data_loaded(self, filename, data_info):
        """Handle data loaded event"""
        print(f"[QtDataWindow]: Data loaded: {filename}")
        # Apply default UI settings
        self.bl_use_roi1.setChecked(True)
        self.dFoverF_trace.setChecked(True)
    
    def _on_axes_updated(self, axes_name, data):
        """Handle axes data update"""
        # This would be implemented based on how the controller sends data
        pass
    
    def _on_roi_marker_updated(self, axes_name, roi_tag, position):
        """Handle ROI marker update"""
        # This would update ROI visualization
        pass
    
    def _on_float_window_requested(self, show, window_data):
        """Handle float window request"""
        if show:
            if self.float_window is None:
                self.float_window = FloatWindow(self)
                # Emit event to notify controller about float window axes
                float_axes_config = {
                    "FloatAxes1": {"type": "Trace", "widget": self.float_window.plot_widget}
                }
                # Controller would need to handle this additional axes
            self.float_window.show()
        else:
            if self.float_window is not None:
                self.float_window.close()
                self.float_window = None
    
    def _on_status_message(self, message):
        """Handle status message"""
        print(f"[QtDataWindow]: {message}")
    
    def _on_error(self, error_message):
        """Handle error message"""
        print(f"[QtDataWindow]: Error - {error_message}")
        QtWidgets.QMessageBox.warning(self, "Error", error_message)


class InputDialog(QtWidgets.QDialog):
    """Dialog for inputting time window values"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Input values")
        self.setGeometry(100, 100, 200, 100)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        self.inputs = []
        for i in range(2):
            number_input = QtWidgets.QLineEdit(self)
            if i == 0:
                number_input.setPlaceholderText("Start")
            elif i == 1:
                number_input.setPlaceholderText("Width")
            self.inputs.append(number_input)
            layout.addWidget(number_input)
        
        self.ok_button = QtWidgets.QPushButton("OK", self)
        layout.addWidget(self.ok_button)
        self.ok_button.clicked.connect(self.accept)
    
    def get_numbers(self):
        try:
            return [int(input_field.text()) for input_field in self.inputs]
        except ValueError:
            return None


class FloatWindow(QtWidgets.QMainWindow):
    """Float window for baseline compensation display"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Float Window")
        self.setGeometry(100, 100, 300, 200)
        
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        
        self.plot_widget.setBackground("w")
        self.plot_widget.getAxis("bottom").setPen(pg.mkPen(color=(0, 0, 0), width=2))
        self.plot_widget.getAxis("left").setPen(pg.mkPen(color=(0, 0, 0), width=2))
        self.plot_widget.setLabel("bottom", "X Axis", color="black")
        self.plot_widget.setLabel("left", "Y Axis", color="black")


class CustomImageView(pg.ImageView):
    """Custom ImageView that ignores certain mouse events"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
    
    def mouseMoveEvent(self, event):
        event.ignore()
    
    def mouseDragEvent(self, event):
        event.ignore()