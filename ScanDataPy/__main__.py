# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:29:01 2024

@author: lunelukkio
"""

import sys
import os

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from ScanDataPy.controller.controller_main import MainController

if __name__ == "__main__":
    print("============== Main ==============")
    print("          Start SCANDATA          ")
    print("==================================")
    gui_app = 'pyqt6'
    MainController(gui_app)

