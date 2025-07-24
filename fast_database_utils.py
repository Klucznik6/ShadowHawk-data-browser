import sqlite3
import pandas as pd
import os
from typing import Dict, List, Any, Optional, Tuple, Callable
import json
import csv
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False

class FastDatabaseManager:
    """High-performance database manager with optimized loading and search"""
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.search_indexes: Dict[str, Dict[str, Any]] = {}  # For fast text search
        self.chunk_size = 50000  # Optimal chunk size for large files
        self.max_workers = min(4, multiprocessing.cpu_count())  # Limit threads
        
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
        else:
            return 'unknown'
    
    def load_csv_fast(self, filename: str, progress_callback: Callable = None) -> Tuple[sqlite3.Connection, str]:
        """Fast CSV loading with chunked processing and progress feedback"""
        start_time = time.time()
        
        # Get file size for progress calculation
        file_size = os.path.getsize(filename)
        
        # Create connection
        conn = sqlite3.connect(':memory:', check_same_thread=False)
        table_name = os.path.splitext(os.path.basename(filename))[0]
        table_name = table_name.replace(' ', '_').replace('-', '_')
        
        # Read CSV in chunks for better memory management
        chunk_iterator = pd.read_csv(filename, chunksize=self.chunk_size)
        
        total_rows = 0
        chunk_count = 0
        
        for chunk in chunk_iterator:
            chunk_count += 1
            
            # Optimize data types for better performance
            chunk = self._optimize_chunk_dtypes(chunk)
            
            # Write to database
            if chunk_count == 1:
                chunk.to_sql(table_name, conn, if_exists='replace', index=False, method='multi')
            else:
                chunk.to_sql(table_name, conn, if_exists='append', index=False, method='multi')
            
            total_rows += len(chunk)
            
            # Report progress
            if progress_callback:
                progress = min(100, (chunk_count * self.chunk_size * 100) // max(1, total_rows * 1.2))
                progress_callback(f"Loading CSV: {total_rows:,} rows processed", progress)
        
        # Create indexes for faster search
        self._create_search_indexes(conn, table_name)
        
        load_time = time.time() - start_time
        if progress_callback:
            progress_callback(f"✅ CSV loaded: {total_rows:,} rows in {load_time:.2f}s", 100)
        
        return conn, table_name
    
    def load_excel_fast(self, filename: str, progress_callback: Callable = None) -> Tuple[sqlite3.Connection, List[str]]:
        """Fast Excel loading with parallel sheet processing"""
        start_time = time.time()
        
        conn = sqlite3.connect(':memory:', check_same_thread=False)
        excel_file = pd.ExcelFile(filename)
        table_names = []
        
        base_name = os.path.splitext(os.path.basename(filename))[0]
        
        # Process sheets in parallel for better performance
        with ThreadPoolExecutor(max_workers=min(len(excel_file.sheet_names), self.max_workers)) as executor:
            future_to_sheet = {}
            
            for i, sheet_name in enumerate(excel_file.sheet_names):
                future = executor.submit(self._process_excel_sheet, filename, sheet_name, base_name)
                future_to_sheet[future] = sheet_name
                
                if progress_callback:
                    progress_callback(f"Starting sheet: {sheet_name}", (i * 20) // len(excel_file.sheet_names))
            
            # Collect results
            for future in as_completed(future_to_sheet):
                sheet_name = future_to_sheet[future]
                try:
                    df, table_name = future.result()
                    
                    # Optimize and load to database
                    df = self._optimize_chunk_dtypes(df)
                    df.to_sql(table_name, conn, if_exists='replace', index=False, method='multi')
                    table_names.append(table_name)
                    
                    # Create search indexes
                    self._create_search_indexes(conn, table_name)
                    
                    if progress_callback:
                        completed = len(table_names)
                        progress = 20 + (completed * 80) // len(excel_file.sheet_names)
                        progress_callback(f"Loaded sheet: {sheet_name} ({len(df):,} rows)", progress)
                        
                except Exception as e:
                    print(f"Error processing sheet {sheet_name}: {e}")
        
        load_time = time.time() - start_time
        if progress_callback:
            total_rows = sum(len(pd.read_sql(f"SELECT * FROM {tn} LIMIT 1", conn)) for tn in table_names)
            progress_callback(f"✅ Excel loaded: {len(table_names)} sheets in {load_time:.2f}s", 100)
        
        return conn, table_names
    
    def _process_excel_sheet(self, filename: str, sheet_name: str, base_name: str) -> Tuple[pd.DataFrame, str]:
        """Process a single Excel sheet"""
        df = pd.read_excel(filename, sheet_name=sheet_name)
        table_name = f"{base_name}_{sheet_name}".replace(' ', '_').replace('-', '_')
        return df, table_name
    
    def _optimize_chunk_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data types for better performance and memory usage"""
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric if possible
                try:
                    # Check if it's actually numeric
                    pd.to_numeric(df[col], errors='raise')
                    df[col] = pd.to_numeric(df[col], downcast='integer')
                except:
                    try:
                        df[col] = pd.to_numeric(df[col], downcast='float')
                    except:
                        # Keep as string but optimize
                        if df[col].nunique() / len(df) < 0.5:  # Low cardinality
                            df[col] = df[col].astype('category')
                        else:
                            # Convert to string to ensure consistency
                            df[col] = df[col].astype(str)
            
            elif df[col].dtype.kind in 'biufc':  # numeric types
                # Downcast numeric types
                if df[col].dtype.kind in 'iu':  # integers
                    df[col] = pd.to_numeric(df[col], downcast='integer')
                else:  # floats
                    df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df
    
    def _create_search_indexes(self, conn: sqlite3.Connection, table_name: str):
        """Create indexes for faster text search"""
        try:
            cursor = conn.cursor()
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Create indexes on text columns for faster LIKE queries
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
    
    def fast_search_table(self, conn: sqlite3.Connection, table_name: str, search_term: str, 
                         limit: int = 1000) -> pd.DataFrame:
        """Optimized search using database queries instead of loading all data"""
        if not search_term.strip():
            return pd.DataFrame()
        
        try:
            cursor = conn.cursor()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Build optimized search query using database LIKE for better performance
            search_conditions = []
            search_term_sql = search_term.replace("'", "''")  # Escape quotes
            
            for col in columns:
                search_conditions.append(f"{col} LIKE '%{search_term_sql}%'")
            
            # Use database search instead of loading all data
            where_clause = " OR ".join(search_conditions)
            query = f"""
                SELECT * FROM {table_name} 
                WHERE {where_clause}
                LIMIT {limit}
            """
            
            return pd.read_sql_query(query, conn)
            
        except Exception as e:
            print(f"Error in fast search for {table_name}: {e}")
            # Fallback to regular search
            return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    
    def parallel_global_search(self, databases: Dict[str, Any], search_term: str, 
                             progress_callback: Callable = None) -> Dict[str, Any]:
        """Parallel search across all databases for maximum speed"""
        results = {
            'matches': [],
            'summary': [],
            'total_matches': 0,
            'tables_searched': 0,
            'databases_searched': 0
        }
        
        if not search_term.strip():
            return results
        
        # Collect all search tasks
        search_tasks = []
        for db_name, db_info in databases.items():
            connection = db_info['connection']
            db_type = db_info['type']
            
            try:
                if db_type == 'sqlite':
                    cursor = connection.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    for table_name in tables:
                        search_tasks.append((db_name, connection, table_name, search_term))
                        
            except Exception as e:
                print(f"Error getting tables for {db_name}: {e}")
                continue
        
        # Execute searches in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {}
            
            for task in search_tasks:
                future = executor.submit(self._search_single_table, *task)
                future_to_task[future] = task
            
            # Collect results
            completed = 0
            for future in as_completed(future_to_task):
                completed += 1
                task = future_to_task[future]
                db_name, _, table_name, _ = task
                
                try:
                    matches = future.result()
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
                            'total_rows': len(matches)  # This is approximate for performance
                        })
                        results['total_matches'] += len(matches)
                    
                    # Progress update
                    if progress_callback and completed % 5 == 0:  # Update every 5 tables
                        progress = (completed * 100) // len(search_tasks)
                        progress_callback(f"Searched {completed}/{len(search_tasks)} tables", progress)
                        
                except Exception as e:
                    print(f"Error searching {db_name}.{table_name}: {e}")
                    continue
        
        # Count unique databases
        results['databases_searched'] = len(set(task[0] for task in search_tasks))
        
        if progress_callback:
            progress_callback(f"✅ Search complete: {results['total_matches']} matches found", 100)
        
        return results
    
    def _search_single_table(self, db_name: str, connection: sqlite3.Connection, 
                            table_name: str, search_term: str) -> pd.DataFrame:
        """Search a single table - optimized for parallel execution"""
        try:
            return self.fast_search_table(connection, table_name, search_term, limit=1000)
        except Exception as e:
            print(f"Error searching {db_name}.{table_name}: {e}")
            return pd.DataFrame()
