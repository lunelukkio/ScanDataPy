try:
    import PyQt6
    print(f"PyQt6 is installed at: {PyQt6.__file__}")
    print(f"Qt6 library directory: {PyQt6.__path__}")
except ImportError as e:
    print(f"Failed to import PyQt6: {e}")