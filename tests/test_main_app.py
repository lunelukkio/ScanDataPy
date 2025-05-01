# -*- coding: utf-8 -*-
"""
Tests for the Main application controller
"""

import unittest
import sys
from unittest.mock import MagicMock, patch

import pytest
from PyQt6 import QtWidgets

# Import the classes to test
from ScanDataPy.__main__ import Main, MainWindow, create_app
from ScanDataPy.common_class import FileService


class TestMainApp(unittest.TestCase):
    """Test suite for the Main application controller"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mocks
        self.mock_file_service = MagicMock(spec=FileService)
        self.mock_qt_app = MagicMock(spec=QtWidgets.QApplication)
        
        # Configure mocks
        self.mock_filename_obj = MagicMock()
        self.mock_filename_obj.name = "test_file"
        self.mock_filename_obj.fullname = "/path/to/test_file.tsm"
        
        self.mock_file_service.open_file.return_value = self.mock_filename_obj
        self.mock_file_service.get_files_with_same_extension.return_value = [
            "/path/to/test_file.tsm",
            "/path/to/another_file.tsm"
        ]
    
    @patch('ScanDataPy.__main__.QtDataWindow')
    def test_init(self, mock_qt_data_window):
        """Test the initialization of the Main class"""
        # Create an instance with mocked dependencies
        app = Main(file_service=self.mock_file_service, qt_app=self.mock_qt_app)
        
        # Assert that the main window was created and shown
        self.assertIsNotNone(app.main_window)
        self.assertTrue(hasattr(app, 'scandata'))
        
    @patch('ScanDataPy.__main__.QtDataWindow')
    def test_open_file(self, mock_qt_data_window):
        """Test the open_file method"""
        # Set up the mock for QtDataWindow
        mock_window_instance = MagicMock()
        mock_qt_data_window.return_value = mock_window_instance
        
        # Create an instance with mocked dependencies
        app = Main(file_service=self.mock_file_service, qt_app=self.mock_qt_app)
        
        # Override update_file_list to avoid problems in testing
        app.update_file_list = MagicMock()
        
        # Call the method to test
        app.open_file()
        
        # Assert that the correct methods were called
        self.mock_file_service.open_file.assert_called_once()
        self.mock_file_service.get_files_with_same_extension.assert_called_once_with(
            self.mock_filename_obj.fullname
        )
        
        # Assert that the new window was created and methods were called
        mock_qt_data_window.assert_called_once()
        mock_window_instance.open_file.assert_called_once_with(self.mock_filename_obj)
        mock_window_instance.show.assert_called_once()
        
        # Assert that the window was added to the list
        self.assertIn("test_file", app.data_window_list)
        self.assertEqual(app.data_window_list["test_file"], mock_window_instance)

    def test_create_app(self):
        """Test the create_app function"""
        # Patch the Main class to avoid creating real objects
        with patch('ScanDataPy.__main__.Main') as mock_main:
            # Call the function
            create_app()
            
            # Assert that Main was called with no arguments
            mock_main.assert_called_once_with()


if __name__ == "__main__":
    pytest.main(["-v", "test_main_app.py"]) 