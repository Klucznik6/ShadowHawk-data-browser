# ShadowHawk Database Browser - User Guide

## Overview

ShadowHawk Database Browser is a high-performance desktop application designed for browsing and analyzing local databases and data files. Built with Python and modern GUI technologies, it provides fast, intuitive access to your data without requiring web connections or complex setups.

## Key Features

### 🚀 Performance
- **Multi-threaded operations** for responsive UI
- **Optimized data loading** with intelligent caching
- **Memory-efficient processing** for large datasets
- **Real-time search** with instant results

### 📊 File Format Support
- **SQLite databases** (.db, .sqlite, .sqlite3)
- **Microsoft Access** (.mdb, .accdb) *requires pyodbc*
- **CSV files** (.csv)
- **Excel spreadsheets** (.xlsx, .xls)
- **JSON data** (.json)

### 🔍 Data Analysis
- **Advanced search and filtering**
- **Column statistics and analysis**
- **Data type detection and optimization**
- **Sortable columns with visual indicators**
- **Export capabilities** to multiple formats

## Getting Started

### Installation

1. **Run the installer** (Windows):
   ```bash
   install.bat
   ```

2. **Or install manually**:
   ```bash
   pip install pandas ttkthemes openpyxl pyodbc Pillow
   ```

### First Launch

1. **Start the application**:
   ```bash
   run.bat
   # or
   python main.py
   ```

2. **Open your first database**:
   - Click "Open DB" in the toolbar
   - Or press `Ctrl+O`
   - Select a database file

3. **Browse your data**:
   - Select a database from the left panel
   - Choose a table to view
   - Double-click to load data

