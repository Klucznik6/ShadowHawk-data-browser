# ShadowHawk Database Browser v1.0.0

<div align="center">
  <img src="assets/icon.png" alt="ShadowHawk Database Browser" width="128" height="128">
</div>

<div align="center">

**A powerful, modern database browser and data analysis tool with ultra-fast performance**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)

*Built with Python, Tkinter, and Polars for maximum performance*

</div>

---

## ✨ Key Features

### 🚀 **Ultra-Fast Performance**
- **5-30x faster** data processing with **Polars integration**
- **Multi-threaded operations** for responsive, non-blocking UI
- **Smart caching system** for instant data access and navigation
- **Memory-efficient processing** of large datasets (millions of rows)
- **Real-time progress indicators** with performance statistics

### 🎨 **Modern User Interface**
- **Professional themed interface** with modern styling
- **Intuitive tabbed layout** with data view and column info tabs
- **Responsive design** that adapts to different screen sizes
- **Context menus** and keyboard shortcuts for power users
- **Status bar** with real-time operation feedback

### 🔍 **Advanced Search & Analysis**
- **Global search** across all loaded databases simultaneously
- **Ultra-fast parallel search** with real-time result filtering
- **Interactive search results** with navigation to source data
- **Local table search** with instant filtering
- **Search highlighting** and match count statistics

### 💾 **Comprehensive File Format Support**
- **SQLite databases** (.db, .sqlite, .sqlite3)
- **CSV files** with intelligent auto-detection and encoding
- **Excel spreadsheets** (.xlsx, .xls) with multi-sheet support
- **JSON data files** with nested structure flattening
- **Microsoft Access** (.mdb, .accdb) via ODBC connection

### 🗃️ **Smart Database Management**
- **Persistent sessions** - automatically remembers all databases between restarts
- **Recent files menu** with quick access to previously opened files
- **Database removal controls** with confirmation dialogs
- **Automatic state restoration** of your last working session
- **Configuration persistence** with user preferences

### 📊 **Professional Data Analysis Tools**
- **Column statistics** with detailed analysis (min/max/mean/null counts)
- **Data type detection** and optimization
- **Export capabilities** to CSV, Excel, and JSON formats
- **SQL query interface** for custom data analysis
- **Copy/paste functionality** for cells, rows, and columns

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (Python 3.10+ recommended)
- **Windows 10/11** (primary support), macOS/Linux compatible

### Installation

#### Option 1: Automatic Installation (Windows)
```bash
# Download and run the setup script
setup.bat
```

#### Option 2: Manual Installation
```bash
# Clone or download the project
git clone https://github.com/yourusername/ShadowHawk-data-browser.git
cd ShadowHawk-data-browser

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

#### Windows
```bash
# Use the start script
start.bat

# Or run directly
python main.py
```

#### macOS/Linux
```bash
# Run directly
python3 main.py

