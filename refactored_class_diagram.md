# Refactored ScanDataPy Class Diagram

## Overview
This document describes the class structure of the refactored ScanDataPy project, which now uses an event-driven architecture to eliminate circular dependencies.

## Class Diagram

```mermaid
classDiagram
    %% Controller Layer
    class MainController {
        -gui_backend: str
        -app: QtWidgets.QApplication
        -list_window: ListView
        -data_controllers: List~DataController~
        +__init__(gui_backend='pyqt6')
        -_initialize_app()
        -_create_data_window(filename_obj)
        -_cleanup_controller(controller)
        +create_app(gui_backend='pyqt6')$
    }

    class DataController {
        <<QObject>>
        -_gui_backend_name: str
        -filename_obj: WholeFilename
        -current_filename: List~int~
        -_model: DataService
        -_file_service: FileService
        -_key_manager: KeyManager
        -_ax_dict: Dict~str, AxesController~
        -view_event_bus: ViewEventBus
        -controller_event_bus: ControllerEventBus
        -_axes_initialized: bool
        +initialize_axes(axes_config)
        +get_filename()
        -_handle_file_open(filename_obj)
        -_handle_roi_size_change(command)
        -_handle_roi_click(axes_name, position)
        -_handle_modifier_value_change(modifier_name, value)
        -_handle_scale_mode_change(mode)
        +create_experiments(filename_obj)
        +create_default_modifier(filename_number)
        +create_modifier(modifier_name)
        +set_observer(ax_name, modifier_tag)
        +default_settings(filename_key)
    }

    class AxesController {
        <<abstract>>
        #_canvas
        #_ax_obj
        #_main_controller
        #_model
        #_key_manager: KeyManager
        #current_mode: str
        #ax_item_dict: Dict
        #_marker_obj_dict: Dict
        #update_flag: bool
        #update_flag_lock: bool
        #_ch_colors: Dict
        #_controller_colors: Dict
        +update()*
        +get_view_data()*
        +set_tag(list_name, key)
        +set_observer(modifier_tag)
    }

    class ImageAxesController {
        -line_color_mode: str
        -color_mode: str
        +get_view_data()
        +update()
        +set_marker(roi_tag)
        +change_color(color)
    }

    class TraceAxesController {
        -line_color_mode: str
        +get_view_data()
        +update()
        +change_current_ax_mode(bl_control_mode)
        +get_bl_obj(data_type)
        +change_roi_size(val)
        +onclick_axes(val)
    }

    %% View Layer
    class QtDataWindow {
        <<QMainWindow>>
        -view_event_bus: ViewEventBus
        -controller_event_bus: ControllerEventBus
        -settings: Dict
        -axes_widgets: Dict
        -current_scale_mode: str
        -float_window: FloatWindow
        -image_ax: CustomImageView
        -trace_ax1: pg.PlotWidget
        -trace_ax2: pg.PlotWidget
        -_connect_controller_events()
        -_load_settings()
        -_setup_ui()
        -_setup_controls(main_layout)
        +get_axes_config()
        -_on_data_loaded(filename, data_info)
        -_on_axes_updated(axes_name, data)
        -_on_roi_marker_updated(axes_name, roi_tag, position)
    }

    class ListView {
        <<QMainWindow>>
        +open_data_window_requested: Signal
    }

    class QtDataWindowFactory {
        +create_data_window(parent, view_event_bus, controller_event_bus)$
    }

    %% Event System
    class ViewEventBus {
        <<QObject>>
        +file_open_requested: Signal
        +roi_size_change_requested: Signal
        +roi_clicked: Signal
        +bl_roi_mode_changed: Signal
        +bl_use_roi1_changed: Signal
        +modifier_value_change_requested: Signal
        +scale_mode_changed: Signal
        +bl_comp_toggled: Signal
        +dif_image_toggled: Signal
        +invert_toggled: Signal
        +fluo_channel_changed: Signal
        +elec_channel_changed: Signal
        +time_window_change_requested: Signal
        +view_update_requested: Signal
        +marker_update_requested: Signal
        +axes_sync_requested: Signal
    }

    class ControllerEventBus {
        <<QObject>>
        +data_loaded: Signal
        +axes_data_updated: Signal
        +roi_marker_updated: Signal
        +modifier_state_changed: Signal
        +float_window_requested: Signal
        +status_message: Signal
        +error_occurred: Signal
    }

    class ViewEvent {
        <<dataclass>>
        +event_type: str
        +data: Dict~str, Any~
    }

    %% Model Layer
    class DataService {
        <<ModelInterface>>
        -__data_repository: Repository
        -__modifier_service: ModifierService
        +create_experiments(fullname)
        +add_modifier(modifier_name)
        +remove_modifier(modifier_name)
        +set_modifier_val(modifier_name, args, kwargs)
        +get_data(data_tag, modifier_list_list)
        +set_observer(controller_key, observer)
        +reset()
    }

    class FileService {
        -filename_obj: WholeFilename
        -gui_app: str
        +open_file(filename)
        +get_fullname_pyqt6()
        +get_fullname_matplotlib()
        +get_files_with_same_extension(file_path, extension)
        +reset()
    }

    class WholeFilename {
        -path: Path
        +fullname: str
        +name: str
        +dir: str
        +stem: str
        +extension: str
        +print_infor()
    }

    class KeyManager {
        -filename_list: List
        -attribute_list: List
        -data_type_list: List
        -origin_list: List
        -modifier_list: List
        -ch_list: List
        -roi_list: List
        -bl_roi_list: List
        +set_tag(tag_list_name, tag)
        +replace_tag(list_name, old_tag, new_tag)
        +get_list(list_name)
        +get_dicts_from_tag_list()
        +print_infor()
        +reset()
    }

    %% Relationships
    MainController "1" --> "*" DataController : creates/manages
    MainController "1" --> "1" ListView : creates
    
    DataController "1" --> "1" DataService : uses
    DataController "1" --> "1" FileService : uses
    DataController "1" --> "1" KeyManager : owns
    DataController "1" --> "*" AxesController : creates/manages
    DataController "1" --> "1" ViewEventBus : subscribes to
    DataController "1" --> "1" ControllerEventBus : publishes to
    
    AxesController <|-- ImageAxesController : inherits
    AxesController <|-- TraceAxesController : inherits
    AxesController "*" --> "1" KeyManager : uses
    
    QtDataWindow "1" --> "1" ViewEventBus : publishes to
    QtDataWindow "1" --> "1" ControllerEventBus : subscribes to
    
    QtDataWindowFactory ..> QtDataWindow : creates
    QtDataWindowFactory ..> ViewEventBus : creates
    QtDataWindowFactory ..> ControllerEventBus : creates
    
    MainController ..> QtDataWindowFactory : uses
    
    ViewEventBus ..> ViewEvent : emits
    ControllerEventBus ..> ViewEvent : emits
```

## Key Architecture Features

### 1. Event-Driven Communication
- **ViewEventBus**: Handles all View → Controller communication
- **ControllerEventBus**: Handles all Controller → View communication
- No direct references between View and Controller layers

### 2. Dependency Flow
```
MainController
    ├── DataController
    │   ├── Model (DataService)
    │   ├── AxesControllers
    │   │   ├── ImageAxesController
    │   │   └── TraceAxesController
    │   ├── ViewEventBus (subscription)
    │   └── ControllerEventBus (publication)
    │
    └── QtDataWindow
        ├── UI Components
        ├── ViewEventBus (publication)
        └── ControllerEventBus (subscription)
```

### 3. Design Patterns Used
- **MVC Pattern**: Clear separation of Model, View, and Controller
- **Observer Pattern**: Event-based communication between layers
- **Factory Pattern**: QtDataWindowFactory for window creation
- **Composition**: Controllers manage sub-controllers and services

### 4. Benefits of Refactored Architecture
- **No Circular Dependencies**: Event buses prevent direct coupling
- **Testability**: Each component can be tested in isolation
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Easy to add new views or controllers
- **Type Safety**: Uses type hints throughout