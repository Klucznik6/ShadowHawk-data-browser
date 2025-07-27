#!/usr/bin/env python3
"""
Test Database Persistence Functionality
"""

import os
import tempfile
import pandas as pd
from config_manager import ConfigManager

def test_persistence():
    """Test the database persistence functionality"""
    print("🧪 Testing Database Persistence")
    print("=" * 50)
    
    # Create a test CSV file
    test_data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'email': ['alice@test.com', 'bob@test.com', 'charlie@test.com', 'diana@test.com', 'eve@test.com'],
        'score': [95, 87, 92, 78, 88]
    }
    
    df = pd.DataFrame(test_data)
    
    # Create temporary CSV file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    
    print(f"✅ Created test CSV: {temp_file.name}")
    
    try:
        # Test config manager
        config_manager = ConfigManager("test_config.json")
        
        # Test saving database state
        db_info = {
            'path': temp_file.name,
            'type': 'csv',
            'tables': ['test_data'],
            'connection': None  # Would be actual connection in real use
        }
        
        config_manager.save_database_state("test_database.csv", db_info)
        print("✅ Saved database state")
        
        # Test recent files
        config_manager.add_recent_file(temp_file.name)
        recent_files = config_manager.get_recent_files()
        print(f"✅ Recent files: {len(recent_files)} files")
        
        # Test retrieving saved databases
        saved_databases = config_manager.get_saved_databases()
        print(f"✅ Saved databases: {len(saved_databases)} databases")
        
        # Test auto-reconnect setting
        auto_reconnect = config_manager.should_auto_reconnect()
        print(f"✅ Auto-reconnect enabled: {auto_reconnect}")
        
        # Test persistence settings
        save_enabled = config_manager.get_setting('persistence_settings', 'save_loaded_databases', True)
        max_recent = config_manager.get_setting('persistence_settings', 'max_recent_databases', 10)
        
        print(f"✅ Save databases enabled: {save_enabled}")
        print(f"✅ Max recent databases: {max_recent}")
        
        # Display saved configuration
        print("\n📋 Current Configuration:")
        for category, settings in config_manager.config.items():
            if category in ['persistence_settings', 'loaded_databases', 'recent_files']:
                print(f"  {category}:")
                if isinstance(settings, dict):
                    for key, value in settings.items():
                        print(f"    {key}: {value}")
                elif isinstance(settings, list):
                    print(f"    {len(settings)} items")
                print()
        
        print("🎉 Database persistence test completed successfully!")
        
        # Test clearing history
        print("\n🗑️ Testing clear functionality...")
        config_manager.clear_database_history()
        
        saved_after_clear = config_manager.get_saved_databases()
        recent_after_clear = config_manager.get_recent_files()
        
        print(f"✅ Databases after clear: {len(saved_after_clear)}")
        print(f"✅ Recent files after clear: {len(recent_after_clear)}")
        
    finally:
        # Cleanup
        try:
            os.unlink(temp_file.name)
            os.unlink("test_config.json")
            print("✅ Cleanup completed")
        except:
            pass

if __name__ == "__main__":
    test_persistence()
