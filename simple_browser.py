#!/usr/bin/env python3
"""
ShadowHawk Database Browser - Simple Version with Polars Ultra-Speed
Fast desktop application for browsing local databases and data files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pandas as pd
import threading
import os
from datetime import datetime
import json

# Import Polars for ultra-fast performance
from polars_database_utils import PolarsDatabaseManager
from config_manager import ConfigManager

try:
    from ttkthemes import ThemedTk
    THEMED_TK_AVAILABLE = True
except ImportError:
    THEMED_TK_AVAILABLE = False

class SimpleDatabaseBrowser:
    """Simple database browser with Polars ultra-fast functionality"""
    
    def __init__(self):
        # Initialize main window
        if THEMED_TK_AVAILABLE:
            self.root = ThemedTk(theme="arc")
        else:
            self.root = tk.Tk()
            
        self.root.title("ShadowHawk Database Browser - Simple (Polars Ultra-Fast)")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Database connections and data
        self.connections = {}
        self.current_db = None
        self.current_table = None
        self.current_data = None
        
        # Initialize managers
        self.config_manager = ConfigManager()  # Configuration and persistence
        self.polars_manager = PolarsDatabaseManager()
        
        # Setup UI
        self.setup_ui()
        
        # Restore saved databases and setup close handler
        self.restore_saved_databases()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Setup the main UI components"""
        self.create_menu()
        self.create_toolbar()
        self.create_main_panels()
        self.create_status_bar()
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Database", command=self.open_database)
        file_menu.add_command(label="Import CSV", command=self.import_csv)
        file_menu.add_command(label="Import Excel", command=self.import_excel)
        file_menu.add_command(label="Import JSON", command=self.import_json)
        file_menu.add_separator()
        
        # Recent files
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="📁 Recent Files", menu=self.recent_menu)
        self.update_recent_files_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="❌ Remove All Databases", command=self.remove_all_databases)
        file_menu.add_separator()
        file_menu.add_command(label="Export Current Table", command=self.export_table)
        file_menu.add_separator()
        file_menu.add_command(label="💾 Save Database State", command=self.save_all_database_states)
        file_menu.add_command(label="🔄 Restore Databases", command=self.restore_saved_databases)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Remove Selected Database", command=self.remove_selected_database)
        file_menu.add_command(label="🗑️ Remove All Databases", command=self.remove_all_databases)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
    def create_toolbar(self):
        """Create toolbar with common actions"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Database operations
        ttk.Button(toolbar, text="Open DB", command=self.open_database).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Import CSV", command=self.import_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Import Excel", command=self.import_excel).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Import JSON", command=self.import_json).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Data operations
        ttk.Button(toolbar, text="Refresh", command=self.refresh_current_table).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export", command=self.export_table).pack(side=tk.LEFT, padx=2)
        
        # Search
        # Global search toggle
        self.global_search_var = tk.BooleanVar()
        global_search_cb = ttk.Checkbutton(toolbar, text="Search All DBs", 
                                         variable=self.global_search_var)
        global_search_cb.pack(side=tk.RIGHT, padx=2)
        
        ttk.Label(toolbar, text="Search:").pack(side=tk.RIGHT, padx=2)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.RIGHT, padx=2)
        self.search_entry.bind('<Return>', self.search_data)
        
    def create_main_panels(self):
        """Create main application panels"""
        # Main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Database and table browser
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Database list
        ttk.Label(left_frame, text="Databases").pack(anchor=tk.W)
        self.db_listbox = tk.Listbox(left_frame, height=6)
        self.db_listbox.pack(fill=tk.X, pady=(0, 5))
        self.db_listbox.bind('<<ListboxSelect>>', self.on_database_select)
        self.db_listbox.bind('<Button-3>', self.show_database_context_menu)  # Right-click context menu
        
        # Table list
        ttk.Label(left_frame, text="Tables").pack(anchor=tk.W)
        self.table_listbox = tk.Listbox(left_frame)
        self.table_listbox.pack(fill=tk.BOTH, expand=True)
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        self.table_listbox.bind('<Double-Button-1>', self.on_table_double_click)
        
        # Right panel - Data display
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=4)
        
        # Table info
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.table_info_label = ttk.Label(info_frame, text="No table selected")
        self.table_info_label.pack(side=tk.LEFT)
        
        self.row_count_label = ttk.Label(info_frame, text="")
        self.row_count_label.pack(side=tk.RIGHT)
        
        # Treeview for data display
        self.create_data_display(right_frame)
        
    def create_data_display(self, parent):
        """Create the data display treeview with scrollbars"""
        # Frame for treeview and scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.data_tree = ttk.Treeview(tree_frame)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        
        self.data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.data_tree.grid(row=0, column=0, sticky=tk.NSEW)
        v_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        h_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_bar.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        self.root.update_idletasks()
        
    def open_database(self):
        """Open a database file"""
        filetypes = [
            ("All Supported", "*.db;*.sqlite;*.sqlite3;*.csv;*.xlsx;*.xls;*.json"),
            ("SQLite files", "*.db;*.sqlite;*.sqlite3"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx;*.xls"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Open Database or Data File",
            filetypes=filetypes
        )
        
        if filename:
            self.load_database_file(filename)
            
    def load_database_file(self, filename: str):
        """Load database file"""
        def load_db():
            try:
                self.update_status(f"Loading: {os.path.basename(filename)}")
                
                ext = os.path.splitext(filename)[1].lower()
                db_name = os.path.basename(filename)
                
                if ext in ['.db', '.sqlite', '.sqlite3']:
                    # SQLite database
                    conn = sqlite3.connect(filename, check_same_thread=False)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    db_info = {
                        'connection': conn,
                        'type': 'sqlite',
                        'path': filename,
                        'tables': tables
                    }
                    
                elif ext == '.csv':
                    # Ultra-fast CSV loading with Polars
                    self.status_label.config(text="🚀 Loading CSV with Polars ultra-speed...")
                    
                    def progress_callback(message, progress):
                        self.status_label.config(text=message)
                        self.root.update_idletasks()
                    
                    conn, table_name = self.polars_manager.load_csv_polars(filename, progress_callback)
                    
                    db_info = {
                        'connection': conn,
                        'type': 'sqlite',
                        'path': filename,
                        'filename': filename,  # For Polars cache access
                        'tables': [table_name]
                    }
                    
                elif ext in ['.xlsx', '.xls']:
                    # Ultra-fast Excel loading with Polars optimization
                    self.status_label.config(text="🚀 Loading Excel with Polars optimization...")
                    
                    def progress_callback(message, progress):
                        self.status_label.config(text=message)
                        self.root.update_idletasks()
                    
                    conn, table_names = self.polars_manager.load_excel_polars(filename, progress_callback)
                        
                    db_info = {
                        'connection': conn,
                        'type': 'sqlite',
                        'path': filename,
                        'filename': filename,  # For Polars cache access
                        'tables': table_names
                    }
                    
                elif ext == '.json':
                    # JSON file
                    conn = sqlite3.connect(':memory:', check_same_thread=False)
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                    elif isinstance(data, dict):
                        if all(isinstance(v, list) for v in data.values()):
                            df = pd.DataFrame(data)
                        else:
                            df = pd.DataFrame([data])
                    else:
                        raise ValueError("Unsupported JSON structure")
                    
                    table_name = os.path.splitext(os.path.basename(filename))[0].replace(' ', '_').replace('-', '_')
                    df.to_sql(table_name, conn, if_exists='replace', index=False)
                    
                    db_info = {
                        'connection': conn,
                        'type': 'sqlite',
                        'path': filename,
                        'tables': [table_name]
                    }
                    
                else:
                    raise ValueError(f"Unsupported file format: {ext}")
                
                # Update UI in main thread
                self.root.after(0, lambda: self.on_database_loaded(db_name, db_info))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load file: {str(e)}"))
                self.root.after(0, lambda: self.update_status("Ready"))
                
        threading.Thread(target=load_db, daemon=True).start()
        
    def on_database_loaded(self, db_name: str, db_info: dict):
        """Handle database loaded event"""
        self.connections[db_name] = db_info
        
        # Save database state for persistence
        self.config_manager.save_database_state(db_name, db_info)
        
        # Update recent files menu
        self.update_recent_files_menu()
        
        # Add to database list
        if db_name not in self.db_listbox.get(0, tk.END):
            self.db_listbox.insert(tk.END, db_name)
            
        # Select the database
        for i in range(self.db_listbox.size()):
            if self.db_listbox.get(i) == db_name:
                self.db_listbox.selection_clear(0, tk.END)
                self.db_listbox.selection_set(i)
                self.db_listbox.activate(i)
                break
                
        self.on_database_select(None)
        self.update_status(f"💾 Loaded & Saved: {db_name} ({len(db_info['tables'])} tables)")
        
    def on_database_select(self, event):
        """Handle database selection"""
        selection = self.db_listbox.curselection()
        if not selection:
            return
            
        db_name = self.db_listbox.get(selection[0])
        self.current_db = db_name
        
        if db_name in self.connections:
            tables = self.connections[db_name]['tables']
            self.update_table_list(tables)
            
    def update_table_list(self, tables: list):
        """Update table list in UI"""
        self.table_listbox.delete(0, tk.END)
        for table in sorted(tables):
            self.table_listbox.insert(tk.END, table)
            
    def on_table_select(self, event):
        """Handle table selection"""
        selection = self.table_listbox.curselection()
        if not selection:
            return
            
        table_name = self.table_listbox.get(selection[0])
        self.current_table = table_name
        
    def on_table_double_click(self, event):
        """Handle table double-click to load data"""
        selection = self.table_listbox.curselection()
        if not selection:
            return
            
        table_name = self.table_listbox.get(selection[0])
        self.current_table = table_name
        self.load_table_data(table_name)
        
    def load_table_data(self, table_name: str):
        """Load table data"""
        if not self.current_db or self.current_db not in self.connections:
            return
            
        def load_data():
            try:
                self.root.after(0, lambda: self.update_status(f"Loading table: {table_name}"))
                
                conn = self.connections[self.current_db]['connection']
                
                # Load data with limit for performance
                query = f"SELECT * FROM {table_name} LIMIT 5000"
                df = pd.read_sql_query(query, conn)
                
                # Get total row count
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                total_rows = cursor.fetchone()[0]
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_data(df, total_rows))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load table: {str(e)}"))
                self.root.after(0, lambda: self.update_status("Ready"))
                
        threading.Thread(target=load_data, daemon=True).start()
        
    def display_data(self, df: pd.DataFrame, total_rows: int):
        """Display data in treeview"""
        # Store current data
        self.current_data = df
        
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        # Configure columns
        columns = list(df.columns)
        self.data_tree['columns'] = columns
        self.data_tree['show'] = 'headings'
        
        # Configure column headings and widths
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100, minwidth=50)
            
        # Insert data
        for index, row in df.iterrows():
            values = [str(val) if pd.notna(val) else '' for val in row]
            self.data_tree.insert('', 'end', values=values)
            
        # Update info labels
        self.table_info_label.config(text=f"Table: {self.current_table}")
        
        displayed_rows = len(df)
        if displayed_rows < total_rows:
            self.row_count_label.config(text=f"Showing: {displayed_rows:,} of {total_rows:,} rows")
        else:
            self.row_count_label.config(text=f"Rows: {total_rows:,}")
            
        self.update_status(f"Loaded {len(df)} rows from {self.current_table}")
        
    def search_data(self, event=None):
        """Search data in current table or across all databases"""
        search_term = self.search_var.get().strip()
        if not search_term:
            return
            
        # Check if global search is enabled
        if self.global_search_var.get():
            self.perform_global_search(search_term)
        else:
            self.perform_local_search(search_term)
    
    def perform_local_search(self, search_term: str):
        """Search data in current table only"""
        if self.current_data is None:
            return
            
        # Simple search in displayed data
        mask = self.current_data.astype(str).apply(
            lambda x: x.str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        
        filtered_df = self.current_data[mask]
        
        # Clear and update treeview
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        # Insert filtered data
        for index, row in filtered_df.iterrows():
            values = [str(val) if pd.notna(val) else '' for val in row]
            self.data_tree.insert('', 'end', values=values)
            
        self.row_count_label.config(text=f"Search results: {len(filtered_df)} rows")
        self.update_status(f"Search completed: {len(filtered_df)} results")
    
    def perform_global_search(self, search_term: str):
        """Ultra-fast search across all loaded databases using Polars"""
        if not self.connections:
            messagebox.showinfo("Global Search", "No databases loaded for global search.")
            return
            
        def global_search_thread():
            try:
                self.update_status(f"🚀 Ultra-fast search for: {search_term}")
                
                # Progress callback
                def progress_callback(message, progress):
                    self.root.after(0, lambda: self.update_status(message))
                
                # Use Polars ultra-fast global search
                search_results = self.polars_manager.ultra_parallel_global_search(
                    self.connections, search_term, progress_callback
                )
                
                # Format results for display
                all_results = search_results['matches']
                
                # Create enhanced summary
                search_summary = []
                if search_results['total_matches'] > 0:
                    search_summary.append(f"🎯 Found {search_results['total_matches']} total matches")
                    search_summary.append(f"⚡ Searched {search_results['tables_searched']} tables in {search_results['databases_searched']} databases")
                    search_summary.append("")
                    
                    for result in search_results['summary']:
                        search_summary.append(f"📋 {result['database']}.{result['table']}: {result['match_count']} matches")
                    
                    # Add performance info
                    perf_stats = self.polars_manager.get_performance_stats()
                    search_summary.extend([
                        "",
                        "🚀 Performance:",
                        f"  ⚡ Polars tables: {perf_stats['polars_cached_tables']}",
                        f"  💾 Memory: {perf_stats['polars_memory_usage_mb']:.1f} MB"
                    ])
                else:
                    search_summary.append(f"❌ No matches found for '{search_term}'")
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_global_results(all_results, search_summary, search_term))
                
            except Exception as e:
                error_msg = f"Ultra-fast search failed: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                
        threading.Thread(target=global_search_thread, daemon=True).start()
    
    def display_global_results(self, all_results, search_summary, search_term):
        """Display global search results with enhanced user interface"""
        # Clear treeview
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        if all_results:
            # Combine all results
            combined_results = pd.concat(all_results, ignore_index=True, sort=False)
            
            # Reorder columns for better user experience
            columns = list(combined_results.columns)
            user_friendly_columns = []
            
            # Add metadata columns with better names
            if '_database' in columns:
                user_friendly_columns.append('📁 Database')
                columns.remove('_database')
            if '_table' in columns:
                user_friendly_columns.append('📋 Table')
                columns.remove('_table')
            
            # Add separator
            user_friendly_columns.append('│')
            
            # Add data columns
            user_friendly_columns.extend(columns)
            
            # Update treeview
            self.data_tree["columns"] = user_friendly_columns
            self.data_tree["show"] = "headings"
            
            # Configure column headers
            for i, col in enumerate(user_friendly_columns):
                self.data_tree.heading(col, text=col)
                if col in ['📁 Database', '📋 Table']:
                    self.data_tree.column(col, width=140, minwidth=100)
                elif col == '│':
                    self.data_tree.column(col, width=20, minwidth=20)
                else:
                    self.data_tree.column(col, width=120, minwidth=80)
            
            # Insert data with enhanced formatting
            display_rows = min(len(combined_results), 2000)
            for index in range(display_rows):
                row = combined_results.iloc[index]
                friendly_values = []
                
                # Database name (clean display)
                if '_database' in combined_results.columns:
                    db_name = str(row['_database'])
                    if '.' in db_name:
                        db_name = db_name.split('.')[0]
                    friendly_values.append(db_name)
                
                # Table name
                if '_table' in combined_results.columns:
                    friendly_values.append(str(row['_table']))
                
                # Separator
                friendly_values.append('│')
                
                # Data values
                for col in [c for c in combined_results.columns if c not in ['_database', '_table']]:
                    val = row[col]
                    str_val = str(val) if pd.notna(val) else ''
                    # Highlight search matches
                    if search_term.lower() in str_val.lower():
                        friendly_values.append(f"🔍 {str_val}")
                    else:
                        friendly_values.append(str_val)
                
                # Alternating colors
                tag = 'even' if index % 2 == 0 else 'odd'
                self.data_tree.insert('', 'end', values=friendly_values, tags=(tag,))
            
            # Configure alternating row colors
            self.data_tree.tag_configure('even', background='#f8f9fa')
            self.data_tree.tag_configure('odd', background='white')
            
            # Enhanced status display
            match_count = len(combined_results)
            db_count = combined_results['_database'].nunique() if '_database' in combined_results.columns else 0
            table_count = len(search_summary)
            
            self.table_info_label.config(text=f"🔍 Global Search: '{search_term}'")
            self.row_count_label.config(text=f"Found {match_count:,} matches in {table_count} tables from {db_count} databases")
            
            # Enhanced summary dialog
            enhanced_summary = self.create_enhanced_summary(search_summary, search_term, match_count, db_count, table_count)
            messagebox.showinfo("🔍 Global Search Results", enhanced_summary)
            
        else:
            self.table_info_label.config(text="🔍 Global Search - No Results")
            self.row_count_label.config(text="No matches found in any database")
            messagebox.showinfo("Search Results", f"No matches found for '{search_term}' in any loaded database.")
            
        self.update_status(f"Global search completed: {len(all_results) if all_results else 0} total results")
    
    def create_enhanced_summary(self, search_summary, search_term, match_count, db_count, table_count):
        """Create an enhanced summary text"""
        summary_lines = [
            f"Search Term: '{search_term}'",
            f"",
            f"📊 SUMMARY:",
            f"  • Total Matches: {match_count:,}",
            f"  • Databases: {db_count}",
            f"  • Tables with Results: {table_count}",
            f"",
            f"📋 DETAILED RESULTS:",
        ]
        
        for result in search_summary:
            summary_lines.append(f"  • {result}")
        
        return "\n".join(summary_lines)
        
    def refresh_current_table(self):
        """Refresh current table data"""
        if self.current_table:
            self.load_table_data(self.current_table)
            
    def import_csv(self):
        """Import CSV file"""
        filename = filedialog.askopenfilename(
            title="Import CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.load_database_file(filename)
            
    def import_excel(self):
        """Import Excel file"""
        filename = filedialog.askopenfilename(
            title="Import Excel File",
            filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")]
        )
        if filename:
            self.load_database_file(filename)
            
    def import_json(self):
        """Import JSON file"""
        filename = filedialog.askopenfilename(
            title="Import JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.load_database_file(filename)
            
    def export_table(self):
        """Export current table"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data to export")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export Table",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("JSON files", "*.json")
            ]
        )
        
        if filename:
            self.export_data_to_file(filename)
            
    def export_data_to_file(self, filename: str):
        """Export data to file"""
        def export():
            try:
                self.root.after(0, lambda: self.update_status(f"Exporting: {os.path.basename(filename)}"))
                
                ext = os.path.splitext(filename)[1].lower()
                if ext == '.csv':
                    self.current_data.to_csv(filename, index=False)
                elif ext == '.xlsx':
                    self.current_data.to_excel(filename, index=False)
                elif ext == '.json':
                    self.current_data.to_json(filename, orient='records', indent=2)
                    
                self.root.after(0, lambda: self.update_status(f"Exported: {os.path.basename(filename)}"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Export failed: {str(e)}"))
                
        threading.Thread(target=export, daemon=True).start()
    
    def save_all_database_states(self):
        """Save all current database states"""
        try:
            count = 0
            for db_name, db_info in self.connections.items():
                self.config_manager.save_database_state(db_name, db_info)
                count += 1
            
            messagebox.showinfo("Database State Saved", 
                              f"✅ Saved state for {count} databases.\n"
                              f"They will be restored on next startup.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save database states: {e}")
    
    def restore_saved_databases(self):
        """Restore previously saved databases"""
        if not self.config_manager.should_auto_reconnect():
            return
            
        saved_databases = self.config_manager.get_saved_databases()
        
        if not saved_databases:
            return
            
        def restore_thread():
            restored_count = 0
            for db_name, db_state in saved_databases.items():
                try:
                    filepath = db_state['path']
                    if os.path.exists(filepath):
                        self.root.after(0, lambda: self.update_status(f"🔄 Restoring: {db_name}..."))
                        self.load_database_file(filepath)
                        restored_count += 1
                except Exception as e:
                    print(f"Failed to restore database {db_name}: {e}")
                    self.config_manager.remove_database_state(db_name)
            
            if restored_count > 0:
                self.root.after(0, lambda: self.update_status(f"✅ Restored {restored_count} databases"))
            else:
                self.root.after(0, lambda: self.update_status("Ready"))
        
        threading.Thread(target=restore_thread, daemon=True).start()
    
    def update_recent_files_menu(self):
        """Update the recent files menu"""
        self.recent_menu.delete(0, tk.END)
        
        recent_files = self.config_manager.get_recent_files()
        
        if not recent_files:
            self.recent_menu.add_command(label="(No recent files)", state="disabled")
            return
        
        for i, filepath in enumerate(recent_files[:10]):
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                if len(filename) > 50:
                    filename = filename[:47] + "..."
                
                self.recent_menu.add_command(
                    label=f"{i+1}. {filename}",
                    command=lambda path=filepath: self.load_database_file(path)
                )
    
    def show_database_context_menu(self, event):
        """Show context menu for database listbox on right-click"""
        # Select the item under cursor
        index = self.db_listbox.nearest(event.y)
        if index >= 0:
            self.db_listbox.selection_clear(0, tk.END)
            self.db_listbox.selection_set(index)
            self.db_listbox.activate(index)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="❌ Remove Database", command=self.remove_selected_database)
            context_menu.add_separator()
            context_menu.add_command(label="🔄 Reload Database", command=self.reload_selected_database)
            
            # Show context menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def remove_selected_database(self):
        """Remove the currently selected database"""
        selection = self.db_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a database to remove.")
            return
        
        db_name = self.db_listbox.get(selection[0])
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Remove Database", 
            f"Remove database '{db_name}' from the application?\n\n"
            f"⚠️ This will:\n"
            f"• Close the database connection\n"
            f"• Remove it from the database list\n"
            f"• Remove it from saved history\n"
            f"• Clear any displayed data\n\n"
            f"The original file will NOT be deleted.",
            icon='warning'
        )
        
        if not result:
            return
        
        try:
            # Close database connection if exists
            if db_name in self.connections:
                db_info = self.connections[db_name]
                if 'connection' in db_info and db_info['connection']:
                    try:
                        db_info['connection'].close()
                    except Exception as e:
                        print(f"Error closing connection for {db_name}: {e}")
                
                # Remove from connections dict
                del self.connections[db_name]
            
            # Remove from config/saved state
            self.config_manager.remove_database_state(db_name)
            
            # Remove from listbox
            self.db_listbox.delete(selection[0])
            
            # Clear UI if this was the current database
            if self.current_db == db_name:
                self.current_db = None
                self.current_table = None
                self.current_data = None
                
                # Clear table list
                self.table_listbox.delete(0, tk.END)
                
                # Clear data display
                for item in self.data_tree.get_children():
                    self.data_tree.delete(item)
            
            # Update recent files menu
            self.update_recent_files_menu()
            
            self.update_status(f"✅ Removed database: {db_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove database: {str(e)}")
    
    def reload_selected_database(self):
        """Reload the currently selected database"""
        selection = self.db_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a database to reload.")
            return
        
        db_name = self.db_listbox.get(selection[0])
        
        if db_name in self.connections:
            db_info = self.connections[db_name]
            if 'path' in db_info and os.path.exists(db_info['path']):
                # Remove current database first
                try:
                    if 'connection' in db_info and db_info['connection']:
                        db_info['connection'].close()
                except:
                    pass
                
                # Remove from UI
                self.db_listbox.delete(selection[0])
                del self.connections[db_name]
                
                # Reload the database
                self.load_database_file(db_info['path'])
                self.update_status(f"🔄 Reloading: {db_name}")
            else:
                messagebox.showerror("Error", f"Database file not found: {db_info.get('path', 'Unknown path')}")
        else:
            messagebox.showwarning("Error", f"Database '{db_name}' not found in loaded databases.")
    
    def remove_all_databases(self):
        """Remove all loaded databases (with confirmation)"""
        if not self.connections:
            messagebox.showinfo("No Databases", "No databases are currently loaded.")
            return
        
        result = messagebox.askyesno(
            "Remove All Databases",
            f"⚠️ Remove ALL {len(self.connections)} loaded databases?\n\n"
            f"This will:\n"
            f"• Close all database connections\n"
            f"• Clear the database list\n"
            f"• Clear all displayed data\n"
            f"• Remove from saved history\n\n"
            f"Original files will NOT be deleted.",
            icon='warning'
        )
        
        if not result:
            return
        
        try:
            # Close all connections
            for db_name, db_info in self.connections.items():
                if 'connection' in db_info and db_info['connection']:
                    try:
                        db_info['connection'].close()
                    except:
                        pass
                
                # Remove from saved state
                self.config_manager.remove_database_state(db_name)
            
            # Clear all data
            self.connections.clear()
            self.db_listbox.delete(0, tk.END)
            self.table_listbox.delete(0, tk.END)
            
            # Clear data display
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            # Reset current selections
            self.current_db = None
            self.current_table = None
            self.current_data = None
            
            # Update recent files menu
            self.update_recent_files_menu()
            
            self.update_status("✅ Removed all databases")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove all databases: {str(e)}")
    
    def on_closing(self):
        """Handle application closing - save state"""
        try:
            # Save all database states
            for db_name, db_info in self.connections.items():
                self.config_manager.save_database_state(db_name, db_info)
            
            # Close connections
            for db_info in self.connections.values():
                if 'connection' in db_info:
                    try:
                        db_info['connection'].close()
                    except:
                        pass
        except Exception as e:
            print(f"Error during shutdown: {e}")
        
        self.root.destroy()
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleDatabaseBrowser()
    app.run()
