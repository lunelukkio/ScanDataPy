# ScanDataPy
Readme 2024/09/27 lunelukkio@gmail.com


baseline compensation is defined by controller_main.py, MainController class, def get_base_line_data

file_setting.json

{
  "tsm": {
    "num_ch": 2,
    "num_elec_ch": 8,
    "default_settings": {
      "default_modifiers": [
        "TimeWindow0",
        "TimeWindow1",
        "TimeWindow2",
        "TimeWindow3",
        "Roi0",
        "Roi1",
        "Average0",
        "Average1",
        "Scale0",
        "BlComp0"
      ],
      "modifier_default_val": {
          "TimeWindow0": [0, 5],   for difference image 
          "TimeWindow1": [0, 5],   for difference image
          "TimeWindow2": [0, -1],  elec trace (whole trace)
          "TimeWindow3": [0, -1],  baseline compensation(whole trace)
          "Roi0": [40, 40, 1, 1],  for baseline comp
          "Roi1": [40, 40, 1, 1],   fluotrace but also for baseline comp
          "Average0": "Image",  for image
          "Average1": "Roi",    for trace
          "Scale0": "Original",  origin, DFoF, Normarize
          "BlComp0": "Normal"    Normal, 
      },
      "default_observer": {
        "FluoAxes": ["Roi0", "Roi1"],
        "ImageAxes": ["TimeWindow0", "TimeWindow1"],
        "ElecAxes": ["TimeWindow2", "TimeWindow3"]
      },
      "main_default_tag": {
        "attribute_list": ["Data"],
        "data_type_list": ["FluoFramesCh1", "FluoFramesCh2"],
        "origin_list": ["File"]
      },
      "image_ax_default_tag": {
        "attribute_list": ["Data"],
        "data_type_list": ["FluoFramesCh1"],
        "origin_list": ["File"],
        "modifier_list": ["TimeWindow1", "Average0"]
      },
      "trace_ax_default_tag": {
        "attribute_list": ["Data"],
        "data_type_list": ["FluoFramesCh1"],
        "origin_list" : ["File"],
        "modifier_list": ["Roi1", "Average1", "Scale0", "BlComp0"]
      },
      "elec_ax_default_tag": {
        "attribute_list": ["Data"],
        "data_type_list": ["ElecTraceCh1"],
        "origin_list" : ["File"],
        "modifier_list": ["TimeWindow2"]
      },
      "baseline_trace": {
        "Filename":"None",
        "Attribute":"Data",
        "DataType":"FluoFramesCh1",
        "Origin": "File"
      }
    }
  },
  "da": {
    "num_ch": 2,
    "num_elec_ch": 8,
    "default_controller": {
      "ROI": 2,
      "ImageController": 2,
      "ElecTraceController": 2
    }
  }
}
