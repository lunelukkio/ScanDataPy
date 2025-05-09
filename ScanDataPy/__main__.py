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

from PyQt6 import QtWidgets, QtCore  # noqa: E402

from ScanDataPy.common_class import FileService  # noqa: E402; Import Filename
from ScanDataPy.view.view import QtDataWindow  # noqa: E402


# Main controller class for the application
class Main:
    def __init__(self, file_service=FileService(), qt_app=None):
        print("============== Main ==============")
        print("          Start SCANDATA          ")
        print("==================================")

        # Allow dependency injection for testing
        self.__file_service = file_service
        self.data_window_list = {}

        # Initialize QApplication (view class)
        self.scandata = (
            qt_app if qt_app is not None else QtWidgets.QApplication(sys.argv)
        )
        self.main_list_window = MainListWindow(self)
        self.main_list_window.show()

        # Start the Qt event loop unless the user is in an interactive prompt
        if sys.flags.interactive == 0 and qt_app is None:
            self.scandata.exec()

    def open_file(self):
        filename_obj = self.__file_service.open_file()
        if (
            not filename_obj
        ):  # Handle case where no file is selected or dialog is cancelled
            print("File selection cancelled or failed.")
            return

        same_ext_file_list = self.__file_service.get_files_with_same_extension(
            filename_obj.fullname
        )
        self.main_list_window.update_file_list(same_ext_file_list)

        # Create and show QtDataWindow
        new_data_controller = QtDataWindow(self.main_list_window)
        new_data_controller.open_file(filename_obj)
        new_data_controller.show()
        self.data_window_list[filename_obj.name] = new_data_controller
        print(f"Created {filename_obj.name}.")

    def open_file_from_list(self, full_name: str):
        if not full_name or not os.path.exists(full_name):
            print(f"Invalid file name from list: {full_name}")
            return
        filename_obj = self.__file_service.open_file(full_name)

        # Create and show QtDataWindow for the selected file
        new_data_controller = QtDataWindow(self.main_list_window)
        new_data_controller.open_file(filename_obj)
        new_data_controller.show()
        self.data_window_list[filename_obj.name] = new_data_controller
        print(f"Created {filename_obj.name} from list.")
        print(self.data_window_list)


class MainListWindow(QtWidgets.QMainWindow):
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
        self.file_list.itemClicked.connect(
            self.handle_file_item_clicked
        )  # Connect itemClicked signal

        # Set minimum size for better visibility
        self.file_list.setMinimumSize(300, 200)

        # Add list widget to layout
        layout.addWidget(self.file_list)

        # Create load button
        load_btn = QtWidgets.QPushButton("Load")
        load_btn.setFixedSize(100, 30)
        load_btn.clicked.connect(self.load_file)
        layout.addWidget(load_btn)

    def update_file_list(self, files_to_display: list[str]):
        """
        Update the file list with the provided list of file paths.
        Display only the file names but store the full paths as item data.
        """
        self.file_list.clear()
        for full_path in files_to_display:
            # Extract just the file name from the full path
            file_name = os.path.basename(full_path)
            # Create a new item with the file name
            item = QtWidgets.QListWidgetItem(file_name)
            # Store the full path as item data for later retrieval
            item.setData(QtCore.Qt.ItemDataRole.UserRole, full_path)
            self.file_list.addItem(item)

    def handle_file_item_clicked(self, item: QtWidgets.QListWidgetItem):
        """Handles the event when an item in the file list is clicked."""
        # Get the full path from the item's data
        selected_file_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if selected_file_path:
            self.scandata_controller.open_file_from_list(selected_file_path)

    def load_file(self):
        # scandata_controller = Main class
        self.scandata_controller.open_file()

    def closeEvent(self, event):
        """Close all associated QtDataWindow instances when MainListWindow is closed."""
        # Iterate over a copy of the dictionary's keys in case the dictionary is modified during iteration
        for window_name in list(self.scandata_controller.data_window_list.keys()):
            child_window = self.scandata_controller.data_window_list.pop(
                window_name, None
            )
            if child_window:
                child_window.close()  # Explicitly close the child window
        super().closeEvent(event)  # Call the parent class's closeEvent


def create_app():
    """Create and return a new application instance.
    This function is useful for testing as it separates app creation from running.
    """
    return Main()


if __name__ == "__main__":
    app = create_app()
