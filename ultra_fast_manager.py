#!/usr/bin/env python3
"""
Ultra-Fast Database Manager using Polars (Rust-based)
This implementation can be 5-30x faster than pandas for many operations.
"""

import polars as pl
import sqlite3
import os
import time
from typing import Dict, List, Any, Optional, Tuple, Callable
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    ARROW_AVAILABLE = True
except ImportError:
    ARROW_AVAILABLE = False

class UltraFastDatabaseManager:
    """Ultra-high performance database manager using Polars and modern techniques"""
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.polars_cache: Dict[str, pl.DataFrame] = {}
        self.chunk_size = 100000  # Larger chunks for better performance
        self.max_workers = min(8, multiprocessing.cpu_count())
        self.use_arrow = ARROW_AVAILABLE
        
    def ultra_fast_csv_import(self, filename: str, progress_callback: Callable = None) -> Tuple[Any, str]:
        """Ultra-fast CSV import using Polars (Rust-based)"""
        start_time = time.time()
        
        if progress_callback:
            progress_callback("🚀 Starting ultra-fast CSV import...", 0)
        
        try:
            # Use Polars for ultra-fast CSV reading (Rust implementation)
            df = pl.read_csv(
                filename,
                try_parse_dates=True,
                rechunk=True,  # Optimize memory layout
                low_memory=True,  # Use less memory
                ignore_errors=True  # Skip problematic rows
            )
            
            if progress_callback:
                progress_callback(f"✅ Polars loaded {len(df):,} rows", 30)
            
            # Create table name
            table_name = os.path.splitext(os.path.basename(filename))[0]
            table_name = table_name.replace(' ', '_').replace('-', '_')
            
            # Convert to SQLite for compatibility (but keep Polars version for speed)
            conn = sqlite3.connect(':memory:', check_same_thread=False)
            
            if progress_callback:
                progress_callback("Converting to SQLite...", 50)
            
            # Convert Polars to Pandas for SQLite (only when needed)
            pandas_df = df.to_pandas()
            pandas_df.to_sql(table_name, conn, if_exists='replace', index=False, method='multi')
            
            if progress_callback:
                progress_callback("Creating search indexes...", 70)
            
            # Create indexes for ultra-fast search
            self._create_ultra_indexes(conn, table_name)
            
            # Cache Polars DataFrame for ultra-fast operations
            cache_key = f"{filename}_{table_name}"
            self.polars_cache[cache_key] = df
            
            if progress_callback:
                progress_callback("Optimizing for Arrow (if available)...", 90)
            
            # Optionally save as Parquet for future ultra-fast loading
            if self.use_arrow:
                try:
                    parquet_path = filename.replace('.csv', '.ultra.parquet')
                    df.write_parquet(parquet_path, compression='snappy')
                except Exception as e:
                    print(f"Could not save Parquet: {e}")
            
            load_time = time.time() - start_time
            if progress_callback:
                rows_per_sec = len(df) / max(0.001, load_time)
                progress_callback(f"🚀 Ultra-fast import complete: {rows_per_sec:,.0f} rows/sec", 100)
            
            return conn, table_name
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"❌ Ultra-fast import failed: {str(e)}", 0)
            raise
    
    def ultra_fast_search(self, filename: str, table_name: str, search_term: str, 
                         limit: int = 5000) -> pl.DataFrame:
        """Ultra-fast search using Polars native operations"""
        cache_key = f"{filename}_{table_name}"
        
        if cache_key not in self.polars_cache:
            # Load from Parquet if available (much faster than CSV)
            parquet_path = filename.replace('.csv', '.ultra.parquet')
            if os.path.exists(parquet_path):
                df = pl.read_parquet(parquet_path)
            else:
                df = pl.read_csv(filename)
            self.polars_cache[cache_key] = df
        
        df = self.polars_cache[cache_key]
        
        if not search_term.strip():
            return df.head(limit)
        
        # Ultra-fast Rust-powered string search
        search_conditions = []
        for col in df.columns:
            try:
                # Use Polars native string operations (much faster than pandas)
                condition = pl.col(col).cast(pl.Utf8).str.to_lowercase().str.contains(
                    search_term.lower(), literal=True
                )
                search_conditions.append(condition)
            except:
                # Skip columns that can't be converted to string
                continue
        
        if search_conditions:
            # Combine conditions with OR (any column matches)
            combined_condition = pl.any_horizontal(search_conditions)
            result = df.filter(combined_condition).head(limit)
        else:
            result = pl.DataFrame()
        
        return result
    
    def parallel_ultra_search(self, databases: Dict[str, Any], search_term: str,
                            progress_callback: Callable = None) -> Dict[str, Any]:
        """Ultra-fast parallel search using process pools for maximum speed"""
        
        if not search_term.strip():
            return {'matches': [], 'summary': [], 'total_matches': 0}
        
        # Prepare search tasks
        search_tasks = []
        for db_name, db_info in databases.items():
            if 'filename' in db_info and 'tables' in db_info:
                for table_name in db_info['tables']:
                    search_tasks.append((db_name, db_info['filename'], table_name, search_term))
        
        if progress_callback:
            progress_callback(f"🚀 Starting parallel search across {len(search_tasks)} tables", 0)
        
        results = {
            'matches': [],
            'summary': [],
            'total_matches': 0,
            'tables_searched': len(search_tasks),
            'databases_searched': len(databases)
        }
        
        # Use ProcessPoolExecutor for true parallelism (bypasses Python GIL)
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all search tasks
            future_to_task = {
                executor.submit(self._ultra_search_single_task, *task): task 
                for task in search_tasks
            }
            
            completed = 0
            for future in future_to_task:
                completed += 1
                task = future_to_task[future]
                db_name, filename, table_name, _ = task
                
                try:
                    matches = future.result(timeout=30)  # 30 second timeout per search
                    
                    if len(matches) > 0:
                        # Add metadata to matches
                        matches_with_meta = matches.with_columns([
                            pl.lit(db_name).alias('_database'),
                            pl.lit(table_name).alias('_table'),
                            pl.int_range(len(matches)).alias('_source_row')
                        ])
                        
                        results['matches'].append(matches_with_meta.to_pandas())
                        results['summary'].append({
                            'database': db_name,
                            'table': table_name,
                            'match_count': len(matches),
                            'total_rows': len(matches)
                        })
                        results['total_matches'] += len(matches)
                    
                    # Progress update
                    if progress_callback and completed % 3 == 0:
                        progress = (completed * 100) // len(search_tasks)
                        progress_callback(f"Searched {completed}/{len(search_tasks)} tables", progress)
                        
                except Exception as e:
                    print(f"Error in ultra search {db_name}.{table_name}: {e}")
                    continue
        
        if progress_callback:
            progress_callback(f"🚀 Ultra-fast search complete: {results['total_matches']} matches", 100)
        
        return results
    
    @staticmethod
    def _ultra_search_single_task(db_name: str, filename: str, table_name: str, search_term: str) -> pl.DataFrame:
        """Single search task for process pool (static method for pickling)"""
        try:
            # Create a new manager instance in the worker process
            manager = UltraFastDatabaseManager()
            return manager.ultra_fast_search(filename, table_name, search_term)
        except Exception as e:
            print(f"Worker process error for {db_name}.{table_name}: {e}")
            return pl.DataFrame()
    
    def _create_ultra_indexes(self, conn: sqlite3.Connection, table_name: str):
        """Create optimized indexes for ultra-fast SQL queries"""
        try:
            cursor = conn.cursor()
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Create indexes on all text columns with error handling
            for col_info in columns:
                col_name = col_info[1]
                try:
                    # Create index with IF NOT EXISTS to avoid conflicts
                    index_name = f"ultra_idx_{table_name}_{col_name}"[:63]  # SQLite name limit
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({col_name})")
                except Exception as e:
                    # Skip columns that can't be indexed
                    continue
            
            # Create a composite index for better search performance
            try:
                composite_cols = [col[1] for col in columns[:5]]  # First 5 columns
                composite_index = f"ultra_composite_{table_name}"[:63]
                col_list = ', '.join(composite_cols)
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {composite_index} ON {table_name}({col_list})")
            except:
                pass
            
            conn.commit()
            
        except Exception as e:
            print(f"Error creating ultra indexes: {e}")
    
    def benchmark_vs_pandas(self, filename: str) -> Dict[str, float]:
        """Benchmark Polars vs Pandas performance"""
        print(f"🏁 Benchmarking {filename}...")
        
        # Test Polars
        start_time = time.time()
        polars_df = pl.read_csv(filename)
        polars_load_time = time.time() - start_time
        
        # Test Pandas
        import pandas as pd
        start_time = time.time()
        pandas_df = pd.read_csv(filename)
        pandas_load_time = time.time() - start_time
        
        # Test search performance
        search_term = "test"
        
        # Polars search
        start_time = time.time()
        polars_results = self.ultra_fast_search(filename, "test", search_term)
        polars_search_time = time.time() - start_time
        
        # Pandas search (simple)
        start_time = time.time()
        pandas_mask = pandas_df.astype(str).apply(
            lambda x: x.str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        pandas_results = pandas_df[pandas_mask]
        pandas_search_time = time.time() - start_time
        
        results = {
            'polars_load_time': polars_load_time,
            'pandas_load_time': pandas_load_time,
            'polars_search_time': polars_search_time,
            'pandas_search_time': pandas_search_time,
            'load_speedup': pandas_load_time / polars_load_time if polars_load_time > 0 else 0,
            'search_speedup': pandas_search_time / polars_search_time if polars_search_time > 0 else 0,
        }
        
        print(f"📊 Load Speed: Polars {polars_load_time:.3f}s vs Pandas {pandas_load_time:.3f}s")
        print(f"🔍 Search Speed: Polars {polars_search_time:.3f}s vs Pandas {pandas_search_time:.3f}s")
        print(f"🚀 Speedup: {results['load_speedup']:.1f}x load, {results['search_speedup']:.1f}x search")
        
        return results

if __name__ == "__main__":
    # Quick test
    manager = UltraFastDatabaseManager()
    print("🚀 Ultra-Fast Database Manager initialized")
    print(f"   Max workers: {manager.max_workers}")
    print(f"   Arrow support: {manager.use_arrow}")
    print(f"   Chunk size: {manager.chunk_size:,}")
