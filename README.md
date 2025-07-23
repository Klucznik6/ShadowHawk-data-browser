# ShadowHawk Database Browser

A fast, modern desktop application for browsing local databases and data files with a sleek GUI.

![ShadowHawk Database Browser](https://via.placeholder.com/800x600/2c3e50/ffffff?text=ShadowHawk+Database+Browser)

## Features

### 🚀 **High Performance**
- **Multi-threaded operations** for responsive UI
- **Optimized data loading** with smart caching
- **Memory-efficient** DataFrame processing
- **Fast search and filtering** across large datasets

### 📊 **Supported File Formats**
- **SQLite** (.db, .sqlite, .sqlite3)
- **Microsoft Access** (.mdb, .accdb) - with pyodbc
- **CSV files** (.csv)
- **Excel files** (.xlsx, .xls) 
- **JSON files** (.json)

### 🔍 **Advanced Data Browsing**
- **Real-time search** with instant filtering
- **Column statistics** and data analysis
- **Sortable columns** with visual indicators
- **Data export** to multiple formats
- **Column type detection** and optimization

### 🎨 **Modern GUI**
- **Clean, intuitive interface** with theming support
- **Tabbed interface** for data and column views
- **Context menus** for quick actions
- **Keyboard shortcuts** for power users
- **Progress indicators** for long operations

## Quick Start

### 1. Install Dependencies
Run the installation script (Windows):
```bash
install.bat
```

Or manually install with pip:
```bash
pip install pandas ttkthemes openpyxl pyodbc Pillow
```

### 2. Run the Application
```bash
# Windows
run.bat

# Or directly with Python
python main.py
```

## Usage

### Opening Databases
1. Click **"Open DB"** or press `Ctrl+O`
2. Select your database file
3. Browse tables in the left panel
4. Double-click a table to load data

### Importing Data Files
- **CSV**: File → Import → CSV File
- **Excel**: File → Import → Excel File  
- **JSON**: File → Import → JSON File

### Searching Data
1. Type in the search box (top-right)
2. Results filter automatically as you type
3. Press `Escape` to clear search

### Exporting Data
- **Current table**: File → Export → Current Table
- **Filtered data**: File → Export → Filtered Data
- Supports CSV, Excel, and JSON formats

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open database |
| `Ctrl+F` | Focus search |
| `F5` | Refresh current table |
| `Ctrl+C` | Copy selected rows |
| `Escape` | Clear search |

## Architecture

### Core Components

**`main.py`** - Main application with enhanced GUI
- Modern tkinter interface with ttkthemes
- Multi-threaded operations for performance
- Advanced search and filtering
- Data visualization and statistics

**`database_utils.py`** - Database management utilities
- Multi-format database support
- Optimized data processing with pandas
- Memory-efficient operations
- Fast search algorithms

**`database_browser.py`** - Simple version for basic usage
- Lightweight implementation
- Core functionality only
- Good for learning/customization

### Performance Optimizations

1. **Lazy Loading**: Only load visible data rows
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

```
ShadowHawk-data-browser/
├── main.py              # Enhanced main application
├── database_browser.py  # Simple version
├── database_utils.py    # Database utilities
├── requirements.txt     # Python dependencies
├── install.bat         # Windows installer
├── run.bat             # Windows launcher
└── README.md           # This file
```

## Advanced Features

### Data Statistics
- **Column analysis**: Data types, null counts, unique values
- **Numeric statistics**: Min, max, mean, standard deviation
- **Memory usage**: Optimized data type recommendations

### Search Capabilities
- **Multi-column search**: Search across all columns simultaneously
- **Data type aware**: Handles text, numeric, and date searches
- **Real-time filtering**: Results update as you type
- **Case-insensitive**: Flexible text matching

### Export Options
- **Format preservation**: Maintain data types during export
- **Filtered exports**: Export only visible/filtered data
- **Large dataset handling**: Efficient export of big files

## Troubleshooting

### Common Issues

**"Import pandas could not be resolved"**
- Run `install.bat` or `pip install pandas`

**"Failed to connect to Access database"**
- Install Microsoft Access Database Engine
- Ensure pyodbc is installed: `pip install pyodbc`

**"Application crashes on large files"**
- Increase max_display_rows in settings
- Use filtering to reduce data size
- Close other applications to free memory

### Performance Tips

1. **For large CSV files**: Use chunked loading
2. **For slow searches**: Create database indexes
3. **For memory issues**: Enable data type optimization
4. **For UI freezing**: Ensure threading is enabled

## Contributing

This is a single-file application designed for simplicity and performance. To contribute:

1. Fork the repository
2. Create feature branches
3. Test with various database formats
4. Submit pull requests

## License

MIT License - See LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review Python and dependency documentation
- File issues on the project repository

---

**Built with ❤️ using Python, tkinter, and pandas**