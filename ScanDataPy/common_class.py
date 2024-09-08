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
import numpy as np
import psutil  # for memory check
#import itertools

#from conda.base.context import mockable_context_envs_dirs
#from sqlalchemy import modifier

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
                initialdir=os.getcwd(),  # current dir
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
        self.__fullname = os.path.join(
            fullname)  # replace separater for each OS
        self.__filename = os.path.basename(self.__fullname)
        self.__filepath = os.path.dirname(self.__fullname) + os.sep
        self.__abspath = os.path.abspath(fullname)  # absolute path
        split_filename = os.path.splitext(self.__filename)
        self.__file_name_no_ext = split_filename[0]
        self.__extension = split_filename[1]  # get only extension

        self.__filename_list = self.__make_filename_list()

    # List need A000-Z999 in the last of filenames
    def __make_filename_list(self) -> list:
        find = os.path.join(os.path.dirname(self.__abspath),
                            '*' + str(self.__extension))
        filename_list = [os.path.basename(f) for f in glob.glob(find)]
        return filename_list

    def __del__(self):
        # print('.')
        # print('Deleted a ImageData object.' + '  myId= {}'.format(id(self)))
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
        print('The file name list in the same folder = ' + str(
            self.__filename_list))


class KeyManager:
    def __init__(self):
        self._filename_dict = {}
        self._attribute_dict = {}  # {'Data':False, 'Text':False}
        self._data_type_dict = {}  # {'FluoFrames1':False, 'FluoTrace1':True, 'ElecTrace1':False, 'Header':False, 'Default':False}
        self._origin_dict = {}  # {'File':False, 'Roi1':True}

        self._time_window_dict = {}  # {'TimeWindow0':True}
        self._roi_dict = {}  # {'Roi0':False, 'Roi1':True, 'Roi2':False}
        self._scale_dict = {}  # {'DFoF':True, 'Normalize':False}
        self._bl_comp_dict = {}  # {'BlComp':True}

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

    def set_key_list_to_dict(self, key_list):
        # copy modifier names from the ModifierService to the KeyManager
        for key in key_list:
            if 'TimeWindow' in key:
                self._time_window_dict[key] = False
            elif 'Roi' in key:
                self._roi_dict[key] = False
            elif 'Scale' in key:
                self._scale_dict[key] = False
            elif 'BlComp' in key:
                self._bl_comp_dict[key] = False

    def set_dict_to_dict(self, key_dict):
        print(key_dict)
        for key, value in key_dict.items():
            if 'Filename' in key:
                self._filename_dict[value] = True
            elif 'Attribute' in key:
                self._attribute_dict[value] = False
            elif 'DataType' in key:
                self._data_type_dict[value] = False
            elif 'DataType' in key:
                self._data_type_dict[value] = False
            elif 'Origin' in key:
                self._origin_dict[value] = True

    def set_key(self, dict_name, key,
                val=None):  # e.g. (filename_dict, '30503A001.tsm',Ture)
        dictionary = getattr(self, f'_{dict_name}')  # get dict

        # inner function to update key
        def update_key(key):
            if key is not None:
                dictionary[key] = val
            else:
                dictionary[key] = not dictionary.get(key,
                                                     False)  # if there is no key, return False
        # if key == 'All', every key will be changed
        if key == 'All':
            for key in dictionary:
                update_key(key)
        else:
            update_key(key)

    def get_true_keys(self, dict_name: str):
        dictionary = getattr(self, f'_{dict_name}')
        return [key for key, value in dictionary.items() if value]

    # get key dict combinations from whole dict.  convert variable names to 'dictionary keys'.
    # val = True: True combination, False: False combination, None: whole combination
    def get_key_dicts(self, val=None) -> list:
        result = []
        dicts = [
            (self._filename_dict, 'Filename'),  # the second name because a key of dictionary
            (self._attribute_dict, 'Attribute'),
            (self._data_type_dict, 'DataType'),
            (self._origin_dict, 'Origin'),

            (self._time_window_dict, 'TimeWindow'),
            (self._roi_dict, 'Roi'),
            (self._scale_dict, 'Scale'),
            (self._bl_comp_dict, 'BlComp')
        ]
        # internal function
        def recursive_combinations(current_combination, remaining_dicts):
            if not remaining_dicts:  # if there is no remaining_dicts,
                result.append(current_combination)  # add a dict to the list
                return
            current_dict, field_name = remaining_dicts[0]
            if current_dict == {}:
                print("22222222222222222222222222222222222222")
                print(current_dict)
                # shallow copy for non effect of original data
                new_combination = current_combination.copy()
                # delete the current remaining object
                recursive_combinations(new_combination, remaining_dicts[1:])
                return
            for key, status in current_dict.items():
                if val is None or status == val:
                    # shallow copy for non effect of original data
                    new_combination = current_combination.copy()
                    new_combination[field_name] = key
                    # delete the current remaining object
                    recursive_combinations(new_combination, remaining_dicts[1:])
        recursive_combinations({}, dicts)

        return result

    def print_infor(self):
        print("===================== Key Manager =========================")
        print(f"filename_dict        = {self._filename_dict}")
        print(f"attribute_dict       = {self._attribute_dict}")
        print(f"data_type_dict       = {self._data_type_dict}")
        print(f"origin_dict          = {self._origin_dict}")
        print("")
        print(f"time_window_dict     = {self._time_window_dict}")
        print(f"roi_dict             = {self._roi_dict}")
        print(f"scale_dict           = {self._scale_dict}")
        print(f"bl_comp_dict         = {self._bl_comp_dict}")
        print("===========================================================")


