import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

import threading
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Import our custom modules
from polars_database_utils import PolarsDatabaseManager
from config_manager import ConfigManager

try:
    from ttkthemes import ThemedTk
    THEMED_TK_AVAILABLE = True
except ImportError:
    THEMED_TK_AVAILABLE = False

class ShadowHawkBrowser:
    """Enhanced database browser with modern GUI and fast performance"""
    
    def __init__(self):
        # Initialize main window
        if THEMED_TK_AVAILABLE:
            self.root = ThemedTk(theme="arc")
        else:
            self.root = tk.Tk()
            
        self.root.title("ShadowHawk Database Browser v1.0.0")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Set window class name for better Windows taskbar recognition
        try:
            self.root.wm_class("ShadowHawk", "ShadowHawk Database Browser")
        except:
            pass
        
        # Set application icon with multiple methods for maximum compatibility
        self._set_application_icon()
        
        # Try Windows-specific taskbar integration
        self._setup_windows_taskbar()
            
        # Initialize managers
        self.config_manager = ConfigManager()  # Configuration and persistence manager
        self.polars_manager = PolarsDatabaseManager()  # Ultra-fast Polars manager
        
        # Application state
        self.databases: Dict[str, Any] = {}
        self.current_db = None
        self.current_table = None
        self.current_data = None
        self.filtered_data = None
        
        # Performance settings
        self.max_display_rows = 10000
        self.chunk_size = 1000
        
        # Setup UI
        self.setup_styles()
        self.setup_ui()
        self.setup_bindings()
        
        # Load settings and restore databases
        self.load_settings()
        self.restore_saved_databases()
        
        # Setup close handler for saving state
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """Setup custom styles for better appearance"""
        style = ttk.Style()
        
        # Configure treeview for better readability
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Segoe UI', 9, 'bold'))
        
    def setup_ui(self):
        """Setup the main UI components"""
        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()
        self.create_status_bar()
        
    def create_menu(self):
        """Create enhanced menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Database...", command=self.open_database, accelerator="Ctrl+O")
        file_menu.add_separator()
        
        import_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Import", menu=import_menu)
        import_menu.add_command(label="CSV File...", command=self.import_csv)
        import_menu.add_command(label="Excel File...", command=self.import_excel)
        import_menu.add_command(label="JSON File...", command=self.import_json)
        
        export_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="Current Table...", command=self.export_table)
        export_menu.add_command(label="Filtered Data...", command=self.export_filtered)
        
        file_menu.add_separator()
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="📁 Recent Files", menu=self.recent_menu)
        self.update_recent_files_menu()
        
        # Database management
        file_menu.add_separator()
        file_menu.add_command(label="💾 Save Database State", command=self.save_all_database_states)
        file_menu.add_command(label="🔄 Restore Saved Databases", command=self.restore_saved_databases)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Remove Selected Database", command=self.remove_selected_database)
        file_menu.add_command(label="🗑️ Remove All Databases", command=self.remove_all_databases)
        file_menu.add_command(label="🧹 Clear Database History", command=self.clear_database_history)
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find...", command=self.focus_search, accelerator="Ctrl+F")
        edit_menu.add_command(label="Clear Search", command=self.clear_search)
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy Selected", command=self.copy_selected, accelerator="Ctrl+C")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self.refresh_current_table, accelerator="F5")
        view_menu.add_command(label="Show Column Stats", command=self.show_column_stats)
        view_menu.add_separator()
        view_menu.add_command(label="Increase Font Size", command=self.increase_font)
        view_menu.add_command(label="Decrease Font Size", command=self.decrease_font)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="SQL Query...", command=self.open_sql_query)
        tools_menu.add_command(label="Data Statistics", command=self.show_data_stats)
        tools_menu.add_separator()
        tools_menu.add_command(label="Settings...", command=self.open_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_toolbar(self):
        """Create enhanced toolbar"""
        # Main toolbar frame
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # File operations
        file_frame = ttk.LabelFrame(toolbar_frame, text="File", padding=5)
        file_frame.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(file_frame, text="Open DB", command=self.open_database, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(file_frame, text="Import", command=self.show_import_menu, width=8).pack(side=tk.LEFT, padx=1)
        
        # Data operations
        data_frame = ttk.LabelFrame(toolbar_frame, text="Data", padding=5)
        data_frame.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(data_frame, text="Refresh", command=self.refresh_current_table, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(data_frame, text="Export", command=self.export_table, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(data_frame, text="Stats", command=self.show_data_stats, width=8).pack(side=tk.LEFT, padx=1)
        
        # Search frame
        search_frame = ttk.LabelFrame(toolbar_frame, text="🔍 Search", padding=5)
        search_frame.pack(side=tk.RIGHT, padx=2)
        
        # Global search toggle with better styling
        self.global_search_var = tk.BooleanVar()
        global_search_cb = ttk.Checkbutton(search_frame, text="🌐 Search All DBs", 
                                         variable=self.global_search_var,
                                         command=self.on_global_search_toggle)
        global_search_cb.pack(side=tk.LEFT, padx=2)
        
        # Search entry with placeholder-like behavior
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=2)
        self.search_entry.bind('<Return>', self.search_data)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        self.search_entry.bind('<FocusIn>', self.on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self.on_search_focus_out)
        
        # Initialize placeholder text
        self.search_placeholder = "Enter search term..."
        self.search_entry.insert(0, self.search_placeholder)
        self.search_entry.config(foreground='gray')
        
        ttk.Button(search_frame, text="🔍", command=self.search_data, width=3).pack(side=tk.LEFT, padx=1)
        ttk.Button(search_frame, text="❌", command=self.clear_search, width=3).pack(side=tk.LEFT, padx=1)
        
    def create_main_layout(self):
        """Create main application layout"""
        # Main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel
        self.create_left_panel(main_paned)
        
        # Right panel
        self.create_right_panel(main_paned)
        
        # Set initial pane sizes
        self.root.after(100, lambda: main_paned.sashpos(0, 300))
        
    def create_left_panel(self, parent):
        """Create left panel with database and table browser"""
        left_frame = ttk.Frame(parent)
        parent.add(left_frame, weight=1)
        
        # Database section
        db_label_frame = ttk.LabelFrame(left_frame, text="Databases", padding=5)
        db_label_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Database listbox with scrollbar
        db_frame = ttk.Frame(db_label_frame)
        db_frame.pack(fill=tk.BOTH, expand=True)
        
        self.db_listbox = tk.Listbox(db_frame, height=6)
        db_scrollbar = ttk.Scrollbar(db_frame, orient=tk.VERTICAL, command=self.db_listbox.yview)
        self.db_listbox.configure(yscrollcommand=db_scrollbar.set)
        
        self.db_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        db_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.db_listbox.bind('<<ListboxSelect>>', self.on_database_select)
        self.db_listbox.bind('<Button-3>', self.show_database_context_menu)  # Right-click context menu
        
        # Table section
        table_label_frame = ttk.LabelFrame(left_frame, text="Tables", padding=5)
        table_label_frame.pack(fill=tk.BOTH, expand=True)
        
        # Table listbox with scrollbar
        table_frame = ttk.Frame(table_label_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        self.table_listbox = tk.Listbox(table_frame)
        table_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table_listbox.yview)
        self.table_listbox.configure(yscrollcommand=table_scrollbar.set)
        
        self.table_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        self.table_listbox.bind('<Double-Button-1>', self.on_table_double_click)
        
    def create_right_panel(self, parent):
        """Create right panel with data display"""
        right_frame = ttk.Frame(parent)
        parent.add(right_frame, weight=4)
        
        # Table info frame
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.table_info_label = ttk.Label(info_frame, text="No table selected", font=('Segoe UI', 10, 'bold'))
        self.table_info_label.pack(side=tk.LEFT)
        
        self.row_count_label = ttk.Label(info_frame, text="")
        self.row_count_label.pack(side=tk.RIGHT)
        
        # Data display notebook for multiple views
        self.data_notebook = ttk.Notebook(right_frame)
        self.data_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Data view tab
        self.data_frame = ttk.Frame(self.data_notebook)
        self.data_notebook.add(self.data_frame, text="Data View")
        
        self.create_data_display(self.data_frame)
        
        # Column info tab
        self.column_frame = ttk.Frame(self.data_notebook)
        self.data_notebook.add(self.column_frame, text="Column Info")
        
        self.create_column_info(self.column_frame)
        
    def create_data_display(self, parent):
        """Create the main data display treeview"""
        # Frame for treeview and scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        self.data_tree = ttk.Treeview(tree_frame, style="Treeview")
        
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
        
        # Context menu for treeview
        self.create_context_menu()
        
    def create_column_info(self, parent):
        """Create column information display"""
        # Column info treeview
        self.column_tree = ttk.Treeview(parent, columns=('Type', 'Null Count', 'Unique', 'Stats'), show='tree headings')
        
        self.column_tree.heading('#0', text='Column Name')
        self.column_tree.heading('Type', text='Data Type')
        self.column_tree.heading('Null Count', text='Null Count')
        self.column_tree.heading('Unique', text='Unique Values')
        self.column_tree.heading('Stats', text='Statistics')
        
        self.column_tree.column('#0', width=150)
        self.column_tree.column('Type', width=100)
        self.column_tree.column('Null Count', width=80)
        self.column_tree.column('Unique', width=80)
        self.column_tree.column('Stats', width=200)
        
        # Scrollbar for column info
        col_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.column_tree.yview)
        self.column_tree.configure(yscrollcommand=col_scrollbar.set)
        
        self.column_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        col_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_context_menu(self):
        """Create context menu for data treeview"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy Cell", command=self.copy_cell)
        self.context_menu.add_command(label="Copy Row", command=self.copy_row)
        self.context_menu.add_command(label="Copy Column", command=self.copy_column)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Filter by Value", command=self.filter_by_value)
        self.context_menu.add_command(label="Show Column Stats", command=self.show_selected_column_stats)
        
        self.data_tree.bind("<Button-3>", self.show_context_menu)
        
    def create_status_bar(self):
        """Create enhanced status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        self.progress_bar.pack_forget()  # Hidden by default
        
    def setup_bindings(self):
        """Setup keyboard bindings and events"""
        self.root.bind('<Control-o>', lambda e: self.open_database())
        self.root.bind('<Control-f>', lambda e: self.focus_search())
        self.root.bind('<Control-c>', lambda e: self.copy_selected())
        self.root.bind('<F5>', lambda e: self.refresh_current_table())
        self.root.bind('<Escape>', lambda e: self.clear_search())
        
    def update_status(self, message: str, show_progress: bool = False):
        """Update status bar with optional progress bar"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.status_bar.config(text=f"{timestamp} - {message}")
        
        if show_progress:
            self.progress_bar.pack(side=tk.RIGHT, padx=5)
        else:
            self.progress_bar.pack_forget()
            
        self.root.update_idletasks()
        
    def show_progress(self, value: float):
        """Show progress bar with value (0-100)"""
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    # Database operations
    def open_database(self):
        """Open database file dialog"""
        filetypes = [
            ("All Supported", "*.db;*.sqlite;*.sqlite3;*.mdb;*.accdb;*.csv;*.xlsx;*.xls;*.json"),
            ("SQLite files", "*.db;*.sqlite;*.sqlite3"),
            ("Access files", "*.mdb;*.accdb"),
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
        """Load database file in background thread with Polars ultra-fast loading"""
        def load_thread():
            try:
                self.root.after(0, lambda: self.update_status(f"🚀 Loading with Polars: {os.path.basename(filename)}", True))
                self.root.after(0, lambda: self.show_progress(10))
                
                db_type = self.polars_manager.detect_database_type(filename)
                db_name = os.path.basename(filename)
                
                self.root.after(0, lambda: self.show_progress(20))
                
                # Progress callback for real-time updates
                def progress_callback(message, progress):
                    self.root.after(0, lambda: self.update_status(message))
                    self.root.after(0, lambda: self.show_progress(progress))
                
                if db_type == 'sqlite':
                    connection, tables = self.polars_manager.load_sqlite_polars(filename, progress_callback)
                elif db_type == 'access':
                    connection, tables = self.polars_manager.load_access_polars(filename, progress_callback)
                elif db_type == 'csv':
                    connection, table_name = self.polars_manager.load_csv_polars(filename, progress_callback)
                    tables = [table_name]
                    db_type = 'sqlite'  # Treat as SQLite for operations
                elif db_type == 'excel':
                    connection, table_names = self.polars_manager.load_excel_polars(filename, progress_callback)
                    tables = table_names
                    db_type = 'sqlite'  # Treat as SQLite for operations
                elif db_type == 'json':
                    connection, table_name = self.polars_manager.load_json_polars(filename, progress_callback)
                    tables = [table_name]
                    db_type = 'sqlite'  # Treat as SQLite for operations
                else:
                    raise ValueError(f"Unsupported file type: {db_type}")
                
                self.root.after(0, lambda: self.show_progress(95))
                
                # Store database info with filename for Polars cache access
                db_info = {
                    'connection': connection,
                    'type': db_type,
                    'path': filename,
                    'filename': filename,  # For Polars cache lookup
                    'tables': tables
                }
                
                self.root.after(0, lambda: self.on_database_loaded(db_name, db_info))
                
            except Exception as e:
                error_msg = f"Failed to load database: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.update_status("Ready"))
                
        threading.Thread(target=load_thread, daemon=True).start()
        
    def on_database_loaded(self, db_name: str, db_info: Dict[str, Any]):
        """Handle successful database loading"""
        self.databases[db_name] = db_info
        
        # Save database state for persistence
        self.config_manager.save_database_state(db_name, db_info)
        
        # Update recent files menu
        self.update_recent_files_menu()
        
        # Update database list
        if db_name not in self.db_listbox.get(0, tk.END):
            self.db_listbox.insert(tk.END, db_name)
            
        # Select the database
        for i in range(self.db_listbox.size()):
            if self.db_listbox.get(i) == db_name:
                self.db_listbox.selection_clear(0, tk.END)
                self.db_listbox.selection_set(i)
                self.db_listbox.activate(i)
                break
                
        self.show_progress(100)
        self.on_database_select(None)
        self.update_status(f"💾 Loaded & Saved: {db_name} ({len(db_info['tables'])} tables)")
        
    def on_database_select(self, event):
        """Handle database selection"""
        selection = self.db_listbox.curselection()
        if not selection:
            return
            
        db_name = self.db_listbox.get(selection[0])
        self.current_db = db_name
        
        if db_name in self.databases:
            tables = self.databases[db_name]['tables']
            self.update_table_list(tables)
            
    def update_table_list(self, tables: List[str]):
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
        """Load table data in background thread"""
        if not self.current_db or self.current_db not in self.databases:
            return

        def load_thread():
            try:
                self.root.after(0, lambda: self.update_status(f"Loading table: {table_name}", True))
                self.root.after(0, lambda: self.show_progress(20))

                db_info = self.databases[self.current_db]
                filename = db_info['path']
                connection = db_info['connection']
                db_type = db_info.get('type', 'sqlite')
                
                # Try to get data from Polars cache first (for CSV, Excel, JSON files)
                df_polars = self.polars_manager.polars_cache.get(filename, {}).get(table_name)
                
                if df_polars is not None:
                    # Use cached Polars DataFrame (faster for CSV/Excel/JSON)
                    df = df_polars.to_pandas()
                else:
                    # Query from database directly (for SQLite, Access, or uncached data)
                    try:
                        query = f"SELECT * FROM [{table_name}]"
                        df = pd.read_sql_query(query, connection)
                    except Exception as sql_error:
                        # Try without brackets in case of naming issues
                        query = f"SELECT * FROM {table_name}"
                        df = pd.read_sql_query(query, connection)
                
                if df is None or len(df) == 0:
                    # Check if table exists but is empty
                    try:
                        count_query = f"SELECT COUNT(*) FROM [{table_name}]"
                        cursor = connection.cursor()
                        cursor.execute(count_query)
                        row_count = cursor.fetchone()[0]
                        if row_count == 0:
                            # Table exists but is empty
                            df = pd.DataFrame()  # Create empty DataFrame with no columns yet
                            # Get column names
                            cursor.execute(f"PRAGMA table_info([{table_name}])")
                            columns_info = cursor.fetchall()
                            if columns_info:
                                column_names = [col[1] for col in columns_info]
                                df = pd.DataFrame(columns=column_names)
                        else:
                            raise ValueError(f"Table '{table_name}' appears to have {row_count} rows but no data could be retrieved")
                    except Exception as e:
                        raise ValueError(f"No data found for table '{table_name}' in file '{filename}': {str(e)}")
                
                table_info = {
                    'row_count': len(df),
                    'columns': list(df.columns)
                }
                self.root.after(0, lambda: self.show_progress(40))
                self.root.after(0, lambda: self.display_table_data(df, table_info))
            except Exception as e:
                error_msg = f"Failed to load table data: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.update_status("Ready"))

        threading.Thread(target=load_thread, daemon=True).start()
        
    def display_table_data(self, df: pd.DataFrame, table_info: Dict[str, Any]):
        """Display table data in treeview"""
        # Store current data
        self.current_data = df
        self.filtered_data = df.copy()
        
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        # Configure columns
        columns = list(df.columns)
        self.data_tree['columns'] = columns
        self.data_tree['show'] = 'headings'
        
        # Configure column headings and widths
        for col in columns:
            self.data_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            # Auto-size columns based on content
            max_width = max(
                len(str(col)) * 8,  # Header width
                df[col].astype(str).str.len().max() * 8 if not df.empty else 50  # Content width
            )
            self.data_tree.column(col, width=min(max_width, 200), minwidth=50)
            
        # Insert data (limit for performance)
        display_rows = min(len(df), 5000)  # Limit displayed rows
        for index in range(display_rows):
            row = df.iloc[index]
            values = [str(val) if pd.notna(val) else '' for val in row]
            self.data_tree.insert('', 'end', values=values)
            
        # Update info labels
        self.table_info_label.config(text=f"Table: {self.current_table}")
        
        total_rows = table_info.get('row_count', len(df))
        if display_rows < total_rows:
            self.row_count_label.config(text=f"Showing: {display_rows:,} of {total_rows:,} rows")
        else:
            self.row_count_label.config(text=f"Rows: {total_rows:,}")
            
        # Update column info
        self.update_column_info(df)
        
        self.show_progress(100)
        self.update_status(f"Loaded {display_rows:,} rows from {self.current_table}")
        
    def update_column_info(self, df: pd.DataFrame):
        """Update column information tab"""
        # Clear existing items
        for item in self.column_tree.get_children():
            self.column_tree.delete(item)
            
        # Add column statistics
        for col in df.columns:
            # Calculate statistics directly using pandas
            col_data = df[col]
            null_count = col_data.isnull().sum()
            unique_count = col_data.nunique()
            data_type = str(col_data.dtype)
            
            # Format statistics string
            stats_str = ""
            try:
                if pd.api.types.is_numeric_dtype(col_data):
                    # Numeric statistics
                    col_min = col_data.min()
                    col_max = col_data.max()
                    col_mean = col_data.mean()
                    stats_str = f"Min: {col_min:.2f}, Max: {col_max:.2f}, Mean: {col_mean:.2f}"
                else:
                    # Non-numeric statistics
                    value_counts = col_data.value_counts()
                    if not value_counts.empty:
                        top_value = value_counts.index[0]
                        top_count = value_counts.iloc[0]
                        stats_str = f"Most common: {top_value} ({top_count})"
                    else:
                        stats_str = "No data"
            except Exception:
                stats_str = "Unable to calculate"
                
            self.column_tree.insert('', 'end', text=col, values=(
                data_type,
                null_count,
                unique_count,
                stats_str
            ))
            
    # Search and filter functionality
    def focus_search(self):
        """Focus on search entry"""
        self.search_entry.focus_set()
        
    def search_data(self, event=None):
        """Search data in current table or across all databases"""
        search_term = self.get_search_term()
        if not search_term:
            if self.current_data is not None:
                self.filtered_data = self.current_data.copy()
                self.refresh_display()
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
            
        def search_thread():
            try:
                self.root.after(0, lambda: self.update_status(f"Searching current table for: {search_term}", True))
                
                # Perform search using pandas
                filtered_df = self.search_dataframe(self.current_data, search_term)
                
                # Update UI
                self.root.after(0, lambda: self.display_search_results(filtered_df, search_term))
                
            except Exception as e:
                error_msg = f"Search failed: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                
        threading.Thread(target=search_thread, daemon=True).start()
    
    def search_dataframe(self, df: pd.DataFrame, search_term: str) -> pd.DataFrame:
        """Search dataframe for the given term across all columns"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Convert search term to string and make case-insensitive
        search_term = str(search_term).lower()
        
        # Create a mask for rows that contain the search term
        mask = pd.Series([False] * len(df))
        
        # Search in each column
        for col in df.columns:
            try:
                # Convert column to string and search case-insensitively
                col_str = df[col].astype(str).str.lower()
                mask = mask | col_str.str.contains(search_term, na=False, regex=False)
            except Exception:
                # If any error occurs with a column, skip it
                continue
                
        return df[mask]
    
    def perform_global_search(self, search_term: str):
        """Ultra-fast search across all loaded databases using Polars"""
        if not self.databases:
            messagebox.showinfo("Global Search", "No databases loaded for global search.")
            return
            
        def global_search_thread():
            try:
                self.root.after(0, lambda: self.update_status(f"🚀 Ultra-fast search for: {search_term}", True))
                
                # Progress callback for real-time updates
                def progress_callback(message, progress):
                    self.root.after(0, lambda: self.update_status(message))
                    self.root.after(0, lambda: self.show_progress(progress))
                
                # Use ultra-fast Polars search
                search_results = self.polars_manager.ultra_parallel_global_search(
                    self.databases, search_term, progress_callback
                )
                
                # Prepare enhanced summary text with performance info
                if search_results['total_matches'] > 0:
                    summary_lines = [
                        f"🎯 Ultra-fast search found {search_results['total_matches']} total matches",
                        f"⚡ Searched {search_results['tables_searched']} tables in {search_results['databases_searched']} databases",
                        "",
                        "📊 Results by table:"
                    ]
                    
                    for result in search_results['summary']:
                        summary_lines.append(
                            f"  📋 {result['database']}.{result['table']}: {result['match_count']} matches "
                            f"(out of {result['total_rows']} total rows)"
                        )
                    
                    # Add performance info
                    perf_stats = self.polars_manager.get_performance_stats()
                    summary_lines.extend([
                        "",
                        "🚀 Performance Info:",
                        f"  ⚡ Polars-cached tables: {perf_stats['polars_cached_tables']}",
                        f"  💾 Memory usage: {perf_stats['polars_memory_usage_mb']:.1f} MB",
                        f"  🔧 Workers: {perf_stats['max_workers']}"
                    ])
                    
                    summary_text = "\n".join(summary_lines)
                    
                    # Combine all results
                    if search_results['matches']:
                        combined_results = pd.concat(search_results['matches'], ignore_index=True, sort=False)
                    else:
                        combined_results = pd.DataFrame()
                else:
                    combined_results = pd.DataFrame()
                    summary_text = f"❌ No matches found for '{search_term}' in any loaded database."
                
                # Update UI
                self.root.after(0, lambda: self.display_global_search_results(combined_results, search_term, summary_text))
                
            except Exception as e:
                error_msg = f"Ultra-fast search failed: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                
        threading.Thread(target=global_search_thread, daemon=True).start()
    
    def display_global_search_results(self, df: pd.DataFrame, search_term: str, summary: str):
        """Display global search results with enhanced user-friendly interface"""
        self.filtered_data = df
        
        # Clear and update treeview
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        if len(df) > 0:
            # Reorder columns for better user experience
            columns = list(df.columns)
            
            # Move metadata columns to front and make them more readable
            user_friendly_columns = []
            if '_database' in columns:
                user_friendly_columns.append('Database')
                columns.remove('_database')
            if '_table' in columns:
                user_friendly_columns.append('Table')
                columns.remove('_table')
            if '_source_row' in columns:
                user_friendly_columns.append('Row #')
                columns.remove('_source_row')
            
            # Add separator column
            user_friendly_columns.append('---')
            
            # Add remaining data columns
            user_friendly_columns.extend(columns)
            
            # Update treeview columns
            self.data_tree["columns"] = user_friendly_columns
            self.data_tree["show"] = "headings"
            
            # Configure column headers with better styling
            for i, col in enumerate(user_friendly_columns):
                if col == 'Database':
                    self.data_tree.heading(col, text="🗄️ Database")
                    self.data_tree.column(col, width=150, minwidth=100)
                elif col == 'Table':
                    self.data_tree.heading(col, text="📋 Table")
                    self.data_tree.column(col, width=130, minwidth=100)
                elif col == 'Row #':
                    self.data_tree.heading(col, text="📍 Row #")
                    self.data_tree.column(col, width=80, minwidth=60)
                elif col == '---':
                    self.data_tree.heading(col, text="│")
                    self.data_tree.column(col, width=20, minwidth=20)
                else:
                    # Highlight columns that contain the search term
                    if any(df[orig_col].astype(str).str.contains(search_term, case=False, na=False).any() 
                           for orig_col in df.columns if orig_col not in ['_database', '_table', '_source_row']):
                        self.data_tree.heading(col, text=f"🔍 {col}")
                    else:
                        self.data_tree.heading(col, text=col)
                    self.data_tree.column(col, width=120, minwidth=80)
            
            # Insert data with better formatting
            display_rows = min(len(df), 5000)
            for index in range(display_rows):
                row = df.iloc[index]
                
                # Create user-friendly values
                friendly_values = []
                
                # Database name (remove file extension for cleaner display)
                if '_database' in df.columns:
                    db_name = str(row['_database'])
                    if '.' in db_name:
                        db_name = db_name.split('.')[0]
                    friendly_values.append(f"📁 {db_name}")
                
                # Table name
                if '_table' in df.columns:
                    table_name = str(row['_table'])
                    friendly_values.append(f"📋 {table_name}")
                
                # Row number
                if '_source_row' in df.columns:
                    friendly_values.append(f"#{row['_source_row']}")
                
                # Separator
                friendly_values.append("│")
                
                # Data values with search term highlighting
                for col in [c for c in df.columns if c not in ['_database', '_table', '_source_row']]:
                    val = row[col]
                    str_val = str(val) if pd.notna(val) else ''
                    
                    # Highlight if this value contains the search term
                    if search_term.lower() in str_val.lower():
                        friendly_values.append(f"🔍 {str_val}")
                    else:
                        friendly_values.append(str_val)
                
                # Insert with alternating row colors for better readability
                tag = 'even' if index % 2 == 0 else 'odd'
                self.data_tree.insert('', 'end', values=friendly_values, tags=(tag,))
            
            # Configure row colors
            self.data_tree.tag_configure('even', background='#f0f8ff')
            self.data_tree.tag_configure('odd', background='white')
            
            # Update info with enhanced display
            match_count = len(df)
            db_count = df['_database'].nunique() if '_database' in df.columns else 0
            table_count = len(df.groupby(['_database', '_table'])) if '_database' in df.columns and '_table' in df.columns else 0
            
            self.table_info_label.config(
                text=f"🔍 Global Search Results for '{search_term}'"
            )
            self.row_count_label.config(
                text=f"Found: {match_count:,} matches in {table_count} tables across {db_count} databases"
            )
            
            # Create a more informative summary dialog
            self.show_enhanced_search_summary(summary, search_term, match_count, db_count, table_count)
            
        else:
            self.table_info_label.config(text="🔍 Global Search - No Results")
            self.row_count_label.config(text="No matches found in any database")
            messagebox.showinfo("Search Results", f"No matches found for '{search_term}' in any loaded database.")
            
        self.update_status(f"Global search completed: {len(df)} total results for '{search_term}'")
    
    def show_enhanced_search_summary(self, summary: str, search_term: str, match_count: int, db_count: int, table_count: int):
        """Show an enhanced search summary dialog"""
        # Create a custom dialog window
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Global Search Summary")
        summary_window.geometry("600x400")
        summary_window.resizable(True, True)
        
        # Make it modal
        summary_window.transient(self.root)
        summary_window.grab_set()
        
        # Center the window
        summary_window.update_idletasks()
        x = (summary_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (summary_window.winfo_screenheight() // 2) - (400 // 2)
        summary_window.geometry(f"600x400+{x}+{y}")
        
        # Header frame
        header_frame = ttk.Frame(summary_window)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(header_frame, text=f"🔍 Search Results for: '{search_term}'", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack()
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(summary_window, text="📊 Search Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Statistics grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        ttk.Label(stats_grid, text="Total Matches:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5)
        ttk.Label(stats_grid, text=f"{match_count:,}", foreground='blue').grid(row=0, column=1, sticky='w')
        
        ttk.Label(stats_grid, text="Databases Searched:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5)
        ttk.Label(stats_grid, text=f"{db_count}", foreground='green').grid(row=1, column=1, sticky='w')
        
        ttk.Label(stats_grid, text="Tables with Matches:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5)
        ttk.Label(stats_grid, text=f"{table_count}", foreground='purple').grid(row=2, column=1, sticky='w')
        
        # Details frame
        details_frame = ttk.LabelFrame(summary_window, text="📋 Detailed Results", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Text area with scrollbar
        text_frame = ttk.Frame(details_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_area = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert formatted summary
        text_area.insert(tk.END, summary)
        text_area.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = ttk.Frame(summary_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="✅ OK", command=summary_window.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="📋 Copy to Clipboard", 
                  command=lambda: self.copy_to_clipboard(summary)).pack(side=tk.RIGHT, padx=5)
    
    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Summary copied to clipboard!")
    
    def on_search_focus_in(self, event=None):
        """Handle search entry focus in - remove placeholder"""
        if self.search_var.get() == self.search_placeholder:
            self.search_var.set("")
            self.search_entry.config(foreground='black')
    
    def on_search_focus_out(self, event=None):
        """Handle search entry focus out - add placeholder if empty"""
        if not self.search_var.get().strip():
            self.search_var.set(self.search_placeholder)
            self.search_entry.config(foreground='gray')
    
    def get_search_term(self):
        """Get the actual search term (excluding placeholder)"""
        search_text = self.search_var.get().strip()
        if search_text == self.search_placeholder:
            return ""
        return search_text
        
    def on_search_change(self, event=None):
        """Handle search text change with delay"""
        # Cancel previous search timer
        if hasattr(self, 'search_timer'):
            self.root.after_cancel(self.search_timer)
            
        # Set new search timer (500ms delay)
        self.search_timer = self.root.after(500, self.search_data)
    
    def on_global_search_toggle(self):
        """Handle global search toggle"""
        if self.global_search_var.get():
            self.update_status("Global search enabled - will search across all loaded databases")
            # Clear current search to avoid confusion
            if self.search_var.get().strip():
                self.clear_search()
        else:
            self.update_status("Global search disabled - will search current table only")
            # If we're showing global results, clear them
            if hasattr(self, 'filtered_data') and self.filtered_data is not None:
                if '_database' in self.filtered_data.columns:
                    self.clear_search()
        
    def display_search_results(self, df: pd.DataFrame, search_term: str):
        """Display search results"""
        self.filtered_data = df
        
        # Clear and update treeview
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        # Insert filtered data
        display_rows = min(len(df), 5000)
        for index in range(display_rows):
            row = df.iloc[index]
            values = [str(val) if pd.notna(val) else '' for val in row]
            self.data_tree.insert('', 'end', values=values)
            
        # Update row count
        if len(df) > 0:
            self.row_count_label.config(text=f"Found: {len(df):,} matches")
        else:
            self.row_count_label.config(text="No matches found")
            
        self.update_status(f"Search completed: {len(df)} results for '{search_term}'")
        
    def clear_search(self):
        """Clear search and show all data"""
        self.search_var.set("")
        self.on_search_focus_out()  # Reset placeholder
        
        # If we have global search results, we need to reload the current table
        if (hasattr(self, 'filtered_data') and self.filtered_data is not None and 
            '_database' in self.filtered_data.columns):
            # We're showing global search results, reload current table
            if self.current_table and self.current_db:
                self.load_table_data(self.current_table)
        elif self.current_data is not None:
            # Regular local search, just restore current data
            self.filtered_data = self.current_data.copy()
            self.refresh_display()
            
    def refresh_display(self):
        """Refresh the current display"""
        if self.filtered_data is not None:
            # Clear and update treeview
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
                
            # Insert current filtered data
            display_rows = min(len(self.filtered_data), 5000)
            for index in range(display_rows):
                row = self.filtered_data.iloc[index]
                values = [str(val) if pd.notna(val) else '' for val in row]
                self.data_tree.insert('', 'end', values=values)
                
            # Update row count
            total_rows = len(self.current_data) if self.current_data is not None else 0
            if len(self.filtered_data) < total_rows:
                self.row_count_label.config(text=f"Filtered: {len(self.filtered_data):,} of {total_rows:,} rows")
            else:
                self.row_count_label.config(text=f"Rows: {total_rows:,}")
                
    # Context menu functions
    def show_context_menu(self, event):
        """Show context menu"""
        self.context_menu.post(event.x_root, event.y_root)
        
    def copy_cell(self):
        """Copy selected cell to clipboard"""
        selection = self.data_tree.selection()
        if selection:
            item = selection[0]
            col = self.data_tree.identify_column(self.data_tree.winfo_pointerx() - self.data_tree.winfo_rootx())
            if col:
                col_index = int(col[1:]) - 1
                values = self.data_tree.item(item)['values']
                if col_index < len(values):
                    self.root.clipboard_clear()
                    self.root.clipboard_append(str(values[col_index]))
                    
    def copy_row(self):
        """Copy selected row to clipboard"""
        selection = self.data_tree.selection()
        if selection:
            item = selection[0]
            values = self.data_tree.item(item)['values']
            row_text = '\t'.join(str(val) for val in values)
            self.root.clipboard_clear()
            self.root.clipboard_append(row_text)
            
    def copy_column(self):
        """Copy selected column to clipboard"""
        # Implementation for copying entire column
        pass
        
    def copy_selected(self):
        """Copy selected data to clipboard"""
        selection = self.data_tree.selection()
        if selection:
            rows = []
            for item in selection:
                values = self.data_tree.item(item)['values']
                rows.append('\t'.join(str(val) for val in values))
            
            if rows:
                self.root.clipboard_clear()
                self.root.clipboard_append('\n'.join(rows))
                self.update_status(f"Copied {len(rows)} rows to clipboard")
                
    # Import functions
    def show_import_menu(self):
        """Show import menu"""
        import_menu = tk.Menu(self.root, tearoff=0)
        import_menu.add_command(label="CSV File...", command=self.import_csv)
        import_menu.add_command(label="Excel File...", command=self.import_excel)
        import_menu.add_command(label="JSON File...", command=self.import_json)
        
        # Show menu at button location
        import_menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
        
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
            
    # Export functions
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
            self.export_data_to_file(self.current_data, filename)
            
    def export_filtered(self):
        """Export filtered data"""
        if self.filtered_data is None:
            messagebox.showwarning("Warning", "No filtered data to export")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export Filtered Data",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("JSON files", "*.json")
            ]
        )
        
        if filename:
            self.export_data_to_file(self.filtered_data, filename)
            
    def export_data_to_file(self, df: pd.DataFrame, filename: str):
        """Export DataFrame to file"""
        def export_thread():
            try:
                self.root.after(0, lambda: self.update_status(f"Exporting to: {os.path.basename(filename)}", True))
                
                ext = os.path.splitext(filename)[1].lower()
                if ext == '.csv':
                    df.to_csv(filename, index=False)
                elif ext == '.xlsx':
                    df.to_excel(filename, index=False)
                elif ext == '.json':
                    df.to_json(filename, orient='records', indent=2)
                    
                self.root.after(0, lambda: self.update_status(f"Exported: {os.path.basename(filename)}"))
                
            except Exception as e:
                error_msg = f"Export failed: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                
        threading.Thread(target=export_thread, daemon=True).start()
        
    # Utility functions
    def sort_by_column(self, column: str):
        """Sort data by column"""
        if self.filtered_data is not None:
            try:
                # Toggle sort order
                if hasattr(self, 'last_sort_column') and self.last_sort_column == column:
                    self.sort_ascending = not getattr(self, 'sort_ascending', True)
                else:
                    self.sort_ascending = True
                    
                self.last_sort_column = column
                
                # Sort data
                self.filtered_data = self.filtered_data.sort_values(
                    by=column, 
                    ascending=self.sort_ascending,
                    na_position='last'
                )
                
                self.refresh_display()
                
                order_text = "ascending" if self.sort_ascending else "descending"
                self.update_status(f"Sorted by {column} ({order_text})")
                
            except Exception as e:
                messagebox.showerror("Error", f"Sort failed: {str(e)}")
                
    def refresh_current_table(self):
        """Refresh current table data"""
        if self.current_table:
            self.load_table_data(self.current_table)
            
    def filter_by_value(self):
        """Filter by selected cell value"""
        # Implementation for filtering by cell value
        pass
        
    def show_selected_column_stats(self):
        """Show statistics for selected column"""
        # Implementation for showing column statistics
        pass
        
    def show_column_stats(self):
        """Show column statistics dialog"""
        # Implementation for column statistics dialog
        pass
        
    def show_data_stats(self):
        """Show data statistics dialog"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
            
        # Create statistics window
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Data Statistics")
        stats_window.geometry("600x400")
        
        # Create text widget for stats
        text_widget = tk.Text(stats_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(stats_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generate statistics
        stats_text = f"Dataset Overview\n{'='*50}\n\n"
        stats_text += f"Table: {self.current_table}\n"
        stats_text += f"Rows: {len(self.current_data):,}\n"
        stats_text += f"Columns: {len(self.current_data.columns)}\n\n"
        
        stats_text += "Column Information\n" + "-"*30 + "\n"
        for col in self.current_data.columns:
            # Generate column statistics directly
            col_data = self.current_data[col]
            null_count = col_data.isnull().sum()
            unique_count = col_data.nunique()
            data_type = str(col_data.dtype)
            
            stats_text += f"\n{col}:\n"
            stats_text += f"  Type: {data_type}\n"
            stats_text += f"  Null values: {null_count}\n"
            stats_text += f"  Unique values: {unique_count}\n"
            
            try:
                if pd.api.types.is_numeric_dtype(col_data):
                    col_min = col_data.min()
                    col_max = col_data.max()
                    col_mean = col_data.mean()
                    stats_text += f"  Min: {col_min}\n"
                    stats_text += f"  Max: {col_max}\n"
                    stats_text += f"  Mean: {col_mean:.2f}\n"
                else:
                    value_counts = col_data.value_counts()
                    if not value_counts.empty:
                        stats_text += f"  Most common: {value_counts.index[0]} ({value_counts.iloc[0]})\n"
            except Exception:
                stats_text += "  Statistics: Unable to calculate\n"
                    
        text_widget.insert('1.0', stats_text)
        text_widget.config(state=tk.DISABLED)
        
    def open_sql_query(self):
        """Open SQL query dialog"""
        # Implementation for SQL query interface
        messagebox.showinfo("Info", "SQL Query interface coming soon!")
        
    def open_settings(self):
        """Open settings dialog"""
        # Implementation for settings dialog
        messagebox.showinfo("Info", "Settings dialog coming soon!")
        
    def increase_font(self):
        """Increase font size"""
        # Implementation for font size increase
        pass
        
    def decrease_font(self):
        """Decrease font size"""
        # Implementation for font size decrease
        pass
        
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts = """
Keyboard Shortcuts
==================

File Operations:
  Ctrl+O    Open Database
  Ctrl+S    Save (if applicable)

Navigation:
  F5        Refresh current table
  Ctrl+F    Focus search box
  Escape    Clear search

Data Operations:
  Ctrl+C    Copy selected rows
  Ctrl+A    Select all (in treeview)

View:
  +         Increase font size
  -         Decrease font size
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
        
    def show_about(self):
        """Show about dialog"""
        about_text = """
ShadowHawk Database Browser v1.0.0

A fast and modern desktop application for browsing local databases and data files.

Supported formats:
• SQLite (.db, .sqlite, .sqlite3)
• Microsoft Access (.mdb, .accdb)
• CSV files (.csv)
• Excel files (.xlsx, .xls)
• JSON files (.json)

Features:
• Fast data loading and display
• Advanced search and filtering
• Data export capabilities
• Column statistics
• Multi-threaded operations

Built with Python, tkinter, and pandas.
"""
        messagebox.showinfo("About ShadowHawk Database Browser", about_text)
        
    def load_settings(self):
        """Load application settings from config manager"""
        try:
            # Load UI settings
            window_width = self.config_manager.get_setting('ui_settings', 'window_width', 1400)
            window_height = self.config_manager.get_setting('ui_settings', 'window_height', 900)
            self.root.geometry(f"{window_width}x{window_height}")
            
            # Load performance settings
            self.max_display_rows = self.config_manager.get_setting('app_settings', 'max_display_rows', 10000)
            self.chunk_size = self.config_manager.get_setting('app_settings', 'chunk_size', 1000)
            
        except Exception as e:
            print(f"Error loading settings: {e}")
        
    def save_settings(self):
        """Save application settings to config manager"""
        try:
            # Save current window size
            geometry = self.root.geometry()
            width, height = geometry.split('x')[0], geometry.split('x')[1].split('+')[0]
            self.config_manager.set_setting('ui_settings', 'window_width', int(width))
            self.config_manager.set_setting('ui_settings', 'window_height', int(height))
            
        except Exception as e:
            print(f"Error saving settings: {e}")
    
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
            context_menu.add_command(label="💾 Save State", command=self.save_selected_database_state)
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
            if db_name in self.databases:
                db_info = self.databases[db_name]
                if 'connection' in db_info and db_info['connection']:
                    try:
                        db_info['connection'].close()
                    except Exception as e:
                        print(f"Error closing connection for {db_name}: {e}")
                
                # Remove from databases dict
                del self.databases[db_name]
            
            # Remove from config/saved state
            self.config_manager.remove_database_state(db_name)
            
            # Remove from listbox
            self.db_listbox.delete(selection[0])
            
            # Clear UI if this was the current database
            if self.current_db == db_name:
                self.current_db = None
                self.current_table = None
                self.current_data = None
                self.filtered_data = None
                
                # Clear table list
                self.table_listbox.delete(0, tk.END)
                
                # Clear data display
                for item in self.data_tree.get_children():
                    self.data_tree.delete(item)
                
                # Clear data tree columns and headers
                self.data_tree['columns'] = ()
                self.data_tree.heading('#0', text='')
                
                # Clear column info panel
                for item in self.column_tree.get_children():
                    self.column_tree.delete(item)
                
                # Clear table info label
                self.table_info_label.config(text="No table selected")
                
                # Clear row count label
                self.row_count_label.config(text="")
            
            # Update recent files menu
            self.update_recent_files_menu()
            
            self.update_status(f"✅ Removed database: {db_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove database: {str(e)}")
    
    def save_selected_database_state(self):
        """Save state for the currently selected database"""
        selection = self.db_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a database.")
            return
        
        db_name = self.db_listbox.get(selection[0])
        
        if db_name in self.databases:
            self.config_manager.save_database_state(db_name, self.databases[db_name])
            messagebox.showinfo("State Saved", f"✅ Saved state for '{db_name}'")
        else:
            messagebox.showwarning("Error", f"Database '{db_name}' not found in loaded databases.")
    
    def reload_selected_database(self):
        """Reload the currently selected database"""
        selection = self.db_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a database to reload.")
            return
        
        db_name = self.db_listbox.get(selection[0])
        
        if db_name in self.databases:
            db_info = self.databases[db_name]
            if 'path' in db_info and os.path.exists(db_info['path']):
                # Remove current database first
                try:
                    if 'connection' in db_info and db_info['connection']:
                        db_info['connection'].close()
                except:
                    pass
                
                # Remove from UI
                self.db_listbox.delete(selection[0])
                del self.databases[db_name]
                
                # Reload the database
                self.load_database_file(db_info['path'])
                self.update_status(f"🔄 Reloading: {db_name}")
            else:
                messagebox.showerror("Error", f"Database file not found: {db_info.get('path', 'Unknown path')}")
        else:
            messagebox.showwarning("Error", f"Database '{db_name}' not found in loaded databases.")
    
    def remove_all_databases(self):
        """Remove all loaded databases (with confirmation)"""
        if not self.databases:
            messagebox.showinfo("No Databases", "No databases are currently loaded.")
            return
        
        result = messagebox.askyesno(
            "Remove All Databases",
            f"⚠️ Remove ALL {len(self.databases)} loaded databases?\n\n"
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
            for db_name, db_info in self.databases.items():
                if 'connection' in db_info and db_info['connection']:
                    try:
                        db_info['connection'].close()
                    except:
                        pass
                
                # Remove from saved state
                self.config_manager.remove_database_state(db_name)
            
            # Clear all data
            self.databases.clear()
            self.db_listbox.delete(0, tk.END)
            self.table_listbox.delete(0, tk.END)
            
            # Clear data display
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            # Clear data tree columns and headers
            self.data_tree['columns'] = ()
            self.data_tree.heading('#0', text='')
            
            # Clear column info panel
            for item in self.column_tree.get_children():
                self.column_tree.delete(item)
            
            # Clear table info label
            self.table_info_label.config(text="No table selected")
            
            # Clear row count label
            self.row_count_label.config(text="")
            
            # Reset current selections
            self.current_db = None
            self.current_table = None
            self.current_data = None
            self.filtered_data = None
            
            # Update recent files menu
            self.update_recent_files_menu()
            
            self.update_status("✅ Removed all databases")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove all databases: {str(e)}")
    
    def restore_saved_databases(self):
        """Restore previously loaded databases on startup"""
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
                    # Remove invalid database from config
                    self.config_manager.remove_database_state(db_name)
            
            if restored_count > 0:
                self.root.after(0, lambda: self.update_status(f"✅ Restored {restored_count} databases"))
            else:
                self.root.after(0, lambda: self.update_status("Ready"))
        
        # Restore databases in background thread
        threading.Thread(target=restore_thread, daemon=True).start()
    
    def save_all_database_states(self):
        """Manually save all current database states"""
        try:
            count = 0
            for db_name, db_info in self.databases.items():
                self.config_manager.save_database_state(db_name, db_info)
                count += 1
            
            messagebox.showinfo("Database State Saved", 
                              f"✅ Saved state for {count} databases.\n"
                              f"They will be automatically restored on next startup.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save database states: {e}")
    
    def clear_database_history(self):
        """Clear all saved database history"""
        result = messagebox.askyesno("Clear Database History", 
                                   "⚠️ This will clear all saved database history and recent files.\n"
                                   "Current loaded databases will remain open.\n\n"
                                   "Are you sure?")
        if result:
            self.config_manager.clear_database_history()
            self.update_recent_files_menu()
            messagebox.showinfo("History Cleared", "✅ Database history has been cleared.")
    
    def update_recent_files_menu(self):
        """Update the recent files menu"""
        # Clear existing menu items
        self.recent_menu.delete(0, tk.END)
        
        recent_files = self.config_manager.get_recent_files()
        
        if not recent_files:
            self.recent_menu.add_command(label="(No recent files)", state="disabled")
            return
        
        # Add recent files
        for i, filepath in enumerate(recent_files[:10]):  # Show max 10 recent files
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                # Truncate long filenames
                if len(filename) > 50:
                    filename = filename[:47] + "..."
                
                self.recent_menu.add_command(
                    label=f"{i+1}. {filename}",
                    command=lambda path=filepath: self.load_database_file(path)
                )
            else:
                # Remove non-existent files from recent list
                recent_files.remove(filepath)
        
        if recent_files:
            self.recent_menu.add_separator()
            self.recent_menu.add_command(label="🗑️ Clear Recent Files", 
                                       command=self.clear_recent_files)
    
    def clear_recent_files(self):
        """Clear recent files list"""
        self.config_manager.config['recent_files'] = []
        self.config_manager.save_config()
        self.update_recent_files_menu()
    
    def _set_application_icon(self):
        """Set application icon with multiple fallback methods"""
        icon_set = False
        
        # Method 1: Try ICO file first (best for Windows)
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
                icon_set = True
        except Exception as e:
            pass
        
        # Method 2: Try PNG via PhotoImage (works for window, not always taskbar)
        if not icon_set:
            try:
                from PIL import Image, ImageTk
                icon_image = Image.open("assets/icon.png")
                
                # Create multiple sizes
                icon_16 = icon_image.resize((16, 16), Image.Resampling.LANCZOS)
                icon_32 = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                icon_48 = icon_image.resize((48, 48), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                self.icon_photo_16 = ImageTk.PhotoImage(icon_16)
                self.icon_photo_32 = ImageTk.PhotoImage(icon_32)
                self.icon_photo_48 = ImageTk.PhotoImage(icon_48)
                
                # Set icon
                self.root.iconphoto(True, self.icon_photo_48, self.icon_photo_32, self.icon_photo_16)
                icon_set = True
                
            except Exception as e:
                pass
        
        # Method 3: Force update after window is shown
        if icon_set:
            self.root.after(100, self._force_icon_update)
    
    def _setup_windows_taskbar(self):
        """Setup Windows-specific taskbar integration"""
        try:
            import sys
            if sys.platform.startswith('win'):
                # Try to set app ID for Windows 7+ taskbar grouping
                try:
                    import ctypes
                    myappid = 'shadowhawk.database.browser.1.0.0'
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                except:
                    pass
                
                # Try additional Windows icon setting
                self.root.after(500, self._windows_icon_fix)
        except:
            pass
    
    def _force_icon_update(self):
        """Force icon update after window is visible"""
        try:
            # Re-apply ICO icon if available
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
            
            # Update window to force refresh
            self.root.update_idletasks()
        except:
            pass
    
    def _windows_icon_fix(self):
        """Windows-specific icon fix for taskbar"""
        try:
            import sys
            if sys.platform.startswith('win'):
                # Try to refresh the window icon
                if os.path.exists("icon.ico"):
                    # Clear and reset icon
                    self.root.iconbitmap("")
                    self.root.iconbitmap("icon.ico")
                    
                # Force window refresh
                self.root.lift()
                self.root.attributes('-topmost', True)
                self.root.after(100, lambda: self.root.attributes('-topmost', False))
        except:
            pass
    
    def _cleanup_temp_icon(self, icon_path: str):
        """Clean up temporary ICO file"""
        try:
            import os
            if os.path.exists(icon_path):
                os.remove(icon_path)
        except Exception:
            pass  # Ignore cleanup errors
    
    def on_closing(self):
        """Handle application closing - save state before exit"""
        try:
            # Save current settings
            self.save_settings()
            
            # Save all database states
            for db_name, db_info in self.databases.items():
                self.config_manager.save_database_state(db_name, db_info)
            
            # Close database connections
            for db_info in self.databases.values():
                if 'connection' in db_info:
                    try:
                        db_info['connection'].close()
                    except:
                        pass
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
        
        # Destroy the window
        self.root.destroy()
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ShadowHawkBrowser()
    app.run()
