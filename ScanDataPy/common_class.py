# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 13:42:38 2023

@author: lunelukkio@gmail.com
"""

from abc import ABCMeta, abstractmethod
import os
import sys
import glob
import copy
import re
import itertools

try:
    from PyQt5.QtWidgets import QFileDialog, QApplication
except:
    import tkinter as tk

class FileService:
    def __init__(self):
        self.filename_obj_list = []
        
    def open_file(self, *filename):  # it can catch variable num of filenames.
        if filename == ():
            fullname = self.get_fullname()  # This is str filename
            if fullname == None:
                print("No filename.")
                return
            new_full_filename = fullname
        else:
            new_full_filename = filename
        new_filename_obj = WholeFilename(new_full_filename)
        self.filename_obj_list.append(new_filename_obj)
        return new_filename_obj
    
    # Function to rename multiple files: https://www.youtube.com/watch?v=uhpnT8hGTnY&t=511s
    def rename_files(self):
        folder_path = "C:/Users/lunel/Documents/python/nnUNetFrame/testfolder"
        for count, filename in enumerate(sorted(os.listdir(folder_path))):
            dst = "ABD_" + str(count).zfill(3) + ".nii.gz"
            src = f"{folder_path}/{filename}"  # foldername/filename, if .py file
            dst = f"{folder_path}/{dst}"
            # rename() function will rename all the files
            os.rename(src, dst)
    
    @staticmethod
    def get_fullname(event=None):
        
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)

            fullname, _ = QFileDialog.getOpenFileName(
            None,
            "Open File",
            os.getcwd(),
            "All files (*.*);;"
            "Tsm files (*.tsm);;"
            "Da files (*.da);;"
            "Axon files (*.abf);;"
            "WinCP files (*.wcp)"
            )
        except:
            # open file dialog
            fullname = tk.filedialog.askopenfilename(
                initialdir = os.getcwd(), # current dir
                filetypes=(('All files', '*.*'), 
                           ('Tsm files', '*.tsm'),
                           ('Da files', '*.da'), 
                           ('Axon files', '*.abf'),
                           ('WinCP files', '*.wcp')
                          ))
        return fullname
    
    def get_filename_obj(self):
        return self.filename_obj_list


"""
Value object
"""

class WholeFilename:  # Use it only in a view and controller
    def __init__(self, fullname: str):
        self.__fullname = os.path.join(fullname)  # replace separater for each OS
        self.__filename = os.path.basename(self.__fullname)
        self.__filepath = os.path.dirname(self.__fullname) + os.sep
        self.__abspath = os.path.abspath(fullname)# absolute path
        split_filename = os.path.splitext(self.__filename)
        self.__file_name_no_ext = split_filename[0]
        self.__extension =  split_filename[1]  # get only extension
        
        self.__filename_list = self.__make_filename_list()
        
    # List need A000-Z999 in the last of filenames
    def __make_filename_list(self) -> list:
        
        find = os.path.join(os.path.dirname(self.__abspath), '*' + str(self.__extension))
        filename_list = [os.path.basename(f) for f in glob.glob(find)]
        return  filename_list
    
    def __del__(self):
        #print('.')
        #print('Deleted a ImageData object.' + '  myId= {}'.format(id(self)))
        pass
        
    @property
    def fullname(self) -> str:
        return self.__fullname
    
    @property
    def name(self) -> str:
        return self.__filename
    
    @property
    def path(self) -> str:
        return self.__filepath
    
    @property
    def abspath(self) -> str:
        return self.__abspath
    
    @property
    def file_name_no_ext(self) -> str:
        return self.__file_name_no_ext
    
    @property
    def extension(self) -> str:
        return self.__extension
    
    @property
    def filename_list(self) -> list:
        return self.__filename_list
    
    def print_infor(self) -> None:
        print('THe absolute path = ' + self.__abspath)
        print('The full path = ' + self.__fullname)
        print('The file name = ' + self.__filename)
        print('The file path = ' + self.__filepath)
        print('The file name without extension = ' + self.__file_name_no_ext)
        print('The file extension = ' + self.__extension)
        print('The file name list in the same folder = ' + str(self.__filename_list))
        
class KeyManager:
    def __init__(self):
        self._filename_dict = {}          # e.g. {'70505A001':Ture}
        self._attribute_dict = {}         # e.g. {'Usercontroller':True, 'Data':False, 'text':False}
        self._data_type_dict = {}         # e.g. {'FluoFrames':False, 'FluoTrace':True, 'ElecTrace':False, 'Header':False, 'Default':False}
        self._origin_dict = {}            # e.g. {'File':False, 'ROI1':Ture, 'ImageController1':False, 'ElecTraceController1':False}
        self._controller_name_dict = {}   # e.g. {'ROI0':False','ROI1':Ture, 'ImageController1':False, 'ElecTraceController1':False}
        self._ch_dict = {}                # e.g. {'Ch0':False, 'Ch1':True, 'Ch2':False}
    
    @property
    def filename_dict(self) -> dict:
        return self._filename_dict
    
    @property
    def attribute_dict(self) -> dict:
        return self._attribute_dict
    
    @property
    def data_type_dict(self) -> dict:
        return self._data_type_dict
    
    @property
    def origin_dict(self) -> dict:
        return self._origin_dict
    
    @property
    def controller_name_dict(self) -> dict:
        return self._controller_name_dict
    
    @property
    def ch_dict(self) -> dict:
        return self._ch_dict
    
    @filename_dict.setter
    def filename_dict(self, filename_dict) -> None:
        self._filename_dict = filename_dict
    
    @attribute_dict.setter
    def attribute_dict(self, attribute_dict) -> None:
        self._attribute_dict = attribute_dict

    @data_type_dict.setter
    def data_type_dict(self, data_type_dict) -> None:
        self._data_type_dict = data_type_dict

    @origin_dict.setter
    def origin_dict(self, origin_dict) -> None:
        self._origin_dict = origin_dict

    @controller_name_dict.setter
    def controller_name_dict(self, controller_name_dict) -> None:
        self._controller_name_dict = controller_name_dict

    @ch_dict.setter
    def ch_dict(self, ch_dict) -> None:
        self._ch_dict = ch_dict
        
    def set_key(self, dict_name, key, val=None):  # e.g. (filename_dict, '30503A001.tsm',Ture)
        dictionary = getattr(self, f'_{dict_name}') # get dict 
        
        # inner function to update key
        def update_key(key):
            if key is not None:
                dictionary[key] = val
            else:
                dictionary[key] = not dictionary.get(key, False)  # if there is no key, return False
        
        # if key == 'ALL', every key will be changed
        if key == 'ALL':
            for key in dictionary:
                update_key(key)
        else:
            update_key(key)

    def get_true_keys(self, dict_name: str):
        dictionary = getattr(self, f'_{dict_name}')
        return [key for key, value in dictionary.items() if value]

    def get_key_dicts(self, val=None) -> list:
        result = []
        
        dicts = [
            (self._filename_dict, 'Filename'),
            (self._attribute_dict, 'Attribute'),
            (self._data_type_dict, 'DataType'),
            (self._origin_dict, 'Origin'),
            (self._controller_name_dict, 'ControllerName'),
            (self._ch_dict, 'Ch')
        ]
    
        def recursive_combinations(current_combination, remaining_dicts):
            if not remaining_dicts:  # if there is no remaining_dicts, 
                result.append(current_combination)  # add a dict to the list
                return
            current_dict, field_name = remaining_dicts[0]
            if current_dict == {}:
                new_combination = current_combination.copy()  # shallow copy for non effect of original data
                recursive_combinations(new_combination, remaining_dicts[1:]) # delete the current remainging object
                return
            for key, status in current_dict.items():
                if val is None or status == val:
                    new_combination = current_combination.copy()  # shallow copy for non effect of original data
                    new_combination[field_name] = key
                    recursive_combinations(new_combination, remaining_dicts[1:]) # delete the current remainging object
    
        recursive_combinations({}, dicts)
    
        return result

    def show_keys(self):
        print("===================== Key Manager =========================")
        print(f"filename_dict        = {self._filename_dict}")
        print(f"attribute_dict       = {self._attribute_dict}")
        print(f"data_type_dict       = {self._data_type_dict}")
        print(f"origin_dict          = {self._origin_dict}")
        print(f"controller_name_dict = {self._controller_name_dict}")
        print(f"ch_dict              = {self._ch_dict}")
        print("===========================================================")



   