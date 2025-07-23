# ShadowHawk Database Browser - Troubleshooting Guide

## ✅ **SOLUTION FOUND!**

**Problem:** Multiple Python installations causing package conflicts

**Root Cause:** You have at least two Python installations:
- `C:\Python313\python.exe` (where packages are installed)
- `C:\MySYS\mingw64\bin\python.exe` (system default, no pip)

**Solution:** Use the correct Python path that has the packages installed.

## 🚀 **How to Run the Application**

### **Method 1: Use the new launcher (Recommended)**
```bash
# Double-click this file:
run_python.bat
```

### **Method 2: Command line with correct Python**
```bash
C:\Python313\python.exe main.py
```

### **Method 3: Original batch files (updated)**
The original `install.bat` and `run.bat` files have been updated to detect the correct Python installation automatically.

## 🔧 **Understanding the Issue**

### **What Happened:**
1. Your system has multiple Python installations
2. When you run `python`, it uses `C:\MySYS\mingw64\bin\python.exe`
3. When you run `pip install`, it installs to `C:\Python313\`
4. This creates a mismatch where packages are in one Python but you're running another

### **How to Check Your Python Setup:**
```bash
# Check which Python is used by default
python --version
where python

# Check which pip is used
where pip

# Check if pandas is available in current Python
python -c "import pandas; print('pandas OK')"

# Check the correct Python installation
C:\Python313\python.exe -c "import pandas; print('pandas OK in Python313')"
```

## 📋 **Files Created for You**

### **Main Application Files:**
- `main.py` - Enhanced application with modern GUI
- `database_browser.py` - Simple version for basic usage
- `database_utils.py` - Database utilities

### **Installation & Launcher Files:**
- `install_python.py` - Smart installer (detects correct Python)
- `run_python.bat` - Launcher using correct Python path
- `install.bat` - Updated batch installer
- `run.bat` - Updated batch launcher

### **Sample Data Files:**
- `sample_data.db` - SQLite database with 4 tables (employees, sales, customers, inventory)
- `sample_employees.csv` - CSV file with employee data
- `sample_products.json` - JSON file with product data

### **Configuration:**
- `requirements.txt` - Package dependencies
- `config.json` - Application settings

## 📊 **Testing the Application**

### **1. Start the Application:**
Double-click `run_python.bat` or run:
```bash
C:\Python313\python.exe main.py
```

### **2. Test with Sample Data:**
1. **Open Database:** Click "Open DB" → Select `sample_data.db`
2. **Browse Tables:** Click on tables in left panel → Double-click to load data
3. **Import CSV:** File → Import → CSV File → Select `sample_employees.csv`
4. **Import JSON:** File → Import → JSON File → Select `sample_products.json`
5. **Search Data:** Type in search box (top-right)
6. **Export Data:** Select table → File → Export

## 🎯 **Key Features to Test**

### **Performance Features:**
- ✅ Multi-threaded loading (no UI freezing)
- ✅ Fast search with real-time filtering
- ✅ Large dataset handling (10,000+ rows)
- ✅ Memory optimization

### **File Format Support:**
- ✅ SQLite databases (.db, .sqlite, .sqlite3)
- ✅ CSV files (.csv)
- ✅ Excel files (.xlsx, .xls) 
- ✅ JSON files (.json)
- ✅ Microsoft Access (.mdb, .accdb) - if available

### **GUI Features:**
- ✅ Modern themed interface
- ✅ Sortable columns
- ✅ Column statistics
- ✅ Context menus
- ✅ Keyboard shortcuts

## 🔧 **Future Prevention**

### **To Avoid Python Path Issues:**
1. **Use Virtual Environments:**
   ```bash
   C:\Python313\python.exe -m venv shadowhawk_env
   shadowhawk_env\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Always Specify Full Python Path:**
   ```bash
   C:\Python313\python.exe -m pip install package_name
   C:\Python313\python.exe script.py
   ```

3. **Check Your Environment:**
   ```bash
   # Before installing packages
   which python
   which pip
   python --version
   ```

## 📞 **Additional Support**

### **If the Application Still Won't Start:**
1. Run the diagnostic command:
   ```bash
   C:\Python313\python.exe -c "import sys, pandas, tkinter; print('All imports OK')"
   ```

2. Check for any error messages in the console

3. Ensure Windows hasn't blocked the executable

### **Common Error Messages:**
- **"No module named 'pandas'"** → Use correct Python path
- **"No module named 'tkinter'"** → tkinter should be built-in to Python
- **"Permission denied"** → Run as administrator or check antivirus
- **Threading errors** → Restart the application

## 🎉 **Success Indicators**

You'll know everything is working when:
- ✅ Application window opens without errors
- ✅ Sample database loads with 4 tables
- ✅ You can search and filter data
- ✅ CSV/JSON imports work
- ✅ Export functions work
- ✅ No console error messages

---

**The application is now ready to use with full functionality!**
