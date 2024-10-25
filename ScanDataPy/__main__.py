# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:29:01 2024

@author: lunelukkio
"""

import sys
from PyQt6 import QtWidgets
from ScanDataPy.view.view import QtDataWindow


class Main:
    def __init__(self):
        print("============== Main ==============")
        print('          Start SCANDATA')
        print("==================================")

        # Initialize QApplication
        self.scandata = QtWidgets.QApplication(sys.argv)
        self.mainWindow = QtDataWindow()
        self.mainWindow.show()

        # Start the Qt event loop unless the user is in an interactive prompt
        if sys.flags.interactive == 0:
            self.scandata.exec()

if __name__ == '__main__':
    app = Main()