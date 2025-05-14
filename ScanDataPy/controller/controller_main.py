import sys
import os
from PyQt6 import QtWidgets

from ScanDataPy.view.view_list import DataListWindow
from ScanDataPy.controller.controller_data import DataController
from ScanDataPy.controller.controller_filename import (
    FileService,
    WholeFilename,
    FileHistoryManager,
)


class MainController:
    def __init__(self, gui_app=None):
        self.gui_backend_name = gui_app  # Store the name of the GUI backend
        file_service = FileService(gui_app=self.gui_backend_name)
        self._file_service = file_service

        self.current_file_list = []
        self.data_controller_dict = {}
        self.history_manager = FileHistoryManager()

        # Handle gui_app selection
        if self.gui_backend_name == "pyqt6":
            print("[MainController] PyQt6 has been selected as the GUI backend.")
            # Ensure QApplication instance exists only if not already created
            self.scandata = QtWidgets.QApplication.instance()
            if self.scandata is None:
                self.scandata = QtWidgets.QApplication(sys.argv)
            self.main_list_window = DataListWindow(self)
            self.main_list_window.show()
            if (
                sys.flags.interactive == 0 and self.scandata
            ):  # Check if scandata is not None
                self.scandata.exec()
        elif self.gui_backend_name == "matplotlib":
            print("[MainController] matplotlib has been selected as the GUI backend.")
            # Matplotlib integration is under construction
            raise NotImplementedError("Matplotlib integration is under construction.")
        elif self.gui_backend_name is None:  # Explicitly check for None
            print("[MainController:ERROR] No GUI backend was provided.")
            print("[MainController] Application will be terminated.")
            sys.exit(0)
        else:  # Handle any other unsupported gui_app string
            print(
                f"[MainController:ERROR] Unsupported GUI backend: {self.gui_backend_name}"
            )
            print("[MainController] Application will be terminated.")
            sys.exit(1)  # Exit with an error code

    def open_file(self):
        filename_obj = self._file_service.open_file()
        if not filename_obj:
            print("[MainController] File selection cancelled or failed.")
            return

        # --- open_file specific behavior: update list with all same-extension files ---
        try:
            self.current_file_list = self._file_service.get_files_with_same_extension(
                filename_obj.fullname
            )
            self.main_list_window.update_file_list(self.current_file_list)
            print(
                f"[MainController] Main file list updated with files sharing extension with {filename_obj.name}."
            )
        except Exception as e:
            print(
                f"[MainController:ERROR] Failed to update main list with same-extension files for {filename_obj.name}: {e}"
            )
            # Continue to attempt to open the selected file itself, error in listing siblings should not block this.
        # --- End of open_file specific behavior ---
        self._prepare_data_controller(filename_obj)

    def open_single_file_and_update_list(self):
        filename_obj = self._file_service.open_file()
        self._prepare_data_controller(filename_obj)
        self.current_file_list.append(filename_obj.fullname)
        self.main_list_window.update_file_list(self.current_file_list)

    def open_file_from_list(self, full_name: str):
        if not full_name or not os.path.exists(full_name):
            print(f"[MainController:ERROR] Invalid file name from list: {full_name}")
            return
        filename_obj = self._file_service.open_file(full_name)
        self._prepare_data_controller(filename_obj)

    def _prepare_data_controller(
        self, filename_obj: WholeFilename
    ) -> tuple[DataController | None, bool]:
        """
        Prepares a DataController for the given filename_obj.
        Adds the file to history if a new controller is successfully created.
        Returns a tuple: (DataController instance or None, was_newly_created_boolean).
        - If filename_obj is None, returns (None, False).
        - If a controller for filename_obj.name already exists, prints a message and returns (existing_controller, False).
        - Otherwise, attempts to create a new DataController, stores it, and returns (new_controller, True).
        - If creation fails, returns (None, False).
        """
        if not filename_obj:
            print(
                "[MainController:_prepare_data_controller] Received no valid filename_obj. Cannot prepare DataController."
            )
            return None, False

        assert filename_obj is not None, (
            "[MainController:ERROR] _prepare_data_controller received a null filename_obj despite initial check. This indicates a logic error."
        )

        if filename_obj.name in self.data_controller_dict:
            print(
                f"[MainController] DataController for {filename_obj.name} already exists. Using existing instance."
            )
            return self.data_controller_dict[filename_obj.name], False

        try:
            print(
                f"[MainController] Creating new DataController for {filename_obj.name}."
            )
            data_controller = DataController(self, filename_obj, self.gui_backend_name)
            self.data_controller_dict[filename_obj.name] = data_controller
            print(
                f"[MainController] New DataController for {filename_obj.name} created and stored."
            )
            self.history_manager.add_file(filename_obj)
            return data_controller, True
        except Exception as e:
            print(
                f"[MainController:ERROR] Error creating DataController for {filename_obj.name}: {e}"
            )
            if (
                filename_obj.name in self.data_controller_dict
            ):  # Clean up if partially added
                del self.data_controller_dict[filename_obj.name]
            return None, False

    def display_file_history(self):
        """Displays the recent file history to the console."""
        recent_files = self.history_manager.get_recent_files()
        if not recent_files:
            print("[MainController] File history is empty.")
            if self.gui_backend_name == "pyqt6":
                # Show message box for PyQt6
                if (
                    hasattr(self, "main_list_window")
                    and self.main_list_window.isVisible()
                ):
                    QtWidgets.QMessageBox.information(
                        self.main_list_window,
                        "File History",
                        "File history is currently empty.",
                    )
            return

        print("--- Recent File History ---")
        for idx, file_obj in enumerate(recent_files):
            print(f"{idx + 1}. {file_obj.fullname}")
        print("-------------------------")

        if self.gui_backend_name == "pyqt6":
            # PyQt6 implementation
            if hasattr(self, "main_list_window") and self.main_list_window.isVisible():
                # Create a list of file names for the dialog
                file_names = [file_obj.fullname for file_obj in recent_files]
                # Show dialog to select file
                selected_file, ok = QtWidgets.QInputDialog.getItem(
                    self.main_list_window,
                    "File History",
                    "Select a file to open:",
                    file_names,
                    0,
                    False,
                )
                if ok and selected_file:
                    # Find the corresponding WholeFilename object
                    for file_obj in recent_files:
                        if file_obj.fullname == selected_file:
                            self._prepare_data_controller(file_obj)
                            break
        elif self.gui_backend_name == "matplotlib":
            # Matplotlib implementation is under construction
            print(
                "[MainController] Matplotlib implementation for file history is under construction."
            )
            raise NotImplementedError(
                "Matplotlib implementation for file history is under construction."
            )

    def close_file(self, filename_obj: WholeFilename):
        if filename_obj.name in self.data_controller_dict:
            self.data_controller_dict[filename_obj.name].close()
            del self.data_controller_dict[filename_obj.name]
