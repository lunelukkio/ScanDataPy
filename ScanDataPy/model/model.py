# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:49:22 2024

@author: lunelukkio
"""

from abc import ABCMeta, abstractmethod

from ScanDataPy.common_class import Tools
from ScanDataPy.common_class import WholeFilename
from ScanDataPy.model.modifier import ModifierService
from ScanDataPy.model.builder import TsmBuilder
from ScanDataPy.model.builder import DaBuilder
from ScanDataPy.model.builder import HekaBuilder


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
    def set_modifier_values(self, modifier_tag: dict, *args, **kwargs):
        raise NotImplementedError()

    # make a new data save in the data_repository.
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
    def update_observer(self, data_tag=None):
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
        self.__modifier_service = ModifierService()

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
        return True

    def add_modifier(self, modifier_name):
        self.__modifier_service.add_chain(modifier_name)

    def remove_modifier(self, modifier_name):
        self.__modifier_service.remove_chain(modifier_name)

    def set_modifier_values(self, modifier_tag: dict, *args, **kwargs):
        pass

    def create_original_data(self, fullname):
        pass

    def create_data(self, data_tag):  #Needs 'Filename', 'Attribute', 'Ch', 'Origin', 'ControllerName'
        pass

    def get_data(self, data_tag, modifier_list=None):
        modified_data_list = []
        print(f"DataService: get_data ({list(data_tag.values())}) ---------->")
        data_list = self.__data_repository.find_by_keys(data_tag)
        if data_list is None:
            print(f"DataService couldn't find {list(data_tag.values())} data")
            return
        for data in data_list:
            modified_data = self.__modifier_service.apply_modifier(data, modifier_list)
            # show gotten data
            print(modified_data.data_tag.values())
            #make a list again
            modified_data_list.append(modified_data)

        print("----------> Dataservice: get_data Done")
        return modified_data_list

    def get_modifier_name(self):
        return self.__modifier_service.get_chain_list()

    def print_infor(self, tag_dict=None, except_dict=None):
        print("Dataservice: print_infor ---------->")
        if tag_dict is None:
            self.__modifier_service.print_chain()
            self.__data_repository.get_infor()
        elif tag_dict == 'Modifier':
            self.__modifier_service.print_chain()
        else:
            self.__data_repository.get_infor(tag_dict, except_dict)
        print("----------> Dataservice: print_infor END")
        print("")

    def reset(self):
        pass

    def set_observer(self):
        pass

    def update_observer(self):
        pass

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
        target_key_set = set(data.data_tag.values())
        extracted_data = [item for item in self._data if target_key_set.issubset(set(item.data_tag.values()))]
        if extracted_data == []:
            self._data.append(data)
            print(f"Repository: Saved object {list(data.data_tag.values())}")
        else:
            for remove_data in extracted_data:
                self._data.remove(remove_data)
                self._data.append(data)
                print(f"Repository: Overwrited overlapping object ({list(data.data_tag.values())})!!!")

        # e.g.  find_by_keys({'Attribute':'Data'}, {'Origin':'File','DataType':'ElecTrace'})

    def find_by_keys(self, target_data_tag: dict, except_dict=None) -> list:
        target_key_set = set(target_data_tag.values())
        extracted_data = [item for item in self._data if target_key_set.issubset(set(item.data_tag.values()))]
        if extracted_data == []:
            print(f"Repository: There is no data in {list(target_data_tag.values())}")
        # remove data from extracted_data using except_dict.
        elif except_dict is not None:
            extracted_data = [data for data in extracted_data
                              if not any(data.data_tag.get(key) == value for key,
                value in except_dict.items())]
        # print(f"Repository: Found {list(target_data_tag.values())}.")
        return extracted_data

    def delete(self, target_data_tag: dict):
        target_key_set = set(target_data_tag.values())
        extracted_data = [item for item in self._data if target_key_set.issubset(set(item.data_tag.values()))]
        for remove_data in extracted_data:
            self._data.remove(remove_data)
        print(f"Repository: {list(target_data_tag.values())} removed.")

        # e.g.  print_infor({'Attribute':'Data'}, {'Origin':'File','DataType':'ElecTrace'})

    def get_infor(self, target_data_tag=None, except_dict=None):
        if target_data_tag is None:
            extracted_data = self._data
            print("Show all infor:")
        else:
            target_key_set = set(target_data_tag.values())
            extracted_data = [item for item in self._data if target_key_set.issubset(set(item.data_tag.values()))]
            # remove data from extracted_data using except_dict.
            if except_dict:
                extracted_data = [data for data in extracted_data
                                  if not any(data.data_tag.get(key) == value for key,
                    value in except_dict.items())]
        for data in extracted_data:
            print(f"Repository: Infor = {list(data.data_tag.values())}")