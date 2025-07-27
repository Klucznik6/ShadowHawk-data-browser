# 💾 Database Persistence Feature - User Guide

## ✨ What's New

Your ShadowHawk Database Browser now **automatically saves and restores** loaded databases! No more manually reloading files every time you start the application.

## 🚀 Key Features

### 📁 **Automatic Database Persistence**
- **Auto-save**: All loaded databases are automatically saved when you load them
- **Auto-restore**: Previously loaded databases are restored when you start the app
- **Smart tracking**: Only file-based databases (CSV, Excel, SQLite, etc.) are saved
- **File validation**: Non-existent files are automatically removed from history

### 🔄 **Recent Files Menu**
- **Quick access**: Recent files menu shows your last 10 loaded files
- **Smart filtering**: Only existing files are displayed
- **One-click loading**: Click any recent file to load it instantly
- **Auto-cleanup**: Deleted files are automatically removed from the list

### ⚙️ **Configurable Settings**
- **Enable/disable**: Turn persistence on/off in settings
- **Auto-reconnect**: Choose whether to restore databases on startup
- **History limit**: Configure how many recent files to remember (default: 10)
- **Manual control**: Save database states manually anytime

## 📋 How It Works

### **When You Load a Database:**
1. 📂 File is loaded normally with Polars ultra-speed
2. 💾 Database info is automatically saved to `config.json`
3. 📁 File is added to recent files list
4. ✅ Status shows "💾 Loaded & Saved" confirmation

### **When You Start the App:**
1. 🔄 App checks for saved databases
2. 📋 Validates that files still exist
3. ⚡ Automatically reloads valid databases
4. 🗑️ Removes invalid entries from history
5. ✅ Shows "✅ Restored X databases" status

### **When You Close the App:**
1. 💾 Current database states are saved
2. 🔒 Database connections are properly closed
3. 📋 Settings and window size are saved
4. ✅ All data is preserved for next session

## 🎯 New Menu Options

### **File Menu Additions:**
- **📁 Recent Files** - Quick access to recently loaded files
- **💾 Save Database State** - Manually save all current databases
- **🔄 Restore Saved Databases** - Manually restore saved databases
- **🗑️ Clear Database History** - Clear all saved history

### **Recent Files Submenu:**
- Shows last 10 loaded files (configurable)
- **1. filename.csv** - Click to load instantly
- **🗑️ Clear Recent Files** - Clear the recent files list

## ⚙️ Configuration Options

The following settings control persistence behavior (in `config.json`):

```json
"persistence_settings": {
  "save_loaded_databases": true,        // Enable/disable auto-save
  "auto_reconnect_on_startup": true,    // Auto-restore on startup
  "max_recent_databases": 10,           // Max recent files to remember
  "remember_database_state": true       // Remember database states
}
```

## 🔧 Manual Controls

### **Save Current State:**
- Menu: `File > 💾 Save Database State`
- Saves all currently loaded databases
- Shows confirmation with count of saved databases

### **Restore Databases:**
- Menu: `File > 🔄 Restore Saved Databases`  
- Manually restores saved databases
- Useful if auto-restore is disabled

### **Clear History:**
- Menu: `File > 🗑️ Clear Database History`
- Clears all saved database history
- Clears recent files list
- Current loaded databases remain open

## 📊 What Gets Saved

### **For Each Database:**
- ✅ **File path** - Full path to the database file
- ✅ **Database type** - CSV, Excel, SQLite, etc.
- ✅ **Table names** - List of tables in the database
- ✅ **Last accessed** - Timestamp of when it was loaded
- ✅ **Display name** - Name shown in the database list

### **Application Settings:**
- ✅ **Window size and position**
- ✅ **UI preferences**
- ✅ **Performance settings**
- ✅ **Recent files list**

## 🚫 What Doesn't Get Saved

- ❌ **In-memory databases** - Only temporary, can't be restored
- ❌ **Database connections** - Recreated when restored
- ❌ **Table data** - Only file paths, data is reloaded from files
- ❌ **Search results** - Filters and searches are reset

## 🎉 Benefits

### **Productivity Boost:**
- **No more manual reloading** - Start working immediately
- **Quick file access** - Recent files menu for instant loading
- **Session continuity** - Pick up where you left off
- **Workflow efficiency** - Focus on analysis, not file management

### **User Experience:**
- **Seamless startup** - Databases ready when you are
- **Smart file tracking** - Only valid files are remembered
- **Visual feedback** - Clear status messages and confirmations
- **Easy cleanup** - Simple history management

### **Data Safety:**
- **No data loss** - Settings and state always preserved
- **File validation** - Invalid files automatically cleaned up
- **Graceful shutdown** - Proper connection cleanup on exit
- **Backup friendly** - Settings stored in readable JSON format

## 🔍 Troubleshooting

### **If Databases Don't Restore:**
1. Check that `auto_reconnect_on_startup` is `true` in config.json
2. Verify that database files still exist at their original locations
3. Check the status bar for restoration messages
4. Use `File > 🔄 Restore Saved Databases` to manually restore

### **If Recent Files Don't Show:**
1. Make sure files were loaded successfully (not just opened)
2. Check that files still exist on disk
3. Try `File > 📁 Recent Files > 🗑️ Clear Recent Files` and reload

### **If Settings Don't Persist:**
1. Ensure the application has write permissions in its directory
2. Check that `config.json` is being created/updated
3. Look for error messages in the console/status bar

## 🎯 Tips for Best Experience

1. **Organize your data files** - Keep databases in stable locations
2. **Use descriptive filenames** - Easier to identify in recent files
3. **Regular cleanup** - Clear history periodically to remove old files
4. **Monitor the status bar** - Shows helpful persistence messages
5. **Enable auto-restore** - Start working immediately every time

---

## 🎉 Summary

Your ShadowHawk Database Browser now automatically saves and restores your work session! Combined with Polars ultra-speed performance, you have a database browser that's both lightning-fast and incredibly convenient.

**Key advantages:**
- 🚀 **46x faster searches** with Polars
- 💾 **Automatic database persistence**
- 📁 **Recent files quick access**
- 🔄 **Seamless session restoration**
- ⚙️ **Fully configurable**

Start the application and your databases will be ready and waiting! 🎯✨
