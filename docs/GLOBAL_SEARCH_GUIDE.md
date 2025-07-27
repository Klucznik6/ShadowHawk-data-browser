# Global Search Feature - User Guide

## Overview
The Global Search feature allows you to search across all loaded databases and tables simultaneously, instead of just searching within the currently selected table.

## How to Use

### 1. Enable Global Search
- In the search toolbar on the right side, you'll see a checkbox labeled "Search All DBs"
- Check this box to enable global search mode
- Uncheck it to return to normal single-table search mode

### 2. Load Multiple Databases
- Use "Open DB" to load SQLite database files
- Use "Import CSV", "Import Excel", or "Import JSON" to load data files
- Each loaded file/database will be available for global search

### 3. Perform Global Search
- With "Search All DBs" checked, type your search term in the search box
- Press Enter or wait for auto-search (500ms delay)
- The application will search through ALL tables in ALL loaded databases

### 4. Understanding Results
Global search results include two additional columns:
- **_database**: Shows which database/file the result came from
- **_table**: Shows which table within that database the result came from
- **_source_row**: Shows the original row number in that table

### 5. Search Summary
When global search completes, you'll see:
- A dialog box showing detailed search statistics
- Number of matches found per database and table
- Total matches across all databases
- Number of tables and databases searched

## Features

### Performance Optimizations
- Multi-threaded searching to keep the UI responsive
- Progress indicators during search operations
- Automatic memory optimization for large datasets

### Search Capabilities
- **Text Search**: Case-insensitive partial text matching
- **Numeric Search**: Exact numeric matches and partial number searches
- **All Column Types**: Searches across all data types (text, numbers, dates)

### Result Management
- Results limited to 5000 rows for main browser, 2000 for simple browser
- Clear search button to return to normal view
- Automatic column resizing for database and table columns

## Tips for Best Results

### 1. Load Related Databases
- Load databases that might contain related information
- Good for finding data scattered across multiple files
- Useful for data validation and cross-referencing

### 2. Use Specific Search Terms
- More specific terms will return more relevant results
- Common terms might return too many matches
- Use partial product codes, names, or IDs for best results

### 3. Understanding Performance
- Global search may take longer with many large databases
- Progress is shown in the status bar
- Search runs in background, so you can continue using the interface

## Example Use Cases

### 1. Customer Data Search
- Load customer databases from different departments
- Search for a customer name across all databases
- See which systems have information about that customer

### 2. Product Inventory Search
- Load inventory files from different locations
- Search for product codes across all locations
- Get a complete view of product availability

### 3. Data Validation
- Load main database and imported data files
- Search for specific values to verify data consistency
- Find duplicates or inconsistencies across datasets

## Troubleshooting

### No Results Found
- Verify databases are properly loaded (check left panel)
- Try simpler or partial search terms
- Check that your search term exists in the data

### Performance Issues
- Close unused databases to improve speed
- Use more specific search terms to reduce result size
- Consider using single-table search for large datasets

### Memory Usage
- Large result sets are automatically optimized
- Display is limited to prevent memory issues
- Clear search frequently when working with large datasets

## Technical Notes

### Supported Database Types
- SQLite databases (.db, .sqlite, .sqlite3)
- CSV files (loaded as in-memory databases)
- Excel files (.xlsx, .xls) - each sheet becomes a table
- JSON files (converted to tabular format)
- Microsoft Access files (.mdb, .accdb) - if pyodbc is available

### Search Algorithm
- Uses pandas string search with regex disabled for safety
- Combines results from all databases using pandas concat
- Maintains original data types and formatting
- Adds metadata columns for source tracking

### Thread Safety
- All database operations are thread-safe
- UI updates happen on the main thread
- Background search operations won't block the interface

---

*This feature is available in both the main ShadowHawk Database Browser and the simple browser version.*
