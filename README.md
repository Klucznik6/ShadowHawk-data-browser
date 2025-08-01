# 🦅 ShadowHawk Database Browser v3.0

A powerful, modern database browser and data analysis tool built with Python. Features ultra-fast Polars integration, CustomTkinter modern UI, and comprehensive database management capabilities.

![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Version](https://img.shields.io/badge/Version-3.0-brightgreen)

## ✨ Key Features

### 🚀 **Ultra-Fast Performance**
- **5-30x faster** data processing with Polars integration
- Multi-threaded operations for responsive UI
- Smart caching system for instant data access
- Memory-efficient processing of large datasets

### 🎨 **Modern User Interface**
- **CustomTkinter** modern GUI framework
- Professional dark/light theme support
- Intuitive tabbed interface design
- Responsive layout with proper widget isolation

### 🔍 **Advanced Search & Analysis**
- **Global search** across all loaded databases
- Ultra-fast parallel search with real-time results
- Interactive search results with click-to-navigate
- Comprehensive data statistics and column analysis

### 💾 **Comprehensive File Support**
- **SQLite** databases (.db, .sqlite, .sqlite3)
- **CSV** files with intelligent auto-detection
- **Excel** files (.xlsx, .xls) with multiple sheets
- **JSON** data files with nested structure support
- **Access** databases (.mdb, .accdb) via ODBC

### 🗃️ **Smart Database Management**
- **Persistent sessions** - remembers all databases between app restarts
- **Recent files menu** with quick access to previously opened files
- **Database deletion** with UI controls and confirmation dialogs
- **Automatic restoration** of last working session
- **Configuration persistence** with user preferences

### 📊 **Professional Data Tools**
- **SQL Query Interface** - execute custom queries
- **Export capabilities** - CSV, Excel, filtered data
- **Column statistics** - detailed analysis with min/max/mean/median
- **Font size controls** - increase/decrease for better readability
- **Keyboard shortcuts** - full shortcut support for power users

## � Quick Start

### 1. Prerequisites
- **Python 3.8+** (3.13+ recommended)
- **Windows/macOS/Linux** support

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Klucznik6/ShadowHawk-data-browser.git
cd ShadowHawk-data-browser

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application
```bash
# Start ShadowHawk Database Browser
python main.py
```

## 💡 Usage Guide

### 📂 **Opening Databases**
1. **File Menu** → Open Database (`Ctrl+O`)
2. **Import Menu** → CSV/Excel/JSON files
3. **Recent Files** → Quick access to previous databases
4. **Drag & Drop** support (where available)

### 🔍 **Searching Data**
- **Local Search**: Search within current table
- **Global Search**: Click "🌐 Search All DBs" for cross-database search
- **Real-time Results**: Search as you type
- **Navigate Results**: Double-click search results to jump to data

### 📊 **Data Analysis**
- **Column Statistics**: View → Column Statistics
- **Data Statistics**: Tools → Data Statistics  
- **SQL Queries**: Tools → SQL Query for custom analysis
- **Export Options**: File → Export (CSV/Excel/Filtered)

### ⚙️ **Database Management**
- **Persistent Sessions**: All databases automatically saved
- **Remove Databases**: Click red ❌ button next to database names
- **Recent Files**: File → Recent Files menu
- **State Management**: File → Save/Restore Database State

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open Database |
| `Ctrl+F` | Find/Search |
| `Ctrl+C` | Copy Selected |
| `F5` | Refresh Table |
| `Esc` | Clear Search |
| `Ctrl++` | Increase Font |
| `Ctrl+-` | Decrease Font |

## 🏗️ Architecture

### **Core Components**

#### **`main.py`** - Enhanced Database Browser
- **CustomTkinter modern UI** with professional styling
- **Multi-threaded operations** for responsive experience
- **Comprehensive menu system** with all features
- **Enhanced search capabilities** with global search

#### **`polars_database_utils.py`** - Ultra-Fast Data Engine
- **Polars integration** for 5-30x performance boost
- **Smart caching system** with automatic optimization
- **Multi-format support** (SQLite, CSV, Excel, JSON, Access)
- **Parallel processing** for large datasets

#### **`app_config.py`** - Configuration Management
- **Persistent settings** stored in user directory
- **Database state preservation** between sessions
- **Window geometry restoration** 
- **Recent files management**

#### **`config_manager.py`** - Legacy Configuration Support
- **Backward compatibility** with older versions
- **Migration utilities** for configuration updates

### **Performance Optimizations**

1. **Polars Integration**: Ultra-fast DataFrame operations
2. **Smart Caching**: Automatic data caching for instant access
3. **Lazy Loading**: Load data on-demand for large datasets
4. **Multi-threading**: Background operations don't block UI
5. **Memory Optimization**: Efficient memory usage patterns
2. **DataFrame Optimization**: Automatic data type optimization
3. **Threaded Operations**: Non-blocking UI during data operations
4. **Smart Caching**: Cache frequently accessed data
5. **Chunked Processing**: Handle large datasets efficiently

## System Requirements

- **Python 3.8+**
- **Windows 10/11** (primary), Linux/macOS (should work)
- **RAM**: 4GB+ recommended for large datasets
- **Storage**: Minimal (< 50MB)

## Dependencies

### Required
- `pandas` - Data manipulation and analysis
- `tkinter` - GUI framework (included with Python)

### Optional but Recommended
- `ttkthemes` - Modern GUI themes
- `openpyxl` - Excel file support
- `pyodbc` - Microsoft Access database support
- `Pillow` - Image processing for icons

## File Structure

## 📁 Project Structure

```
ShadowHawk-data-browser/
├── main.py                 # Main application (modern GUI)
├── polars_database_utils.py # Ultra-fast data processing engine
├── app_config.py           # Modern configuration management
├── config_manager.py       # Legacy configuration support
├── simple_browser.py       # Lightweight database browser
├── requirements.txt        # Python dependencies
├── sample_data/           # Sample datasets for testing
├── docs/                  # Documentation
├── tests/                 # Unit tests
├── scripts/               # Utility scripts
└── README.md              # This file
```

## 🔧 Advanced Features

### **💾 Persistent Sessions**
- **Auto-save**: All opened databases remembered between sessions
- **Window state**: Size and position restored on startup  
- **Last selection**: Returns to your last viewed table
- **Configuration**: Settings stored in `~/.shadowhawk/config.json`

### **🔍 Global Search Engine**
- **Cross-database**: Search across all loaded databases simultaneously
- **Multi-threaded**: Parallel search for maximum speed
- **Smart results**: Click results to navigate directly to data
- **Performance stats**: Real-time search performance information

### **📊 Data Analysis Tools**
- **SQL Query Interface**: Execute custom SQL queries
- **Column Statistics**: Detailed statistical analysis
- **Data Export**: Multiple format support with filtering
- **Memory Optimization**: Efficient handling of large datasets

### **🎨 Modern UI Features**
- **CustomTkinter**: Professional modern interface
- **Theme Support**: Dark/light themes with system integration
- **Font Controls**: Adjustable font sizes for accessibility
- **Responsive Layout**: Adapts to different screen sizes

## 🚨 Troubleshooting

### **Installation Issues**
```bash
# If CustomTkinter installation fails
pip install --upgrade pip
pip install customtkinter

# If Polars installation fails  
pip install --upgrade polars
```

### **Runtime Issues**
- **Large files slow to load**: Enable Polars optimization in settings
- **Search results not showing**: Check debug console for error messages
- **Database won't open**: Verify file permissions and format support
- **UI appears broken**: Try updating CustomTkinter to latest version

### **Performance Optimization**
1. **Enable Polars caching** for frequently accessed tables
2. **Limit display rows** in settings for very large datasets  
3. **Close unused databases** to free memory
4. **Use SSD storage** for better file I/O performance

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### **Development Setup**
```bash
# Clone the repository
git clone https://github.com/Klucznik6/ShadowHawk-data-browser.git
cd ShadowHawk-data-browser

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black *.py
```

### **Reporting Issues**
- Use GitHub Issues for bug reports
- Include Python version and OS information
- Attach sample data files if relevant
- Describe steps to reproduce the issue

## 📈 Version History

- **v3.0** - Modern CustomTkinter UI, database persistence, global search
- **v2.0** - Polars integration, enhanced performance, multi-format support  
- **v1.0** - Initial release with basic database browsing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Polars** team for the ultra-fast DataFrame library
- **CustomTkinter** for the modern GUI framework
- **Python** community for excellent data processing libraries
- **Contributors** who helped improve this project

## 📞 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join project discussions for feature requests
- **Email**: Contact maintainers for security-related issues

---

**🦅 ShadowHawk Database Browser** - *Fast, Modern, Reliable*

Built with ❤️ using Python, CustomTkinter, and Polars