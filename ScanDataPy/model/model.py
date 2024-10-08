# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:49:22 2024

@author: lunelukkio
"""

from abc import ABCMeta, abstractmethod
import copy
from logging import raiseExceptions

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


    @abstractmethod
    def add_modifier(self, modifier_name):
        raise NotImplementedError()

    @abstractmethod
    def remove_modifier(self, modifier_name):
        raise NotImplementedError()

    # set modifier_values. e.g.:* args = (40, 40, 1, 1)
    @abstractmethod
    def set_modifier_val(self, modifier_tag: dict, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def set_data(self, data_tag, modifier_list_list=None):
        raise NotImplementedError()

    # return value object
    @abstractmethod
    def get_data(self, data_tag, modifier_list_list=None):
        raise NotImplementedError()

    @abstractmethod
    def get_list_of_repository_tag_dict(self, filename_key):
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

    def create_experiments(self,
                           fullname):  # Use the same name to delete a model
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

    def set_modifier_val(self, modifier_name, *args, **kwargs):
        self.__modifier_service.set_modifier_val(modifier_name, *args, **kwargs)

        # This is for saving data to repository
    def set_data(self, data_tag, modifier_list=None) -> object:
        print(f"DataService: set_data ({list(data_tag.values())}) ---------->")
        # create data
        modified_value_obj = self.__create_data(data_tag, modifier_list)
        # save in the repository
        self.__data_repository.save(modified_value_obj)
        print("----------> Dataservice: set_data Done")
        return modified_value_obj

        # This is for sending data to frontend.
    def get_data(self, data_tag, modifier_list=None):
        print(f"DataService: get_data ({list(data_tag.values())}) ---------->")
        # create data
        modified_value_obj = self.__create_data(data_tag, modifier_list)
        print("----------> Dataservice: get_data Done")
        return modified_value_obj

    def __create_data(self, data_tag, modifier_list=None):
        # get data from repository
        data_list = self.__data_repository.find_by_keys(data_tag)

        assert type(data_list) == list, f"DataService couldn't find {list(data_tag.values())} data"
        assert len(data_list) <=1, f"DataService found more than two data {list(data_tag.values())} data. It should be only a single data."

        # pass or modify
        if modifier_list is None:
            modified_data = data_list[0]

            print(f"DataService: get data without modified-> {modified_data.data_tag.values()}")
        else:
            # apply modifier. the number of data in data_list should be 0.
            modified_data = self.__modifier_service.apply_modifier(data_list[0],
                                                               modifier_list)
            # show gotten data
            print(f"DataService: get modified data -> {modified_data.data_tag.values()}")

        return modified_data

    def get_list_of_repository_tag_dict(self):
        return self.__data_repository.get_list_of_tag_dict()

    def reset(self):
        self.__data_repository = Repository()
        self.__modifier_service = ModifierService()

    def set_observer(self, modifier_tag, observer):
        print(f"DataService: set_observer ({observer.__class__.__name__} to {modifier_tag}) ---------->")
        found = False
        modifier_obj_list = self.__modifier_service.modifier_chain_list
        for modifier_obj in modifier_obj_list:
            if modifier_obj.modifier_name == modifier_tag:
                modifier_obj.set_observer(observer)
                found = True
        print("----------> Dataservice: set_observer Done")
        if found is not True:
            raise ValueError(f"These is no much tag {modifier_tag}")

    def update_observer(self):
        pass

    def get_modifier_val(self, modifier_name):
        return self.__modifier_service.get_modifier_val(modifier_name)

    def print_infor(self, tag_dict=None, except_dict=None):
        print("Dataservice: print_infor ---------->")
        if tag_dict is None:
            self.__modifier_service.print_chain()
            self.__data_repository.print_infor()
        elif tag_dict == 'Modifier':
            self.__modifier_service.print_chain()
        else:
            self.__data_repository.print_infor(tag_dict, except_dict)
        print("----------> Dataservice: print_infor END")
        print("")
"""
Repository
"""


# ['Filename':'20408B002.tsm', 'Attribute':'Data', 'DataType':'FluoTraceCh1', 'Origin':'File']
class Repository:
    def __init__(self):
        self._data = []  # list of object pointer

    @property
    def data(self):
        return self._data

    def save(self, data):
        # get all match keys objects.
        target_key_set = set(data.data_tag.values())
        extracted_data = [item for item in self._data if
                          target_key_set.issubset(set(item.data_tag.values()))]
        if extracted_data == []:
            self._data.append(data)
            print(f"Repository: Saved object {list(data.data_tag.values())}")
        else:
            for remove_data in extracted_data:
                self._data.remove(remove_data)
                self._data.append(data)
                print(
                    f"Repository: Overwrite overlapping object ({list(data.data_tag.values())})!!!")

        # e.g.  find_by_keys({'Attribute':'Data'}, {'Origin':'File','DataType':'ElecTrace'})

    def find_by_keys(self, target_data_tag: dict, except_dict=None) -> list:
        target_key_set = set(target_data_tag.values())
        extracted_data = [item for item in self._data if
                          target_key_set.issubset(set(item.data_tag.values()))]
        if extracted_data == []:
            print(
                f"Repository: There is no data in {list(target_data_tag.values())}")
        # remove data from extracted_data using except_dict.
        elif except_dict is not None:
            extracted_data = [data for data in extracted_data
                              if
                              not any(data.data_tag.get(key) == value for key,
                              value in except_dict.items())]
        # print(f"Repository: Found {list(target_data_tag.values())}.")
        return extracted_data

    def delete(self, target_data_tag: dict):
        target_key_set = set(target_data_tag.values())
        extracted_data = [item for item in self._data if
                          target_key_set.issubset(set(item.data_tag.values()))]
        for remove_data in extracted_data:
            self._data.remove(remove_data)
        print(f"Repository: {list(target_data_tag.values())} removed.")

    def get_list_of_tag_dict(self, target_data_tag=None, except_dict=None):
        whole_list = []
        if target_data_tag is None:
            extracted_data = self._data
        else:
            target_key_set = set(target_data_tag.values())
            extracted_data = [item for item in self._data if
                              target_key_set.issubset(
                                  set(item.data_tag.values()))]
            # remove data from extracted_data using except_dict.
            if except_dict:
                extracted_data = [data for data in extracted_data
                                  if not any(
                        data.data_tag.get(key) == value for key,
                        value in except_dict.items())]
        for data in extracted_data:
            whole_list.append(data.data_tag)
        return whole_list

        # e.g.  print_infor({'Attribute':'Data'}, {'Origin':'File','DataType':'ElecTrace'})

    def print_infor(self, target_data_tag=None, except_dict=None):
        for tag_dict in self.get_list_of_tag_dict():
            print(f"Repository: Infor = {list(tag_dict.values())}")
