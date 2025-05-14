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
from typing import List
from pathlib import Path
# import itertools

# from conda.base.context import mockable_context_envs_dirs
# from sqlalchemy import modifier


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

