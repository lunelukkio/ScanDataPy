# -*- coding: utf-8 -*-
"""
Created on Thu ug 29 15:16:57 2024

@author: lunelukkio
"""

from abc import ABCMeta, abstractmethod
import numpy as np

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
    def set_modifier_val(self, val):
        raise NotImplementedError()


class ModifierService(ModifierServiceInterface):
    def __init__(self):
        self.__current_modifier = None
        # chain always should have start and end
        self.__start_modifier = StartModifier('StartModifier')
        # make a default modifier chain list
        self.__modifier_chain_list = [self.__start_modifier,
                                      EndModifier('EndModifier')]
        # make a modifier chain from the chain list
        self.__modifier_chain = ModifierService.make_modifier_chain(
            self.__modifier_chain_list)
        self.print_chain()

    @property
    def modifier_chain_list(self):
        return self.__modifier_chain_list

    # This is actual method run by DataService and return modified data
    def apply_modifier(self, data, modifier_list=None):
        # start the chain of responsibility and get modded data
        modified_data = self.__start_modifier.apply_modifier(data,
                                                             modifier_list)
        print("77777777777777777777777777777777777777777")
        print(modified_data)
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
            self.__modifier_chain_list)
        # make a modifier chain from the chain list
        self.__modifier_chain = ModifierService.make_modifier_chain(
            self.__modifier_chain_list)

    def remove_chain(self, modifier_name):
        # remove modifier_name object from the list
        self.__modifier_chain_list = [obj for obj in self.__modifier_chain_list
                                      if obj.modifier_name != modifier_name]
        # sort and add start chain
        self.__modifier_chain_list = ModifierService.sort_chain_list(
            self.__modifier_chain_list)
        # make a modifier chain from the chain list
        self.__modifier_chain = ModifierService.make_modifier_chain(
            self.__modifier_chain_list)

    @staticmethod
    def check_modifier_type(modifier_name):
        if 'TimeWindow' in modifier_name:
            return TimeWindowFactory()
        elif 'Roi' in modifier_name:
            return RoiFactory()
        elif 'Average' in modifier_name:
            return AverageFactory()
        elif 'Scale' in modifier_name:
            return ScaleFactory()
        elif 'BlComp' in modifier_name:
            return BlCompFactory()
        else:
            raise ValueError(f"{modifier_name} Factory done not exist.")

    # To make a number for modifier.
    def __num_maker(self, modifier_name):
        modifier_name_list = [modifier.modifier_name for modifier in
                              self.__modifier_chain_list]
        # Count existing modifier name
        i = 0
        while True:
            current_name = f'{modifier_name}{i}'
            if not current_name in modifier_name_list:
                break
            i += 1
        new_name = modifier_name + str(i)
        return new_name

    # modifier list always should be done by this list order.
    @staticmethod
    def sort_chain_list(old_obj_list):
        new_order_word_list = [
            'StartModifier',
            'TimeWindow',
            'Roi',
            'Average',
            'Scale',
            'BlComp',
            'EndModifier'
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
                modifier_chain_list[index].set_next(
                    modifier_chain_list[index + 1])
                # next object
                set_chain(index + 1)

        # if there is objects in the list
        if modifier_chain_list:
            # start from the first object
            set_chain(0)
            # return the chain
        return modifier_chain_list[0] if modifier_chain_list else None

    def print_chain(self):
        print("ModifierService: modifier_chain -> ", end="")
        current_modifier = self.__start_modifier
        while current_modifier:
            print(f"{current_modifier.modifier_name}.", end="")
            current_modifier = current_modifier.next_modifier
        print("")

    def set_modifier_val(self, modifier_name, *args, **kwargs):
        for modifier_obj in self.__modifier_chain_list:
            if modifier_name == modifier_obj.modifier_name:
                modifier_obj.set_val(*args, **kwargs)


""" abstract factory """


class ModifierFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_modifier(self,
                        modifier_name: dict):  # data_tag = controller_key dict
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


""" super class """


class ModifierHandler(metaclass=ABCMeta):  # BaseHandler
    def __init__(self, modifier_name):
        self.__modifier_name = modifier_name
        self.__next_modifier = None
        self._val_obj = None
        self.observer = Observer()

    def __del__(self):  #make a message when this object is deleted.
        print('.')
        #print(f"----- Deleted a object.' + ' {format(id(self)}")
        #pass

    def set_next(self, next_modifier):
        self.__next_modifier = next_modifier
        return next_modifier

    def modifier_request(self, data, modifier_list):
        if self.__next_modifier:
            return self.__next_modifier.apply_modifier(data, modifier_list)

    def apply_modifier(self, data, modifier_list):
        if self.modifier_name in modifier_list:
            new_data = self.set_data(data)
            # set True of update on each AxesController
        else:
            new_data = data
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
    def set_val(self):
        raise NotImplementedError()

    def get_val(self):  # e.g. roi value
        return self._val_obj

    @abstractmethod
    def set_data(self, data):
        raise NotImplementedError()

    def set_observer(self, observer):
        self.observer.set_observer(observer)

    def notify_observer(self):
        self.observer.notify_observer()


"""concrete modifier"""


class StartModifier(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)

    def apply_modifier(self, data, modifier_list):
        return super().modifier_request(data, modifier_list)

    def set_val(self):
        pass

    def set_data(self, data):
        pass

class TimeWindow(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
        self._val_obj = TimeWindowVal(0, 1)

    def __del__(self):  #make a message when this object is deleted.
        print('.')
        print(f"----- Deleted a TimeWindow object. + {format(id(self))}")
        #pass

    def set_val(self, val: list):  # val = [start, width]
        window_value_list = val
        start = window_value_list[0]
        width = window_value_list[1]
        self._val_obj = TimeWindowVal(start,
                                      width)  # replace the roi
        self.observer.notify_observer()
        print(f"set TimeWindow: {self._val_obj.data} and notified")

    # calculate a image from a single frames data with a time window value object
    def set_data(self, origin_data):
        if origin_data is None:
            raise Exception("TimeWindow: origin_data is empty.")
        elif all('FluoFrames' not in str for str in list(origin_data.data_tag.values())):
            # print("ImageController: {origin_data.data_tag} is not FluoFrames value object. Skip This data.")
            return
        # check value is correct
        TimeWindow.check_val(origin_data, self._val_obj)
        # make raw trace data
        start = self._val_obj.data[0]
        width = self._val_obj.data[1]
        # slice end is end+1
        data = origin_data.data[:, :, start:start + width]

        print(
            "TimeWindow: A frames from frame# {start} to {start+width-1}")
        # take Ch from DataType
        ch = Tools.take_ch_from_str(origin_data.data_tag['DataType'])
        return FramesData(
            data,
            {
                'Filename': origin_data.data_tag['Filename'],
                'Attribute': 'Data',
                'DataType': 'FluoFrames' + ch,
                'Origin': self.modifier_name
            },
            origin_data.interval,
            origin_data.pixel_size
        )

    @staticmethod
    def check_val(frames_obj, time_window_obj) -> bool:
        # convert to raw values
        time_window = time_window_obj.data
        # check the value is correct. See TimeWindowVal class.
        frame_length = frames_obj.data.shape[2]
        # check the start and end values
        if time_window[0] < 0:
            raise Exception('The start frame should be 0 or more.')
        if time_window[1] < 1:
            raise Exception('The width should be 1 or more.')
        # compare the val to frame lentgh
        if time_window[0] + time_window[1] > frame_length:
            raise Exception(
                f"The total frame should be less than {frame_length - 1}.")
        else:
            return True

    def reset(self) -> None:
        self.set_val([0, 1])


class Roi(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
        self._val_obj = RoiVal(40, 40, 1, 1)

    def __del__(self):  # make a message when this object is deleted.
        print('.')
        print(f"----- Deleted a Roi object. + {format(id(self))}")
        #pass

    # make a new ROI value object
    def set_val(self, val: list):
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
                    roi_val[i] = self._val_obj.data[
                        i]  # for width and height
                else:
                    roi_val[i] = self._val_obj.data[i] + roi_val[i]
        self._val_obj = RoiVal(*roi_val[:4])  # replace the roi
        self.observer.notify_observer()
        print(f"set Roi: {self._val_obj.data} and notified")

    # calculate a trace from a single frames data with a roi value object
    def set_data(self, origin_data: object):
        if origin_data is None:
            raise Exception("ROI: origin_data is empty.")
        elif all('FluoFrames' not in str for str in list(origin_data.data_tag.values())):
            # print(f"ROI: {origin_data.data_tag['DataType']} is not FluoFrames value object. Skip This data.")
            return
        roi_obj = self._val_obj
        # check value is correct
        Roi.check_val(origin_data, roi_obj)
        # make raw trace data
        x, y, x_width, y_width = roi_obj.data[:4]
        print("7777777777777777777777777777777777777777777")
        print(x)
        print(y)
        print(np.shape(origin_data))
        data = origin_data.data[x:x + x_width, y:y + y_width, :]
        print(np.shape(data))
        # make a trace value object
        print(f"Roi:A frames from {roi_obj.data}")
        # take Ch from DataType
        ch = Tools.take_ch_from_str(origin_data.data_tag['DataType'])
        new_data = FramesData(
            data,
            {
                'Filename': origin_data.data_tag['Filename'],
                'Attribute': 'Data',
                'DataType': 'FluoFrames' + ch,
                'Origin': self.modifier_name
            },
            origin_data.interval
        )
        return new_data

    @staticmethod
    def check_val(frames_obj, roi_obj) -> bool:
        # convert to raw values
        roi = roi_obj.data
        # check the value is correct. See ROIVal class.
        frames_size = frames_obj.shape
        if roi[0] + roi[2] - 1 > frames_size[0] or roi[1] + roi[3] - 1 > \
                frames_size[1]:  # width is always 1 or more.
            raise Exception(
                "The roi size should be the same as the image size or less")
        if roi[0] < 0 or roi[1] < 0:
            raise Exception("The roi should be the same as 0 or more")
        if roi[2] < 1 or roi[3] < 1:
            raise Exception("The roi width should be the same as 1 or more")
        else:
            return True

    def reset(self) -> None:
        self.set_val([40, 40, 1, 1])


class Average(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
        self.average_mode = 'None' # 'Image' or 'Trace'

    def __del__(self):  # make a message when this object is deleted.
        print('.')
        print(f"----- Deleted a Average object. + {format(id(self))}")
        # pass

    # average direction. 1 is for images, 2 is for traces
    def set_val(self, val: str):  # val = [start, width]
        self.average_mode = val
        print(f"set Average: {self.average_mode}  1=Image, 2=Trace")

    def set_data(self, data):
        if any('Image' in str for str in data.data_tag.values()):
            self.average_mode = 'Image'
        elif any('Roi' in str for str in data.data_tag.values()):
            self.average_mode = 'Roi'
        if self.average_mode == 'Image':
            # mean to image
            data = np.mean(data, axis=2)
            print("Average: Averaged a FluoFrames to an image")
            # take Ch from DataType
            ch = Tools.take_ch_from_str(data.data_tag['DataType'])
            return ImageData(
                data,
                {
                    'Filename': data.data_tag['Filename'],
                    'Attribute': 'Data',
                    'DataType': 'FluoImage' + ch,
                    'Origin': self.modifier_name
                },
                [0, 0]  # pixel size
        )
        if self.average_mode == 'Roi':
            # mean to trace
            data = np.mean(data, axis=(0, 1))
            # make a trace value object
            print(f"Average: Averaged a FluoFrames to a trace")
            # take Ch from DataType
            ch = Tools.take_ch_from_str(data.data_tag['DataType'])
            return TraceData(
                data,
                {
                    'Filename': data.data_tag['Filename'],
                    'Attribute': 'Data',
                    'DataType': 'FluoTrace' + ch,
                    'Origin': self.modifier_name
                },
                data.interval
            )


class Scale(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)
        self.scale_mode = 'Normal' # 'DFoF' or 'Normalize'

    def __del__(self):  # make a message when this object is deleted.
        print('.')
        print(f"----- Deleted a Scale object. + {format(id(self))}")
        # pass

    # 'Normal' or 'DFoF' or 'Normalize'
    def set_val(self, mode: str):  # 'DFoF' or 'Normalize'
        self.scale_mode = mode
        print(f"set Scale: {mode}")

    def set_data(self, data) -> object:
        if self.scale_mode == 'Normal':
            print("Scale: Normal -> No modified")

        elif self.scale_mode == 'DFoF':
            # make dF/F value object
            df_over_f = Tools.create_df_over_f(data)
            return df_over_f

        elif self.scale_mode == 'Normalize':
            normalized_data = Tools.create_normalize(data)
            # return Normalized value object
            return normalized_data

        else:
            raise ValueError(f"No such a scale mode -> {self.scale_mode} "
                             f"check set_val in Scale" )


class BlComp(ModifierHandler):
    def set_val(self, data):  # data = baseline trace obj
        pass

    def set_data(self, data):
        pass










class EndModifier(ModifierHandler):
    def __init__(self, modifier_name):
        super().__init__(modifier_name)

    def apply_modifier(self, data, modifier_list):
        return data

    def set_val(self):
        pass

    def set_data(self, data):
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
            f"Controller observer added {observer.__class__.__name__} to a user controller")

    def notify_observer(self):
        for observer_name in self._observers:
            # enable view axes update
            observer_name.set_update_flag(True)
            # This is for direct view axes update
            # observer_name.update()
        # print("Update Notification from ROI")

    @property
    def observers(self) -> list:
        return self._observers
