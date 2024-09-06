# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 11:45:37 2022
lunelukkio@gmail.com
main for controller
"""

from abc import ABCMeta, abstractmethod
from ScanDataPy.model.model import DataService
from ScanDataPy.controller.controller_axes import TraceAxesController, \
    ImageAxesController
from ScanDataPy.common_class import FileService, KeyManager, Tools
import os
import copy


class ControllerInterface(metaclass=ABCMeta):
    """ MainController """

    @abstractmethod
    def add_axes(self, axes_name: str, axes: object) -> None:
        raise NotImplementedError()

    @abstractmethod
    def open_file(self, filename_obj):
        raise NotImplementedError()

    @abstractmethod
    def create_experiments(self, filename_obj):
        raise NotImplementedError()

    @abstractmethod
    def onclick_axes(self, event, axes_name):
        raise NotImplementedError()

    # set a new traces to user controller with value from experiments entity
    @abstractmethod
    def update_view(self, axes):
        raise NotImplementedError()

    """ Delegation to the Model """

    @abstractmethod
    def create_modifier(self, modifier_name):
        raise NotImplementedError()

        # set a new user controller values such as ROIVal.

    @abstractmethod
    def set_controller_val(self, controller_key: str, val: list):
        raise NotImplementedError()

    @abstractmethod
    def print_infor(self):
        raise NotImplementedError()

    """ Delegation to the AxesController """

    @abstractmethod
    def ax_print_infor(self, ax_key: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def set_roibox(self, controller_key, roi_box_pos):
        raise NotImplementedError()

    @abstractmethod
    def set_observer(self, controller_key: str, ax_num: int) -> None:
        raise NotImplementedError()

    """ Delegation to the Model """

    @abstractmethod
    def set_mod_key(self, controller_key, mod_key, val=None):
        raise NotImplementedError()

    @abstractmethod
    def set_trace_type(self, selected_test):
        raise NotImplementedError()

    # class MainController(ControllerInterface):


class MainController():
    def __init__(self, view=None):
        self.__model = DataService()
        self.__file_service = FileService()
        self.__key_manager = KeyManager()
        self.__ax_dict = {}  # {"": ImageAxes class, FluoAxes: TraceAx class, FluoAxes: TraceAx class}\

    def __del__(self):
        print('.')
        # print('Deleted a MainController.' + '  myId= {}'.format(id(self)))
        # pass

    @property
    def ax_dict(self):
        return self.__ax_dict

    """ MainController """

    def add_axes(self, ax_type, axes_name: str, canvas, ax: object) -> None:
        if ax_type == 'Image':
            new_axes_controller = ImageAxesController(self, self.__model,
                                                      canvas, ax)
        elif ax_type == 'Trace':
            new_axes_controller = TraceAxesController(self, self.__model,
                                                      canvas, ax)
        else:
            new_axes_controller = None
            raise Exception(f"There is no {ax_type} axes controller")
        self.__ax_dict[axes_name] = new_axes_controller

    def open_file(self, filename_obj=None) -> dict:
        # get filename object
        if filename_obj is None:
            filename_obj = self.__file_service.open_file()
        elif filename_obj.name == "":
            print("MainController: File opening is Cancelled!!")
            return {}

        # make experiments data
        open_experiments = self.create_experiments(filename_obj)
        if open_experiments is True:
            self.__key_manager.set_key('filename_dict', filename_obj.name, True)
            print(
                "============================================================================")
            print(
                f"========== MainController: Open {filename_obj.name}: suceeded!!! ==========          :)")
            print(
                "============================================================================")
            print("")
        else:
            print(
                "=============================================================")
            print(
                "========== MainController: Failed to open the file ==========                :(")
            print(
                "=============================================================")
            print("")

    def create_experiments(self, filename_obj: object):
        print("MainController: create_experiments() ----->")
        new_data = self.__model.create_experiments(filename_obj.fullname)
        # create_model end process
        if new_data is not True:
            raise Exception('Failed to create a model.')
        else:
            print("-----> MainController: create_experiments() Done")
            return True

    # filename number from the list in dict
    def create_default_modifier(self, filename_number):
        print("MainController: create_default_modifiers() ----->")

        filename = self.__key_manager.get_true_keys('filename_dict')[
            filename_number]
        # get default information from text data in the json file
        default = self.__model.get_data(
            {'Filename': filename, 'Attribute': 'Default', 'DataType': 'Text'})

        # default[0] because default is returned as value object list
        for modifier_name in default[0].data['default_controllers']:
            self.create_modifier(modifier_name)
        print("-----> MainController: create_default_modifier() Done")

        self.__model.print_infor('Modifier')
        print(
            "=======================================================================")
        print(
            "========== MainController: Made new Modifiers chain ==================")
        print(
            "=======================================================================")
        print("")

    def create_modifier(self, modifier_name):
        self.__model.add_modifier(modifier_name)

    def get_modifier_list(self):
        return self.__model.get_modifier_list()

        # take keys from data_repository and put them into the key_manager

    def set_keys_manager(self):
        print("MainController: set_keys_manager() ----->")
        # get the modifier name list
        modifier_name_list = self.get_modifier_list()
        # set list into key_manager
        self.__key_manager.set_key_list_to_dict(modifier_name_list)
        # get data_tag_dict
        list_of_tag_dict = self.__model.get_list_of_repository_tag_dict()
        # set data_tag to key_manager
        for tag_dict in list_of_tag_dict:
            self.__key_manager.set_dict_to_dict(tag_dict)
        print("===================== MainController =========================")
        # show key flags
        self.__key_manager.print_infor()
        # copy key manager to AxesController
        for ax in self.__ax_dict.values():
            ax.key_manager = copy.deepcopy(self.__key_manager)
        print("------> MainController: set_keys_manager() Done")

    # set data into controllers and generate data
    def set_data(self, val=None):  # val = None, True, False
        # get key dict whole conbinations
        key_dict_list = self.__key_manager.get_key_dicts(val)
        # print(key_dict_list)
        for key_dict in key_dict_list:
            self.__model.set_data(key_dict)

    def get_controller_infor(self, controller_key=None) -> dict:
        if controller_key is None:
            data_infor = self.__model.get_infor()
        else:
            data_infor = self.__model.get_infor(controller_key)
        return data_infor

    def update_view(self, axes=None) -> None:
        if axes is None:
            for ax in self.__ax_dict.values():
                ax.update()
                ax.set_update_flag(False)  # return to deactive
        else:
            self.__ax_dict[axes].update()
            self.__ax_dict[axes].set_update_flag(False)  # return to deactive
        print("Main controller: Update done!")
        print("")

    def default_settings(self, filename_key):

        print("=============================================")
        print("========== Start default settings. ==========")
        print("=============================================")
        print("To Do: default setting should be moved into a json file")

        self.set_observer('FluoAxes', 'ROI0')
        self.set_observer('FluoAxes', 'ROI1')
        self.set_observer('ImageAxes', 'TimeWindow0')
        self.set_observer('ImageAxes', 'TimeWindow1')
        self.set_observer('ElecAxes', 'TimeWindow2')




        # this is for test
        self.__model.set_modifier_val('Roi1',[40,40,5,5])








        # Reset controller flags
        self.__key_manager.set_key('controller_name_dict', 'ALL',
                                   False)  # see KeyManager in classcommon_class
        self.__key_manager.set_key('ch_dict', 'ALL', False)

        # set controller flags for operation
        self.__key_manager.set_key('controller_name_dict', 'ROI0', True)
        self.__key_manager.set_key('controller_name_dict', 'ROI1', True)
        self.__key_manager.set_key('controller_name_dict', 'ImageController1',
                                   True)
        self.__key_manager.set_key('controller_name_dict',
                                   'ElecTraceController1', True)
        self.__key_manager.set_key('ch_dict', 'Ch1', True)
        # self.__key_manager.set_key('ch_dict', 'Ch2', True)

        # set ax view flags
        for ax in self.ax_dict.values():
            ax.set_key('controller_name_dict', 'ALL',
                       False)  # see KeyManager in classcommon_class
            ax.set_key('ch_dict', 'ALL', False)

        # for the fluo trace window
        self.ax_dict['FluoAxes'].set_key('controller_name_dict', 'ROI1', True)
        self.ax_dict['FluoAxes'].set_key('ch_dict', 'Ch1', True)
        # self.ax_dict['FluoAxes'].set_key('ch_dict', 'Ch2', True)

        # for the image window
        self.ax_dict['ImageAxes'].set_key('controller_name_dict',
                                           'ImageController1', True)
        self.ax_dict['ImageAxes'].set_key('ch_dict', 'Ch1', True)

        # for the elec trace window
        self.ax_dict['ElecAxes'].set_key('controller_name_dict',
                                          'ElecTraceController1', True)
        self.ax_dict['ElecAxes'].set_key('ch_dict', 'Ch1', True)

        print("===================== MainController =========================")
        self.__key_manager.print_infor()
        print("")
        print("===================== AxesController =========================")
        for ax in self.ax_dict.values():
            ax.print_infor()

        # Mod settings
        print("tempral 88888888888888888888888888888888888888888888")
        # self.set_trace_type('FluoAxes', 'DFoF')
        # self.set_trace_type('FluoAxes', 'Normalize')
        self.set_trace_type('FluoAxes', 'BlComp')

        # Set ROI0 as background in ROI1 controller
        # send background ROI. but it done outside of the model.
        # background_dict = self.get_controller_data("ROI0")
        # self.set_mod_val("ROI1", "BGCOMP", background_dict)
        # Turn on the flag of BGCOMP for ROI1.
        # self.set_mod_key("ROI1", "BGCOMP")

        print("========== End of default settings ==========")
        print("")

    def set_observer(self, ax_name: str, modifier_tag: str) -> None:
        self.__ax_dict[ax_name].set_observer(modifier_tag)



















    def onclick_axes(self, event, axes_name):
        axes_name = axes_name.upper()

        if axes_name == "ImageAxes":
            image_pos = self.__ax_dict[
                "ImageAxes"]._ax_obj.getView().mapSceneToView(event.scenePos())
            if event.button() == 1:  # left click
                x = round(image_pos.x())
                y = round(image_pos.y())
                val = [x, y, None, None]

                # get True dict from key_manager of main controller
                whole_dict_list = self.__key_manager.get_key_dicts(True)
                roi_dict_list = [item for item in whole_dict_list if
                                 'ROI' in item['ControllerName']]
                for main_controller_dict in roi_dict_list:
                    # make a dict for a controller
                    controller_dict = Tools.extract_key(main_controller_dict,
                                                        ['ControllerName'])
                    # make a dict for data to distingish original files 
                    data_dict = main_controller_dict.copy()
                    data_dict['Origin'] = 'File'
                    # get data
                    self.__model.set_val(controller_dict, val)
                    self.__model.set_data(data_dict)
                self.update_view("FluoAxes")

            elif event.button() == 2:
                pass
            # move to next controller
            elif event.button() == 3:
                # move and copy ch boolen value
                self.__operating_controller_set.next_controller_to_true("ROI")
                self.__ax_dict["FluoAxes"].next_controller_to_true("ROI")
                self.update_view("FluoAxes")
        elif axes_name == "FluoAxes":
            if event.inaxes == self.__ax_dict["FluoAxes"]:
                raise NotImplementedError()
            elif event.inaxes == self.__ax_dict["ElecAxes"]:
                raise NotImplementedError()
        elif axes_name == "ElecAxes":
            raise NotImplementedError()

    def change_roi_size(self, val: list):
        controller_name = []
        new_roi_pos = []
        whole_dict_list = self.__key_manager.get_key_dicts(True)
        roi_dict_list = [item for item in whole_dict_list if
                         'ROI' in item['ControllerName']]
        for main_controller_dict in roi_dict_list:
            if main_controller_dict[
                'ControllerName'] in controller_name:  # avoid overwriting of ch1 and ch2
                controller_dict = Tools.extract_key(main_controller_dict,
                                                    ['ControllerName'])
                # make a dict for data to distingish original files 
                data_dict = main_controller_dict.copy()
                data_dict['Origin'] = 'File'
            else:
                # make a dict for a controller
                controller_dict = Tools.extract_key(main_controller_dict,
                                                    ['ControllerName'])
                # make a dict for data to distingish original files 
                data_dict = main_controller_dict.copy()
                data_dict['Origin'] = 'File'

                # get old roi position
                old_roi_pos = self.__model.get_controller(controller_dict)[
                    0].val_obj.data  # list shold have only one value
                new_roi_pos = [
                    old_roi_pos[0],
                    old_roi_pos[1],
                    old_roi_pos[2] + val[2],
                    old_roi_pos[3] + val[3]
                ]
            self.__model.set_val(controller_dict, new_roi_pos)
            self.__model.set_data(data_dict)
            controller_name.append(controller_dict['ControllerName'])
        self.update_view("FluoAxes")

    """ Delegation to the Model """

    def create_user_controller(self, controller_key):
        new_key = self.__model.create_user_controller(controller_key)
        return new_key

    # set UserController value. but not calculate data. Currently, self.update calculate data.
    def set_controller_val(self, val: list,
                           key_type=None):  # e.g. val = [x, y, None, None]
        controller_list = self.__operating_controller_set.get_true_list(
            "CONTROLLER", key_type)  # e.g. key_type = "ROI"
        for controller_key in controller_list:
            self.__model.set_controller_val(controller_key, val)
        print(f"{controller_list}: ", end='')

    def set_key(self, dict_name, key, val=None):
        self.__key_manager.set_key(dict_name, key, val)

    def print_infor(self):
        print("======================================")
        print("========== Data Information ==========")
        print("======================================")
        self.__model.print_infor()
        print("Operating controller list ---------->")
        self.__key_manager.print_infor()
        print("Axes controller infor ---------->")
        for ax in self.__ax_dict.values():
            ax.print_infor()
        print("========== Data Information End ==========")
        print("")

    def get_key_dict(self):
        return self.__singleton_key_dict.get_dict()

    def get_canvas_axes(self, view_controller) -> object:
        return self.__ax_dict[view_controller].get_canvas_axes()

    def set_trace_type(self, controller_axes, selected_text):
        if selected_text == 'Original':
            self.__ax_dict[controller_axes].set_mod_key_list('Original')
        elif selected_text == 'DFoF':
            self.__ax_dict[controller_axes].set_mod_key_list('DFoF')
        elif selected_text == 'Normalize':
            self.__ax_dict[controller_axes].set_mod_key_list('Normalize')
        elif selected_text == 'BlComp':
            self.__ax_dict[controller_axes].set_mod_key_list('BlComp')
        self.update_view("FluoAxes")

    """ Delegation to the AxesController """

    def set_view_flag(self, ax_key, controller_key, ch_key,
                      bool_val=None) -> None:
        if ax_key == "ALL":
            for ax in self.__ax_dict.values():
                ax.set_flag(controller_key, ch_key, bool_val)
        else:
            if ax_key not in self.__ax_dict:
                print(f"There is no Axes: {ax_key}")
            else:
                self.__ax_dict[ax_key].set_flag(controller_key, ch_key,
                                                bool_val)

    def update_flag_lock_sw(self, ax_key, val):
        self.__ax_dict[ax_key].update_flag_lock_sw(
            val)  # see AxesController class in conrtoller_axes.py

    def ax_print_infor(self, ax_key):
        self.__ax_dict[ax_key].print_infor()

    def set_roibox(self, controller_key, roi_box_pos):
        self.__ax_dict["ImageAxes"].set_roibox(controller_key, roi_box_pos)



    """ Delegation to the ModController """

    def set_mod_key(self, controller_key, mod_key, mod_val=None):
        self.__model.set_mod_key(controller_key, mod_key, mod_val)

    def show_data(self, target_dict, except_dict):
        # show datain data_repository
        self.__model.print_infor(target_dict, except_dict)


class AiController:
    def __init__(self):
        self.__file_service = FileService()

    def rename_files(self):
        self.__file_service.rename_files()
