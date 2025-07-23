#!/usr/bin/env python3
"""
ShadowHawk Database Browser - Simple Version
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

try:
    from ttkthemes import ThemedTk
    THEMED_TK_AVAILABLE = True
except ImportError:
    THEMED_TK_AVAILABLE = False

class SimpleDatabaseBrowser:
    """Simple database browser with essential functionality"""
    
    def __init__(self):
        # Initialize main window
        if THEMED_TK_AVAILABLE:
            self.root = ThemedTk(theme="arc")
        else:
            self.root = tk.Tk()
            
        self.root.title("ShadowHawk Database Browser - Simple")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Database connections and data
        self.connections = {}
        self.current_db = None
        self.current_table = None
        self.current_data = None
        
        # Setup UI
        self.setup_ui()
        
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
        file_menu.add_command(label="Export Current Table", command=self.export_table)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
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
                    # CSV file
                    conn = sqlite3.connect(':memory:', check_same_thread=False)
                    df = pd.read_csv(filename)
                    table_name = os.path.splitext(os.path.basename(filename))[0].replace(' ', '_').replace('-', '_')
                    df.to_sql(table_name, conn, if_exists='replace', index=False)
                    
                    db_info = {
                        'connection': conn,
                        'type': 'sqlite',
                        'path': filename,
                        'tables': [table_name]
                    }
                    
                elif ext in ['.xlsx', '.xls']:
                    # Excel file
                    conn = sqlite3.connect(':memory:', check_same_thread=False)
                    excel_file = pd.ExcelFile(filename)
                    tables = []
                    
                    base_name = os.path.splitext(os.path.basename(filename))[0]
                    for sheet_name in excel_file.sheet_names:
                        df = pd.read_excel(filename, sheet_name=sheet_name)
                        table_name = f"{base_name}_{sheet_name}".replace(' ', '_').replace('-', '_')
                        df.to_sql(table_name, conn, if_exists='replace', index=False)
                        tables.append(table_name)
                        
                    db_info = {
                        'connection': conn,
                        'type': 'sqlite',
                        'path': filename,
                        'tables': tables
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
        self.update_status(f"Loaded: {db_name} ({len(db_info['tables'])} tables)")
        
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
        """Search across all loaded databases and tables"""
        if not self.connections:
            messagebox.showinfo("Global Search", "No databases loaded for global search.")
            return
            
        def global_search_thread():
            try:
                self.update_status(f"Searching all databases for: {search_term}")
                
                all_results = []
                search_summary = []
                
                for db_name, db_info in self.connections.items():
                    connection = db_info['connection']
                    tables = db_info.get('tables', [])
                    
                    # If no tables info stored, get them from connection
                    if not tables:
                        try:
                            cursor = connection.cursor()
                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                            tables = [row[0] for row in cursor.fetchall()]
                        except Exception as e:
                            print(f"Error getting tables for {db_name}: {e}")
                            continue
                    
                    for table_name in tables:
                        try:
                            # Load table data
                            df = pd.read_sql_query(f"SELECT * FROM {table_name}", connection)
                            
                            # Search in this table
                            mask = df.astype(str).apply(
                                lambda x: x.str.contains(search_term, case=False, na=False)
                            ).any(axis=1)
                            
                            matches = df[mask]
                            
                            if len(matches) > 0:
                                # Add database and table info to each row
                                matches = matches.copy()
                                matches.insert(0, '_database', db_name)
                                matches.insert(1, '_table', table_name)
                                all_results.append(matches)
                                search_summary.append(f"{db_name}.{table_name}: {len(matches)} matches")
                                
                        except Exception as e:
                            print(f"Error searching table {db_name}.{table_name}: {e}")
                            continue
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_global_results(all_results, search_summary, search_term))
                
            except Exception as e:
                error_msg = f"Global search failed: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                
        threading.Thread(target=global_search_thread, daemon=True).start()
    
    def display_global_results(self, all_results, search_summary, search_term):
        """Display global search results"""
        # Clear treeview
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        if all_results:
            # Combine all results
            combined_results = pd.concat(all_results, ignore_index=True, sort=False)
            
            # Update treeview columns to include database and table info
            columns = list(combined_results.columns)
            self.data_tree["columns"] = columns
            self.data_tree["show"] = "headings"
            
            # Configure column headers
            for col in columns:
                self.data_tree.heading(col, text=col)
                if col in ['_database', '_table']:
                    self.data_tree.column(col, width=120, minwidth=80)
                else:
                    self.data_tree.column(col, width=100, minwidth=50)
            
            # Insert data (limit to 2000 rows for performance in simple browser)
            display_rows = min(len(combined_results), 2000)
            for index in range(display_rows):
                row = combined_results.iloc[index]
                values = [str(val) if pd.notna(val) else '' for val in row]
                self.data_tree.insert('', 'end', values=values)
            
            # Update status
            self.table_info_label.config(text="Global Search Results")
            self.row_count_label.config(text=f"Found: {len(combined_results):,} matches across all databases")
            
            # Show summary
            summary_text = f"Global search found {len(combined_results)} total matches in {len(search_summary)} tables:\n" + "\n".join(search_summary)
            messagebox.showinfo("Global Search Results", summary_text)
            
        else:
            self.row_count_label.config(text="No matches found in any database")
            
        self.update_status(f"Global search completed: {len(all_results) if all_results else 0} total results")
        
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
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleDatabaseBrowser()
    app.run()
