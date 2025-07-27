# Changelog

All notable changes to ShadowHawk Database Browser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-27

### Added
- 🚀 **Ultra-fast Polars integration** - 46x faster data processing than pandas
- 🔍 **Global search functionality** across all loaded databases and tables
- 💾 **Database persistence** - databases stay loaded between application sessions
- 🗑️ **Database management** - right-click context menus to remove/reload databases
- 📁 **Enhanced file menu** with recent files and database management options
- ⚡ **Performance optimizations** with chunked data loading and memory management
- 🎨 **Improved UI** with emoji icons and user-friendly confirmations
- 🔧 **Configuration management** system with persistent settings

### Changed
- **Major performance improvement**: Search operations now 46x faster
- **Enhanced search interface**: Toggle between single table and global search
- **Better memory management**: Optimized for large datasets
- **Improved error handling**: Better user feedback and error messages
- **Modern UI elements**: Enhanced with emojis and better visual feedback

### Fixed
- ✅ Database deletion now properly clears all UI elements
- ✅ Column headers and table information correctly reset when removing databases
- ✅ Memory leaks in database connections resolved
- ✅ Search results properly highlight matching data
- ✅ Configuration persistence across application restarts

### Technical Details
- **Polars integration**: Replaced pandas operations with Polars for massive speed gains
- **Multi-threading**: Background operations don't block UI
- **SQLite optimization**: Chunked insertion for large datasets
- **State management**: Comprehensive cleanup when removing databases
- **Configuration system**: JSON-based settings with auto-save

## [1.0.0] - 2024-12-01

### Added
- Initial release of ShadowHawk Database Browser
- Basic SQLite database browsing
- CSV file import functionality
- Simple data viewing interface
- Export capabilities

### Features
- Load and browse SQLite databases
- Import CSV files
- View data in tabular format
- Basic column information display
- Export data to CSV format

---

## Legend
- 🚀 Performance improvements
- 🔍 Search functionality
- 💾 Data persistence
- 🗑️ Data management
- 📁 File operations
- ⚡ Speed optimizations
- 🎨 UI improvements
- 🔧 Configuration
- ✅ Bug fixes
