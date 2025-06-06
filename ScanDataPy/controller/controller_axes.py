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
        self._canvas = canvas
        self._ax_obj = ax
        self._main_controller = main_controller
        self._model = model
        self._key_manager = KeyManager()  # see common class
        self.current_mode = 'Normal'    # Normal, Baseline,

        self.ax_item_dict = {}
        self._marker_obj_dict = {}  # This is for makers in axes windows.

        self.update_flag = False  # Ture or False or empty: flip flag.
        self.update_flag_lock = False  # to skip ImageAxe update

        # color selection for traces and ROiooxes
        setting = None
        search_paths = [
            "./setting/data_window_setting.json",
            "../setting/data_window_setting.json",
            "./ScanDataPy/setting/data_window_setting.json"
        ]
        
        for path in search_paths:
            try:
                with open(path, "r") as json_file:
                    setting = json.load(json_file)
                print(f"AxesController: Successfully loaded settings from: {path}")
                break
            except FileNotFoundError:
                continue
            except json.JSONDecodeError:
                print(f"AxesController: Error: {path} is not a valid JSON file")
                continue
            except Exception as e:
                print(f"AxesController: Unexpected error while reading {path}: {str(e)}")
                continue
        
        if setting is None:
            print("AxesController: Error: Could not find or load data_window_setting.json in any of these locations:")
            for path in search_paths:
                print(f"- {path}")
            raise FileNotFoundError("AxesController: No valid settings file found")

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

    def set_tag(self, list_name, key):
        self._key_manager.set_tag(list_name, key)

    def set_observer(self, modifier_tag) -> None:
        self._model.set_observer(modifier_tag, self)

    @abstractmethod
    def update(self):
        raise NotImplementedError()

    @abstractmethod
    def get_view_data(self):
        raise NotImplementedError()

    def set_scale(self):
        raise NotImplementedError()

    def get_canvas_axes(self):
        return self._canvas, self._ax_obj

    # update flag from the UserController classes in the model
    def set_update_flag(self, update_flag):
        if self.update_flag_lock == True:
            pass
        else:
            self.update_flag = update_flag

    def set_data(self, data_tag, modifier_list=None):
        self._model.set_data(self, data_tag, modifier_list)

    def get_data(self, data_tag, modifier_list=None):
        self._model.get_data(self, data_tag, modifier_list)

    # return only items with modifier_name in list_name.
    def get_key_list(self, list_name, modifier_name='All'):
        if modifier_name == 'All':
            return self._key_manager.get_list(list_name)
        else:
            return [name for name in self._key_manager.get_list(list_name)
                                  if modifier_name in name]

    def replace_key_manager_tag(self, list_name, old_tag, new_tag):
        self._key_manager.replace_tag(list_name, old_tag, new_tag)

    def change_color(self, color):
        self.color_mode = color

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











