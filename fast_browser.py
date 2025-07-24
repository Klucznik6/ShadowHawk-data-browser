#!/usr/bin/env python3
"""
ShadowHawk Database Browser - Performance Optimized Version
Fast desktop application for browsing local databases with enhanced speed.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from datetime import datetime
import os
import pandas as pd

# Import our enhanced modules
from fast_database_utils import FastDatabaseManager
from database_utils import DataProcessor

try:
    from ttkthemes import ThemedTk
    THEMED_TK_AVAILABLE = True
except ImportError:
    THEMED_TK_AVAILABLE = False

class FastShadowHawkBrowser:
    """High-performance database browser with optimized loading and search"""
    
    def __init__(self):
        # Initialize main window
        if THEMED_TK_AVAILABLE:
            self.root = ThemedTk(theme="arc")
        else:
            self.root = tk.Tk()
            
        self.root.title("🚀 ShadowHawk Database Browser - High Performance")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Initialize managers
        self.db_manager = FastDatabaseManager()
        self.data_processor = DataProcessor()
        
        # Application state
        self.databases = {}
        self.current_db = None
        self.current_table = None
        self.current_data = None
        self.filtered_data = None
        
        # Performance settings
        self.max_display_rows = 10000
        self.enable_parallel_search = True
        
        # Progress tracking
        self.progress_var = tk.DoubleVar()
        self.progress_text = tk.StringVar()
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI components"""
        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()
        self.create_status_bar()
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="⚡ Fast Import CSV", command=self.fast_import_csv)
        file_menu.add_command(label="⚡ Fast Import Excel", command=self.fast_import_excel)
        file_menu.add_separator()
        file_menu.add_command(label="Open Database", command=self.open_database)
        file_menu.add_separator()
        file_menu.add_command(label="Performance Settings", command=self.show_performance_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Search menu
        search_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Search", menu=search_menu)
        search_menu.add_command(label="🔍 Fast Search Current", command=self.focus_search)
        search_menu.add_command(label="🌐 Fast Global Search", command=self.toggle_global_search)
        
    def create_toolbar(self):
        """Create enhanced toolbar with performance features"""
        # Main toolbar
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Performance section
        perf_frame = ttk.LabelFrame(toolbar_frame, text="⚡ Fast Import", padding=5)
        perf_frame.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(perf_frame, text="🚀 CSV", command=self.fast_import_csv, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(perf_frame, text="🚀 Excel", command=self.fast_import_excel, width=8).pack(side=tk.LEFT, padx=1)
        
        # Regular import
        import_frame = ttk.LabelFrame(toolbar_frame, text="📁 Standard", padding=5)
        import_frame.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(import_frame, text="Open DB", command=self.open_database, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(import_frame, text="Import", command=self.show_import_menu, width=8).pack(side=tk.LEFT, padx=1)
        
        # Search section
        search_frame = ttk.LabelFrame(toolbar_frame, text="🔍 Smart Search", padding=5)
        search_frame.pack(side=tk.RIGHT, padx=2)
        
        # Performance toggle
        self.parallel_search_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(search_frame, text="⚡ Parallel", 
                       variable=self.parallel_search_var).pack(side=tk.LEFT, padx=2)
        
        # Global search toggle
        self.global_search_var = tk.BooleanVar()
        ttk.Checkbutton(search_frame, text="🌐 Global", 
                       variable=self.global_search_var).pack(side=tk.LEFT, padx=2)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=2)
        self.search_entry.bind('<Return>', self.fast_search)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        ttk.Button(search_frame, text="🔍", command=self.fast_search, width=3).pack(side=tk.LEFT, padx=1)
        ttk.Button(search_frame, text="❌", command=self.clear_search, width=3).pack(side=tk.LEFT, padx=1)
        
    def create_main_layout(self):
        """Create main application layout"""
        # Progress bar (initially hidden)
        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.pack(fill=tk.X, padx=5)
        
        ttk.Label(self.progress_frame, textvariable=self.progress_text).pack(side=tk.LEFT)
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, 
                                          maximum=100, length=300)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        
        # Hide progress initially
        self.progress_frame.pack_forget()
        
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
        db_label_frame = ttk.LabelFrame(left_frame, text="📊 Databases", padding=5)
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
        
        # Table section
        table_label_frame = ttk.LabelFrame(left_frame, text="📋 Tables", padding=5)
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
        
    def create_right_panel(self, parent):
        """Create right panel with data display"""
        right_frame = ttk.Frame(parent)
        parent.add(right_frame, weight=4)
        
        # Table info frame
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.table_info_label = ttk.Label(info_frame, text="No table selected", 
                                         font=('Segoe UI', 10, 'bold'))
        self.table_info_label.pack(side=tk.LEFT)
        
        self.row_count_label = ttk.Label(info_frame, text="")
        self.row_count_label.pack(side=tk.RIGHT)
        
        # Performance indicator
        self.perf_label = ttk.Label(info_frame, text="", foreground="green")
        self.perf_label.pack(side=tk.RIGHT, padx=10)
        
        # Data display
        self.create_data_display(right_frame)
        
    def create_data_display(self, parent):
        """Create the data display treeview"""
        # Treeview with scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.data_tree = ttk.Treeview(tree_frame)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        
        self.data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and treeview
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Performance stats
        self.perf_stats_label = ttk.Label(self.status_frame, text="")
        self.perf_stats_label.pack(side=tk.RIGHT)
        
    def show_progress(self, text: str, value: int):
        """Show progress bar with text"""
        self.progress_text.set(text)
        self.progress_var.set(value)
        
        if not self.progress_frame.winfo_viewable():
            self.progress_frame.pack(fill=tk.X, padx=5, before=self.status_frame)
        
        self.root.update_idletasks()
        
    def hide_progress(self):
        """Hide progress bar"""
        if self.progress_frame.winfo_viewable():
            self.progress_frame.pack_forget()
        
    def fast_import_csv(self):
        """Fast CSV import with progress feedback"""
        filename = filedialog.askopenfilename(
            title="Fast Import CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            def import_thread():
                start_time = time.time()
                try:
                    # Show progress
                    self.root.after(0, lambda: self.show_progress("Preparing CSV import...", 0))
                    
                    connection, table_name = self.db_manager.load_csv_fast(
                        filename, 
                        progress_callback=lambda text, progress: self.root.after(0, lambda: self.show_progress(text, progress))
                    )
                    
                    # Store database info
                    db_name = os.path.basename(filename)
                    db_info = {
                        'connection': connection,
                        'type': 'csv',
                        'tables': [table_name],
                        'filename': filename
                    }
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.finish_fast_import(db_name, db_info, start_time))
                    
                except Exception as e:
                    error_msg = f"Fast CSV import failed: {str(e)}"
                    self.root.after(0, lambda: self.show_import_error(error_msg))
                    
            threading.Thread(target=import_thread, daemon=True).start()
            
    def fast_import_excel(self):
        """Fast Excel import with progress feedback"""
        filename = filedialog.askopenfilename(
            title="Fast Import Excel",
            filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")]
        )
        
        if filename:
            def import_thread():
                start_time = time.time()
                try:
                    # Show progress
                    self.root.after(0, lambda: self.show_progress("Preparing Excel import...", 0))
                    
                    connection, table_names = self.db_manager.load_excel_fast(
                        filename,
                        progress_callback=lambda text, progress: self.root.after(0, lambda: self.show_progress(text, progress))
                    )
                    
                    # Store database info
                    db_name = os.path.basename(filename)
                    db_info = {
                        'connection': connection,
                        'type': 'excel',
                        'tables': table_names,
                        'filename': filename
                    }
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.finish_fast_import(db_name, db_info, start_time))
                    
                except Exception as e:
                    error_msg = f"Fast Excel import failed: {str(e)}"
                    self.root.after(0, lambda: self.show_import_error(error_msg))
                    
            threading.Thread(target=import_thread, daemon=True).start()
            
    def finish_fast_import(self, db_name: str, db_info: dict, start_time: float):
        """Finish fast import process"""
        # Store database
        self.databases[db_name] = db_info
        
        # Update database list
        self.db_listbox.insert(tk.END, f"⚡ {db_name}")
        
        # Hide progress and show completion
        self.hide_progress()
        
        import_time = time.time() - start_time
        table_count = len(db_info['tables'])
        
        self.status_label.config(text=f"✅ Fast import completed: {table_count} tables in {import_time:.2f}s")
        self.perf_stats_label.config(text=f"⚡ Performance: {table_count/import_time:.1f} tables/sec")
        
        messagebox.showinfo("Fast Import Complete", 
                           f"Successfully imported {table_count} tables in {import_time:.2f} seconds")
        
    def show_import_error(self, error_msg: str):
        """Show import error"""
        self.hide_progress()
        self.status_label.config(text="❌ Import failed")
        messagebox.showerror("Import Error", error_msg)
        
    def fast_search(self, event=None):
        """Perform fast search"""
        search_term = self.search_var.get().strip()
        if not search_term:
            return
            
        if self.global_search_var.get():
            self.perform_fast_global_search(search_term)
        else:
            self.perform_fast_local_search(search_term)
            
    def perform_fast_global_search(self, search_term: str):
        """Fast parallel global search"""
        if not self.databases:
            messagebox.showinfo("Global Search", "No databases loaded for global search.")
            return
            
        def search_thread():
            start_time = time.time()
            try:
                # Show progress
                self.root.after(0, lambda: self.show_progress("Starting parallel global search...", 0))
                
                if self.parallel_search_var.get():
                    # Use parallel search
                    results = self.db_manager.parallel_global_search(
                        self.databases, 
                        search_term,
                        progress_callback=lambda text, progress: self.root.after(0, lambda: self.show_progress(text, progress))
                    )
                else:
                    # Use regular search
                    results = self.data_processor.search_all_databases(
                        self.databases, search_term, self.db_manager
                    )
                
                search_time = time.time() - start_time
                
                # Update UI
                self.root.after(0, lambda: self.finish_fast_search(results, search_term, search_time, True))
                
            except Exception as e:
                error_msg = f"Fast global search failed: {str(e)}"
                self.root.after(0, lambda: self.show_search_error(error_msg))
                
        threading.Thread(target=search_thread, daemon=True).start()
        
    def perform_fast_local_search(self, search_term: str):
        """Fast local table search"""
        if not self.current_table or not self.current_db:
            return
            
        def search_thread():
            start_time = time.time()
            try:
                # Show progress
                self.root.after(0, lambda: self.show_progress(f"Fast searching {self.current_table}...", 0))
                
                db_info = self.databases[self.current_db]
                connection = db_info['connection']
                
                # Use fast database search
                results = self.db_manager.fast_search_table(connection, self.current_table, search_term)
                
                search_time = time.time() - start_time
                
                # Update UI
                self.root.after(0, lambda: self.display_fast_local_results(results, search_term, search_time))
                
            except Exception as e:
                error_msg = f"Fast local search failed: {str(e)}"
                self.root.after(0, lambda: self.show_search_error(error_msg))
                
        threading.Thread(target=search_thread, daemon=True).start()
        
    def display_fast_local_results(self, df, search_term: str, search_time: float):
        """Display fast local search results"""
        self.hide_progress()
        
        # Clear treeview
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        if len(df) > 0:
            # Setup columns
            columns = list(df.columns)
            self.data_tree["columns"] = columns
            self.data_tree["show"] = "headings"
            
            # Configure headers
            for col in columns:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=120, minwidth=80)
            
            # Insert data
            for index, row in df.iterrows():
                values = [str(val) if pd.notna(val) else '' for val in row]
                self.data_tree.insert('', 'end', values=values)
            
            self.row_count_label.config(text=f"🔍 Found: {len(df):,} matches")
        else:
            self.row_count_label.config(text="No matches found")
            
        # Performance stats
        matches_per_sec = len(df) / max(0.001, search_time)
        self.perf_stats_label.config(text=f"⚡ {matches_per_sec:.0f} matches/sec")
        self.status_label.config(text=f"✅ Fast search completed in {search_time:.3f}s")
        
    def finish_fast_search(self, results: dict, search_term: str, search_time: float, is_global: bool):
        """Finish fast search and display results"""
        self.hide_progress()
        
        # Display results (similar to enhanced version but with performance stats)
        total_matches = results.get('total_matches', 0)
        tables_searched = results.get('tables_searched', 0)
        
        # Performance calculations
        if search_time > 0:
            matches_per_sec = total_matches / search_time
            tables_per_sec = tables_searched / search_time
        else:
            matches_per_sec = tables_per_sec = 0
        
        self.perf_stats_label.config(
            text=f"⚡ {matches_per_sec:.0f} matches/sec, {tables_per_sec:.1f} tables/sec"
        )
        
        self.status_label.config(
            text=f"✅ Fast {'global' if is_global else 'local'} search: {total_matches} matches in {search_time:.2f}s"
        )
        
        # Display results using enhanced method from main app
        # (You would implement the display logic here)
        
    def show_search_error(self, error_msg: str):
        """Show search error"""
        self.hide_progress()
        self.status_label.config(text="❌ Search failed")
        messagebox.showerror("Search Error", error_msg)
        
    # Additional methods would be implemented here...
    # (database selection, table loading, etc.)
    
    def toggle_global_search(self):
        """Toggle global search"""
        self.global_search_var.set(not self.global_search_var.get())
        
    def focus_search(self):
        """Focus on search entry"""
        self.search_entry.focus_set()
        
    def clear_search(self):
        """Clear search"""
        self.search_var.set("")
        
    def on_search_change(self, event=None):
        """Handle search change with delay"""
        if hasattr(self, 'search_timer'):
            self.root.after_cancel(self.search_timer)
        self.search_timer = self.root.after(300, self.fast_search)  # Faster response
        
    def show_performance_settings(self):
        """Show performance settings dialog"""
        # Implement performance settings dialog
        pass
        
    def show_import_menu(self):
        """Show import menu"""
        # Standard import options
        pass
        
    def open_database(self):
        """Open database file"""
        # Standard database opening
        pass
        
    def on_database_select(self, event=None):
        """Handle database selection"""
        # Database selection logic
        pass
        
    def on_table_select(self, event=None):
        """Handle table selection"""
        # Table selection logic
        pass

if __name__ == "__main__":
    print("🚀 Starting High-Performance ShadowHawk Database Browser...")
    print("Features:")
    print("  ⚡ Parallel CSV/Excel import")
    print("  🔍 Database-optimized search")
    print("  🌐 Parallel global search")
    print("  📊 Real-time performance metrics")
    
    app = FastShadowHawkBrowser()
    app.root.mainloop()
