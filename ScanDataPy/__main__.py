# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:29:01 2024

@author: lunelukkio
"""

from ScanDataPy.common_class import FileService
from ScanDataPy.view.view import QtDataWindow
import sys
import os


# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from PyQt6 import QtWidgets  # noqa: E402


# Main controller class for the application
class Main:
    def __init__(self):
        print("============== Main ==============")
        print("          Start SCANDATA          ")
        print("==================================")

        self.__file_service = FileService()
        self.data_window_list = {}

        # Initialize QApplication (view class)
        self.scandata = QtWidgets.QApplication(sys.argv)
        self.main_window = MainWindow(self)
        self.main_window.show()

        # Start the Qt event loop unless the user is in an interactive prompt
        if sys.flags.interactive == 0:
            self.scandata.exec()

    def open_file(self):
        filename_obj = self.__file_service.open_file()
        same_ext_file_list = self.__file_service.get_files_with_same_extension(
            filename_obj.fullname
        )
        self.main_window.update_file_list(same_ext_file_list)

        # Create and show QtDataWindow
        new_window = QtDataWindow()
        new_window.open_file(filename_obj)
        new_window.show()
        self.data_window_list[filename_obj.name] = new_window

        # Update the file list
        self.update_file_list()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, scandata_controller):
        super().__init__()
        self.setWindowTitle("SCANDATA Main Window")
        self.scandata_controller = scandata_controller  # Main class

        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Create list widget for files
        self.file_list = QtWidgets.QListWidget()
        self.file_list.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
        )

        # Set minimum size for better visibility
        self.file_list.setMinimumSize(300, 200)

        # Add list widget to layout
        layout.addWidget(self.file_list)

        # Create load button
        load_btn = QtWidgets.QPushButton("Load")
        load_btn.setFixedSize(100, 30)
        load_btn.clicked.connect(self.load_file)
        layout.addWidget(load_btn)

    def update_file_list(self):
        """
        Update the file list with files from filename_obj
        """
        self.file_list.clear()
        if hasattr(self, "_main_controller") and hasattr(
            self._main_controller, "filename_obj"
        ):
            # Get the folder path from filename_obj
            folder_path = os.path.dirname(self._main_controller.filename_obj.fullname)
            # Get all files in the folder
            files = [f for f in os.listdir(folder_path) if f.endswith(".tsm")]
            for file in files:
                self.file_list.addItem(os.path.join(folder_path, file))

    def load_file(self):
        # scandata_controller = Main class
        self.scandata_controller.open_file()


if __name__ == "__main__":
    app = Main()