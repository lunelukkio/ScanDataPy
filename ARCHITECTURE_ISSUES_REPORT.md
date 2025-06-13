# ScanDataPy Architecture Issues Report

## 1. View and Controller Responsibilities Mixed

### Issue 1.1: View contains business logic and direct model manipulation
**Location: `ScanDataPy/view/view.py`**

- **Lines 377-389**: The `open_file()` method in the View creates model data and handles file operations
  ```python
  def open_file(self, filename_obj=None):
      filename_obj, same_ext_file_list = self._main_controller.open_file(filename_obj)
      self._main_controller.create_default_modifier(0)
      self._main_controller.default_settings(filename_obj.name)
      self._main_controller.print_infor()
      self._main_controller.update_view()
      self._main_controller.set_marker(ax_key="ImageAxes", roi_tag="Roi1")
      self.default()
  ```
  **Problem**: View should not orchestrate complex business operations

- **Lines 391-398**: The `default()` method sets application state
  ```python
  def default(self):
      self.bl_use_roi1.setChecked(True)
      self.bl_use_roi1_switch()
      self.dFoverF_trace.setChecked(True)
      self.scale(self.dFoverF_trace)
  ```
  **Problem**: Default configurations should be managed by the controller or a configuration service

- **Lines 456-488**: The `bl_comp()` method manages complex window creation and data flow
  ```python
  def bl_comp(self, state):
      if self.bl_comp_checkbox.isChecked():
          self._main_controller.set_tag(...)
          self._main_controller.set_modifier_val("BlComp0", "Exponential")
          if not hasattr(self, 'float_window') or self.float_window is None:
              self.float_window = FloatWindow(self, self._main_controller)
              self._main_controller.add_axes(...)
  ```
  **Problem**: View creates child windows and manages their lifecycle

### Issue 1.2: Controller tightly coupled to View
**Location: `ScanDataPy/controller/controller_main.py`**

- **Line 23**: Controller is initialized with view reference
  ```python
  self._main_controller = MainController(self)
  ```
  **Problem**: Creates circular dependency between View and Controller

## 2. Circular Import Issues

### Issue 2.1: View imports Controller, Controller references View
- **View imports Controller**: `ScanDataPy/view/view.py:12`
  ```python
  from ScanDataPy.controller.controller_main import MainController
  ```
- **Controller accepts View**: `ScanDataPy/controller/controller_main.py:53`
  ```python
  def __init__(self, view=None):
  ```

### Issue 2.2: Tight coupling between Model and Controller layers
- **Controller imports Model**: `ScanDataPy/controller/controller_main.py:11`
  ```python
  from ScanDataPy.model.model import DataService
  ```
- **Model sets observers from Controller**: `ScanDataPy/model/model.py:173-183`
  ```python
  def set_observer(self, modifier_tag, observer):
      # observer is typically an AxesController instance
  ```

## 3. Singleton Pattern Issues

### Issue 3.1: Services that should be singletons but aren't

#### DataService (Model)
**Location: `ScanDataPy/model/model.py:81-206`**
- Multiple instances can be created
- Each MainController creates its own DataService instance
- No shared state between instances

#### FileService
**Location: `ScanDataPy/common_class.py:23-157`**
- Multiple instances created in different controllers
- No centralized file management
- State not shared across application

#### ModifierService
**Location: `ScanDataPy/model/modifier.py:45-56`**
- Created inside DataService
- Should be a singleton to maintain consistent modifier chain

### Issue 3.2: Multiple KeyManager instances
**Location: `ScanDataPy/common_class.py:239-320`**
- Created in MainController: Line 56
- Created in each AxesController: `controller_axes.py:24`
- No synchronization between instances

## 4. Additional Architecture Issues

### Issue 4.1: God Object Anti-pattern
**MainController** (`controller_main.py`) has too many responsibilities:
- File management (lines 87-139)
- Experiment creation (lines 140-167)
- Modifier management (lines 170-191)
- View updates (lines 339-360)
- Default settings (lines 260-335)

### Issue 4.2: Inconsistent State Management
- View manages UI state directly through checkboxes and buttons
- Controller manages application state
- Model manages data state
- No clear separation of concerns

### Issue 4.3: Event Handling Mixed with Business Logic
**Location: `ScanDataPy/view/view.py`**
- Button click handlers contain business logic
- Example: `roi_size()` (lines 399-407), `bl_comp()` (lines 456-488)

## Recommendations

1. **Implement Proper MVC/MVP Pattern**
   - Move all business logic from View to Controller
   - Use View only for UI rendering and event delegation
   - Implement a Presenter or ViewModel layer

2. **Fix Circular Dependencies**
   - Use dependency injection
   - Implement interfaces/protocols
   - Use event bus or observer pattern for communication

3. **Implement Singleton Pattern Correctly**
   ```python
   class DataService:
       _instance = None
       
       def __new__(cls):
           if cls._instance is None:
               cls._instance = super().__new__(cls)
           return cls._instance
   ```

4. **Refactor MainController**
   - Split into smaller, focused controllers
   - Extract file operations to FileService
   - Extract modifier operations to ModifierController

5. **Implement Proper State Management**
   - Create a centralized state manager
   - Use immutable state updates
   - Implement state change notifications