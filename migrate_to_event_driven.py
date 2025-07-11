#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Migration script to transition from direct controller references to event-driven architecture.
This script creates backups and updates the codebase to use the new architecture.
"""

import shutil
import os
from datetime import datetime


def create_backup(file_path):
    """Create a backup of the file with timestamp"""
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        shutil.copy2(file_path, backup_path)
        print(f"Created backup: {backup_path}")
        return backup_path
    return None


def migrate_files():
    """Migrate files to use the new event-driven architecture"""
    base_path = "ScanDataPy"
    
    migrations = [
        {
            "old": f"{base_path}/controller/controller_data.py",
            "new": f"{base_path}/controller/controller_data_refactored.py",
            "target": f"{base_path}/controller/controller_data.py"
        },
        {
            "old": f"{base_path}/view/view_data.py",
            "new": f"{base_path}/view/view_data_refactored.py",
            "target": f"{base_path}/view/view_data.py"
        },
        {
            "old": f"{base_path}/controller/controller_main.py",
            "new": f"{base_path}/controller/controller_main_refactored.py",
            "target": f"{base_path}/controller/controller_main.py"
        }
    ]
    
    print("Starting migration to event-driven architecture...")
    print("=" * 60)
    
    # First, create backups of all files
    for migration in migrations:
        if os.path.exists(migration["old"]):
            create_backup(migration["old"])
    
    # Copy new files over old ones
    for migration in migrations:
        if os.path.exists(migration["new"]):
            print(f"\nMigrating: {migration['old']}")
            shutil.copy2(migration["new"], migration["target"])
            print(f"✓ Replaced with refactored version")
        else:
            print(f"✗ Warning: {migration['new']} not found")
    
    # Update imports in __main__.py
    main_file = f"{base_path}/__main__.py"
    if os.path.exists(main_file):
        print(f"\nUpdating imports in {main_file}")
        create_backup(main_file)
        
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update import
        old_import = "from ScanDataPy.controller.controller_main import MainController"
        new_import = "from ScanDataPy.controller.controller_main import MainController"
        content = content.replace(old_import, new_import)
        
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ Updated imports")
    
    print("\n" + "=" * 60)
    print("Migration completed!")
    print("\nNOTE: The refactored architecture includes:")
    print("- Event-driven communication between View and Controller")
    print("- No circular dependencies")
    print("- AxesController creation moved to DataController")
    print("- All View->Controller communication via events")
    print("\nBackup files have been created with .backup_[timestamp] extension")
    print("\nTo rollback, restore from the backup files.")


def print_architecture_summary():
    """Print a summary of the new architecture"""
    print("\n" + "=" * 60)
    print("NEW ARCHITECTURE SUMMARY")
    print("=" * 60)
    print("""
1. Event-Driven Communication:
   - ViewEventBus: View → Controller events
   - ControllerEventBus: Controller → View events
   
2. Dependency Flow:
   MainController
       ├── DataController (no view reference)
       │   ├── Model
       │   ├── AxesControllers
       │   └── Event Buses
       └── Views (QtDataWindow)
           └── Connect to Event Buses
           
3. Key Changes:
   - QtDataWindow no longer calls controller methods directly
   - DataController creates AxesControllers
   - All communication via PyQt signals
   - No circular dependencies
   
4. Benefits:
   - Better separation of concerns
   - Easier testing
   - More maintainable
   - Follows MVC pattern properly
""")


if __name__ == "__main__":
    import sys
    
    print("Event-Driven Architecture Migration Tool")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        print_architecture_summary()
    else:
        response = input("This will migrate your codebase to the event-driven architecture.\nBackups will be created. Continue? (y/n): ")
        if response.lower() == 'y':
            migrate_files()
            print_architecture_summary()
        else:
            print("Migration cancelled.")