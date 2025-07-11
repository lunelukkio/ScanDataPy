# -*- coding: utf-8 -*-
"""
Refactored MainController that creates DataController and View separately,
ensuring no circular dependencies.
"""

import sys
from PyQt6 import QtWidgets

from ScanDataPy.controller.controller_data_refactored import DataController
from ScanDataPy.controller.controller_filename import WholeFilename
from ScanDataPy.view.view_list import ListView


class MainController:
    """
    Main application controller that manages the overall application flow.
    Creates and coordinates the DataController and Views.
    """
    
    def __init__(self, gui_backend='pyqt6'):
        self.gui_backend = gui_backend
        self.app = None
        self.list_window = None
        self.data_controllers = []  # List of data controllers for multiple windows
        
        # Initialize the application
        self._initialize_app()
    
    def _initialize_app(self):
        """Initialize the GUI application"""
        if self.gui_backend == 'pyqt6':
            if QtWidgets.QApplication.instance() is None:
                self.app = QtWidgets.QApplication(sys.argv)
            else:
                self.app = QtWidgets.QApplication.instance()
            
            # Create main list window
            self.list_window = ListView()
            self.list_window.show()
            
            # Connect list window events
            self.list_window.open_data_window_requested.connect(self._create_data_window)
            
            # Start the application
            if sys.flags.interactive == 0:
                self.app.exec()
        else:
            raise ValueError(f"Unsupported GUI backend: {self.gui_backend}")
    
    def _create_data_window(self, filename_obj=None):
        """
        Create a new data window with its own DataController.
        This ensures proper separation of concerns.
        """
        # Create the DataController (no view reference)
        data_controller = DataController(self.gui_backend)
        
        # Create the data window factory based on backend
        if self.gui_backend == 'pyqt6':
            from ScanDataPy.view.view_data_refactored import QtDataWindowFactory
            
            # Create the window with event buses
            data_window = QtDataWindowFactory.create_data_window(
                self.list_window,
                data_controller.view_event_bus,
                data_controller.controller_event_bus
            )
            
            # Initialize axes in the controller after window is created
            axes_config = data_window.get_axes_config()
            data_controller.initialize_axes(axes_config)
            
            # Show the window
            data_window.show()
            
            # If a filename was provided, open it
            if filename_obj:
                data_controller.view_event_bus.file_open_requested.emit(filename_obj)
            
            # Store the controller
            self.data_controllers.append(data_controller)
            
            # Clean up closed controllers
            data_window.destroyed.connect(lambda: self._cleanup_controller(data_controller))
        else:
            raise ValueError(f"Unsupported GUI backend: {self.gui_backend}")
    
    def _cleanup_controller(self, controller):
        """Remove controller when its window is closed"""
        if controller in self.data_controllers:
            self.data_controllers.remove(controller)


def create_app(gui_backend='pyqt6'):
    """Factory function to create the application"""
    return MainController(gui_backend)


if __name__ == "__main__":
    print("============== Main ==============")
    print("          Start SCANDATA          ")
    print("==================================")
    
    # Create and run the application
    app = create_app('pyqt6')