# Or with specific Python version
python3.10 main.py
```

---

## 💡 Usage Guide

### 📂 **Opening Databases and Files**

1. **Open Database Files**
   - Click **"Open DB"** button or use `Ctrl+O`
   - Select SQLite database files (.db, .sqlite, .sqlite3)
   - Database appears in the left panel

2. **Import Data Files**
   - Click **"Import"** button or use File → Import menu
   - Supported formats: CSV, Excel (.xlsx/.xls), JSON
   - Files are automatically converted to SQLite for fast access

3. **Recent Files**
   - Access recently opened files via File → Recent Files
   - Databases are remembered between application sessions

### 🔍 **Searching and Filtering Data**

#### **Local Search (Current Table)**
- Enter search terms in the search box
- Results update in real-time as you type
- Search across all columns simultaneously

#### **Global Search (All Databases)**
- Enable **"🌐 Search All DBs"** checkbox
- Search across all loaded databases and tables
- View results in unified interface with source information
- Click results to navigate to original data location

### 📊 **Data Analysis and Statistics**

#### **Column Information**
- Switch to **"Column Info"** tab for detailed column statistics
- View data types, null counts, unique values
- See min/max/mean for numeric columns

#### **Data Statistics**
- Use Tools → Data Statistics for comprehensive analysis
- Export statistics for reporting

#### **SQL Queries**
- Access Tools → SQL Query for custom database queries
- Execute complex joins and aggregations
- Results displayed in main data view

### 💾 **Data Export**

1. **Export Current Table**
   - File → Export → Current Table
   - Choose format: CSV, Excel, JSON

2. **Export Filtered Data**
   - Perform search/filter operations
   - File → Export → Filtered Data
   - Only matching rows are exported

### ⚙️ **Database Management**

#### **Persistent Sessions**
- All opened databases are automatically saved
- Restored on next application startup
- Manual save via File → Save Database State

#### **Remove Databases**
- Right-click database name for context menu
- Select "❌ Remove Database"
- Original files are not deleted

#### **Clear History**
- File → Clear Database History
- Removes all saved database states

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open Database/File |
| `Ctrl+F` | Focus Search Box |
| `Ctrl+C` | Copy Selected Data |
| `F5` | Refresh Current Table |
| `Esc` | Clear Search |
| `Ctrl++` | Increase Font Size |
| `Ctrl+-` | Decrease Font Size |

---

## 🏗️ Architecture

### **Core Components**

#### **main.py** - Enhanced Database Browser
- Modern Tkinter-based GUI with professional styling
- Multi-threaded operations for responsive user experience
- Comprehensive menu system with all application features
- Enhanced search capabilities with global database search

#### **polars_database_utils.py** - Ultra-Fast Data Processing Engine
- **Polars integration** for 5-30x performance improvement over pandas
- Smart caching system with automatic data optimization
- Multi-format file support with intelligent type detection
- Parallel processing capabilities for large dataset handling

#### **config_manager.py** - Configuration and Persistence Management
- Persistent application settings stored in user directory
- Database state preservation between application sessions
- Window geometry and layout restoration
- Recent files management with automatic cleanup

#### **simple_browser.py** - Lightweight Alternative
- Simplified interface for basic database browsing
- Reduced resource usage for older systems
- Core functionality without advanced features

### **Performance Optimizations**

1. **Polars Integration**: Ultra-fast DataFrame operations (5-30x faster than pandas)
2. **Smart Caching**: Automatic data caching for instant subsequent access
3. **Lazy Loading**: Data loaded on-demand to reduce memory usage
4. **Multi-threading**: Background operations don't block the user interface
5. **Memory Optimization**: Efficient data structures and garbage collection
6. **Chunked Processing**: Handle datasets larger than available RAM

---

## 📁 Project Structure

```
ShadowHawk-data-browser/
├── main.py                    # Main application with modern GUI
├── polars_database_utils.py   # Ultra-fast Polars data processing engine
├── config_manager.py          # Configuration and persistence management
├── simple_browser.py          # Lightweight alternative browser
├── requirements.txt           # Python dependencies
├── setup.bat                  # Windows installation script
├── start.bat                  # Windows application launcher
├── config.json.template       # Configuration template
├── assets/
│   └── icon.png              # Application icon
├── docs/                     # Documentation
│   ├── USER_GUIDE.md         # Comprehensive user guide
│   ├── PERFORMANCE_GUIDE.md  # Performance optimization guide
│   ├── TROUBLESHOOTING.md    # Common issues and solutions
│   └── *.md                  # Additional documentation
├── sample_data/              # Sample datasets for testing
│   └── create_sample_data.py # Generate test databases
├── tests/                    # Unit tests and performance tests
│   ├── performance_test.py   # Performance benchmarking
│   ├── polars_speed_test.py  # Polars vs pandas comparison
│   └── test_*.py            # Various unit tests
└── scripts/                  # Utility scripts
    └── *.py                  # Installation and setup utilities