## User Interface Guide

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ File  Edit  View  Tools  Help                              │
├─────────────────────────────────────────────────────────────┤
│ [Open DB] [Import] [Refresh] [Export]     Search: [____]   │
├─────────────────────────────────────────────────────────────┤
│ Databases    │ Table: employees                           │
│ ┌─────────┐   │ ┌─────────────────────────────────────────┐ │
│ │ sample  │   │ │ Data View │ Column Info │             │ │
│ │ orders  │   │ ├─────────────────────────────────────────┤ │
│ │         │   │ │ ID │ Name      │ Dept    │ Salary      │ │
│ └─────────┘   │ │ 1  │ John Doe  │ IT      │ 75000      │ │
│               │ │ 2  │ Jane Smith│ HR      │ 65000      │ │
│ Tables        │ │ 3  │ Bob Jones │ Sales   │ 80000      │ │
│ ┌─────────┐   │ └─────────────────────────────────────────┘ │
│ │employees│   │                                            │
│ │sales    │   │ Rows: 150                                  │
│ │products │   │                                            │
│ └─────────┘   │                                            │
├─────────────────────────────────────────────────────────────┤
│ Ready                                          [Progress]   │
└─────────────────────────────────────────────────────────────┘
```

### Toolbar Functions

| Button | Function | Shortcut |
|--------|----------|----------|
| Open DB | Open database file | Ctrl+O |
| Import | Import CSV/Excel/JSON | - |
| Refresh | Reload current table | F5 |
| Export | Export current data | - |
| Search | Filter table data | Ctrl+F |

### Menu Reference

#### File Menu
- **Open Database**: Load SQLite, Access, or other database files
- **Import > CSV/Excel/JSON**: Import data files as temporary databases
- **Export > Current Table**: Export all table data
- **Export > Filtered Data**: Export only visible/filtered data

#### Edit Menu
- **Find**: Focus search box (Ctrl+F)
- **Clear Search**: Remove current filter (Escape)
- **Copy Selected**: Copy selected rows to clipboard (Ctrl+C)

#### View Menu
- **Refresh**: Reload current table data (F5)
- **Show Column Stats**: Display detailed column information
- **Font Size**: Adjust display font size

#### Tools Menu
- **SQL Query**: Execute custom SQL queries (coming soon)
- **Data Statistics**: Show comprehensive data analysis
- **Settings**: Configure application preferences

## Working with Data

### Opening Files

#### Database Files
1. Click "Open DB" or press `Ctrl+O`
2. Navigate to your database file
3. Supported formats: `.db`, `.sqlite`, `.sqlite3`, `.mdb`, `.accdb`
4. The database appears in the left panel
5. Select it to view available tables

#### Data Files (CSV/Excel/JSON)
1. Use File → Import or toolbar "Import" button
2. Files are converted to temporary SQLite databases
3. Each sheet/file becomes a table
4. Full database functionality available

### Browsing Data

#### Table Selection
- Click a database in the left panel to see its tables
- Double-click a table name to load its data
- Data appears in the main view area

#### Data Navigation
- **Scroll**: Use scrollbars or arrow keys
- **Sort**: Click column headers to sort
- **Select**: Click rows to select, Ctrl+click for multiple
- **Copy**: Ctrl+C to copy selected rows

### Search and Filter

#### Basic Search
1. Type in the search box (top-right)
2. Results filter automatically as you type
3. Search looks across all columns
4. Case-insensitive matching

#### Advanced Features
- **Numeric search**: Enter numbers to find exact matches
- **Partial matching**: Searches within text fields
- **Multi-word**: Finds rows containing all search terms
- **Clear search**: Press Escape or click "Clear"

### Data Analysis

#### Column Information
1. Click the "Column Info" tab
2. View for each column:
   - Data type
   - Null count
   - Unique values
   - Basic statistics

#### Data Statistics
1. Tools → Data Statistics
2. Comprehensive overview including:
   - Dataset summary
   - Column-by-column analysis
   - Memory usage information
   - Data quality indicators

### Exporting Data

#### Export Options
- **Current Table**: All data from the selected table
- **Filtered Data**: Only currently visible (searched) data
- **Format Support**: CSV, Excel (.xlsx), JSON

#### Export Process
1. Select File → Export or click "Export" button
2. Choose export type (Current Table vs Filtered Data)
3. Select output format and location
4. Export runs in background with progress indicator

## Performance Tips

### Large Databases
- **Limit display**: Only first 10,000 rows shown by default
- **Use search**: Filter data before analysis
- **Memory monitoring**: Check system resources
- **Close unused databases**: Free up memory

### Search Optimization
- **Specific terms**: More specific searches are faster
- **Column-specific**: Future feature for targeted searches
- **Index usage**: Database indexes improve search speed

### Memory Management
- **Data type optimization**: Automatic for better performance
- **Chunked loading**: Large files loaded in pieces
- **Cache management**: Clear cache if memory becomes limited

## Troubleshooting

### Common Issues

#### "Import pandas could not be resolved"
**Solution**: Install required packages
```bash
pip install pandas ttkthemes openpyxl
```

#### "Failed to connect to Access database"
**Solution**: Install Microsoft Access Database Engine and pyodbc
```bash
pip install pyodbc
```
Download Access Database Engine from Microsoft.

#### Application crashes with large files
**Solutions**:
- Increase available memory
- Use search to filter data before loading
- Close other applications
- Consider breaking large files into smaller pieces

#### Slow performance
**Solutions**:
- Enable data type optimization (default)
- Use database indexes for frequently searched columns
- Filter data before analysis
- Check available system memory

#### Threading errors with SQLite
**Solution**: Update to latest version - this is fixed in current release

### Performance Optimization

#### For Large CSV Files
1. Convert to SQLite for better performance
2. Use chunked import if memory limited
3. Create indexes on frequently searched columns

#### For Slow Searches
1. Use more specific search terms
2. Consider creating database views for common queries
3. Use column-specific searches when available

#### Memory Issues
1. Monitor memory usage in Task Manager
2. Close unused databases and applications
3. Use filtering to reduce data size
4. Consider upgrading system RAM for very large datasets

## Keyboard Shortcuts Reference

### File Operations
- `Ctrl+O`: Open database file
- `Ctrl+S`: Save (where applicable)
- `Ctrl+Q`: Quit application

### Navigation
- `F5`: Refresh current table
- `Ctrl+F`: Focus search box
- `Escape`: Clear search/cancel
- `Ctrl+G`: Go to (future feature)

### Data Operations
- `Ctrl+C`: Copy selected rows
- `Ctrl+A`: Select all visible rows
- `Ctrl+X`: Cut (where applicable)
- `Ctrl+V`: Paste (where applicable)

### View Controls
- `Ctrl++`: Increase font size
- `Ctrl+-`: Decrease font size
- `Ctrl+0`: Reset font size
- `F11`: Toggle fullscreen (future feature)

## Configuration

### Settings File
Location: `config.json` in application directory

### Key Settings
```json
{
  "max_display_rows": 10000,     // Maximum rows to display
  "chunk_size": 1000,            // Loading chunk size
  "auto_optimize_datatypes": true, // Optimize memory usage
  "theme": "arc"                 // UI theme
}
```

### Customization
- Edit `config.json` to change defaults
- Restart application for changes to take effect
- Backup configuration before making changes

## Advanced Usage

### SQL Queries (Future Feature)
- Custom query interface for advanced users
- Support for complex joins and aggregations
- Query history and favorites
- Export query results

### Data Visualization (Future Feature)
- Charts and graphs for numeric data
- Data distribution analysis
- Trend analysis for time-series data
- Export visualizations

### Automation (Future Feature)
- Batch processing multiple files
- Scheduled data imports
- Custom data transformation scripts
- API integration for external data sources

## Support and Development

### Getting Help
1. Check this documentation
2. Review troubleshooting section
3. Check Python and dependency documentation
4. File issues on project repository

### Contributing
- Application designed for easy customization
- Main logic in `main.py` and `database_utils.py`
- UI components modular and extensible
- Follow Python PEP 8 style guidelines

### Feature Requests
- SQL query interface
- Data visualization
- Batch processing
- Additional database formats
- Cloud storage integration

---

**ShadowHawk Database Browser** - Fast, reliable local database browsing for professionals and enthusiasts.