class Tools:

    """ key modify"""

    # extract dict from original.  e.g. extract_list=['Filename', 'Ch', 'Origin'] original_dict={'Filename': '20408B002.tsm', 'ControllerName': 'ROI1', 'Ch': 'Ch1'}
    @staticmethod
    def extract_key(original_dict, extract_list):
        return {key: original_dict[key] for key in extract_list if
                key in original_dict}

        # delete tail numbers

    @staticmethod
    def remove_tail_numbers(input_string):
        result = re.sub(r'\d+$', '', input_string)
        return result

    @staticmethod
    def take_ch_from_str(input_string):
        pattern = r"Ch\d+"
        return re.search(pattern, input_string)

    """ calculation """

    @staticmethod
    def create_df_over_f(trace_obj) -> object:
        f = Tools.f_value(trace_obj)
        df_over_f = (trace_obj / f - 1) * 100
        # return value object
        return df_over_f

    @staticmethod
    def f_value(trace_obj) -> float:  # trace is value object.
        average_start = 1  # this is for a F value
        average_length = 4  # This is for a F value
        part_trace = trace_obj.data[
                     average_start: average_start + average_length]
        average = np.average(part_trace)
        return average

    @staticmethod
    def create_normalize(trace_obj) -> object:
        min_val = np.min(trace_obj.data)
        pre_trace_obj = trace_obj - min_val
        max_val = np.max(pre_trace_obj.data)
        norm_obj = pre_trace_obj / max_val
        # return value object
        return norm_obj

    @staticmethod
    def delta_f(trace_obj, bl_trace_obj) -> object:
        # return value object
        return trace_obj - bl_trace_obj

    @staticmethod
    def create_bl_comp(trace_obj, bl_trace_obj, degreePoly=2):
        # get f value
        f_trace = Tools.f_value(trace_obj)
        # get fitting curve from baseline trace
        coefficients = np.polyfit(bl_trace_obj.time, bl_trace_obj.data,
                                  degreePoly)
        y_fit = np.polyval(coefficients, bl_trace_obj.time)

        bl_trace_fit_obj = TraceData(y_fit, trace_obj.key_dict,
                                     trace_obj.interval)

        # calculate baseline compensated trace
        delta_f_trace = Tools.delta_f(trace_obj, bl_trace_fit_obj)
        # trace_obj.show_data()
        # bl_trace_fit_obj.show_data()
        # trace_obj.show_data()
        # delta_F_trace.show_data()
        bl_comp_trace = delta_f_trace + f_trace
        # bl_comp_trace = f_trace
        return bl_comp_trace

    """ misc """

    @staticmethod
    def get_memory_infor():
        pid = os.getpid()
        process = psutil.Process(pid)
        memory_infor = process.memory_info().rss
        maximum_memory = psutil.virtual_memory().total
        available_memory = psutil.virtual_memory().available
        return memory_infor, maximum_memory, available_memory
