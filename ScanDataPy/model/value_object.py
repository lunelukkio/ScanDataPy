# -*- coding: utf-8 -*-
"""
Created on Sun Jan  1 10:04:06 2023

@author: lunelukkio@gmail.com
"""
import sys
from abc import ABCMeta, abstractmethod
import numpy as np
import pyqtgraph as pg
import inspect

        
"""
Value object
"""
class ValueObj(metaclass=ABCMeta): 
    def __init__(self, val, data_tag):
        self._data = val
        if isinstance(val, np.ndarray):
            self._shape = val.shape  # data dimension e.g. frames [pixel, pixel, frame]
        else:
            self._shape = None
        self._data_tag = data_tag
        
    def __del__(self):
        #print('.')
        #print(f'Deleted {self.__class__.__name__}: myId= {format(id(self))}')
        pass
        
    @property
    def data(self) -> np.ndarray:
        return self._data
    
    @data.setter
    def data(self, val):
        raise Exception('Value object should be Immutable.')
        
    @property
    def shape(self) -> int:
        return self._shape

    @property
    def data_tag(self) -> list:
        return self._data_tag
    
    @data_tag.setter
    def data_tag(self, data_tag: dict):
        raise Exception('Value object should be Immutable.')
    
    @abstractmethod
    def show_data(self, plt):
        raise NotImplementedError()

class FramesData(ValueObj):
    def __init__(self, 
                 val: np.ndarray, 
                 data_tag=None,
                 interval=0,
                 pixel_size=None):
        super().__init__(val, data_tag)
        assert val.ndim == 3, 'The argument of FrameData should be numpy 3D data(x, y, t)'
            
        self.__interval = interval  # frame interval (ms)
        self.__pixel_size = pixel_size  #actual length (um)
   
    # This is for background subtraction
    def __sub__(self):
        raise NotImplementedError()
            
    @property
    def interval(self):
        return self.__interval

    @property
    def pixel_size(self):
        return self.__pixel_size

    # plt should be an axes in a view class object = AxesImage
    def show_data(self, frame_num, plt=pg) -> object:
        return plt.setImage(self._data[:, :, frame_num])



class ImageData(ValueObj):
    def __init__(self, 
                 val: np.ndarray, 
                 data_tag=None,
                 pixel_size=None):
        super().__init__(val, data_tag)
        assert val.ndim == 2, 'The argument of ImageData should be numpy 2D data(x, y)'
            
        self.__pixel_size = pixel_size

    @property
    def pixel_size(self):
        return self.__pixel_size

    # This is for difference image
    def __sub__(self):
        raise NotImplementedError()
    
    def show_data(self, plt=pg) -> object:    # plt should be an axes in a view class object = AxesImage
        return plt.setImage(self._data)

    
class TraceData(ValueObj):
    def __init__(self, 
                 val: np.ndarray,  
                 data_tag=None,
                 interval=0):
        super().__init__(val, data_tag)
        assert val.ndim == 1, 'The argument of TraceData should be numpy 1D data(x)'
        if  val.shape[0] < 5: 
            print('------------------------------------------------------------------------')
            print('This data length is ' + str(val))
            print('Warning!!! The number of the data points of TraceData is less than 5 !!!')
            print('It makes a bug during dF over calculation !!!')
            print('------------------------------------------------------------------------')

        self.__time = self.__create_time_data(val, interval)
        self.__length = val.shape[0]  # the number of data points
        self.__interval = interval  # data interval

    @property
    def time(self) -> np.ndarray:
        return self.__time

    @time.setter
    def time(self, val):
        raise Exception('TimeData is a value object (Immutable).')

    @property
    def length(self) -> int:
        return self.__length

    @property
    def interval(self) -> float:
        return self.__interval

    def operator(self, val_obj, func, operation):
        if type(val_obj) in [float, int, np.int64, np.float64]:
            trace = func(self._data, val_obj)
        else:
            assert type(val_obj) == TraceData, "TraceData: Wrong type"
            assert self._data_tag['DataType'] == val_obj.data_tag['DataType'], \
            f"TraceData class: {self._data_tag['DataType']} - {val_obj.data_tag['DataType']} \n" \
            f"Wrong value. This value object should be {operation} by int or float or other value object"
            if len(self._data) != len(val_obj.data):
                print('!!! Caution! The length of these data is not matched!', file=sys.stderr)
            trace = func(self._data, val_obj.data)

        return TraceData(trace, self._data_tag, self.__interval)

    def __add__(self, val_obj) -> object:
        return self.operator(val_obj, np.add, "addition")
        
    def __sub__(self, val_obj) -> object:
        return self.operator(val_obj, np.subtract, "subtracted")

    def __truediv__(self, val_obj) -> object:
        return self.operator(val_obj, np.true_divide, "division")
    
    def __mul__(self, val_obj) -> object:
        return self.operator(val_obj, np.multiply, "multiplication")

    def __create_time_data(self, trace, interval) -> np.ndarray:
        num_data_point = interval * np.shape(trace)[0]
        time_val = np.linspace(interval, num_data_point, np.shape(trace)[0])
        shifted_time_val = time_val - time_val[0]  # This is for shifting the first data to 0ms.
        return shifted_time_val
    
    def check_length(self, data: object) -> bool:
        return bool(self.__length == data.__length)
    
    def show_data(self, plt=pg) -> list:  # plt should be an axes in a view class object = [matplotlib.lines.Line2D]
            return plt.plot(self.__time, self._data) 



