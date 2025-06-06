# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 18:02:18 2022

lunelukkio@gmail.com
"""

import unittest
from ScanDataPy.common_class import WholeFilename
from ScanDataPy.model.value_object import FramesData
from ScanDataPy.model.file_io import TsmFileIo
try:
    import pyqtgraph as pg
    from pyqt6.QtWidgets import QApplication, QMainWindow
except:
    pass


filename_obj = WholeFilename('..\\220408\\20408B002.tsm')  # this isa a value object

class TestFrames(unittest.TestCase):
    def test_frame(self):

        file_io = TsmFileIo(filename_obj)

        rawdata = file_io.get_3d()

        data_channel = 0  # 0:fullFrames 1,2: chFrames
        frame_num = 0

        test = FramesData(rawdata[data_channel])

        app = QApplication([])
        image_view = pg.ImageView()
        test.show_data(frame_num, image_view)
        image_view.show()
        app.exec_()


if __name__ == '__main__':
    unittest.main()