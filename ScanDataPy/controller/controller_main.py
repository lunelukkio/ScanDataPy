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
        self.__ax_dict = {}  # {"": ImageAxes class, FluoAxes: TraceAx class, FluoAxes: TraceAx class}\

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

        filename = self._key_manager.filename_list[0]
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

    # set values into controllers
    def get_data(self):
        # get lists of the data tag list
        lists_of_tag_list = self._key_manager.get_dicts_from_tag_list()
        # get modifier list
        modifier_list = self._key_manager.get_modifier_list()
        for tag_list in lists_of_tag_list:
            self.__model.get_data(tag_list, modifier_list)

    # set modifier values e.g. 'Roi1', [40, 40, 1, 1]. Be called by view and self.default_settings.
    def set_modifier_val(self, modifier, val):
        self.__model.set_modifier_val(modifier, val)


    def default_settings(self, filename_key):

        print("=============================================")
        print("========== Start default settings. ==========")
        print("=============================================")
        print("To Do: default setting should be moved into a json file")

        # get default information from text data in the json file
        #get the first of the filename true list
        filename = self._key_manager.filename_list[0]

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

    def set_observer(self, ax_name: str, modifier_tag: str) -> None:
        self.__ax_dict[ax_name].set_observer(modifier_tag)

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
                whole_dict_list = self._key_manager.get_key_dicts(True)
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
        whole_dict_list = self._key_manager.get_key_dicts(True)
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
        self._key_manager.set_key(dict_name, key, val)

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
        if ax_key == "All":
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