```

---

## 📋 System Requirements

### **Minimum Requirements**
- **Python 3.8+** (Python 3.10+ recommended)
- **2GB RAM** (4GB+ recommended for large datasets)
- **100MB disk space** for application and dependencies
- **Windows 10/11**, macOS 10.14+, or Linux (Ubuntu 20.04+)

### **Recommended Specifications**
- **Python 3.10+** with latest pip
- **8GB RAM** for optimal performance with large datasets
- **SSD storage** for faster database file access
- **Multi-core CPU** for parallel processing benefits

---

## 📦 Dependencies

### **Required Libraries**
```
polars>=0.20.0          # Ultra-fast DataFrame operations
pandas>=2.0.0           # Data manipulation and analysis
pyarrow>=14.0.0         # Arrow columnar format support
```

### **Optional Libraries (Recommended)**
```
ttkthemes>=3.2.2        # Additional GUI themes
openpyxl>=3.1.0         # Excel file read/write support
xlrd>=2.0.0             # Legacy Excel file support
pyodbc>=4.0.39          # Microsoft Access database support
Pillow>=10.0.0          # Image processing for GUI icons
fastparquet>=2023.10.0  # Fast Parquet file operations
```

### **Development Dependencies**
```
pytest>=7.0.0           # Testing framework
black>=23.0.0           # Code formatting
flake8>=6.0.0           # Code linting
```

---

## 🔧 Advanced Features

### **💾 Persistent Session Management**
- **Auto-save functionality**: All opened databases are automatically remembered
- **Window state restoration**: Application size, position, and layout restored on startup
- **Last session recovery**: Returns to your last viewed database and table
- **Configuration backup**: Settings stored in user directory for safety

### **🔍 Ultra-Fast Global Search Engine**
- **Cross-database search**: Search across all loaded databases simultaneously
- **Parallel processing**: Multi-threaded search for maximum performance
- **Smart result navigation**: Click search results to jump directly to source data
- **Performance monitoring**: Real-time search statistics and optimization info

### **📊 Professional Data Analysis Tools**
- **SQL query interface**: Execute custom SQL queries with syntax highlighting
- **Statistical analysis**: Comprehensive column statistics with min/max/mean/median
- **Data export flexibility**: Multiple format support with advanced filtering options
- **Memory optimization**: Handle datasets larger than available system RAM

### **🎨 Modern User Interface Features**
- **Theme support**: Professional light/dark themes with system integration
- **Font size controls**: Adjustable text size for improved accessibility
- **Responsive layout**: Interface adapts to different screen sizes and orientations
- **Context-sensitive menus**: Right-click menus for quick access to relevant actions

---

## 🚨 Troubleshooting

### **Common Issues**

#### **"Module not found" errors**
```bash
pip install -r requirements.txt
```

#### **Permission errors on Windows**
- Run Command Prompt as Administrator
- Or use: `python -m pip install --user -r requirements.txt`

#### **Large file performance issues**
- Enable Polars optimization in settings
- Increase system virtual memory
- Close other resource-intensive applications

#### **Database connection issues**
- Verify file permissions and paths
- Check if database files are corrupted
- For Access databases, ensure ODBC drivers are installed

### **Performance Optimization Tips**

1. **Enable Polars acceleration** for 5-30x speed improvement
2. **Close unused databases** to free memory
3. **Use SSD storage** for database files when possible
4. **Increase virtual memory** for very large datasets
5. **Keep Python and dependencies updated**

---

## 🤝 Contributing

We welcome contributions to ShadowHawk Database Browser! Here's how to get started:

### **Development Setup**
```bash
# Clone the repository
git clone https://github.com/yourusername/ShadowHawk-data-browser.git
cd ShadowHawk-data-browser

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
python -m pytest tests/

# Format code
black *.py
```

### **Contribution Guidelines**
1. **Fork the repository** and create a feature branch
2. **Follow PEP 8** style guidelines for Python code
3. **Add tests** for new functionality
4. **Update documentation** for user-facing changes
5. **Submit pull requests** with clear descriptions

### **Areas for Contribution**
- Additional database format support
- Performance optimizations
- UI/UX improvements
- Documentation and tutorials
- Bug fixes and testing

---

## 📈 Version History

### **v1.0.0** (Current)
- ✅ Complete rewrite with Polars integration for ultra-fast performance
- ✅ Modern GUI with professional theming and responsive layout
- ✅ Global search across multiple databases with parallel processing
- ✅ Persistent session management with automatic state restoration
- ✅ Comprehensive file format support (SQLite, CSV, Excel, JSON, Access)
- ✅ Advanced data analysis tools and export capabilities
- ✅ Full keyboard shortcut support and accessibility features

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for full details.

### MIT License Summary
- ✅ **Commercial use** - Use in commercial projects
- ✅ **Modification** - Modify and adapt the code
- ✅ **Distribution** - Distribute original or modified versions
- ✅ **Private use** - Use privately without restrictions
- ❓ **Warranty** - No warranty provided
- ❓ **Liability** - Authors not liable for damages

---

## 🙏 Acknowledgments

Special thanks to the following projects and communities:

- **[Polars](https://pola.rs/)** team for the ultra-fast DataFrame library that powers our performance
- **Python Software Foundation** for the excellent standard library and ecosystem
- **Tkinter community** for GUI framework documentation and examples
- **Pandas team** for data analysis inspiration and compatibility
- **Open source contributors** who helped improve this project

---

## 📞 Support & Community

### **Getting Help**
- 📖 **Documentation**: Check the `/docs` folder for detailed guides
- 🐛 **Bug Reports**: Submit issues via GitHub Issues with detailed information
- 💡 **Feature Requests**: Use GitHub Discussions for feature suggestions
- 📧 **Security Issues**: Contact maintainers directly for security-related concerns

### **Community Resources**
- **User Guide**: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- **Performance Guide**: [docs/PERFORMANCE_GUIDE.md](docs/PERFORMANCE_GUIDE.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

### **Professional Support**
For commercial support, training, or custom development:
- Custom feature development
- Performance optimization consulting
- Integration with existing systems
- Training and workshops

---

<div align="center">

## 🦅 **ShadowHawk Database Browser**

***Fast • Modern • Reliable***

*Empowering data professionals with lightning-fast database browsing and analysis*

**Built with ❤️ using Python, Tkinter, and Polars**

---

*⭐ Star this project if you find it useful!*

</div>