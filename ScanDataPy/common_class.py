# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 13:42:38 2023

@author: lunelukkio@gmail.com
"""

import os
import sys
import glob
import re
import numpy as np
import psutil  # for memory check
from PyQt6.QtWidgets import QApplication, QFileDialog
from typing import List
from pathlib import Path
# import itertools

# from conda.base.context import mockable_context_envs_dirs
# from sqlalchemy import modifier


class FileService:
    def __init__(self):
        self.filename_obj_dict = {}

    def open_file(self, filename=None):
        if filename is None:
            fullname = self.get_fullname()
            if not fullname:
                print("No filename.")
                return None
        else:
            fullname = filename
        return WholeFilename(fullname)

    # Function to rename multiple files. This is for nnU-net model: https://www.youtube.com/watch?v=uhpnT8hGTnY&t=511s
    def rename_files(self):
        folder_path = "C:/Users/lunel/Documents/python/nnUNetFrame/testfolder"
        for count, filename in enumerate(sorted(os.listdir(folder_path))):
            dst = "ABD_" + str(count).zfill(3) + ".nii.gz"
            src = f"{folder_path}/{filename}"  # foldername/filename, if .py file
            dst = f"{folder_path}/{dst}"
            # rename() function will rename all the files
            os.rename(src, dst)

    @staticmethod
    def get_fullname():
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        fullname, _ = QFileDialog.getOpenFileName(
            None, "Open File", str(Path.cwd()),
            "Data files (*.tsm *.da *.abf *.wcp);;All files (*.*);;"
        )
        return fullname

    @staticmethod
    def get_files_with_same_extension(file_path: str, extension: str = None):
        path = Path(file_path)
        ext = extension or path.suffix
        files = list(path.parent.glob(f"*{ext}")) if ext else list(path.parent.glob("*"))
        return [str(f) for f in files]

    def get_filename_obj(self):
        return self.filename_obj_list

    def get_current_file_path(self):
        return self.filename_obj_list[0].path

    def reset(self):
        self.filename_obj_list = []


"""
Value object
"""


class WholeFilename:  # Use it only in a view and controller
    def __init__(self, fullname: str):
        self.path = Path(fullname).resolve()

    @property
    def fullname(self) -> str:
        return str(self.path)

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def dir(self) -> str:
        return str(self.path.parent)

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def extension(self) -> str:
        return self.path.suffix

    # List need A000-Z999 in the last of filenames
    def __make_filename_list(self) -> list:
        find = os.path.join(
            os.path.dirname(self.path.absolute()), "*" + str(self.extension)
        )
        filename_list = [os.path.basename(f) for f in glob.glob(find)]
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(
            "This function was replaced by get_files_with_same_extension() in FileService class."
        )
        print(filename_list)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return filename_list

    def __del__(self):
        # print('.')
        # print('Deleted a ImageData object.' + '  myId= {}'.format(id(self)))
        pass

    def print_infor(self) -> None:
        print("THe absolute path = " + str(self.path.absolute()))
        print("The full path = " + str(self.path))
        print("The file name = " + self.name)
        print("The file path = " + self.dir)
        print("The file name without extension = " + self.stem)
        print("The file extension = " + self.extension)
        print("The file name list in the same folder = " + str(self.__make_filename_list()))


class KeyManager:
    def __init__(self):
        self.filename_list = []
        self.attribute_list = []  # ['Data', 'Text']
        self.data_type_list = []  # ['FluoFramesCh1', 'FluoTraceCh1', 'ElecTraceCh1', 'Header', 'Default']
        self.origin_list = []  # ['File', 'Roi1']

        self.modifier_list = []  # ['TimeWindow3','Roi1','Average1','TagMaker0']

        self.ch_list = []
        self.roi_list = []
        self.bl_roi_list = []

    # set if tag is in the list the tag will be removed, if not tag will be added.
    def set_tag(self, tag_list_name, tag):  # e.g. (filename_dict, '30503A001.tsm')
        list_name = getattr(self, f"{tag_list_name}")  # get list
        if tag in list_name:
            list_name.remove(tag)
            print(f"KeyManager: removed {tag} from {list_name} ")
        else:
            list_name.append(tag)
            print(f"KeyManager: added {tag} to {list_name} ")
        # need this line because list_name is just like a copy.
        setattr(self, f"{tag_list_name}", list_name)

    # remove old tag and add new tag
    def replace_tag(
        self, list_name, old_tag, new_tag
    ):  # e.g. old_tag='Roi' new_tag='Roi1'
        # get list
        if hasattr(self, list_name):
            current_list = getattr(self, list_name)
            # delete old_tag from the list
            current_list = [item for item in current_list if old_tag not in item]
            current_list.append(new_tag)
            setattr(self, list_name, current_list)
            print(f"KeyManager: new_list of {list_name} = {current_list}")
        else:
            print(f"There is no {list_name} in the class")

    def get_list(self, list_name):
        if hasattr(self, list_name):
            return getattr(self, list_name)

    # get key dict combinations from whole dict.  convert variable names to 'dictionary keys'.
    # val = True: True combination, False: False combination, None: whole combination
    def get_dicts_from_tag_list(self) -> list:
        result = []
        # add ch to data_type_list
        datatype_list_with_ch = []
        for item in self.data_type_list:
            for ch in self.ch_list:
                datatype_list_with_ch.append(item + ch)

        all_dicts = [
            [
                self.filename_list,
                "Filename",
            ],  # the second name because a key of dictionary
            [self.attribute_list, "Attribute"],
            [datatype_list_with_ch, "DataType"],
            [self.origin_list, "Origin"],
        ]

        # internal function
        def recursive_combinations(current_combination, remaining_lists):
            if not remaining_lists:  # if there is no remaining_dicts,
                # after the last dict, the result has dict combinations
                result.append(current_combination)  # add a dict to the list
                return
            # take the first from the remaining dicts
            current_list, field_name = remaining_lists[0]
            # check key is the same as status
            for tag in current_list:
                # shallow copy for non effect of original data
                new_combination = current_combination.copy()
                new_combination[field_name] = tag
                # delete the current remaining object
                recursive_combinations(new_combination, remaining_lists[1:])

        # start from this line
        recursive_combinations({}, all_dicts)

        return result

    def print_infor(self):
        print("===================== Key Manager =========================")
        print(f"filename_list        = {self.filename_list}")
        print(f"attribute_list       = {self.attribute_list}")
        print(f"data_type_list       = {self.data_type_list}")
        print(f"origin_list          = {self.origin_list}")
        print("")
        print(f"modifier_list        = {self.modifier_list}")
        print(f"ch_list              = {self.ch_list}")
        print(f"roi_list    = {self.roi_list}")
        print(f"bl_roi_list    = {self.bl_roi_list}")

        print("===========================================================")

    def reset(self):
        for attr_name, attr_value in self.__dict__.items():
            if isinstance(attr_value, list):
                setattr(self, attr_name, [])
                print(f"{attr_name} has been reset to an empty list")


class Tools:
    """key modify"""

    # extract dict from original.  e.g. extract_list=['Filename', 'Ch', 'Origin'] original_dict={'Filename': '20408B002.tsm', 'ControllerName': 'ROI1', 'Ch': 'Ch1'}
    @staticmethod
    def extract_key(original_dict, extract_list):
        return {key: original_dict[key] for key in extract_list if key in original_dict}

        # delete tail numbers

    @staticmethod
    def remove_tail_numbers(input_string):
        result = re.sub(r"\d+$", "", input_string)
        return result

    @staticmethod
    def take_ch_from_str(input_string):
        pattern = r"Ch\d+"
        match = re.search(pattern, input_string)
        if match:
            matched_part = match.group()  # matched part
            start = match.start()  # matched first cha
            end = match.end()  # matched end cha
            before_match = input_string[:start]  # before matched
            after_match = input_string[end:]  # after matched  # noqa: F841
            return matched_part, before_match
        # if no match return None
        return None

    """ calculation """

    @staticmethod
    def f_value(data) -> float:  # trace is value object.
        start = 0  # this is for a F value
        length = 4  # This is for a F value
        part_trace = data[start : start + length]
        average = np.average(part_trace)
        return average

    # take the smallest average value in the end of the trace
    @staticmethod
    def trace_min(data):  # trace is value object.
        start = -5
        part_trace = data[start:]
        average = np.average(part_trace)
        return average

    @staticmethod
    def exponential_func(x, a, b, c):
        return a * np.exp(b * x) + c

    """ misc """

    @staticmethod
    def get_memory_infor():
        pid = os.getpid()
        process = psutil.Process(pid)
        memory_infor = process.memory_info().rss
        maximum_memory = psutil.virtual_memory().total
        available_memory = psutil.virtual_memory().available
        return memory_infor, maximum_memory, available_memory


class FileHistoryManager:
    def __init__(self, max_history=10):
        self.history = []
        self.current_file = None
        self.max_history = max_history

    def add_file(self, file_obj: WholeFilename):
        self.current_file = file_obj
        # Remove if already in history
        self.history = [f for f in self.history if f.fullname != file_obj.fullname]
        self.history.insert(0, file_obj)
        # Keep only the latest N
        self.history = self.history[:self.max_history]

    def get_recent_files(self):
        return self.history

    def get_current_file(self):
        return self.current_file

    def clear_history(self):
        self.history = []
        self.current_file = None