class TextData(ValueObj):
    def __init__(self, 
                 val,
                 data_tag=None):
        super().__init__(val, data_tag)

    def show_data(self):
        print("This is Text data")
        print(self._data)

"""
Value object for controller
"""
class RoiVal:  # Should be called by the same class for __add__ and __sub__
    def __init__(self, x: int, y: int, x_width: int, y_width: int, data_type=None):
        if x < 0 or y < 0:  # np.mean slice doesn't include end value. so width should be 1 or more than 1
            print('ROI x and y values should be 0 or more')
        if x_width < 1 or y_width < 1:
            print('ROI width values should be 1 or more')
        self.__data = np.array([x, y, x_width, y_width])  # self.__data should be np.array data.
        called_class = inspect.stack()[1].frame.f_locals['self']
        if data_type is None:
            self.__data_type = called_class.__class__.__name__
        else:
            self.__data_type = data_type
        #print(self.__data_type + ' made a RoiVal' + '  myId= {}'.format(id(self)))
        
    def __del__(self):
        #print('.')
        #print('Deleted a RoiVal object.' + '  myId={}'.format(id(self)))
        pass

    def operate(self, val, func, operation):
        assert self.__data_type == val.data_type, f"Wrong data! Only RoiVal can be {operation}"
        new_val = func(self.__data, val.data)
        new_obj = RoiVal(*new_val)
        new_obj.data_type = self.__data_type
        return new_obj

    #override for "+"
    def __add__(self, val: object)  -> object:
        return self.operate(val, np.add, "added")
    
    def __sub__(self, val: object)  -> object:
        return self.operate(val, np.subtract, "subtracted")
        
    @property
    def data(self) -> list:
        return self.__data
    
    @data.setter
    def data(self, x, y, x_width=1, y_width=1):  
        raise Exception('RoiVal is a value object (Immutable).')
    
    @property
    def data_type(self) -> str:
        return self.__data_type
    
    @data_type.setter
    def data_type(self, data_type) -> None:  
        self.__data_type = data_type
    
    
# self.__data = frame number.  width = -1 means start from the end of the trace
class TimeWindowVal:
    # be careful about end_width. np.mean slice a value not include end.
    def __init__(self, start: int, width=1, data_type=None):
        if start < 0:
            print('TimeWindow start values should be 0 or more')
        if width < 1:
            print('FrameWindow width values should be 1 or more')
        self.__data = np.array([start, width])  # frame number
        called_class = inspect.stack()[1].frame.f_locals['self']
        if data_type is None:
            self.__data_type = called_class.__class__.__name__
        else:
            self.__data_type = data_type
        #print(self.__data_type + ' made a TimeWindowVal' + '  myId= {}'.format(id(self)))
        
    def __del__(self):
        #print('.')
        #print('Deleted a TimeWindowVal object.' + '  myId={}'.format(id(self)))
        pass

    def operate(self, val, func, operation):
        assert self.__data_type == val.data_type, f"Wrong data! Only TimeWindowVal can be {operation}!"
        new_val = func(self.__data, val.data)
        new_obj = TimeWindowVal(new_val)
        new_obj.data_type = self.__data_type
        return new_obj
        
    #override for "+"
    def __add__(self, val: object) -> object:
        self.operate(val, np.add, "added")
    
    def __sub__(self, val: object)  -> object:
        self.operate(val, np.subtract, "subtracted")

    @property
    def data(self) -> list:
        return self.__data
    
    @data.setter
    def data(self, start, width=1):  
        raise Exception('TimeWindowVal is a value object (Immutable).')
    
    @property
    def data_type(self) -> str:
        return self.__data_type
