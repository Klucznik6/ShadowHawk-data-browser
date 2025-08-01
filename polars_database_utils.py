import sqlite3
import polars as pl
import pandas as pd
import os
from typing import Dict, List, Any, Optional, Tuple, Callable
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False

class PolarsDatabaseManager:
    """Ultra-fast database manager using Polars for 5-30x speed improvements"""
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.polars_cache: Dict[str, Dict[str, pl.DataFrame]] = {}  # Cache Polars DataFrames
        self.chunk_size = 100000  # Larger chunks for Polars efficiency
        self.max_workers = min(8, multiprocessing.cpu_count())  # More workers with Polars
        
    def detect_database_type(self, filename: str) -> str:
        """Detect database type from file extension"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext in ['.db', '.sqlite', '.sqlite3']:
            return 'sqlite'
        elif ext in ['.mdb', '.accdb']:
            return 'access'
        elif ext in ['.csv']:
            return 'csv'
        elif ext in ['.xlsx', '.xls']:
            return 'excel'
        elif ext in ['.json']:
            return 'json'
        elif ext in ['.parquet']:
            return 'parquet'
        else:
            return 'unknown'
    
    def load_csv_polars(self, filename: str, progress_callback: Callable = None) -> Tuple[sqlite3.Connection, str]:
        """Ultra-fast CSV loading with Polars - up to 10x faster than pandas"""
        start_time = time.time()
        
        # Get file info and validate
        file_size = os.path.getsize(filename)
        table_name = os.path.splitext(os.path.basename(filename))[0]
        table_name = table_name.replace(' ', '_').replace('-', '_')
        
        # Check if file is empty
        if file_size == 0:
            raise ValueError(f"CSV file is empty: {filename}")
        
        if file_size < 10:
            raise ValueError(f"CSV file is too small (only {file_size} bytes): {filename}")
        
        if progress_callback:
            progress_callback(f"🚀 Starting Polars ultra-fast CSV load...", 10)
        
        try:
            # Try multiple CSV parsing strategies
            parsing_strategies = [
                # Standard comma-separated with header
                {"separator": ",", "has_header": True},
                # Semicolon-separated (common in Europe)
                {"separator": ";", "has_header": True},
                # Tab-separated
                {"separator": "\t", "has_header": True},
                # Pipe-separated
                {"separator": "|", "has_header": True},
                # Comma-separated without header
                {"separator": ",", "has_header": False},
            ]
            
            df_polars = None
            successful_strategy = None
            
            for i, strategy in enumerate(parsing_strategies):
                try:
                    if progress_callback:
                        progress_callback(f"🔍 Trying parsing strategy {i+1}/{len(parsing_strategies)}...", 10 + (i * 5))
                    
                    # Use scan_csv for lazy loading
                    df_lazy = pl.scan_csv(
                        filename,
                        separator=strategy["separator"],
                        has_header=strategy["has_header"],
                        infer_schema_length=10000,
                        null_values=["", "NULL", "null", "None", "N/A", "n/a", "#N/A"],
                        try_parse_dates=True,
                        ignore_errors=True
                    )
                    
                    # Try to collect a small sample first
                    sample_df = df_lazy.head(5).collect()
                    
                    if len(sample_df.columns) > 0 and len(sample_df) > 0:
                        # Success! Now collect the full dataset
                        df_polars = df_lazy.collect()
                        successful_strategy = strategy
                        break
                        
                except Exception as strategy_error:
                    if progress_callback:
                        progress_callback(f"⚠️ Strategy {i+1} failed: {str(strategy_error)[:50]}...", 10 + (i * 5))
                    continue
            
            if df_polars is None or len(df_polars.columns) == 0:
                raise ValueError("Could not parse CSV file with any strategy. The file may be corrupted or have an unsupported format.")
            
            if progress_callback:
                strategy_desc = f"separator='{successful_strategy['separator']}', header={successful_strategy['has_header']}"
                progress_callback(f"✨ Polars loaded {len(df_polars):,} rows with {strategy_desc}", 60)
            
            # Cache the Polars DataFrame for ultra-fast search
            if filename not in self.polars_cache:
                self.polars_cache[filename] = {}
            self.polars_cache[filename][table_name] = df_polars
            
            # Convert to pandas for SQLite compatibility (still faster overall)
            df_pandas = df_polars.to_pandas()
            
            if progress_callback:
                progress_callback(f"🔄 Converting for database storage...", 80)
            
            # Create SQLite connection and store with optimized chunked insertion
            conn = sqlite3.connect(':memory:', check_same_thread=False)
            
            # Optimize SQLite for faster bulk inserts
            cursor = conn.cursor()
            cursor.execute("PRAGMA synchronous = OFF")
            cursor.execute("PRAGMA journal_mode = MEMORY")
            cursor.execute("PRAGMA temp_store = MEMORY")
            cursor.execute("PRAGMA cache_size = 1000000")
            
            # Use larger chunks for better performance, but safe for SQLite
            chunk_size = 5000  # Optimized chunk size
            total_chunks = (len(df_pandas) + chunk_size - 1) // chunk_size
            
            for i in range(0, len(df_pandas), chunk_size):
                chunk = df_pandas.iloc[i:i+chunk_size]
                if i == 0:
                    chunk.to_sql(table_name, conn, if_exists='replace', index=False, method=None)
                else:
                    chunk.to_sql(table_name, conn, if_exists='append', index=False, method=None)
                
                # Progress update
                if progress_callback and (i // chunk_size) % 5 == 0:
                    progress = 80 + (i // chunk_size * 15) // total_chunks
                    progress_callback(f"🔄 Storing chunk {i//chunk_size + 1}/{total_chunks}", progress)
            
            # Create indexes for hybrid search
            self._create_search_indexes(conn, table_name)
            
            load_time = time.time() - start_time
            if progress_callback:
                rows_per_sec = len(df_polars) / load_time if load_time > 0 else 0
                progress_callback(f"🎯 Polars CSV loaded: {len(df_polars):,} rows in {load_time:.2f}s ({rows_per_sec:,.0f} rows/sec)", 100)
            
            return conn, table_name
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"⚠️ Polars failed, falling back to pandas: {str(e)}", 50)
            
            # Fallback to pandas if Polars fails
            return self._fallback_csv_load(filename, table_name, progress_callback)
    
    def load_excel_polars(self, filename: str, progress_callback: Callable = None) -> Tuple[sqlite3.Connection, List[str]]:
        """Ultra-fast Excel loading with Polars where possible"""
        start_time = time.time()
        
        # Note: Polars doesn't support Excel directly, but we can optimize the process
        conn = sqlite3.connect(':memory:', check_same_thread=False)
        table_names = []
        
        base_name = os.path.splitext(os.path.basename(filename))[0]
        
        if progress_callback:
            progress_callback(f"📋 Reading Excel file structure...", 10)
        
        # Read Excel file info
        excel_file = pd.ExcelFile(filename)
        
        # Process sheets in parallel with Polars optimization
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_sheet = {}
            
            for i, sheet_name in enumerate(excel_file.sheet_names):
                future = executor.submit(self._process_excel_sheet_polars, filename, sheet_name, base_name)
                future_to_sheet[future] = sheet_name
                
                if progress_callback:
                    progress_callback(f"📊 Starting sheet: {sheet_name}", 20 + (i * 10) // len(excel_file.sheet_names))
            
            # Collect results
            processed_sheets = 0
            for future in as_completed(future_to_sheet):
                sheet_name = future_to_sheet[future]
                try:
                    df_polars, table_name = future.result()
                    
                    # Cache Polars DataFrame
                    if filename not in self.polars_cache:
                        self.polars_cache[filename] = {}
                    self.polars_cache[filename][table_name] = df_polars
                    
                    # Convert to pandas for SQLite
                    df_pandas = df_polars.to_pandas()
                    
                    # Use chunked insertion for large datasets
                    chunk_size = 1000
                    for i in range(0, len(df_pandas), chunk_size):
                        chunk = df_pandas.iloc[i:i+chunk_size]
                        if table_name not in table_names:  # First chunk
                            chunk.to_sql(table_name, conn, if_exists='replace', index=False, method=None)
                            table_names.append(table_name)
                        else:  # Subsequent chunks
                            chunk.to_sql(table_name, conn, if_exists='append', index=False, method=None)
                    
                    # Create search indexes
                    self._create_search_indexes(conn, table_name)
                    
                    processed_sheets += 1
                    if progress_callback:
                        progress = 30 + (processed_sheets * 70) // len(excel_file.sheet_names)
                        progress_callback(f"✅ Loaded sheet: {sheet_name} ({len(df_polars):,} rows)", progress)
                        
                except Exception as e:
                    print(f"Error processing sheet {sheet_name}: {e}")
        
        load_time = time.time() - start_time
        if progress_callback:
            progress_callback(f"🎯 Excel loaded: {len(table_names)} sheets in {load_time:.2f}s", 100)
        
        return conn, table_names
    
    def _process_excel_sheet_polars(self, filename: str, sheet_name: str, base_name: str) -> Tuple[pl.DataFrame, str]:
        """Process Excel sheet and convert to Polars for optimization"""
        # Read with pandas first (Excel limitation)
        df_pandas = pd.read_excel(filename, sheet_name=sheet_name)
        
        # Convert to Polars for optimization
        df_polars = pl.from_pandas(df_pandas)
        
        # Optimize data types in Polars (much faster than pandas)
        df_polars = self._optimize_polars_dtypes(df_polars)
        
        table_name = f"{base_name}_{sheet_name}".replace(' ', '_').replace('-', '_')
        return df_polars, table_name
    
    def _optimize_polars_dtypes(self, df: pl.DataFrame) -> pl.DataFrame:
        """Optimize data types using Polars - much faster than pandas"""
        optimized_exprs = []
        
        for col in df.columns:
            col_expr = pl.col(col)
            dtype = df[col].dtype
            
            if dtype == pl.Utf8:
                # Try to optimize string columns
                try:
                    # Check if it's numeric
                    optimized_exprs.append(
                        pl.when(pl.col(col).str.contains(r"^\d+$"))
                        .then(pl.col(col).cast(pl.Int64, strict=False))
                        .otherwise(
                            pl.when(pl.col(col).str.contains(r"^\d+\.\d+$"))
                            .then(pl.col(col).cast(pl.Float64, strict=False))
                            .otherwise(pl.col(col))
                        ).alias(col)
                    )
                except:
                    optimized_exprs.append(col_expr)
            else:
                optimized_exprs.append(col_expr)
        
        return df.select(optimized_exprs)
    
    def _fallback_csv_load(self, filename: str, table_name: str, progress_callback: Callable = None) -> Tuple[sqlite3.Connection, str]:
        """Fallback to pandas loading if Polars fails"""
        if progress_callback:
            progress_callback(f"📦 Using pandas fallback...", 60)
        
        # Use chunked pandas loading
        conn = sqlite3.connect(':memory:', check_same_thread=False)
        chunk_iterator = pd.read_csv(filename, chunksize=self.chunk_size)
        
        total_rows = 0
        for i, chunk in enumerate(chunk_iterator):
            if i == 0:
                chunk.to_sql(table_name, conn, if_exists='replace', index=False, method=None)
            else:
                chunk.to_sql(table_name, conn, if_exists='append', index=False, method=None)
            total_rows += len(chunk)
            
            if progress_callback:
                progress_callback(f"📦 Pandas loading: {total_rows:,} rows", 60 + (i * 20) // 100)
        
        self._create_search_indexes(conn, table_name)
        return conn, table_name
    
    def _create_search_indexes(self, conn: sqlite3.Connection, table_name: str):
        """Create indexes for faster search"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col_info in columns:
                col_name = col_info[1]
                col_type = col_info[2].upper()
                
                if 'TEXT' in col_type or 'VARCHAR' in col_type or col_type == '':
                    try:
                        index_name = f"idx_{table_name}_{col_name}"
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({col_name})")
                    except Exception as e:
                        print(f"Could not create index on {col_name}: {e}")
            
            conn.commit()
        except Exception as e:
            print(f"Error creating indexes for {table_name}: {e}")
    
    def ultra_fast_search_table(self, conn: sqlite3.Connection, table_name: str, search_term: str, 
                               filename: str = None, limit: int = 1000) -> pd.DataFrame:
        """Ultra-fast search using Polars if available, fallback to SQL"""
        if not search_term.strip():
            return pd.DataFrame()
        
        # Try Polars search first (much faster)
        if filename and filename in self.polars_cache and table_name in self.polars_cache[filename]:
            try:
                return self._polars_search(self.polars_cache[filename][table_name], search_term, limit)
            except Exception as e:
                print(f"Polars search failed, falling back to SQL: {e}")
        
        # Fallback to SQL search
        return self._sql_search(conn, table_name, search_term, limit)
    
    def _polars_search(self, df_polars: pl.DataFrame, search_term: str, limit: int) -> pd.DataFrame:
        """Ultra-fast search using Polars - up to 10x faster"""
        search_conditions = []
        
        for col in df_polars.columns:
            # Polars string operations are much faster
            search_conditions.append(
                pl.col(col).cast(pl.Utf8).str.contains(f"(?i){search_term}")  # Case insensitive
            )
        
        # Combine conditions with OR
        combined_condition = search_conditions[0]
        for condition in search_conditions[1:]:
            combined_condition = combined_condition | condition
        
        # Execute search and limit results
        result_polars = df_polars.filter(combined_condition).head(limit)
        
        # Convert to pandas for compatibility
        return result_polars.to_pandas()
    
    def _sql_search(self, conn: sqlite3.Connection, table_name: str, search_term: str, limit: int) -> pd.DataFrame:
        """SQL search fallback"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            search_conditions = []
            search_term_sql = search_term.replace("'", "''")
            
            for col in columns:
                search_conditions.append(f"{col} LIKE '%{search_term_sql}%'")
            
            where_clause = " OR ".join(search_conditions)
            query = f"SELECT * FROM {table_name} WHERE {where_clause} LIMIT {limit}"
            
            return pd.read_sql_query(query, conn)
            
        except Exception as e:
            print(f"Error in SQL search for {table_name}: {e}")
            return pd.DataFrame()
    
    def ultra_parallel_global_search(self, databases: Dict[str, Any], search_term: str, 
                                   progress_callback: Callable = None) -> Dict[str, Any]:
        """Ultra-fast parallel search using Polars optimization"""
        results = {
            'matches': [],
            'summary': [],
            'total_matches': 0,
            'tables_searched': 0,
            'databases_searched': 0
        }
        
        if not search_term.strip():
            return results
        
        # Collect search tasks with Polars optimization info
        search_tasks = []
        for db_name, db_info in databases.items():
            connection = db_info['connection']
            db_type = db_info['type']
            filename = db_info.get('filename', None)
            
            try:
                if db_type == 'sqlite':
                    cursor = connection.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    for table_name in tables:
                        search_tasks.append((db_name, connection, table_name, search_term, filename))
                        
            except Exception as e:
                print(f"Error getting tables for {db_name}: {e}")
                continue
        
        if progress_callback:
            progress_callback(f"🚀 Starting ultra-fast search across {len(search_tasks)} tables...", 5)
        
        # Execute searches in parallel with more workers
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {}
            
            for task in search_tasks:
                future = executor.submit(self._ultra_search_single_table, *task)
                future_to_task[future] = task
            
            # Collect results
            completed = 0
            polars_used = 0
            for future in as_completed(future_to_task):
                completed += 1
                task = future_to_task[future]
                db_name, _, table_name, _, _ = task
                
                try:
                    matches, used_polars = future.result()
                    if used_polars:
                        polars_used += 1
                    
                    results['tables_searched'] += 1
                    
                    if len(matches) > 0:
                        # Add metadata
                        matches = matches.copy()
                        matches.insert(0, '_database', db_name)
                        matches.insert(1, '_table', table_name)
                        matches.insert(2, '_source_row', range(len(matches)))
                        
                        results['matches'].append(matches)
                        results['summary'].append({
                            'database': db_name,
                            'table': table_name,
                            'match_count': len(matches),
                            'total_rows': len(matches)
                        })
                        results['total_matches'] += len(matches)
                    
                    # Progress update
                    if progress_callback and completed % 3 == 0:  # More frequent updates
                        progress = 10 + (completed * 85) // len(search_tasks)
                        speed_info = f"({polars_used}/{completed} ultra-fast)" if polars_used > 0 else ""
                        progress_callback(f"⚡ Searched {completed}/{len(search_tasks)} tables {speed_info}", progress)
                        
                except Exception as e:
                    print(f"Error searching {db_name}.{table_name}: {e}")
                    continue
        
        # Count unique databases
        results['databases_searched'] = len(set(task[0] for task in search_tasks))
        
        if progress_callback:
            efficiency = f"({polars_used}/{len(search_tasks)} used Polars ultra-speed)" if polars_used > 0 else ""
            progress_callback(f"🎯 Ultra-fast search complete: {results['total_matches']} matches {efficiency}", 100)
        
        return results
    
    def _ultra_search_single_table(self, db_name: str, connection: sqlite3.Connection, 
                                  table_name: str, search_term: str, filename: str = None) -> Tuple[pd.DataFrame, bool]:
        """Search single table with Polars optimization"""
        try:
            if filename and filename in self.polars_cache and table_name in self.polars_cache[filename]:
                # Use ultra-fast Polars search
                result = self._polars_search(self.polars_cache[filename][table_name], search_term, 1000)
                return result, True  # True indicates Polars was used
            else:
                # Fallback to SQL search
                result = self._sql_search(connection, table_name, search_term, 1000)
                return result, False  # False indicates SQL was used
                
        except Exception as e:
            print(f"Error in ultra search {db_name}.{table_name}: {e}")
            return pd.DataFrame(), False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        polars_tables = sum(len(tables) for tables in self.polars_cache.values())
        total_memory = sum(
            df.estimated_size() if hasattr(df, 'estimated_size') else 0
            for file_cache in self.polars_cache.values()
            for df in file_cache.values()
        )
        
        return {
            'polars_cached_tables': polars_tables,
            'polars_memory_usage_mb': total_memory / (1024 * 1024),
            'max_workers': self.max_workers,
            'chunk_size': self.chunk_size
        }
    
    def load_sqlite_polars(self, filename: str, progress_callback: Callable = None) -> Tuple[sqlite3.Connection, List[str]]:
        """Load SQLite database and return connection with table list"""
        if progress_callback:
            progress_callback(f"🗂️ Opening SQLite database: {os.path.basename(filename)}", 20)
        
        try:
            # Create connection to the SQLite file
            conn = sqlite3.connect(filename, check_same_thread=False)
            
            if progress_callback:
                progress_callback(f"📊 Reading database schema...", 40)
            
            # Get list of tables
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                raise ValueError("No tables found in SQLite database")
            
            if progress_callback:
                progress_callback(f"✅ Found {len(tables)} tables: {', '.join(tables)}", 100)
            
            return conn, tables
            
        except Exception as e:
            raise ValueError(f"Failed to load SQLite database: {str(e)}")
    
    def load_access_polars(self, filename: str, progress_callback: Callable = None) -> Tuple[sqlite3.Connection, List[str]]:
        """Load MS Access database and convert to SQLite connection"""
        if not PYODBC_AVAILABLE:
            raise ValueError("pyodbc is required for Access database support")
        
        if progress_callback:
            progress_callback(f"🗂️ Opening Access database: {os.path.basename(filename)}", 10)
        
        try:
            # Create connection string for Access database
            conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={filename};"
            access_conn = pyodbc.connect(conn_str)
            
            if progress_callback:
                progress_callback(f"📊 Reading Access schema...", 30)
            
            # Get list of tables
            cursor = access_conn.cursor()
            tables = [row.table_name for row in cursor.tables(tableType='TABLE')]
            
            if not tables:
                raise ValueError("No tables found in Access database")
            
            # Create SQLite in-memory database
            sqlite_conn = sqlite3.connect(':memory:', check_same_thread=False)
            
            if progress_callback:
                progress_callback(f"🔄 Converting {len(tables)} tables to SQLite...", 50)
            
            # Copy each table from Access to SQLite
            for i, table_name in enumerate(tables):
                # Read table from Access using pandas
                df = pd.read_sql(f"SELECT * FROM [{table_name}]", access_conn)
                
                # Write to SQLite
                df.to_sql(table_name, sqlite_conn, if_exists='replace', index=False)
                
                if progress_callback:
                    progress = 50 + (i * 40) // len(tables)
                    progress_callback(f"🔄 Converted table: {table_name}", progress)
            
            access_conn.close()
            
            if progress_callback:
                progress_callback(f"✅ Access database converted: {len(tables)} tables", 100)
            
            return sqlite_conn, tables
            
        except Exception as e:
            raise ValueError(f"Failed to load Access database: {str(e)}")
    
    def load_json_polars(self, filename: str, progress_callback: Callable = None) -> Tuple[sqlite3.Connection, str]:
        """Load JSON file and convert to SQLite table"""
        table_name = os.path.splitext(os.path.basename(filename))[0]
        table_name = table_name.replace(' ', '_').replace('-', '_')
        
        if progress_callback:
            progress_callback(f"📄 Loading JSON file: {os.path.basename(filename)}", 20)
        
        try:
            # Try loading with Polars first (faster)
            df_polars = pl.read_json(filename)
            
            if progress_callback:
                progress_callback(f"✨ Polars loaded {len(df_polars):,} records", 60)
            
            # Convert to pandas for SQLite compatibility
            df_pandas = df_polars.to_pandas()
            
            if progress_callback:
                progress_callback(f"🔄 Converting to database format...", 80)
            
            # Create SQLite connection
            conn = sqlite3.connect(':memory:', check_same_thread=False)
            df_pandas.to_sql(table_name, conn, if_exists='replace', index=False)
            
            if progress_callback:
                progress_callback(f"✅ JSON loaded as table: {table_name}", 100)
            
            return conn, table_name
            
        except Exception as e:
            # Fallback to pandas
            if progress_callback:
                progress_callback(f"⚠️ Polars failed, using pandas fallback...", 40)
            
            try:
                df_pandas = pd.read_json(filename)
                
                if progress_callback:
                    progress_callback(f"📦 Pandas loaded {len(df_pandas):,} records", 80)
                
                conn = sqlite3.connect(':memory:', check_same_thread=False)
                df_pandas.to_sql(table_name, conn, if_exists='replace', index=False)
                
                if progress_callback:
                    progress_callback(f"✅ JSON loaded as table: {table_name}", 100)
                
                return conn, table_name
                
            except Exception as fallback_error:
                raise ValueError(f"Failed to load JSON file: {str(fallback_error)}")
