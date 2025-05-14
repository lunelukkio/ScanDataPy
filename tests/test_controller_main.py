import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to Python's search path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from ScanDataPy.controller.controller_main import MainController
from ScanDataPy.controller.controller_filename import WholeFilename # Now used for type checks/assertions
from PyQt6 import QtWidgets # For QApplication setup

class TestMainController(unittest.TestCase):
    qapp = None # Shared QApplication instance

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance once for all tests in this class."""
        cls.qapp = QtWidgets.QApplication.instance()
        if cls.qapp is None:
            cls.qapp = QtWidgets.QApplication(sys.argv)

    @patch('ScanDataPy.controller.controller_main.DataController') # Still mock DataController
    def setUp(self, MockDataController):
        """Called before each test method."""
        self.MockDataController = MockDataController # Store the mock class

        # Ensure sys.flags.interactive is set to prevent QApplication.exec() from blocking.
        # This is important because we are using a real QApplication.
        with patch.object(sys, 'flags', MagicMock(interactive=1)):
            self.controller = MainController(gui_app='pyqt6')
            # self.controller now has real instances of FileService and DataListWindow
            # self.controller.scandata is the real QApplication instance (or from .instance())

        # For convenience, get references to the real instances if needed for direct manipulation/mocking
        self.file_service_instance = self.controller._file_service
        self.main_list_window_instance = self.controller.main_list_window

    def test_open_file_creates_new_controller_and_updates_list(self):
        """
        Tests if the open_file method creates a new DataController
        and updates the related file list, using real FileService and DataListWindow.
        """
        # --- Arrange ---
        test_file_full_path = "/fake/path/test_file.dat"
        test_file_name = "test_file.dat"

        # Mock FileService.get_fullname (called by self.file_service_instance.open_file)
        # This prevents the actual QFileDialog from appearing.
        with patch('ScanDataPy.controller.controller_filename.FileService.get_fullname', return_value=test_file_full_path) as mock_get_fullname:
            
            # Mock FileService.get_files_with_same_extension on the *instance*
            expected_sibling_files = [test_file_full_path, "/fake/path/other.dat"]
            self.file_service_instance.get_files_with_same_extension = MagicMock(return_value=expected_sibling_files)

            # Mock DataListWindow.update_file_list on the *instance*
            self.main_list_window_instance.update_file_list = MagicMock()
            
            # Mock for the DataController instance that MainController will create
            mock_dc_instance = MagicMock()
            self.MockDataController.return_value = mock_dc_instance

            # --- Act ---
            self.controller.open_file()

            # --- Assert ---
            # Check that get_fullname was called (indirectly, via FileService.open_file)
            mock_get_fullname.assert_called_once()

            # Check that get_files_with_same_extension was called on the FileService instance
            self.file_service_instance.get_files_with_same_extension.assert_called_once_with(test_file_full_path)

            # Check that update_file_list was called on the DataListWindow instance
            self.main_list_window_instance.update_file_list.assert_called_once_with(expected_sibling_files)

            # Check DataController instantiation
            # The first argument to DataController will be a real WholeFilename instance
            self.MockDataController.assert_called_once()
            args, _ = self.MockDataController.call_args
            filename_obj_arg = args[0]
            self.assertIsInstance(filename_obj_arg, WholeFilename)
            self.assertEqual(filename_obj_arg.name, test_file_name)
            self.assertEqual(filename_obj_arg.fullname, test_file_full_path)
            self.assertEqual(args[1], self.controller.gui_backend_name)
            
            # Check controller storage
            self.assertIn(test_file_name, self.controller.data_controller_dict)
            self.assertEqual(self.controller.data_controller_dict[test_file_name], mock_dc_instance)

    def test_open_file_uses_existing_controller_if_present(self):
        """
        Tests if open_file reuses an existing DataController.
        DataController class should not be instantiated again.
        """
        # --- Arrange ---
        test_file_full_path = "/fake/path/existing_file.dat"
        test_file_name = "existing_file.dat"

        # Pre-set an existing DataController mock in data_controller_dict
        existing_dc_mock = MagicMock()
        self.controller.data_controller_dict[test_file_name] = existing_dc_mock
        
        # Reset the class mock for DataController to ensure it's not called
        self.MockDataController.reset_mock()

        with patch('ScanDataPy.controller.controller_filename.FileService.get_fullname', return_value=test_file_full_path) as mock_get_fullname:
            # Mock methods on real instances that would be called
            self.file_service_instance.get_files_with_same_extension = MagicMock(return_value=[test_file_full_path])
            self.main_list_window_instance.update_file_list = MagicMock()
            
            # --- Act ---
            self.controller.open_file()

            # --- Assert ---
            mock_get_fullname.assert_called_once() # File dialog would still be "shown"
            
            # DataController class should NOT have been called to create a new instance
            self.MockDataController.assert_not_called()
            
            # The dictionary should still contain the original existing mock
            self.assertEqual(self.controller.data_controller_dict[test_file_name], existing_dc_mock)
            
            # List window and file service methods for siblings would still be called
            self.file_service_instance.get_files_with_same_extension.assert_called_once_with(test_file_full_path)
            self.main_list_window_instance.update_file_list.assert_called_once_with([test_file_full_path])


    def test_close_file_removes_controller_and_calls_close(self):
        """Tests if close_file removes a DataController and calls its close method."""
        # --- Arrange ---
        test_file_name = "file_to_close.dat"
        # We need a WholeFilename object to pass to close_file
        # For this test, we can create a real one or a mock.
        # Since close_file only uses .name, a mock is simpler.
        mock_filename_obj_for_close = MagicMock(spec=WholeFilename)
        mock_filename_obj_for_close.name = test_file_name
        
        # Mock for the DataController to be closed (this is an instance from self.MockDataController)
        mock_dc_to_close = MagicMock() 
        mock_dc_to_close.close = MagicMock() # Mock the close method

        self.controller.data_controller_dict[test_file_name] = mock_dc_to_close

        # --- Act ---
        self.controller.close_file(mock_filename_obj_for_close) # Pass the mock WholeFilename

        # --- Assert ---
        mock_dc_to_close.close.assert_called_once()
        self.assertNotIn(test_file_name, self.controller.data_controller_dict)

    # Add more tests for:
    # - open_single_file_and_update_list
    # - open_file_from_list
    # - _prepare_data_controller (especially edge cases if it were public, but test through public methods)
    # - Cases where filename_obj is None (e.g., user cancels file dialog)
    #   - In this setup, self.file_service_instance.open_file() would return None
    #     if mock_get_fullname returns None.

if __name__ == '__main__':
    unittest.main()