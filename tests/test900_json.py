# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 10:55:57 2023

@author: lunel
"""

import json

scandata_setting = {
    "color_ch": {"Ch0": "black",
                 "Ch1": "red",
                 "Ch2": "blue"},
    "color_roi" : {"Roi1": "black",
                    "Roi2": "red",
                    "Roi3": "blue",
                    "Roi4": "green",
                    "Roi5": "purple",
                    "Roi6": "brown",
                    "Roi7": "pink",
                    "Roi8": "olive",
                    "Roi9": "cyan",
                    "Roi10": "orange"}
    }


json_data = json.dumps(scandata_setting, indent=4)

print(json_data)

with open("scandata_setting.json", "w") as json_file:
    json_file.write(json_data)