import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pandas as pd
import threading
import os
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
try:
    from ttkthemes import ThemedTk
    THEMED_TK_AVAILABLE = True
except ImportError:
    THEMED_TK_AVAILABLE = False

class DatabaseBrowser:
    def __init__(self):
        # Initialize main window
        if THEMED_TK_AVAILABLE:
            self.root = ThemedTk(theme="arc")
        else:
            self.root = tk.Tk()
            
        self.root.title("ShadowHawk Database Browser")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Database connections and data
        self.connections: Dict[str, Any] = {}
        self.current_db = None
        self.current_table = None
        self.data_cache = {}
        
        # Setup UI
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Create main containers
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
        file_menu.add_separator()
        file_menu.add_command(label="Export Current Table", command=self.export_table)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self.refresh_current_table)
        view_menu.add_command(label="Clear Cache", command=self.clear_cache)
        
    def create_toolbar(self):
        """Create toolbar with common actions"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Database operations
        ttk.Button(toolbar, text="Open DB", command=self.open_database).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Import CSV", command=self.import_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Import Excel", command=self.import_excel).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Data operations
        ttk.Button(toolbar, text="Refresh", command=self.refresh_current_table).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export", command=self.export_table).pack(side=tk.LEFT, padx=2)
        
        # Search
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
        
        # Right panel - Data display
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=4)
        
        # Data display area
        data_frame = ttk.Frame(right_frame)
        data_frame.pack(fill=tk.BOTH, expand=True)
        
        # Table info
        info_frame = ttk.Frame(data_frame)
        info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.table_info_label = ttk.Label(info_frame, text="No table selected")
        self.table_info_label.pack(side=tk.LEFT)
        
        self.row_count_label = ttk.Label(info_frame, text="")
        self.row_count_label.pack(side=tk.RIGHT)
        
        # Treeview for data display
        self.create_data_display(data_frame)
        
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
        
    def setup_bindings(self):
        """Setup keyboard bindings"""
        self.root.bind('<Control-o>', lambda e: self.open_database())
        self.root.bind('<F5>', lambda e: self.refresh_current_table())
        
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_bar.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        self.root.update_idletasks()
        
    def open_database(self):
        """Open a database file"""
        filetypes = [
            ("All Supported", "*.db;*.sqlite;*.sqlite3"),
            ("SQLite files", "*.db;*.sqlite;*.sqlite3"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Open Database",
            filetypes=filetypes
        )
        
        if filename:
            self.load_database(filename)
            
    def load_database(self, filename: str):
        """Load database in a separate thread"""
        def load_db():
            try:
                self.update_status(f"Loading database: {os.path.basename(filename)}")
                
                # Connect to database
                conn = sqlite3.connect(filename)
                db_name = os.path.basename(filename)
                
                # Store connection
                self.connections[db_name] = {
                    'connection': conn,
                    'path': filename,
                    'type': 'sqlite'
                }
                
                # Update UI in main thread
                self.root.after(0, lambda: self.on_database_loaded(db_name))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load database: {str(e)}"))
                self.root.after(0, lambda: self.update_status("Ready"))
                
        threading.Thread(target=load_db, daemon=True).start()
        
    def on_database_loaded(self, db_name: str):
        """Handle database loaded event"""
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
        self.update_status(f"Database loaded: {db_name}")
        
    def on_database_select(self, event):
        """Handle database selection"""
        selection = self.db_listbox.curselection()
        if not selection:
            return
            
        db_name = self.db_listbox.get(selection[0])
        self.current_db = db_name
        
        # Load tables
        self.load_tables()
        
    def load_tables(self):
        """Load tables for selected database"""
        if not self.current_db or self.current_db not in self.connections:
            return
            
        def load_tables_thread():
            try:
                conn = self.connections[self.current_db]['connection']
                
                # Get table list
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Update UI in main thread
                self.root.after(0, lambda: self.update_table_list(tables))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load tables: {str(e)}"))
                
        threading.Thread(target=load_tables_thread, daemon=True).start()
        
    def update_table_list(self, tables: List[str]):
        """Update table list in UI"""
        self.table_listbox.delete(0, tk.END)
        for table in tables:
            self.table_listbox.insert(tk.END, table)
            
    def on_table_select(self, event):
        """Handle table selection"""
        selection = self.table_listbox.curselection()
        if not selection:
            return
            
        table_name = self.table_listbox.get(selection[0])
        self.current_table = table_name
        self.load_table_data(table_name)
        
    def load_table_data(self, table_name: str, limit: int = 1000):
        """Load table data"""
        if not self.current_db or self.current_db not in self.connections:
            return
            
        def load_data_thread():
            try:
                self.root.after(0, lambda: self.update_status(f"Loading table: {table_name}"))
                
                conn = self.connections[self.current_db]['connection']
                
                # Get column info
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Get data with limit for performance
                query = f"SELECT * FROM {table_name} LIMIT {limit}"
                df = pd.read_sql_query(query, conn)
                
                # Get total row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                total_rows = cursor.fetchone()[0]
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_data(df, columns, total_rows, limit))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load table data: {str(e)}"))
                self.root.after(0, lambda: self.update_status("Ready"))
                
        threading.Thread(target=load_data_thread, daemon=True).start()
        
    def display_data(self, df: pd.DataFrame, columns: List[str], total_rows: int, displayed_rows: int):
        """Display data in treeview"""
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        # Configure columns
        self.data_tree['columns'] = columns
        self.data_tree['show'] = 'headings'
        
        # Configure column headings and widths
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100, minwidth=50)
            
        # Insert data
        for index, row in df.iterrows():
            values = [str(val) if val is not None else '' for val in row]
            self.data_tree.insert('', 'end', values=values)
            
        # Update info labels
        self.table_info_label.config(text=f"Table: {self.current_table}")
        
        if displayed_rows >= total_rows:
            self.row_count_label.config(text=f"Rows: {total_rows}")
        else:
            self.row_count_label.config(text=f"Rows: {displayed_rows} of {total_rows} (limited)")
            
        self.update_status(f"Loaded {len(df)} rows from {self.current_table}")
        
    def import_csv(self):
        """Import CSV file to database"""
        filename = filedialog.askopenfilename(
            title="Import CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            self.import_csv_file(filename)
            
    def import_csv_file(self, filename: str):
        """Import CSV file in separate thread"""
        def import_thread():
            try:
                self.root.after(0, lambda: self.update_status(f"Importing CSV: {os.path.basename(filename)}"))
                
                # Read CSV
                df = pd.read_csv(filename)
                
                # Create in-memory database if none exists
                if not self.connections:
                    conn = sqlite3.connect(':memory:')
                    db_name = "Memory Database"
                    self.connections[db_name] = {
                        'connection': conn,
                        'path': ':memory:',
                        'type': 'sqlite'
                    }
                    self.root.after(0, lambda: self.on_database_loaded(db_name))
                
                # Use current database
                conn = list(self.connections.values())[0]['connection']
                
                # Create table name from filename
                table_name = os.path.splitext(os.path.basename(filename))[0]
                table_name = table_name.replace(' ', '_').replace('-', '_')
                
                # Import to database
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                
                self.root.after(0, lambda: self.on_csv_imported(table_name))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to import CSV: {str(e)}"))
                self.root.after(0, lambda: self.update_status("Ready"))
                
        threading.Thread(target=import_thread, daemon=True).start()
        
    def on_csv_imported(self, table_name: str):
        """Handle CSV import completion"""
        self.load_tables()  # Refresh table list
        self.update_status(f"CSV imported as table: {table_name}")
        
    def import_excel(self):
        """Import Excel file"""
        filename = filedialog.askopenfilename(
            title="Import Excel File",
            filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")]
        )
        
        if filename:
            self.import_excel_file(filename)
            
    def import_excel_file(self, filename: str):
        """Import Excel file in separate thread"""
        def import_thread():
            try:
                self.root.after(0, lambda: self.update_status(f"Importing Excel: {os.path.basename(filename)}"))
                
                # Read Excel - all sheets
                excel_file = pd.ExcelFile(filename)
                
                # Create in-memory database if none exists
                if not self.connections:
                    conn = sqlite3.connect(':memory:')
                    db_name = "Memory Database"
                    self.connections[db_name] = {
                        'connection': conn,
                        'path': ':memory:',
                        'type': 'sqlite'
                    }
                    self.root.after(0, lambda: self.on_database_loaded(db_name))
                
                conn = list(self.connections.values())[0]['connection']
                
                # Import each sheet
                imported_tables = []
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(filename, sheet_name=sheet_name)
                    table_name = f"{os.path.splitext(os.path.basename(filename))[0]}_{sheet_name}"
                    table_name = table_name.replace(' ', '_').replace('-', '_')
                    
                    df.to_sql(table_name, conn, if_exists='replace', index=False)
                    imported_tables.append(table_name)
                
                self.root.after(0, lambda: self.on_excel_imported(imported_tables))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to import Excel: {str(e)}"))
                self.root.after(0, lambda: self.update_status("Ready"))
                
        threading.Thread(target=import_thread, daemon=True).start()
        
    def on_excel_imported(self, table_names: List[str]):
        """Handle Excel import completion"""
        self.load_tables()  # Refresh table list
        self.update_status(f"Excel imported as {len(table_names)} tables")
        
    def export_table(self):
        """Export current table"""
        if not self.current_table or not self.current_db:
            messagebox.showwarning("Warning", "No table selected")
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
            self.export_table_file(filename)
            
    def export_table_file(self, filename: str):
        """Export table to file"""
        def export_thread():
            try:
                self.root.after(0, lambda: self.update_status(f"Exporting table: {self.current_table}"))
                
                conn = self.connections[self.current_db]['connection']
                df = pd.read_sql_query(f"SELECT * FROM {self.current_table}", conn)
                
                # Export based on file extension
                ext = os.path.splitext(filename)[1].lower()
                if ext == '.csv':
                    df.to_csv(filename, index=False)
                elif ext == '.xlsx':
                    df.to_excel(filename, index=False)
                elif ext == '.json':
                    df.to_json(filename, orient='records', indent=2)
                    
                self.root.after(0, lambda: self.update_status(f"Table exported: {os.path.basename(filename)}"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to export table: {str(e)}"))
                self.root.after(0, lambda: self.update_status("Ready"))
                
        threading.Thread(target=export_thread, daemon=True).start()
        
    def search_data(self, event=None):
        """Search data in current table"""
        search_term = self.search_var.get().strip()
        if not search_term or not self.current_table or not self.current_db:
            return
            
        def search_thread():
            try:
                conn = self.connections[self.current_db]['connection']
                
                # Get column names
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({self.current_table})")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Build search query
                where_clauses = []
                for col in columns:
                    where_clauses.append(f"{col} LIKE ?")
                
                where_clause = " OR ".join(where_clauses)
                query = f"SELECT * FROM {self.current_table} WHERE {where_clause} LIMIT 1000"
                
                # Execute search
                search_pattern = f"%{search_term}%"
                params = [search_pattern] * len(columns)
                
                df = pd.read_sql_query(query, conn, params=params)
                
                # Update UI
                self.root.after(0, lambda: self.display_search_results(df, columns, search_term))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Search failed: {str(e)}"))
                
        threading.Thread(target=search_thread, daemon=True).start()
        
    def display_search_results(self, df: pd.DataFrame, columns: List[str], search_term: str):
        """Display search results"""
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        # Insert search results
        for index, row in df.iterrows():
            values = [str(val) if val is not None else '' for val in row]
            self.data_tree.insert('', 'end', values=values)
            
        self.row_count_label.config(text=f"Search results: {len(df)} rows")
        self.update_status(f"Search completed for '{search_term}': {len(df)} results")
        
    def refresh_current_table(self):
        """Refresh current table data"""
        if self.current_table:
            self.load_table_data(self.current_table)
            
    def clear_cache(self):
        """Clear data cache"""
        self.data_cache.clear()
        self.update_status("Cache cleared")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DatabaseBrowser()
    app.run()
