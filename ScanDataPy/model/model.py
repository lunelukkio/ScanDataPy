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

    # set an axes observer of view into modifier. If observer is empty, update all controllers.
    @abstractmethod
    def set_observer(self, controller_key, observer:object):
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
        
    """ From AxesController """
   
       # From ax controllers. Make order of modifier in DataGenerator class
    @abstractmethod
    def set_modifier_order(self, modifier_tag_list: list):
        raise NotImplementedError()

    # make a new data from user_controller entities and save in the data_repository.
    @abstractmethod
    def create_data(self, data_tag):  #Needs 'Filename', 'Attribute', 'Ch', 'Origin', 'ControllerName'
        raise NotImplementedError()

    # return value object
    @abstractmethod
    def get_data(self, data_tag):
        raise NotImplementedError()
        
    @abstractmethod
    def help(self):
        raise NotImplementedError()

        
class DataService(ModelInterface):
    def __init__(self):
        # repository for Roi, TimeWindow, DFoF
        self.modifier_repository = ModifierRepository()



class DataCreator:
    def __init__(self):
        # the first modifier
        self.first_modifier = ModHandler()
        self.current_modifier = None

        
    # make a chain for modifier
    def set_modifier(self, modifier_obj_list):
        # Reset start of chain of responsibility
        self.current_modifier = self.first_modifier
        # make chain
        for modifier in modifier_obj_list:
            self.current_modifier = self.current_modifier.set_next(modifier)

    # this is called by DataService for creating data
    def apply_modifier(self, data):
        # run chain of responsibility
        self.first_modifier.apply_modifier(data)
