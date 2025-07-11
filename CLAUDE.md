# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ScanDataPy is a scientific data analysis and visualization application built with PyQt6. It follows an MVC architecture pattern and is designed for analyzing scanning/imaging data with real-time visualization capabilities and machine learning integration.

## Running the Application

```bash
# Run the main application
python -m ScanDataPy

# Or directly
python ScanDataPy/__main__.py
```

## Development Commands

### Testing
```bash
# Run all tests using unittest (main test runner)
python tests/test_main.py

# Run specific test categories:
# - Model tests: modify test_main.py to use pattern "test0*.py"
# - View tests: modify test_main.py to use pattern "test1*.py"  
# - Controller tests: modify test_main.py to use pattern "test2*.py"

# Run with pytest (if installed in virtual environment)
python -m pytest tests/
```

### Linting
```bash
# Run ruff linter
ruff check .
ruff check --fix .  # Auto-fix issues
```

### Virtual Environment
```bash
# Activate virtual environment (Windows)
Scripts\activate.bat

# Activate virtual environment (Unix/MacOS)
source Scripts/activate
```

### Package Management
```bash
# Install dependencies using uv (recommended)
uv pip install -r requirements.txt

# Install specific packages
uv pip install package_name
```

## Architecture Overview

The application follows a Model-View-Controller (MVC) pattern:

### Controllers (`ScanDataPy/controller/`)
- `controller_main.py`: Main application controller and entry point
- `controller_data.py`: Handles data operations and processing
- `controller_axes.py`: Manages axis-related functionality
- `controller_filename.py`: File handling and naming logic
- `controller_key_manager.py`: Keyboard shortcuts and key event handling
- `controller_live_view.py`: Real-time data visualization controller

### Models (`ScanDataPy/model/`)
- `model.py`: Core data models and structures
- `file_io.py`: File input/output operations (supports .tif, .dat, .da, .tbn, .tsm formats)
- `builder.py`: Factory pattern implementations for object creation
- `modifier.py`: Data transformation and modification logic
- `value_object.py`: Immutable value objects
- `analyze/`: Analysis module for data processing

### Views (`ScanDataPy/view/`)
- `view_data.py`: Data visualization window
- `view_list.py`: List/table views for data display

### Configuration
- `scandata_setting.json`: Application-wide settings (color schemes for channels and ROIs)
- `ScanDataPy/setting/data_window_setting.json`: Data window specific settings
- `ScanDataPy/setting/file_setting.json`: File handling settings

## Key Dependencies

- **GUI Framework**: PyQt6, pyqtgraph
- **Scientific Computing**: numpy, pandas, scipy, matplotlib
- **Machine Learning**: torch (PyTorch)
- **Testing**: pytest, unittest
- **Linting**: ruff

## Development Guidelines

Follow the principles defined in `.cursor/rules/my-custom-rule.mdc`:

1. **Code Style**: Follow PEP 8, use functional programming patterns where appropriate
2. **Performance**: Prefer vectorized operations over loops, optimize memory usage
3. **Error Handling**: Validate inputs, provide informative error messages
4. **Testing**: Write unit tests for new functionality
5. **Documentation**: Include docstrings following PEP 257 conventions

## File Format Support

The application supports various scientific data formats:
- Image formats: .tif
- Data formats: .dat, .da, .tbn, .tsm

## Docker Development

For containerized development:
```bash
# Build image
docker build -t scandata-py Docker/

# Run with GUI support (see Docker/docker-README.md for X11 setup)
docker run --name scandata-container -it -e DISPLAY=:0.0 -v /tmp/.X11-unix:/tmp/.X11-unix scandata-py

# Mount local directory for development
docker run --name scandata -v $(pwd):/app -it scandata-py
```