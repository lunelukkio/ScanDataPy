# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 11:43:13 2022

lunelukkio@gmail.com
main for view
"""

import sys
import json
from ScanDataPy.common_class import WholeFilename
from ScanDataPy.controller.controller_main import MainController
import PyQt6
from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets


class QtDataWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main_controller = MainController(self)
        self.setWindowTitle("SCANDATA")

        # import a JSON setting file
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
                print(f"QtDataWindow: Successfully loaded settings from: {path}")
                break
            except FileNotFoundError:
                continue
            except json.JSONDecodeError:
                print(f"Error: {path} is not a valid JSON file")
                continue
            except Exception as e:
                print(f"QtDataWindow: Unexpected error while reading {path}: {str(e)}")
                continue

        if setting is None:
            print(
                "QtDataWindow: Error: Could not find or load data_window_setting.json in any of these locations:"
            )
            for path in search_paths:
                print(f"- {path}")
            raise FileNotFoundError("QtDataWindow: No valid settings file found")

        # window color, position and size
        self.setStyleSheet("background-color: " + setting["main_window"]["color"] + ";")
        self.setGeometry(
            setting["main_window"]["window_posX"],
            setting["main_window"]["window_posY"],
            setting["main_window"]["geometryX"],
            setting["main_window"]["geometryY"],
        )

        # set central widget
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QtWidgets.QVBoxLayout(centralWidget)
        size = centralWidget.size()  # noqa: F841

        # image window
        # image_ax = pg.ImageView()
        image_ax = CustomImageView()
        image_ax.ui.histogram.hide()  # hide contrast bar
        image_ax.ui.menuBtn.hide()  # hide a menu button
        image_ax.ui.roiBtn.hide()  # hide a ROI button
        view = image_ax.getView()
        view.setBackgroundColor(setting["main_window"]["color"])

        # for fix a image
        # it doesn't work
        image_item = image_ax.getImageItem()
        image_item.setFlag(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False
        )

        self.horizontalSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.verticalSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)

        trace_ax1 = pg.PlotWidget()
        trace_ax2 = pg.PlotWidget()
        self.verticalSplitter.addWidget(trace_ax1)
        self.verticalSplitter.addWidget(trace_ax2)

        trace_ax1.setBackground("white")
        trace_ax2.setBackground("white")
        trace_ax1.getAxis("bottom").setPen(pg.mkPen(color=(0, 0, 0), width=2))
        trace_ax1.getAxis("left").setPen(pg.mkPen(color=(0, 0, 0), width=2))
        trace_ax2.getAxis("bottom").setPen(pg.mkPen(color=(0, 0, 0), width=2))
        trace_ax2.getAxis("left").setPen(pg.mkPen(color=(0, 0, 0), width=2))
        trace_ax2.setLabel("bottom", "Time (ms)", color="black", size=20, width=2)

        self.horizontalSplitter.addWidget(image_ax)
        self.horizontalSplitter.addWidget(self.verticalSplitter)

        mainLayout.addWidget(self.horizontalSplitter)

        self.horizontalSplitter.setSizes([600, 1000])
        self.verticalSplitter.setSizes([450, 150])

        self._main_controller.add_axes(
            "Image", "ImageAxes", self, image_ax
        )  # ax_dict["ImageAxes"]
        self._main_controller.add_axes("Trace", "FluoAxes", self, trace_ax1)
        self._main_controller.add_axes("Trace", "ElecAxes", self, trace_ax2)

        # connect x axis of windows
        self._main_controller.ax_dict["FluoAxes"].ax_obj.sigXRangeChanged.connect(
            self.sync_x_axes
        )
        self._main_controller.ax_dict["ElecAxes"].ax_obj.sigXRangeChanged.connect(
            self.sync_x_axes
        )

        # main buttons
        bottom_btn_layout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )

        # differential image
        self.dif_image_button = QtWidgets.QCheckBox("Differential Image")
        self.dif_image_button.setChecked(False)  # default
        self.dif_image_button.stateChanged.connect(self.dif_image_switch)
        mainLayout.addWidget(self.dif_image_button)

        # baseline compensation
        self.bl_comp_checkbox = QtWidgets.QCheckBox("Baseline Comp")
        self.bl_comp_checkbox.setChecked(False)  # default
        self.bl_comp_checkbox.stateChanged.connect(self.bl_comp)
        mainLayout.addWidget(self.bl_comp_checkbox)

        # radio check buttons for scale
        self.origin_trace = QtWidgets.QRadioButton("Original")
        self.dFoverF_trace = QtWidgets.QRadioButton("dF/F")
        self.normalized_trace = QtWidgets.QRadioButton("Normalize")
        # make a group
        self.trace_type = QtWidgets.QButtonGroup()
        self.trace_type.addButton(self.origin_trace)
        self.trace_type.addButton(self.dFoverF_trace)
        self.trace_type.addButton(self.normalized_trace)
        # default setting
        self.origin_trace.setChecked(True)
        self.current_checked_button = self.origin_trace
        # add buttons in the widget
        mainLayout.addWidget(self.origin_trace)
        mainLayout.addWidget(self.dFoverF_trace)
        mainLayout.addWidget(self.normalized_trace)
        # label. it need for label selection in self.scale
        self.scale_label = QtWidgets.QLabel("Selected: None")
        # send a signal for selected
        self.trace_type.buttonClicked.connect(self.scale)

        # file buttons
        load_btn = QtWidgets.QPushButton("Load")
        load_btn.setFixedSize(40, 30)
        bottom_btn_layout.addWidget(
            load_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )
        load_btn.clicked.connect(lambda: self.open_file())

        large_btn = QtWidgets.QPushButton("Large")
        large_btn.setFixedSize(60, 30)
        bottom_btn_layout.addWidget(
            large_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )
        large_btn.clicked.connect(lambda: self.roi_size("large"))

        small_btn = QtWidgets.QPushButton("Small")
        small_btn.setFixedSize(60, 30)
        bottom_btn_layout.addWidget(
            small_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )
        small_btn.clicked.connect(lambda: self.roi_size("small"))

        """ for baseline"""
        self.bl_roi_change_btn = QtWidgets.QCheckBox("BL")
        self.bl_roi_change_btn.setChecked(False)  # default
        self.bl_roi_change_btn.setFixedSize(40, 30)
        self.bl_roi_change_btn.clicked.connect(self.bl_roi)
        bottom_btn_layout.addWidget(
            self.bl_roi_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        """ for baseline use roi1"""
        self.bl_use_roi1 = QtWidgets.QCheckBox("BL Roi1")
        self.bl_use_roi1.setChecked(False)  # default
        self.bl_use_roi1.setFixedSize(60, 30)
        self.bl_use_roi1.clicked.connect(self.bl_use_roi1_switch)
        bottom_btn_layout.addWidget(
            self.bl_use_roi1, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        """ for baseline cutting time window"""
        self.bl_time_button = QtWidgets.QPushButton("BL cut")
        bottom_btn_layout.addWidget(
            self.bl_time_button, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.bl_time_button.clicked.connect(
            lambda: self.two_input_dialog("BlComp0", "FluoAxes")
        )

        """ values for the image"""
        self.image_time_button = QtWidgets.QPushButton("Img time window")
        bottom_btn_layout.addWidget(
            self.image_time_button, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.image_time_button.clicked.connect(
            lambda: self.two_input_dialog("TimeWindow0", "ImageAxes")
        )

        """ values for the difference image"""
        self.dif_button = QtWidgets.QPushButton("dif image")
        bottom_btn_layout.addWidget(
            self.dif_button, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.dif_button.clicked.connect(
            lambda: self.two_input_dialog("TimeWindow1", "ImageAxes")
        )

        """ for Fluo Ch """
        self.ch0_change_btn = QtWidgets.QCheckBox("Ch0")
        self.ch0_change_btn.setChecked(False)  # default
        self.ch0_change_btn.setFixedSize(50, 30)
        self.ch0_change_btn.clicked.connect(lambda: self.switch_ch("Ch0"))
        bottom_btn_layout.addWidget(
            self.ch0_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.ch1_change_btn = QtWidgets.QCheckBox("Ch1")
        self.ch1_change_btn.setChecked(True)  # default
        self.ch1_change_btn.setFixedSize(50, 30)
        self.ch1_change_btn.clicked.connect(lambda: self.switch_ch("Ch1"))
        bottom_btn_layout.addWidget(
            self.ch1_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.ch2_change_btn = QtWidgets.QCheckBox("Ch2")
        self.ch2_change_btn.setChecked(False)  # default
        self.ch2_change_btn.setFixedSize(50, 30)
        self.ch2_change_btn.clicked.connect(lambda: self.switch_ch("Ch2"))
        bottom_btn_layout.addWidget(
            self.ch2_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        """ for invert trace"""
        self.invert_switch = QtWidgets.QCheckBox("Invert")
        self.invert_switch.setChecked(False)  # default
        self.invert_switch.setFixedSize(60, 30)
        self.invert_switch.clicked.connect(self.invert_fn)
        bottom_btn_layout.addWidget(
            self.invert_switch, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        bottom_btn_layout.addSpacerItem(spacer)
        mainLayout.addLayout(bottom_btn_layout)

        """ for elec channel"""
        self.elec_ch1_change_btn = QtWidgets.QCheckBox("Ch1")
        self.elec_ch1_change_btn.setChecked(True)  # default
        self.elec_ch1_change_btn.setFixedSize(50, 30)
        self.elec_ch1_change_btn.clicked.connect(lambda: self.switch_elec_ch("Ch1"))
        bottom_btn_layout.addWidget(
            self.elec_ch1_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.elec_ch2_change_btn = QtWidgets.QCheckBox("Ch2")
        self.elec_ch2_change_btn.setChecked(False)  # default
        self.elec_ch2_change_btn.setFixedSize(50, 30)
        self.elec_ch2_change_btn.clicked.connect(lambda: self.switch_elec_ch("Ch2"))
        bottom_btn_layout.addWidget(
            self.elec_ch2_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.elec_ch3_change_btn = QtWidgets.QCheckBox("Ch3")
        self.elec_ch3_change_btn.setChecked(False)  # default
        self.elec_ch3_change_btn.setFixedSize(50, 30)
        self.elec_ch3_change_btn.clicked.connect(lambda: self.switch_elec_ch("Ch3"))
        bottom_btn_layout.addWidget(
            self.elec_ch3_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.elec_ch4_change_btn = QtWidgets.QCheckBox("Ch4")
        self.elec_ch4_change_btn.setChecked(False)  # default
        self.elec_ch4_change_btn.setFixedSize(50, 30)
        self.elec_ch4_change_btn.clicked.connect(lambda: self.switch_elec_ch("Ch4"))
        bottom_btn_layout.addWidget(
            self.elec_ch4_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.elec_ch5_change_btn = QtWidgets.QCheckBox("Ch5")
        self.elec_ch5_change_btn.setChecked(False)  # default
        self.elec_ch5_change_btn.setFixedSize(50, 30)
        self.elec_ch5_change_btn.clicked.connect(lambda: self.switch_elec_ch("Ch5"))
        bottom_btn_layout.addWidget(
            self.elec_ch5_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.elec_ch6_change_btn = QtWidgets.QCheckBox("Ch6")
        self.elec_ch6_change_btn.setChecked(False)  # default
        self.elec_ch6_change_btn.setFixedSize(50, 30)
        self.elec_ch6_change_btn.clicked.connect(lambda: self.switch_elec_ch("Ch6"))
        bottom_btn_layout.addWidget(
            self.elec_ch6_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.elec_ch7_change_btn = QtWidgets.QCheckBox("Ch7")
        self.elec_ch7_change_btn.setChecked(False)  # default
        self.elec_ch7_change_btn.setFixedSize(50, 30)
        self.elec_ch7_change_btn.clicked.connect(lambda: self.switch_elec_ch("Ch7"))
        bottom_btn_layout.addWidget(
            self.elec_ch7_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.elec_ch8_change_btn = QtWidgets.QCheckBox("Ch8")
        self.elec_ch8_change_btn.setChecked(False)  # default
        self.elec_ch8_change_btn.setFixedSize(50, 30)
        self.elec_ch8_change_btn.clicked.connect(lambda: self.switch_elec_ch("Ch8"))
        bottom_btn_layout.addWidget(
            self.elec_ch8_change_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft
        )

        """ mouse click event """
        image_ax.getView().scene().sigMouseClicked.connect(
            lambda event: self._main_controller.onclick_axes(event, "ImageAxes")
        )

    # timewindow = TimeWindow0 or BlComp,  axes is for update
    def two_input_dialog(self, timewindow, axes):
        dialog = InputDialog(self)
        if (
            dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted
        ):  # exec_() を exec() に変更
            val = dialog.get_numbers()
            if val is not None:
                print(f"Input values: {val}")
                self._main_controller.set_modifier_val(timewindow, val)
                self._main_controller.set_update_flag(axes, True)
                self._main_controller.update_view(axes)
            else:
                print("Only numerical values are available")

        # connect x axis of windows

    def sync_x_axes(self, view):
        # get the x axis setting of the fluo axes
        x_range1 = self._main_controller.ax_dict["FluoAxes"].ax_obj.viewRange()[0]

        # set the x axis of the elec axes
        self._main_controller.ax_dict["ElecAxes"].ax_obj.setXRange(
            x_range1[0], x_range1[1], padding=0
        )

        # get the x axis setting of the elec axes
        x_range2 = self._main_controller.ax_dict["ElecAxes"].ax_obj.viewRange()[0]

        # set the x axis of the fluo axes
        self._main_controller.ax_dict["FluoAxes"].ax_obj.setXRange(
            x_range2[0], x_range2[1], padding=0
        )

    """ button functions """

    def open_file(self, filename_obj=None):
        # make a model and get filename obj
        filename_obj, same_ext_file_list = self._main_controller.open_file(filename_obj)

        # make user controllers
        self._main_controller.create_default_modifier(0)  # filename number
        self._main_controller.default_settings(filename_obj.name)

        self._main_controller.print_infor()
        self._main_controller.update_view()
        self._main_controller.set_marker(ax_key="ImageAxes", roi_tag="Roi1")

        self.default()

    def default(self):
        self.bl_comp_checkbox.setChecked(True)
        self.bl_use_roi1.setChecked(True)
        self.bl_use_roi1_switch()
        self.dFoverF_trace.setChecked(True)
        self.scale(self.dFoverF_trace)

    def roi_size(self, command):
        if command == "large":
            val = [None, None, 1, 1]
        elif command == "small":
            val = [None, None, -1, -1]
        else:
            raise Exception("Should be Small or Large")
        self._main_controller.change_roi_size(val)

    def bl_roi(self):
        if self.bl_roi_change_btn.isChecked():
            self._main_controller.change_current_ax_mode(
                ax_key="FluoAxes", mode="Baseline"
            )
        else:
            self._main_controller.change_current_ax_mode(
                ax_key="FluoAxes", mode="Normal"
            )

    # under construction
    """
    def change_roi(self, state):
        if self..isChecked():
            remove_tag = 'Roi'
            add_tag = 'Roi0'
        else:
            remove_tag = 'Roi'
            add_tag = 'Roi1'
        self._main_controller.replace_key_manager_tag(
            'FluoAxes',
            'modifier_list',
            remove_tag,
            add_tag
        )
    """

    def scale(self, button):
        if self.current_checked_button == button:
            return

        self.current_checked_button = button
        if button:
            text = button.text()
            self.scale_label.setText(f"Selected: {text}")
            scale_values = {"dF/F": "DFoF", "Normalize": "Normalize"}
            selected_text = scale_values.get(text, "Original")
            # send value to modifier through main controller
            self._main_controller.set_modifier_val("Scale0", selected_text)
            self._main_controller.set_update_flag(ax_name="FluoAxes", flag=True)
            self._main_controller.update_view("FluoAxes")

    def bl_comp(self, state):
        if self.bl_comp_checkbox.isChecked():
            # activate baseline comp
            self._main_controller.set_modifier_val("BlComp0", "Exponential")
            self._main_controller.set_update_flag(ax_name="FluoAxes", flag=True)
            self._main_controller.update_view("FluoAxes")
        else:
            # disable baseline comp
            self._main_controller.set_modifier_val("BlComp0", "Disable")
            self._main_controller.set_update_flag(ax_name="FluoAxes", flag=True)
            self._main_controller.update_view("FluoAxes")

    def switch_bl_roi(self, state):
        raise NotImplementedError()

    def switch_ch(self, text):
        self._main_controller.set_tag(
            list_name="ch_list", new_tag=text, ax_key="FluoAxes"
        )
        self._main_controller.set_tag(
            list_name="ch_list", new_tag=text, ax_key="ImageAxes"
        )
        self._main_controller.set_update_flag(ax_name="FluoAxes", flag=True)
        self._main_controller.set_update_flag(ax_name="ImageAxes", flag=True)
        self._main_controller.update_view("FluoAxes")
        self._main_controller.update_view("ImageAxes")

    def switch_elec_ch(self, text):
        self._main_controller.set_tag(
            list_name="ch_list", new_tag=text, ax_key="ElecAxes"
        )
        self._main_controller.set_update_flag(ax_name="ElecAxes", flag=True)
        self._main_controller.update_view("ElecAxes")

    def dif_image_switch(self):
        self._main_controller.set_tag(
            list_name="modifier_list", new_tag="DifImage0", ax_key="ImageAxes"
        )
        if self.dif_image_button.isChecked():
            self._main_controller.change_color(color="plasma", ax_key="ImageAxes")
        else:
            self._main_controller.change_color(color="grey", ax_key="ImageAxes")
        self._main_controller.set_update_flag(ax_name="ImageAxes", flag=True)
        self._main_controller.update_view("ImageAxes")

    def bl_use_roi1_switch(self):
        if self.bl_use_roi1.isChecked():
            roi = "Roi1"
        else:
            roi = "Roi0"
        self._main_controller.replace_key_manager_tag(
            "FluoAxes", "bl_roi_list", "Roi", roi
        )
        self._main_controller.set_update_flag(ax_name="FluoAxes", flag=True)
        self._main_controller.update_view("FluoAxes")

    def invert_fn(self):
        self._main_controller.set_tag(
            list_name="modifier_list", new_tag="Invert0", ax_key="FluoAxes"
        )
        self._main_controller.set_update_flag(ax_name="FluoAxes", flag=True)
        self._main_controller.update_view("FluoAxes")


class InputDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("difference image: input values")
        self.setGeometry(100, 100, 200, 100)

        layout = QtWidgets.QVBoxLayout(self)

        self.inputs = []
        for i in range(2):
            number_input = QtWidgets.QLineEdit(self)
            if i == 0:
                number_input.setPlaceholderText("Start")
            elif i == 1:
                number_input.setPlaceholderText("width")
            self.inputs.append(number_input)
            layout.addWidget(number_input)

        self.ok_button = QtWidgets.QPushButton("OK", self)
        layout.addWidget(self.ok_button)

        # close dialog
        self.ok_button.clicked.connect(self.accept)

    def get_numbers(self):
        try:
            # return four numbers
            return [int(input_field.text()) for input_field in self.inputs]
        except ValueError:
            return None


class CustomImageView(pg.ImageView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # This is to ignore every mouse event.
        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        print(
            "yyyyyyyyyyyyyyCustomImageViewylmousePressEvent event ignoreyyyyyyyyyyyyyyyyy"
        )
        event.ignore()

    def mouseDragEvent(self, event):
        print(
            "xxxxxxxxxxxxxxxxxxxxCustomImageViewxPressEvent event ignoredxxxxxxxxxxxxxxxxxxxxx"
        )
        event.ignore()


if __name__ == "__main__":
    fullname = "..\\..\\220408\\20408B002.tsm"
    filename_obj = WholeFilename(fullname)

    scandata = PyQt6.QtWidgets.QApplication(sys.argv)
    mainWindow = QtDataWindow()
    mainWindow.open_file(filename_obj)
    mainWindow.show()

    if sys.flags.interactive == 0:
        scandata.exec()

    print("＝＝＝to do list＝＝＝")
    print("second trace time shift ")
    print("fix re-open method")
    print("")
