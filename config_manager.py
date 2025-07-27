import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading

class ConfigManager:
    """Manages application configuration and database persistence"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = {}
        self._lock = threading.Lock()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = self._get_default_config()
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self._get_default_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with self._lock:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "app_settings": {
                "theme": "arc",
                "max_display_rows": 10000,
                "chunk_size": 1000,
                "auto_optimize_datatypes": True,
                "show_progress_bar": True,
                "default_export_format": "csv"
            },
            "ui_settings": {
                "window_width": 1400,
                "window_height": 900,
                "font_family": "Segoe UI",
                "font_size": 9,
                "tree_row_height": 25
            },
            "performance_settings": {
                "use_threading": True,
                "cache_enabled": True,
                "lazy_loading": True,
                "memory_threshold_mb": 500
            },
            "persistence_settings": {
                "save_loaded_databases": True,
                "auto_reconnect_on_startup": True,
                "max_recent_databases": 10,
                "remember_database_state": True
            },
            "recent_files": [],
            "database_connections": {},
            "loaded_databases": {}
        }
    
    def get_setting(self, category: str, key: str, default=None):
        """Get a specific setting value"""
        return self.config.get(category, {}).get(key, default)
    
    def set_setting(self, category: str, key: str, value: Any):
        """Set a specific setting value"""
        if category not in self.config:
            self.config[category] = {}
        self.config[category][key] = value
        self.save_config()
    
    def add_recent_file(self, filepath: str):
        """Add file to recent files list"""
        recent_files = self.config.get('recent_files', [])
        
        # Remove if already exists
        if filepath in recent_files:
            recent_files.remove(filepath)
        
        # Add to beginning
        recent_files.insert(0, filepath)
        
        # Limit to max recent files
        max_recent = self.get_setting('persistence_settings', 'max_recent_databases', 10)
        recent_files = recent_files[:max_recent]
        
        self.config['recent_files'] = recent_files
        self.save_config()
    
    def get_recent_files(self) -> List[str]:
        """Get list of recent files"""
        return self.config.get('recent_files', [])
    
    def save_database_state(self, db_name: str, db_info: Dict[str, Any]):
        """Save database state for persistence"""
        if not self.get_setting('persistence_settings', 'save_loaded_databases', True):
            return
        
        # Only save file-based databases that can be reopened
        if 'path' in db_info and os.path.exists(db_info['path']):
            db_state = {
                'path': db_info['path'],
                'type': db_info.get('type', 'unknown'),
                'tables': db_info.get('tables', []),
                'last_accessed': datetime.now().isoformat(),
                'display_name': db_name
            }
            
            loaded_databases = self.config.get('loaded_databases', {})
            loaded_databases[db_name] = db_state
            self.config['loaded_databases'] = loaded_databases
            
            # Also add to recent files
            self.add_recent_file(db_info['path'])
            
            self.save_config()
    
    def remove_database_state(self, db_name: str):
        """Remove database from saved state"""
        loaded_databases = self.config.get('loaded_databases', {})
        if db_name in loaded_databases:
            del loaded_databases[db_name]
            self.config['loaded_databases'] = loaded_databases
            self.save_config()
    
    def get_saved_databases(self) -> Dict[str, Dict[str, Any]]:
        """Get saved database states"""
        saved_databases = {}
        loaded_databases = self.config.get('loaded_databases', {})
        
        # Filter out databases whose files no longer exist
        for db_name, db_state in loaded_databases.items():
            if 'path' in db_state and os.path.exists(db_state['path']):
                saved_databases[db_name] = db_state
        
        # Clean up config if some files were removed
        if len(saved_databases) != len(loaded_databases):
            self.config['loaded_databases'] = saved_databases
            self.save_config()
        
        return saved_databases
    
    def should_auto_reconnect(self) -> bool:
        """Check if auto-reconnect is enabled"""
        return self.get_setting('persistence_settings', 'auto_reconnect_on_startup', True)
    
    def clear_database_history(self):
        """Clear all saved database history"""
        self.config['loaded_databases'] = {}
        self.config['recent_files'] = []
        self.save_config()
    
    def export_config(self, filepath: str):
        """Export configuration to a file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False
    
    def import_config(self, filepath: str):
        """Import configuration from a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Merge with current config
            for category, settings in imported_config.items():
                if category in self.config and isinstance(settings, dict):
                    self.config[category].update(settings)
                else:
                    self.config[category] = settings
            
            self.save_config()
            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False
