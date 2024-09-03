# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:49:22 2024

@author: lunelukkio
"""

from abc import ABCMeta, abstractmethod

from ScanDataPy.model.modifiers import ModHandler
from ScanDataPy.model.modifiers import ModifierRepository
from SCANDATA.common_class import WholeFilename, Tools
from SCANDATA.model.user_controller import ROIFactory
from SCANDATA.model.user_controller import FluoTraceControllerFactory
from SCANDATA.model.user_controller import ImageControllerFactory
from SCANDATA.model.user_controller import ElecTraceControllerFactory

from SCANDATA.model.builder import TsmBuilder, DaBuilder, HekaBuilder
from SCANDATA.model.mod.mod_main import ModService


class ModelInterface(metaclass=ABCMeta):

    """
    Model interface controlled by MainController
    It has a data repository which have whole value object data.
    Basically, call set_modifier_values > 
    """
    
    # create data from experiments files.
    @abstractmethod
    def create_original_data(self, fullname):
        raise NotImplementedError()
        
    @abstractmethod
    def add_modifier(self, modifier_name):
        raise NotImplementedError()

    @abstractmethod
    def remove_modifier(self, modifier_name):
        raise NotImplementedError()
        
    # set modifier_values. e.g.:* args = (40, 40, 1, 1)
    @abstractmethod
    def add_modifier_values(self, modifier_tag: dict, *args, **kwargs):
        raise NotImplementedError()

    # make a new data from user_controller entities and save in the data_repository.
    @abstractmethod
    def create_data(self, data_tag):  #Needs 'Filename', 'Attribute', 'Ch', 'Origin', 'ControllerName'
        raise NotImplementedError()

    # return value object
    @abstractmethod
    def get_data(self, data_tag):
        raise NotImplementedError()




    # set an axes observer of view into modifier. If observer is empty, update all controllers.
    @abstractmethod
    def set_observer(self, controller_key, observer: object):
        raise NotImplementedError()

    # update_observer without changing.
    @abstractmethod
    def update_observer(self, key_dict=None):
        raise NotImplementedError()

    # reset modifier vals
    @abstractmethod
    def reset(self, controller_key):
        raise NotImplementedError()

    @abstractmethod
    def print_infor(self, filename_key):
        raise NotImplementedError()

        
class DataService(ModelInterface):
    def __init__(self):
        # repository for Roi, TimeWindow, DFoF
        self.__data_repository = Repository()
        self.__data_creator = DataCreator()

    def __create_filename_obj(self, fullname):
        filename_obj = WholeFilename(fullname)
        return filename_obj

    def __builder_selector(self, filename_obj):
        if filename_obj.extension == ".tsm":
            return TsmBuilder()
        elif filename_obj.extension == ".tbn":
            raise Exception("Select a .tsm file instead of a .tbn file!!!")
        elif filename_obj.extension == ".da":
            return DaBuilder()
        elif filename_obj.extension == ".dat":
            return HekaBuilder()
        else:
            raise Exception("This file is an undefineded file!!!")

    def create_experiments(self, fullname): # Use the same name to delete a model
        # make a filename value obj from fullname
        filename_obj = self.__create_filename_obj(fullname)

        # create default data set.
        builder = self.__builder_selector(filename_obj)
        # make value objects from a file.
        data_list = builder.create_data(filename_obj)
        for data in data_list:
            self.__data_repository.save(data)
        print("")
        print("===============================================================")
        print("==========DataService: Created new expriments data!!!==========")
        print("===============================================================")
        print("")

    def create_original_data(self, fullname):
        raise NotImplementedError()


class DataCreator:
    def __init__(self):
        # the first modifier
        self.__modifier_service = ModifierService{}
        self.start_modifier = StartModifier()
        self.current_modifier = None

    # make a chain for modifier
    def set_modifier(self, modifier_obj_list):
        # Reset start of chain of responsibility
        self.current_modifier = self.start_modifier
        # make chain
        for modifier in modifier_obj_list:
            self.current_modifier = self.current_modifier.set_next(modifier)

    # this is called by DataService for creating data
    def apply_modifier(self, data):
        # run chain of responsibility
        self.start_modifier.apply_modifier(data)


"""
Repository
"""

# ['Filename':'20408B002.tsm', 'ControllerName:'UserController', 'ControllerName':'ROI1', 'Ch':'Ch1', 'Origin':'File']
class Repository:
    def __init__(self):
        self._data = []  # list of object pointer

    @property
    def data(self):
        return self._data

    def save(self, data):
        # get all match keys objects.
        target_key_set = set(data.key_dict.values())
        extracted_data = [item for item in self._data if target_key_set.issubset(set(item.key_dict.values()))]
        if extracted_data == []:
            self._data.append(data)
            print(f"Repository: Saved object {list(data.key_dict.values())}")
        else:
            for remove_data in extracted_data:
                self._data.remove(remove_data)
                self._data.append(data)
                print(f"Repository: Overwrited overlapping object ({list(data.key_dict.values())})!!!")

        # e.g.  find_by_keys({'Attribute':'Data'}, {'Origin':'File','DataType':'ElecTrace'})

    def find_by_keys(self, target_key_dict: dict, except_dict=None) -> list:
        target_key_set = set(target_key_dict.values())
        extracted_data = [item for item in self._data if target_key_set.issubset(set(item.key_dict.values()))]
        if extracted_data == []:
            print(f"Repository: There is no data in {list(target_key_dict.values())}")
        # remove data from extracted_data using except_dict.
        elif except_dict is not None:
            extracted_data = [data for data in extracted_data
                              if not any(data.key_dict.get(key) == value for key,
                value in except_dict.items())]
        # print(f"Repository: Found {list(target_key_dict.values())}.")
        return extracted_data

    def delete(self, target_key_dict: dict):
        target_key_set = set(target_key_dict.values())
        extracted_data = [item for item in self._data if target_key_set.issubset(set(item.key_dict.values()))]
        for remove_data in extracted_data:
            self._data.remove(remove_data)
        print(f"Repository: {list(target_key_dict.values())} removed.")

        # e.g.  print_infor({'Attribute':'Data'}, {'Origin':'File','DataType':'ElecTrace'})

    def get_infor(self, target_key_dict=None, except_dict=None):
        if target_key_dict is None:
            extracted_data = self._data
            print("Show all infor:")
        else:
            target_key_set = set(target_key_dict.values())
            extracted_data = [item for item in self._data if target_key_set.issubset(set(item.key_dict.values()))]
            # remove data from extracted_data using except_dict.
            if except_dict:
                extracted_data = [data for data in extracted_data
                                  if not any(data.key_dict.get(key) == value for key,
                    value in except_dict.items())]
        for data in extracted_data:
            print(f"Repository: Infor = {list(data.key_dict.values())}")