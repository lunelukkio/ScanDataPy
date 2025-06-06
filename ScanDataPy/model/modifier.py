# -*- coding: utf-8 -*-
"""
Created on Thu ug 29 15:16:57 2024
This is to modify value object data. It uses Chain of responsibility.
Data through every chain part and find their name in modifier_list.
It don't have for modifier in modifier_list, because the order of modifier_list
is not stable.

@author: lunelukkio
"""

from abc import ABCMeta, abstractmethod

import numpy as np
import itertools
from scipy.optimize import curve_fit
import pyqtgraph as pg

from ScanDataPy.model.value_object import FramesData
from ScanDataPy.model.value_object import ImageData
from ScanDataPy.model.value_object import TraceData
from ScanDataPy.model.value_object import RoiVal
from ScanDataPy.model.value_object import TimeWindowVal
from ScanDataPy.common_class import Tools


class ModifierServiceInterface(metaclass=ABCMeta):
    """
    order is defined by self.__order_chain()
    """

    @abstractmethod
    def add_chain(self, modifier_name):
        raise NotImplementedError()

    @abstractmethod
    def remove_chain(self, modifier_name):
        raise NotImplementedError()

    @abstractmethod
    def set_modifier_val(self, modifier_name, *args, **kwargs):
        raise NotImplementedError()