class ImageAxesController(AxesController):
    def __init__(self, main_controller, model, canvas, ax):
        super().__init__(main_controller, model, canvas, ax)
        self.mode = None  # no use
        self.color_mode = 'grey'

    def set_click_position(self, event):
        raise NotImplementedError()

    # from the flag, get data from the model and show data.
    def get_view_data(self):
        # get lists of the data tag list
        lists_of_tag_dict = self._key_manager.get_dicts_from_tag_list()
        # get modifier list
        modifier_list = self._key_manager.get_list('modifier_list')

        for tag_dict in lists_of_tag_dict:
            value_obj = self._model.get_data(tag_dict, modifier_list)
            # show data
            plot_data = value_obj.show_data(self._ax_obj)
            # combine keys  e.g. '20408B002.tsmDataFluoImageCh1Average0'
            item_key = ''.join(value_obj.data_tag.values())
            # make a new item dict for a graph
            self.ax_item_dict[item_key] = plot_data
            self._ax_obj.setPredefinedGradient(self.color_mode)

    # override    should be in main controller
    def update(self) -> None:
        if self.update_flag is True:
            # delete old image objects. not delete box
            self._ax_obj.clear()
            self.ax_item_dict = {}
            self.get_view_data()  # This belong to Image Controller
            print(f"AxesController: {self.__class__.__name__} updated")
        else:
            pass

    def set_marker(self, roi_tag):
        modifier_val_obj = self._model.get_modifier_val(roi_tag)
        roi_val = modifier_val_obj.data
        # if need, box_pos is for adjusting box position as pixels 0.5
        box_pos = [
            roi_val[0],
            roi_val[1],
            roi_val[2],
            roi_val[3]
        ]
        if roi_tag in self._marker_obj_dict:  # if roi_tag is already in the dict
            # set box_pos into roi box obj
            self._marker_obj_dict[roi_tag].set_roi(box_pos)
        else:  # if not, make new RoiBox instance
            self._marker_obj_dict[roi_tag] = RoiBox(
                self._controller_colors[roi_tag])
            self._marker_obj_dict[roi_tag].set_roi(box_pos)
            # put the ROI BOX on the top of images.
            self._marker_obj_dict[roi_tag].rectangle_obj.setZValue(1)
            self._ax_obj.addItem(
                self._marker_obj_dict[roi_tag].rectangle_obj)

    def set_scale(self):
        raise NotImplementedError()

    def make_second_obj(self, data_type):
        current_filename = self._key_manager.filename_list[0]
        baseline_data_tag = {
            'Filename': current_filename,
            'Attribute': 'Data',
            'DataType': data_type,
            'Origin': 'File'
        }
        # TimeWindow = [5,-1], -1 means whole trace. see modifier.TimeWindow()
        baseline_modifier_tag_list = [
            'TimeWindow1',
            'Average0'
        ]
        # return to modifier BlComp class
        return self._model.get_data(baseline_data_tag, baseline_modifier_tag_list)


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
            self.get_view_data()
            # axes method
            self._ax_obj.autoRange()
            print(f"AxesController: {self.__class__.__name__} updated")
        else:
            print("TraceAxesController: update flag is False")

    def change_current_ax_mode(self, mode):
        self.current_mode = mode

    # from the flag, get data from the model and show data. 
    def get_view_data(self):
        # get lists of the data tag list
        lists_of_tag_dict = self._key_manager.get_dicts_from_tag_list()
        # get modifier list
        modifier_list = self._key_manager.get_list('modifier_list')
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

    def onclick_axes(self, val):
        if self.current_mode == 'Normal':
            modifier_name_list = self.get_key_list('modifier_list', 'Roi')
        elif self.current_mode == 'Baseline':
            modifier_name_list = self.get_key_list('bl_roi_list', 'Roi')
        for modifier_name in modifier_name_list:

            # set modifier values
            self._model.set_modifier_val(modifier_name, val)
            return modifier_name

    def change_roi_size(self, val: list):
        if self.current_mode == 'Normal':
            modifier_name_list = [name for name in self._key_manager.modifier_list if 'Roi' in name]
        elif self.current_mode == 'Baseline':
            modifier_name_list = self.get_key_list('bl_roi_list', 'Roi')
        for modifier_name in modifier_name_list:
            # set modifier values
            self._model.set_modifier_val(modifier_name, val)
            return modifier_name

    # Be called by modifier.BlComp.observer.notify_observer_baseline()
    def make_second_obj(self, data_type):
        current_filename = self._key_manager.filename_list[0]
        current_baseline_roi = self._key_manager.bl_roi_list[0]
        baseline_data_tag = {
            'Filename': current_filename,
            'Attribute': 'Data',
            'DataType': data_type,
            'Origin': 'File'
        }
        # TimeWindow = [5,-1], -1 means whole trace. see modifier.TimeWindow()
        baseline_modifier_tag_list = [
            'TimeWindow3',
            current_baseline_roi,
            'Average1',
            'TagMaker0'
        ]
        # return to modifier BlComp class
        return self._model.get_data(baseline_data_tag, baseline_modifier_tag_list)

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
