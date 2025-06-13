# Detailed Code Analysis - ScanDataPy Architecture Issues

## 1. View-Controller Responsibility Violations

### Problem 1: View directly manipulates model state

**File**: `ScanDataPy/view/view.py`
**Lines**: 451-454
```python
def scale(self, button):
    # View directly tells controller to modify model values
    self._main_controller.set_modifier_val("Scale0", selected_text)
    self._main_controller.set_update_flag(ax_name="FluoAxes", flag=True)
    self._main_controller.update_view("FluoAxes")
```

**Issue**: View should only notify controller of user actions, not orchestrate model updates.

### Problem 2: View creates and manages child windows

**File**: `ScanDataPy/view/view.py`
**Lines**: 467-474
```python
if not hasattr(self, 'float_window') or self.float_window is None:
    self.float_window = FloatWindow(self, self._main_controller)
    self._main_controller.add_axes("Trace", "FloatAxes1", self.float_window, self.float_window.plot_widget)
    self.float_window.show()
```

**Issue**: Window management should be handled by a window manager or controller.

### Problem 3: Controller tightly coupled to PyQt widgets

**File**: `ScanDataPy/controller/controller_axes.py`
**Lines**: 355-357
```python
def __init__(self, color):
    self.__rectangle_obj = QtWidgets.QGraphicsRectItem(40, 40, 1, 1)
    self.__rectangle_obj.setPen(pg.mkPen(color=color, width=0.7))
```

**Issue**: Controller should be UI framework agnostic.

## 2. Circular Dependency Details

### Circular Import Chain 1:
```
view.py → imports MainController → has reference to view
         ↓                         ↑
      creates                   stored as
         ↓                         ↑
   MainController  ←──────────────┘
```

**Code Evidence**:
- `view.py:12`: `from ScanDataPy.controller.controller_main import MainController`
- `view.py:23`: `self._main_controller = MainController(self)`
- `controller_main.py:53`: `def __init__(self, view=None):`

### Circular Import Chain 2:
```
Model (DataService) → sets observers → AxesController
         ↑                                    ↓
      accessed by                      has reference to
         ↑                                    ↓
   MainController  ←──────────────────────────┘
```

**Code Evidence**:
- `model.py:173`: `def set_observer(self, modifier_tag, observer):`
- `controller_axes.py:88`: `def set_observer(self, modifier_tag) -> None:`
- `controller_axes.py:89`: `self._model.set_observer(modifier_tag, self)`

## 3. Singleton Pattern Implementation Issues

### Current Non-Singleton Services:

#### DataService
**File**: `ScanDataPy/model/model.py`
**Lines**: 81-82
```python
class DataService(ModelInterface):
    def __init__(self):
```
**Usage**: `controller_main.py:54`
```python
self.__model = DataService()  # New instance each time
```

#### FileService
**File**: `ScanDataPy/common_class.py`
**Lines**: 23-24
```python
class FileService:
    def __init__(self):
```
**Multiple Instances**:
- `controller_main.py:55`: `self.__file_service = FileService()`
- `controller_main.py:384`: `self.__file_service = FileService()`

### Correct Singleton Implementation Example:
```python
class DataService(ModelInterface):
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.__data_repository = Repository()
            self.__modifier_service = ModifierService()
            self._initialized = True
```

## 4. State Management Issues

### Problem: Scattered State Management

**UI State in View**:
```python
# view.py:137-138
self.dif_image_button = QtWidgets.QCheckBox("Differential Image")
self.dif_image_button.setChecked(False)

# view.py:142-143
self.bl_comp_checkbox = QtWidgets.QCheckBox("Baseline Comp")
self.bl_comp_checkbox.setChecked(False)
```

**Application State in Controller**:
```python
# controller_main.py:58
self.current_filename = [0]

# controller_axes.py:25
self.current_mode = 'Normal'
```

**Data State in Model**:
```python
# model.py:215
self._data = []  # Repository data
```

## 5. Event Handling Anti-patterns

### Problem: Business Logic in Event Handlers

**File**: `ScanDataPy/view/view.py`
**Lines**: 511-521
```python
def dif_image_switch(self):
    self._main_controller.set_tag(
        list_name="modifier_list", new_tag="DifImage0", ax_key="ImageAxes"
    )
    if self.dif_image_button.isChecked():
        self._main_controller.change_color(color="plasma", ax_key="ImageAxes")
    else:
        self._main_controller.change_color(color="grey", ax_key="ImageAxes")
    self._main_controller.set_update_flag(ax_name="ImageAxes", flag=True)
    self._main_controller.update_view("ImageAxes")
```

**Better Pattern**:
```python
def dif_image_switch(self):
    # View only notifies controller
    self._main_controller.handle_dif_image_toggle(self.dif_image_button.isChecked())
```

## 6. God Object Examples

### MainController doing too much:

**File Operations**:
```python
# Lines 87-139: open_file method
# Lines 257-259: get_current_file_path
```

**Model Operations**:
```python
# Lines 140-167: create_experiments
# Lines 189-191: create_modifier
```

**View Operations**:
```python
# Lines 339-360: update_view
# Lines 199-201: set_marker
```

**Configuration**:
```python
# Lines 260-335: default_settings (75 lines!)
```

## Recommended Refactoring Priority:

1. **High Priority**: Fix circular dependencies
   - Extract interfaces
   - Use dependency injection
   - Implement event bus

2. **High Priority**: Implement singletons for services
   - DataService
   - FileService
   - ModifierService

3. **Medium Priority**: Separate View and Controller responsibilities
   - Move business logic to controller
   - Create view models/presenters
   - Implement command pattern for user actions

4. **Medium Priority**: Break up MainController
   - FileController
   - ExperimentController
   - ViewCoordinator
   - ConfigurationManager

5. **Low Priority**: Centralize state management
   - Implement state store
   - Use observer pattern for state changes