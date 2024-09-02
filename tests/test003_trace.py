# -*- coding: utf-8 -*-
"""
Created on Sun Dec 25 13:33:19 2022

@author: lulul
"""     
import unittest
import sys
from ScanDataPy.common_class import WholeFilename
from ScanDataPy.model.value_object import TraceData
from ScanDataPy.model.file_io import TsmFileIo
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow




filename_obj = WholeFilename('..\\220408\\20408B002.tsm')  # this isa a value object

class Test(unittest.TestCase):
    def test(self):


        file_io = TsmFileIo(filename_obj)
        
        text = file_io.get_infor()
        print(text)

        rawdata = file_io.get_3d()
        
        data_channel = 0  # 0:fullFrames 1,2: chFrames
        
        x = 40
        y = 40
        interval = 1
        
        data = rawdata[data_channel][x,y,:]
        test = TraceData(data, {'Attribute':"ROI1", 'ch':'Ch1'}, interval,)

        
        app = QApplication([])
        #app = pg.mkQApp("My Application")

        try:
            plot_window = pg.plot(title="Simple Plot Example")
            test.show_data(plot_window)
            if (sys.flags.interactive != 1) or not hasattr(pg.QtCore, 'PYQT_VERSION'):
                app.exec_()
        except:
            test.show_data()
            

        

if __name__ == '__main__':
    unittest.main()