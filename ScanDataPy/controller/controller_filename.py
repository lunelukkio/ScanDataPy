import sys
import os
from pathlib import Path

from PyQt6 import QtWidgets

class FileService:
    def __init__(self, gui_app: str | None = None):
        self.filename_obj = None
        self.gui_app = gui_app
        assert self.gui_app in ['pyqt6', 'matplotlib'], f"Invalid GUI backend: {self.gui_app}. Must be 'pyqt6' or 'matplotlib'."

    def open_file(self, filename=None):
        if filename is None:
            if self.gui_app == 'pyqt6':
                fullname = self.get_fullname_pyqt6() # This static method uses PyQt6
                if not fullname:
                    print("[FileService] No filename selected or operation cancelled via PyQt6 dialog.")
                    return None
            elif self.gui_app == 'matplotlib':
                fullname = self.get_fullname_matplotlib() # This static method uses Matplotlib
                if not fullname:
                    print("[FileService] No filename selected or operation cancelled via Matplotlib dialog.")
                    return None
            else:
                print(f"[FileService:ERROR] File dialog not supported for gui_app: {self.gui_app}. Provide a filename directly.")
                # Or raise an error, or return None, depending on desired behavior
                # For now, let's make it clear that a filename must be provided if no supported GUI
                raise ValueError(f"File dialog not supported for gui_app: {self.gui_app}. A filename must be provided.")
        else:
            fullname = filename

        if not os.path.exists(fullname):
            print(f"[FileService:ERROR] File does not exist: {fullname}")
            return None
        if not os.path.isfile(fullname):
            print(f"[FileService:ERROR] Path is not a file: {fullname}")
            return None
        
        self.filename_obj = WholeFilename(fullname)
        return self.filename_obj

    def get_fullname_pyqt6(self) -> str | None:
        app = QtWidgets.QApplication.instance()
        if app is None:
            # This might be problematic if no QApplication is intended to be running
            # when this static method is called. Consider if this method truly needs to be static
            # or if it should be tied to an instance that has access to a QApplication.
            print("[FileService:get_fullname] Creating new QApplication instance. This might be unintended.")
            app = QtWidgets.QApplication(sys.argv) 
        
        # Determine current working directory or a sensible default for the dialog
        # Path.cwd() is generally a good default.
        start_dir = str(Path.cwd())

        fullname, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 
            "Open File", 
            start_dir,
            "Data files (*.tsm *.da *.abf *.wcp);;All files (*.*);;"
        )
        if fullname:
            return fullname
        else:
            # User cancelled the dialog
            return None

    def get_fullname_matplotlib(self) -> str | None:
        print("[FileService:ERROR] Matplotlib file dialog is under construction.")
        raise NotImplementedError('Matplotlib file dialog is under construction.')

    def get_files_with_same_extension(self, file_path: str, extension: str = None) -> list[str]:
        """
        Finds all files in the same directory as the given file_path
        that share the same extension.

        If no extension is explicitly provided, the extension of the file_path
        is used. If the file_path itself has no extension and no explicit
        extension is given, all files in the directory are listed.

        Args:
            file_path: The absolute or relative path to a file.
                       The directory of this file will be scanned.
            extension: Optional. The specific file extension to look for (e.g., ".txt" or "txt").
                       If None, the extension of file_path is used.

        Returns:
            A list of strings, where each string is the full path to a found file.
            Returns an empty list if the directory or file_path is invalid,
            or if no matching files are found.

        Note:
            This method currently does not use any instance attributes ('self')
            and could potentially be a static method if it doesn't rely on
            FileService instance state in the future.
            Consider error handling for cases where file_path does not exist
            or is not a file (added basic check).
        """
        path = Path(file_path)
        if not path.exists():
            print(f"[FileService:ERROR] get_files_with_same_extension: file_path does not exist: {file_path}")
            return []
        if not path.is_file():
            # If path is a directory, this would list its contents based on extension,
            # but the method name implies starting from a file. Clarify desired behavior if path is dir.
            print(f"[FileService:WARNING] get_files_with_same_extension: file_path is not a file (it might be a directory or something else): {file_path}. Attempting to use its parent directory anyway if it's a directory, otherwise this might fail or produce unexpected results.")
            # If it's a directory, use it directly. Otherwise, use its parent.
            # This part can be made more robust based on expected inputs.
            directory_to_scan = path if path.is_dir() else path.parent
        else:
            directory_to_scan = path.parent

        # Determine the effective extension to search for
        effective_extension = extension if extension is not None else path.suffix

        # Ensure the extension for globbing starts with a '.', or handle no extension case
        if effective_extension:
            if not effective_extension.startswith('.'):
                glob_pattern = f"*.{effective_extension}"
            else:
                glob_pattern = f"*{effective_extension}"
        else: # No extension (original file has no suffix and no extension arg provided)
            glob_pattern = "*" # List all files
        
        try:
            files = [str(f) for f in directory_to_scan.glob(glob_pattern) if f.is_file()]
        except Exception as e:
            print(f"[FileService:ERROR] Error during glob operation in {directory_to_scan} with pattern {glob_pattern}: {e}")
            return []
        return files

    def reset(self):
        self.filename_obj = None

    def rename_files(self):
        # This method is mentioned in the original file but not implemented in the new version
        # If you need to implement this method, you can add the implementation here
        pass


class WholeFilename:
    def __init__(self, fullname: str):
        self.path = Path(fullname).resolve()
        if not self.path.exists():
            print(f"[WholeFilename:WARNING] File does not exist at path: {fullname}. Proceeding, but operations may fail.")
        elif not self.path.is_file():
            print(f"[WholeFilename:WARNING] Path is not a file: {fullname}. Proceeding, but operations may fail.")

    @property
    def fullname(self) -> str:
        return str(self.path)

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def dir(self) -> str:
        return str(self.path.parent)

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def extension(self) -> str:
        return self.path.suffix

    def print_infor(self) -> None:
        print(f"--- File Information for: {self.name} ---")
        print(f"Absolute Path: {self.path.absolute()}")
        print(f"Full Name: {self.fullname}")
        print(f"Directory: {self.dir}")
        print(f"Stem (name without ext): {self.stem}")
        print(f"Extension: {self.extension}")
        print("--- End of Information ---")


class FileHistoryManager:
    def __init__(self, max_history=10):
        self.history = []
        self.current_file = None
        self.max_history = max_history

    def add_file(self, file_obj: WholeFilename):
        self.current_file = file_obj
        # Remove if already in history
        self.history = [f for f in self.history if f.fullname != file_obj.fullname]
        self.history.insert(0, file_obj)
        # Keep only the latest N
        self.history = self.history[:self.max_history]

    def get_recent_files(self):
        return self.history

    def get_current_file(self):
        return self.current_file

    def clear_history(self):
        self.history = []
        self.current_file = None
