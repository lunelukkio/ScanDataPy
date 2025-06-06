# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 11:47:25 2023

@author: lunelukkio@gmail.com
"""

import json
from ScanDataPy.model.value_object import FramesData
from ScanDataPy.model.value_object import ImageData
from ScanDataPy.model.value_object import TraceData
from ScanDataPy.model.value_object import TextData
from ScanDataPy.model.file_io import TsmFileIo
from ScanDataPy.model.file_io import DaFileIo
from ScanDataPy.model.file_io import HekaFileIO


# This class define the names of controllers and data
class TsmBuilder:

    @staticmethod
    def create_data(filename_obj):

        def tag_creator(filename, attribute, data_type, origin='File'):
            return {
                'Filename': filename,
                'Attribute': attribute,
                'DataType': data_type,
                'Origin': origin
            }

        # import a JSON setting file
        setting = None
        search_paths = [
            "./setting/file_setting.json",
            "../setting/file_setting.json",
            "./ScanDataPy/setting/file_setting.json"
        ]
        
        for path in search_paths:
            try:
                with open(path, "r") as json_file:
                    setting = json.load(json_file)
                print(f"Successfully loaded settings from: {path}")
                break
            except FileNotFoundError:
                continue
            except json.JSONDecodeError:
                print(f"Error: {path} is not a valid JSON file")
                continue
            except Exception as e:
                print(f"Unexpected error while reading {path}: {str(e)}")
                continue
        
        if setting is None:
            print("Error: Could not find or load file_setting.json in any of these locations:")
            for path in search_paths:
                print(f"- {path}")
            raise FileNotFoundError("No valid settings file found")

        num_ch = setting["tsm"]["num_ch"]
        num_elec_ch = setting["tsm"]["num_elec_ch"]

        default_dict = setting['tsm'].copy()

        default = TextData(default_dict, tag_creator(
            filename_obj.name,
            'Default',
            'Text'
            )
        )
        file_io = TsmFileIo(filename_obj, num_ch)

        # header value object
        header = TextData(
            file_io.get_header(), tag_creator(
                filename_obj.name,
                'Header',
                'Text'
            )
        )

        # get and set data from files
        data_interval = file_io.get_infor()  # get interval infor from the io
        frames_list = file_io.get_3d()  # frames list
        # make a full frames
        full_frames = [
            FramesData(frames_list[0], tag_creator(
                filename_obj.name,
                'Data',
                'FluoFramesCh0'
            ), data_interval[0])
        ]
        # make a ch frames list
        ch_frames = [
            FramesData(
                frames_list[i], tag_creator(
                    filename_obj.name,
                    'Data',
                    'FluoFramesCh' + str(i)
                ), data_interval[i]
            ) for i in range(1, num_ch + 1)
        ]
        frames = full_frames + ch_frames
        # make an elec list
        trace_list = file_io.get_1d()
        elec_trace_list = [
            TraceData(
                trace_list[:, ch], tag_creator(
                    filename_obj.name,
                    'Data',
                    'ElecTraceCh' + str(ch + 1)
                ), data_interval[1 + num_ch + ch]
            ) for ch in range(num_elec_ch)
        ]

        del file_io  # release the io object to allow file changes during recording.

        # make a list for every value objects. They will be saved by DataService class.
        data_list = [default, header] + frames + elec_trace_list
        # print("----- TsmBulder: The .tsm file was imported and the file_io object was deleted.")
        # for data in data_list:
        #    print(data.key_list)
        # print("")
        return data_list


class DaBuilder:
    @staticmethod
    def create_data(filename_obj):
        def tag_creator(filename, attribute, data_type, origin="File"):
            return {
                "Filename": filename,
                "Attribute": attribute,
                "DataType": data_type,
                "Origin": origin,
            }

        # import a JSON setting file
        try:
            with open("./setting/file_setting.json", "r") as json_file:
                setting = json.load(json_file)
        except:
            try:
                with open("../setting/file_setting.json", "r") as json_file:
                    setting = json.load(json_file)
            except:
                with open("ScanDataPy/setting/file_setting.json", "r") as json_file:
                    setting = json.load(json_file)
        num_ch = setting["da"]["num_ch"]
        num_elec_ch = setting["da"]["num_elec_ch"]

        default_dict = setting["da"].copy()

        default = TextData(
            default_dict, tag_creator(filename_obj.name, "Default", "Text")
        )
        file_io = DaFileIo(filename_obj, num_ch)

        # header value object
        header = TextData(
            file_io.get_header(), tag_creator(filename_obj.name, "Header", "Text")
        )

        # get and set data from files
        data_interval = file_io.get_infor()  # get interval infor from the io
        frames_list = file_io.get_3d()  # frames list
        # make a full frames
        full_frames = [
            FramesData(
                frames_list[0],
                tag_creator(filename_obj.name, "Data", "FluoFramesCh0"),
                data_interval[0],
            )
        ]
        # make a ch frames list
        ch_frames = [
            FramesData(
                frames_list[i],
                tag_creator(filename_obj.name, "Data", "FluoFramesCh" + str(i)),
                data_interval[i],
            )
            for i in range(1, num_ch + 1)
        ]
        frames = full_frames + ch_frames
        # make an elec list
        trace_list = file_io.get_1d()
        elec_trace_list = [
            TraceData(
                trace_list[:, ch],
                tag_creator(filename_obj.name, "Data", "ElecTraceCh" + str(ch + 1)),
                data_interval[1 + num_ch + ch],
            )
            for ch in range(num_elec_ch)
        ]

        del file_io  # release the io object to allow file changes during recording.

        # make a list for every value objects. They will be saved by DataService class.
        data_list = [default, header] + frames + elec_trace_list
        # print("----- TsmBulder: The .tsm file was imported and the file_io object was deleted.")
        # for data in data_list:
        #    print(data.key_list)
        # print("")
        return data_list


class HekaBuilder:
    def __init__(self, filename_obj):
        file_io = HekaFileIO(filename_obj)

        # get and set data from files
        self.data_interval_dict = dict(
            zip("Meta_data", file_io.get_infor()))  # make an interval dict
        self.frames = None
        self.image = None
        self.elec_data = file_io.get_1d()
        print(self.data_interval_dict)

        def get_infor(self, filename_obj):
            return self.data_interval_dict

        def get_frame(self, filename_obj):
            print("No frame data")

        def get_image(self, filename_obj):
            print("No image data")

        def get_trace(self, filename_obj):
            return self.elec_data

        def get_default_data_structure(self, filename_obj):
            raise NotImplementedError()
