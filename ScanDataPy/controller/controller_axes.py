# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 09:01:53 2023

@author: lunel
"""

from abc import ABCMeta, abstractmethod
from ScanDataPy.common_class import KeyManager
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
            with open("../setting/data_window_setting.json", "r") as json_file:
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
    def set_view_data(self, active_controller_dict):
        raise NotImplementedError()







    def next_controller_to_true(self, controller):
        self._view_flag_set.next_controller_to_true(controller)

    def get_canvas_axes(self):
        return self._canvas, self._ax_obj

    # to get a controller valueobject
    def get_controller_val(self, controller_key) -> object:
        return self._model.get_controller_val(controller_key)

    # get value object from controllers
    def get_controller_data(self, controller_key) -> dict:
        data_dict = self._model.get_controller_data(controller_key)
        if data_dict is None:
            print(f"Can't find data_dict in {controller_key}")
        else:
            return data_dict



    def set_mod_key_list(self, mod_key):
        if mod_key == 'Original':
            self._mod_key_list = []
        elif mod_key == 'DFoF':
            if 'Normalize' in self._mod_key_list:
                self._mod_key_list.remove('Normalize')
            self._mod_key_list.append('DFoF')
        elif mod_key == 'Normalize':
            if 'DFoF' in self._mod_key_list:
                self._mod_key_list.remove('DFoF')
            self._mod_key_list.append('Normalize')
        elif mod_key == 'BlComp':
            if 'BlComp' in self._mod_key_list:
                self._mod_key_list.remove('BlComp')
            else:
                self._mod_key_list.append('BlComp')

        print(
            f"AxesController: Current mod set[{self.__class__.__name__}]: {self._mod_key_list}")



    def update_flag_lock_sw(self, val=None) -> None:
        if val is True:
            self.update_flag_lock = True
        elif val is False:
            self.update_flag_lock = False
        else:
            self.update_flag_lock = not self.update_flag_lock

    # update flag from the UserController classes in the model
    def set_update_flag(self, update_flag):
        if self.update_flag_lock == True:
            pass
        else:
            self.update_flag = update_flag



    def print_infor(self):
        print(f"{self.__class__.__name__} current data list = ")
        self._key_manager.print_infor()


class TraceAxesController(AxesController):
    def __init__(self, main_controller, model, canvas,
                 ax):  # controller is for getting ROI information from FLU-AXES.
        super().__init__(main_controller, model, canvas, ax)

    def update(self):
        if self.update_flag is True:
            # clear axes variables
            #self._ax_obj.clear()
            # delete old image objects. not delete box
            print("88888888888888888888888888888888888888888888888888888888888888888888888888888888 should be not clear?")
            self.ax_item_dict = {}
            # make white background
            print("999999999999999999999999999999999999999999999999999999999999999999999999999999999 should it be here?")
            self._ax_obj.setBackground('w')
            # See each subclass.
            self.set_view_data()
            # for RoiBOX
            self.set_marker()
            # axes method
            self._ax_obj.autoRange()
            print(f"AxesController: {self.__class__.__name__} updated")
        else:
            pass

    # from the flag, get data from the model and show data. 
    def set_view_data(self):
        # get true key_dict list
        true_dict_list = self._key_manager.get_key_dicts(True)
        for true_dict in true_dict_list:
            # get data list. This case list shold be only one value.
            data = self._model.get_data(true_dict, self._mod_key_list)
            # show data of the value object
            plot_data = data[0].show_data(self._ax_obj)
            # combaine keys
            item_key = ''.join(true_dict.values())
            # make a new item dict for a graph
            self.ax_item_dict[item_key] = plot_data

            self.mode = 'CH_MODE'
            color = None
            # color setting
            if self.mode == "CH_MODE":
                for key in true_dict.values():
                    if 'Elec' in key:
                        plot_data.setPen(
                            pg.mkPen(color=self._ch_colors['Elec0']))
                        return
                    for color in self._ch_colors:
                        if key in color:
                            if color:
                                plot_data.setPen(
                                    pg.mkPen(color=self._ch_colors[key]))
            elif self.mode == "ROI_MODE":
                for key in true_dict.values():
                    if 'Elec' in key:
                        plot_data.setPen(
                            pg.mkPen(color=self._ch_colors['Elec0']))
                        return
                    print(true_dict.values())
                    for color in self._controller_colors:
                        if key in color:
                            if color:
                                print(self._controller_colors[key])
                                plot_data.setPen(pg.mkPen(
                                    color=self._controller_colors[key]))

    def set_marker(self):
        # get flag data from ImageAxes
        image_canvas, image_axes = self._main_controller.get_canvas_axes(
            "ImageAxes")
        # get a true flag list of dict
        true_controller_list = self._key_manager.get_key_dicts(True)
        for controller_dict in true_controller_list:
            # pick up ROI controller names
            roi_controller_list = [key for key in controller_dict.values() if
                                   "ROI" in key]
        for controller_key in roi_controller_list:
            # get roi value
            controller_list = self._model.get_controller(
                {'Attribute': 'UserController',
                 'ControllerName': controller_key})
            for controller in controller_list:
                roi_val = controller.val_obj.data
                # if need, box_pos is for adjusting box posision as pixels 0.5
                box_pos = [
                    roi_val[0],
                    roi_val[1],
                    roi_val[2],
                    roi_val[3]
                ]
            if controller_key in self._marker_obj:
                self._marker_obj[controller_key].set_roi(box_pos)
            else:
                self._marker_obj[controller_key] = RoiBox(
                    self._controller_colors[controller_key])
                self._marker_obj[controller_key].set_roi(box_pos)
                # put the ROI BOX on the top of images.
                self._marker_obj[controller_key].rectangle_obj.setZValue(1)
                image_axes.addItem(
                    self._marker_obj[controller_key].rectangle_obj)




class ImageAxesController(AxesController):
    def __init__(self, main_controller, model, canvas, ax):
        super().__init__(main_controller, model, canvas, ax)
        self.mode = None  # no use

    def set_click_position(self, event):
        raise NotImplementedError()

    # from the flag, get data from the model and show data. 
    def set_view_data(self):
        # get true key_dict list
        true_dict_list = self._key_manager.get_key_dicts(True)
        for true_dict in true_dict_list:
            # get data list. This case list shold be only one value.
            data = self._model.get_data(true_dict, self._mod_key_list)
            # show data of the value object
            plot_data = data[0].show_data(self._ax_obj)
            # combaine keys
            item_key = ''.join(true_dict.values())
            # make a new item dict for a graph
            self.ax_item_dict[item_key] = plot_data

    # override    shold be in main conrtoller         
    def update(self) -> None:
        if self.update_flag is True:
            # delete old image objects. not delete box
            self.ax_item_dict = {}
            self.set_view_data()  # This belong to Image Controller
            print(f"AxesController: {self.__class__.__name__} updated")
        else:
            pass


class RoiBox():
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
