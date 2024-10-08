# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 09:01:53 2023

@author: lunel
"""

from abc import ABCMeta, abstractmethod
from ScanDataPy.common_class import KeyManager, Tools
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

# import matplotlib.patches as patches
# from matplotlib.image import AxesImage
import json


class AxesController(metaclass=ABCMeta):
    def __init__(self, main_controller, model, canvas, ax):
        self._tools = AxesTools(ax)
        self._canvas = canvas
        self._ax_obj = ax
        self._main_controller = main_controller
        self._model = model

        self._key_manager = KeyManager()  # see common class

        self.ax_item_dict = {}
        self._marker_obj = {}  # This is for makers in axes windows.

        self.update_flag = False  # Ture or False or empty: flip flag.
        self.update_flag_lock = False  # to skip ImageAxe update

        # color selection for traces and ROiooxes
        try:
            with open("./setting/data_window_setting.json", "r") as json_file:
                setting = json.load(json_file)
        except:
            with open("../setting/data_window_setting.json", "r") as json_file:
                setting = json.load(json_file)
        self._ch_colors = setting.get("ch_color")
        self._controller_colors = setting.get("controller_color")

    @property
    def key_manager(self):
        return self._key_manager

    @property
    def view_flag_set(self):
        return self._view_flag_set

    @property
    def ax_obj(self):
        return self._ax_obj

    @property
    def key_manager(self):
        return self._key_manager

    @key_manager.setter
    def key_manager(self, key_dict):
        self._key_manager = key_dict

    def set_key(self, dict_name, key, val=None):
        self._key_manager.set_key(dict_name, key, val)

    def set_observer(self, modifier_tag) -> None:
        self._model.set_observer(modifier_tag, self)

    @abstractmethod
    def update(self):
        raise NotImplementedError()

    @abstractmethod
    def get_view_data(self):
        raise NotImplementedError()

    def get_canvas_axes(self):
        return self._canvas, self._ax_obj

    # update flag from the UserController classes in the model
    def set_update_flag(self, update_flag):
        if self.update_flag_lock == True:
            pass
        else:
            self.update_flag = update_flag

    def print_infor(self):
        print(f"{self.__class__.__name__} current data list = ")
        self._key_manager.print_infor()






    def update_flag_lock_sw(self, val=None) -> None:
        if val is True:
            self.update_flag_lock = True
        elif val is False:
            self.update_flag_lock = False
        else:
            self.update_flag_lock = not self.update_flag_lock




    def next_controller_to_true(self, controller):
        self._view_flag_set.next_controller_to_true(controller)









class ImageAxesController(AxesController):
    def __init__(self, main_controller, model, canvas, ax):
        super().__init__(main_controller, model, canvas, ax)
        self.mode = None  # no use

    def set_click_position(self, event):
        raise NotImplementedError()

    # from the flag, get data from the model and show data.
    def get_view_data(self):
        # get lists of the data tag list
        lists_of_tag_dict = self._key_manager.get_dicts_from_tag_list()
        # get modifier list
        modifier_list = self._key_manager.get_modifier_list()

        for tag_dict in lists_of_tag_dict:
            value_obj = self._model.get_data(tag_dict, modifier_list)
            # show data
            plot_data = value_obj.show_data(self._ax_obj)
            # combine keys  e.g. '20408B002.tsmDataFluoImageCh1Average0'
            item_key = ''.join(value_obj.data_tag.values())
            # make a new item dict for a graph
            self.ax_item_dict[item_key] = plot_data

    # override    should be in main controller
    def update(self) -> None:
        if self.update_flag is True:
            # delete old image objects. not delete box
            self.ax_item_dict = {}
            self.get_view_data()  # This belong to Image Controller
            print(f"AxesController: {self.__class__.__name__} updated")
        else:
            pass


class TraceAxesController(AxesController):
    def __init__(self, main_controller, model, canvas,
                 ax):  # controller is for getting ROI information from FLU-AXES.
        super().__init__(main_controller, model, canvas, ax)
        self.mode = 'ChMode'

    def update(self):
        if self.update_flag is True:
            # clear axes variables
            self._ax_obj.clear()
            # See each subclass.
            value_obj = self.get_view_data()
            # for RoiBOX
            if 'FluoTrace' in value_obj.data_tag['DataType']:
                self.set_marker(value_obj)
            # axes method
            self._ax_obj.autoRange()
            print(f"AxesController: {self.__class__.__name__} updated")
        else:
            pass

    # from the flag, get data from the model and show data. 
    def get_view_data(self):
        # get lists of the data tag list
        lists_of_tag_dict = self._key_manager.get_dicts_from_tag_list()
        # get modifier list
        modifier_list = self._key_manager.get_modifier_list()
        for tag_dict in lists_of_tag_dict:
            value_obj = self._model.get_data(tag_dict, modifier_list)

            # show data
            plot_data = value_obj.show_data(self._ax_obj)
            # combine keys  e.g. '20408B002.tsmDataFluoTraceCh1Average0'
            item_key = ''.join(value_obj.data_tag.values())
            # make a new item dict for a graph
            self.ax_item_dict[item_key] = plot_data

            # color setting
            if self.mode == "ChMode":
                if 'Elec' in value_obj.data_tag['DataType']:
                    plot_data.setPen(
                        pg.mkPen(color=self._ch_colors[value_obj.data_tag['DataType']]))
                elif 'Fluo' in value_obj.data_tag['DataType']:
                    plot_data.setPen(
                        pg.mkPen(color=self._ch_colors[value_obj.data_tag['DataType']]))
                else:
                    plot_data.setPen(
                        pg.mkPen(color=self._ch_colors["black"]))
            elif self.mode == "RoiMode":
                if 'Elec' in value_obj.data_tag['DataType']:
                    plot_data.setPen(
                        pg.mkPen(color=self._ch_colors[value_obj.data_tag['DataType']]))
                    print(tag_dict.values())
                elif 'Fluo' in value_obj.data_tag['Origin']:
                    plot_data.setPen(
                        pg.mkPen(color=self._ch_colors[
                            value_obj.data_tag['Origin']]))
                else:
                    plot_data.setPen(
                        pg.mkPen(color=self._ch_colors["black"]))

        return value_obj

    def set_marker(self, value_obj):
        roi_tag_list = []
        # get flag data from ImageAxes
        image_canvas, image_axes = self._main_controller.get_canvas_axes(
            "ImageAxes")
        modifier_name = value_obj.data_tag['Origin']
        modifier_val_obj = self._model.get_modifier_val(modifier_name)

        roi_val = modifier_val_obj.data
        # if need, box_pos is for adjusting box position as pixels 0.5
        box_pos = [
            roi_val[0],
            roi_val[1],
            roi_val[2],
            roi_val[3]
        ]
        if modifier_name in self._marker_obj:
            self._marker_obj[modifier_name].set_roi(box_pos)
        else:
            self._marker_obj[modifier_name] = RoiBox(
                self._controller_colors[modifier_name])
            self._marker_obj[modifier_name].set_roi(box_pos)
            # put the ROI BOX on the top of images.
            self._marker_obj[modifier_name].rectangle_obj.setZValue(1)
            image_axes.addItem(
                self._marker_obj[modifier_name].rectangle_obj)

    def change_scale(self):
        current_filename = self._key_manager.filename_list[0]
        current_ch = self._key_manager.ch_list[0]
        current_baseline_roi = self._key_manager.baseline_roi_list[0]
        modifier_tag_list = [
            'TimeWindow3',
            current_baseline_roi,
            'Average1',
            'Scale0',
            'TagMaker0'
        ]
        # This tag dict is to find original data.
        self._model.set_data(
            {
                'Filename': current_filename,
                'Attribute': 'Data',
                'DataType': 'FluoFrames' + current_ch,
                'Origin': 'File'
            }, modifier_tag_list
        )

        self.set_update_flag('FluoAxes', True)
        self.update_view('FluoAxes')


class RoiBox:
    # """ class variable """
    # color_selection = ['white', 'red', 'blue', 'green', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan', 'orange']

    # """ instance method """
    def __init__(self, color):
        self.__rectangle_obj = QtWidgets.QGraphicsRectItem(40, 40, 1, 1)
        self.__rectangle_obj.setPen(pg.mkPen(color=color, width=0.7))
        self.__rectangle_obj.setBrush(pg.mkBrush(None))

    def set_roi(self, roi_val):
        x, y, width, height = roi_val
        self.__rectangle_obj.setRect(x, y, width, height)

    def delete(self):
        raise NotImplementedError()

    @property
    def rectangle_obj(self):
        return self.__rectangle_obj


class AxesTools:
    def __init__(self, axes):
        self.axes = axes

    def axes_patches_check(self, target_class):
        target_list = []
        for target in self.axes.patches:
            if isinstance(target, target_class):
                target_list.append(target)
        return target_list
