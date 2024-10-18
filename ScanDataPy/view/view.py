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
import PyQt5
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtWidgets


class QtDataWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.__main_controller = MainController(self)
        self.setWindowTitle('SCANDATA')
        self.__live_camera_mode = False
        self.__live_camera_view = None

        # import a JSON setting file
        try:
            with open("./setting/data_window_setting.json", "r") as json_file:
                setting = json.load(json_file)
        except:
            with open("../setting/data_window_setting.json", "r") as json_file:
                setting = json.load(json_file)

        # window color, position and size
        self.setStyleSheet(
            "background-color: " +
            setting["main_window"]["color"] +
            ";"
        )
        self.setGeometry(
            setting["main_window"]["window_posX"],
            setting["main_window"]["window_posY"],
            setting["main_window"]["geometryX"],
            setting["main_window"]["geometryY"]
        )

        # set central widget
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QtWidgets.QVBoxLayout(centralWidget)
        size = centralWidget.size()

        # image window
        #image_ax = pg.ImageView()
        image_ax = CustomImageView()
        image_ax.ui.histogram.hide()  # hide contrast bar
        image_ax.ui.menuBtn.hide()  # hide a menu button
        image_ax.ui.roiBtn.hide()  # hide a ROI button
        view = image_ax.getView()
        view.setBackgroundColor(setting["main_window"]["color"])

        # for fix a image
        # it doesn't work
        image_item = image_ax.getImageItem()
        image_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)

        self.horizontalSplitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.verticalSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        trace_ax1 = pg.PlotWidget()
        trace_ax2 = pg.PlotWidget()
        self.verticalSplitter.addWidget(trace_ax1)
        self.verticalSplitter.addWidget(trace_ax2)

        trace_ax1.setBackground('white')
        trace_ax2.setBackground('white')
        trace_ax1.getAxis('bottom').setPen(pg.mkPen(color=(0, 0, 0), width=2))
        trace_ax1.getAxis('left').setPen(pg.mkPen(color=(0, 0, 0), width=2))
        trace_ax2.getAxis('bottom').setPen(pg.mkPen(color=(0, 0, 0), width=2))
        trace_ax2.getAxis('left').setPen(pg.mkPen(color=(0, 0, 0), width=2))
        trace_ax2.setLabel('bottom', 'Time (ms)', color='black', size=20,
                           width=2)

        self.horizontalSplitter.addWidget(image_ax)
        self.horizontalSplitter.addWidget(self.verticalSplitter)

        mainLayout.addWidget(self.horizontalSplitter)

        self.horizontalSplitter.setSizes([600, 1000])
        self.verticalSplitter.setSizes([450, 150])

        self.__main_controller.add_axes(
            'Image',
            'ImageAxes',
            self,
            image_ax
        )  # ax_dict["ImageAxes"]
        self.__main_controller.add_axes(
            'Trace',
            'FluoAxes',
            self,
            trace_ax1
        )
        self.__main_controller.add_axes(
            'Trace',
            'ElecAxes',
            self,
            trace_ax2
        )

        # connect x axis of windows
        self.__main_controller.ax_dict[
            "FluoAxes"].ax_obj.sigXRangeChanged.connect(self.sync_x_axes)
        self.__main_controller.ax_dict[
            "ElecAxes"].ax_obj.sigXRangeChanged.connect(self.sync_x_axes)

        # main buttons
        bottom_btn_layout = QtWidgets.QHBoxLayout(centralWidget)
        spacer = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum
        )

        # live view
        self.live_view_checkbox = QtWidgets.QCheckBox("Live View")
        self.live_view_checkbox.setChecked(False)  # default
        if self.__live_camera_mode:
            self.live_view_checkbox.stateChanged.connect(
                lambda: self.__live_camera_view.start_live_view())
        mainLayout.addWidget(self.live_view_checkbox)

        # baseline compensation
        self.bl_comp_checkbox = QtWidgets.QCheckBox("Baseline Comp")
        self.bl_comp_checkbox.setChecked(False)  # default
        self.bl_comp_checkbox.stateChanged.connect(self.bl_comp)
        mainLayout.addWidget(self.bl_comp_checkbox)

        # radio check buttons
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
        # label
        self.label = QtWidgets.QLabel("Selected: None")
        mainLayout.addWidget(self.label)
        # send a signal for selected
        self.trace_type.buttonClicked.connect(self.scale)

        # file buttons
        load_btn = QtWidgets.QPushButton("Load")
        load_btn.setFixedSize(30, 30)
        bottom_btn_layout.addWidget(load_btn, alignment=QtCore.Qt.AlignLeft)
        load_btn.clicked.connect(lambda: self.open_file())

        large_btn = QtWidgets.QPushButton("Large")
        large_btn.setFixedSize(100, 30)
        bottom_btn_layout.addWidget(large_btn, alignment=QtCore.Qt.AlignLeft)
        large_btn.clicked.connect(lambda: self.roi_size("large"))

        small_btn = QtWidgets.QPushButton("Small")
        small_btn.setFixedSize(100, 30)
        bottom_btn_layout.addWidget(small_btn, alignment=QtCore.Qt.AlignLeft)
        small_btn.clicked.connect(lambda: self.roi_size("small"))

        roi_change_btn = QtWidgets.QPushButton("BL")
        roi_change_btn.setFixedSize(30, 30)
        bottom_btn_layout.addWidget(roi_change_btn,
                                    alignment=QtCore.Qt.AlignLeft)
        roi_change_btn.clicked.connect(self.switch_bl_roi)
        bottom_btn_layout.addSpacerItem(spacer)

        mainLayout.addLayout(bottom_btn_layout)

        if self.__live_camera_mode:
            # override with live camera view
            from ScanDataPy.controller.controller_live_view import PcoPanda
            self.__live_camera_view = PcoPanda()
            self.__live_camera_view.set_axes(image_ax)
            """
            try:
                from SCANDATA.controller.controller_live_view import PcoPanda
                self.__live_camera_view = PcoPanda() 
                self.__live_camera_view.set_axes(image_ax)
                except:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("Failed to find a live camera!")
                    print("")
            """

        # mouse click event
        image_ax.getView().scene().sigMouseClicked.connect(
            lambda event: self.__main_controller.onclick_axes(
                event,
                "ImageAxes"
            )
        )

        # connect x axis of windows
    def sync_x_axes(self, view):
        # get the x axis setting of the fluo axes
        x_range1 = \
            self.__main_controller.ax_dict["FluoAxes"].ax_obj.viewRange()[0]

        # set the x axis of the elec axes
        self.__main_controller.ax_dict["ElecAxes"].ax_obj.setXRange(
            x_range1[0], x_range1[1], padding=0)

        # get the x axis setting of the elec axes
        x_range2 = \
            self.__main_controller.ax_dict["ElecAxes"].ax_obj.viewRange()[0]

        # set the x axis of the fluo axes
        self.__main_controller.ax_dict["FluoAxes"].ax_obj.setXRange(
            x_range2[0], x_range2[1], padding=0)

    def open_file(self, filename_obj=None):
        # make a model and get filename obj
        filename_obj = self.__main_controller.open_file(filename_obj)
        # make user controllers
        self.__main_controller.create_default_modifier(0)  # filename number
        self.__main_controller.default_settings(filename_obj.name)

        self.__main_controller.print_infor()
        self.__main_controller.update_view()
        self.__main_controller.set_maker()

    def roi_size(self, command):
        if command == "large":
            val = [None, None, 1, 1]
        elif command == "small":
            val = [None, None, -1, -1]
        else:
            raise Exception('Should be Small or Large')
        self.__main_controller.change_roi_size(val)

    def change_roi(self, state):
        self.__main_controller.operating_controller_set.next_controller_to_true(
            "ROI")
        # need modify
        # self.__main_controller.set_view_flag("FluoAxes", "ROI0", "CH1")  # (ax, controller_key, data_key, value)

    def scale(self, button):
        if self.current_checked_button != button:
            self.current_checked_button = button
            if button:
                text = button.text()
                self.label.setText(f"Selected: {text}")
                # change to keys from labels
                if button.text() == "dF/F":
                    selected_text = "DFoF"
                elif button.text() == "Normalize":
                    selected_text = "Normalize"
                else:
                    selected_text = "Original"
                # send value to modifier through main controller
                self.__main_controller.set_modifier_val(
                    'Scale0',
                    selected_text
                )
                self.__main_controller.set_scale("FluoAxes")
        else:
            return

    def bl_comp(self, state):
        if self.bl_comp_checkbox.isChecked():
            # activate baseline comp
            self.__main_controller.set_modifier_val(
                'BlComp0',
                'PolyVal'
            )
            self.__main_controller.set_update_flag('FluoAxes', True)
            self.__main_controller.update_view('FluoAxes')
        else:
            #disable baseline comp
            self.__main_controller.set_modifier_val(
                'BlComp0',
                'Disable'
            )
            self.__main_controller.set_update_flag('FluoAxes', True)
            self.__main_controller.update_view('FluoAxes')
            self.__main_controller.set_modifier_val('BlComp0', 'WindowClose')

    def switch_bl_roi(self, state):
        raise NotImplementedError()


