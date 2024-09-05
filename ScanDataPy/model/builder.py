# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 11:47:25 2023

@author: lunelukkio@gmail.com
"""

import json
from ScanDataPy.model.value_object import FramesData, ImageData, TraceData, TextData
from ScanDataPy.model.file_io import TsmFileIo, DaFileIo, HekaFileIO
  

# This class define the names of controllers and data
class TsmBuilder:

    @staticmethod
    def create_data(filename_obj):
        
        # import a JSON setting file
        try:
            with open("./setting/file_setting.json", "r") as json_file:
                setting = json.load(json_file)
        except:
            with open("../setting/file_setting.json", "r") as json_file:
                setting = json.load(json_file)
        num_ch = setting["tsm"]["num_ch"]
        num_elec_ch = setting["tsm"]["num_elec_ch"]
        default_controllers = setting["tsm"]["default_controllers"] 
        default_data_structure = setting["tsm"]["default_data_structure"]
        
        default_dict = {'num_ch':num_ch, 
                        'num_elec_ch':num_elec_ch, 
                        'default_controllers':default_controllers, 
                        'default_data_structure':default_data_structure
                        }
        
        default = TextData(default_dict, {'Filename':filename_obj.name, 
                                                'Attribute':'Default', 
                                                'DataType':'Text',  # need to think about category
                                                'Origin':'File'})
        file_io = TsmFileIo(filename_obj, num_ch)
        
        # header value object
        header = TextData(file_io.get_header(), {'Filename':filename_obj.name, 
                                                 'Attribute':'Header', 
                                                 'DataType':'Text', 
                                                 'Origin':'File'})
        
        # get and set data from files
        data_interval = file_io.get_infor()   # get interval infor from the io
        frames_list = file_io.get_3d()  # frames list
        # make a full frames
        full_frames = [FramesData(frames_list[0],  {'Filename':filename_obj.name, 'Attribute':'Data', 'DataType':'FluoFramesCh0', 'Origin':'File'}, data_interval[0])]
        # make a ch frames list
        ch_frames = [FramesData(frames_list[i], {'Filename':filename_obj.name, 'Attribute':'Data', 'DataType':'FluoFramesCh'+str(i), 'Origin':'File'}, data_interval[i]) for i in range(1, num_ch+1)]
        frames = full_frames + ch_frames
        # make an elec list
        trace_list = file_io.get_1d()
        elec_trace_list = [TraceData(trace_list[:, ch], {'Filename':filename_obj.name, 'Attribute':'Data', 'DataType':'ElecTraceCh'+str(ch+1), 'Origin':'File'}, data_interval[1+num_ch+ch]) for ch in range(num_elec_ch)]

        del file_io   # release the io object to allow file changes during recording.
        
        # make a list for every value objects. They will be saved by DataService class.
        data_list =  [default, header] + frames + elec_trace_list
        #print("----- TsmBulder: The .tsm file was imported and the file_io object was deleted.")
        #for data in data_list:
        #    print(data.key_list)
        #print("")
        return data_list

class DaBuilder:
    def __init__(self, filename_obj):
        num_ch = 2   # this is for Na+ and Ca2+ recording.
        num_elec_ch = 8

        self.default_controller = ["ROI", 
                                   "ROI", 
                                   "IMAGECONTROLLER", 
                                   "IMAGECONTROLLER", 
                                   "ELECTRACECONTROLLER", 
                                   "ELECTRACECONTROLLER"] 
        self.default_data = ["CH" + str(num) for num in range(num_ch+1)] +\
                            ["ELEC" + str(num) for num in range(num_elec_ch)]
        infor_keys = [f"CH{i}_INTERVAL" for i in range(num_ch+1) ] + \
                     [f"ELEC{i}_INTERVAL" for i in range (num_elec_ch)]
                     
        ch_list = [f"CH{i}" for i in range(num_ch+1)]  # This includes full trace
        elec_list = [f"ELEC{i}" for i in range(num_elec_ch)]
        self.__default_data_structure = {"ROI0": ch_list, 
                                         "ROI1": ch_list, 
                                         "IMAGECONTROLLER0": ch_list,
                                         "IMAGECONTROLLER1": ch_list,
                                         "ELECTRACECONTROLLER0": elec_list,
                                         "ELECTRACECONTROLLER1": elec_list}

        file_io = DaFileIo(filename_obj, num_ch)
        
        # get and set data from files
        data_interval = file_io.get_infor()   # get interval infor from the io
        self.data_interval_dict = dict(zip(infor_keys, data_interval))   # make an interval dict
        self.frames = file_io.get_3d()
        self.elec_data = file_io.get_1d()
        print(self.data_interval_dict)
        
        #file_io.print_data_interval()
        
        del file_io   # release the io object to allow file changes during recording.
        print("----- DaBulder: The .da file was imported and the file_io object was deleted.")
        print("")
        
    def get_infor(self):
        return self.data_interval_dict
        
    # make data_dict {ch_key: FrameData}  {"CH0": data, "CH1": data ......} 
    def get_frame(self) -> dict:  # change to numpy to value obj
        data = {"CH"+str(i): FramesData(self.frames[i],  
                            self.data_interval_dict["CH"+str(i)+"_INTERVAL"]) for i in range(num_ch+1)}
        print(f"Frames data = {data.keys()}")
        return data

    def get_image(self):
        print("----- There is no image data")
        return None
    
    # make data_dict {ch_key: TraceData}  {"ELEC1": data, ""ELEC2": data ......}
    def get_trace(self):
        data = {"ELEC"+str(ch): TraceData(self.elec_data[:, ch], 
                                      self.data_interval_dict[f"ELEC{ch}_INTERVAL"], "ElecTraceController")for ch in range(num_elec_ch)}
        print(f"Trace data = {data.keys()}")
        return data
    
    def get_default_data_structure(self):
        return self.__default_data_structure
    
class HekaBuilder:
    def __init__(self, filename_obj):
        file_io = HekaFileIO(filename_obj)
        
        # get and set data from files
        self.data_interval_dict = dict(zip("Meta_data", file_io.get_infor()))   # make an interval dict
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