class ModifierService(ModifierServiceInterface):
    def __init__(self):
        self.__current_modifier = None
        # chain always should have start and end
        self.__start_modifier = StartModifier("StartModifier")
        # make a default modifier chain list. It has modifier list.
        self.__modifier_chain_list = [self.__start_modifier, EndModifier("EndModifier")]
        # make a modifier chain from the chain list. It has modifier order.
        self.__modifier_chain = ModifierService.make_modifier_chain(
            self.__modifier_chain_list
        )

    @property
    def modifier_chain_list(self):
        return self.__modifier_chain_list

    # This is actual method run by DataService and return a modified value object data
    def apply_modifier(self, data_obj, original_modifier_list=None):
        # copy modifier list for error checking in EndModifier class
        modifier_list = original_modifier_list.copy()
        # start the chain of responsibility and get modified data
        modified_data = self.__start_modifier.apply_modifier(data_obj, modifier_list)
        return modified_data

    def add_chain(self, modifier_name):
        # get a modifier factory
        modifier_factory = ModifierService.check_modifier_type(modifier_name)
        # get a new modifier name
        if modifier_name[-1].isdigit():
            new_modifier_name = modifier_name
        else:
            new_modifier_name = self.__num_maker(modifier_name)
        # create a modifier with their name
        new_modifier = modifier_factory.create_modifier(new_modifier_name)
        # add to the chain object list
        self.__modifier_chain_list.append(new_modifier)
        # sort and add start chain
        self.__modifier_chain_list = ModifierService.sort_chain_list(
            self.__modifier_chain_list
        )
        # make a modifier chain from the chain list
        self.__modifier_chain = ModifierService.make_modifier_chain(
            self.__modifier_chain_list
        )

    def remove_chain(self, modifier_name):
        # remove modifier_name object from the list
        self.__modifier_chain_list = [
            obj
            for obj in self.__modifier_chain_list
            if obj.modifier_name != modifier_name
        ]
        # sort and add start chain
        self.__modifier_chain_list = ModifierService.sort_chain_list(
            self.__modifier_chain_list
        )
        # make a modifier chain from the chain list
        self.__modifier_chain = ModifierService.make_modifier_chain(
            self.__modifier_chain_list
        )

    # return modifier value_object taken for ROIBOX
    def get_modifier_val(self, modifier_name):
        for modifier_obj in self.modifier_chain_list:
            if modifier_obj.modifier_name == modifier_name:
                return modifier_obj.val_obj

    def set_modifier_val(self, modifier_name, *args, **kwargs):
        for modifier_obj in self.__modifier_chain_list:
            if modifier_name == modifier_obj.modifier_name:
                modifier_obj.set_modifier_val(*args, **kwargs)
                break
        else:
            raise ValueError(
                f"Modifier '{modifier_name}' not found in the modifier chain list."
            )

    @staticmethod
    def check_modifier_type(modifier_name):
        if "TimeWindow" in modifier_name:
            return TimeWindowFactory()
        elif "Roi" in modifier_name:
            return RoiFactory()
        elif "Average" in modifier_name:
            return AverageFactory()
        elif "Scale" in modifier_name:
            return ScaleFactory()
        elif "BlComp" in modifier_name:
            return BlCompFactory()
        elif "DifImage" in modifier_name:
            return DifImageFactory()
        elif "Invert" in modifier_name:
            return InvertFactory()
        elif "TagMaker" in modifier_name:
            return TagMakerFactory()
        else:
            raise ValueError(f"{modifier_name} Factory done not exist.")

    # To make a number for modifier.
    def __num_maker(self, modifier_name):
        modifier_name_list = [
            modifier.modifier_name for modifier in self.__modifier_chain_list
        ]
        # Count existing modifier name
        for i in itertools.count():  # This is for  i +=1
            current_name = f"{modifier_name}{i}"
            if current_name not in modifier_name_list:
                return current_name

    # modifier list always should be done by this list order.
    @staticmethod
    def sort_chain_list(old_obj_list):
        new_order_word_list = [
            "StartModifier",
            "TimeWindow",
            "Roi",
            "Average",
            "BlComp",
            "Scale",
            "DifImage",
            "Invert",
            "TagMaker",
            "EndModifier",
        ]
        # order to new list
        sorted_obj_list = []
        for word in new_order_word_list:
            for modifier_obj in old_obj_list:
                # check word in modifier_name
                if modifier_obj.modifier_name.startswith(word):
                    sorted_obj_list.append(modifier_obj)
        return sorted_obj_list

    @staticmethod
    def make_modifier_chain(modifier_chain_list):
        def set_chain(index):
            if index < len(modifier_chain_list) - 1:
                # make chain with modifier in inner function
                modifier_chain_list[index].set_next(modifier_chain_list[index + 1])
                # next object
                set_chain(index + 1)

        # if there is objects in the list
        if modifier_chain_list:
            # start from the first object
            set_chain(0)
            # return the chain
        return modifier_chain_list[0] if modifier_chain_list else None

    def print_chain(self):
        print("")
        print(
            "++++++++++ Modifiers ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        )
        print("ModifierService: modifier_chain -> ", end="")

        current_modifier = self.__start_modifier
        while current_modifier:
            print(f"{current_modifier.modifier_name}.", end="")
            current_modifier = current_modifier.next_modifier
        print("")
        print(
            "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        )
        print("")


""" abstract factory """


class ModifierFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_modifier(self, modifier_name: dict):  # data_tag = controller_key dict
        raise NotImplementedError()


"""concrete factory"""


class TimeWindowFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return TimeWindow(modifier_name)


class RoiFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return Roi(modifier_name)


class AverageFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return Average(modifier_name)


class ScaleFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return Scale(modifier_name)


class BlCompFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return BlComp(modifier_name)


class DifImageFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return DifImage(modifier_name)


class InvertFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return Invert(modifier_name)


class TagMakerFactory(ModifierFactory):
    def create_modifier(self, modifier_name):
        return TagMaker(modifier_name)


""" super class """


class ModifierHandler(metaclass=ABCMeta):  # BaseHandler
    def __init__(self, modifier_name):
        self.__modifier_name = modifier_name
        self.__next_modifier = None
        self._val_obj = None
        self.observer = Observer()

    def __del__(self):  # make a message when this object is deleted.
        print(".")
        # print(f"----- Deleted a object.' + ' {format(id(self)}")
        # pass

    def set_next(self, next_modifier):
        self.__next_modifier = next_modifier
        return next_modifier

    def modifier_request(self, data_obj, modifier_list):
        if self.__next_modifier:
            return self.__next_modifier.apply_modifier(data_obj, modifier_list)

    def apply_modifier(self, data_obj, modifier_list):
        # if current modifier name is in modifier_list, go to self.set_data
        if self.modifier_name in modifier_list:
            new_data = self.set_data(data_obj)
            modifier_list.remove(self.modifier_name)
        else:
            new_data = data_obj
        return self.modifier_request(new_data, modifier_list)

    @property
    def modifier_name(self):
        return self.__modifier_name

    @property
    def next_modifier(self):
        return self.__next_modifier

    @property
    def val_obj(self):
        return self._val_obj

    @abstractmethod
    def set_modifier_val(self, *args, **kwargs):
        raise NotImplementedError()

    def get_val(self):  # e.g. roi value
        return self._val_obj

    @abstractmethod
    def set_data(self, data_obj):
        raise NotImplementedError()

    def set_observer(self, observer):
        self.observer.set_observer(observer)

    def notify_observer(self):
        self.observer.notify_observer()


"""concrete modifier"""


class StartModifier(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)

    def apply_modifier(self, data_obj, modifier_list):
        return super().modifier_request(data_obj, modifier_list)

    def set_modifier_val(self):
        raise NotImplementedError()

    def set_data(self, data_obj):
        raise NotImplementedError()


class TimeWindow(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
        self.average_mode = "Frames"  # 'Frames' or 'Trace'

    def __del__(self):  # make a message when this object is deleted.
        print(".")
        print(f"----- Deleted a TimeWindow object. + {format(id(self))}")
        # pass

    def set_modifier_val(self, val: list):  # val = [start, width]
        start, width = val
        self._val_obj = TimeWindowVal(start, width)  # replace the roi
        self.observer.notify_observer()
        print(f"set TimeWindow: {self._val_obj.data} and notified")

    # calculate a image from a single frames data with a time window value object
    def set_data(self, origin_data):
        if origin_data is None:
            raise Exception("TimeWindow: origin_data is empty.")
        elif any("FluoFrames" in str for str in list(origin_data.data_tag.values())):
            # check value is correct
            TimeWindow.check_frames_val(origin_data, self._val_obj)
            # make raw trace data
            start, width = self._val_obj.data
            if width == -1 or width == 0:
                # if width = 0 or 1, trace include the end of the trace
                data = origin_data.data[:, :, start:]
            else:
                # slice end is end+1
                data = origin_data.data[:, :, start : start + width]
            print(
                f"TimeWindow:   A frames from frame# {start} to {start + width - 1} (- means whole)"
            )
            # take Ch from DataType
            ch, data_type = Tools.take_ch_from_str(origin_data.data_tag["DataType"])
            return FramesData(
                data,
                {
                    "Filename": origin_data.data_tag["Filename"],
                    "Attribute": "Data",
                    "DataType": origin_data.data_tag["DataType"],
                    "Origin": self.modifier_name,
                },
                origin_data.interval,
                origin_data.pixel_size,
            )
        elif any("ElecTrace" in str for str in list(origin_data.data_tag.values())):
            TimeWindow.check_trace_val(origin_data, self._val_obj)
            start, width = self._val_obj.data
            if width == -1 or width == 0:
                # if width = 0 or 1, trace include the end of the trace
                data = origin_data.data[start:]
            else:
                # slice end is end+1
                data = origin_data.data[start : start + width]
            print(
                f"TimeWindow:   A Trace from data point# {start} to {start + width - 1} (- means whole)"
            )
            # take Ch from DataType
            ch, data_type = Tools.take_ch_from_str(origin_data.data_tag["DataType"])
            return TraceData(
                data,
                {
                    "Filename": origin_data.data_tag["Filename"],
                    "Attribute": "Data",
                    "DataType": origin_data.data_tag["DataType"],
                    "Origin": self.modifier_name,
                },
                origin_data.interval,
            )

        else:
            raise Exception(
                "TimeWindow: This value object is not FluoFrames or ElecTrace."
            )

    @staticmethod
    def check_frames_val(frames_obj, time_window_obj) -> bool:
        # convert to raw values
        time_window = time_window_obj.data
        # check the value is correct. See TimeWindowVal class.
        frame_length = frames_obj.data.shape[2]
        # check the start and end values
        if time_window[0] < 0:
            raise Exception("The start frame should be 0 or more.")
        if time_window[1] < -1:
            raise Exception("The width should be -1 or more.")
        # compare the val to frame length
        if time_window[0] + time_window[1] > frame_length:
            raise Exception(f"The total frame should be less than {frame_length}.")
        else:
            return True

    @staticmethod
    def check_trace_val(trace_obj, time_window_obj) -> bool:
        # convert to raw values
        time_window = time_window_obj.data
        # check the value is correct. See TimeWindowVal class.
        trace_length = trace_obj.data.shape
        # check the start and end values
        if time_window[0] < 0:
            raise Exception("The start frame should be 0 or more.")
        if time_window[1] < -1:
            raise Exception("The width should be -1 or more.")
        # compare the val to frame length
        if time_window[0] + time_window[1] > trace_length:
            raise Exception(f"The total frame should be less than {frame_length - 1}.")
        else:
            return True

    def reset(self) -> None:
        self.set_modifier_val([0, 1])


class Roi(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)

    def __del__(self):  # make a message when this object is deleted.
        print(".")
        print(f"----- Deleted a Roi object. + {format(id(self))}")
        # pass

    # make a new ROI value object
    def set_modifier_val(self, val: list):
        roi_val = [None, None, None, None]
        if None not in val:
            roi_val = val
        else:
            for i in range(2):  # for x and y
                if val[i] is None:
                    roi_val[i] = self._val_obj.data[i]
                else:
                    roi_val[i] = val[i]
            for i in range(2, 4):
                if val[i] is None:
                    roi_val[i] = self._val_obj.data[i]  # for width and height
                else:
                    roi_val[i] = self._val_obj.data[i] + val[i]
        self._val_obj = RoiVal(*roi_val[:4])  # replace the roi
        self.observer.notify_observer()
        print(f"set Roi: {self._val_obj.data} and notified")

    # calculate a trace from a single frames data with a roi value object
    def set_data(self, origin_data: object):
        if origin_data is None:
            raise Exception("ROI: origin_data is empty.")
        elif all(
            "FluoFrames" not in str for str in list(origin_data.data_tag.values())
        ):
            # print(f"ROI: {origin_data.data_tag['DataType']} is not FluoFrames value object. Skip This data.")
            return
        roi_obj = self._val_obj
        # check value is correct
        Roi.check_val(origin_data, roi_obj)
        # make raw trace data
        x, y, x_width, y_width = roi_obj.data[:4]
        data = origin_data.data[x : x + x_width, y : y + y_width, :]
        # make a trace value object
        print(f"Roi:        A frames from {roi_obj.data}")
        # take Ch from DataType
        ch, data_type = Tools.take_ch_from_str(origin_data.data_tag["DataType"])
        new_data = FramesData(
            data,
            {
                "Filename": origin_data.data_tag["Filename"],
                "Attribute": "Data",
                "DataType": origin_data.data_tag["DataType"],
                "Origin": self.modifier_name,
            },
            origin_data.interval,
        )
        return new_data

    @staticmethod
    def check_val(frames_obj, roi_obj) -> bool:
        # convert to raw values
        roi = roi_obj.data
        # check the value is correct. See ROIVal class.
        frames_size = frames_obj.shape
        if (
            roi[0] + roi[2] - 1 > frames_size[0] or roi[1] + roi[3] - 1 > frames_size[1]
        ):  # width is always 1 or more.
            print("The roi size should be the same as the image size or less")
        if roi[0] < 0 or roi[1] < 0:
            roi[0] += 1
            print("The roi x should be the same as 0 or more")
        if roi[1] < 0:
            roi[1] += 1
            print("The roi y should be the same as 0 or more")
        if roi[2] < 1 or roi[3] < 1:
            roi[2] += 1
            print("The roi width x should be the same as 1 or more")
        if roi[3] < 1:
            roi[3] += 1
            print("The roi width y should be the same as 1 or more")
        else:
            return True

    def reset(self) -> None:
        self.set_modifier_val([40, 40, 1, 1])


class Average(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
        self.average_mode = "None"  # 'Image' or 'Trace'

    def __del__(self):  # make a message when this object is deleted.
        print(".")
        print(f"----- Deleted a Average object. + {format(id(self))}")
        # pass

    # average direction. 1 is for images, 2 is for traces
    def set_modifier_val(self, val: str):  # val = [start, width]
        self.average_mode = val
        print(f"set Average: {self.average_mode}  1=Image, 2=Trace")

    def set_data(self, value_obj):
        # if any('Image' in str for str in data.data_tag.values()):
        #    self.average_mode = 'Image'
        # elif any('Roi' in str for str in data.data_tag.values()):
        #    self.average_mode = 'Roi'
        if self.average_mode == "Image":
            # mean to image
            mean_data = np.mean(value_obj.data, axis=2)
            print("Average:     Averaged a FluoFrames to an image")
            # take Ch from DataType
            ch, data_type = Tools.take_ch_from_str(value_obj.data_tag["DataType"])
            return ImageData(
                mean_data,
                {
                    "Filename": value_obj.data_tag["Filename"],
                    "Attribute": "Data",
                    "DataType": "FluoImage" + ch,
                    "Origin": value_obj.data_tag["Origin"],
                },
                value_obj.pixel_size,  # pixel size
            )
        if self.average_mode == "Roi":
            # mean to trace
            mean_data = np.mean(value_obj.data, axis=(0, 1))
            # make a trace value object
            print("Average:    Averaged a FluoFrames to a trace")
            # take Ch from DataType
            ch, data_type = Tools.take_ch_from_str(value_obj.data_tag["DataType"])
            return TraceData(
                mean_data,
                {
                    "Filename": value_obj.data_tag["Filename"],
                    "Attribute": "Data",
                    "DataType": "FluoTrace" + ch,
                    "Origin": value_obj.data_tag["Origin"],
                },
                value_obj.interval,
            )


class Scale(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
        self.scale_mode = "Original"  # 'DFoF' or 'Normalize'

    def __del__(self):  # make a message when this object is deleted.
        print(".")
        print(f"----- Deleted a Scale object. + {format(id(self))}")
        # pass

    # 'Normal' or 'DFoF' or 'Normalize'
    def set_modifier_val(self, mode: str):  # 'DFoF' or 'Normalize'
        self.scale_mode = mode
        print(f"set Scale: {mode}")

    def set_data(self, data_obj) -> object:
        if self.scale_mode == "Original":
            print("Scale:      Original -> No modified")
            return data_obj

        elif self.scale_mode == "DFoF":
            f = Tools.f_value(data_obj.data)
            df_over_f = (data_obj / f - 1) * 100
            print("Scale:      Original -> dF/F")
            return df_over_f

        elif self.scale_mode == "Normalize":
            min_val = np.min(data_obj.data)
            pre_data_obj = data_obj - min_val
            max_val = np.max(pre_data_obj.data)
            normalized_data = pre_data_obj / max_val
            print("Scale:      Original -> Normalized")
            return normalized_data
        else:
            raise ValueError(
                f"No such a scale mode -> {self.scale_mode} "
                f"check set_modifier_val in Scale"
            )


class BlComp(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
        self.bl_mode = "Disable"  # or 'PolyVal' or 'Exponential'
        self.baseline_window = None  # This is to show the baseline and fitting curve
        self.cutting_time_window = [0, 0]  # [start, width]

    def __del__(self):  # make a message when this object is deleted.
        print(".")
        print(f"----- Deleted a BlComp object. + {format(id(self))}")
        # pass

    def set_modifier_val(self, val):  # val = [start, width]
        if isinstance(val, str):
            self.bl_mode = val
            print(f"set BlComp: {self.bl_mode}")  # 1.Disable, 2.Enable
        elif isinstance(val, list):
            self.cutting_time_window = val
            print(
                f"BlComp: Set new cutting time window value {self.cutting_time_window}"
            )
        else:
            raise ValueError(f"value: '{val}' should be a string or a list")

    def set_data(self, data_obj) -> object:
        if self.bl_mode == "Disable":
            print("BlComp:     No modified")
            return data_obj
        # make Polyval fitting curve
        elif self.bl_mode == "PolyVal":
            print("BlComp:     Enable -> <PolyVal> baseline compensation")
            degree_poly = 2
            data_type = data_obj.data_tag["DataType"].replace("Trace", "Frames")
            bl_trace_raw = self.observer.notify_observer_second_obj(data_type)
            bl_trace = bl_trace_raw.slice_data(
                self.cutting_time_window[0], self.cutting_time_window[1]
            )

            mu = [np.mean(bl_trace.time), np.std(bl_trace.time)]
            # time data centering and scaling
            t_scaled = (bl_trace.time - mu[0]) / mu[1]
            # Polynomial fitting with scaled data
            fitcoef = np.polyfit(t_scaled, bl_trace.data, degree_poly)
            # Evaluate fitted polynomial in data points
            # fitting_trace = np.polyval(fitcoef, t_scaled)
            # Scaling x values
            x_scaled = (data_obj.time - mu[0]) / mu[1]
            # Evaluate polynomial
            fitting_trace_raw = np.polyval(fitcoef, x_scaled)
        # make exponential fitting curve: currently doen't work well
        elif self.bl_mode == "Exponential":
            print("BlComp:     Enable -> <Exponential> baseline compensation")
            data_type = data_obj.data_tag["DataType"].replace("Trace", "Frames")
            bl_trace_raw = self.observer.notify_observer_second_obj(data_type)

            bl_trace = bl_trace_raw.slice_data(
                self.cutting_time_window[0], self.cutting_time_window[1]
            )

            initial_guess = (np.max(bl_trace.data), -0.1, np.min(bl_trace.data))
            popt, pcov = curve_fit(
                Tools.exponential_func,
                bl_trace.time,
                bl_trace.data,
                p0=initial_guess,
                maxfev=2000,
            )

            a_fit, b_fit, c_fit = popt
            fitting_trace_raw = Tools.exponential_func(
                data_obj.time, a_fit, b_fit, c_fit
            )
        else:
            raise ValueError(
                f"No such a BlComp mode -> '{self.bl_mode}' \n "
                f"check set_modifier_val in BlComp"
            )

        # make baseline value object
        fit_baseline_obj = TraceData(
            fitting_trace_raw, bl_trace.data_tag, bl_trace.interval
        )
        # get ratio of f (data/baseline)
        f_val = Tools.f_value(data_obj.data)
        baseline_f_val = Tools.f_value(fit_baseline_obj.data)
        f_val_ratio = f_val / baseline_f_val
        # set size of baseline to data
        norm_bl_trace = fit_baseline_obj * f_val_ratio
        # get comp delta F
        delta_F_trace = data_obj - norm_bl_trace
        bl_comp_trace = delta_F_trace + f_val

        # show a baseline fitting trace : this should be in the view class
        if self.baseline_window is None:
            self.baseline_window = pg.plot()
            self.baseline_window.setWindowTitle("Baseline fitting")
            self.baseline_window.setGeometry(100, 100, 200, 150)
        else:
            self.baseline_window.clear()
        bl_trace.show_data(self.baseline_window)
        fit_baseline_obj.show_data(self.baseline_window)

        return bl_comp_trace


class DifImage(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
        # self._val_obj is for subtracting image

    def set_modifier_val(self, val: list):  # val = [start, width]
        start, width = val
        self._val_obj = TimeWindowVal(start, width)  # replace the roi
        print(f"set DifImage: {self._val_obj.data} ")

    def set_data(self, data_obj) -> object:
        print("DifImage:     Enable")
        data_type = data_obj.data_tag["DataType"].replace("Image", "Frames")
        bl_trace = self.observer.notify_observer_second_obj(data_type)
        dif_image = bl_trace - data_obj
        return dif_image


class Invert(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)

    def set_modifier_val(self):
        raise NotImplementedError()

    def set_data(self, data_obj) -> object:
        return data_obj * -1


# currently noting meaning. but in future this is working with saving in the repository
class TagMaker(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
        self.tag_dict = {}  # 'DFoF' or 'Normalize'

    def __del__(self):  # make a message when this object is deleted.
        print(".")
        print(f"----- Deleted a TagMaker object. + {format(id(self))}")
        # pass

    def set_modifier_val(self, new_tag_dict: dict):  # val = [start, width]
        self.tag_dict = new_tag_dict
        print(f"set TagMaker: {new_tag_dict}")

    def set_data(self, data_obj) -> object:
        print(f"TagMaker:     New tag -> {self.tag_dict}")
        data_obj.data_tag.update(self.tag_dict)
        return data_obj


class EndModifier(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)

    # overwrite
    def apply_modifier(self, data_obj, modifier_list):
        assert modifier_list == [], (
            f"EndModifier: Modifier Error. {modifier_list} didn't use."
        )
        return data_obj

    def set_modifier_val(self):
        pass

    def set_data(self, data_obj):
        pass


class Observer:
    def __init__(self):
        self._observers = []

    def set_observer(self, observer):
        for check_observer in self._observers:
            if check_observer == observer:
                self._observers.remove(observer)
                print(f"Observer removed {observer.__class__.__name__}")
                return
        self._observers.append(observer)
        print(
            f"Controller observer added {observer.__class__.__name__} to a user controller"
        )

    def notify_observer(self):
        for observer_name in self._observers:
            # enable view axes update
            observer_name.set_update_flag(True)
            # This is for direct view axes update
            # observer_name.update()
        # print("Update Notification from ROI")

    def notify_observer_second_obj(self, data_type) -> object:
        for observer_name in self._observers:
            return observer_name.make_second_obj(data_type)

    @property
    def observers(self) -> list:
        return self._observers