class CustomImageView(pg.ImageView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # This is to ignore every mouse event.
        #self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setMouseTracking(True)

    """
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            print("zzzzzzzzzzzzzzzzzzCustomImageViewzmousePressEvent event ignorezzzzzzzzzzzz")
            event.ignore()
        else:
            #super().mousePressEvent(event)
            print("wwwwwwwwwwwCustomImageViewwmousePressEvent event ignorewwwwwwwww")
            #help(pg.ImageView)
            event.ignore()

    def mouseMoveEvent(self, event):
        print("yyyyyyyyyyyyyyCustomImageViewylmousePressEvent event ignoreyyyyyyyyyyyyyyyyy")
        event.ignore()

    def mouseDragEvent(self, event):
        print("xxxxxxxxxxxxxxxxxxxxCustomImageViewxPressEvent event ignoredxxxxxxxxxxxxxxxxxxxxx")
        event.ignore()

    def mouseReleaseEvent(self, event):
        print("vvvvvvvvvvvvvvvvvCustomImageViewvlmousePressEvent event ignorevvvvvvvvvvvvvvvv")
        print(event.button())
        if event.button() == QtCore.Qt.RightButton:
            print("uuuuuuuuuuuuuuuuuuuCustomImageViewuumousePressEvent eventuuuuuuuuuuuuuuuuuu")
            print(event.button())
            event.ignore()
        else:
            super().mouseReleaseEvent(event)
   """

if __name__ == '__main__':
    fullname = '..\\..\\220408\\20408B002.tsm'
    filename_obj = WholeFilename(fullname)

    scandata = PyQt5.QtWidgets.QApplication(sys.argv)
    mainWindow = QtDataWindow()
    mainWindow.open_file(filename_obj)
    mainWindow.show()

    if sys.flags.interactive == 0:
        scandata.exec_()

    print("＝＝＝to do list＝＝＝")
    print("second trace time shift ")
    print("fix re-open method")
    print("make difference image functions")
    print("")
