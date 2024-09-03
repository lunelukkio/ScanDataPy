# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 11:45:37 2022
lunelukkio@gmail.com
main for controller
"""

from abc import ABCMeta, abstractmethod
from SCANDATA.model.model_main import DataService
from SCANDATA.controller.controller_axes import TraceAxesController, ImageAxesController
from SCANDATA.common_class import FileService, KeyManager, Tools
import os
import psutil  # for memory check
import copy
    

class ControllerInterface(metaclass=ABCMeta):
    """
    MainController 
    """
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
        
    """
    Delegation to the Model
    """ 
    @abstractmethod
    def create_user_controller(self, controller_key):
        raise NotImplementedError() 
  
    # set a new user controller values such as ROIVal.
    @abstractmethod
    def set_controller_val(self, controller_key: str, val: list):
        raise NotImplementedError() 

        
    @abstractmethod
    def print_infor(self):
        raise NotImplementedError() 
        
    """
    Delegation to the AxesController
    """   

        
    @abstractmethod
    def ax_print_infor(self, ax_key: str) -> None:
        raise NotImplementedError()
        
    @abstractmethod
    def set_roibox(self, controller_key, roi_box_pos):
        raise NotImplementedError()
        
    @abstractmethod
    def set_observer(self, controller_key: str, ax_num: int) -> None:
        raise NotImplementedError() 
    
    """
    Delegation to the Model
    """
    @abstractmethod
    def set_mod_key(self, controller_key, mod_key, val=None):
        raise NotImplementedError() 
    
    @abstractmethod
    def set_trace_type(self, selected_test):
        raise NotImplementedError() 
        

class MainController(ControllerInterface):
    def __init__(self, view=None):
        self.__model = DataService()
        self.__file_service = FileService()
        self.__key_manager = KeyManager()
        self.__ax_dict = {}  # {"IMAGE_AXES": ImageAxsis class, FLUO_AXES: TraceAx class, ELEC_AXES: TraceAx class}\

    def __del__(self):
        print('.')
        #print('Deleted a MainController.' + '  myId= {}'.format(id(self)))
        #pass
        
    @property
    def ax_dict(self):
        return self.__ax_dict
        
    """
    MainController 
    """
    def add_axes(self, ax_type, axes_name: str, canvas, ax: object) -> None:
        if ax_type == "IMAGE":
            new_axes_controller = ImageAxesController(self, self.__model, canvas, ax)
        elif ax_type == "TRACE":
            new_axes_controller = TraceAxesController(self, self.__model, canvas, ax)
        self.__ax_dict[axes_name] = new_axes_controller
    
    def open_file(self, filename_obj=None) -> dict:
        # get filename object
        if filename_obj is None:
            filename_obj = self.__file_service.open_file()
        if filename_obj.name == "":
            print("MainController: File openning is Cancelled!!")
            return
        # make experiments data
        open_experiments = self.create_experiments(filename_obj) 
        if open_experiments is True:
            self.__key_manager.set_key('filename_dict', filename_obj.name, True)
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
        self.__model.create_experiments(filename_obj.fullname)
        # create_model end proccess
        if self.__model == None:
            raise Exception('Failed to create a model.')
        else:
            return True
        print("-----> MainController: create_experiments() Done")
        
    def create_default_controller(self, filename_number):
        print("MainController: create_default_controller() ----->")
        filename = self.__key_manager.get_true_keys('filename_dict')[filename_number]  # filename number from the list in dict
        default = self.__model.get_data({'Filename':filename,'Attribute':'Default', 'DataType':'Text'})  # get default information
        for controller_key_without_number in default[0].data['default_controllers']:
            # create data
            print("MainController: create_user_controller() ----->")
            self.__model.create_user_controller(controller_key_without_number)
            print("-----> MainController: create_user_controller() Done")
            
        self.__model.print_infor({'Attribute': 'UserController'})
        print("=======================================================================")
        print("========== MainController: Made new User Controllers ==================")
        print("=======================================================================")
        print("")
        
        # take keys from data_repository and put them into the key_manager
    def set_user_controller_keys_to_manager(self):
        print("MainController: set_user_controller_keys_to_manager() ----->")
        controllers = self.__model.get_controller({})
        for controller in controllers:
            # copy controller names from the repository to the key manager
            self.__key_manager.set_key('controller_name_dict', controller.key_dict['ControllerName'], True)
        whole_data = self.__model.get_data({})
        for data in whole_data:
            # copy controller names from the repository to the key manager
            if 'Ch' in data.key_dict and data.key_dict['Ch'] is not None:
                # copy ch names from the repository to the key manager
                self.__key_manager.set_key('ch_dict', data.key_dict['Ch'], True)
        print("===================== MainController =========================")
        # show key flags
        self.__key_manager.print_infor()
        for ax in self.__ax_dict.values():
            ax.key_manager = copy.deepcopy(self.__key_manager)
        print("------> MainController: set_user_controller_keys_to_manager() Done")
                
    # set data into controllers and generate data
    def set_data(self, val=None):  # val = None, True, False
        # get key dict whole conbinations
        key_dict_list = self.__key_manager.get_key_dicts(val)
        #print(key_dict_list)
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
        
        self.set_observer({'Attribute':'UserController', 'ControllerName':'ROI0'}, 'FLUO_AXES')   #background for bg_comp, (controller_key, AXES number)
        self.set_observer({'Attribute':'UserController', 'ControllerName':'ROI1'}, 'FLUO_AXES')
        self.set_observer({'Attribute':'UserController', 'ControllerName':'ImageController0'}, 'IMAGE_AXES')  # base image for difference image
        self.set_observer({'Attribute':'UserController', 'ControllerName':'ImageController1'}, 'IMAGE_AXES')  # base image for difference image
        self.set_observer({'Attribute':'UserController', 'ControllerName':'ElecTraceController0'}, 'ELEC_AXES')  # no use
        self.set_observer({'Attribute':'UserController', 'ControllerName':'ElecTraceController1'}, 'ELEC_AXES')  # no use
        
        # Reset controller flags
        self.__key_manager.set_key('controller_name_dict', 'ALL', False)  # see KeyManager in classcommon_class 
        self.__key_manager.set_key('ch_dict', 'ALL', False)
        
        # set controller flags for operation
        self.__key_manager.set_key('controller_name_dict', 'ROI0', True)
        self.__key_manager.set_key('controller_name_dict', 'ROI1', True) 
        self.__key_manager.set_key('controller_name_dict', 'ImageController1', True) 
        self.__key_manager.set_key('controller_name_dict', 'ElecTraceController1', True) 
        self.__key_manager.set_key('ch_dict', 'Ch1', True)
        #self.__key_manager.set_key('ch_dict', 'Ch2', True)
           
        # set ax view flags
        for ax in self.ax_dict.values():
            ax.set_key('controller_name_dict', 'ALL', False)  # see KeyManager in classcommon_class 
            ax.set_key('ch_dict', 'ALL', False)
            
        # for the fluo trace window
        self.ax_dict['FLUO_AXES'].set_key('controller_name_dict', 'ROI1', True) 
        self.ax_dict['FLUO_AXES'].set_key('ch_dict', 'Ch1', True)  
        #self.ax_dict['FLUO_AXES'].set_key('ch_dict', 'Ch2', True) 
        
        # for the image window
        self.ax_dict['IMAGE_AXES'].set_key('controller_name_dict', 'ImageController1', True)    
        self.ax_dict['IMAGE_AXES'].set_key('ch_dict', 'Ch1', True)    
        
        # for the elec trace window
        self.ax_dict['ELEC_AXES'].set_key('controller_name_dict', 'ElecTraceController1', True)  
        self.ax_dict['ELEC_AXES'].set_key('ch_dict', 'Ch1', True) 
        
        print("===================== MainController =========================")
        self.__key_manager.print_infor()
        print("")
        print("===================== AxesController =========================")
        for ax in self.ax_dict.values():
            ax.print_infor()
        
        # Mod settings
        print("tempral 88888888888888888888888888888888888888888888")
        #self.set_trace_type('FLUO_AXES', 'DFoF')
        #self.set_trace_type('FLUO_AXES', 'Normalize')
        self.set_trace_type('FLUO_AXES', 'BlComp')

        
        # Set ROI0 as background in ROI1 controller
        # send background ROI. but it done outside of the model.
        #background_dict = self.get_controller_data("ROI0")
        #self.set_mod_val("ROI1", "BGCOMP", background_dict)
        # Turn on the flag of BGCOMP for ROI1.
        #self.set_mod_key("ROI1", "BGCOMP")
        """
        # set background roi to the mod class
        self.set_mod_val("ROI1", "BgCompMod")
        
        # set mod
        self.set_mod_key("ROI2", "BGCOMP")
        """

        print("========== End of default settings ==========")
        print("")
    
    def get_memory_infor(self):
        pid = os.getpid()
        process = psutil.Process(pid)
        memory_infor = process.memory_info().rss
        maximum_memory = psutil.virtual_memory().total
        available_memory = psutil.virtual_memory().available
        return memory_infor, maximum_memory, available_memory
    
    def onclick_axes(self, event, axes_name):
        axes_name = axes_name.upper()

        if axes_name == "IMAGE_AXES":
            image_pos = self.__ax_dict["IMAGE_AXES"]._ax_obj.getView().mapSceneToView(event.scenePos())
            if event.button() == 1:  # left click
                x = round(image_pos.x())
                y = round(image_pos.y())
                val = [x, y, None, None]
                
                # get True dict from key_manager of main controller
                whole_dict_list = self.__key_manager.get_key_dicts(True)
                roi_dict_list = [item for item in whole_dict_list if 'ROI' in item['ControllerName']]
                for main_controller_dict in roi_dict_list:
                    # make a dict for a controller
                    controller_dict = Tools.extract_key(main_controller_dict, ['ControllerName'])
                    # make a dict for data to distingish original files 
                    data_dict = main_controller_dict.copy()
                    data_dict['Origin'] = 'File'
                    # get data
                    self.__model.set_val(controller_dict, val)
                    self.__model.set_data(data_dict)
                self.update_view("FLUO_AXES")
                
            elif event.button() == 2:
                pass
            # move to next controller
            elif event.button() == 3:
                # move and copy ch boolen value
                self.__operating_controller_set.next_controller_to_true("ROI")
                self.__ax_dict["FLUO_AXES"].next_controller_to_true("ROI")
                self.update_view("FLUO_AXES")
        elif axes_name == "FLUO_AXES":
            if event.inaxes == self.__ax_dict["FLUO_AXES"]:
                raise NotImplementedError()
            elif event.inaxes == self.__ax_dict["ELEC_AXES"]:
                raise NotImplementedError()
        elif axes_name == "ELEC_AXES":
           raise NotImplementedError() 
        
    def change_roi_size(self, val:list):
        controller_name = []
        new_roi_pos = []
        whole_dict_list = self.__key_manager.get_key_dicts(True)
        roi_dict_list = [item for item in whole_dict_list if 'ROI' in item['ControllerName']]
        for main_controller_dict in roi_dict_list:
            if main_controller_dict['ControllerName'] in controller_name:  # avoid overwriting of ch1 and ch2
                controller_dict = Tools.extract_key(main_controller_dict, ['ControllerName'])
                # make a dict for data to distingish original files 
                data_dict = main_controller_dict.copy()
                data_dict['Origin'] = 'File'
            else:
                # make a dict for a controller
                controller_dict = Tools.extract_key(main_controller_dict, ['ControllerName'])
                # make a dict for data to distingish original files 
                data_dict = main_controller_dict.copy()
                data_dict['Origin'] = 'File'
                
                # get old roi position
                old_roi_pos = self.__model.get_controller(controller_dict)[0].val_obj.data  # list shold have only one value
                new_roi_pos = [
                    old_roi_pos[0], 
                    old_roi_pos[1], 
                    old_roi_pos[2]+val[2], 
                    old_roi_pos[3]+val[3]
                ]
            self.__model.set_val(controller_dict, new_roi_pos)
            self.__model.set_data(data_dict)
            controller_name.append(controller_dict['ControllerName'])
        self.update_view("FLUO_AXES")

    """
    Delegation to the Model
    """           
    def create_user_controller(self, controller_key):
        new_key = self.__model.create_user_controller(controller_key)
        return new_key
    
    # set UserController value. but not calculate data. Currently, self.update calculate data.
    def set_controller_val(self, val: list, key_type=None):  # e.g. val = [x, y, None, None]
        controller_list = self.__operating_controller_set.get_true_list("CONTROLLER", key_type)  # e.g. key_type = "ROI"
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
        self.update_view("FLUO_AXES") 
        
    """
    Delegation to the AxesController
    """               
    def set_view_flag(self, ax_key, controller_key, ch_key, bool_val=None) -> None:
        if ax_key == "ALL":
            for ax in self.__ax_dict.values():
                ax.set_flag(controller_key, ch_key, bool_val)
        else:
            if ax_key not in self.__ax_dict:
                print(f"There is no Axes: {ax_key}")
            else:
                self.__ax_dict[ax_key].set_flag(controller_key, ch_key, bool_val)

    def update_flag_lock_sw(self, ax_key, val):
        self.__ax_dict[ax_key].update_flag_lock_sw(val)  # see AxesController class in conrtoller_axes.py
        
    def ax_print_infor(self, ax_key):
        self.__ax_dict[ax_key].print_infor()
        
    def set_roibox(self, controller_key, roi_box_pos):
        self.__ax_dict["IMAGE_AXES"].set_roibox(controller_key, roi_box_pos)
        
    def set_observer(self, controller_key: str, ax_name: str) -> None:
        self.__ax_dict[ax_name].set_observer(controller_key)
    
    """
    Delegation to the ModController
    """        
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



