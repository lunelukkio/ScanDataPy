from PyQt6 import QtWidgets, QtCore
import os

class DataListWindow(QtWidgets.QMainWindow):
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

        # Create load single file button
        load_single_btn = QtWidgets.QPushButton("Load Single")
        load_single_btn.setFixedSize(100, 30)
        load_single_btn.clicked.connect(self.load_single_file)
        
        # Create History button
        history_btn = QtWidgets.QPushButton("History")
        history_btn.setFixedSize(100, 30)
        history_btn.clicked.connect(self.handle_history_button_clicked) # Connect to a new handler

        # Horizontal layout for buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(load_btn)
        button_layout.addWidget(load_single_btn)
        button_layout.addWidget(history_btn) # Add the history button to the layout
        button_layout.addStretch() # Add stretch to push buttons to the left

        layout.addLayout(button_layout) # Add button layout to the main vertical layout

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

    def load_single_file(self):
        """Calls the controller method to open a single file and update the list with only that file."""
        self.scandata_controller.open_single_file_and_update_list()

    def handle_history_button_clicked(self):
        """Handles the event when the History button is clicked."""
        # This will call a method on the main controller, which should handle
        # the logic for displaying or interacting with the file history.
        # For example, it might open a new dialog with recent files.
        if hasattr(self.scandata_controller, 'display_file_history'):
            self.scandata_controller.display_file_history()
        else:
            print("[DataListWindow:INFO] MainController does not have a 'display_file_history' method.")
            QtWidgets.QMessageBox.information(self, "History", "History feature is under development in the controller.")

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