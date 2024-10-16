# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 11:45:37 2022
lunelukkio@gmail.com
main for controller
"""

from abc import ABCMeta, abstractmethod

from ScanDataPy.model.model import DataService
from ScanDataPy.controller.controller_axes import TraceAxesController
from ScanDataPy.controller.controller_axes import ImageAxesController
from ScanDataPy.common_class import FileService, KeyManager, Tools


class ControllerInterface(metaclass=ABCMeta):
    """ MainController """

    @abstractmethod
    def get_filename(self):
        raise NotImplementedError()

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


    """ Delegation to the AxesController """

    @abstractmethod
    def ax_print_infor(self, ax_key: str) -> None:
        raise NotImplementedError()


    @abstractmethod
    def set_observer(self, controller_key: str, ax_num: int) -> None:
        raise NotImplementedError()


class MainController():
    def __init__(self, view=None):
        self.__model = DataService()
        self.__file_service = FileService()
        self._key_manager = KeyManager()
        self.__ax_dict = {}  # {"": ImageAxes class, FluoAxes: TraceAx class, ElecAxes: TraceAx class}\
        self.current_filename = [0]
        self.current_roi = [1]

    def __del__(self):
        print('.')
        # print('Deleted a MainController.' + '  myId= {}'.format(id(self)))
        # pass

    @property
    def ax_dict(self):
        return self.__ax_dict

    @property
    def key_manager(self):
        return self._key_manager

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

    def get_canvas_axes(self, view_controller) -> object:
        return self.__ax_dict[view_controller].get_canvas_axes()

    def open_file(self, filename_obj=None) -> dict:
        self.__reset()
        # get filename object
        if filename_obj is None:
            filename_obj = self.__file_service.open_file()
        elif filename_obj.name == "":
            print("MainController: File opening is Cancelled!!")
            return {}
        # make experiments data
        open_experiments = self.create_experiments(filename_obj)
        if open_experiments is True:
            self._key_manager.set_key('filename_list', filename_obj.name)
            print("============================================================================")
            print(f"========== MainController: Open {filename_obj.name}: suceeded!!! ==========          :)")
            print("============================================================================")
            print("")
        else:
            print("=============================================================")
            print("========== MainController: Failed to open the file ==========                :(")
            print("=============================================================")
            print("")
        return filename_obj

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

        filename = self._key_manager.filename_list[self.current_filename[0]]
        # get default information from text data in the json file
        default = self.__model.get_data(
            {'Filename': filename, 'Attribute': 'Default', 'DataType': 'Text'})

        for modifier_name in default.data['default_settings']['default_modifiers']:
            self.create_modifier(modifier_name)
        print("-----> MainController: create_default_modifier() Done")

        self.__model.print_infor('Modifier')
        print("=======================================================================")
        print("========== MainController: Made new Modifiers chain ==================")
        print("=======================================================================")
        print("")

    def create_modifier(self, modifier_name):
        self.__model.add_modifier(modifier_name)

    def set_observer(self, ax_name: str, modifier_tag: str) -> None:
        self.__ax_dict[ax_name].set_observer(modifier_tag)

    # set modifier values e.g. 'Roi1', [40, 40, 1, 1]. Be called by view and self.default_settings.
    def set_modifier_val(self, modifier, *args, **kwargs):
        self.__model.set_modifier_val(modifier, *args, **kwargs)

    def onclick_axes(self, event, axes_name):
        if axes_name == 'ImageAxes':
            # get clicked position
            image_pos = self.__ax_dict['ImageAxes']._ax_obj.getView().mapSceneToView(event.scenePos())
            if event.button() == 1:  # left click
                x = round(image_pos.x())
                y = round(image_pos.y())
                val = [x, y, None, None]
                roi_tag = self.__ax_dict['FluoAxes'].onclick_axes(val)
                self.update_view('FluoAxes')
                # for RoiBOX
                self.__ax_dict['ImageAxes'].set_marker(roi_tag)

            elif event.button() == 2:
                self.current_roi[0] = (self.current_roi[0] + 1) % len(self._key_manager.roi_list)
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
        modifier_name_list = [name for name in self.__ax_dict[
            'FluoAxes']._key_manager.modifier_list if 'Roi' in name]
        for modifier_name in modifier_name_list:
            # set modifier values
            self.set_modifier_val(modifier_name, val)
        self.update_view('FluoAxes')

    def set_scale(self,ax_key):
        self.set_update_flag('FluoAxes', True)
        self.update_view('FluoAxes')

    def default_settings(self, filename_key):

        print("=============================================")
        print("========== Start default settings. ==========")
        print("=============================================")

        # get default information from text data in the json file
        #get the first of the filename true list
        filename = self._key_manager.filename_list[self.current_filename[0]]

        # get default information from JSON
        default = self.__model.get_data(
            {'Filename': filename, 'Attribute': 'Default', 'DataType': 'Text'})
        default_observer = default.data['default_settings']['default_observer']

        # set_observer. see KeyManager and  file_setting.json
        for key, item_list in default_observer.items():
            for value in item_list:
                self.set_observer(key, value)

        # MainController default settings from file_setting.json
        main_default_tag_list = default.data['default_settings']['main_default_tag']
        # set_keys.   see KeyManager and file_setting.json in class common_class set_key_list_to_dict, set_dict_to_dict
        for tag_list_name, tag_list in main_default_tag_list.items():
            for tag in tag_list:
                self._key_manager.set_key(tag_list_name, tag)
        # show the final default infor of the main controller
        print("============ MainController key manager infor =============")
        self._key_manager.print_infor()

        # set ax view flags
        self.ax_dict['FluoAxes'].key_manager.set_key('filename_list', filename)
        fluo_default_tag_list = default.data['default_settings']['trace_ax_default_tag']
        for tag_list_name, tag_list in fluo_default_tag_list.items():
            for tag in tag_list:
                self.ax_dict['FluoAxes'].key_manager.set_key(tag_list_name, tag)
        # show the final default infor of the main controller
        print("========== Trace AxesController key manager infor =========")
        self.ax_dict['FluoAxes']._key_manager.print_infor()

        self.ax_dict['ImageAxes'].key_manager.set_key('filename_list', filename)
        image_default_tag_list = default.data['default_settings']['image_ax_default_tag']
        for tag_list_name, tag_list in image_default_tag_list.items():
            for tag in tag_list:
                self.ax_dict['ImageAxes'].key_manager.set_key(tag_list_name, tag)
        # show the final default infor of the main controller
        print("========== Image AxesController key manager infor =========")
        self.ax_dict['ImageAxes']._key_manager.print_infor()

        self.ax_dict['ElecAxes'].key_manager.set_key('filename_list', filename)
        elec_default_tag_list = default.data['default_settings']['elec_ax_default_tag']
        for tag_list_name, tag_list in elec_default_tag_list.items():
            for tag in tag_list:
                self.ax_dict['ElecAxes'].key_manager.set_key(tag_list_name, tag)
        # show the final default infor of the main controller
        print("========== Elec AxesController key manager infor ==========")
        self.ax_dict['ElecAxes']._key_manager.print_infor()

        # default modifiers values.
        default_values_list = default.data['default_settings']['modifier_default_val']
        for modifier, value in default_values_list.items():
            self.set_modifier_val(modifier, value)

        print("========== End of default settings ==========")
        print("")

        # this is for test
        #self.__model.set_modifier_val('Roi1',[40,40,5,5])

    def set_update_flag(self, ax_name, flag):
        self.__ax_dict[ax_name].set_update_flag(flag)

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

    def __reset(self):
        self.__model.reset()
        self.__file_service.reset()
        self._key_manager.reset()
        for ax in self.__ax_dict.values():
            ax.key_manager.reset()

    def print_infor(self):
        print("======================================")
        print("========== Data Information ==========")
        print("======================================")
        self.__model.print_infor()
        print("Operating controller list ---------->")
        self._key_manager.print_infor()
        print("Axes controller infor ---------->")
        for ax in self.__ax_dict.values():
            ax.print_infor()
        print("========== Data Information End ==========")
        print("")








    # no use
    def update_flag_lock_sw(self, ax_key, val):
        self.__ax_dict[ax_key].update_flag_lock_sw(
            val)  # see AxesController class in conrtoller_axes.py

    # no use
    def ax_print_infor(self, ax_key):
        self.__ax_dict[ax_key].print_infor()

    # no use
    def show_data(self, target_dict, except_dict):
        # show data in data_repository
        self.__model.print_infor(target_dict, except_dict)


class AiController:
    def __init__(self):
        self.__file_service = FileService()

    def rename_files(self):
        self.__file_service.rename_files()
